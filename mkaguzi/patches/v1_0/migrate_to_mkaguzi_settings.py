# License: MIT
# Copyright (c) 2025, Coale Tech and contributors
"""
Migrate data from OpenRouter Settings into Mkaguzi Settings,
then delete the OpenRouter Settings DocType entirely.

This is a post-model-sync patch — the Mkaguzi Settings DocType
must already exist before this runs.
"""

import frappe
from frappe import _


def execute():
    """Main patch entry-point."""
    _migrate_openrouter_data()
    _delete_openrouter_settings()


def _migrate_openrouter_data():
    """Copy field values from OpenRouter Settings → Mkaguzi Settings."""
    if not frappe.db.exists("DocType", "OpenRouter Settings"):
        frappe.log("OpenRouter Settings not found — skipping migration", "Mkaguzi Patch")
        return

    try:
        old = frappe.get_single("OpenRouter Settings")
        new = frappe.get_single("Mkaguzi Settings")

        # Field mapping: OpenRouter → Mkaguzi Settings
        field_map = {
            "enabled": "ai_enabled",
            "api_key": "api_key",
            "use_paid_model": "use_paid_model",
            "free_model": "free_model",
            "paid_model": "paid_model",
            "max_tokens": "max_tokens",
            "temperature": "temperature",
            "max_findings_per_run": "max_findings_per_run",
            "min_severity_for_review": "min_severity_for_review",
            "review_prompt_template": "review_prompt_template",
            "severity_mismatch_notify": "severity_mismatch_notify",
            "mismatch_notification_roles": "mismatch_notification_roles",
            "available_free_models": "available_free_models",
            "available_paid_models": "available_paid_models",
            "models_last_fetched": "models_last_fetched",
        }

        migrated_count = 0
        for old_field, new_field in field_map.items():
            old_val = getattr(old, old_field, None)
            if old_val is not None and old_val != "" and old_val != 0:
                setattr(new, new_field, old_val)
                migrated_count += 1

        new.flags.ignore_validate = True
        new.flags.ignore_permissions = True
        new.save()
        frappe.db.commit()

        frappe.log(f"Migrated {migrated_count} fields from OpenRouter Settings → Mkaguzi Settings", "Mkaguzi Patch")

    except Exception as e:
        frappe.log_error(f"OpenRouter → Mkaguzi migration error: {e}", "Mkaguzi Patch")


def _delete_openrouter_settings():
    """Remove the OpenRouter Settings DocType and all associated artefacts."""
    if not frappe.db.exists("DocType", "OpenRouter Settings"):
        return

    try:
        # Drop the singles table rows
        frappe.db.delete("Singles", {"doctype": "OpenRouter Settings"})

        # Remove DocType record (cascade deletes DocField, DocPerm, etc.)
        frappe.delete_doc("DocType", "OpenRouter Settings", force=True, ignore_permissions=True)
        frappe.db.commit()

        frappe.log("Deleted OpenRouter Settings DocType", "Mkaguzi Patch")

    except Exception as e:
        frappe.log_error(f"Failed to delete OpenRouter Settings: {e}", "Mkaguzi Patch")
