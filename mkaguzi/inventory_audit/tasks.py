# Copyright (c) 2025, CoaleTech and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import today


def recalculate_all_scorecards():
    """
    Daily scheduled task to recalculate all active audit compliance scorecards.
    This task runs at midnight and:
    1. Fetches all active Inventory Audit Plans
    2. Recalculates or creates scorecard for each plan
    3. Creates historical snapshot for trend tracking
    """
    frappe.log_error(
        f"Starting daily scorecard recalculation - {today()}",
        "Scorecard Recalculation"
    )
    
    try:
        # Get all active and in-progress audit plans
        plans = frappe.get_all(
            "Inventory Audit Plan",
            filters={"status": ["in", ["Planned", "In Progress"]]},
            fields=["name", "plan_title"]
        )
        
        success_count = 0
        error_count = 0
        errors = []
        
        for plan in plans:
            try:
                # Check if scorecard exists
                scorecard_name = frappe.db.get_value(
                    "Audit Compliance Scorecard",
                    {"audit_plan": plan.name}
                )
                
                if scorecard_name:
                    scorecard = frappe.get_doc("Audit Compliance Scorecard", scorecard_name)
                else:
                    # Create new scorecard
                    scorecard = frappe.get_doc({
                        "doctype": "Audit Compliance Scorecard",
                        "audit_plan": plan.name,
                        "audit_plan_title": plan.plan_title,
                        "status": "Active"
                    })
                    scorecard.insert(ignore_permissions=True)
                
                # Recalculate metrics
                scorecard.recalculate_metrics()
                scorecard.save(ignore_permissions=True)
                
                # Create history snapshot
                scorecard.create_history_snapshot()
                
                success_count += 1
                
            except Exception as plan_error:
                error_count += 1
                errors.append(f"{plan.name}: {str(plan_error)}")
                frappe.log_error(
                    f"Error recalculating scorecard for {plan.name}: {plan_error}",
                    "Scorecard Recalculation Error"
                )
        
        frappe.db.commit()
        
        # Log summary
        frappe.log_error(
            f"Scorecard recalculation complete - "
            f"Success: {success_count}, Errors: {error_count}",
            "Scorecard Recalculation Complete"
        )
        
        if errors:
            frappe.log_error(
                f"Errors during recalculation:\n" + "\n".join(errors),
                "Scorecard Recalculation Errors"
            )
        
        return {
            "success": True,
            "plans_processed": len(plans),
            "success_count": success_count,
            "error_count": error_count,
            "errors": errors
        }
        
    except Exception as e:
        frappe.log_error(
            f"Fatal error in scorecard recalculation: {e}",
            "Scorecard Recalculation Fatal Error"
        )
        raise


def update_sla_statuses():
    """
    Daily scheduled task to update SLA breach status for:
    1. Variance Reconciliation Cases
    2. Stock Take Issue Logs
    """
    from frappe.utils import getdate
    
    today_date = getdate(today())
    
    # Update Variance Reconciliation Cases
    variance_cases = frappe.get_all(
        "Variance Reconciliation Case",
        filters={
            "status": ["not in", ["Resolved", "Closed", "No Variance"]],
            "is_sla_breached": 0,
            "sla_due_date": ["<", today_date]
        },
        fields=["name"]
    )
    
    for case in variance_cases:
        frappe.db.set_value(
            "Variance Reconciliation Case",
            case.name,
            "is_sla_breached",
            1,
            update_modified=False
        )
    
    # Update Stock Take Issue Logs
    issues = frappe.get_all(
        "Stock Take Issue Log",
        filters={
            "status": ["not in", ["Resolved", "Closed"]],
            "is_sla_breached": 0,
            "sla_due_date": ["<", today_date]
        },
        fields=["name"]
    )
    
    for issue in issues:
        frappe.db.set_value(
            "Stock Take Issue Log",
            issue.name,
            "is_sla_breached",
            1,
            update_modified=False
        )
    
    frappe.db.commit()
    
    frappe.log_error(
        f"SLA status updated - Cases: {len(variance_cases)}, Issues: {len(issues)}",
        "SLA Status Update"
    )
    
    return {
        "cases_updated": len(variance_cases),
        "issues_updated": len(issues)
    }
