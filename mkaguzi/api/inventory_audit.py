# Copyright (c) 2025, CoaleTech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import now_datetime, today, add_days, getdate
import csv
import io


@frappe.whitelist()
def get_inventory_audit_plans(filters=None, page=1, page_size=50):
    """Get inventory audit plans with filtering and pagination"""
    try:
        filter_conditions = {}
        if filters:
            data = frappe.parse_json(filters) if isinstance(filters, str) else filters
            if data.get("status"):
                filter_conditions["status"] = data["status"]
            if data.get("audit_period"):
                filter_conditions["audit_period"] = data["audit_period"]
            if data.get("branch"):
                filter_conditions["branch"] = data["branch"]
            if data.get("warehouse"):
                filter_conditions["warehouse"] = data["warehouse"]
        
        offset = (int(page) - 1) * int(page_size)
        
        plans = frappe.get_all(
            "Inventory Audit Plan",
            filters=filter_conditions,
            fields=[
                "name", "plan_id", "plan_title", "status", "audit_period",
                "branch", "warehouse", "lead_auditor", "audit_scope",
                "planned_start_date", "planned_end_date", "due_date",
                "sessions_count", "completed_sessions_count", "variance_cases_count",
                "compliance_score", "priority", "modified"
            ],
            order_by="modified desc",
            limit_page_length=int(page_size),
            limit_start=offset
        )
        
        total_count = frappe.db.count("Inventory Audit Plan", filters=filter_conditions)
        
        return {
            "plans": plans,
            "total_count": total_count,
            "page": int(page),
            "page_size": int(page_size),
            "total_pages": (total_count + int(page_size) - 1) // int(page_size)
        }
    
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Error fetching inventory audit plans"))
        frappe.throw(str(e))


@frappe.whitelist()
def get_stock_take_sessions(filters=None, page=1, page_size=50):
    """Get stock take sessions with filtering and pagination"""
    try:
        filter_conditions = {}
        if filters:
            data = frappe.parse_json(filters) if isinstance(filters, str) else filters
            if data.get("status"):
                filter_conditions["status"] = data["status"]
            if data.get("audit_plan"):
                filter_conditions["audit_plan"] = data["audit_plan"]
            if data.get("count_type"):
                filter_conditions["count_type"] = data["count_type"]
            if data.get("warehouse"):
                filter_conditions["warehouse"] = data["warehouse"]
        
        offset = (int(page) - 1) * int(page_size)
        
        sessions = frappe.get_all(
            "Stock Take Session",
            filters=filter_conditions,
            fields=[
                "name", "session_id", "session_title", "status", "audit_plan",
                "count_type", "warehouse", "start_datetime", "end_datetime",
                "total_items_counted", "items_with_variance", "total_variance_value",
                "variance_rate", "session_compliance_score", "materiality_breaches",
                "team_signoff", "supervisor_signoff", "auditor_signoff", "modified"
            ],
            order_by="modified desc",
            limit_page_length=int(page_size),
            limit_start=offset
        )
        
        total_count = frappe.db.count("Stock Take Session", filters=filter_conditions)
        
        return {
            "sessions": sessions,
            "total_count": total_count,
            "page": int(page),
            "page_size": int(page_size),
            "total_pages": (total_count + int(page_size) - 1) // int(page_size)
        }
    
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Error fetching stock take sessions"))
        frappe.throw(str(e))


@frappe.whitelist()
def get_variance_cases(filters=None, page=1, page_size=50):
    """Get variance reconciliation cases with filtering and pagination"""
    try:
        filter_conditions = {}
        if filters:
            data = frappe.parse_json(filters) if isinstance(filters, str) else filters
            if data.get("status"):
                filter_conditions["status"] = data["status"]
            if data.get("audit_plan"):
                filter_conditions["audit_plan"] = data["audit_plan"]
            if data.get("root_cause"):
                filter_conditions["root_cause"] = data["root_cause"]
            if data.get("priority"):
                filter_conditions["priority"] = data["priority"]
            if data.get("investigator"):
                filter_conditions["investigator"] = data["investigator"]
        
        offset = (int(page) - 1) * int(page_size)
        
        cases = frappe.get_all(
            "Variance Reconciliation Case",
            filters=filter_conditions,
            fields=[
                "name", "case_id", "case_title", "status", "priority",
                "stock_take_session", "audit_plan", "item_code", "item_description",
                "variance_quantity", "variance_value", "variance_percent",
                "root_cause", "investigator", "sla_due_date", "is_sla_breached",
                "sla_days_remaining", "modified"
            ],
            order_by="modified desc",
            limit_page_length=int(page_size),
            limit_start=offset
        )
        
        total_count = frappe.db.count("Variance Reconciliation Case", filters=filter_conditions)
        
        return {
            "cases": cases,
            "total_count": total_count,
            "page": int(page),
            "page_size": int(page_size),
            "total_pages": (total_count + int(page_size) - 1) // int(page_size)
        }
    
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Error fetching variance cases"))
        frappe.throw(str(e))


