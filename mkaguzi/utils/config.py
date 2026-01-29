"""
Configuration management for Mkaguzi
"""
import frappe

class MkaguziConfig:
    """Centralized configuration management"""

    @staticmethod
    def get_default_notification_recipients():
        """
        Get default notification recipients from system settings

        Returns:
            List of email addresses
        """
        try:
            # Try to get from Audit Settings doctype
            recipients = frappe.db.get_single_value('Audit Settings', 'default_notification_recipients')

            if recipients:
                return [email.strip() for email in recipients.split(',') if email.strip()]

            # Fallback to system admin
            admin_email = frappe.db.get_value('User', {'administrator': 1}, 'email')

            if admin_email:
                return [admin_email]

            # Last resort - system default
            return [frappe.get_system_conf('email_from') or 'system@example.com']

        except Exception:
            return []

    @staticmethod
    def get_sync_alert_recipients():
        """
        Get sync alert recipients

        Returns:
            List of email addresses
        """
        try:
            recipients = frappe.db.get_single_value('Audit Settings', 'sync_alert_recipients')

            if recipients:
                return [email.strip() for email in recipients.split(',') if email.strip()]

            # Get system administrators
            recipients = frappe.get_all('User',
                filters={'enabled': 1, 'role_profile_name': ['like', '%System%']},
                pluck='email')

            return recipients or MkaguziConfig.get_default_notification_recipients()

        except Exception:
            return MkaguziConfig.get_default_notification_recipients()