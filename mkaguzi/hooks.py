app_name = "mkaguzi"
app_title = "Mkaguzi"
app_publisher = "Coale Tech"
app_description = "Internal Audit Management System"
app_email = "info@coale.tech"
app_license = "mit"

# Fixtures
# --------
fixtures = [
    {"dt": "Role", "filters": [["role_name", "in", [
        "Stock Analyst", "Stock Taker", "Store Manager", "HOD Inventory", "Internal Auditor"
    ]]]},
]

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

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Audit Finding": {
        "after_insert": "mkaguzi.utils.notifications.on_audit_finding_insert",
        "on_update": "mkaguzi.utils.notifications.on_audit_finding_update",
    },
    "Compliance Check": {
        "on_update": "mkaguzi.utils.notifications.on_compliance_check_update",
    },
    "Audit Execution": {
        "on_update": "mkaguzi.utils.notifications.on_audit_execution_update",
    }
}

# Scheduled Tasks
# ---------------

scheduler_events = {
    "daily": [
        "mkaguzi.utils.notifications.schedule_notifications",
        "mkaguzi.inventory_audit.tasks.recalculate_all_scorecards",
        "mkaguzi.inventory_audit.tasks.update_sla_statuses"
    ],
    "weekly": [
        "mkaguzi.utils.notifications.send_weekly_digest"
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