@frappe.whitelist()
def get_stock_take_audits(filters=None, page=1, page_size=50):
    """Get stock take audits with filtering and pagination"""
    try:
        filter_conditions = {}
        if filters:
            data = frappe.parse_json(filters) if isinstance(filters, str) else filters
            if data.get("status"):
                filter_conditions["status"] = data["status"]
            if data.get("warehouse"):
                filter_conditions["warehouse"] = data["warehouse"]
            if data.get("stock_take_type"):
                filter_conditions["stock_take_type"] = data["stock_take_type"]
        
        offset = (int(page) - 1) * int(page_size)
        
        audits = frappe.get_all(
            "Stock Take Audit",
            filters=filter_conditions,
            fields=[
                "name", "status", "audit_date", "warehouse", "stock_take_type",
                "import_date", "resolution_deadline", "investigation_deadline",
                "total_items", "total_system_qty", "total_physical_qty",
                "total_variance_value", "items_pending", "items_verified_match",
                "items_verified_discrepancy", "items_resolved",
                "created_by", "physical_count_submitted", "physical_count_submitted_by",
                "analyst_reviewed", "stock_analyst", "hod_approved", "hod_approver",
                "branch", "modified"
            ],
            order_by="modified desc",
            limit_page_length=int(page_size),
            limit_start=offset
        )
        
        total_count = frappe.db.count("Stock Take Audit", filters=filter_conditions)
        
        # Get summary stats
        pending_resolution = frappe.db.count("Stock Take Audit", 
            filters={"status": ["in", ["Draft", "Physical Count Submitted", "Analyst Reviewed"]]})
        under_investigation = frappe.db.count("Stock Take Audit", 
            filters={"status": "Under Investigation"})
        total_variance = frappe.db.sql("""
            SELECT COALESCE(SUM(total_variance_value), 0) as total
            FROM `tabStock Take Audit`
            WHERE status NOT IN ('HOD Approved')
        """, as_dict=True)[0].get('total', 0)
        
        return {
            "audits": audits,
            "total_count": total_count,
            "page": int(page),
            "page_size": int(page_size),
            "total_pages": (total_count + int(page_size) - 1) // int(page_size),
            "stats": {
                "pending_resolution": pending_resolution,
                "under_investigation": under_investigation,
                "total_variance": total_variance
            }
        }
    
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Error fetching stock take audits"))
        frappe.throw(str(e))


@frappe.whitelist()
def get_stock_take_issues(filters=None, page=1, page_size=50):
    """Get stock take issue logs with filtering and pagination"""
    try:
        filter_conditions = {}
        if filters:
            data = frappe.parse_json(filters) if isinstance(filters, str) else filters
            if data.get("status"):
                filter_conditions["status"] = data["status"]
            if data.get("audit_plan"):
                filter_conditions["audit_plan"] = data["audit_plan"]
            if data.get("issue_type"):
                filter_conditions["issue_type"] = data["issue_type"]
            if data.get("priority"):
                filter_conditions["priority"] = data["priority"]
            if data.get("assigned_to"):
                filter_conditions["assigned_to"] = data["assigned_to"]
        
        offset = (int(page) - 1) * int(page_size)
        
        issues = frappe.get_all(
            "Stock Take Issue Log",
            filters=filter_conditions,
            fields=[
                "name", "issue_id", "issue_title", "status", "priority",
                "issue_type", "stock_take_session", "audit_plan",
                "item_code", "warehouse", "assigned_to", "reported_by",
                "reported_date", "sla_due_date", "is_sla_breached", "modified"
            ],
            order_by="modified desc",
            limit_page_length=int(page_size),
            limit_start=offset
        )
        
        total_count = frappe.db.count("Stock Take Issue Log", filters=filter_conditions)
        
        return {
            "issues": issues,
            "total_count": total_count,
            "page": int(page),
            "page_size": int(page_size),
            "total_pages": (total_count + int(page_size) - 1) // int(page_size)
        }
    
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Error fetching stock take issues"))
        frappe.throw(str(e))


