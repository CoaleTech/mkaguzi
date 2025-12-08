import frappe
import json
from frappe import _
from frappe.utils import now, cstr


@frappe.whitelist()
def get_templates(filters=None):
    """Get all templates with optional filters"""
    try:
        filters = filters or {}

        # Build query conditions
        conditions = []
        values = {}

        if filters.get('template_type'):
            conditions.append("template_type = %(template_type)s")
            values['template_type'] = filters['template_type']

        if filters.get('category'):
            conditions.append("category = %(category)s")
            values['category'] = filters['category']

        if filters.get('is_active') is not None:
            conditions.append("is_active = %(is_active)s")
            values['is_active'] = filters['is_active']

        if filters.get('search'):
            conditions.append("(template_name LIKE %(search)s OR description LIKE %(search)s)")
            values['search'] = f"%{filters['search']}%"

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        templates = frappe.db.sql("""
            SELECT
                name,
                template_name,
                template_type,
                category,
                description,
                template_engine,
                is_active,
                is_default,
                usage_count,
                last_used,
                creation,
                modified,
                owner
            FROM `tabTemplate Registry`
            WHERE {where_clause}
            ORDER BY is_default DESC, template_name ASC
        """.format(where_clause=where_clause), values, as_dict=True)

        return templates

    except Exception as e:
        frappe.log_error(f"Error getting templates: {str(e)}")
        frappe.throw(_("Error retrieving templates"))


@frappe.whitelist()
def get_template(template_id):
    """Get a specific template by ID"""
    try:
        if not template_id:
            frappe.throw(_("Template ID is required"))

        template = frappe.db.get_value(
            "Template Registry",
            template_id,
            ["name", "template_name", "template_type", "category", "description",
             "template_content", "template_config", "template_engine", "is_active",
             "is_default", "usage_count", "last_used", "creation", "modified", "owner"],
            as_dict=True
        )

        if not template:
            frappe.throw(_("Template not found"))

        # Parse template config if it's JSON
        if template.template_config:
            try:
                template.template_config = json.loads(template.template_config)
            except:
                pass

        return template

    except Exception as e:
        frappe.log_error(f"Error getting template {template_id}: {str(e)}")
        frappe.throw(_("Error retrieving template"))


@frappe.whitelist()
def create_template(data):
    """Create a new template"""
    try:
        # Validate required fields
        required_fields = ['template_name', 'template_type']
        for field in required_fields:
            if not data.get(field):
                frappe.throw(_(f"{field.replace('_', ' ').title()} is required"))

        # Check for duplicate template name
        if frappe.db.exists("Template Registry", {"template_name": data['template_name']}):
            frappe.throw(_("Template with this name already exists"))

        # Create new template document
        template = frappe.get_doc({
            "doctype": "Template Registry",
            "template_name": data['template_name'],
            "template_type": data.get('template_type', 'Report'),
            "category": data.get('category', ''),
            "description": data.get('description', ''),
            "template_content": data.get('template_content', ''),
            "template_config": json.dumps(data.get('template_config', {})),
            "template_engine": data.get('template_engine', 'Jinja2'),
            "is_active": data.get('is_active', True),
            "is_default": data.get('is_default', False),
            "usage_count": 0
        })

        template.insert()

        # Update usage count if this is set as default
        if template.is_default:
            _update_default_template(template.template_type, template.name)

        frappe.db.commit()

        return {
            "success": True,
            "message": _("Template created successfully"),
            "data": {
                "name": template.name,
                "template_name": template.template_name
            }
        }

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(f"Error creating template: {str(e)}")
        frappe.throw(_("Error creating template"))


