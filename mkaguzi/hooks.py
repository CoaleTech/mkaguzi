# -*- coding: utf-8 -*-
# Copyright (c) 2025, Coale Tech and contributors
# For license information, please see license.txt

app_name = "mkaguzi"
app_title = "Mkaguzi"
app_publisher = "Coale Tech"
app_description = "Internal Audit Management System"
app_email = "info@coale.tech"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "mkaguzi",
# 		"logo": "/assets/mkaguzi/logo.png",
# 		"title": "Mkaguzi",
# 		"route": "/mkaguzi",
# 		"has_permission": "mkaguzi.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/mkaguzi/css/mkaguzi.css"
# app_include_js = "/assets/mkaguzi/js/mkaguzi.js"

# include js, css files in header of web template
# web_include_css = "/assets/mkaguzi/css/mkaguzi.css"
# web_include_js = "/assets/mkaguzi/js/mkaguzi.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "mkaguzi/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "mkaguzi/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "mkaguzi.utils.jinja_methods",
# 	"filters": "mkaguzi.utils.jinja_filters"
# }

# Fixtures
# --------
fixtures = [
    {"dt": "Number Card", "filters": [["module", "=", "Mkaguzi"]]},
    {"dt": "Workspace", "filters": [["module", "=", "Mkaguzi"]]}
]

# Installation
# ------------

# before_install = "mkaguzi.install.before_install"
# after_install = "mkaguzi.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "mkaguzi.uninstall.before_uninstall"
# after_uninstall = "mkaguzi.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "mkaguzi.utils.before_app_install"
# after_app_install = "mkaguzi.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "mkaguzi.utils.before_app_uninstall"
# after_app_uninstall = "mkaguzi.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "mkaguzi.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Audit permissions are now defined in mkaguzi.utils.audit_permissions
# Import them for use in permission hooks if needed:
# from mkaguzi.utils.audit_permissions import (
#     get_audit_permissions,
#     get_full_audit_permissions,
#     get_audit_role_permissions,
#     get_default_permissions,
#     has_audit_permission,
#     AUDIT_DOCTYPES
# )

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    # Core ERPNext Financial Doctypes
    "GL Entry": {
        "after_insert": "mkaguzi.integration.sync.create_audit_trail_entry",
        "on_update": "mkaguzi.integration.sync.update_audit_trail_entry",
        "on_trash": "mkaguzi.integration.sync.delete_audit_trail_entry"
    },
    "Journal Entry": {
        "after_insert": "mkaguzi.integration.sync.create_audit_trail_entry",
        "on_update": "mkaguzi.integration.sync.update_audit_trail_entry",
        "on_trash": "mkaguzi.integration.sync.delete_audit_trail_entry"
    },
    "Payment Entry": {
        "after_insert": "mkaguzi.integration.sync.create_audit_trail_entry",
        "on_update": "mkaguzi.integration.sync.update_audit_trail_entry",
        "on_trash": "mkaguzi.integration.sync.delete_audit_trail_entry"
    },
    "Sales Invoice": {
        "after_insert": "mkaguzi.integration.sync.create_audit_trail_entry",
        "on_update": "mkaguzi.integration.sync.update_audit_trail_entry",
        "on_trash": "mkaguzi.integration.sync.delete_audit_trail_entry"
    },
    "Purchase Invoice": {
        "after_insert": "mkaguzi.integration.sync.create_audit_trail_entry",
        "on_update": "mkaguzi.integration.sync.update_audit_trail_entry",
        "on_trash": "mkaguzi.integration.sync.delete_audit_trail_entry"
    },
    "Sales Order": {
        "after_insert": "mkaguzi.integration.sync.create_audit_trail_entry",
        "on_update": "mkaguzi.integration.sync.update_audit_trail_entry",
        "on_trash": "mkaguzi.integration.sync.delete_audit_trail_entry"
    },
    "Purchase Order": {
        "after_insert": "mkaguzi.integration.sync.create_audit_trail_entry",
        "on_update": "mkaguzi.integration.sync.update_audit_trail_entry",
        "on_trash": "mkaguzi.integration.sync.delete_audit_trail_entry"
    },
    "Delivery Note": {
        "after_insert": "mkaguzi.integration.sync.create_audit_trail_entry",
        "on_update": "mkaguzi.integration.sync.update_audit_trail_entry",
        "on_trash": "mkaguzi.integration.sync.delete_audit_trail_entry"
    },
    "Purchase Receipt": {
        "after_insert": "mkaguzi.integration.sync.create_audit_trail_entry",
        "on_update": "mkaguzi.integration.sync.update_audit_trail_entry",
        "on_trash": "mkaguzi.integration.sync.delete_audit_trail_entry"
    },

    # HRMS Doctypes
    "Employee": {
        "after_insert": "mkaguzi.integration.sync.create_audit_trail_entry",
        "on_update": "mkaguzi.integration.sync.update_audit_trail_entry",
        "on_trash": "mkaguzi.integration.sync.delete_audit_trail_entry"
    },
    "Salary Slip": {
        "after_insert": "mkaguzi.integration.sync.create_audit_trail_entry",
        "on_update": "mkaguzi.integration.sync.update_audit_trail_entry",
        "on_trash": "mkaguzi.integration.sync.delete_audit_trail_entry"
    },
    "Salary Structure": {
        "after_insert": "mkaguzi.integration.sync.create_audit_trail_entry",
        "on_update": "mkaguzi.integration.sync.update_audit_trail_entry",
        "on_trash": "mkaguzi.integration.sync.delete_audit_trail_entry"
    },
    "Leave Application": {
        "after_insert": "mkaguzi.integration.sync.create_audit_trail_entry",
        "on_update": "mkaguzi.integration.sync.update_audit_trail_entry",
        "on_trash": "mkaguzi.integration.sync.delete_audit_trail_entry"
    },
    "Attendance": {
        "after_insert": "mkaguzi.integration.sync.create_audit_trail_entry",
        "on_update": "mkaguzi.integration.sync.update_audit_trail_entry",
        "on_trash": "mkaguzi.integration.sync.delete_audit_trail_entry"
    },
    "Expense Claim": {
        "after_insert": "mkaguzi.integration.sync.create_audit_trail_entry",
        "on_update": "mkaguzi.integration.sync.update_audit_trail_entry",
        "on_trash": "mkaguzi.integration.sync.delete_audit_trail_entry"
    },

    # Stock/Inventory Doctypes
    "Stock Entry": {
        "after_insert": "mkaguzi.integration.sync.create_audit_trail_entry",
        "on_update": "mkaguzi.integration.sync.update_audit_trail_entry",
        "on_trash": "mkaguzi.integration.sync.delete_audit_trail_entry"
    },
    "Stock Reconciliation": {
        "after_insert": "mkaguzi.integration.sync.create_audit_trail_entry",
        "on_update": "mkaguzi.integration.sync.update_audit_trail_entry",
        "on_trash": "mkaguzi.integration.sync.delete_audit_trail_entry"
    },
    "Item": {
        "after_insert": "mkaguzi.integration.sync.create_audit_trail_entry",
        "on_update": "mkaguzi.integration.sync.update_audit_trail_entry",
        "on_trash": "mkaguzi.integration.sync.delete_audit_trail_entry"
    },

    # User Access Control
    "User": {
        "after_insert": "mkaguzi.integration.sync.create_audit_trail_entry",
        "on_update": "mkaguzi.integration.sync.update_audit_trail_entry",
        "on_trash": "mkaguzi.integration.sync.delete_audit_trail_entry"
    },
    "Role": {
        "after_insert": "mkaguzi.integration.sync.create_audit_trail_entry",
        "on_update": "mkaguzi.integration.sync.update_audit_trail_entry",
        "on_trash": "mkaguzi.integration.sync.delete_audit_trail_entry"
    },
    "User Permission": {
        "after_insert": "mkaguzi.integration.sync.create_audit_trail_entry",
        "on_update": "mkaguzi.integration.sync.update_audit_trail_entry",
        "on_trash": "mkaguzi.integration.sync.delete_audit_trail_entry"
    },

    # Mkaguzi Internal Doctypes
    "Audit Finding": {
        "after_insert": "mkaguzi.utils.notifications.on_audit_finding_insert",
        "on_update": "mkaguzi.utils.notifications.on_audit_finding_update",
    },
    "Compliance Check": {
        "on_update": "mkaguzi.utils.notifications.on_compliance_check_update",
    },
    "Audit Execution": {
        "on_update": "mkaguzi.utils.notifications.on_audit_execution_update",
    },
    "Audit Trail Entry": {
        "after_insert": "mkaguzi.integration.sync.on_audit_trail_entry_insert",
        "on_update": "mkaguzi.integration.sync.on_audit_trail_entry_update",
    },

    # NOTE: DocType controller methods (validate, on_submit, on_update, etc.)
    # are called automatically by Frappe framework. No need to define them in hooks.
    # Only use doc_events for cross-app integrations or external method calls.
}

