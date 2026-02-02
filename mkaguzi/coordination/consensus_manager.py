# Consensus Manager for Multi-Agent System
# =============================================================================
# Implements consensus mechanisms for multi-agent decision making

import frappe
from typing import Any, Dict, List, Optional, Set
from datetime import datetime, timedelta
from enum import Enum
import threading

from ..agents.agent_manager import get_agent_manager
from ..agents.message_bus import MessageBus


class ConsensusStatus(Enum):
    """Consensus status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    REACHED = "reached"
    FAILED = "failed"
    TIMEOUT = "timeout"


class Vote:
    """A vote in a consensus process"""

    def __init__(self, voter_id: str, proposal_id: str, decision: bool,
                 reason: Optional[str] = None, timestamp: Optional[datetime] = None):
        self.voter_id = voter_id
        self.proposal_id = proposal_id
        self.decision = decision  # True = approve, False = reject
        self.reason = reason
        self.timestamp = timestamp or datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert vote to dictionary"""
        return {
            'voter_id': self.voter_id,
            'proposal_id': self.proposal_id,
            'decision': self.decision,
            'reason': self.reason,
            'timestamp': self.timestamp.isoformat()
        }


class Proposal:
    """A proposal for consensus voting"""

    def __init__(self, proposal_id: str, title: str, description: str,
                 proposer_id: str, data: Dict[str, Any],
                 quorum: int = 3, timeout_seconds: int = 300):
        self.proposal_id = proposal_id
        self.title = title
        self.description = description
        self.proposer_id = proposer_id
        self.data = data
        self.quorum = quorum  # Minimum votes required
        self.timeout_seconds = timeout_seconds
        self.created_at = datetime.now()
        self.expires_at = datetime.now() + timedelta(seconds=timeout_seconds)
        self.status = ConsensusStatus.PENDING
        self.votes: Dict[str, Vote] = {}
        self.required_agents: Set[str] = set()
        self.responded_agents: Set[str] = set()

    def add_vote(self, vote: Vote) -> None:
        """Add a vote to the proposal"""
        self.votes[vote.voter_id] = vote
        self.responded_agents.add(vote.voter_id)

        # Update status if all required agents have responded
        if self.responded_agents >= self.required_agents:
            self.status = ConsensusStatus.IN_PROGRESS

    def has_quorum(self) -> bool:
        """Check if proposal has reached quorum"""
        return len(self.votes) >= self.quorum

    def get_result(self) -> Optional[bool]:
        """
        Get consensus result if available

        Returns:
            True if consensus reached for approval, False for rejection,
            None if no consensus yet
        """
        if not self.has_quorum():
            return None

        approvals = sum(1 for vote in self.votes.values() if vote.decision)
        rejections = len(self.votes) - approvals

        return approvals > rejections

    def is_expired(self) -> bool:
        """Check if proposal has expired"""
        return datetime.now() > self.expires_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert proposal to dictionary"""
        return {
            'proposal_id': self.proposal_id,
            'title': self.title,
            'description': self.description,
            'proposer_id': self.proposer_id,
            'quorum': self.quorum,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'votes': {k: v.to_dict() for k, v in self.votes.items()},
            'vote_count': len(self.votes),
            'approvals': sum(1 for v in self.votes.values() if v.decision),
            'rejections': sum(1 for v in self.votes.values() if not v.decision),
            'result': self.get_result()
        }


class ConsensusManager:
    """
    Manages consensus processes for multi-agent decision making.
    Supports voting, proposal management, and result determination.
    """

    def __init__(self):
        """Initialize the Consensus Manager"""
        self.agent_manager = get_agent_manager()
        self.message_bus = MessageBus()

        # Proposal storage
        self.proposals: Dict[str, Proposal] = {}
        self.proposal_history: List[str] = []

        # Voting configuration
        self.default_quorum = 3
        self.default_timeout = 300  # 5 minutes

        # Synchronization
        self.lock = threading.Lock()

        # Subscribe to consensus-related messages
        self._setup_message_handlers()

    def _setup_message_handlers(self) -> None:
        """Setup message handlers for consensus communication"""
        def handle_vote(message_data, source):
            return self.handle_vote_message(message_data, source)

        def handle_response(message_data, source):
            return self.handle_proposal_response(message_data, source)

        # Subscribe to message types
        self.message_bus.subscribe('consensus_manager', [
            'consensus_vote',
            'consensus_response',
            'consensus_request'
        ])

        # Register handlers (simplified - in production would use proper registry)
        # self.message_bus.message_handlers['consensus_vote'] = handle_vote
        # self.message_bus.message_handlers['consensus_response'] = handle_response

    def create_proposal(self, title: str, description: str,
                       proposer_id: str, data: Dict[str, Any],
                       required_agents: Optional[List[str]] = None,
                       quorum: Optional[int] = None,
                       timeout_seconds: Optional[int] = None) -> Proposal:
        """
        Create a new proposal for consensus voting

        Args:
            title: Proposal title
            description: Proposal description
            proposer_id: Agent creating the proposal
            data: Proposal data
            required_agents: Agents that must vote
            quorum: Minimum votes required
            timeout_seconds: Time limit for voting

        Returns:
            Proposal object
        """
        proposal_id = f"proposal_{datetime.now().timestamp()}_{id(data)}"

        proposal = Proposal(
            proposal_id=proposal_id,
            title=title,
            description=description,
            proposer_id=proposer_id,
            data=data,
            quorum=quorum or self.default_quorum,
            timeout_seconds=timeout_seconds or self.default_timeout
        )

        if required_agents:
            proposal.required_agents = set(required_agents)

        with self.lock:
            self.proposals[proposal_id] = proposal
            self.proposal_history.append(proposal_id)

        # Notify required agents
        self._send_proposal_request(proposal)

        frappe.logger().info(f"Created proposal {proposal_id}: {title}")

        return proposal

    def cast_vote(self, proposal_id: str, voter_id: str,
                 decision: bool, reason: Optional[str] = None) -> bool:
        """
        Cast a vote for a proposal

        Args:
            proposal_id: Proposal identifier
            voter_id: Agent casting the vote
            decision: True for approve, False for reject
            reason: Optional reason for the vote

        Returns:
            True if vote was recorded
        """
        with self.lock:
            proposal = self.proposals.get(proposal_id)

            if not proposal:
                frappe.logger().warning(f"Proposal {proposal_id} not found")
                return False

            if proposal.status not in [ConsensusStatus.PENDING, ConsensusStatus.IN_PROGRESS]:
                frappe.logger().warning(f"Cannot vote on {proposal_id} with status {proposal.status}")
                return False

            if proposal.is_expired():
                proposal.status = ConsensusStatus.TIMEOUT
                return False

            # Create and add vote
            vote = Vote(
                voter_id=voter_id,
                proposal_id=proposal_id,
                decision=decision,
                reason=reason
            )

            proposal.add_vote(vote)

            frappe.logger().info(f"Vote cast for {proposal_id} by {voter_id}: {decision}")

            # Check if we can determine result
            if proposal.has_quorum():
                result = proposal.get_result()
                if result is not None:
                    proposal.status = ConsensusStatus.REACHED
                    self._notify_consensus_result(proposal)
                else:
                    # Check if it's impossible to reach consensus
                    if self._is_impossible_to_reach_consensus(proposal):
                        proposal.status = ConsensusStatus.FAILED
                        self._notify_consensus_result(proposal)

            return True

    def get_proposal(self, proposal_id: str) -> Optional[Proposal]:
        """
        Get a proposal by ID

        Args:
            proposal_id: Proposal identifier

        Returns:
            Proposal or None
        """
        return self.proposals.get(proposal_id)

    def get_active_proposals(self) -> List[Proposal]:
        """
        Get all active proposals

        Returns:
            List of active proposals
        """
        with self.lock:
            return [
                p for p in self.proposals.values()
                if p.status in [ConsensusStatus.PENDING, ConsensusStatus.IN_PROGRESS]
            ]

    def get_proposal_result(self, proposal_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the result of a proposal

        Args:
            proposal_id: Proposal identifier

        Returns:
            Result dictionary or None
        """
        proposal = self.get_proposal(proposal_id)

        if not proposal:
            return None

        result = proposal.get_result()

        if result is None:
            return None

        return {
            'proposal_id': proposal_id,
            'result': result,
            'status': proposal.status.value,
            'vote_summary': {
                'total_votes': len(proposal.votes),
                'approvals': sum(1 for v in proposal.votes.values() if v.decision),
                'rejections': sum(1 for v in proposal.votes.values() if not v.decision)
            },
            'timestamp': datetime.now().isoformat()
        }

    def check_expired_proposals(self) -> List[str]:
        """
        Check for and mark expired proposals

        Returns:
            List of expired proposal IDs
        """
        expired = []

        with self.lock:
            for proposal_id, proposal in self.proposals.items():
                if proposal.is_expired() and proposal.status in [ConsensusStatus.PENDING, ConsensusStatus.IN_PROGRESS]:
                    proposal.status = ConsensusStatus.TIMEOUT
                    expired.append(proposal_id)
                    self._notify_consensus_result(proposal)

        return expired

    def cleanup_old_proposals(self, older_than_hours: int = 24) -> int:
        """
        Clean up old proposals from memory

        Args:
            older_than_hours: Remove proposals older than this

        Returns:
            Number of proposals cleaned up
        """
        cutoff = datetime.now() - timedelta(hours=older_than_hours)
        cleaned = 0

        with self.lock:
            to_remove = [
                pid for pid, proposal in self.proposals.items()
                if proposal.created_at < cutoff and
                proposal.status in [ConsensusStatus.REACHED, ConsensusStatus.FAILED, ConsensusStatus.TIMEOUT]
            ]

            for proposal_id in to_remove:
                self.proposals.pop(proposal_id)
                cleaned += 1

        return cleaned

    def handle_vote_message(self, message_data: Dict[str, Any], source: str) -> Optional[Dict[str, Any]]:
        """
        Handle incoming vote message

        Args:
            message_data: Message data containing vote
            source: Source agent ID

        Returns:
            Response message
        """
        proposal_id = message_data.get('proposal_id')
        decision = message_data.get('decision')
        reason = message_data.get('reason')

        if proposal_id and decision is not None:
            success = self.cast_vote(proposal_id, source, decision, reason)

            return {
                'proposal_id': proposal_id,
                'success': success,
                'message': 'Vote recorded' if success else 'Vote failed'
            }

        return None

    def handle_proposal_response(self, message_data: Dict[str, Any], source: str) -> Optional[Dict[str, Any]]:
        """
        Handle proposal response from an agent

        Args:
            message_data: Message data
            source: Source agent ID

        Returns:
            Response message
        """
        proposal_id = message_data.get('proposal_id')
        decision = message_data.get('decision')
        reason = message_data.get('reason')

        if proposal_id and decision is not None:
            success = self.cast_vote(proposal_id, source, decision, reason)

            return {
                'proposal_id': proposal_id,
                'success': success
            }

        return None

    def _send_proposal_request(self, proposal: Proposal) -> None:
        """Send proposal request to required agents"""
        for agent_id in proposal.required_agents:
            try:
                self.message_bus.send_direct(
                    target_agent_id=agent_id,
                    message_type='consensus_request',
                    data={
                        'proposal_id': proposal.proposal_id,
                        'title': proposal.title,
                        'description': proposal.description,
                        'data': proposal.data,
                        'expires_at': proposal.expires_at.isoformat()
                    },
                    source='consensus_manager'
                )
            except Exception as e:
                frappe.log_error(f"Failed to send proposal request to {agent_id}: {str(e)}", "Consensus Manager")

    def _notify_consensus_result(self, proposal: Proposal) -> None:
        """Notify all participants of consensus result"""
        result = proposal.get_result()

        notification_data = {
            'proposal_id': proposal.proposal_id,
            'title': proposal.title,
            'status': proposal.status.value,
            'result': result,
            'vote_count': len(proposal.votes),
            'approvals': sum(1 for v in proposal.votes.values() if v.decision),
            'rejections': sum(1 for v in proposal.votes.values() if not v.decision)
        }

        # Notify all participants
        for voter_id in proposal.votes.keys():
            try:
                self.message_bus.send_direct(
                    target_agent_id=voter_id,
                    message_type='consensus_result',
                    data=notification_data,
                    source='consensus_manager'
                )
            except Exception as e:
                frappe.log_error(f"Failed to send result to {voter_id}: {str(e)}", "Consensus Manager")

    def _is_impossible_to_reach_consensus(self, proposal: Proposal) -> bool:
        """
        Check if it's mathematically impossible to reach consensus

        Args:
            proposal: Proposal to check

        Returns:
            True if impossible to reach consensus
        """
        remaining_votes = len(proposal.required_agents) - len(proposal.votes)
        current_approvals = sum(1 for v in proposal.votes.values() if v.decision)
        current_rejections = len(proposal.votes) - current_approvals

        # Even with all remaining votes as approvals, can't reach majority
        if current_approvals + remaining_votes <= current_rejections:
            return True

        # Even with all remaining votes as rejections, can't reach majority
        if current_rejections + remaining_votes <= current_approvals:
            return True

        return False

    def set_default_quorum(self, quorum: int) -> None:
        """Set the default quorum requirement"""
        if quorum > 0:
            self.default_quorum = quorum

    def set_default_timeout(self, timeout_seconds: int) -> None:
        """Set the default timeout for proposals"""
        if timeout_seconds > 0:
            self.default_timeout = timeout_seconds