@frappe.whitelist()
def update_template(data):
    """Update an existing template"""
    try:
        template_id = data.get('template_id') or data.get('name')
        if not template_id:
            frappe.throw(_("Template ID is required"))

        # Check if template exists
        if not frappe.db.exists("Template Registry", template_id):
            frappe.throw(_("Template not found"))

        # Get existing template
        template = frappe.get_doc("Template Registry", template_id)

        # Update fields
        update_fields = [
            'template_name', 'template_type', 'category', 'description',
            'template_content', 'template_config', 'template_engine',
            'is_active', 'is_default'
        ]

        for field in update_fields:
            if field in data:
                if field == 'template_config' and isinstance(data[field], dict):
                    template.set(field, json.dumps(data[field]))
                else:
                    template.set(field, data[field])

        # Check for duplicate name if name changed
        if (data.get('template_name') and
            data['template_name'] != template.template_name and
            frappe.db.exists("Template Registry", {"template_name": data['template_name']})):
            frappe.throw(_("Template with this name already exists"))

        template.save()

        # Update usage count if this is set as default
        if template.is_default:
            _update_default_template(template.template_type, template.name)

        frappe.db.commit()

        return {
            "success": True,
            "message": _("Template updated successfully"),
            "data": {
                "name": template.name,
                "template_name": template.template_name
            }
        }

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(f"Error updating template {data.get('template_id')}: {str(e)}")
        frappe.throw(_("Error updating template"))


@frappe.whitelist()
def delete_template(template_id):
    """Delete a template"""
    try:
        if not template_id:
            frappe.throw(_("Template ID is required"))

        if not frappe.db.exists("Template Registry", template_id):
            frappe.throw(_("Template not found"))

        # Check if template is in use
        usage_count = frappe.db.get_value("Template Registry", template_id, "usage_count")
        if usage_count and usage_count > 0:
            frappe.throw(_("Cannot delete template that is currently in use"))

        # Delete the template
        frappe.delete_doc("Template Registry", template_id)
        frappe.db.commit()

        return {
            "success": True,
            "message": _("Template deleted successfully")
        }

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(f"Error deleting template {template_id}: {str(e)}")
        frappe.throw(_("Error deleting template"))


@frappe.whitelist()
def duplicate_template(template_id, new_name=None):
    """Duplicate an existing template"""
    try:
        if not template_id:
            frappe.throw(_("Template ID is required"))

        # Get original template
        original = frappe.get_doc("Template Registry", template_id)

        # Generate new name if not provided
        if not new_name:
            new_name = f"{original.template_name} (Copy)"

        # Check for duplicate name
        if frappe.db.exists("Template Registry", {"template_name": new_name}):
            counter = 1
            while frappe.db.exists("Template Registry", {"template_name": f"{new_name} {counter}"}):
                counter += 1
            new_name = f"{new_name} {counter}"

        # Create duplicate
        duplicate = frappe.get_doc({
            "doctype": "Template Registry",
            "template_name": new_name,
            "template_type": original.template_type,
            "category": original.category,
            "description": original.description,
            "template_content": original.template_content,
            "template_config": original.template_config,
            "template_engine": original.template_engine,
            "is_active": True,
            "is_default": False,
            "usage_count": 0
        })

        duplicate.insert()
        frappe.db.commit()

        return {
            "success": True,
            "message": _("Template duplicated successfully"),
            "data": {
                "name": duplicate.name,
                "template_name": duplicate.template_name
            }
        }

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(f"Error duplicating template {template_id}: {str(e)}")
        frappe.throw(_("Error duplicating template"))


@frappe.whitelist()
def render_template(template_id, context=None):
    """Render a template with given context"""
    try:
        if not template_id:
            frappe.throw(_("Template ID is required"))

        template = frappe.get_doc("Template Registry", template_id)

        if not template.is_active:
            frappe.throw(_("Template is not active"))

        # Update usage statistics
        template.usage_count = (template.usage_count or 0) + 1
        template.last_used = now()
        template.save(ignore_permissions=True)

        # Render template
        context = context or {}

        if template.template_engine == 'Jinja2':
            from jinja2 import Template
            jinja_template = Template(template.template_content)
            rendered_content = jinja_template.render(**context)
        else:
            # Plain text or other engines
            rendered_content = template.template_content

        return {
            "success": True,
            "content": rendered_content,
            "template_name": template.template_name
        }

    except Exception as e:
        frappe.log_error(f"Error rendering template {template_id}: {str(e)}")
        frappe.throw(_("Error rendering template"))


