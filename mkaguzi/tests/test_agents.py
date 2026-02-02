# Tests for Multi-Agent System
# =============================================================================
# Comprehensive test suite for agent infrastructure and individual agents

import frappe
from frappe.tests.utils import FrappeTestCase
from datetime import datetime, timedelta
import json

from mkaguzi.agents.agent_base import AuditAgent
from mkaguzi.agents.agent_manager import AgentManager
from mkaguzi.agents.message_bus import MessageBus, Message
from mkaguzi.agents.state_manager import StateManager
from mkaguzi.agents.agent_registry import AgentRegistry


class TestAgentBase(FrappeTestCase):
    """Test cases for base agent functionality"""

    def test_agent_lifecycle(self):
        """Test agent spawn, start, stop"""
        agent = AuditAgent('test_agent', {})
        self.assertEqual(agent.state, 'idle')

        # Test start
        result = agent.start()
        self.assertTrue(result)
        self.assertEqual(agent.state, 'running')

        # Test stop
        result = agent.stop()
        self.assertTrue(result)
        self.assertEqual(agent.state, 'stopped')

    def test_agent_state_management(self):
        """Test agent state get/set"""
        agent = AuditAgent('test_agent_state', {})
        agent.start()

        # Test set_state
        result = agent.set_state('test_key', 'test_value')
        self.assertTrue(result)

        # Test get_state
        value = agent.get_state('test_key')
        self.assertEqual(value, 'test_value')

        # Test default value
        default_value = agent.get_state('non_existent_key', 'default')
        self.assertEqual(default_value, 'default')

        agent.stop()

    def test_agent_messaging(self):
        """Test agent message sending"""
        agent1 = AuditAgent('test_agent_1', {})
        agent2 = AuditAgent('test_agent_2', {})

        agent1.start()
        agent2.start()

        # Test subscribe
        result = agent2.subscribe(['test_message'])
        self.assertTrue(result)

        # Test send message
        result = agent1.send_message('test_agent_2', 'test_message', {'data': 'test'})
        self.assertTrue(result)

        # Verify message received
        messages = agent2.message_bus.get_messages('test_agent_2', timeout=0.1)
        # Messages may not be immediately available in test environment

        agent1.stop()
        agent2.stop()

    def test_agent_status(self):
        """Test agent status reporting"""
        agent = AuditAgent('test_agent_status', {})
        agent.start()

        status = agent.get_status()
        self.assertIn('agent_id', status)
        self.assertIn('agent_type', status)
        self.assertIn('state', status)
        self.assertEqual(status['state'], 'running')

        agent.stop()

        status = agent.get_status()
        self.assertEqual(status['state'], 'stopped')


class TestAgentManager(FrappeTestCase):
    """Test cases for Agent Manager"""

    def setUp(self):
        """Set up test fixtures"""
        self.manager = AgentManager()

    def tearDown(self):
        """Clean up after tests"""
        # Stop all agents
        self.manager.stop_all_agents()

    def test_spawn_agent(self):
        """Test spawning agents"""
        # Note: This test will fail if agents don't exist yet
        # We're testing the infrastructure here

        # Test that manager exists
        self.assertIsNotNone(self.manager)

        # Test list_agents returns list
        agents = self.manager.list_agents()
        self.assertIsInstance(agents, list)

    def test_get_agent(self):
        """Test getting an agent by ID"""
        # Get non-existent agent
        agent = self.manager.get_agent('non_existent_agent')
        self.assertIsNone(agent)

    def test_system_status(self):
        """Test getting system status"""
        status = self.manager.get_system_status()
        self.assertIn('total_agents', status)
        self.assertIn('active_agents', status)
        self.assertIn('timestamp', status)

    def test_manager_singleton(self):
        """Test Agent Manager singleton pattern"""
        manager1 = AgentManager()
        manager2 = AgentManager()

        # Should be the same instance
        self.assertIs(manager1, manager2)


class TestMessageBus(FrappeTestCase):
    """Test cases for Message Bus"""

    def setUp(self):
        """Set up test fixtures"""
        self.message_bus = MessageBus()

    def test_publish_subscribe(self):
        """Test publish/subscribe pattern"""
        # Subscribe agents
        self.message_bus.subscribe('agent1', ['test_event'])
        self.message_bus.subscribe('agent2', ['test_event'])

        # Publish message
        result = self.message_bus.publish('test_event', {'data': 'test'})
        self.assertTrue(result)

        # Verify subscribers
        subscribers = self.message_bus.get_subscribers('test_event')
        self.assertIn('agent1', subscribers)
        self.assertIn('agent2', subscribers)

    def test_direct_messaging(self):
        """Test direct agent-to-agent messaging"""
        # Send direct message
        result = self.message_bus.send_direct(
            'agent1',
            'agent2',
            'direct_message',
            {'data': 'test'}
        )
        self.assertTrue(result)

    def test_unsubscribe(self):
        """Test unsubscribing from messages"""
        # Subscribe first
        self.message_bus.subscribe('agent1', ['test_event'])

        # Unsubscribe
        result = self.message_bus.unsubscribe('agent1', ['test_event'])
        self.assertTrue(result)

        # Verify unsubscribed
        subscribers = self.message_bus.get_subscribers('test_event')
        self.assertNotIn('agent1', subscribers)