@frappe.whitelist()
def get_compliance_scorecards(filters=None):
    """Get compliance scorecards"""
    try:
        filter_conditions = {}
        if filters:
            data = frappe.parse_json(filters) if isinstance(filters, str) else filters
            if data.get("audit_plan"):
                filter_conditions["audit_plan"] = data["audit_plan"]
            if data.get("status"):
                filter_conditions["status"] = data["status"]
        
        scorecards = frappe.get_all(
            "Audit Compliance Scorecard",
            filters=filter_conditions,
            fields=[
                "name", "scorecard_id", "audit_plan", "audit_plan_title",
                "calculation_date", "status", "completion_rate", "variance_rate",
                "accuracy_score", "timeliness_score", "sla_compliance_rate",
                "issue_resolution_rate", "overall_compliance_score", "grade",
                "total_sessions", "completed_sessions", "total_variance_cases",
                "resolved_variance_cases", "total_issues", "resolved_issues"
            ],
            order_by="overall_compliance_score desc"
        )
        
        return scorecards
    
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Error fetching compliance scorecards"))
        frappe.throw(str(e))


@frappe.whitelist()
def get_scorecard_history(scorecard):
    """Get historical snapshots for a scorecard"""
    try:
        history = frappe.get_all(
            "Scorecard History",
            filters={"scorecard": scorecard},
            fields=[
                "name", "snapshot_date", "completion_rate", "variance_rate",
                "accuracy_score", "timeliness_score", "sla_compliance_rate",
                "issue_resolution_rate", "overall_compliance_score", "grade"
            ],
            order_by="snapshot_date desc",
            limit_page_length=100
        )
        
        return history
    
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Error fetching scorecard history"))
        frappe.throw(str(e))


@frappe.whitelist()
def recalculate_scorecard(audit_plan):
    """Recalculate scorecard for an audit plan"""
    try:
        # Check if scorecard exists
        scorecard_name = frappe.db.get_value(
            "Audit Compliance Scorecard",
            {"audit_plan": audit_plan}
        )
        
        if scorecard_name:
            scorecard = frappe.get_doc("Audit Compliance Scorecard", scorecard_name)
        else:
            # Create new scorecard
            plan = frappe.get_doc("Inventory Audit Plan", audit_plan)
            scorecard = frappe.get_doc({
                "doctype": "Audit Compliance Scorecard",
                "audit_plan": audit_plan,
                "audit_plan_title": plan.plan_title,
                "status": "Active"
            })
            scorecard.insert(ignore_permissions=True)
        
        # Recalculate metrics
        scorecard.recalculate_metrics()
        scorecard.save(ignore_permissions=True)
        
        # Create history snapshot
        snapshot_name = scorecard.create_history_snapshot()
        
        frappe.db.commit()
        
        return {
            "success": True,
            "scorecard": scorecard.name,
            "snapshot": snapshot_name,
            "overall_score": scorecard.overall_compliance_score,
            "grade": scorecard.grade
        }
    
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Error recalculating scorecard"))
        frappe.throw(str(e))


@frappe.whitelist()
def calculate_count_variance(session_name):
    """Calculate variances for all items in a stock take session"""
    try:
        session = frappe.get_doc("Stock Take Session", session_name)
        plan = frappe.get_doc("Inventory Audit Plan", session.audit_plan)
        
        materiality_amount = plan.materiality_amount_threshold or 0
        materiality_qty = plan.materiality_qty_threshold or 0
        materiality_percent = plan.materiality_percent_threshold or 0
        
        for item in session.count_items:
            # Calculate variance
            system_qty = item.system_quantity or 0
            counted_qty = item.counted_quantity or 0
            valuation_rate = item.valuation_rate or 0
            
            variance_qty = counted_qty - system_qty
            item.variance_quantity = variance_qty
            
            if system_qty > 0:
                item.variance_percent = (variance_qty / system_qty) * 100
            else:
                item.variance_percent = 100 if variance_qty != 0 else 0
            
            item.variance_value = variance_qty * valuation_rate
            
            # Check materiality
            is_material = False
            if materiality_amount and abs(item.variance_value) >= materiality_amount:
                is_material = True
            if materiality_qty and abs(variance_qty) >= materiality_qty:
                is_material = True
            if materiality_percent and abs(item.variance_percent) >= materiality_percent:
                is_material = True
            
            item.materiality_flag = is_material
            
            # Create variance case if material and not already created
            if is_material and not item.variance_case_created:
                case = create_variance_case(session, item, plan)
                item.variance_case_created = 1
        
        session.save(ignore_permissions=True)
        frappe.db.commit()
        
        return {
            "success": True,
            "items_processed": len(session.count_items),
            "items_with_variance": session.items_with_variance,
            "materiality_breaches": session.materiality_breaches
        }
    
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Error calculating count variance"))
        frappe.throw(str(e))


