import frappe
from frappe import _
import json


@frappe.whitelist()
def export_board_report(report_id):
    """Export board report as PDF/Word"""
    try:
        report = frappe.get_doc("Board Report", report_id)

        # Generate PDF content (placeholder - implement actual PDF generation)
        pdf_content = generate_board_report_pdf(report)

        return {
            "success": True,
            "file_url": pdf_content,
            "filename": f"board_report_{report.report_id}.pdf"
        }
    except Exception as e:
        frappe.log_error(f"Error exporting board report: {str(e)}")
        return {"success": False, "error": str(e)}


def generate_board_report_pdf(report):
    """Generate PDF content for board report"""
    # Placeholder implementation - replace with actual PDF generation
    return f"/files/board_reports/board_report_{report.report_id}.pdf"


@frappe.whitelist()
def schedule_board_report(report_id, schedule_data):
    """Schedule a board report for generation"""
    try:
        report = frappe.get_doc("Board Report", report_id)

        # Parse schedule data
        schedule_data = json.loads(schedule_data) if isinstance(schedule_data, str) else schedule_data

        scheduled_task = frappe.get_doc({
            "doctype": "Scheduled Task",
            "task_name": f"Generate Board Report: {report.report_title}",
            "scheduled_date": schedule_data.get("date"),
            "assigned_to": schedule_data.get("assigned_to"),
            "reference_type": "Board Report",
            "reference_name": report_id,
            "status": "Pending",
            "task_description": f"Auto-generate board report: {report.report_title}"
        })
        scheduled_task.insert()

        # Update report status
        report.status = "Scheduled"
        report.scheduled_date = schedule_data.get("date")
        report.save()

        return {"success": True, "scheduled_task": scheduled_task.name}
    except Exception as e:
        frappe.log_error(f"Error scheduling board report: {str(e)}")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def schedule_board_meeting(report_id, meeting_data):
    """Schedule a board meeting to present report"""
    try:
        # Parse meeting data
        meeting_data = json.loads(meeting_data) if isinstance(meeting_data, str) else meeting_data

        meeting = frappe.get_doc({
            "doctype": "Event",
            "subject": f"Board Meeting: {meeting_data.get('title', 'Board Report Presentation')}",
            "starts_on": meeting_data.get("date_time"),
            "ends_on": meeting_data.get("end_date_time"),
            "event_type": "Public",
            "description": meeting_data.get("description", ""),
            "event_category": "Meeting"
        })
        meeting.insert()

        # Link meeting to board report
        frappe.db.set_value("Board Report", report_id, "board_meeting", meeting.name)

        return {"success": True, "meeting_id": meeting.name}
    except Exception as e:
        frappe.log_error(f"Error scheduling board meeting: {str(e)}")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def prepare_board_materials(report_id):
    """Prepare meeting materials (agendas, presentations, minutes)"""
    try:
        report = frappe.get_doc("Board Report", report_id)

        # Get related findings
        findings = frappe.get_all("Audit Finding",
            filters={"report_reference": report_id, "include_in_board": 1},
            fields=["finding_title", "finding_category", "risk_rating", "recommendation"]
        )

        materials = {
            "executive_summary": generate_executive_summary(report, findings),
            "findings_summary": findings,
            "presentation_data": generate_presentation_slides(report, findings),
            "material_urls": get_material_urls(report_id)
        }

        return {
            "success": True,
            **materials
        }
    except Exception as e:
        frappe.log_error(f"Error preparing board materials: {str(e)}")
        return {"success": False, "error": str(e)}


def generate_executive_summary(report, findings):
    """Generate executive summary for board materials"""
    try:
        summary = {
            "report_title": report.report_title,
            "period_covered": f"{report.start_date} to {report.end_date}",
            "total_findings": len(findings),
            "high_risk_findings": len([f for f in findings if f.get("risk_rating") == "High"]),
            "key_recommendations": [f.get("recommendation") for f in findings[:3] if f.get("recommendation")],
            "overall_status": report.overall_status or "Under Review"
        }
        return summary
    except Exception:
        return {}


def generate_presentation_slides(report, findings):
    """Generate presentation slide data"""
    try:
        slides = [
            {
                "title": "Executive Summary",
                "content": f"Board Report: {report.report_title}",
                "type": "title"
            },
            {
                "title": "Key Findings",
                "content": findings,
                "type": "findings"
            },
            {
                "title": "Recommendations",
                "content": [f.get("recommendation") for f in findings if f.get("recommendation")],
                "type": "recommendations"
            }
        ]
        return slides
    except Exception:
        return []


def get_material_urls(report_id):
    """Get URLs for prepared materials"""
    try:
        # Generate material file URLs
        base_url = "/files/board_materials"
        return {
            "agenda": f"{base_url}/agenda_{report_id}.pdf",
            "presentation": f"{base_url}/presentation_{report_id}.pdf",
            "minutes_template": f"{base_url}/minutes_template_{report_id}.docx",
            "supporting_docs": f"{base_url}/supporting_{report_id}.zip"
        }
    except Exception:
        return {}