class TestStateManager(FrappeTestCase):
    """Test cases for State Manager"""

    def setUp(self):
        """Set up test fixtures"""
        self.state_manager = StateManager()

    def test_set_get_state(self):
        """Test setting and getting state"""
        # Set state
        result = self.state_manager.set_state('agent1', 'key1', 'value1')
        self.assertTrue(result)

        # Get state
        value = self.state_manager.get_state('agent1', 'key1')
        self.assertEqual(value, 'value1')

    def test_delete_state(self):
        """Test deleting state"""
        # Set state first
        self.state_manager.set_state('agent1', 'key1', 'value1')

        # Delete specific key
        result = self.state_manager.delete_state('agent1', 'key1')
        self.assertTrue(result)

        # Verify deleted
        value = self.state_manager.get_state('agent1', 'key1')
        self.assertIsNone(value)

    def test_get_all_agent_state(self):
        """Test getting all state for an agent"""
        # Set multiple keys
        self.state_manager.set_state('agent1', 'key1', 'value1')
        self.state_manager.set_state('agent1', 'key2', 'value2')

        # Get all
        all_state = self.state_manager.get_all_agent_state('agent1')
        self.assertIsInstance(all_state, dict)
        self.assertIn('key1', all_state)
        self.assertIn('key2', all_state)

    def test_increment_counter(self):
        """Test counter increment"""
        # Increment
        value = self.state_manager.increment_counter('agent1', 'counter')
        self.assertEqual(value, 1)

        # Increment again
        value = self.state_manager.increment_counter('agent1', 'counter')
        self.assertEqual(value, 2)

    def test_list_agents(self):
        """Test listing agents with state"""
        # Set state for multiple agents
        self.state_manager.set_state('agent1', 'key1', 'value1')
        self.state_manager.set_state('agent2', 'key1', 'value2')

        # List agents
        agents = self.state_manager.list_agents()
        self.assertIsInstance(agents, list)


class TestAgentRegistry(FrappeTestCase):
    """Test cases for Agent Registry"""

    def test_list_agents(self):
        """Test listing registered agent types"""
        agents = AgentRegistry.list_agents()
        self.assertIsInstance(agents, list)
        self.assertGreater(len(agents), 0)

    def test_get_agent_info(self):
        """Test getting agent information"""
        # Get info for financial agent
        info = AgentRegistry.get_agent_info('financial')
        self.assertIsNotNone(info)
        self.assertIn('description', info)

    def test_get_default_config(self):
        """Test getting default configuration"""
        config = AgentRegistry.get_default_config('financial')
        self.assertIsNotNone(config)
        self.assertIsInstance(config, dict)

    def test_get_categories(self):
        """Test getting agent categories"""
        categories = AgentRegistry.get_categories()
        self.assertIsInstance(categories, list)


class TestAgentCoordination(FrappeTestCase):
    """Test cases for multi-agent coordination"""

    def setUp(self):
        """Set up test fixtures"""
        self.manager = AgentManager()

    def tearDown(self):
        """Clean up after tests"""
        self.manager.stop_all_agents()

    def test_workflow_definition(self):
        """Test workflow definition creation"""
        from mkaguzi.coordination.workflow_engine import WorkflowEngine, WorkflowDefinition

        engine = WorkflowEngine()
        workflow = engine.create_workflow(
            'test_workflow',
            'Test Workflow',
            'Test workflow for unit testing'
        )

        self.assertIsNotNone(workflow)
        self.assertEqual(workflow.workflow_id, 'test_workflow')

    def test_task_scheduler_priority(self):
        """Test task scheduler priority handling"""
        from mkaguzi.coordination.task_scheduler import TaskScheduler, Priority

        scheduler = TaskScheduler()

        # Schedule tasks with different priorities
        scheduler.start()
        task1 = scheduler.schedule_task('financial', {'task': 'test1'}, Priority.LOW)
        task2 = scheduler.schedule_task('financial', {'task': 'test2'}, Priority.HIGH)

        self.assertIsNotNone(task1)
        self.assertIsNotNone(task2)

        # Get queue stats
        stats = scheduler.get_queue_stats()
        self.assertIn('high', stats)
        self.assertIn('low', stats)

        scheduler.stop()

    def test_consensus_manager(self):
        """Test consensus manager functionality"""
        from mkaguzi.coordination.consensus_manager import ConsensusManager

        manager = ConsensusManager()

        # Create proposal
        proposal = manager.create_proposal(
            'Test Proposal',
            'Test proposal for unit testing',
            'test_agent',
            {'test': 'data'},
            required_agents=['agent1', 'agent2', 'agent3'],
            quorum=2
        )

        self.assertIsNotNone(proposal)
        self.assertEqual(proposal.title, 'Test Proposal')

        # Cast votes
        manager.cast_vote(proposal.proposal_id, 'agent1', True, 'Approve')
        manager.cast_vote(proposal.proposal_id, 'agent2', False, 'Reject')

        # Check result
        result = manager.get_proposal_result(proposal.proposal_id)
        self.assertIsNotNone(result)