def create_variance_case(session, item, plan):
    """Create a variance reconciliation case for a material variance"""
    case = frappe.get_doc({
        "doctype": "Variance Reconciliation Case",
        "case_title": f"Variance: {item.item_code} in {session.session_title}",
        "stock_take_session": session.name,
        "audit_plan": plan.name,
        "item_code": item.item_code,
        "item_description": item.item_description,
        "warehouse": session.warehouse,
        "bin_location": item.bin_location,
        "system_quantity": item.system_quantity,
        "counted_quantity": item.counted_quantity,
        "variance_quantity": item.variance_quantity,
        "variance_value": item.variance_value,
        "variance_percent": item.variance_percent,
        "sla_start_date": today(),
        "sla_due_date": add_days(today(), 7),
        "status": "New",
        "priority": "High" if abs(item.variance_value or 0) > 10000 else "Medium"
    })
    case.insert(ignore_permissions=True)
    return case


@frappe.whitelist()
def get_item_import_template():
    """Generate and return CSV template for item import"""
    try:
        # Create CSV content
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header row
        headers = [
            "item_code", "item_description", "category", "sub_category",
            "unit_of_measure", "valuation_rate", "warehouse", "bin_location",
            "minimum_stock_level", "maximum_stock_level", "reorder_level",
            "abc_classification", "velocity_classification", "risk_classification",
            "is_active", "is_serialized", "is_batch_tracked", "notes"
        ]
        writer.writerow(headers)
        
        # Sample data rows
        sample_data = [
            ["SKU001", "Widget A - Standard", "Electronics", "Components",
             "Each", "150.00", "Main Warehouse", "A-01-01",
             "10", "100", "20", "A - High Value", "Fast Moving", "Medium Risk",
             "1", "0", "0", "Sample item 1"],
            ["SKU002", "Gadget B - Premium", "Electronics", "Accessories",
             "Each", "350.00", "Main Warehouse", "A-02-03",
             "5", "50", "10", "A - High Value", "Medium Moving", "High Risk",
             "1", "1", "0", "Serial tracked item"],
            ["SKU003", "Raw Material C", "Raw Materials", "Chemicals",
             "Kg", "25.50", "Storage Area B", "B-05-02",
             "100", "1000", "200", "B - Medium Value", "Fast Moving", "Low Risk",
             "1", "0", "1", "Batch tracked material"]
        ]
        
        for row in sample_data:
            writer.writerow(row)
        
        csv_content = output.getvalue()
        output.close()
        
        return {
            "success": True,
            "filename": "inventory_item_import_template.csv",
            "content": csv_content,
            "headers": headers
        }
    
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Error generating import template"))
        frappe.throw(str(e))


@frappe.whitelist()
def import_items_from_csv(file_content):
    """Import items from CSV content"""
    try:
        data = frappe.parse_json(file_content) if isinstance(file_content, str) else file_content
        csv_content = data.get("content", "")
        
        # Parse CSV
        reader = csv.DictReader(io.StringIO(csv_content))
        
        imported = 0
        errors = []
        
        for row_num, row in enumerate(reader, start=2):
            try:
                item_code = row.get("item_code", "").strip()
                if not item_code:
                    errors.append(f"Row {row_num}: Missing item_code")
                    continue
                
                # Check if item exists
                existing = frappe.db.exists("Inventory Item Master", item_code)
                
                item_data = {
                    "doctype": "Inventory Item Master",
                    "item_code": item_code,
                    "item_description": row.get("item_description", "").strip(),
                    "category": row.get("category", "").strip(),
                    "sub_category": row.get("sub_category", "").strip(),
                    "unit_of_measure": row.get("unit_of_measure", "Each").strip(),
                    "valuation_rate": float(row.get("valuation_rate", 0) or 0),
                    "warehouse": row.get("warehouse", "").strip(),
                    "bin_location": row.get("bin_location", "").strip(),
                    "minimum_stock_level": float(row.get("minimum_stock_level", 0) or 0),
                    "maximum_stock_level": float(row.get("maximum_stock_level", 0) or 0),
                    "reorder_level": float(row.get("reorder_level", 0) or 0),
                    "abc_classification": row.get("abc_classification", "").strip(),
                    "velocity_classification": row.get("velocity_classification", "").strip(),
                    "risk_classification": row.get("risk_classification", "").strip(),
                    "is_active": int(row.get("is_active", 1) or 1),
                    "is_serialized": int(row.get("is_serialized", 0) or 0),
                    "is_batch_tracked": int(row.get("is_batch_tracked", 0) or 0),
                    "notes": row.get("notes", "").strip()
                }
                
                if existing:
                    # Update existing item
                    doc = frappe.get_doc("Inventory Item Master", item_code)
                    for key, value in item_data.items():
                        if key != "doctype":
                            setattr(doc, key, value)
                    doc.save(ignore_permissions=True)
                else:
                    # Create new item
                    doc = frappe.get_doc(item_data)
                    doc.insert(ignore_permissions=True)
                
                imported += 1
                
            except Exception as row_error:
                errors.append(f"Row {row_num}: {str(row_error)}")
        
        frappe.db.commit()
        
        return {
            "success": True,
            "imported": imported,
            "errors": errors,
            "total_errors": len(errors)
        }
    
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Error importing items"))
        frappe.throw(str(e))


