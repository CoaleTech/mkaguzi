# Discovery Agent for Multi-Agent System
# =============================================================================
# Agent for automatic doctype discovery and catalog updates

import frappe
from typing import Any, Dict, List, Optional, Set
from datetime import datetime, timedelta
from collections import defaultdict

from .agent_base import AuditAgent


class DiscoveryAgent(AuditAgent):
    """
    Agent for automatic doctype discovery, field mapping detection,
    and schema change monitoring.
    """

    def __init__(self, agent_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """Initialize the Discovery Agent"""
        super().__init__(agent_id, config)
        self.agent_type = 'DiscoveryAgent'

        # Configuration
        self.scan_interval_hours = config.get('scan_interval_hours', 24) if config else 24
        self.auto_update_catalog = config.get('auto_update_catalog', True) if config else True
        self.detect_schema_changes = config.get('detect_schema_changes', True) if config else True

        # Known doctypes cache
        self.known_doctypes: Set[str] = set()
        self._load_known_doctypes()

        # Subscribe to relevant message types
        self.subscribe(['discovery_request', 'schema_change_notification'])

    def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a discovery task

        Args:
            task_data: Task data dictionary

        Returns:
            Task result dictionary
        """
        task_type = task_data.get('task_type')

        if task_type == 'discover_doctypes':
            return self.discover_doctypes()
        elif task_type == 'detect_schema_changes':
            return self.detect_schema_changes()
        elif task_type == 'update_catalog':
            return self.update_catalog()
        elif task_type == 'scan_module':
            return self.scan_module(task_data.get('module_name'))
        elif task_type == 'map_field_relationships':
            return self.map_field_relationships(task_data.get('doctype'))
        elif task_type == 'validate_catalog':
            return self.validate_catalog()
        else:
            return {
                'status': 'error',
                'error': f'Unknown task type: {task_type}'
            }

    def discover_doctypes(self) -> Dict[str, Any]:
        """
        Automatically discover new doctypes in ERPNext

        Returns:
            Discovery results with new doctypes found
        """
        try:
            # Get all custom doctypes
            all_doctypes = frappe.get_all('DocType',
                filters={
                    'custom': 1,
                    'module': ['not in', ['Core', 'Frappe']]
                },
                fields=['name', 'module', 'creation', 'modified'],
                limit=500
            )

            # Find new doctypes
            new_doctypes = []
            for doctype in all_doctypes:
                if doctype['name'] not in self.known_doctypes:
                    new_doctypes.append(doctype)
                    self.known_doctypes.add(doctype['name'])

            # Analyze each new doctype
            discovery_results = []
            for doctype in new_doctypes:
                analysis = self._analyze_doctype(doctype['name'])
                discovery_results.append(analysis)

                # Auto-add to catalog if enabled
                if self.auto_update_catalog:
                    self._add_to_catalog(doctype, analysis)

            return {
                'status': 'success',
                'total_doctypes': len(all_doctypes),
                'new_doctypes_found': len(new_doctypes),
                'new_doctypes': new_doctypes,
                'analysis': discovery_results
            }

        except Exception as e:
            frappe.log_error(f"Doctype Discovery Error: {str(e)}", "Discovery Agent")
            return {'status': 'error', 'error': str(e)}

    def detect_schema_changes(self) -> Dict[str, Any]:
        """
        Monitor for schema changes affecting audit

        Returns:
            Schema change detection results
        """
        try:
            changes = {
                'new_fields': [],
                'removed_fields': [],
                'modified_fields': [],
                'new_child_tables': [],
                'breaking_changes': []
            }

            # Get doctypes from catalog
            if not frappe.db.table_exists('Audit Doctype Catalog'):
                return {'status': 'error', 'error': 'Audit Doctype Catalog not found'}

            catalog_doctypes = frappe.get_all('Audit Doctype Catalog',
                filters={'is_active': 1},
                fields=['doctype_name', 'field_mapping', 'schema_version']
            )

            for catalog_entry in catalog_doctypes:
                doctype_name = catalog_entry['doctype_name']

                # Get current schema
                current_schema = self._get_current_schema(doctype_name)
                stored_schema = frappe.parse_json(catalog_entry['field_mapping']) if catalog_entry.get('field_mapping') else {}

                # Compare schemas
                field_changes = self._compare_schemas(stored_schema, current_schema)

                if field_changes['new_fields']:
                    changes['new_fields'].extend([
                        {'doctype': doctype_name, 'field': f}
                        for f in field_changes['new_fields']
                    ])

                if field_changes['removed_fields']:
                    changes['removed_fields'].extend([
                        {'doctype': doctype_name, 'field': f}
                        for f in field_changes['removed_fields']
                    ])

                    # Check for breaking changes
                    critical_fields = self._get_critical_fields(doctype_name)
                    breaking = [f for f in field_changes['removed_fields'] if f in critical_fields]

                    if breaking:
                        changes['breaking_changes'].append({
                            'doctype': doctype_name,
                            'fields': breaking
                        })

                # Update catalog if changes detected
                if any(field_changes.values()):
                    self._update_catalog_schema(doctype_name, current_schema)

            # Create alert if breaking changes found
            if changes['breaking_changes']:
                self._create_schema_change_alert(changes['breaking_changes'])

            return {
                'status': 'success',
                'doctypes_checked': len(catalog_doctypes),
                'changes_detected': sum(len(v) if isinstance(v, list) else 0 for v in changes.values()),
                'changes': changes
            }

        except Exception as e:
            frappe.log_error(f"Schema Change Detection Error: {str(e)}", "Discovery Agent")
            return {'status': 'error', 'error': str(e)}

    def update_catalog(self) -> Dict[str, Any]:
        """
        Auto-update audit doctype catalog

        Returns:
            Catalog update results
        """
        try:
            if not frappe.db.table_exists('Audit Doctype Catalog'):
                return {'status': 'error', 'error': 'Audit Doctype Catalog not found'}

            # Get all doctypes to catalog
            doctypes_to_catalog = self._get_doctypes_to_catalog()

            updated_count = 0
            created_count = 0

            for doctype_name in doctypes_to_catalog:
                # Check if exists
                exists = frappe.db.exists('Audit Doctype Catalog', {'doctype_name': doctype_name})

                # Get analysis
                analysis = self._analyze_doctype(doctype_name)

                if exists:
                    # Update existing
                    doc = frappe.get_doc('Audit Doctype Catalog', {'doctype_name': doctype_name})
                    doc.field_mapping = frappe.as_json(analysis.get('fields', {}))
                    doc.relationships = frappe.as_json(analysis.get('relationships', []))
                    doc.schema_version = analysis.get('schema_version', 1)
                    doc.last_synced = datetime.now()
                    doc.save()
                    updated_count += 1
                else:
                    # Create new entry
                    self._add_to_catalog({'name': doctype_name}, analysis)
                    created_count += 1

            frappe.db.commit()

            return {
                'status': 'success',
                'updated': updated_count,
                'created': created_count,
                'total': updated_count + created_count
            }

        except Exception as e:
            frappe.log_error(f"Catalog Update Error: {str(e)}", "Discovery Agent")
            return {'status': 'error', 'error': str(e)}

    def scan_module(self, module_name: str) -> Dict[str, Any]:
        """
        Scan a specific module for doctypes

        Args:
            module_name: Name of module to scan

        Returns:
            Module scan results
        """
        try:
            # Get doctypes in module
            module_doctypes = frappe.get_all('DocType',
                filters={'module': module_name},
                fields=['name', 'custom', 'issingle']
            )

            scan_results = {
                'module': module_name,
                'doctype_count': len(module_doctypes),
                'doctypes': [],
                'recommendations': []
            }

            for doctype in module_doctypes):
                analysis = self._analyze_doctype(doctype['name'])
                scan_results['doctypes'].append(analysis)

                # Generate recommendations
                if analysis.get('field_count', 0) > 50:
                    scan_results['recommendations'].append({
                        'doctype': doctype['name'],
                        'recommendation': 'Complex doctype - consider targeted audit procedures'
                    })

                if analysis.get('has_link_fields'):
                    scan_results['recommendations'].append({
                        'doctype': doctype['name'],
                        'recommendation': 'Contains link fields - audit data relationships'
                    })

            return {
                'status': 'success',
                **scan_results
            }

        except Exception as e:
            frappe.log_error(f"Module Scan Error [{module_name}]: {str(e)}", "Discovery Agent")
            return {'status': 'error', 'error': str(e)}

    def map_field_relationships(self, doctype: str) -> Dict[str, Any]:
        """
        Map field relationships for a doctype

        Args:
            doctype: Doctype to analyze

        Returns:
            Field relationship mapping
        """
        try:
            # Get doctype meta
            meta = frappe.get_meta(doctype)

            if not meta:
                return {'status': 'error', 'error': f'Doctype {doctype} not found'}

            relationships = []

            # Find link fields
            for field in meta.fields:
                if field.fieldtype == 'Link':
                    relationships.append({
                        'field': field.fieldname,
                        'target_doctype': field.options,
                        'relationship_type': 'many_to_one'
                    })
                elif field.fieldtype == 'Table':
                    relationships.append({
                        'field': field.fieldname,
                        'target_doctype': field.options,
                        'relationship_type': 'one_to_many'
                    })

            return {
                'status': 'success',
                'doctype': doctype,
                'relationships': relationships,
                'relationship_count': len(relationships)
            }

        except Exception as e:
            frappe.log_error(f"Field Relationship Mapping Error: {str(e)}", "Discovery Agent")
            return {'status': 'error', 'error': str(e)}

    def validate_catalog(self) -> Dict[str, Any]:
        """
        Validate the audit doctype catalog for accuracy

        Returns:
            Validation results
        """
        try:
            if not frappe.db.table_exists('Audit Doctype Catalog'):
                return {'status': 'error', 'error': 'Audit Doctype Catalog not found'}

            catalog_entries = frappe.get_all('Audit Doctype Catalog',
                filters={'is_active': 1},
                fields=['name', 'doctype_name', 'field_mapping']
            )

            validation_results = {
                'total_entries': len(catalog_entries),
                'valid': 0,
                'invalid': 0,
                'issues': []
            }

            for entry in catalog_entries:
                doctype_name = entry['doctype_name']

                # Check if doctype still exists
                if not frappe.db.exists('DocType', doctype_name):
                    validation_results['invalid'] += 1
                    validation_results['issues'].append({
                        'entry': entry['name'],
                        'issue': 'Doctype no longer exists',
                        'severity': 'high'
                    })
                    continue

                # Validate field mapping
                try:
                    field_mapping = frappe.parse_json(entry['field_mapping']) if entry.get('field_mapping') else {}
                    current_schema = self._get_current_schema(doctype_name)

                    # Check for removed fields
                    removed_fields = set(field_mapping.keys()) - set(current_schema.keys())

                    if removed_fields:
                        validation_results['invalid'] += 1
                        validation_results['issues'].append({
                            'entry': entry['name'],
                            'issue': f'Removed fields: {", ".join(removed_fields)}',
                            'severity': 'medium'
                        })
                    else:
                        validation_results['valid'] += 1

                except Exception:
                    validation_results['invalid'] += 1
                    validation_results['issues'].append({
                        'entry': entry['name'],
                        'issue': 'Invalid field mapping',
                        'severity': 'low'
                    })

            return {
                'status': 'success',
                **validation_results
            }

        except Exception as e:
            frappe.log_error(f"Catalog Validation Error: {str(e)}", "Discovery Agent")
            return {'status': 'error', 'error': str(e)}

    def _load_known_doctypes(self) -> None:
        """Load known doctypes from catalog"""
        try:
            if frappe.db.table_exists('Audit Doctype Catalog'):
                entries = frappe.get_all('Audit Doctype Catalog',
                    fields=['doctype_name']
                )
                self.known_doctypes = set(e['doctype_name'] for e in entries)
        except Exception:
            self.known_doctypes = set()

    def _analyze_doctype(self, doctype_name: str) -> Dict[str, Any]:
        """Analyze a doctype for audit relevance"""
        try:
            meta = frappe.get_meta(doctype_name)

            if not meta:
                return {'error': 'Doctype not found'}

            # Count field types
            field_types = defaultdict(int)
            has_link_fields = False
            fields = {}

            for field in meta.fields:
                field_types[field.fieldtype] += 1
                if field.fieldtype == 'Link':
                    has_link_fields = True

                fields[field.fieldname] = {
                    'fieldtype': field.fieldtype,
                    'label': field.label,
                    'required': field.reqd,
                    'options': field.options
                }

            # Determine module
            module = meta.module

            return {
                'doctype': doctype_name,
                'module': module,
                'field_count': len(fields),
                'field_types': dict(field_types),
                'has_link_fields': has_link_fields,
                'fields': fields,
                'relationships': [],
                'schema_version': 1,
                'audit_relevance': self._assess_audit_relevance(doctype_name, field_types)
            }

        except Exception as e:
            return {'error': str(e)}

    def _assess_audit_relevance(self, doctype: str, field_types: Dict) -> str:
        """Assess how relevant a doctype is for auditing"""
        # Financial doctypes are highly relevant
        if any(keyword in doctype.lower() for keyword in ['gl', 'payment', 'invoice', 'journal', 'account']):
            return 'high'

        # Has monetary fields
        if field_types.get('Currency', 0) > 0 or field_types.get('Float', 0) > 5:
            return 'high'

        # Has user/reference fields
        if field_types.get('Link', 0) > 0:
            return 'medium'

        return 'low'

    def _add_to_catalog(self, doctype: Dict, analysis: Dict) -> None:
        """Add doctype to audit catalog"""
        try:
            if not frappe.db.table_exists('Audit Doctype Catalog'):
                return

            # Determine module from analysis or doctype
            module = analysis.get('module') or 'General'

            catalog_entry = frappe.get_doc({
                'doctype': 'Audit Doctype Catalog',
                'doctype_name': doctype.get('name'),
                'module': module,
                'is_active': 1,
                'field_mapping': frappe.as_json(analysis.get('fields', {})),
                'relationships': frappe.as_json(analysis.get('relationships', [])),
                'schema_version': analysis.get('schema_version', 1),
                'audit_relevance': analysis.get('audit_relevance', 'low'),
                'last_synced': datetime.now()
            })

            catalog_entry.insert()
            frappe.db.commit()

        except Exception as e:
            frappe.log_error(f"Failed to add to catalog: {str(e)}", "Discovery Agent")

    def _get_current_schema(self, doctype_name: str) -> Dict[str, Any]:
        """Get current schema for a doctype"""
        analysis = self._analyze_doctype(doctype_name)
        return analysis.get('fields', {})

    def _compare_schemas(self, old_schema: Dict, new_schema: Dict) -> Dict[str, List[str]]:
        """Compare two schemas and identify changes"""
        return {
            'new_fields': list(set(new_schema.keys()) - set(old_schema.keys())),
            'removed_fields': list(set(old_schema.keys()) - set(new_schema.keys())),
            'modified_fields': []  # Would need more detailed comparison
        }

    def _get_critical_fields(self, doctype: str) -> List[str]:
        """Get list of critical fields for a doctype"""
        # Common critical fields
        return ['name', 'owner', 'creation', 'modified', 'docstatus']

    def _update_catalog_schema(self, doctype_name: str, new_schema: Dict) -> None:
        """Update catalog with new schema"""
        try:
            catalog_entry = frappe.get_doc('Audit Doctype Catalog', {'doctype_name': doctype_name})
            catalog_entry.field_mapping = frappe.as_json(new_schema)
            catalog_entry.schema_version += 1
            catalog_entry.last_synced = datetime.now()
            catalog_entry.save()
            frappe.db.commit()
        except Exception as e:
            frappe.log_error(f"Failed to update catalog schema: {str(e)}", "Discovery Agent")

    def _create_schema_change_alert(self, breaking_changes: List[Dict]) -> None:
        """Create alert for breaking schema changes"""
        try:
            if frappe.db.table_exists('Compliance Alert'):
                alert = frappe.get_doc({
                    'doctype': 'Compliance Alert',
                    'alert_title': 'Breaking Schema Changes Detected',
                    'alert_message': f'{len(breaking_changes)} doctypes have breaking schema changes',
                    'severity': 'high',
                    'source': 'Discovery Agent',
                    'details': frappe.as_json(breaking_changes)
                })
                alert.insert()
                frappe.db.commit()
        except Exception as e:
            frappe.log_error(f"Failed to create schema change alert: {str(e)}", "Discovery Agent")

    def _get_doctypes_to_catalog(self) -> List[str]:
        """Get list of doctypes that should be in the audit catalog"""
        # Get custom doctypes and standard audit-relevant doctypes
        custom_doctypes = frappe.get_all('DocType',
            filters={'custom': 1},
            pluck='name'
        )

        # Standard audit-relevant doctypes
        standard_doctypes = [
            'GL Entry', 'Payment Entry', 'Journal Entry',
            'Purchase Invoice', 'Sales Invoice', 'Expense Claim',
            'User', 'Role', 'Item', 'Stock Entry'
        ]

        return list(set(custom_doctypes + standard_doctypes))