@frappe.whitelist()
def get_template_categories():
    """Get all unique template categories"""
    try:
        categories = frappe.db.sql("""
            SELECT DISTINCT category
            FROM `tabTemplate Registry`
            WHERE category IS NOT NULL AND category != ''
            ORDER BY category
        """, as_dict=False)

        return [cat[0] for cat in categories]

    except Exception as e:
        frappe.log_error(f"Error getting template categories: {str(e)}")
        return []


@frappe.whitelist()
def get_template_stats():
    """Get template usage statistics"""
    try:
        stats = frappe.db.sql("""
            SELECT
                COUNT(*) as total_templates,
                SUM(usage_count) as total_usage,
                COUNT(CASE WHEN is_active = 1 THEN 1 END) as active_templates,
                COUNT(CASE WHEN is_default = 1 THEN 1 END) as default_templates
            FROM `tabTemplate Registry`
        """, as_dict=True)

        return stats[0] if stats else {}

    except Exception as e:
        frappe.log_error(f"Error getting template stats: {str(e)}")
        return {}


def _update_default_template(template_type, template_name):
    """Update default template for a type (only one default per type)"""
    try:
        # Remove default flag from other templates of same type
        frappe.db.sql("""
            UPDATE `tabTemplate Registry`
            SET is_default = 0
            WHERE template_type = %s AND name != %s
        """, (template_type, template_name))

    except Exception as e:
        frappe.log_error(f"Error updating default template: {str(e)}")


@frappe.whitelist()
def validate_template_content(template_content, template_engine='Jinja2'):
    """Validate template content syntax"""
    try:
        if not template_content:
            return {"valid": True, "message": "Empty template"}

        if template_engine == 'Jinja2':
            from jinja2 import Template
            try:
                Template(template_content)
                return {"valid": True, "message": "Template syntax is valid"}
            except Exception as e:
                return {"valid": False, "message": f"Template syntax error: {str(e)}"}
        else:
            return {"valid": True, "message": "Template validation not available for this engine"}

    except Exception as e:
        return {"valid": False, "message": f"Validation error: {str(e)}"}


# Template Variable Management Functions

@frappe.whitelist()
def get_template_variables(template_id=None, category=None, include_global=True):
    """Get variables for a template, category, or globally"""
    try:
        from mkaguzi.mkaguzi.doctype.template_variable.template_variable import get_template_variables

        variables = get_template_variables(template_id, category, include_global)

        return {
            "success": True,
            "variables": variables
        }

    except Exception as e:
        frappe.log_error(f"Error getting template variables: {str(e)}")
        frappe.throw(_("Error retrieving template variables"))


@frappe.whitelist()
def create_template_variable(data):
    """Create a new template variable"""
    try:
        # Validate required fields
        required_fields = ['variable_name', 'variable_type']
        for field in required_fields:
            if not data.get(field):
                frappe.throw(_(f"{field.replace('_', ' ').title()} is required"))

        # Create new variable document
        variable = frappe.get_doc({
            "doctype": "Template Variable",
            "variable_name": data['variable_name'],
            "variable_type": data['variable_type'],
            "default_value": data.get('default_value', ''),
            "description": data.get('description', ''),
            "is_required": data.get('is_required', False),
            "validation_rules": json.dumps(data.get('validation_rules', {})) if data.get('validation_rules') else '',
            "template": data.get('template', ''),
            "category": data.get('category', ''),
            "is_global": data.get('is_global', False)
        })

        variable.insert()
        frappe.db.commit()

        return {
            "success": True,
            "message": _("Variable created successfully"),
            "data": {
                "name": variable.name,
                "variable_name": variable.variable_name
            }
        }

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(f"Error creating template variable: {str(e)}")
        frappe.throw(_("Error creating template variable"))