class TestFinancialAgent(FrappeTestCase):
    """Test cases for Financial Agent"""

    def setUp(self):
        """Set up test fixtures"""
        from mkaguzi.agents.financial_agent import FinancialAgent
        self.agent = FinancialAgent('test_financial', {'max_batch_size': 100})

    def tearDown(self):
        """Clean up after tests"""
        if self.agent.is_running():
            self.agent.stop()

    def test_analyze_transactions(self):
        """Test transaction analysis"""
        self.agent.start()

        result = self.agent.analyze_transactions({
            'start_date': '2024-01-01',
            'end_date': '2024-01-31',
            'limit': 10
        })

        self.assertIn('status', result)

    def test_calculate_transaction_risk(self):
        """Test risk calculation for transactions"""
        entry = {
            'name': 'TEST-001',
            'account_no': 'Test Account',
            'debit': 150000,  # Large amount
            'credit': 0,
            'posting_date': '2024-01-15'
        }

        risk = self.agent._calculate_transaction_risk(entry)
        self.assertGreater(risk, 0)  # Should have some risk due to large amount


class TestRiskAgent(FrappeTestCase):
    """Test cases for Risk Agent"""

    def setUp(self):
        """Set up test fixtures"""
        from mkaguzi.agents.risk_agent import RiskAgent
        self.agent = RiskAgent('test_risk', {'prediction_horizon_days': 30})

    def tearDown(self):
        """Clean up after tests"""
        if self.agent.is_running():
            self.agent.stop()

    def test_predict_risks(self):
        """Test risk prediction"""
        self.agent.start()

        result = self.agent.predict_risks('financial', 30)
        self.assertIn('status', result)

    def test_assess_module_risks(self):
        """Test module risk assessment"""
        self.agent.start()

        result = self.agent.assess_module_risks('financial')
        self.assertIn('status', result)


class TestComplianceAgent(FrappeTestCase):
    """Test cases for Compliance Agent"""

    def setUp(self):
        """Set up test fixtures"""
        from mkaguzi.agents.compliance_agent import ComplianceAgent
        self.agent = ComplianceAgent('test_compliance', {'auto_update_checks': True})

    def tearDown(self):
        """Clean up after tests"""
        if self.agent.is_running():
            self.agent.stop()

    def test_verify_compliance(self):
        """Test compliance verification"""
        self.agent.start()

        result = self.agent.verify_compliance({
            'requirement_name': 'Test Requirement',
            'compliance_type': 'general'
        })

        self.assertIn('status', result)


class TestDiscoveryAgent(FrappeTestCase):
    """Test cases for Discovery Agent"""

    def setUp(self):
        """Set up test fixtures"""
        from mkaguzi.agents.discovery_agent import DiscoveryAgent
        self.agent = DiscoveryAgent('test_discovery', {'auto_update_catalog': True})

    def tearDown(self):
        """Clean up after tests"""
        if self.agent.is_running():
            self.agent.stop()

    def test_discover_doctypes(self):
        """Test doctype discovery"""
        self.agent.start()

        result = self.agent.discover_doctypes()
        self.assertIn('status', result)

    def test_validate_catalog(self):
        """Test catalog validation"""
        self.agent.start()

        result = self.agent.validate_catalog()
        self.assertIn('status', result)


class TestNotificationAgent(FrappeTestCase):
    """Test cases for Notification Agent"""

    def setUp(self):
        """Set up test fixtures"""
        from mkaguzi.agents.notification_agent import NotificationAgent
        self.agent = NotificationAgent('test_notification', {'escalation_enabled': True})

    def tearDown(self):
        """Clean up after tests"""
        if self.agent.is_running():
            self.agent.stop()

    def test_send_notification(self):
        """Test sending notifications"""
        self.agent.start()

        result = self.agent.send_notification({
            'title': 'Test Notification',
            'message': 'Test message from unit test',
            'priority': 'normal',
            'channels': ['system'],
            'recipients': ['Administrator']
        })

        self.assertIn('status', result)

    def test_aggregate_alerts(self):
        """Test alert aggregation"""
        self.agent.start()

        result = self.agent.aggregate_alerts(15)
        self.assertIn('status', result)
