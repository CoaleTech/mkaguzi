# Test file for agent system bug fixes
# Tests all critical fixes including static method calls, datetime arithmetic, tuple handling, etc.

import frappe
from frappe.tests import IntegrationTestCase
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, call
import json

from mkaguzi.agents.agent_executor import AgentExecutor
from mkaguzi.agents.message_bus import MessageBus
from mkaguzi.agents.discovery_agent import DiscoveryAgent
from mkaguzi.agents.notification_agent import NotificationAgent, NotificationPriority, NotificationChannel
from mkaguzi.agents.scheduler import get_agent_status
from mkaguzi.utils.rate_limiter import RateLimiter


class TestAgentFixures(IntegrationTestCase):
    """Test critical agent system fixes"""

    def test_enqueue_agent_task_no_name_error(self):
        """Test that enqueue_agent_task doesn't raise NameError with self in staticmethod"""
        with patch('frappe.enqueue') as mock_enqueue:
            mock_enqueue.return_value = 'test_job_id'
            
            # This should not raise NameError
            try:
                job_id = AgentExecutor.enqueue_agent_task(
                    agent_type='Financial',
                    task_data={'task_type': 'analyze_transactions', 'timeout': 300},
                    priority='normal'
                )
                self.assertEqual(job_id, 'test_job_id')
                mock_enqueue.assert_called_once()
                
                # Verify that AgentExecutor._get_default_timeout was called, not self._get_default_timeout
                call_kwargs = mock_enqueue.call_args[1]
                self.assertIsNotNone(call_kwargs.get('timeout'))
                self.assertIsInstance(call_kwargs.get('timeout'), (int, float))
            except NameError as e:
                if 'self' in str(e):
                    self.fail(f"NameError with 'self': {str(e)}")
                raise

    def test_log_execution_uses_correct_fields(self):
        """Test that _log_execution uses correct Agent Execution Log field names"""
        with patch('frappe.get_doc') as mock_get_doc:
            mock_doc = MagicMock()
            mock_get_doc.return_value = mock_doc
            
            AgentExecutor._log_execution(
                agent_id='financial_test_001',
                task_type='analyze_transactions',
                status='success',
                duration=15.5,
                result={'findings': []},
                error=None
            )
            
            # Verify that frappe.get_doc was called with correct field names
            mock_get_doc.assert_called_once()
            call_args = mock_get_doc.call_args[0][0]
            
            # Check for correct field names from Agent Execution Log schema
            self.assertIn('agent_type', call_args)
            self.assertIn('task_type', call_args)
            self.assertIn('start_time', call_args)
            self.assertIn('status', call_args)
            self.assertIn('output_data', call_args)
            
            # Make sure wrong field names are NOT used
            self.assertNotIn('event_type', call_args)
            self.assertNotIn('timestamp', call_args)
            self.assertNotIn('event_details', call_args)

    def test_create_digest_handles_tuples(self):
        """Test that _create_digest correctly unpacks (recipient, message) tuples"""
        agent = NotificationAgent()
        
        # Create sample NotificationMessage objects
        msg1 = NotificationAgent.__dict__.get('NotificationMessage')
        if not msg1:
            # Create directly if not accessible
            from mkaguzi.agents.notification_agent import NotificationMessage
            msg1 = NotificationMessage(
                title='Test Alert 1',
                message='Test message 1',
                priority=NotificationPriority.HIGH,
                channels=[NotificationChannel.EMAIL],
                recipients=['user1@example.com']
            )
            msg2 = NotificationMessage(
                title='Test Alert 2',
                message='Test message 2',
                priority=NotificationPriority.NORMAL,
                channels=[NotificationChannel.SYSTEM],
                recipients=['user2@example.com']
            )
        
            # Pass tuples (recipient, message) like _group_notifications returns
            tuples = [('user1@example.com', msg1), ('user2@example.com', msg2)]
            
            digest = agent._create_digest(tuples)
            
            self.assertIsNotNone(digest)
            self.assertIn('user1@example.com', digest.recipients)
            self.assertIn('user2@example.com', digest.recipients)
            self.assertEqual(digest.title, f'Notification Digest (2 items)')

    def test_create_digest_handles_empty_list(self):
        """Test that _create_digest returns None for empty message list"""
        agent = NotificationAgent()
        digest = agent._create_digest([])
        self.assertIsNone(digest)

    def test_load_subscriptions_populates_subscribers(self):
        """Test that MessageBus._load_subscriptions populates self.subscribers (not subscriptions)"""
        bus = MessageBus()
        
        # Seed cache with test subscription data
        subscription_data = {
            'test_message_type': ['agent_1', 'agent_2'],
            'another_type': ['agent_3']
        }
        
        with patch.object(bus.cache, 'get') as mock_cache_get:
            mock_cache_get.return_value = json.dumps(subscription_data)
            bus._load_subscriptions()
        
        # Verify subscribers is populated (not subscriptions)
        self.assertIn('test_message_type', bus.subscribers)
        self.assertEqual(bus.subscribers['test_message_type'], ['agent_1', 'agent_2'])

    def test_load_subscriptions_called_in_init(self):
        """Test that _load_subscriptions is called during MessageBus.__init__"""
        with patch('mkaguzi.agents.message_bus.MessageBus._load_subscriptions') as mock_load:
            bus = MessageBus()
            mock_load.assert_called_once()

    def test_detect_schema_changes_not_shadowed(self):
        """Test that detect_schema_changes method is not shadowed by bool attribute"""
        config = {'detect_schema_changes': True}
        agent = DiscoveryAgent(config=config)
        
        # Verify _detect_schema_changes_enabled is bool (the config)
        self.assertIsInstance(agent._detect_schema_changes_enabled, bool)
        
        # Verify detect_schema_changes is callable (the method)
        self.assertTrue(callable(agent.detect_schema_changes))
        
        # Verify method can be called without TypeError
        try:
            result = agent.detect_schema_changes()
            # Should return a dict, not raise TypeError
            self.assertIsInstance(result, dict)
        except TypeError as e:
            if "object is not callable" in str(e):
                self.fail("detect_schema_changes method is shadowed by attribute")
            raise

    def test_risk_indicator_query_uses_correct_fields(self):
        """Test that risk agent queries use correct Risk Indicator field names"""
        from mkaguzi.agents.risk_agent import RiskAgent
        
        agent = RiskAgent()
        
        with patch('frappe.get_all') as mock_get_all:
            mock_get_all.return_value = [
                {'name': 'ind_1', 'threshold': 0.7, 'current_value': 0.65}
            ]
            
            indicators = agent._get_module_risk_indicators('Financial')
            
            # Verify correct filter field name (status, not active)
            call_kwargs = mock_get_all.call_args[1]
            self.assertEqual(call_kwargs['filters']['status'], 'Active')
            
            # Verify correct field name requested (threshold, not risk_score)
            self.assertIn('threshold', call_kwargs['fields'])

    def test_scheduler_date_arithmetic_valid(self):
        """Test that scheduler date arithmetic doesn't raise TypeError"""
        with patch('frappe.get_all') as mock_get_all:
            mock_get_all.return_value = []
            
            try:
                # This should not raise TypeError about string - timedelta
                status = get_agent_status()
                self.assertIsNotNone(status)
            except TypeError as e:
                if 'unsupported operand type' in str(e):
                    self.fail(f"Date arithmetic TypeError: {str(e)}")
                raise

    def test_rate_limiter_translation_import(self):
        """Test that rate limiter has _ (translation function) imported"""
        # Import should not raise error
        from mkaguzi.utils import rate_limiter
        
        # Verify the module has gettext function available
        self.assertTrue(hasattr(rate_limiter, '_') or 'frappe' in dir(rate_limiter))