# Scheduled Tasks
# ---------------

# Scheduled Tasks
# ---------------

scheduler_events = {
    "hourly": [
        "mkaguzi.integration.sync.hourly_data_sync",
        "mkaguzi.integration.sync.check_system_health",
        "mkaguzi.agents.agent_manager.hourly_agent_health_check"
    ],
    "daily": [
        "mkaguzi.integration.sync.daily_reconciliation",
        "mkaguzi.integration.sync.daily_compliance_check",
        "mkaguzi.integration.sync.daily_risk_assessment",
        "mkaguzi.utils.notifications.schedule_notifications",
        "mkaguzi.integration.sync.cleanup_old_audit_trails",
        "mkaguzi.agents.agent_manager.daily_agent_cleanup"
    ],
    "weekly": [
        "mkaguzi.integration.sync.weekly_comprehensive_audit",
        "mkaguzi.utils.notifications.send_weekly_digest",
        "mkaguzi.integration.sync.weekly_performance_report"
    ],
    "monthly": [
        "mkaguzi.integration.sync.monthly_executive_summary",
        "mkaguzi.integration.sync.monthly_compliance_report"
    ]
}

# Testing
# -------

# before_tests = "mkaguzi.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "mkaguzi.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "mkaguzi.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["mkaguzi.utils.before_request"]
# after_request = ["mkaguzi.utils.after_request"]

# Job Events
# ----------
# before_job = ["mkaguzi.utils.before_job"]
# after_job = ["mkaguzi.utils.after_job"]

# User Data Protection
# --------------------

user_data_fields = [
    {
        "doctype": "Audit Finding",
        "filter_by": "responsible_party",
        "redact_fields": ["description", "recommendation"],
        "partial": 1,
    },
    {
        "doctype": "Audit Notification",
        "filter_by": "recipients",
        "redact_fields": ["message"],
        "partial": 1,
    },
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"mkaguzi.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }


website_route_rules = [{'from_route': '/frontend/<path:app_path>', 'to_route': 'frontend'},]