@frappe.whitelist()
def update_template_variable(data):
    """Update an existing template variable"""
    try:
        variable_id = data.get('variable_id') or data.get('name')
        if not variable_id:
            frappe.throw(_("Variable ID is required"))

        # Check if variable exists
        if not frappe.db.exists("Template Variable", variable_id):
            frappe.throw(_("Variable not found"))

        # Get existing variable
        variable = frappe.get_doc("Template Variable", variable_id)

        # Update fields
        update_fields = [
            'variable_name', 'variable_type', 'default_value', 'description',
            'is_required', 'validation_rules', 'template', 'category', 'is_global'
        ]

        for field in update_fields:
            if field in data:
                if field == 'validation_rules' and isinstance(data[field], dict):
                    variable.set(field, json.dumps(data[field]))
                else:
                    variable.set(field, data[field])

        variable.save()
        frappe.db.commit()

        return {
            "success": True,
            "message": _("Variable updated successfully"),
            "data": {
                "name": variable.name,
                "variable_name": variable.variable_name
            }
        }

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(f"Error updating template variable {data.get('variable_id')}: {str(e)}")
        frappe.throw(_("Error updating template variable"))


@frappe.whitelist()
def delete_template_variable(variable_id):
    """Delete a template variable"""
    try:
        if not variable_id:
            frappe.throw(_("Variable ID is required"))

        if not frappe.db.exists("Template Variable", variable_id):
            frappe.throw(_("Variable not found"))

        # Delete the variable
        frappe.delete_doc("Template Variable", variable_id)
        frappe.db.commit()

        return {
            "success": True,
            "message": _("Variable deleted successfully")
        }

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(f"Error deleting template variable {variable_id}: {str(e)}")
        frappe.throw(_("Error deleting template variable"))


@frappe.whitelist()
def render_template_with_variables(template_id, variable_values=None):
    """Render a template with variable resolution"""
    try:
        if not template_id:
            frappe.throw(_("Template ID is required"))

        template = frappe.get_doc("Template Registry", template_id)

        if not template.is_active:
            frappe.throw(_("Template is not active"))

        # Get template variables
        variables = get_template_variables(template_id, template.category, True)
        variables = variables.get('variables', []) if isinstance(variables, dict) else variables

        # Build context with variable values and defaults
        context = {}

        # Add provided variable values
        if variable_values:
            if isinstance(variable_values, str):
                variable_values = json.loads(variable_values)
            context.update(variable_values)

        # Add default values for missing variables
        for var in variables:
            var_name = var.get('variable_name')
            if var_name and var_name not in context:
                default_value = var.get('default_value', '')
                if default_value:
                    # Try to evaluate default value if it's a template expression
                    try:
                        if default_value.startswith('{{') and default_value.endswith('}}'):
                            # Simple template evaluation for defaults
                            from jinja2 import Template
                            template_expr = Template(default_value)
                            default_value = template_expr.render()
                        context[var_name] = default_value
                    except:
                        context[var_name] = default_value

        # Validate required variables
        for var in variables:
            if var.get('is_required') and var.get('variable_name') not in context:
                frappe.throw(_("Required variable '{0}' is missing").format(var.get('variable_name')))

        # Update usage statistics
        template.usage_count = (template.usage_count or 0) + 1
        template.last_used = now()
        template.save(ignore_permissions=True)

        # Track analytics
        import time
        start_time = time.time()

        try:
            # Render template
            if template.template_engine == 'Jinja2':
                from jinja2 import Template
                jinja_template = Template(template.template_content)
                rendered_content = jinja_template.render(**context)
            else:
                # Plain text or other engines
                rendered_content = template.template_content

            # Calculate render time
            render_time = time.time() - start_time

            # Track successful render
            track_template_render(
                template_id=template_id,
                render_time=render_time,
                success=True,
                variable_count=len(context)
            )

            return {
                "success": True,
                "content": rendered_content,
                "template_name": template.template_name,
                "variables_used": list(context.keys()),
                "render_time": render_time
            }

        except Exception as render_error:
            # Calculate render time for failed render
            render_time = time.time() - start_time

            # Track failed render
            track_template_render(
                template_id=template_id,
                render_time=render_time,
                success=False,
                variable_count=len(context),
                error_details=json.dumps({
                    "error": str(render_error),
                    "template_engine": template.template_engine
                })
            )
            raise  # Re-raise the original error

    except Exception as e:
        frappe.log_error(f"Error rendering template with variables {template_id}: {str(e)}")
        frappe.throw(_("Error rendering template"))


