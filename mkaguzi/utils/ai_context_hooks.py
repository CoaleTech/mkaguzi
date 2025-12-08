# Copyright (c) 2025, Coale Tech and contributors
# For license information, please see license.txt

"""
AI Context Hook Functions for cache invalidation and scheduled tasks.
"""

import frappe
from frappe.utils import now_datetime


# DocType to page_type mapping
DOCTYPE_PAGE_TYPE_MAP = {
    "VAT Reconciliation": "vat_reconciliation",
    "Risk Assessment": "risk_assessment",
    "Audit Finding": "audit_finding",
    "Audit Universe Item": "audit_universe",
    "Annual Audit Plan": "annual_plan",
    "Engagement": "engagement",
    "Stock Take Session": "stock_take",
    "Variance Case": "variance_case",
    "Corrective Action Plan": "corrective_action",
    "Follow Up": "follow_up"
}


def invalidate_context_on_update(doc, method):
    """Invalidate context cache when a document is updated."""
    try:
        page_type = DOCTYPE_PAGE_TYPE_MAP.get(doc.doctype)
        if not page_type:
            return
        
        from mkaguzi.api.ai_specialist import _invalidate_context_cache
        _invalidate_context_cache(page_type, doc.name)
        
        # Also invalidate the list context
        _invalidate_context_cache(f"{page_type}_list")
        
    except Exception as e:
        # Cache invalidation should never break the main operation
        frappe.log_error(f"Context cache invalidation error: {e}", "AI Context Hooks")


def invalidate_context_on_delete(doc, method):
    """Invalidate context cache when a document is deleted."""
    try:
        page_type = DOCTYPE_PAGE_TYPE_MAP.get(doc.doctype)
        if not page_type:
            return
        
        from mkaguzi.api.ai_specialist import _invalidate_context_cache
        _invalidate_context_cache(page_type, doc.name)
        
        # Also invalidate the list context
        _invalidate_context_cache(f"{page_type}_list")
        
    except Exception as e:
        frappe.log_error(f"Context cache invalidation error: {e}", "AI Context Hooks")


def cleanup_expired_shares():
    """Clean up expired context shares (daily task)."""
    try:
        if not frappe.db.exists("DocType", "AI Context Share"):
            return
        
        # Delete expired shares
        expired = frappe.get_all(
            "AI Context Share",
            filters={"expires_at": ["<", now_datetime()]},
            fields=["name"]
        )
        
        for share in expired:
            frappe.delete_doc("AI Context Share", share["name"], ignore_permissions=True)
        
        if expired:
            frappe.db.commit()
            frappe.log_error(f"Cleaned up {len(expired)} expired context shares", "AI Context Cleanup")
            
    except Exception as e:
        frappe.log_error(f"Context share cleanup error: {e}", "AI Context Hooks")


def analyze_context_patterns():
    """Analyze and update context access patterns (weekly task)."""
    try:
        from mkaguzi.api.ai_specialist import analyze_context_patterns as api_analyze
        result = api_analyze()
        
        if result.get("success"):
            frappe.log_error(
                f"Context pattern analysis completed. Patterns analyzed: {result.get('patterns_analyzed', 0)}",
                "AI Context Learning"
            )
        else:
            frappe.log_error(
                f"Context pattern analysis failed: {result.get('error', 'Unknown error')}",
                "AI Context Learning"
            )
            
    except Exception as e:
        frappe.log_error(f"Context pattern analysis error: {e}", "AI Context Hooks")


def refresh_context_analytics():
    """Refresh context analytics aggregations (hourly task)."""
    try:
        if not frappe.db.exists("DocType", "AI Context Analytics"):
            return
        
        # Clean up old analytics (keep last 30 days)
        from frappe.utils import add_to_date
        cutoff_date = add_to_date(now_datetime(), days=-30)
        
        old_records = frappe.db.sql("""
            DELETE FROM `tabAI Context Analytics`
            WHERE access_timestamp < %s
            LIMIT 1000
        """, (cutoff_date,))
        
        frappe.db.commit()
        
    except Exception as e:
        frappe.log_error(f"Context analytics refresh error: {e}", "AI Context Hooks")


def update_context_affinity_scores():
    """Update context affinity scores based on patterns (weekly task)."""
    try:
        if not frappe.db.exists("DocType", "AI Context Pattern"):
            return
        
        if not frappe.db.exists("DocType", "AI Context Affinity"):
            return
        
        from mkaguzi.api.ai_specialist import AFFINITY_DECAY_FACTOR
        
        # Get all patterns with significant co-access
        patterns = frappe.get_all(
            "AI Context Pattern",
            filters={"co_access_count": [">=", 3]},
            fields=["source_page_type", "target_page_type", "co_access_count", "explanation_type"]
        )
        
        for pattern in patterns:
            # Calculate affinity score (normalized 0-1)
            score = min(1.0, pattern["co_access_count"] / 50)
            
            # Check if affinity exists
            existing = frappe.db.get_value(
                "AI Context Affinity",
                {
                    "source_page_type": pattern["source_page_type"],
                    "target_page_type": pattern["target_page_type"]
                },
                ["name", "affinity_score"]
            )
            
            if existing:
                # Decay old score and blend with new
                old_score = existing[1] or 0
                new_score = (old_score * AFFINITY_DECAY_FACTOR) + (score * (1 - AFFINITY_DECAY_FACTOR))
                
                frappe.db.set_value(
                    "AI Context Affinity",
                    existing[0],
                    {
                        "affinity_score": new_score,
                        "last_updated": now_datetime()
                    }
                )
            else:
                # Create new affinity
                frappe.get_doc({
                    "doctype": "AI Context Affinity",
                    "source_page_type": pattern["source_page_type"],
                    "target_page_type": pattern["target_page_type"],
                    "affinity_score": score,
                    "explanation_template": _get_explanation_template(pattern["explanation_type"]),
                    "last_updated": now_datetime()
                }).insert(ignore_permissions=True)
        
        frappe.db.commit()
        
    except Exception as e:
        frappe.log_error(f"Affinity score update error: {e}", "AI Context Hooks")


def _get_explanation_template(explanation_type):
    """Get explanation template for affinity type."""
    templates = {
        "co_access": "Users frequently review {target} when working with {source}",
        "workflow": "{target} is typically accessed after {source} in the audit workflow",
        "parent_child": "{target} contains details related to this {source}",
        "reference": "This {source} references {target} data",
        "audit_flow": "Audit procedures commonly require reviewing {target} with {source}",
        "compliance": "Compliance requirements link {source} to {target}",
        "risk_related": "Risk analysis connects {source} with {target}"
    }
    return templates.get(explanation_type, templates["co_access"])