@frappe.whitelist()
def get_inventory_items(filters=None, page=1, page_size=50):
    """Get inventory items with filtering and pagination"""
    try:
        filter_conditions = {}
        if filters:
            data = frappe.parse_json(filters) if isinstance(filters, str) else filters
            if data.get("category"):
                filter_conditions["category"] = data["category"]
            if data.get("warehouse"):
                filter_conditions["warehouse"] = data["warehouse"]
            if data.get("abc_classification"):
                filter_conditions["abc_classification"] = data["abc_classification"]
            if data.get("is_active") is not None:
                filter_conditions["is_active"] = data["is_active"]
            if data.get("search"):
                filter_conditions["item_code"] = ["like", f"%{data['search']}%"]
        
        offset = (int(page) - 1) * int(page_size)
        
        items = frappe.get_all(
            "Inventory Item Master",
            filters=filter_conditions,
            fields=[
                "name", "item_code", "item_description", "category", "sub_category",
                "unit_of_measure", "valuation_rate", "warehouse", "bin_location",
                "abc_classification", "velocity_classification", "risk_classification",
                "is_active", "last_count_date", "last_count_quantity", "modified"
            ],
            order_by="modified desc",
            limit_page_length=int(page_size),
            limit_start=offset
        )
        
        total_count = frappe.db.count("Inventory Item Master", filters=filter_conditions)
        
        return {
            "items": items,
            "total_count": total_count,
            "page": int(page),
            "page_size": int(page_size),
            "total_pages": (total_count + int(page_size) - 1) // int(page_size)
        }
    
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Error fetching inventory items"))
        frappe.throw(str(e))


@frappe.whitelist()
def get_inventory_dashboard_stats():
    """Get dashboard statistics for inventory audit module"""
    try:
        # Plans stats
        total_plans = frappe.db.count("Inventory Audit Plan")
        active_plans = frappe.db.count("Inventory Audit Plan", {"status": "In Progress"})
        completed_plans = frappe.db.count("Inventory Audit Plan", {"status": "Completed"})
        
        # Sessions stats
        total_sessions = frappe.db.count("Stock Take Session")
        in_progress_sessions = frappe.db.count("Stock Take Session", {"status": "In Progress"})
        
        # Variance cases stats
        total_cases = frappe.db.count("Variance Reconciliation Case")
        open_cases = frappe.db.count("Variance Reconciliation Case", 
                                      {"status": ["in", ["New", "Under Investigation", "Resolution Proposed"]]})
        breached_cases = frappe.db.count("Variance Reconciliation Case", {"is_sla_breached": 1})
        
        # Issues stats
        total_issues = frappe.db.count("Stock Take Issue Log")
        open_issues = frappe.db.count("Stock Take Issue Log", 
                                       {"status": ["in", ["Open", "In Progress"]]})
        
        # Items stats
        total_items = frappe.db.count("Inventory Item Master")
        active_items = frappe.db.count("Inventory Item Master", {"is_active": 1})
        
        # Calculate average compliance score
        avg_score = frappe.db.sql("""
            SELECT AVG(overall_compliance_score) as avg_score
            FROM `tabAudit Compliance Scorecard`
            WHERE status = 'Active'
        """, as_dict=True)
        
        return {
            "plans": {
                "total": total_plans,
                "active": active_plans,
                "completed": completed_plans
            },
            "sessions": {
                "total": total_sessions,
                "in_progress": in_progress_sessions
            },
            "variance_cases": {
                "total": total_cases,
                "open": open_cases,
                "sla_breached": breached_cases
            },
            "issues": {
                "total": total_issues,
                "open": open_issues
            },
            "items": {
                "total": total_items,
                "active": active_items
            },
            "avg_compliance_score": avg_score[0].avg_score if avg_score else 0
        }
    
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Error fetching dashboard stats"))
        frappe.throw(str(e))