@frappe.whitelist()
def validate_variable_values(template_id, variable_values):
    """Validate variable values for a template"""
    try:
        if not template_id:
            frappe.throw(_("Template ID is required"))

        # Get template variables
        variables = get_template_variables(template_id, None, True)
        variables = variables.get('variables', []) if isinstance(variables, dict) else variables

        validation_results = []

        if isinstance(variable_values, str):
            variable_values = json.loads(variable_values)

        # Validate each variable
        for var in variables:
            var_name = var.get('variable_name')
            var_type = var.get('variable_type')
            is_required = var.get('is_required', False)

            value = variable_values.get(var_name) if variable_values else None

            try:
                # Check required
                if is_required and (value is None or value == ''):
                    raise ValueError(f"Variable '{var_name}' is required")

                if value is not None and value != '':
                    # Type validation
                    if var_type == "Number":
                        float(value)
                    elif var_type == "Boolean":
                        if str(value).lower() not in ["true", "false", "1", "0"]:
                            raise ValueError(f"Variable '{var_name}' must be a boolean value")
                    elif var_type == "Date":
                        import re
                        if not re.match(r'^\d{4}-\d{2}-\d{2}', str(value)):
                            raise ValueError(f"Variable '{var_name}' must be a valid date")
                    elif var_type == "List":
                        parsed = json.loads(value)
                        if not isinstance(parsed, list):
                            raise ValueError(f"Variable '{var_name}' must be a valid JSON array")
                    elif var_type == "Object":
                        parsed = json.loads(value)
                        if not isinstance(parsed, dict):
                            raise ValueError(f"Variable '{var_name}' must be a valid JSON object")

                validation_results.append({
                    "variable_name": var_name,
                    "valid": True,
                    "message": "Valid"
                })

            except Exception as e:
                validation_results.append({
                    "variable_name": var_name,
                    "valid": False,
                    "message": str(e)
                })

        return {
            "success": True,
            "validation_results": validation_results,
            "all_valid": all(result["valid"] for result in validation_results)
        }

    except Exception as e:
        frappe.log_error(f"Error validating variable values for template {template_id}: {str(e)}")
        frappe.throw(_("Error validating variable values"))


@frappe.whitelist()
def track_template_view(template_id):
    """Track when a template is viewed"""
    try:
        from mkaguzi.reporting.doctype.report_template_analytics.report_template_analytics import ReportTemplateAnalytics

        if not frappe.db.exists("Report Template", template_id):
            frappe.throw(_("Template not found"))

        ReportTemplateAnalytics.track_template_view(template_id)

        return {
            "success": True,
            "message": "Template view tracked successfully"
        }

    except Exception as e:
        frappe.log_error(f"Error tracking template view for {template_id}: {str(e)}")
        frappe.throw(_("Error tracking template view"))