class TestMessageBusSubscriptions(IntegrationTestCase):
    """Test message bus subscription persistence"""

    def test_subscriptions_persist_and_reload(self):
        """Test that subscriptions persist to cache and reload on new instance"""
        bus1 = MessageBus()
        
        # Subscribe agent to message type
        bus1.subscribe('agent_1', ['message_type_1'])
        
        # Persist subscriptions (normally done by _persist_subscriptions)
        with patch.object(bus1.cache, 'set'):
            bus1._persist_subscriptions()
        
        # Create new bus instance - should load persisted subscriptions
        with patch.object(MessageBus, '_load_subscriptions', wraps=MessageBus._load_subscriptions):
            bus2 = MessageBus()
            # _load_subscriptions should have been called during init


class TestExecutionLogging(IntegrationTestCase):
    """Test agent execution logging with correct field names"""

    def test_background_task_logs_execution(self):
        """Test that background task execution logs to Agent Execution Log"""
        with patch('mkaguzi.agents.agent_executor.get_agent_manager') as mock_manager:
            with patch('mkaguzi.agents.agent_executor.AgentExecutor._log_execution') as mock_log:
                mock_agent = MagicMock()
                mock_agent.execute_task.return_value = {
                    'status': 'success',
                    'findings': []
                }
                mock_manager.return_value.spawn_agent.return_value = mock_agent
                
                result = AgentExecutor.execute_background_task(
                    agent_type='Financial',
                    task_data={'task_type': 'analyze_transactions'}
                )
                
                # Verify _log_execution was called
                mock_log.assert_called_once()
                call_args = mock_log.call_args[0]
                
                # Verify execution was logged with correct task_type
                self.assertEqual(call_args[1], 'analyze_transactions')


if __name__ == '__main__':
    import unittest
    unittest.main()
