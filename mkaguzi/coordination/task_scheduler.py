# Task Scheduler for Multi-Agent System
# =============================================================================
# Distributes agent tasks optimally with load balancing and priority queues

import frappe
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime, timedelta
import queue
import threading
import heapq
from dataclasses import dataclass, field
from enum import Enum

from ..agents.agent_manager import get_agent_manager


class Priority(Enum):
    """Task priority levels"""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3


@dataclass(order=True)
class ScheduledTask:
    """A task scheduled for execution"""
    priority: Priority
    created_at: datetime = field(compare=False)
    task_id: str = field(compare=False)
    agent_type: str = field(default=None, compare=False)
    task_data: Dict[str, Any] = field(default_factory=dict, compare=False)
    timeout: int = field(default=300, compare=False)
    retry_count: int = field(default=0, compare=False)
    max_retries: int = field(default=3, compare=False)
    dependencies: List[str] = field(default_factory=list, compare=False)


class TaskScheduler:
    """
    Distributes agent tasks optimally with load balancing, priority queues,
    and deadlock prevention.
    """

    def __init__(self):
        """Initialize the Task Scheduler"""
        self.agent_manager = get_agent_manager()

        # Priority queues for each priority level
        self.queues = {
            Priority.CRITICAL: queue.PriorityQueue(),
            Priority.HIGH: queue.PriorityQueue(),
            Priority.NORMAL: queue.PriorityQueue(),
            Priority.LOW: queue.PriorityQueue()
        }

        # Agent load tracking
        self.agent_load: Dict[str, int] = {}  # agent_id -> active task count
        self.agent_capacity: Dict[str, int] = {}  # agent_id -> max concurrent tasks

        # Task tracking
        self.pending_tasks: Dict[str, ScheduledTask] = {}
        self.running_tasks: Dict[str, ScheduledTask] = {}
        self.completed_tasks: Dict[str, ScheduledTask] = {}
        self.failed_tasks: Dict[str, ScheduledTask] = {}

        # Synchronization
        self.lock = threading.Lock()
        self.condition = threading.Condition()

        # Configuration
        self.default_capacity = 5  # Default max concurrent tasks per agent
        self.scheduled_tasks: List[Dict[str, Any]] = []  # Heap for scheduled tasks

        # Worker thread
        self.worker_thread = None
        self.running = False

    def start(self) -> None:
        """Start the task scheduler worker thread"""
        with self.lock:
            if self.running:
                return

            self.running = True
            self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
            self.worker_thread.start()

            frappe.logger().info("Task Scheduler started")

    def stop(self) -> None:
        """Stop the task scheduler worker thread"""
        with self.lock:
            self.running = False
            self.condition.notify_all()

        if self.worker_thread:
            self.worker_thread.join(timeout=5)

        frappe.logger().info("Task Scheduler stopped")

    def schedule_task(self, agent_type: str, task_data: Dict[str, Any],
                     priority: Priority = Priority.NORMAL,
                     scheduled_for: Optional[datetime] = None,
                     dependencies: Optional[List[str]] = None,
                     timeout: int = 300,
                     max_retries: int = 3) -> str:
        """
        Schedule a task for execution

        Args:
            agent_type: Type of agent to execute the task
            task_data: Task data dictionary
            priority: Task priority
            scheduled_for: Optional scheduled execution time
            dependencies: Optional list of task IDs this task depends on
            timeout: Task timeout in seconds
            max_retries: Maximum retry attempts

        Returns:
            Task ID
        """
        task_id = f"task_{datetime.now().timestamp()}_{id(task_data)}"

        task = ScheduledTask(
            priority=priority,
            created_at=datetime.now(),
            task_id=task_id,
            agent_type=agent_type,
            task_data=task_data,
            timeout=timeout,
            max_retries=max_retries,
            dependencies=dependencies or []
        )

        with self.lock:
            self.pending_tasks[task_id] = task

            if scheduled_for and scheduled_for > datetime.now():
                # Add to scheduled tasks heap
                heapq.heappush(self.scheduled_tasks, {
                    'scheduled_time': scheduled_for,
                    'task_id': task_id
                })
            else:
                # Add to appropriate priority queue
                self.queues[priority].put(task)

            self.condition.notify()

        frappe.logger().info(f"Scheduled task {task_id} for {agent_type} agent")
        return task_id

    def get_next_task(self, agent_id: str,
                     max_wait: float = 1.0) -> Optional[ScheduledTask]:
        """
        Get next task for an agent based on priority and load

        Args:
            agent_id: Agent identifier
            max_wait: Maximum wait time in seconds

        Returns:
            ScheduledTask or None
        """
        deadline = datetime.now() + timedelta(seconds=max_wait)

        with self.condition:
            while datetime.now() < deadline:
                # Check for scheduled tasks that are due
                self._check_scheduled_tasks()

                # Try to get task from highest priority queue first
                for priority in [Priority.CRITICAL, Priority.HIGH, Priority.NORMAL, Priority.LOW]:
                    try:
                        task = self.queues[priority].get_nowait()

                        # Check if dependencies are met
                        if self._check_dependencies(task):
                            # Remove from pending and add to running
                            self.pending_tasks.pop(task.task_id, None)
                            self.running_tasks[task.task_id] = task
                            return task
                        else:
                            # Put back in queue
                            self.queues[priority].put(task)
                            continue

                    except queue.Empty:
                        continue

                # Wait for new tasks or timeout
                remaining = (deadline - datetime.now()).total_seconds()
                if remaining > 0:
                    self.condition.wait(timeout=min(remaining, 0.1))

        return None

    def complete_task(self, task_id: str, result: Optional[Dict[str, Any]] = None,
                     error: Optional[str] = None) -> bool:
        """
        Mark a task as completed

        Args:
            task_id: Task identifier
            result: Optional task result
            error: Optional error message if failed

        Returns:
            True if successful
        """
        with self.lock:
            task = self.running_tasks.pop(task_id, None)

            if not task:
                return False

            # Update agent load
            agent_id = self._get_agent_for_task(task)
            if agent_id:
                self.agent_load[agent_id] = self.agent_load.get(agent_id, 1) - 1

            if error:
                # Check if we should retry
                if task.retry_count < task.max_retries:
                    task.retry_count += 1
                    self.pending_tasks[task_id] = task
                    self.queues[task.priority].put(task)
                    self.condition.notify()
                    frappe.logger().info(f"Retrying task {task_id} (attempt {task.retry_count})")
                    return True
                else:
                    self.failed_tasks[task_id] = task
                    frappe.logger().error(f"Task {task_id} failed after {task.max_retries} retries")
            else:
                self.completed_tasks[task_id] = task
                self.condition.notify()

            return True

    def get_task_status(self, task_id: str) -> Optional[str]:
        """
        Get the status of a task

        Args:
            task_id: Task identifier

        Returns:
            Status string or None
        """
        with self.lock:
            if task_id in self.pending_tasks:
                return 'pending'
            elif task_id in self.running_tasks:
                return 'running'
            elif task_id in self.completed_tasks:
                return 'completed'
            elif task_id in self.failed_tasks:
                return 'failed'

        return None

    def get_queue_stats(self) -> Dict[str, int]:
        """
        Get statistics about task queues

        Returns:
            Dictionary with queue sizes
        """
        with self.lock:
            return {
                'critical': self.queues[Priority.CRITICAL].qsize(),
                'high': self.queues[Priority.HIGH].qsize(),
                'normal': self.queues[Priority.NORMAL].qsize(),
                'low': self.queues[Priority.LOW].qsize(),
                'pending': len(self.pending_tasks),
                'running': len(self.running_tasks),
                'completed': len(self.completed_tasks),
                'failed': len(self.failed_tasks),
                'scheduled': len(self.scheduled_tasks)
            }

    def balance_load(self) -> None:
        """Rebalance tasks across agents based on current load"""
        with self.lock:
            # Calculate average load
            if not self.agent_load:
                return

            avg_load = sum(self.agent_load.values()) / len(self.agent_load)

            # Find overloaded and underloaded agents
            overloaded = [aid for aid, load in self.agent_load.items() if load > avg_load * 1.5]
            underloaded = [aid for aid, load in self.agent_load.items() if load < avg_load * 0.5]

            if not overloaded or not underloaded:
                return

            frappe.logger().info(f"Load balancing: Overloaded={overloaded}, Underloaded={underloaded}")

            # Note: Actual task migration would require more complex logic
            # This is a placeholder for the rebalancing mechanism

    def detect_deadlocks(self) -> List[str]:
        """
        Detect potential deadlocks in task dependencies

        Returns:
            List of task IDs involved in deadlocks
        """
        deadlocks = []

        with self.lock:
            # Build dependency graph
            graph = {}
            for task_id, task in self.pending_tasks.items():
                graph[task_id] = task.dependencies

            # Check for cycles using DFS
            visited = set()
            rec_stack = set()

            def has_cycle(node, path=None):
                if path is None:
                    path = []

                visited.add(node)
                rec_stack.add(node)
                path.append(node)

                for dep in graph.get(node, []):
                    if dep not in visited:
                        if has_cycle(dep, path):
                            return True
                    elif dep in rec_stack:
                        # Found a cycle
                        cycle_start = path.index(dep)
                        deadlocks.extend(path[cycle_start:])
                        return True

                rec_stack.remove(node)
                path.pop()
                return False

            for task_id in list(graph.keys()):
                if task_id not in visited:
                    has_cycle(task_id)

        return list(set(deadlocks))

    def _worker_loop(self) -> None:
        """Worker thread loop for processing scheduled tasks"""
        while self.running:
            try:
                self._check_scheduled_tasks()

                # Auto-balance load periodically
                if datetime.now().second % 30 == 0:
                    self.balance_load()

                # Check for deadlocks periodically
                if datetime.now().second % 60 == 0:
                    deadlocks = self.detect_deadlocks()
                    if deadlocks:
                        frappe.logger().warning(f"Potential deadlocks detected: {deadlocks}")

                threading.Event().wait(1)

            except Exception as e:
                frappe.log_error(f"Task Scheduler Worker Error: {str(e)}", "Task Scheduler")

    def _check_scheduled_tasks(self) -> None:
        """Check for and queue scheduled tasks that are due"""
        now = datetime.now()

        while self.scheduled_tasks:
            if self.scheduled_tasks[0]['scheduled_time'] <= now:
                scheduled = heapq.heappop(self.scheduled_tasks)
                task_id = scheduled['task_id']

                if task_id in self.pending_tasks:
                    task = self.pending_tasks[task_id]
                    self.queues[task.priority].put(task)
            else:
                break

    def _check_dependencies(self, task: ScheduledTask) -> bool:
        """Check if task dependencies are met"""
        for dep_id in task.dependencies:
            if dep_id not in self.completed_tasks:
                return False
        return True

    def _get_agent_for_task(self, task: ScheduledTask) -> Optional[str]:
        """Get the agent ID executing a task"""
        # This would need to track which agent is running which task
        # For now, return None as placeholder
        return None

    def set_agent_capacity(self, agent_id: str, capacity: int) -> None:
        """
        Set maximum concurrent task capacity for an agent

        Args:
            agent_id: Agent identifier
            capacity: Maximum concurrent tasks
        """
        with self.lock:
            self.agent_capacity[agent_id] = capacity

    def get_agent_load(self, agent_id: str) -> int:
        """
        Get current load for an agent

        Args:
            agent_id: Agent identifier

        Returns:
            Current number of active tasks
        """
        return self.agent_load.get(agent_id, 0)

    def cleanup_old_tasks(self, older_than_hours: int = 24) -> int:
        """
        Clean up old completed and failed tasks

        Args:
            older_than_hours: Remove tasks older than this many hours

        Returns:
            Number of tasks cleaned up
        """
        cutoff = datetime.now() - timedelta(hours=older_than_hours)
        cleaned = 0

        with self.lock:
            # Clean completed tasks
            to_remove = [
                task_id for task_id, task in self.completed_tasks.items()
                if task.created_at < cutoff
            ]
            for task_id in to_remove:
                self.completed_tasks.pop(task_id)
                cleaned += 1

            # Clean failed tasks
            to_remove = [
                task_id for task_id, task in self.failed_tasks.items()
                if task.created_at < cutoff
            ]
            for task_id in to_remove:
                self.failed_tasks.pop(task_id)
                cleaned += 1

        return cleaned