@frappe.whitelist()
def track_template_render(template_id, render_time=None, success=True, variable_count=0, error_details=None):
    """Track when a template is rendered"""
    try:
        from mkaguzi.reporting.doctype.report_template_analytics.report_template_analytics import ReportTemplateAnalytics

        if not frappe.db.exists("Report Template", template_id):
            frappe.throw(_("Template not found"))

        # Get variables used in this render (if available)
        variables = {}
        if variable_count > 0:
            # This would be passed from the frontend when variables are used
            # For now, we'll track the count
            pass

        ReportTemplateAnalytics.track_template_usage(
            template_id=template_id,
            render_time=float(render_time) if render_time else None,
            success=success,
            variables=variables,
            error_details=json.loads(error_details) if error_details else None
        )

        return {
            "success": True,
            "message": "Template render tracked successfully"
        }

    except Exception as e:
        frappe.log_error(f"Error tracking template render for {template_id}: {str(e)}")
        frappe.throw(_("Error tracking template render"))


@frappe.whitelist()
def get_template_analytics(template_id=None, date_from=None, date_to=None):
    """Get analytics data for templates"""
    try:
        from mkaguzi.reporting.doctype.report_template_analytics.report_template_analytics import ReportTemplateAnalytics

        analytics_data = ReportTemplateAnalytics.get_analytics_summary(
            template_id=template_id,
            date_from=date_from,
            date_to=date_to
        )

        return {
            "success": True,
            "data": analytics_data
        }

    except Exception as e:
        frappe.log_error(f"Error getting template analytics: {str(e)}")
        frappe.throw(_("Error retrieving template analytics"))


@frappe.whitelist()
def get_analytics_dashboard_data():
    """Get comprehensive analytics dashboard data"""
    try:
        from mkaguzi.reporting.doctype.report_template_analytics.report_template_analytics import ReportTemplateAnalytics

        # Get overall performance metrics
        performance_metrics = ReportTemplateAnalytics.get_performance_metrics()

        # Get top templates by usage
        top_templates = frappe.db.sql("""
            SELECT
                template_name,
                total_views,
                total_uses,
                total_renders,
                average_render_time,
                success_rate,
                last_used_date
            FROM `tabReport Template Analytics`
            ORDER BY total_uses DESC
            LIMIT 10
        """, as_dict=True)

        # Get usage trends (last 30 days)
        thirty_days_ago = frappe.utils.add_days(frappe.utils.now(), -30)
        usage_trends = frappe.db.sql("""
            SELECT
                DATE(last_used_date) as date,
                SUM(total_views) as views,
                SUM(total_uses) as uses,
                SUM(total_renders) as renders
            FROM `tabReport Template Analytics`
            WHERE last_used_date >= %s
            GROUP BY DATE(last_used_date)
            ORDER BY date
        """, (thirty_days_ago,), as_dict=True)

        # Get error summary
        error_summary = frappe.db.sql("""
            SELECT
                COUNT(*) as total_errors,
                AVG(total_render_errors) as avg_errors_per_template
            FROM `tabReport Template Analytics`
            WHERE total_render_errors > 0
        """, as_dict=True)

        return {
            "success": True,
            "data": {
                "performance_metrics": performance_metrics,
                "top_templates": top_templates,
                "usage_trends": usage_trends,
                "error_summary": error_summary[0] if error_summary else {},
                "generated_at": frappe.utils.now()
            }
        }

    except Exception as e:
        frappe.log_error(f"Error getting analytics dashboard data: {str(e)}")
        frappe.throw(_("Error retrieving analytics dashboard data"))


@frappe.whitelist()
def cleanup_analytics_logs(days_to_keep=90):
    """Clean up old analytics logs"""
    try:
        from mkaguzi.reporting.doctype.report_template_analytics.report_template_analytics import ReportTemplateAnalytics

        if not frappe.session.user_has_role("System Manager"):
            frappe.throw(_("Only System Managers can perform this action"))

        ReportTemplateAnalytics.cleanup_old_logs(int(days_to_keep))

        return {
            "success": True,
            "message": f"Analytics logs older than {days_to_keep} days have been cleaned up"
        }

    except Exception as e:
        frappe.log_error(f"Error cleaning up analytics logs: {str(e)}")
        frappe.throw(_("Error cleaning up analytics logs"))