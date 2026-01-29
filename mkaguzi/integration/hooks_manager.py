# -*- coding: utf-8 -*-
# Copyright (c) 2025, Mkaguzi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import now, now_datetime, cstr, flt
import json
import logging
import os
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class HooksManager:
    """
    Manages dynamic addition and removal of doctype hooks for audit monitoring
    """

    def __init__(self):
        self.hooks_file = os.path.join(frappe.get_app_path('mkaguzi'), 'mkaguzi', 'hooks.py')
        self.backup_hooks = {}

    def add_doctype_hooks(self, doctype_name, audit_triggers=None):
        """
        Add audit hooks for a specific doctype

        Args:
            doctype_name: Name of the doctype
            audit_triggers: List of triggers to add (optional)
        """
        try:
            if not audit_triggers:
                # Get triggers from catalog
                catalog_doc = frappe.get_doc('Audit Doctype Catalog', doctype_name)
                audit_triggers = json.loads(catalog_doc.audit_triggers or '["after_insert", "on_update"]')

            # Read current hooks
            hooks_content = self._read_hooks_file()

            # Backup current hooks
            self._backup_hooks(doctype_name, hooks_content)

            # Add new hooks
            updated_hooks = self._add_hooks_to_content(hooks_content, doctype_name, audit_triggers)

            # Write back to file
            self._write_hooks_file(updated_hooks)

            # Clear hooks cache
            self._clear_hooks_cache()

            frappe.logger().info(f"Added audit hooks for {doctype_name}")
            return {"success": True, "message": f"Hooks added for {doctype_name}"}

        except Exception as e:
            logger.error(f"Failed to add hooks for {doctype_name}: {str(e)}")
            return {"success": False, "error": str(e)}

    def remove_doctype_hooks(self, doctype_name):
        """
        Remove audit hooks for a specific doctype

        Args:
            doctype_name: Name of the doctype
        """
        try:
            # Read current hooks
            hooks_content = self._read_hooks_file()

            # Remove hooks
            updated_hooks = self._remove_hooks_from_content(hooks_content, doctype_name)

            # Write back to file
            self._write_hooks_file(updated_hooks)

            # Clear hooks cache
            self._clear_hooks_cache()

            frappe.logger().info(f"Removed audit hooks for {doctype_name}")
            return {"success": True, "message": f"Hooks removed for {doctype_name}"}

        except Exception as e:
            logger.error(f"Failed to remove hooks for {doctype_name}: {str(e)}")
            return {"success": False, "error": str(e)}

    def update_doctype_hooks(self, doctype_name, new_triggers):
        """
        Update audit hooks for a specific doctype

        Args:
            doctype_name: Name of the doctype
            new_triggers: New list of triggers
        """
        try:
            # Remove existing hooks
            self.remove_doctype_hooks(doctype_name)

            # Add new hooks
            self.add_doctype_hooks(doctype_name, new_triggers)

            return {"success": True, "message": f"Hooks updated for {doctype_name}"}

        except Exception as e:
            logger.error(f"Failed to update hooks for {doctype_name}: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_current_hooks(self, doctype_name=None):
        """
        Get current hooks configuration

        Args:
            doctype_name: Specific doctype to check (optional)

        Returns:
            dict: Current hooks configuration
        """
        try:
            hooks_content = self._read_hooks_file()

            if doctype_name:
                # Extract hooks for specific doctype
                return self._extract_doctype_hooks(hooks_content, doctype_name)
            else:
                # Return all doc_events
                return self._extract_all_doc_events(hooks_content)

        except Exception as e:
            logger.error(f"Failed to get current hooks: {str(e)}")
            return {}

    def validate_hooks_syntax(self, hooks_content=None):
        """
        Validate hooks.py syntax

        Args:
            hooks_content: Hooks content to validate (optional)

        Returns:
            dict: Validation result
        """
        try:
            if not hooks_content:
                hooks_content = self._read_hooks_file()

            # Try to compile the Python code
            compile(hooks_content, 'hooks.py', 'exec')

            return {"valid": True, "message": "Hooks syntax is valid"}

        except SyntaxError as e:
            return {"valid": False, "error": f"Syntax error: {str(e)}"}
        except Exception as e:
            return {"valid": False, "error": f"Validation error: {str(e)}"}

    def _read_hooks_file(self):
        """Read the hooks.py file content"""
        try:
            with open(self.hooks_file, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            frappe.throw(f"Hooks file not found: {self.hooks_file}")
        except Exception as e:
            frappe.throw(f"Failed to read hooks file: {str(e)}")

    def _write_hooks_file(self, content):
        """Write content to hooks.py file"""
        try:
            # Create backup before writing
            backup_file = f"{self.hooks_file}.backup.{int(datetime.now().timestamp())}"
            if os.path.exists(self.hooks_file):
                os.rename(self.hooks_file, backup_file)

            with open(self.hooks_file, 'w', encoding='utf-8') as f:
                f.write(content)

        except Exception as e:
            frappe.throw(f"Failed to write hooks file: {str(e)}")

    def _backup_hooks(self, doctype_name, content):
        """Backup current hooks for a doctype"""
        self.backup_hooks[doctype_name] = {
            'content': content,
            'timestamp': now_datetime()
        }

    def _add_hooks_to_content(self, content, doctype_name, triggers):
        """Add hooks to hooks.py content"""
        try:
            # Find the doc_events section
            doc_events_start = content.find('doc_events = {')
            if doc_events_start == -1:
                frappe.throw("doc_events section not found in hooks.py")

            # Find the end of doc_events
            brace_count = 0
            doc_events_end = doc_events_start
            for i, char in enumerate(content[doc_events_start:], doc_events_start):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        doc_events_end = i + 1
                        break

            # Extract existing doc_events
            existing_events = content[doc_events_start:doc_events_end]

            # Check if doctype already exists
            doctype_pattern = f'    "{doctype_name}": {{'
            if doctype_pattern in existing_events:
                # Update existing hooks
                updated_events = self._update_existing_hooks(existing_events, doctype_name, triggers)
            else:
                # Add new hooks
                new_hooks = self._generate_hooks_entry(doctype_name, triggers)
                # Insert before the closing brace
                insert_pos = existing_events.rfind('}')
                updated_events = existing_events[:insert_pos] + new_hooks + existing_events[insert_pos:]

            # Replace in content
            new_content = content[:doc_events_start] + updated_events + content[doc_events_end:]

            return new_content

        except Exception as e:
            frappe.throw(f"Failed to add hooks to content: {str(e)}")

    def _remove_hooks_from_content(self, content, doctype_name):
        """Remove hooks from hooks.py content"""
        try:
            # Find and remove the doctype entry
            lines = content.split('\n')
            new_lines = []
            skip_lines = False

            for line in lines:
                if f'    "{doctype_name}": {{' in line:
                    skip_lines = True
                    continue
                elif skip_lines and line.strip().startswith('    }'):
                    skip_lines = False
                    continue
                elif skip_lines and line.strip().startswith('    },'):
                    skip_lines = False
                    continue
                elif skip_lines:
                    continue
                else:
                    new_lines.append(line)

            return '\n'.join(new_lines)

        except Exception as e:
            frappe.throw(f"Failed to remove hooks from content: {str(e)}")

    def _generate_hooks_entry(self, doctype_name, triggers):
        """Generate hooks entry for a doctype"""
        hooks_lines = [f'    "{doctype_name}": {{']

        for trigger in triggers:
            hook_function = self._get_hook_function(doctype_name, trigger)
            hooks_lines.append(f'        "{trigger}": "{hook_function}",')

        # Remove trailing comma from last trigger
        if hooks_lines[-1].endswith(','):
            hooks_lines[-1] = hooks_lines[-1][:-1]

        hooks_lines.append('    },')

        return '\n'.join(hooks_lines) + '\n'

    def _get_hook_function(self, doctype_name, trigger):
        """Get the appropriate hook function for a trigger"""
        # Map triggers to audit trail functions
        trigger_mapping = {
            'after_insert': 'mkaguzi.integration.sync.create_audit_trail_entry',
            'on_update': 'mkaguzi.integration.sync.update_audit_trail_entry',
            'on_trash': 'mkaguzi.integration.sync.delete_audit_trail_entry',
            'on_submit': 'mkaguzi.integration.sync.submit_audit_trail_entry',
            'on_cancel': 'mkaguzi.integration.sync.cancel_audit_trail_entry',
            'validate': 'mkaguzi.integration.sync.validate_audit_trail_entry',
            'before_save': 'mkaguzi.integration.sync.before_save_audit_trail_entry'
        }

        return trigger_mapping.get(trigger, 'mkaguzi.integration.sync.create_audit_trail_entry')

    def _update_existing_hooks(self, existing_events, doctype_name, new_triggers):
        """Update existing hooks for a doctype"""
        # For simplicity, replace the entire doctype entry
        # In a more sophisticated implementation, this could merge triggers
        lines = existing_events.split('\n')
        new_lines = []
        skip_doctype = False

        for line in lines:
            if f'    "{doctype_name}": {{' in line:
                skip_doctype = True
                # Add new hooks
                new_lines.extend(self._generate_hooks_entry(doctype_name, new_triggers).split('\n')[:-1])  # Remove extra newline
                continue
            elif skip_doctype and line.strip().startswith('    }'):
                skip_doctype = False
                continue
            elif skip_doctype and line.strip().startswith('    },'):
                skip_doctype = False
                continue
            elif skip_doctype:
                continue
            else:
                new_lines.append(line)

        return '\n'.join(new_lines)

    def _extract_doctype_hooks(self, content, doctype_name):
        """Extract hooks for a specific doctype"""
        try:
            # Find the doctype entry
            start_pattern = f'    "{doctype_name}": {{'
            start_idx = content.find(start_pattern)

            if start_idx == -1:
                return {}

            # Find the end of this doctype entry
            brace_count = 0
            end_idx = start_idx

            for i, char in enumerate(content[start_idx:], start_idx):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_idx = i + 1
                        break

            doctype_section = content[start_idx:end_idx]

            # Parse the hooks
            hooks = {}
            lines = doctype_section.split('\n')

            for line in lines:
                line = line.strip()
                if ':' in line and not line.startswith('"'):
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        trigger = parts[0].strip().strip('"')
                        function = parts[1].strip().strip(',').strip('"')
                        hooks[trigger] = function

            return hooks

        except Exception as e:
            logger.error(f"Failed to extract doctype hooks: {str(e)}")
            return {}

    def _extract_all_doc_events(self, content):
        """Extract all doc_events from hooks content"""
        try:
            doc_events_start = content.find('doc_events = {')
            if doc_events_start == -1:
                return {}

            # Find the end
            brace_count = 0
            end_idx = doc_events_start

            for i, char in enumerate(content[doc_events_start:], doc_events_start):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_idx = i + 1
                        break

            doc_events_content = content[doc_events_start:end_idx]

            # Simple parsing - in production, use a proper Python parser
            events = {}
            current_doctype = None

            for line in doc_events_content.split('\n'):
                line = line.strip()

                if ':' in line and line.startswith('"') and '{' in line:
                    # Doctype line
                    doctype_part = line.split(':')[0].strip().strip('"')
                    current_doctype = doctype_part
                    events[current_doctype] = {}

                elif current_doctype and ':' in line and not line.startswith('"'):
                    # Hook line
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        trigger = parts[0].strip().strip('"')
                        function = parts[1].strip().strip(',').strip('"')
                        events[current_doctype][trigger] = function

            return events

        except Exception as e:
            logger.error(f"Failed to extract all doc_events: {str(e)}")
            return {}

    def _clear_hooks_cache(self):
        """Clear Frappe's hooks cache"""
        try:
            # Clear various caches
            frappe.cache().delete_key('app_hooks')
            frappe.cache().delete_key('doc_events')

            # Force reload of hooks
            import importlib
            if 'mkaguzi.hooks' in sys.modules:
                importlib.reload(sys.modules['mkaguzi.hooks'])

        except Exception as e:
            logger.error(f"Failed to clear hooks cache: {str(e)}")

    def restore_backup(self, doctype_name):
        """Restore hooks from backup"""
        try:
            if doctype_name in self.backup_hooks:
                backup_content = self.backup_hooks[doctype_name]['content']
                self._write_hooks_file(backup_content)

                self._clear_hooks_cache()

                return {"success": True, "message": f"Backup restored for {doctype_name}"}
            else:
                return {"success": False, "error": "No backup found"}

        except Exception as e:
            logger.error(f"Failed to restore backup: {str(e)}")
            return {"success": False, "error": str(e)}

# Global hooks manager instance
hooks_manager = HooksManager()

@frappe.whitelist()
def add_doctype_hooks(doctype_name, audit_triggers):
    """API endpoint to add hooks for a doctype"""
    if not frappe.has_permission('Audit Doctype Catalog', 'write'):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    audit_triggers = json.loads(audit_triggers) if isinstance(audit_triggers, str) else audit_triggers
    result = hooks_manager.add_doctype_hooks(doctype_name, audit_triggers)
    return result

@frappe.whitelist()
def remove_doctype_hooks(doctype_name):
    """API endpoint to remove hooks for a doctype"""
    if not frappe.has_permission('Audit Doctype Catalog', 'write'):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    result = hooks_manager.remove_doctype_hooks(doctype_name)
    return result

@frappe.whitelist()
def update_doctype_hooks(doctype_name, new_triggers):
    """API endpoint to update hooks for a doctype"""
    if not frappe.has_permission('Audit Doctype Catalog', 'write'):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    new_triggers = json.loads(new_triggers) if isinstance(new_triggers, str) else new_triggers
    result = hooks_manager.update_doctype_hooks(doctype_name, new_triggers)
    return result

@frappe.whitelist()
def get_doctype_hooks(doctype_name=None):
    """API endpoint to get current hooks"""
    return hooks_manager.get_current_hooks(doctype_name)

@frappe.whitelist()
def validate_hooks():
    """API endpoint to validate hooks syntax"""
    return hooks_manager.validate_hooks_syntax()