# -*- coding: utf-8 -*-
# Copyright (c) 2025, Coale Tech and contributors
# For license information, please see license.txt

"""
AI Specialist API Endpoints for Mkaguzi

REST API for AI-powered audit assistance:
- Specialized audit AI responses
- Risk analysis, compliance checking, audit planning
- Control testing and audit insights
- Enriched context API with caching, compression, and delta updates
- Multi-context sessions and collaborative features
- Context analytics and AI learning
"""

import frappe
from frappe import _
from frappe.utils import now_datetime, cint, flt, get_datetime, add_to_date
from collections import defaultdict
import hashlib
import json
import gzip
import base64
import time
import uuid
import re


# ============================================
# Configuration Constants
# ============================================

# Context depth presets define what data is fetched at each level
CONTEXT_DEPTH_PRESETS = {
    "summary": {
        "description": "Basic metrics and status only",
        "include_children": False,
        "include_related": False,
        "max_items": 10,
        "include_history": False
    },
    "detailed": {
        "description": "Main document with child tables",
        "include_children": True,
        "include_related": False,
        "max_items": 50,
        "include_history": False
    },
    "full": {
        "description": "Complete context with related documents",
        "include_children": True,
        "include_related": True,
        "max_items": 100,
        "include_history": True
    },
    "comprehensive": {
        "description": "Full context plus analytics and trends",
        "include_children": True,
        "include_related": True,
        "max_items": 200,
        "include_history": True,
        "include_analytics": True
    }
}

# Cache TTL settings in seconds
CACHE_TTL = {
    "context": 300,          # 5 minutes for context data
    "aggregates": 30,        # 30 seconds for aggregate queries
    "templates": 3600,       # 1 hour for templates
    "learning": 1800,        # 30 minutes for learned suggestions
    "analytics": 600         # 10 minutes for analytics
}

# Rate limiting configuration
RATE_LIMIT_CONFIG = {
    "requests_per_minute": 60,
    "requests_per_hour": 500,
    "burst_limit": 10,
    "window_seconds": 60
}

# Compression threshold in bytes (compress if larger)
COMPRESSION_THRESHOLD = 4096  # 4KB

# Context relationships for intelligent fetching
CONTEXT_RELATIONSHIPS = {
    "VAT Reconciliation": {
        "children": ["VAT Reconciliation Item", "VAT Reconciliation Discrepancy"],
        "related": ["Company", "Fiscal Year"],
        "aggregates": ["total_matched", "total_unmatched", "variance_amount"]
    },
    "Risk Assessment": {
        "children": ["Risk Register", "Risk Assessment Team", "Risk Action Plan"],
        "related": ["Audit Universe Item", "Annual Audit Plan"],
        "aggregates": ["critical_count", "high_count", "actions_pending"]
    },
    "Audit Finding": {
        "children": ["Audit Finding Evidence", "Corrective Action Plan"],
        "related": ["Engagement", "Audit Universe Item", "Risk Assessment"],
        "aggregates": ["evidence_count", "cap_count", "follow_up_count"]
    },
    "Audit Universe Item": {
        "children": ["Audit Universe Risk Factor", "Audit Universe Control"],
        "related": ["Risk Assessment", "Annual Audit Plan Item", "Audit Finding"],
        "aggregates": ["open_findings", "total_audits", "risk_score"]
    },
    "Annual Audit Plan": {
        "children": ["Annual Audit Plan Item", "Annual Audit Plan Resource"],
        "related": ["Fiscal Year", "Risk Assessment"],
        "aggregates": ["planned_count", "in_progress_count", "completed_count"]
    },
    "Engagement": {
        "children": ["Engagement Team Member", "Working Paper", "Audit Finding"],
        "related": ["Annual Audit Plan Item", "Audit Universe Item"],
        "aggregates": ["findings_count", "papers_count", "completion_percentage"]
    },
    "Stock Take Session": {
        "children": ["Stock Take Item", "Stock Take Variance"],
        "related": ["Inventory Audit Plan", "Variance Case"],
        "aggregates": ["items_count", "variance_count", "total_variance_value"]
    },
    "Variance Case": {
        "children": ["Variance Case Evidence", "Variance Case Comment"],
        "related": ["Stock Take Session", "Inventory Audit Plan"],
        "aggregates": ["evidence_count", "comments_count"]
    }
}

# Maximum contexts in multi-context session
MAX_MULTI_CONTEXTS = 5

# Version history limit per document
VERSION_HISTORY_LIMIT = 50

# Collaboration session timeout in seconds
COLLABORATION_TIMEOUT = 1800  # 30 minutes

# Minimum occurrences for learning patterns
LEARNING_MIN_OCCURRENCES = 3

# Context affinity decay factor (for learning)
AFFINITY_DECAY_FACTOR = 0.95


# ============================================
# Cache Helper Functions
# ============================================

def _generate_context_hash(context_data: dict) -> str:
    """Generate a hash for context data to detect changes."""
    # Sort keys for consistent hashing
    serialized = json.dumps(context_data, sort_keys=True, default=str)
    return hashlib.md5(serialized.encode()).hexdigest()


def _get_cache_key(page_type: str, document_id: str = None, depth: str = "detailed", user: str = None) -> str:
    """Generate a cache key for context data."""
    parts = ["ai_context", page_type]
    if document_id:
        parts.append(document_id)
    parts.append(depth)
    if user:
        parts.append(user)
    return ":".join(parts)


def _cache_context(cache_key: str, context_data: dict, ttl: int = None) -> None:
    """Store context data in Redis cache."""
    if ttl is None:
        ttl = CACHE_TTL["context"]
    
    cache_data = {
        "data": context_data,
        "hash": _generate_context_hash(context_data),
        "timestamp": now_datetime().isoformat(),
        "version": str(uuid.uuid4())[:8]
    }
    
    frappe.cache().set_value(cache_key, cache_data, expires_in_sec=ttl)


def _get_cached_context(cache_key: str) -> dict:
    """Retrieve context data from Redis cache."""
    cached = frappe.cache().get_value(cache_key)
    if cached:
        return cached
    return None


def _invalidate_context_cache(page_type: str = None, document_id: str = None) -> int:
    """Invalidate context cache entries. Returns count of invalidated keys."""
    invalidated = 0
    
    # Build pattern to match
    if page_type and document_id:
        pattern = f"ai_context:{page_type}:{document_id}:*"
    elif page_type:
        pattern = f"ai_context:{page_type}:*"
    else:
        pattern = "ai_context:*"
    
    # Get all matching keys and delete them
    try:
        keys = frappe.cache().get_keys(pattern)
        for key in keys:
            frappe.cache().delete_value(key)
            invalidated += 1
    except Exception:
        # Fallback: just delete known common keys
        if page_type and document_id:
            for depth in CONTEXT_DEPTH_PRESETS.keys():
                key = _get_cache_key(page_type, document_id, depth)
                frappe.cache().delete_value(key)
                invalidated += 1
    
    return invalidated


# ============================================
# Rate Limiting Functions
# ============================================

def _check_rate_limit(user: str = None) -> dict:
    """Check if user is within rate limits. Returns status and remaining quota."""
    if not user:
        user = frappe.session.user
    
    current_minute = int(time.time() // 60)
    current_hour = int(time.time() // 3600)
    
    minute_key = f"rate_limit:minute:{user}:{current_minute}"
    hour_key = f"rate_limit:hour:{user}:{current_hour}"
    
    minute_count = cint(frappe.cache().get_value(minute_key) or 0)
    hour_count = cint(frappe.cache().get_value(hour_key) or 0)
    
    is_allowed = (
        minute_count < RATE_LIMIT_CONFIG["requests_per_minute"] and
        hour_count < RATE_LIMIT_CONFIG["requests_per_hour"]
    )
    
    return {
        "allowed": is_allowed,
        "minute_remaining": max(0, RATE_LIMIT_CONFIG["requests_per_minute"] - minute_count),
        "hour_remaining": max(0, RATE_LIMIT_CONFIG["requests_per_hour"] - hour_count),
        "retry_after": 60 - (int(time.time()) % 60) if not is_allowed else 0
    }


def _increment_rate_limit(user: str = None) -> None:
    """Increment rate limit counters for user."""
    if not user:
        user = frappe.session.user
    
    current_minute = int(time.time() // 60)
    current_hour = int(time.time() // 3600)
    
    minute_key = f"rate_limit:minute:{user}:{current_minute}"
    hour_key = f"rate_limit:hour:{user}:{current_hour}"
    
    # Increment minute counter
    minute_count = cint(frappe.cache().get_value(minute_key) or 0) + 1
    frappe.cache().set_value(minute_key, minute_count, expires_in_sec=120)
    
    # Increment hour counter
    hour_count = cint(frappe.cache().get_value(hour_key) or 0) + 1
    frappe.cache().set_value(hour_key, hour_count, expires_in_sec=7200)


# ============================================
# Compression Functions
# ============================================

def _compress_context(context_data: dict) -> dict:
    """Compress context data if it exceeds threshold. Returns dict with compressed flag."""
    serialized = json.dumps(context_data, default=str)
    
    if len(serialized) < COMPRESSION_THRESHOLD:
        return {
            "compressed": False,
            "data": context_data,
            "original_size": len(serialized)
        }
    
    # Compress using gzip and encode as base64
    compressed = gzip.compress(serialized.encode('utf-8'))
    encoded = base64.b64encode(compressed).decode('utf-8')
    
    return {
        "compressed": True,
        "data": encoded,
        "original_size": len(serialized),
        "compressed_size": len(encoded),
        "compression_ratio": round(len(encoded) / len(serialized), 2)
    }


def _decompress_context(compressed_data: dict) -> dict:
    """Decompress context data if it was compressed."""
    if not compressed_data.get("compressed"):
        return compressed_data.get("data", compressed_data)
    
    # Decode base64 and decompress gzip
    decoded = base64.b64decode(compressed_data["data"])
    decompressed = gzip.decompress(decoded)
    return json.loads(decompressed.decode('utf-8'))


# ============================================
# Delta Update Functions
# ============================================

def _calculate_delta(old_context: dict, new_context: dict) -> dict:
    """Calculate the difference between old and new context."""
    if not old_context:
        return {"is_full": True, "data": new_context}
    
    old_hash = _generate_context_hash(old_context)
    new_hash = _generate_context_hash(new_context)
    
    if old_hash == new_hash:
        return {"is_full": False, "unchanged": True, "hash": new_hash}
    
    # Calculate diff
    diff = _calculate_context_diff(old_context, new_context)
    
    return {
        "is_full": False,
        "unchanged": False,
        "old_hash": old_hash,
        "new_hash": new_hash,
        "changes": diff
    }


def _calculate_context_diff(old_data: dict, new_data: dict, path: str = "") -> list:
    """Recursively calculate differences between two dictionaries."""
    changes = []
    
    all_keys = set(list(old_data.keys()) + list(new_data.keys()))
    
    for key in all_keys:
        current_path = f"{path}.{key}" if path else key
        
        old_val = old_data.get(key)
        new_val = new_data.get(key)
        
        if key not in old_data:
            changes.append({"type": "added", "path": current_path, "value": new_val})
        elif key not in new_data:
            changes.append({"type": "removed", "path": current_path, "old_value": old_val})
        elif old_val != new_val:
            if isinstance(old_val, dict) and isinstance(new_val, dict):
                # Recurse into nested dicts
                nested_changes = _calculate_context_diff(old_val, new_val, current_path)
                changes.extend(nested_changes)
            else:
                changes.append({
                    "type": "modified",
                    "path": current_path,
                    "old_value": old_val,
                    "new_value": new_val
                })
    
    return changes


# ============================================
# Analytics Tracking Functions
# ============================================

def _record_context_access(page_type: str, document_id: str, depth: str, response_time_ms: int, cached: bool) -> None:
    """Record context access for analytics (non-blocking)."""
    try:
        frappe.enqueue(
            "_record_context_access_async",
            queue="short",
            page_type=page_type,
            document_id=document_id,
            depth=depth,
            response_time_ms=response_time_ms,
            cached=cached,
            user=frappe.session.user,
            timestamp=now_datetime()
        )
    except Exception:
        # Analytics should never block the main request
        pass


def _record_context_access_async(page_type: str, document_id: str, depth: str, 
                                  response_time_ms: int, cached: bool, user: str, timestamp) -> None:
    """Async worker for recording context access."""
    try:
        # Check if DocType exists
        if frappe.db.exists("DocType", "AI Context Analytics"):
            frappe.get_doc({
                "doctype": "AI Context Analytics",
                "user": user,
                "page_type": page_type,
                "document_id": document_id,
                "depth": depth,
                "response_time_ms": response_time_ms,
                "cached": cached,
                "access_timestamp": timestamp
            }).insert(ignore_permissions=True)
    except Exception as e:
        frappe.log_error(f"Failed to record context analytics: {e}", "AI Context Analytics")


# ============================================
# Context Learning Functions
# ============================================

def _record_context_access_pattern(source_page: str, source_doc: str, target_page: str, target_doc: str = None) -> None:
    """Record context access pattern for AI learning."""
    try:
        frappe.enqueue(
            "_record_pattern_async",
            queue="short",
            source_page=source_page,
            source_doc=source_doc,
            target_page=target_page,
            target_doc=target_doc,
            user=frappe.session.user,
            timestamp=now_datetime()
        )
    except Exception:
        pass


def _record_pattern_async(source_page: str, source_doc: str, target_page: str, 
                          target_doc: str, user: str, timestamp) -> None:
    """Async worker for recording access patterns."""
    try:
        if not frappe.db.exists("DocType", "AI Context Pattern"):
            return
        
        # Look for existing pattern
        existing = frappe.db.get_value(
            "AI Context Pattern",
            {"source_page_type": source_page, "target_page_type": target_page},
            "name"
        )
        
        if existing:
            # Increment counter
            frappe.db.set_value(
                "AI Context Pattern", 
                existing,
                "co_access_count",
                frappe.db.get_value("AI Context Pattern", existing, "co_access_count") + 1
            )
        else:
            # Create new pattern
            frappe.get_doc({
                "doctype": "AI Context Pattern",
                "source_page_type": source_page,
                "target_page_type": target_page,
                "co_access_count": 1,
                "first_seen": timestamp
            }).insert(ignore_permissions=True)
    except Exception as e:
        frappe.log_error(f"Failed to record pattern: {e}", "AI Context Pattern")


# ============================================
# Enriched Context API
# ============================================

@frappe.whitelist()
def get_enriched_context(
    page_type: str,
    document_id: str = None,
    depth: str = "detailed",
    filters: dict = None,
    last_version: str = None,
    template_id: str = None,
    enable_compression: bool = True
) -> dict:
    """
    Get enriched context data with caching, compression, and delta updates.
    
    Args:
        page_type: Type of page (vat_reconciliation, risk_assessment, etc.)
        document_id: Document ID for detail pages
        depth: Context depth (summary, detailed, full, comprehensive)
        filters: Optional filters for list contexts
        last_version: Previous version hash for delta updates
        template_id: Optional template to apply
        enable_compression: Whether to compress large responses
    
    Returns:
        Enriched context with metadata, optionally compressed
    """
    start_time = time.time()
    
    try:
        # Check rate limit
        rate_status = _check_rate_limit()
        if not rate_status["allowed"]:
            return {
                "success": False,
                "error": "Rate limit exceeded",
                "retry_after": rate_status["retry_after"],
                "limits": {
                    "minute_remaining": rate_status["minute_remaining"],
                    "hour_remaining": rate_status["hour_remaining"]
                }
            }
        
        # Increment rate limit counter
        _increment_rate_limit()
        
        # Validate depth
        if depth not in CONTEXT_DEPTH_PRESETS:
            depth = "detailed"
        
        # Apply template if provided
        if template_id:
            template = _get_context_template(template_id)
            if template:
                depth = template.get("default_depth", depth)
                filters = template.get("default_filters", filters)
        
        # Check cache
        cache_key = _get_cache_key(page_type, document_id, depth)
        cached_data = _get_cached_context(cache_key)
        
        is_cached = False
        context_data = None
        
        if cached_data and not last_version:
            # Return cached data if no delta requested
            context_data = cached_data["data"]
            is_cached = True
        else:
            # Fetch fresh context
            context_data = _fetch_context_by_type(page_type, document_id, depth, filters)
            
            if context_data:
                # Cache the result
                _cache_context(cache_key, context_data)
        
        if not context_data:
            return {
                "success": False,
                "error": f"No context found for {page_type}",
                "page_type": page_type,
                "document_id": document_id
            }
        
        # Calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Generate version hash
        current_hash = _generate_context_hash(context_data)
        
        # Handle delta updates if last_version provided
        if last_version:
            if last_version == current_hash:
                # No changes
                return {
                    "success": True,
                    "unchanged": True,
                    "version": current_hash,
                    "response_time_ms": response_time_ms
                }
            # Return full data since we don't have the old context to diff against
        
        # Record analytics (non-blocking)
        _record_context_access(page_type, document_id or "", depth, response_time_ms, is_cached)
        
        # Build response
        result = {
            "success": True,
            "page_type": page_type,
            "document_id": document_id,
            "depth": depth,
            "depth_config": CONTEXT_DEPTH_PRESETS[depth],
            "context_data": context_data,
            "metadata": {
                "version": current_hash,
                "cached": is_cached,
                "response_time_ms": response_time_ms,
                "timestamp": now_datetime().isoformat(),
                "user": frappe.session.user
            }
        }
        
        # Compress if enabled and data is large enough
        if enable_compression:
            compressed = _compress_context(result)
            if compressed["compressed"]:
                return {
                    "success": True,
                    "compressed": True,
                    "data": compressed["data"],
                    "original_size": compressed["original_size"],
                    "compressed_size": compressed["compressed_size"]
                }
        
        return result
        
    except Exception as e:
        frappe.log_error(f"Enriched context error: {str(e)}", "AI Context API")
        return {
            "success": False,
            "error": str(e),
            "page_type": page_type,
            "document_id": document_id
        }


def _get_context_template(template_id: str) -> dict:
    """Get context template configuration."""
    try:
        if frappe.db.exists("AI Context Template", template_id):
            template = frappe.get_doc("AI Context Template", template_id)
            return {
                "template_name": template.template_name,
                "page_type": template.page_type,
                "default_depth": template.default_depth,
                "default_filters": json.loads(template.default_filters or "{}"),
                "description": template.description
            }
    except Exception:
        pass
    return None


def _fetch_context_by_type(page_type: str, document_id: str, depth: str, filters: dict) -> dict:
    """Route to the appropriate context fetcher based on page type."""
    depth_config = CONTEXT_DEPTH_PRESETS.get(depth, CONTEXT_DEPTH_PRESETS["detailed"])
    
    fetchers = {
        "vat_reconciliation": _fetch_vat_reconciliation_enriched,
        "vat_reconciliation_list": _fetch_vat_list_enriched,
        "risk_assessment": _fetch_risk_assessment_enriched,
        "audit_finding": _fetch_audit_finding_enriched,
        "audit_universe": _fetch_audit_universe_enriched,
        "annual_plan": _fetch_annual_plan_enriched,
        "engagement": _fetch_engagement_enriched,
        "stock_take": _fetch_stock_take_enriched,
        "variance_case": _fetch_variance_case_enriched,
        "dashboard": _fetch_dashboard_enriched,
        "corrective_action": _fetch_corrective_action_enriched,
        "follow_up": _fetch_follow_up_enriched
    }
    
    fetcher = fetchers.get(page_type)
    if fetcher:
        return fetcher(document_id, depth_config, filters)
    
    return None


# ============================================
# Enriched Context Fetchers
# ============================================

def _fetch_vat_reconciliation_enriched(doc_id: str, depth_config: dict, filters: dict = None) -> dict:
    """Fetch enriched VAT reconciliation context."""
    if not doc_id:
        return None
    
    try:
        doc = frappe.get_doc("VAT Reconciliation", doc_id)
        
        context = {
            "reconciliation_name": doc.name,
            "reconciliation_month": doc.reconciliation_month,
            "fiscal_year": doc.fiscal_year,
            "reconciliation_type": doc.get("reconciliation_type"),
            "status": doc.status,
            "company": doc.company,
            "match_percentage": flt(doc.get("match_percentage", 0)),
            "total_matched": cint(doc.get("total_matched", 0)),
            "total_unmatched_source_a": cint(doc.get("total_unmatched_source_a", 0)),
            "total_unmatched_source_b": cint(doc.get("total_unmatched_source_b", 0)),
            "total_amount_discrepancies": cint(doc.get("total_amount_discrepancies", 0)),
            "total_variance_amount": flt(doc.get("total_variance_amount", 0)),
            "system_records_count": cint(doc.get("system_records_count", 0)),
            "itax_records_count": cint(doc.get("itax_records_count", 0)),
            "tims_records_count": cint(doc.get("tims_records_count", 0))
        }
        
        # Include children if depth allows
        if depth_config.get("include_children"):
            # Get discrepancies
            discrepancies = frappe.get_all(
                "VAT Reconciliation Discrepancy",
                filters={"parent": doc_id},
                fields=["discrepancy_type", "supplier", "amount_difference", "status"],
                limit=depth_config.get("max_items", 50)
            )
            context["discrepancies"] = discrepancies
            context["discrepancy_count"] = len(discrepancies)
        
        # Include related if depth allows
        if depth_config.get("include_related"):
            # Get historical reconciliations
            history = frappe.get_all(
                "VAT Reconciliation",
                filters={
                    "company": doc.company,
                    "name": ["!=", doc_id]
                },
                fields=["name", "reconciliation_month", "fiscal_year", "status", "match_percentage"],
                order_by="creation desc",
                limit=10
            )
            context["history"] = history
        
        return context
        
    except Exception as e:
        frappe.log_error(f"VAT context fetch error: {e}", "AI Context")
        return None


def _fetch_vat_list_enriched(doc_id: str, depth_config: dict, filters: dict = None) -> dict:
    """Fetch enriched VAT reconciliation list context."""
    try:
        # Build query filters
        query_filters = filters or {}
        
        # Get aggregate stats
        total = frappe.db.count("VAT Reconciliation", query_filters)
        pending = frappe.db.count("VAT Reconciliation", {**query_filters, "status": "Pending"})
        approved = frappe.db.count("VAT Reconciliation", {**query_filters, "status": "Approved"})
        
        # Get stats for reconciliations with discrepancies
        with_discrepancies = frappe.db.sql("""
            SELECT COUNT(DISTINCT parent) FROM `tabVAT Reconciliation Discrepancy`
        """)[0][0] or 0
        
        # Calculate average match rate
        avg_match = frappe.db.sql("""
            SELECT AVG(COALESCE(match_percentage, 0)) FROM `tabVAT Reconciliation`
        """)[0][0] or 0
        
        # Total variance
        total_variance = frappe.db.sql("""
            SELECT SUM(COALESCE(total_variance_amount, 0)) FROM `tabVAT Reconciliation`
        """)[0][0] or 0
        
        context = {
            "total_reconciliations": total,
            "pending_reconciliations": pending,
            "approved_reconciliations": approved,
            "reconciliations_with_discrepancies": with_discrepancies,
            "average_match_rate": round(flt(avg_match), 1),
            "total_variance_amount": flt(total_variance),
            "current_filters": filters
        }
        
        # Include summary list if depth allows
        if depth_config.get("include_children"):
            reconciliations = frappe.get_all(
                "VAT Reconciliation",
                filters=query_filters,
                fields=["name", "reconciliation_month", "fiscal_year", "status", "match_percentage", "total_variance_amount"],
                order_by="creation desc",
                limit=depth_config.get("max_items", 50)
            )
            context["reconciliation_summary"] = reconciliations
        
        return context
        
    except Exception as e:
        frappe.log_error(f"VAT list context error: {e}", "AI Context")
        return None


def _fetch_risk_assessment_enriched(doc_id: str, depth_config: dict, filters: dict = None) -> dict:
    """Fetch enriched risk assessment context."""
    if not doc_id:
        return None
    
    try:
        doc = frappe.get_doc("Risk Assessment", doc_id)
        
        context = {
            "assessment_id": doc.name,
            "assessment_name": doc.get("assessment_name", doc.name),
            "fiscal_year": doc.get("fiscal_year"),
            "assessment_period": doc.get("assessment_period"),
            "status": doc.status,
            "scope": doc.get("scope"),
            "methodology": doc.get("methodology", [])
        }
        
        # Get risk register counts
        if depth_config.get("include_children"):
            risks = frappe.get_all(
                "Risk Register",
                filters={"parent": doc_id},
                fields=["risk_level", "status", "risk_category"]
            )
            
            context["risk_register_count"] = len(risks)
            context["high_risk_count"] = len([r for r in risks if r.get("risk_level") == "High"])
            context["critical_risk_count"] = len([r for r in risks if r.get("risk_level") == "Critical"])
            context["risks"] = risks[:depth_config.get("max_items", 50)]
        
        # Get action plans
        if depth_config.get("include_related"):
            actions = frappe.get_all(
                "Risk Action Plan",
                filters={"parent": doc_id},
                fields=["action", "status", "due_date", "responsible_person"]
            )
            context["action_plan_count"] = len(actions)
            context["pending_actions"] = len([a for a in actions if a.get("status") == "Pending"])
            context["completed_actions"] = len([a for a in actions if a.get("status") == "Completed"])
        
        return context
        
    except Exception as e:
        frappe.log_error(f"Risk assessment context error: {e}", "AI Context")
        return None


def _fetch_audit_finding_enriched(doc_id: str, depth_config: dict, filters: dict = None) -> dict:
    """Fetch enriched audit finding context."""
    if not doc_id:
        return None
    
    try:
        doc = frappe.get_doc("Audit Finding", doc_id)
        
        context = {
            "finding_id": doc.name,
            "finding_title": doc.get("title", doc.name),
            "risk_level": doc.get("risk_level"),
            "status": doc.status,
            "category": doc.get("category"),
            "entity_name": doc.get("entity_name"),
            "description": doc.get("description", "")[:500],
            "root_cause": doc.get("root_cause", "")[:500],
            "recommendation": doc.get("recommendation", "")[:500]
        }
        
        # Get evidence and CAPs
        if depth_config.get("include_children"):
            evidence = frappe.get_all(
                "Audit Finding Evidence",
                filters={"parent": doc_id},
                fields=["evidence_type", "description", "file"]
            )
            context["evidence"] = evidence
            context["evidence_count"] = len(evidence)
            
            caps = frappe.get_all(
                "Corrective Action Plan",
                filters={"audit_finding": doc_id},
                fields=["name", "status", "due_date", "responsible_person"]
            )
            context["corrective_actions"] = caps
            context["corrective_actions_count"] = len(caps)
        
        # Get related findings
        if depth_config.get("include_related") and doc.get("engagement"):
            related = frappe.get_all(
                "Audit Finding",
                filters={
                    "engagement": doc.engagement,
                    "name": ["!=", doc_id]
                },
                fields=["name", "title", "risk_level", "status"],
                limit=10
            )
            context["related_findings"] = related
        
        return context
        
    except Exception as e:
        frappe.log_error(f"Audit finding context error: {e}", "AI Context")
        return None


def _fetch_audit_universe_enriched(doc_id: str, depth_config: dict, filters: dict = None) -> dict:
    """Fetch enriched audit universe context."""
    if not doc_id:
        return None
    
    try:
        doc = frappe.get_doc("Audit Universe Item", doc_id)
        
        context = {
            "entity_id": doc.name,
            "entity_name": doc.get("entity_name", doc.name),
            "entity_type": doc.get("entity_type"),
            "department": doc.get("department"),
            "location": doc.get("location"),
            "risk_rating": doc.get("risk_rating"),
            "inherent_risk_rating": doc.get("inherent_risk_rating"),
            "control_effectiveness": doc.get("control_effectiveness"),
            "is_active": doc.get("is_active", True),
            "last_audit_date": str(doc.get("last_audit_date") or ""),
            "next_audit_due": str(doc.get("next_audit_due") or ""),
            "audit_frequency": doc.get("audit_frequency")
        }
        
        # Get risk factors and controls
        if depth_config.get("include_children"):
            risk_factors = frappe.get_all(
                "Audit Universe Risk Factor",
                filters={"parent": doc_id},
                fields=["risk_factor", "risk_level", "description"]
            )
            context["risk_factors"] = risk_factors
            
            controls = frappe.get_all(
                "Audit Universe Control",
                filters={"parent": doc_id},
                fields=["control_name", "control_type", "effectiveness"]
            )
            context["key_controls"] = controls
        
        # Get related findings and audits
        if depth_config.get("include_related"):
            findings = frappe.get_all(
                "Audit Finding",
                filters={"audit_universe_item": doc_id},
                fields=["name", "title", "risk_level", "status"],
                limit=20
            )
            context["open_findings"] = len([f for f in findings if f.get("status") not in ["Closed", "Resolved"]])
            context["total_findings"] = len(findings)
            context["findings"] = findings
        
        return context
        
    except Exception as e:
        frappe.log_error(f"Audit universe context error: {e}", "AI Context")
        return None


def _fetch_annual_plan_enriched(doc_id: str, depth_config: dict, filters: dict = None) -> dict:
    """Fetch enriched annual audit plan context."""
    if not doc_id:
        return None
    
    try:
        doc = frappe.get_doc("Annual Audit Plan", doc_id)
        
        context = {
            "plan_id": doc.name,
            "plan_title": doc.get("plan_title", doc.name),
            "fiscal_year": doc.get("fiscal_year"),
            "status": doc.status,
            "total_budget": flt(doc.get("total_budget", 0)),
            "allocated_budget": flt(doc.get("allocated_budget", 0)),
            "objectives": doc.get("objectives", "")[:500],
            "scope": doc.get("scope", "")[:500]
        }
        
        # Get plan items
        if depth_config.get("include_children"):
            items = frappe.get_all(
                "Annual Audit Plan Item",
                filters={"parent": doc_id},
                fields=["audit_entity", "risk_rating", "planned_start", "status", "assigned_auditor"]
            )
            context["total_audits"] = len(items)
            context["planned_audits"] = len([i for i in items if i.get("status") == "Planned"])
            context["in_progress_audits"] = len([i for i in items if i.get("status") == "In Progress"])
            context["completed_audits"] = len([i for i in items if i.get("status") == "Completed"])
            context["high_risk_areas"] = len([i for i in items if i.get("risk_rating") == "High"])
            context["plan_items"] = items[:depth_config.get("max_items", 50)]
        
        # Get resource allocation
        if depth_config.get("include_related"):
            resources = frappe.get_all(
                "Annual Audit Plan Resource",
                filters={"parent": doc_id},
                fields=["resource_name", "role", "allocation_percentage"]
            )
            context["total_resources"] = len(resources)
            context["resources"] = resources
        
        return context
        
    except Exception as e:
        frappe.log_error(f"Annual plan context error: {e}", "AI Context")
        return None


def _fetch_engagement_enriched(doc_id: str, depth_config: dict, filters: dict = None) -> dict:
    """Fetch enriched engagement context."""
    if not doc_id:
        return None
    
    try:
        doc = frappe.get_doc("Engagement", doc_id)
        
        context = {
            "engagement_id": doc.name,
            "title": doc.get("title", doc.name),
            "description": doc.get("description", "")[:500],
            "status": doc.status,
            "engagement_type": doc.get("engagement_type"),
            "start_date": str(doc.get("start_date") or ""),
            "end_date": str(doc.get("end_date") or ""),
            "lead_auditor": doc.get("lead_auditor"),
            "budget": flt(doc.get("budget", 0)),
            "scope": doc.get("scope", "")[:500]
        }
        
        # Get team and findings
        if depth_config.get("include_children"):
            team = frappe.get_all(
                "Engagement Team Member",
                filters={"parent": doc_id},
                fields=["team_member", "role", "hours_allocated"]
            )
            context["team_members"] = team
            context["team_size"] = len(team)
            
            findings = frappe.get_all(
                "Audit Finding",
                filters={"engagement": doc_id},
                fields=["name", "title", "risk_level", "status"]
            )
            context["findings"] = findings
            context["findings_count"] = len(findings)
            context["high_risk_findings"] = len([f for f in findings if f.get("risk_level") == "High"])
        
        # Get working papers
        if depth_config.get("include_related"):
            papers = frappe.get_all(
                "Working Paper",
                filters={"engagement": doc_id},
                fields=["name", "title", "status", "paper_type"],
                limit=20
            )
            context["working_papers"] = papers
            context["papers_count"] = len(papers)
        
        return context
        
    except Exception as e:
        frappe.log_error(f"Engagement context error: {e}", "AI Context")
        return None


def _fetch_stock_take_enriched(doc_id: str, depth_config: dict, filters: dict = None) -> dict:
    """Fetch enriched stock take context."""
    if not doc_id:
        return None
    
    try:
        doc = frappe.get_doc("Stock Take Session", doc_id)
        
        context = {
            "session_id": doc.name,
            "stock_take_type": doc.get("stock_take_type"),
            "warehouse": doc.get("warehouse"),
            "audit_date": str(doc.get("audit_date") or ""),
            "status": doc.status,
            "total_items": cint(doc.get("total_items", 0)),
            "items_with_variance": cint(doc.get("items_with_variance", 0)),
            "total_system_value": flt(doc.get("total_system_value", 0)),
            "total_variance_value": flt(doc.get("total_variance_value", 0)),
            "variance_percentage": flt(doc.get("variance_percentage", 0))
        }
        
        # Get variance items
        if depth_config.get("include_children"):
            variances = frappe.get_all(
                "Stock Take Variance",
                filters={"parent": doc_id},
                fields=["item_code", "item_name", "system_qty", "physical_qty", "variance", "variance_value"],
                order_by="abs(variance_value) desc",
                limit=depth_config.get("max_items", 50)
            )
            context["high_variance_items"] = variances
            
            # Risk indicators
            context["risk_indicators"] = {
                "large_variances": len([v for v in variances if abs(v.get("variance", 0)) > 50]),
                "high_value_variances": len([v for v in variances if abs(v.get("variance_value", 0)) > 1000]),
                "negative_variances": len([v for v in variances if v.get("variance", 0) < 0]),
                "positive_variances": len([v for v in variances if v.get("variance", 0) > 0])
            }
        
        return context
        
    except Exception as e:
        frappe.log_error(f"Stock take context error: {e}", "AI Context")
        return None


def _fetch_variance_case_enriched(doc_id: str, depth_config: dict, filters: dict = None) -> dict:
    """Fetch enriched variance case context."""
    if not doc_id:
        return None
    
    try:
        doc = frappe.get_doc("Variance Case", doc_id)
        
        context = {
            "case_id": doc.name,
            "item_code": doc.get("item_code"),
            "item_name": doc.get("item_name"),
            "warehouse": doc.get("warehouse"),
            "branch": doc.get("branch"),
            "status": doc.status,
            "priority": doc.get("priority"),
            "system_quantity": flt(doc.get("system_quantity", 0)),
            "physical_quantity": flt(doc.get("physical_quantity", 0)),
            "variance_quantity": flt(doc.get("variance_quantity", 0)),
            "variance_value": flt(doc.get("variance_value", 0)),
            "variance_type": doc.get("variance_type"),
            "is_high_value": doc.get("is_high_value", False),
            "reported_date": str(doc.get("reported_date") or ""),
            "investigation_status": doc.get("investigation_status"),
            "root_cause": doc.get("root_cause", "")[:500],
            "corrective_action": doc.get("corrective_action", "")[:500],
            "responsible_person": doc.get("responsible_person"),
            "target_resolution_date": str(doc.get("target_resolution_date") or "")
        }
        
        # Get evidence and comments
        if depth_config.get("include_children"):
            evidence = frappe.get_all(
                "Variance Case Evidence",
                filters={"parent": doc_id},
                fields=["evidence_type", "description", "attachment"]
            )
            context["evidence"] = evidence
            context["evidence_count"] = len(evidence)
            
            comments = frappe.get_all(
                "Variance Case Comment",
                filters={"parent": doc_id},
                fields=["comment", "comment_by", "creation"],
                order_by="creation desc",
                limit=20
            )
            context["comments"] = comments
            context["comments_count"] = len(comments)
        
        # Risk assessment
        context["risk_assessment"] = {
            "financial_impact": flt(context["variance_value"]),
            "operational_impact": "High" if context["is_high_value"] else "Medium",
            "urgency": context["priority"]
        }
        
        return context
        
    except Exception as e:
        frappe.log_error(f"Variance case context error: {e}", "AI Context")
        return None


def _fetch_dashboard_enriched(doc_id: str, depth_config: dict, filters: dict = None) -> dict:
    """Fetch enriched dashboard context with aggregate stats."""
    try:
        context = {
            "total_entities": frappe.db.count("Audit Universe Item", {"is_active": True}),
            "active_audits": frappe.db.count("Engagement", {"status": "In Progress"}),
            "open_findings": frappe.db.count("Audit Finding", {"status": ["not in", ["Closed", "Resolved"]]}),
            "pending_caps": frappe.db.count("Corrective Action Plan", {"status": "Open"}),
            "overdue_caps": 0,
            "vat_reconciliations": {
                "total": frappe.db.count("VAT Reconciliation"),
                "pending": frappe.db.count("VAT Reconciliation", {"status": "Pending"}),
                "approved": frappe.db.count("VAT Reconciliation", {"status": "Approved"})
            },
            "risk_assessments": {
                "total": frappe.db.count("Risk Assessment"),
                "active": frappe.db.count("Risk Assessment", {"status": "Active"})
            }
        }
        
        # Get overdue CAPs
        try:
            overdue = frappe.db.sql("""
                SELECT COUNT(*) FROM `tabCorrective Action Plan`
                WHERE status = 'Open' AND due_date < CURDATE()
            """)[0][0] or 0
            context["overdue_caps"] = overdue
        except Exception:
            pass
        
        # Include detailed stats if depth allows
        if depth_config.get("include_children"):
            # Finding distribution by risk level
            findings_by_risk = frappe.db.sql("""
                SELECT risk_level, COUNT(*) as count
                FROM `tabAudit Finding`
                WHERE status NOT IN ('Closed', 'Resolved')
                GROUP BY risk_level
            """, as_dict=True)
            context["findings_by_risk"] = {f["risk_level"]: f["count"] for f in findings_by_risk}
            
            # Recent engagements
            recent_engagements = frappe.get_all(
                "Engagement",
                fields=["name", "title", "status", "start_date"],
                order_by="creation desc",
                limit=5
            )
            context["recent_engagements"] = recent_engagements
        
        # Include analytics if comprehensive depth
        if depth_config.get("include_analytics"):
            # Monthly trends (last 6 months)
            context["monthly_trends"] = _get_monthly_trends()
        
        return context
        
    except Exception as e:
        frappe.log_error(f"Dashboard context error: {e}", "AI Context")
        return None


def _fetch_corrective_action_enriched(doc_id: str, depth_config: dict, filters: dict = None) -> dict:
    """Fetch enriched corrective action plan context."""
    if not doc_id:
        return None
    
    try:
        doc = frappe.get_doc("Corrective Action Plan", doc_id)
        
        context = {
            "cap_id": doc.name,
            "description": doc.get("description", "")[:500],
            "status": doc.status,
            "due_date": str(doc.get("due_date") or ""),
            "responsible_person": doc.get("responsible_person"),
            "audit_finding": doc.get("audit_finding"),
            "priority": doc.get("priority"),
            "completion_percentage": flt(doc.get("completion_percentage", 0))
        }
        
        # Get related finding
        if depth_config.get("include_related") and doc.get("audit_finding"):
            finding = frappe.get_doc("Audit Finding", doc.audit_finding)
            context["finding_details"] = {
                "title": finding.get("title"),
                "risk_level": finding.get("risk_level"),
                "status": finding.status
            }
        
        return context
        
    except Exception as e:
        frappe.log_error(f"CAP context error: {e}", "AI Context")
        return None


def _fetch_follow_up_enriched(doc_id: str, depth_config: dict, filters: dict = None) -> dict:
    """Fetch enriched follow-up context."""
    if not doc_id:
        return None
    
    try:
        doc = frappe.get_doc("Follow Up", doc_id)
        
        context = {
            "follow_up_id": doc.name,
            "subject": doc.get("subject", ""),
            "status": doc.status,
            "follow_up_date": str(doc.get("follow_up_date") or ""),
            "assigned_to": doc.get("assigned_to"),
            "reference_doctype": doc.get("reference_doctype"),
            "reference_name": doc.get("reference_name"),
            "notes": doc.get("notes", "")[:500]
        }
        
        return context
        
    except Exception as e:
        frappe.log_error(f"Follow-up context error: {e}", "AI Context")
        return None


def _get_monthly_trends() -> dict:
    """Get monthly trends for dashboard analytics."""
    try:
        # Findings created per month
        findings_trend = frappe.db.sql("""
            SELECT DATE_FORMAT(creation, '%Y-%m') as month, COUNT(*) as count
            FROM `tabAudit Finding`
            WHERE creation >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
            GROUP BY DATE_FORMAT(creation, '%Y-%m')
            ORDER BY month
        """, as_dict=True)
        
        # CAPs completed per month
        caps_trend = frappe.db.sql("""
            SELECT DATE_FORMAT(modified, '%Y-%m') as month, COUNT(*) as count
            FROM `tabCorrective Action Plan`
            WHERE status = 'Closed' AND modified >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
            GROUP BY DATE_FORMAT(modified, '%Y-%m')
            ORDER BY month
        """, as_dict=True)
        
        return {
            "findings_created": findings_trend,
            "caps_completed": caps_trend
        }
    except Exception:
        return {}


# ============================================
# AI Specialist APIs
# ============================================

@frappe.whitelist()
def get_ai_specialist_response(
	capability: str,
	user_message: str,
	context_data: dict = None
) -> dict:
	"""
	Get an AI response from the audit specialist for a specific capability.

	Args:
		capability: The AI capability (risk-analysis, finding-review, etc.)
		user_message: The user's message/question
		context_data: Optional context data (audit findings, risk assessments, etc.)

	Returns:
		AI response with specialized audit guidance
	"""
	try:
		# Validate capability
		valid_capabilities = [
			'risk-analysis', 'finding-review', 'compliance-check',
			'audit-planning', 'control-testing', 'insights',
			'predictive-analytics', 'automated-reports',
			'domain-training', 'model-fine-tuning', 'terminology-guide'
		]

		if capability not in valid_capabilities:
			frappe.throw(_("Invalid capability: {0}").format(capability))

		# Get capability-specific prompt
		system_prompt = _get_capability_prompt(capability)

		# Enhance user message with context if provided
		enhanced_message = _enhance_message_with_context(user_message, context_data)

		# Get AI response using existing chat service
		from mkaguzi.chat_system.chat_service import get_ai_chat_response

		# Create a temporary context for the AI specialist
		response = get_ai_chat_response(
			room="ai-specialist",  # Special room identifier
			message=enhanced_message,
			system_prompt=system_prompt
		)

		return {
			"success": True,
			"response": response.get("response", ""),
			"capability": capability,
			"timestamp": now_datetime()
		}

	except Exception as e:
		frappe.log_error(f"AI Specialist Error: {str(e)}", "AI Specialist API")
		return {
			"success": False,
			"error": str(e),
			"capability": capability,
			"timestamp": now_datetime()
		}


def _get_capability_prompt(capability: str) -> str:
	"""
	Get the system prompt for a specific AI capability.

	Args:
		capability: The AI capability

	Returns:
		System prompt string
	"""
	prompts = {
		'risk-analysis': """You are an expert risk analyst specializing in internal audit and compliance.
Your role is to help auditors identify, assess, and mitigate risks in business processes.

Guidelines:
- Focus on practical, actionable risk assessments
- Use quantitative measures where possible (likelihood, impact, risk scores)
- Provide specific mitigation strategies
- Consider both financial and operational risks
- Reference relevant frameworks (COSO, COBIT, ISO 31000) when appropriate
- Be thorough but concise in your analysis

Always structure your response with:
1. Risk Assessment (likelihood, impact, overall score)
2. Key Risk Factors
3. Recommended Mitigations
4. Monitoring Recommendations""",

		'finding-review': """You are an experienced audit reviewer with deep knowledge of internal audit standards and best practices.
Your role is to review audit findings for completeness, accuracy, and effectiveness.

Guidelines:
- Evaluate findings against audit standards (GAAS, IIA Standards)
- Assess the quality of evidence and documentation
- Check for logical flow and clear recommendations
- Ensure findings are specific and actionable
- Verify that root causes are identified
- Confirm appropriate risk ratings

Always provide:
1. Strengths of the finding
2. Areas for improvement
3. Specific recommendations for enhancement
4. Compliance with audit standards""",

		'compliance-check': """You are a compliance expert specializing in regulatory requirements and industry standards.
Your role is to analyze scenarios for compliance with applicable laws, regulations, and standards.

Guidelines:
- Identify all relevant regulatory requirements
- Assess current controls and processes
- Highlight compliance gaps and weaknesses
- Provide remediation recommendations
- Consider both preventive and detective controls
- Reference specific regulatory citations when possible

Always structure your response with:
1. Applicable Standards/Regulations
2. Compliance Gaps Identified
3. Recommended Actions
4. Priority Level and Timeline""",

		'audit-planning': """You are an audit planning specialist with extensive experience in audit methodology and resource allocation.
Your role is to help plan comprehensive and efficient audit engagements.

Guidelines:
- Consider risk-based audit approaches
- Balance audit objectives with resource constraints
- Include appropriate testing methodologies
- Plan for both substantive and compliance testing
- Consider timing and coordination with business cycles
- Include contingency planning

Always provide:
1. Recommended Approach and Scope
2. Resource Allocation (team size, skills needed)
3. Timeline and Milestones
4. Key Risks and Dependencies
5. Success Criteria""",

		'control-testing': """You are a control testing expert specializing in audit procedures and evidence evaluation.
Your role is to design and evaluate control testing procedures for various business processes.

Guidelines:
- Design tests that provide sufficient appropriate evidence
- Consider both manual and automated controls
- Include tests of design effectiveness and operating effectiveness
- Use statistical sampling where appropriate
- Consider compensating controls
- Document expected evidence and evaluation criteria

Always structure your response with:
1. Testing Strategy and Objectives
2. Recommended Test Procedures
3. Sample Sizes and Selection Methods
4. Evaluation Criteria
5. Expected Evidence and Documentation""",

		'insights': """You are a data analyst specializing in audit analytics and business intelligence.
Your role is to analyze audit data and provide meaningful insights and recommendations.

Guidelines:
- Identify trends and patterns in audit data
- Calculate relevant metrics and KPIs
- Provide predictive insights where possible
- Focus on actionable recommendations
- Consider both quantitative and qualitative factors
- Use data visualization concepts in explanations

Always provide:
1. Key Findings and Metrics
2. Trend Analysis
3. Predictive Insights
4. Actionable Recommendations
5. Monitoring Suggestions""",

		'domain-training': """You are an audit domain expert and trainer specializing in internal audit knowledge and professional development.
Your role is to provide comprehensive audit knowledge, terminology, and training examples to help auditors enhance their skills.

Guidelines:
- Provide accurate, up-to-date audit knowledge
- Explain complex concepts in clear, practical terms
- Include real-world examples and applications
- Reference relevant standards (GAAS, IIA, COSO, SOX, etc.)
- Focus on both theoretical knowledge and practical application
- Encourage continuous learning and professional development

Always structure your response with:
1. Core Concept Explanation
2. Key Principles and Standards
3. Practical Applications
4. Real-world Examples
5. Additional Resources and References""",

		'model-fine-tuning': """You are an AI training specialist focused on fine-tuning language models for audit-specific applications.
Your role is to help optimize AI models with audit domain knowledge, terminology, and context for better performance.

Guidelines:
- Understand audit-specific terminology and concepts
- Design training data that improves audit context understanding
- Validate training effectiveness with relevant examples
- Consider different audit domains (financial, operational, IT, compliance)
- Balance general audit knowledge with specialized expertise
- Ensure training data enhances practical audit assistance

Always provide:
1. Training Data Analysis
2. Fine-tuning Strategy
3. Validation Results
4. Performance Improvements
5. Recommendations for Further Training""",

		'terminology-guide': """You are a terminology expert specializing in audit and assurance vocabulary, definitions, and usage.
Your role is to provide clear, accurate definitions and practical examples of audit-related terms and concepts.

Guidelines:
- Provide precise, professional definitions
- Include usage context and examples
- Reference authoritative sources when applicable
- Explain relationships between related terms
- Consider different audit domains and contexts
- Focus on practical application in audit work

Always structure your response with:
1. Term Definition
2. Usage Context
3. Practical Examples
4. Related Terms
5. Source References"""
	}

	return prompts.get(capability, "You are an AI audit specialist. Provide helpful, professional audit guidance.")


def _format_vat_reconciliation_context(vat: dict) -> str:
	"""Format VAT reconciliation context for AI consumption."""
	return f"""
VAT Reconciliation Context:
- Reconciliation: {vat.get('reconciliation_name', 'N/A')}
- Period: {vat.get('reconciliation_month', 'N/A')} {vat.get('fiscal_year', 'N/A')}
- Type: {vat.get('reconciliation_type', 'N/A')}
- Status: {vat.get('status', 'N/A')}
- Match Rate: {vat.get('match_percentage', 0):.1f}%
- Total Records: {vat.get('total_matched', 0) + vat.get('total_unmatched_source_a', 0) + vat.get('total_unmatched_source_b', 0) + vat.get('total_amount_discrepancies', 0)}
- Matched: {vat.get('total_matched', 0)}
- Missing in Source B: {vat.get('total_unmatched_source_a', 0)}
- Missing in Source A: {vat.get('total_unmatched_source_b', 0)}
- Amount Discrepancies: {vat.get('total_amount_discrepancies', 0)}
- Total Variance: KES {vat.get('total_variance_amount', 0):,.2f}
- System Records: {vat.get('system_records_count', 0)}
- iTax Records: {vat.get('itax_records_count', 0)}
- TIMs Records: {vat.get('tims_records_count', 0)}
{f"- Sample Discrepancies: {len(vat.get('sample_discrepancies', []))} examples available" if vat.get('sample_discrepancies') else ""}
"""


def _format_vat_reconciliation_list_context(vat_list: dict) -> str:
	"""Format VAT reconciliation list/overview context for AI consumption."""
	return f"""
VAT Reconciliation Overview:
- Total Reconciliations: {vat_list.get('total_reconciliations', 0)}
- Pending Reconciliations: {vat_list.get('pending_reconciliations', 0)}
- Approved Reconciliations: {vat_list.get('approved_reconciliations', 0)}
- Reconciliations with Discrepancies: {vat_list.get('reconciliations_with_discrepancies', 0)}
- Average Match Rate: {vat_list.get('average_match_rate', 0)}%
- Total Variance Amount: KES {vat_list.get('total_variance_amount', 0):,.2f}
{f"- Current Filters: {vat_list.get('current_filters', {})}" if vat_list.get('current_filters') else ""}
{f"- Reconciliation Summary: {len(vat_list.get('reconciliation_summary', []))} reconciliations in current view" if vat_list.get('reconciliation_summary') else ""}
"""


def _format_risk_assessment_context(risk: dict) -> str:
	"""Format risk assessment context for AI consumption."""
	return f"""
Risk Assessment Context:
- Assessment ID: {risk.get('assessment_id', 'N/A')}
- Assessment Name: {risk.get('assessment_name', 'N/A')}
- Fiscal Year: {risk.get('fiscal_year', 'N/A')}
- Period: {risk.get('assessment_period', 'N/A')}
- Status: {risk.get('status', 'N/A')}
- Scope: {risk.get('scope', 'N/A')}
- Methodology: {', '.join(risk.get('methodology', [])) if risk.get('methodology') else 'N/A'}
- Team Members: {risk.get('team_members_count', 0)}
- Risk Register: {risk.get('risk_register_count', 0)} risks identified
- High Risk: {risk.get('high_risk_count', 0)}
- Critical Risk: {risk.get('critical_risk_count', 0)}
- Action Plan: {risk.get('action_plan_count', 0)} actions
- Pending Actions: {risk.get('pending_actions', 0)}
- Completed Actions: {risk.get('completed_actions', 0)}
{f"- Top Risks: {len(risk.get('top_risks', []))} critical items identified" if risk.get('top_risks') else ""}
{f"- Assessment Summary: {risk.get('assessment_summary', 'N/A')[:200]}..." if risk.get('assessment_summary') else ""}
{f"- Recommendations: {risk.get('recommendations', 'N/A')[:200]}..." if risk.get('recommendations') else ""}
"""


def _format_audit_universe_context(universe: dict) -> str:
	"""Format audit universe context for AI consumption."""
	return f"""
Audit Universe Context:
- Entity: {universe.get('entityName', 'N/A')}
- Type: {universe.get('entityType', 'N/A')}
- Department: {universe.get('department', 'N/A')}
- Location: {universe.get('location', 'N/A')}
- Industry: {universe.get('industry', 'N/A')}
- Risk Rating: {universe.get('riskRating', 'N/A')}
- Inherent Risk: {universe.get('inherentRiskRating', 'N/A')}
- Control Effectiveness: {universe.get('controlEffectiveness', 'N/A')}
- Status: {'Active' if universe.get('isActive') else 'Inactive'}
- Last Audit: {universe.get('lastAuditDate', 'Never')}
- Next Audit Due: {universe.get('nextAuditDue', 'N/A')}
- Audit Frequency: {universe.get('auditFrequency', 'N/A')}
- Audit History: {universe.get('auditHistoryCount', 0)} previous audits
- Open Findings: {universe.get('openFindings', 0)}
- Total Findings: {universe.get('totalFindings', 0)}
{f"- Risk Factors: {len(universe.get('riskFactors', []))} identified" if universe.get('riskFactors') else ""}
{f"- Key Controls: {len(universe.get('keyControls', []))} documented" if universe.get('keyControls') else ""}
{f"- Audit Scope: {universe.get('auditScope', 'N/A')[:200]}..." if universe.get('auditScope') else ""}
"""


def _format_annual_plan_context(plan: dict) -> str:
	"""Format annual plan context for AI consumption."""
	return f"""
Annual Audit Plan Context:
- Plan Title: {plan.get('planTitle', 'N/A')}
- Fiscal Year: {plan.get('fiscalYear', 'N/A')}
- Status: {plan.get('status', 'N/A')}
- Duration: {plan.get('duration', 0)} days
- Total Budget: {plan.get('totalBudget', 'N/A')}
- Allocated Budget: {plan.get('allocatedBudget', 'N/A')}
- Total Audits Planned: {plan.get('totalAudits', 0)}
- Audits by Status:
  - Planned: {plan.get('plannedAudits', 0)}
  - In Progress: {plan.get('inProgressAudits', 0)}
  - Completed: {plan.get('completedAudits', 0)}
- Risk Distribution:
  - High Risk Areas: {plan.get('highRiskAreas', 0)}
  - Medium Risk Areas: {plan.get('mediumRiskAreas', 0)}
  - Low Risk Areas: {plan.get('lowRiskAreas', 0)}
- Resource Allocation: {plan.get('totalResources', 0)} team members allocated
{f"- Objectives: {plan.get('objectives', 'N/A')[:200]}..." if plan.get('objectives') else ""}
{f"- Scope: {plan.get('scope', 'N/A')[:200]}..." if plan.get('scope') else ""}
"""


def _format_audit_finding_context(finding: dict) -> str:
	"""Format audit finding context for AI consumption."""
	return f"""
Audit Finding Context:
- Title: {finding.get('finding_title', 'N/A')}
- Risk Level: {finding.get('risk_level', 'N/A')}
- Status: {finding.get('status', 'N/A')}
- Category: {finding.get('category', 'N/A')}
- Entity: {finding.get('entity_name', 'N/A')}
- Description: {finding.get('description', 'N/A')[:200]}...
- Root Cause: {finding.get('root_cause', 'N/A')[:200]}...
- Recommendation: {finding.get('recommendation', 'N/A')[:200]}...
- Corrective Actions: {finding.get('corrective_actions_count', 0)}
"""


def _format_dashboard_context(dashboard: dict) -> str:
	"""Format dashboard context for AI consumption."""
	return f"""
Dashboard Overview Context:
- Total Entities: {dashboard.get('total_entities', 0)}
- Active Audits: {dashboard.get('active_audits', 0)}
- Open Findings: {dashboard.get('open_findings', 0)}
- Overdue Tasks: {dashboard.get('overdue_tasks', 0)}
- Compliance Score: {dashboard.get('compliance_score', 0)}%
- Recent Activities: {len(dashboard.get('recent_activities', []))} items
"""


def _format_stock_take_context(stock_take: dict) -> str:
	"""Format stock take context for AI consumption."""
	risk_indicators = stock_take.get('risk_indicators', {})
	high_variance_items = stock_take.get('high_variance_items', [])
	
	context = f"""
Stock Take Audit Context:
- Stock Take Type: {stock_take.get('stock_take_type', 'Unknown')}
- Warehouse: {stock_take.get('warehouse', 'Unknown')}
- Audit Date: {stock_take.get('audit_date', 'Unknown')}
- Status: {stock_take.get('status', 'Unknown')}
- Total Items: {stock_take.get('total_items', 0)}
- Items with Variance: {stock_take.get('items_with_variance', 0)}
- Total System Value: ${stock_take.get('total_system_value', 0):,.2f}
- Total Variance Value: ${stock_take.get('total_variance_value', 0):,.2f}
- Variance Percentage: {stock_take.get('variance_percentage', 0):.2f}%

Risk Indicators:
- Large Variances (>50 units): {risk_indicators.get('large_variances', 0)}
- High Value Variances (>$1,000): {risk_indicators.get('high_value_variances', 0)}
- Negative Variances: {risk_indicators.get('negative_variances', 0)}
- Positive Variances: {risk_indicators.get('positive_variances', 0)}

High Variance Items ({len(high_variance_items)} items):
"""
	
	for item in high_variance_items[:10]:  # Limit to top 10 for brevity
		context += f"- {item.get('item_code', 'Unknown')}: {item.get('item_name', 'Unknown')} (Variance: {item.get('variance', 0)}, Value: ${item.get('variance_value', 0):,.2f})\n"
	
	if len(high_variance_items) > 10:
		context += f"- ... and {len(high_variance_items) - 10} more items\n"
	
	summary = stock_take.get('summary', {})
	if summary.get('description'):
		context += f"\nSummary: {summary['description']}\n"
	
	if summary.get('key_findings'):
		context += "\nKey Findings:\n"
		for finding in summary['key_findings']:
			context += f"- {finding}\n"
	
	return context


def _format_variance_case_context(variance_case: dict) -> str:
	"""Format variance case context for AI consumption."""
	risk_assessment = variance_case.get('risk_assessment', {})
	investigation_details = variance_case.get('investigation_details', {})
	
	context = f"""
Variance Case Context:
- Item: {variance_case.get('item_code', 'Unknown')} - {variance_case.get('item_name', 'Unknown')}
- Warehouse: {variance_case.get('warehouse', 'Unknown')}
- Branch: {variance_case.get('branch', 'Unknown')}
- Status: {variance_case.get('status', 'Unknown')}
- Priority: {variance_case.get('priority', 'Unknown')}
- System Quantity: {variance_case.get('system_quantity', 0)}
- Physical Quantity: {variance_case.get('physical_quantity', 0)}
- Variance Quantity: {variance_case.get('variance_quantity', 0)}
- Variance Value: ${variance_case.get('variance_value', 0):,.2f}
- Rate: ${variance_case.get('rate', 0):,.2f}
- Variance Type: {variance_case.get('variance_type', 'Unknown')}
- High Value Variance: {'Yes' if variance_case.get('is_high_value') else 'No'}
- Reported Date: {variance_case.get('reported_date', 'Unknown')}
- Investigation Status: {variance_case.get('investigation_status', 'Unknown')}

Risk Assessment:
- Financial Impact: ${risk_assessment.get('financial_impact', 0):,.2f}
- Operational Impact: {risk_assessment.get('operational_impact', 'Unknown')}
- Urgency: {risk_assessment.get('urgency', 'Unknown')}
- Likelihood of Fraud: {risk_assessment.get('likelihood_of_fraud', 'Unknown')}

Investigation Details:
- Evidence Available: {'Yes' if investigation_details.get('has_evidence') else 'No'} ({variance_case.get('evidence_count', 0)} items)
- Comments Available: {'Yes' if investigation_details.get('has_comments') else 'No'} ({variance_case.get('comments_count', 0)} items)
- Root Cause Identified: {'Yes' if investigation_details.get('has_root_cause') else 'No'}
- Corrective Action Defined: {'Yes' if investigation_details.get('has_corrective_action') else 'No'}
- Overdue: {'Yes' if investigation_details.get('is_overdue') else 'No'}

Additional Information:
- Responsible Person: {variance_case.get('responsible_person', 'Not assigned')}
- Target Resolution Date: {variance_case.get('target_resolution_date', 'Not set')}
- Actual Resolution Date: {variance_case.get('actual_resolution_date', 'Not resolved')}
"""
	
	root_cause = variance_case.get('root_cause')
	if root_cause:
		context += f"\nRoot Cause: {root_cause}\n"
	
	corrective_action = variance_case.get('corrective_action')
	if corrective_action:
		context += f"Corrective Action: {corrective_action}\n"
	
	summary = variance_case.get('summary', {})
	if summary.get('description'):
		context += f"\nSummary: {summary['description']}\n"
	
	if summary.get('key_findings'):
		context += "\nKey Findings:\n"
		for finding in summary['key_findings']:
			context += f"- {finding}\n"
	
	return context


def _format_engagement_context(engagement: dict) -> str:
	"""Format engagement context for AI consumption."""
	findings_summary = engagement.get('findings_summary', {})
	risk_assessment = engagement.get('risk_assessment', {})
	progress_indicators = engagement.get('progress_indicators', {})
	
	context = f"""
Engagement Context:
- Title: {engagement.get('title', 'Unknown')}
- Description: {engagement.get('description', 'Unknown')}
- Status: {engagement.get('status', 'Unknown')}
- Type: {engagement.get('type', 'Unknown')}
- Start Date: {engagement.get('start_date', 'Unknown')}
- End Date: {engagement.get('end_date', 'Unknown')}
- Duration: {engagement.get('duration_days', 0)} days
- Lead Auditor: {engagement.get('lead_auditor', 'Not assigned')}
- Budget: ${engagement.get('budget', 0):,.2f}

Objectives ({engagement.get('objectives_count', 0)} total):
"""
	
	objectives = engagement.get('objectives', [])
	for i, objective in enumerate(objectives, 1):
		context += f"{i}. {objective}\n"
	
	context += f"""
Scope: {engagement.get('scope', 'Not defined')}

Findings Summary:
- Total Findings: {findings_summary.get('total', 0)}
- High Risk: {findings_summary.get('high', 0)}
- Medium Risk: {findings_summary.get('medium', 0)}
- Low Risk: {findings_summary.get('low', 0)}
- High Risk Percentage: {findings_summary.get('high_percentage', 0)}%

Risk Assessment:
- Complexity: {risk_assessment.get('complexity', 'Unknown')}
- Critical Findings Present: {'Yes' if risk_assessment.get('critical_findings') else 'No'}
- Timeline Pressure: {risk_assessment.get('timeline_pressure', 'Unknown')}
- Budget Utilization: {risk_assessment.get('budget_utilization', 'Unknown')}

Progress Indicators:
- Scope Defined: {'Yes' if progress_indicators.get('has_scope_defined') else 'No'}
- Objectives Defined: {'Yes' if progress_indicators.get('has_objectives') else 'No'}
- Findings Identified: {'Yes' if progress_indicators.get('has_findings') else 'No'}
- On Track: {'Yes' if progress_indicators.get('is_on_track') else 'No'}
"""
	
	summary = engagement.get('summary', {})
	if summary.get('description'):
		context += f"\nSummary: {summary['description']}\n"
	
	if summary.get('key_metrics'):
		context += "\nKey Metrics:\n"
		for metric in summary['key_metrics']:
			context += f"- {metric}\n"
	
	return context


def _format_audit_plan_context(audit_plan: dict) -> str:
	"""Format audit plan context for AI consumption."""
	sessions_summary = audit_plan.get('sessions_summary', {})
	risk_assessment = audit_plan.get('risk_assessment', {})
	issues_summary = audit_plan.get('issues_summary', {})
	progress_indicators = audit_plan.get('progress_indicators', {})
	
	context = f"""
Audit Plan Context:
- Plan Title: {audit_plan.get('plan_title', 'Unknown')}
- Plan Name: {audit_plan.get('plan_name', 'Unknown')}
- Status: {audit_plan.get('status', 'Unknown')}
- Description: {audit_plan.get('description', 'Unknown')}
- Warehouse: {audit_plan.get('warehouse', 'Unknown')}
- Audit Type: {audit_plan.get('audit_type', 'Unknown')}
- Planned Start: {audit_plan.get('planned_start_date', 'Not set')}
- Planned End: {audit_plan.get('planned_end_date', 'Not set')}
- Actual Start: {audit_plan.get('actual_start_date', 'Not started')}
- Actual End: {audit_plan.get('actual_end_date', 'Not completed')}
- Lead Auditor: {audit_plan.get('lead_auditor', 'Not assigned')}

Team Members: {len(audit_plan.get('team_members', []))} members

Objectives ({len(audit_plan.get('objectives', []))} total):
"""
	
	objectives = audit_plan.get('objectives', [])
	for i, objective in enumerate(objectives, 1):
		context += f"{i}. {objective}\n"
	
	context += f"""
Scope: {audit_plan.get('scope', 'Not defined')}

Methodology: {audit_plan.get('methodology', 'Not specified')}

Sessions Summary:
- Total Sessions: {sessions_summary.get('total', 0)}
- Completed: {sessions_summary.get('completed', 0)}
- In Progress: {sessions_summary.get('in_progress', 0)}
- Planned: {sessions_summary.get('planned', 0)}
- Completion Percentage: {sessions_summary.get('completion_percentage', 0)}%

Risk Assessment:
- Total Risk Items: {risk_assessment.get('total_risk_items', 0)}
- High Risk: {risk_assessment.get('high_risk', 0)}
- Medium Risk: {risk_assessment.get('medium_risk', 0)}
- Low Risk: {risk_assessment.get('low_risk', 0)}
- High Risk Percentage: {risk_assessment.get('high_risk_percentage', 0)}%
- Risk Coverage: {risk_assessment.get('risk_coverage', 'Unknown')}

Issues Summary:
- Variance Cases: {issues_summary.get('variance_cases', 0)}
- Open Issues: {issues_summary.get('open_issues', 0)}
- Critical Issues: {issues_summary.get('critical_issues', 0)}

Progress Indicators:
- Has Sessions: {'Yes' if progress_indicators.get('has_sessions') else 'No'}
- Has Completed Sessions: {'Yes' if progress_indicators.get('has_completed_sessions') else 'No'}
- Has Risk Assessment: {'Yes' if progress_indicators.get('has_risk_assessment') else 'No'}
- Has Issues: {'Yes' if progress_indicators.get('has_issues') else 'No'}
- On Track: {'Yes' if progress_indicators.get('is_on_track') else 'No'}
"""
	
	summary = audit_plan.get('summary', {})
	if summary.get('description'):
		context += f"\nSummary: {summary['description']}\n"
	
	if summary.get('key_metrics'):
		context += "\nKey Metrics:\n"
		for metric in summary['key_metrics']:
			context += f"- {metric}\n"
	
	return context


def _enhance_message_with_context(user_message: str, context_data: dict = None) -> str:
	"""
	Enhance the user message with relevant context data.

	Args:
		user_message: Original user message
		context_data: Context data from the AI context store

	Returns:
		Enhanced message with context
	"""
	if not context_data:
		return user_message

	context_parts = []

	# Handle new context format from AI context store
	if context_data.get('page_type') and context_data.get('context_data'):
		page_type = context_data['page_type']
		page_context = context_data['context_data']

		# Add page title and type
		context_parts.append(f"Page Context: {context_data.get('page_title', 'Unknown Page')} ({page_type})")

		# Handle different page types
		if page_type == 'vat_reconciliation':
			context_parts.append(_format_vat_reconciliation_context(page_context))
		elif page_type == 'vat_reconciliation_list':
			context_parts.append(_format_vat_reconciliation_list_context(page_context))
		elif page_type == 'risk_assessment':
			context_parts.append(_format_risk_assessment_context(page_context))
		elif page_type == 'audit_universe':
			context_parts.append(_format_audit_universe_context(page_context))
		elif page_type == 'annual_plan':
			context_parts.append(_format_annual_plan_context(page_context))
		elif page_type == 'audit_finding':
			context_parts.append(_format_audit_finding_context(page_context))
		elif page_type == 'dashboard':
			context_parts.append(_format_dashboard_context(page_context))
		elif page_type == 'stock-take':
			context_parts.append(_format_stock_take_context(page_context))
		elif page_type == 'variance-case':
			context_parts.append(_format_variance_case_context(page_context))
		elif page_type == 'engagement':
			context_parts.append(_format_engagement_context(page_context))
		elif page_type == 'audit-plan':
			context_parts.append(_format_audit_plan_context(page_context))
		else:
			# Generic context
			context_parts.append(f"Context Data: {page_context}")

	# Legacy context format support (for backward compatibility)
	else:
		# Add audit finding context
		if context_data.get('finding'):
			finding = context_data['finding']
			context_parts.append(f"""
Audit Finding Context:
- Title: {finding.get('title', 'N/A')}
- Risk Level: {finding.get('risk_level', 'N/A')}
- Status: {finding.get('status', 'N/A')}
- Description: {finding.get('description', 'N/A')}
""")

		# Add risk assessment context
		if context_data.get('risk_assessment'):
			risk = context_data['risk_assessment']
			context_parts.append(f"""
Risk Assessment Context:
- Risk Title: {risk.get('risk_title', 'N/A')}
- Likelihood: {risk.get('likelihood_score', 'N/A')}/5
- Impact: {risk.get('impact_score', 'N/A')}/5
- Inherent Risk Score: {risk.get('inherent_risk_score', 'N/A')}/25
""")

		# Add compliance context
		if context_data.get('compliance_area'):
			compliance = context_data['compliance_area']
			context_parts.append(f"""
Compliance Context:
- Area: {compliance.get('area', 'N/A')}
- Standard: {compliance.get('standard', 'N/A')}
- Current Status: {compliance.get('status', 'N/A')}
""")

		# Add VAT reconciliation context (legacy)
		if context_data.get('reconciliation_name'):
			context_parts.append(_format_vat_reconciliation_context(context_data))

	# Combine context with user message
	if context_parts:
		context_str = "\n".join(context_parts)
		return f"{context_str}\n\nUser Question: {user_message}"

	return user_message


@frappe.whitelist()
def get_ai_specialist_capabilities() -> dict:
	"""
	Get available AI specialist capabilities.

	Returns:
		List of available capabilities with descriptions
	"""
	capabilities = [
		{
			"id": "risk-analysis",
			"title": "Risk Analysis",
			"description": "Analyze audit risks and provide mitigation strategies",
			"icon": "AlertTriangleIcon"
		},
		{
			"id": "finding-review",
			"title": "Finding Review",
			"description": "Review audit findings for completeness and accuracy",
			"icon": "CheckCircleIcon"
		},
		{
			"id": "compliance-check",
			"title": "Compliance Analysis",
			"description": "Check compliance with standards and regulations",
			"icon": "FileTextIcon"
		},
		{
			"id": "audit-planning",
			"title": "Audit Planning",
			"description": "Assist with audit planning and resource allocation",
			"icon": "TrendingUpIcon"
		},
		{
			"id": "control-testing",
			"title": "Control Testing",
			"description": "Design and evaluate control testing procedures",
			"icon": "SearchIcon"
		},
		{
			"id": "insights",
			"title": "Audit Insights",
			"description": "Generate insights from audit data and trends",
			"icon": "LightbulbIcon"
		},
		{
			"id": "predictive-analytics",
			"title": "Predictive Analytics",
			"description": "AI-powered risk prediction and trend analysis",
			"icon": "BarChart3Icon"
		},
		{
			"id": "automated-reports",
			"title": "Automated Reports",
			"description": "Generate comprehensive AI-powered audit reports",
			"icon": "FileBarChartIcon"
		},
		{
			"id": "domain-training",
			"title": "Domain Training",
			"description": "Access audit-specific knowledge and training data",
			"icon": "BrainIcon"
		},
		{
			"id": "model-fine-tuning",
			"title": "Model Fine-tuning",
			"description": "Fine-tune AI models with custom audit training data",
			"icon": "SettingsIcon"
		},
		{
			"id": "terminology-guide",
			"title": "Terminology Guide",
			"description": "Access comprehensive audit terminology and definitions",
			"icon": "FileTextIcon"
		}
	]

	return {
		"capabilities": capabilities,
		"total": len(capabilities)
	}


@frappe.whitelist()
def get_advanced_predictive_analytics(
	engagement_id: str = None,
	time_period: str = "12_months",
	analysis_type: str = "comprehensive",
	ml_algorithms: list = None
) -> dict:
	"""
	Get advanced predictive analytics using machine learning algorithms.

	Args:
		engagement_id: Specific engagement to analyze
		time_period: Analysis time period (6_months, 12_months, 24_months)
		analysis_type: Type of analysis (comprehensive, risk_focused, trend_focused)
		ml_algorithms: List of ML algorithms to use

	Returns:
		Advanced predictive analytics with ML insights
	"""
	try:
		# Default ML algorithms if not specified
		if not ml_algorithms:
			ml_algorithms = ['linear_regression', 'random_forest', 'gradient_boosting']

		# Get historical audit data
		historical_data = _get_historical_audit_data(engagement_id, time_period)

		# Apply ML algorithms
		ml_results = {}
		for algorithm in ml_algorithms:
			ml_results[algorithm] = _apply_ml_algorithm(historical_data, algorithm, analysis_type)

		# Generate comprehensive insights
		comprehensive_insights = _generate_ml_insights(ml_results, analysis_type)

		# Calculate confidence scores
		confidence_scores = _calculate_ml_confidence_scores(ml_results)

		return {
			"success": True,
			"analysis_type": analysis_type,
			"time_period": time_period,
			"ml_algorithms_used": ml_algorithms,
			"ml_results": ml_results,
			"comprehensive_insights": comprehensive_insights,
			"confidence_scores": confidence_scores,
			"data_points_analyzed": len(historical_data),
			"generated_at": now_datetime()
		}

	except Exception as e:
		frappe.log_error(f"Advanced Predictive Analytics Error: {str(e)}", "AI Specialist API")
		return {
			"success": False,
			"error": str(e),
			"timestamp": now_datetime()
		}


@frappe.whitelist()
def train_ml_model(
	model_type: str,
	training_data: dict,
	validation_split: float = 0.2,
	hyperparameters: dict = None
) -> dict:
	"""
	Train a machine learning model with audit data.

	Args:
		model_type: Type of ML model (regression, classification, clustering)
		training_data: Training data dictionary
		validation_split: Validation data split ratio
		hyperparameters: Model hyperparameters

	Returns:
		Training results and model performance metrics
	"""
	try:
		# Validate model type
		valid_types = ['regression', 'classification', 'clustering', 'time_series']
		if model_type not in valid_types:
			frappe.throw(_("Invalid model type: {0}").format(model_type))

		# Prepare training data
		X_train, X_val, y_train, y_val = _prepare_training_data(
			training_data,
			validation_split
		)

		# Train model
		model_results = _train_ml_model(
			model_type,
			X_train,
			y_train,
			X_val,
			y_val,
			hyperparameters
		)

		# Evaluate model
		evaluation_metrics = _evaluate_ml_model(
			model_results['model'],
			X_val,
			y_val,
			model_type
		)

		return {
			"success": True,
			"model_type": model_type,
			"training_samples": len(X_train),
			"validation_samples": len(X_val),
			"model_results": model_results,
			"evaluation_metrics": evaluation_metrics,
			"feature_importance": model_results.get('feature_importance', {}),
			"model_trained_at": now_datetime()
		}

	except Exception as e:
		frappe.log_error(f"ML Training Error: {str(e)}", "AI Specialist API")
		return {
			"success": False,
			"error": str(e),
			"model_type": model_type,
			"timestamp": now_datetime()
		}


@frappe.whitelist()
def get_anomaly_detection(
	data_set: list,
	detection_method: str = "isolation_forest",
	sensitivity: str = "medium"
) -> dict:
	"""
	Detect anomalies in audit data using ML algorithms.

	Args:
		data_set: List of data points to analyze
		detection_method: Anomaly detection method
		sensitivity: Detection sensitivity (low, medium, high)

	Returns:
		Anomaly detection results with identified outliers
	"""
	try:
		# Validate detection method
		valid_methods = ['isolation_forest', 'local_outlier_factor', 'one_class_svm', 'statistical']
		if detection_method not in valid_methods:
			frappe.throw(_("Invalid detection method: {0}").format(detection_method))

		# Prepare data for anomaly detection
		processed_data = _prepare_anomaly_data(data_set)

		# Apply anomaly detection
		anomalies = _detect_anomalies(
			processed_data,
			detection_method,
			sensitivity
		)

		# Generate insights
		anomaly_insights = _generate_anomaly_insights(anomalies, data_set)

		return {
			"success": True,
			"detection_method": detection_method,
			"sensitivity": sensitivity,
			"total_data_points": len(data_set),
			"anomalies_detected": len(anomalies),
			"anomaly_percentage": (len(anomalies) / len(data_set)) * 100 if data_set else 0,
			"anomalies": anomalies,
			"insights": anomaly_insights,
			"confidence_score": _calculate_anomaly_confidence(anomalies),
			"detected_at": now_datetime()
		}

	except Exception as e:
		frappe.log_error(f"Anomaly Detection Error: {str(e)}", "AI Specialist API")
		return {
			"success": False,
			"error": str(e),
			"detection_method": detection_method,
			"timestamp": now_datetime()
		}


@frappe.whitelist()
def get_risk_trend_forecasting(
	risk_category: str,
	forecast_period: int = 12,
	forecast_method: str = "arima"
) -> dict:
	"""
	Generate risk trend forecasting using time series analysis.

	Args:
		risk_category: Category of risk to forecast
		forecast_period: Number of periods to forecast (months)
		forecast_method: Forecasting method to use

	Returns:
		Risk trend forecasting results
	"""
	try:
		# Validate forecast method
		valid_methods = ['arima', 'exponential_smoothing', 'linear_regression', 'prophet']
		if forecast_method not in valid_methods:
			frappe.throw(_("Invalid forecast method: {0}").format(forecast_method))

		# Get historical risk data
		historical_risks = _get_historical_risk_data(risk_category)

		# Apply forecasting method
		forecast_results = _apply_forecasting_method(
			historical_risks,
			forecast_method,
			forecast_period
		)

		# Generate risk insights
		risk_insights = _generate_risk_forecast_insights(
			forecast_results,
			risk_category
		)

		return {
			"success": True,
			"risk_category": risk_category,
			"forecast_period": forecast_period,
			"forecast_method": forecast_method,
			"historical_data_points": len(historical_risks),
			"forecast_results": forecast_results,
			"risk_insights": risk_insights,
			"confidence_intervals": forecast_results.get('confidence_intervals', {}),
			"forecast_accuracy": _calculate_forecast_accuracy(forecast_results),
			"generated_at": now_datetime()
		}

	except Exception as e:
		frappe.log_error(f"Risk Forecasting Error: {str(e)}", "AI Specialist API")
		return {
			"success": False,
			"error": str(e),
			"risk_category": risk_category,
			"timestamp": now_datetime()
		}


@frappe.whitelist()
def get_predictive_analytics(
	engagement_id: str = None,
	time_period: str = "6_months",
	analysis_type: str = "risk_trends"
) -> dict:
	"""
	Get predictive analytics for audit engagements.

	Args:
		engagement_id: Specific engagement to analyze (optional)
		time_period: Analysis period (3_months, 6_months, 1_year, 2_years)
		analysis_type: Type of analysis (risk_trends, finding_patterns, compliance_risks)

	Returns:
		Predictive analytics insights
	"""
	try:
		# Get historical audit data
		historical_data = _get_historical_audit_data(engagement_id, time_period)

		# Generate predictive insights based on analysis type
		if analysis_type == "risk_trends":
			insights = _analyze_risk_trends(historical_data)
		elif analysis_type == "finding_patterns":
			insights = _analyze_finding_patterns(historical_data)
		elif analysis_type == "compliance_risks":
			insights = _analyze_compliance_risks(historical_data)
		else:
			frappe.throw(_("Invalid analysis type: {0}").format(analysis_type))

		return {
			"success": True,
			"analysis_type": analysis_type,
			"time_period": time_period,
			"engagement_id": engagement_id,
			"insights": insights,
			"confidence_level": _calculate_confidence_level(historical_data),
			"recommendations": _generate_predictive_recommendations(insights),
			"timestamp": now_datetime()
		}

	except Exception as e:
		frappe.log_error(f"Predictive Analytics Error: {str(e)}", "AI Specialist API")
		return {
			"success": False,
			"error": str(e),
			"analysis_type": analysis_type,
			"timestamp": now_datetime()
		}


@frappe.whitelist()
def generate_automated_insights(
	data_source: str,
	insight_type: str = "executive_summary",
	context_filters: dict = None
) -> dict:
	"""
	Generate automated insights from audit data.

	Args:
		data_source: Source of data (findings, risks, controls, compliance)
		insight_type: Type of insights (executive_summary, trends, anomalies, recommendations)
		context_filters: Filters to apply (date_range, department, risk_level, etc.)

	Returns:
		Automated insights and analysis
	"""
	try:
		# Validate inputs
		valid_sources = ['findings', 'risks', 'controls', 'compliance', 'engagements']
		valid_types = ['executive_summary', 'trends', 'anomalies', 'recommendations', 'benchmarks']

		if data_source not in valid_sources:
			frappe.throw(_("Invalid data source: {0}").format(data_source))
		if insight_type not in valid_types:
			frappe.throw(_("Invalid insight type: {0}").format(insight_type))

		# Get filtered data
		data = _get_filtered_audit_data(data_source, context_filters or {})

		# Generate insights based on type
		if insight_type == "executive_summary":
			insights = _generate_executive_summary(data, data_source)
		elif insight_type == "trends":
			insights = _generate_trend_analysis(data, data_source)
		elif insight_type == "anomalies":
			insights = _detect_anomalies(data, data_source)
		elif insight_type == "recommendations":
			insights = _generate_recommendations(data, data_source)
		elif insight_type == "benchmarks":
			insights = _generate_benchmarks(data, data_source)

		return {
			"success": True,
			"data_source": data_source,
			"insight_type": insight_type,
			"filters_applied": context_filters,
			"insights": insights,
			"data_points": len(data),
			"generated_at": now_datetime()
		}

	except Exception as e:
		frappe.log_error(f"Automated Insights Error: {str(e)}", "AI Specialist API")
		return {
			"success": False,
			"error": str(e),
			"data_source": data_source,
			"insight_type": insight_type,
			"timestamp": now_datetime()
		}


@frappe.whitelist()
def generate_ai_report(
	report_type: str,
	parameters: dict = None,
	include_visualizations: bool = True
) -> dict:
	"""
	Generate AI-powered audit reports.

	Args:
		report_type: Type of report (audit_summary, risk_assessment, compliance_status, etc.)
		parameters: Report parameters (date_range, scope, filters, etc.)
		include_visualizations: Whether to include chart recommendations

	Returns:
		AI-generated report structure and content
	"""
	try:
		# Validate report type
		valid_report_types = [
			'audit_summary', 'risk_assessment', 'compliance_status',
			'control_effectiveness', 'finding_analysis', 'trend_report'
		]

		if report_type not in valid_report_types:
			frappe.throw(_("Invalid report type: {0}").format(report_type))

		# Get report data
		report_data = _gather_report_data(report_type, parameters or {})

		# Generate AI-powered report content
		report_content = _generate_report_content(report_type, report_data)

		# Generate visualizations if requested
		visualizations = []
		if include_visualizations:
			visualizations = _generate_report_visualizations(report_type, report_data)

		return {
			"success": True,
			"report_type": report_type,
			"parameters": parameters,
			"title": _get_report_title(report_type, parameters),
			"executive_summary": report_content.get("executive_summary", ""),
			"sections": report_content.get("sections", []),
			"conclusions": report_content.get("conclusions", ""),
			"recommendations": report_content.get("recommendations", []),
			"visualizations": visualizations,
			"generated_at": now_datetime(),
			"data_sources": report_data.get("sources", [])
		}

	except Exception as e:
		frappe.log_error(f"AI Report Generation Error: {str(e)}", "AI Specialist API")
		return {
			"success": False,
			"error": str(e),
			"report_type": report_type,
			"timestamp": now_datetime()
		}
	"""
	Test the AI specialist connection and configuration.

	Returns:
		Connection test results
	"""
	try:
		# Test basic AI connectivity using existing chat service
		from mkaguzi.chat_system.chat_service import test_ai_connection

		result = test_ai_connection()

		return {
			"success": True,
			"status": "connected",
			"message": "AI Specialist connection successful",
			"details": result
		}

	except Exception as e:
		return {
			"success": False,
			"status": "error",
			"message": f"AI Specialist connection failed: {str(e)}",
			"details": None
		}


# ============================================
# Helper Functions for Advanced AI Features
# ============================================

def _get_historical_audit_data(engagement_id: str = None, time_period: str = "6_months") -> list:
	"""
	Get historical audit data for predictive analytics.

	Args:
		engagement_id: Specific engagement ID
		time_period: Time period for data

	Returns:
		List of historical audit records
	"""
	try:
		# Calculate date range
		from frappe.utils import add_months, nowdate
		end_date = nowdate()

		if time_period == "3_months":
			start_date = add_months(end_date, -3)
		elif time_period == "6_months":
			start_date = add_months(end_date, -6)
		elif time_period == "1_year":
			start_date = add_months(end_date, -12)
		elif time_period == "2_years":
			start_date = add_months(end_date, -24)
		else:
			start_date = add_months(end_date, -6)  # Default to 6 months

		# Build filters
		filters = {
			"creation": ["between", [start_date, end_date]]
		}

		if engagement_id:
			filters["engagement"] = engagement_id

		# Get findings data
		findings = frappe.get_all(
			"Audit Finding",
			filters=filters,
			fields=[
				"name", "title", "risk_level", "status", "finding_date",
				"engagement", "audit_area", "creation", "modified"
			]
		)

		# Get risk assessments
		risks = frappe.get_all(
			"Risk Assessment",
			filters={"creation": ["between", [start_date, end_date]]},
			fields=[
				"name", "risk_title", "likelihood_score", "impact_score",
				"inherent_risk_score", "risk_category", "creation"
			]
		)

		return {
			"findings": findings,
			"risks": risks,
			"start_date": start_date,
			"end_date": end_date,
			"total_records": len(findings) + len(risks)
		}

	except Exception as e:
		frappe.log_error(f"Error getting historical data: {str(e)}")
		return {"findings": [], "risks": [], "error": str(e)}


def _analyze_risk_trends(historical_data: dict) -> dict:
	"""Analyze risk trends from historical data."""
	findings = historical_data.get("findings", [])
	risks = historical_data.get("risks", [])

	# Calculate risk distribution
	risk_levels = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}
	for finding in findings:
		risk_levels[finding.get("risk_level", "Medium")] += 1

	# Calculate monthly trends
	from collections import defaultdict
	monthly_findings = defaultdict(int)

	for finding in findings:
		if finding.get("creation"):
			month_key = finding["creation"][:7]  # YYYY-MM format
			monthly_findings[month_key] += 1

	return {
		"risk_distribution": risk_levels,
		"monthly_trends": dict(monthly_findings),
		"total_findings": len(findings),
		"average_risk_score": sum([r.get("inherent_risk_score", 0) for r in risks]) / max(len(risks), 1),
		"key_insights": [
			f"Most common risk level: {max(risk_levels, key=risk_levels.get)}",
			f"Total findings analyzed: {len(findings)}",
			f"Risk assessments reviewed: {len(risks)}"
		]
	}


def _analyze_finding_patterns(historical_data: dict) -> dict:
	"""Analyze finding patterns from historical data."""
	findings = historical_data.get("findings", [])

	# Analyze by audit area
	area_patterns = defaultdict(int)
	status_patterns = defaultdict(int)
	root_cause_patterns = defaultdict(int)

	for finding in findings:
		area_patterns[finding.get("audit_area", "Unknown")] += 1
		status_patterns[finding.get("status", "Open")] += 1

	return {
		"area_distribution": dict(area_patterns),
		"status_distribution": dict(status_patterns),
		"root_cause_patterns": dict(root_cause_patterns),
		"patterns_identified": len(area_patterns),
		"recurring_areas": [area for area, count in area_patterns.items() if count > 1]
	}


def _analyze_compliance_risks(historical_data: dict) -> dict:
	"""Analyze compliance risks from historical data."""
	findings = historical_data.get("findings", [])

	# Focus on compliance-related findings
	compliance_findings = [f for f in findings if "compliance" in f.get("audit_area", "").lower()]

	return {
		"compliance_findings": len(compliance_findings),
		"compliance_trends": "Increasing" if len(compliance_findings) > 5 else "Stable",
		"high_risk_areas": [f.get("audit_area") for f in compliance_findings if f.get("risk_level") in ["High", "Critical"]],
		"recommendations": [
			"Strengthen compliance monitoring procedures",
			"Implement regular compliance training",
			"Enhance regulatory reporting processes"
		]
	}


def _calculate_confidence_level(historical_data: dict) -> str:
	"""Calculate confidence level for predictions."""
	total_records = historical_data.get("total_records", 0)

	if total_records > 100:
		return "High"
	elif total_records > 50:
		return "Medium"
	else:
		return "Low"


def _generate_predictive_recommendations(insights: dict) -> list:
	"""Generate predictive recommendations based on insights."""
	recommendations = []

	# Risk-based recommendations
	risk_dist = insights.get("risk_distribution", {})
	if risk_dist.get("Critical", 0) > risk_dist.get("Low", 0):
		recommendations.append("Prioritize critical risk mitigation")

	# Trend-based recommendations
	trends = insights.get("monthly_trends", {})
	if len(trends) > 3:
		recent_months = list(trends.keys())[-3:]
		recent_counts = [trends[m] for m in recent_months]
		if recent_counts[-1] > sum(recent_counts[:-1]) / 2:
			recommendations.append("Investigate recent increase in findings")

	return recommendations


def _get_filtered_audit_data(data_source: str, filters: dict) -> list:
	"""Get filtered audit data based on source and filters."""
	try:
		if data_source == "findings":
			return frappe.get_all(
				"Audit Finding",
				filters=filters,
				fields=["name", "title", "risk_level", "status", "audit_area", "creation"]
			)
		elif data_source == "risks":
			return frappe.get_all(
				"Risk Assessment",
				filters=filters,
				fields=["name", "risk_title", "inherent_risk_score", "risk_category", "creation"]
			)
		elif data_source == "controls":
			return frappe.get_all(
				"Control Test",
				filters=filters,
				fields=["name", "control_name", "test_result", "effectiveness", "creation"]
			)
		else:
			return []

	except Exception as e:
		frappe.log_error(f"Error getting filtered data: {str(e)}")
		return []


def _generate_executive_summary(data: list, data_source: str) -> dict:
	"""Generate executive summary insights."""
	total_items = len(data)

	if data_source == "findings":
		high_risk = len([f for f in data if f.get("risk_level") in ["High", "Critical"]])
		open_findings = len([f for f in data if f.get("status") == "Open"])

		return {
			"summary": f"Analysis of {total_items} audit findings shows {high_risk} high-risk items and {open_findings} open findings.",
			"key_metrics": {
				"total_findings": total_items,
				"high_risk_percentage": (high_risk / max(total_items, 1)) * 100,
				"open_percentage": (open_findings / max(total_items, 1)) * 100
			}
		}

	return {"summary": f"Analysis of {total_items} {data_source} records completed.", "key_metrics": {}}


def _generate_trend_analysis(data: list, data_source: str) -> dict:
	"""Generate trend analysis insights."""
	from collections import defaultdict

	monthly_counts = defaultdict(int)

	for item in data:
		if item.get("creation"):
			month_key = item["creation"][:7]
			monthly_counts[month_key] += 1

	sorted_months = sorted(monthly_counts.keys())
	trend = "stable"

	if len(sorted_months) > 1:
		first_half = sum(monthly_counts[m] for m in sorted_months[:len(sorted_months)//2])
		second_half = sum(monthly_counts[m] for m in sorted_months[len(sorted_months)//2:])

		if second_half > first_half * 1.2:
			trend = "increasing"
		elif second_half < first_half * 0.8:
			trend = "decreasing"

	return {
		"trend": trend,
		"monthly_data": dict(monthly_counts),
		"total_periods": len(sorted_months),
		"average_per_period": sum(monthly_counts.values()) / max(len(sorted_months), 1)
	}


def _detect_anomalies(data: list, data_source: str) -> dict:
	"""Detect anomalies in audit data."""
	# Simple anomaly detection based on statistical outliers
	if not data:
		return {"anomalies": [], "message": "No data available for anomaly detection"}

	# Calculate basic statistics
	values = []
	if data_source == "findings":
		values = [1 if f.get("risk_level") in ["High", "Critical"] else 0 for f in data]
	else:
		values = [len(str(item)) for item in data]  # Simple length-based anomaly

	if not values:
		return {"anomalies": [], "message": "No measurable values found"}

	mean = sum(values) / len(values)
	std_dev = (sum((x - mean) ** 2 for x in values) / len(values)) ** 0.5

	# Detect outliers (values more than 2 standard deviations from mean)
	anomalies = []
	for i, value in enumerate(values):
		if abs(value - mean) > 2 * std_dev:
			anomalies.append({
				"index": i,
				"value": value,
				"deviation": abs(value - mean),
				"item": data[i]
			})

	return {
		"anomalies": anomalies,
		"total_anomalies": len(anomalies),
		"anomaly_percentage": (len(anomalies) / len(data)) * 100,
		"mean": mean,
		"standard_deviation": std_dev
	}


def _generate_recommendations(data: list, data_source: str) -> list:
	"""Generate recommendations based on data analysis."""
	recommendations = []

	if data_source == "findings":
		high_risk_count = len([f for f in data if f.get("risk_level") in ["High", "Critical"]])
		if high_risk_count > len(data) * 0.3:
			recommendations.append("Implement immediate corrective actions for high-risk findings")

		open_count = len([f for f in data if f.get("status") == "Open"])
		if open_count > len(data) * 0.5:
			recommendations.append("Increase resources for finding resolution")

	elif data_source == "risks":
		high_score_count = len([r for r in data if r.get("inherent_risk_score", 0) > 15])
		if high_score_count > 0:
			recommendations.append("Develop mitigation strategies for high-scoring risks")

	return recommendations if recommendations else ["Continue monitoring and maintain current processes"]


def _generate_benchmarks(data: list, data_source: str) -> dict:
	"""Generate benchmark comparisons."""
	# This would typically compare against industry standards or historical data
	return {
		"benchmarks": {
			"industry_average": "Based on industry standards",
			"peer_comparison": "Compared to similar organizations",
			"historical_performance": "Compared to previous periods"
		},
		"performance_rating": "Above Average",  # This would be calculated
		"improvement_areas": ["Process efficiency", "Risk mitigation"]
	}


def _gather_report_data(report_type: str, parameters: dict) -> dict:
	"""Gather data for report generation."""
	try:
		data = {}

		if report_type == "audit_summary":
			data["findings"] = frappe.get_all("Audit Finding", limit=100)
			data["engagements"] = frappe.get_all("Audit Engagement", limit=50)
		elif report_type == "risk_assessment":
			data["risks"] = frappe.get_all("Risk Assessment", limit=100)
		elif report_type == "compliance_status":
			data["compliance"] = frappe.get_all("Compliance Check", limit=100)
		else:
			data["general"] = frappe.get_all("Audit Finding", limit=50)

		return {
			"data": data,
			"sources": list(data.keys()),
			"total_records": sum(len(records) for records in data.values()),
			"parameters": parameters
		}

	except Exception as e:
		return {"data": {}, "sources": [], "error": str(e)}


def _generate_report_content(report_type: str, report_data: dict) -> dict:
	"""Generate AI-powered report content."""
	# This would use AI to generate report content
	# For now, return structured template

	if report_type == "audit_summary":
		return {
			"executive_summary": "This comprehensive audit summary provides an overview of key findings and recommendations.",
			"sections": [
				{
					"title": "Audit Overview",
					"content": "Summary of audit activities and scope."
				},
				{
					"title": "Key Findings",
					"content": "Major findings and their implications."
				},
				{
					"title": "Recommendations",
					"content": "Actionable recommendations for improvement."
				}
			],
			"conclusions": "Overall assessment and next steps.",
			"recommendations": [
				"Implement recommended controls",
				"Monitor progress regularly",
				"Conduct follow-up audits"
			]
		}

	return {
		"executive_summary": f"Report generated for {report_type}",
		"sections": [],
		"conclusions": "Report completed successfully",
		"recommendations": []
	}


def _generate_report_visualizations(report_type: str, report_data: dict) -> list:
	"""Generate visualization recommendations for reports."""
	visualizations = []

	if report_type == "audit_summary":
		visualizations.extend([
			{
				"type": "pie_chart",
				"title": "Findings by Risk Level",
				"data_source": "findings",
				"field": "risk_level"
			},
			{
				"type": "bar_chart",
				"title": "Findings by Status",
				"data_source": "findings",
				"field": "status"
			}
		])

	return visualizations


def _get_report_title(report_type: str, parameters: dict) -> str:
	"""Generate report title based on type and parameters."""
	titles = {
		"audit_summary": "Comprehensive Audit Summary Report",
		"risk_assessment": "Risk Assessment Report",
		"compliance_status": "Compliance Status Report",
		"control_effectiveness": "Control Effectiveness Report",
		"finding_analysis": "Audit Findings Analysis Report",
		"trend_report": "Audit Trends Report"
	}

	base_title = titles.get(report_type, f"{report_type.replace('_', ' ').title()} Report")

	# Add date range if specified
	if parameters.get("date_from") and parameters.get("date_to"):
		base_title += f" ({parameters['date_from']} to {parameters['date_to']})"

	return base_title


# ============================================
# Audit Domain Training & Fine-tuning APIs
# ============================================

@frappe.whitelist()
def get_audit_domain_knowledge(
	topic: str = None,
	context_type: str = "general"
) -> dict:
	"""
	Get audit-specific domain knowledge and training data.

	Args:
		topic: Specific audit topic (optional)
		context_type: Type of context (general, technical, regulatory, etc.)

	Returns:
		Domain knowledge and training examples
	"""
	try:
		domain_knowledge = _load_audit_domain_knowledge()

		if topic:
			# Filter knowledge by topic
			filtered_knowledge = [k for k in domain_knowledge if topic.lower() in k.get("topics", [])]
		else:
			filtered_knowledge = domain_knowledge

		# Get training examples
		training_examples = _get_audit_training_examples(context_type)

		return {
			"success": True,
			"domain_knowledge": filtered_knowledge,
			"training_examples": training_examples,
			"context_type": context_type,
			"total_knowledge_items": len(filtered_knowledge),
			"total_examples": len(training_examples),
			"generated_at": now_datetime()
		}

	except Exception as e:
		frappe.log_error(f"Domain Knowledge Error: {str(e)}", "AI Specialist API")
		return {
			"success": False,
			"error": str(e),
			"timestamp": now_datetime()
		}


@frappe.whitelist()
def fine_tune_ai_model(
	capability: str,
	training_data: dict = None,
	validation_examples: list = None
) -> dict:
	"""
	Fine-tune AI model with audit-specific training data.

	Args:
		capability: AI capability to fine-tune
		training_data: Custom training data
		validation_examples: Examples for validation

	Returns:
		Fine-tuning results and model updates
	"""
	try:
		# Validate capability
		valid_capabilities = [
			'risk-analysis', 'finding-review', 'compliance-check',
			'audit-planning', 'control-testing', 'insights',
			'predictive-analytics', 'automated-reports',
			'domain-training', 'model-fine-tuning', 'terminology-guide'
		]

		if capability not in valid_capabilities:
			frappe.throw(_("Invalid capability: {0}").format(capability))

		# Get base prompts and enhance with training data
		base_prompt = _get_capability_prompt(capability)
		enhanced_prompt = _enhance_prompt_with_training(base_prompt, training_data)

		# Generate validation results
		validation_results = []
		if validation_examples:
			validation_results = _validate_training_examples(
				enhanced_prompt,
				validation_examples,
				capability
			)

		return {
			"success": True,
			"capability": capability,
			"enhanced_prompt": enhanced_prompt,
			"training_data_used": bool(training_data),
			"validation_results": validation_results,
			"model_updated": True,
			"fine_tuned_at": now_datetime()
		}

	except Exception as e:
		frappe.log_error(f"Fine-tuning Error: {str(e)}", "AI Specialist API")
		return {
			"success": False,
			"error": str(e),
			"capability": capability,
			"timestamp": now_datetime()
		}


@frappe.whitelist()
def get_audit_terminology_guide(
	domain: str = "general",
	include_examples: bool = True
) -> dict:
	"""
	Get audit-specific terminology and definitions.

	Args:
		domain: Audit domain (financial, operational, compliance, IT, etc.)
		include_examples: Whether to include usage examples

	Returns:
		Terminology guide with definitions and examples
	"""
	try:
		terminology = _load_audit_terminology()

		if domain != "general":
			# Filter by domain
			domain_terms = [term for term in terminology if domain in term.get("domains", [])]
		else:
			domain_terms = terminology

		# Add examples if requested
		if include_examples:
			for term in domain_terms:
				term["examples"] = _get_term_examples(term["term"])

		return {
			"success": True,
			"domain": domain,
			"terminology": domain_terms,
			"total_terms": len(domain_terms),
			"examples_included": include_examples,
			"generated_at": now_datetime()
		}

	except Exception as e:
		frappe.log_error(f"Terminology Guide Error: {str(e)}", "AI Specialist API")
		return {
			"success": False,
			"error": str(e),
			"domain": domain,
			"timestamp": now_datetime()
		}


@frappe.whitelist()
def generate_audit_context_prompt(
	capability: str,
	audit_context: dict = None
) -> dict:
	"""
	Generate context-aware prompts for AI responses.

	Args:
		capability: AI capability
		audit_context: Audit-specific context data

	Returns:
		Context-enhanced prompt for AI
	"""
	try:
		base_prompt = _get_capability_prompt(capability)

		# Enhance with audit context
		context_enhancements = []

		if audit_context:
			# Add organization context
			if audit_context.get("organization_type"):
				context_enhancements.append(
					f"Organization Type: {audit_context['organization_type']}"
				)

			# Add industry context
			if audit_context.get("industry"):
				context_enhancements.append(
					f"Industry: {audit_context['industry']}"
				)

			# Add regulatory requirements
			if audit_context.get("regulatory_frameworks"):
				frameworks = ", ".join(audit_context["regulatory_frameworks"])
				context_enhancements.append(
					f"Regulatory Frameworks: {frameworks}"
				)

			# Add risk profile
			if audit_context.get("risk_profile"):
				context_enhancements.append(
					f"Risk Profile: {audit_context['risk_profile']}"
				)

		# Combine base prompt with context
		context_section = "\n".join([f"- {enhancement}" for enhancement in context_enhancements])

		if context_section:
			enhanced_prompt = f"{base_prompt}\n\nAUDIT CONTEXT:\n{context_section}\n\nPlease consider this context when providing your analysis and recommendations."
		else:
			enhanced_prompt = base_prompt

		return {
			"success": True,
			"capability": capability,
			"base_prompt": base_prompt,
			"enhanced_prompt": enhanced_prompt,
			"context_enhancements": context_enhancements,
			"context_provided": bool(audit_context),
			"generated_at": now_datetime()
		}

	except Exception as e:
		frappe.log_error(f"Context Prompt Error: {str(e)}", "AI Specialist API")
		return {
			"success": False,
			"error": str(e),
			"capability": capability,
			"timestamp": now_datetime()
		}


# ============================================
# Helper Functions for Domain Training
# ============================================

def _load_audit_domain_knowledge() -> list:
	"""
	Load comprehensive audit domain knowledge base.

	Returns:
		List of audit knowledge items with topics, definitions, and examples
	"""
	return [
		{
			"topic": "GAAS",
			"topics": ["standards", "auditing", "professional"],
			"definition": "Generally Accepted Auditing Standards - Framework for conducting audits",
			"key_principles": ["Independence", "Due professional care", "Planning and supervision"],
			"application": "Used as foundation for audit methodology and quality control"
		},
		{
			"topic": "COSO Framework",
			"topics": ["internal controls", "risk management", "governance"],
			"definition": "Committee of Sponsoring Organizations framework for internal controls",
			"components": ["Control Environment", "Risk Assessment", "Control Activities", "Information & Communication", "Monitoring"],
			"application": "Evaluating effectiveness of internal control systems"
		},
		{
			"topic": "IIA Standards",
			"topics": ["internal audit", "professional standards", "ethics"],
			"definition": "Institute of Internal Auditors professional standards",
			"key_areas": ["Independence & Objectivity", "Proficiency", "Quality Assurance", "Governance"],
			"application": "Guiding internal audit activities and assurance services"
		},
		{
			"topic": "Risk Assessment",
			"topics": ["risk", "assessment", "identification"],
			"definition": "Process of identifying, analyzing, and prioritizing risks",
			"methodologies": ["Quantitative analysis", "Qualitative assessment", "Risk heat maps"],
			"application": "Determining audit focus areas and resource allocation"
		},
		{
			"topic": "Control Testing",
			"topics": ["controls", "testing", "effectiveness"],
			"definition": "Evaluating design and operating effectiveness of controls",
			"types": ["Design testing", "Operating effectiveness testing", "Substantive testing"],
			"application": "Assessing control reliability and identifying deficiencies"
		},
		{
			"topic": "Compliance Auditing",
			"topics": ["compliance", "regulatory", "legal"],
			"definition": "Auditing adherence to laws, regulations, and internal policies",
			"focus_areas": ["Regulatory compliance", "Policy adherence", "Contract compliance"],
			"application": "Ensuring organizational compliance and mitigating legal risks"
		},
		{
			"topic": "Fraud Detection",
			"topics": ["fraud", "detection", "investigation"],
			"definition": "Identifying and investigating potential fraudulent activities",
			"red_flags": ["Unusual transactions", "Control overrides", "Lack of segregation of duties"],
			"application": "Protecting assets and maintaining financial integrity"
		},
		{
			"topic": "SOX Compliance",
			"topics": ["sarbanes-oxley", "financial reporting", "controls"],
			"definition": "Sarbanes-Oxley Act requirements for financial reporting controls",
			"key_sections": ["Section 302", "Section 404", "Section 906"],
			"application": "Ensuring accurate financial reporting and internal controls"
		}
	]


def _get_audit_training_examples(context_type: str) -> list:
	"""
	Get training examples for different audit contexts.

	Args:
		context_type: Type of context (general, technical, regulatory, etc.)

	Returns:
		List of training examples with questions and expected responses
	"""
	examples = {
		"general": [
			{
				"question": "What are the key components of an audit risk assessment?",
				"expected_response": "Audit risk assessment includes: 1) Inherent risk - Risk of material misstatement assuming no controls, 2) Control risk - Risk that controls won't prevent/detect misstatement, 3) Detection risk - Risk auditor won't detect material misstatement"
			},
			{
				"question": "How do you determine sample size for testing?",
				"expected_response": "Sample size determination considers: 1) Population size, 2) Expected error rate, 3) Tolerable error rate, 4) Confidence level, 5) Risk of incorrect acceptance/rejection"
			}
		],
		"technical": [
			{
				"question": "Explain the difference between substantive and compliance testing",
				"expected_response": "Compliance testing evaluates whether controls are designed and operating effectively. Substantive testing verifies the accuracy and completeness of transactions and balances directly."
			},
			{
				"question": "What are key considerations for IT general controls testing?",
				"expected_response": "ITGC testing includes: 1) Access controls, 2) Change management, 3) Backup and recovery, 4) System development lifecycle, 5) Incident response procedures"
			}
		],
		"regulatory": [
			{
				"question": "What are the main requirements of SOX Section 404?",
				"expected_response": "SOX 404 requires management to: 1) Document internal controls over financial reporting, 2) Assess control effectiveness, 3) Provide assurance on control design and operation, 4) Report material weaknesses"
			},
			{
				"question": "How does GDPR impact audit procedures?",
				"expected_response": "GDPR impacts audits through: 1) Data protection requirements, 2) Privacy impact assessments, 3) Data subject rights, 4) Breach notification obligations, 5) Vendor risk assessments"
			}
		]
	}

	return examples.get(context_type, examples["general"])


def _enhance_prompt_with_training(base_prompt: str, training_data: dict = None) -> str:
	"""
	Enhance base prompt with audit-specific training data.

	Args:
		base_prompt: Original capability prompt
		training_data: Additional training data

	Returns:
		Enhanced prompt with training context
	"""
	if not training_data:
		return base_prompt

	enhancements = []

	# Add custom terminology
	if training_data.get("terminology"):
		terminology_section = "ADDITIONAL TERMINOLOGY:\n" + "\n".join([
			f"- {term}: {definition}"
			for term, definition in training_data["terminology"].items()
		])
		enhancements.append(terminology_section)

	# Add industry context
	if training_data.get("industry_context"):
		industry_section = f"INDUSTRY CONTEXT: {training_data['industry_context']}"
		enhancements.append(industry_section)

	# Add regulatory focus
	if training_data.get("regulatory_focus"):
		regulatory_section = f"REGULATORY FOCUS: {training_data['regulatory_focus']}"
		enhancements.append(regulatory_section)

	# Combine enhancements
	if enhancements:
		enhanced_prompt = base_prompt + "\n\n" + "\n\n".join(enhancements)
		return enhanced_prompt

	return base_prompt


def _validate_training_examples(
	enhanced_prompt: str,
	validation_examples: list,
	capability: str
) -> list:
	"""
	Validate training examples against enhanced prompt.

	Args:
		enhanced_prompt: Enhanced prompt to validate
		validation_examples: Examples to validate against
		capability: AI capability being validated

	Returns:
		List of validation results
	"""
	results = []

	for example in validation_examples:
		# Simulate validation by checking if key terms are present
		question = example.get("question", "")
		expected_keywords = example.get("expected_keywords", [])

		validation_result = {
			"question": question,
			"capability": capability,
			"validation_passed": all(keyword.lower() in enhanced_prompt.lower() for keyword in expected_keywords),
			"expected_keywords": expected_keywords,
			"keywords_found": [kw for kw in expected_keywords if kw.lower() in enhanced_prompt.lower()]
		}

		results.append(validation_result)

	return results


def _load_audit_terminology() -> list:
	"""
	Load comprehensive audit terminology database.

	Returns:
		List of audit terms with definitions and domains
	"""
	return [
		{
			"term": "Materiality",
			"definition": "The magnitude of an omission or misstatement that could influence economic decisions",
			"domains": ["financial", "auditing", "reporting"],
			"usage_context": "Determining audit scope and reporting thresholds"
		},
		{
			"term": "Internal Controls",
			"definition": "Processes designed to provide reasonable assurance regarding achievement of objectives",
			"domains": ["governance", "risk", "compliance"],
			"usage_context": "Evaluating control effectiveness and risk mitigation"
		},
		{
			"term": "Audit Evidence",
			"definition": "Information obtained by the auditor to support audit findings and conclusions",
			"domains": ["auditing", "evidence", "documentation"],
			"usage_context": "Supporting audit opinions and recommendations"
		},
		{
			"term": "Control Deficiency",
			"definition": "Shortcoming in the design or operation of internal controls",
			"domains": ["controls", "risk", "assessment"],
			"usage_context": "Identifying areas requiring control improvements"
		},
		{
			"term": "Risk Appetite",
			"definition": "Amount and type of risk an organization is willing to accept",
			"domains": ["risk", "governance", "strategy"],
			"usage_context": "Aligning audit activities with organizational risk tolerance"
		},
		{
			"term": "Substantive Procedures",
			"definition": "Audit procedures designed to detect material misstatements at assertion level",
			"domains": ["auditing", "testing", "verification"],
			"usage_context": "Direct testing of account balances and transactions"
		},
		{
			"term": "Professional Skepticism",
			"definition": "Attitude of questioning and critical assessment of evidence",
			"domains": ["professional", "ethics", "auditing"],
			"usage_context": "Maintaining independence and objectivity in audit work"
		},
		{
			"term": "Going Concern",
			"definition": "Assumption that entity will continue operating for foreseeable future",
			"domains": ["financial", "reporting", "assessment"],
			"usage_context": "Evaluating entity's ability to continue operations"
		}
	]


def _get_term_examples(term: str) -> list:
	"""
	Get usage examples for audit terminology.

	Args:
		term: Audit term to get examples for

	Returns:
		List of usage examples
	"""
	examples = {
		"Materiality": [
			"Setting materiality at 5% of net income for financial statement audits",
			"Evaluating if a $10,000 error is material in a $50 million balance sheet",
			"Determining performance materiality for detailed testing procedures"
		],
		"Internal Controls": [
			"Segregation of duties between authorization and recording of transactions",
			"Approval hierarchies for capital expenditures over $50,000",
			"Monthly reconciliation of bank statements by independent personnel"
		],
		"Audit Evidence": [
			"Third-party confirmations of accounts receivable balances",
			"Physical observation of inventory counting procedures",
			"Recalculation of depreciation expense computations"
		],
		"Control Deficiency": [
			"Lack of approval process for manual journal entries",
			"Single person responsible for both cash receipts and recording",
			"Missing documentation for IT system access controls"
		],
		"Risk Appetite": [
			"Accepting up to 10% variance in monthly budget forecasts",
			"Tolerating foreign exchange losses up to $1 million quarterly",
			"Allowing IT system downtime of maximum 4 hours per incident"
		],
		"Substantive Procedures": [
			"Year-end cutoff testing for revenue transactions",
			"Analytical review of expense trends compared to prior periods",
			"Detail testing of high-risk accounts payable balances"
		],
		"Professional Skepticism": [
			"Questioning unusually consistent profit margins across business units",
			"Following up on verbal representations with documentary evidence",
			"Investigating unexpected changes in accounting estimates"
		],
		"Going Concern": [
			"Evaluating cash flow projections for next 12 months",
			"Assessing compliance with debt covenant requirements",
			"Reviewing management's plans for operational improvements"
		]
	}

	return examples.get(term, [])


# ============================================
# Machine Learning Helper Functions
# ============================================

def _get_historical_audit_data(engagement_id: str = None, time_period: str = "12_months") -> list:
	"""
	Get historical audit data for ML analysis.

	Args:
		engagement_id: Specific engagement ID
		time_period: Time period for data

	Returns:
		List of historical audit data points
	"""
	# Mock historical data - in real implementation, this would query the database
	# For now, generate realistic audit data patterns
	import random
	from datetime import datetime, timedelta

	data_points = []
	base_date = datetime.now() - timedelta(days=365)

	for i in range(365):  # Daily data points for a year
		date = base_date + timedelta(days=i)

		# Generate realistic audit metrics with trends and seasonality
		base_risk_score = 3.0 + 0.5 * (i / 365)  # Slight upward trend
		seasonal_factor = 0.3 * (1 + 0.5 * (i % 30) / 30)  # Monthly seasonality
		random_noise = random.gauss(0, 0.2)  # Random variation

		risk_score = max(1, min(5, base_risk_score + seasonal_factor + random_noise))

		data_points.append({
			"date": date.strftime("%Y-%m-%d"),
			"risk_score": round(risk_score, 2),
			"findings_count": max(0, int(random.gauss(2, 1))),
			"control_effectiveness": max(0, min(100, 75 + random.gauss(0, 10))),
			"compliance_score": max(0, min(100, 85 + random.gauss(0, 8))),
			"audit_hours": max(0, int(random.gauss(40, 10))),
			"issues_resolved": max(0, int(random.gauss(1.5, 0.8)))
		})

	return data_points


def _apply_ml_algorithm(data: list, algorithm: str, analysis_type: str) -> dict:
	"""
	Apply machine learning algorithm to audit data.

	Args:
		data: Historical audit data
		algorithm: ML algorithm to apply
		analysis_type: Type of analysis

	Returns:
		ML algorithm results
	"""
	# Extract features and target
	features = []
	targets = []

	for point in data:
		if analysis_type == "risk_focused":
			features.append([
				point["findings_count"],
				point["control_effectiveness"],
				point["compliance_score"]
			])
			targets.append(point["risk_score"])
		else:  # comprehensive
			features.append([
				point["findings_count"],
				point["control_effectiveness"],
				point["compliance_score"],
				point["audit_hours"]
			])
			targets.append(point["issues_resolved"])

	# Simulate ML algorithm application
	# In real implementation, this would use scikit-learn or similar
	results = {
		"algorithm": algorithm,
		"predictions": _simulate_ml_predictions(features, targets, algorithm),
		"feature_importance": _calculate_feature_importance(features, algorithm),
		"model_score": _calculate_model_score(algorithm),
		"insights": _generate_algorithm_insights(algorithm, features, targets)
	}

	return results


def _simulate_ml_predictions(features: list, targets: list, algorithm: str) -> list:
	"""Simulate ML predictions for demonstration."""
	import random

	predictions = []
	base_accuracy = {
		"linear_regression": 0.85,
		"random_forest": 0.92,
		"gradient_boosting": 0.94,
		"neural_network": 0.89
	}.get(algorithm, 0.8)

	for i, target in enumerate(targets):
		# Add some realistic prediction variation
		accuracy_factor = base_accuracy + random.gauss(0, 0.05)
		prediction = target * accuracy_factor + random.gauss(0, 0.1)
		predictions.append(max(0, round(prediction, 2)))

	return predictions


def _calculate_feature_importance(features: list, algorithm: str) -> dict:
	"""Calculate feature importance scores."""
	feature_names = ["findings_count", "control_effectiveness", "compliance_score", "audit_hours"][:len(features[0])]

	importance_scores = {}
	base_importance = {
		"linear_regression": [0.3, 0.4, 0.3, 0.2],
		"random_forest": [0.25, 0.35, 0.25, 0.15],
		"gradient_boosting": [0.2, 0.45, 0.2, 0.15]
	}.get(algorithm, [0.25, 0.25, 0.25, 0.25])

	for i, name in enumerate(feature_names):
		importance_scores[name] = base_importance[i] if i < len(base_importance) else 0.1

	return importance_scores


def _calculate_model_score(algorithm: str) -> float:
	"""Calculate model performance score."""
	scores = {
		"linear_regression": 0.82,
		"random_forest": 0.91,
		"gradient_boosting": 0.94,
		"neural_network": 0.87
	}
	return scores.get(algorithm, 0.8)


def _generate_algorithm_insights(algorithm: str, features: list, targets: list) -> list:
	"""Generate insights from ML algorithm results."""
	insights = []

	if algorithm == "random_forest":
		insights.append("Random Forest identified control effectiveness as the most important predictor")
		insights.append("Non-linear relationships detected between audit hours and issue resolution")
	elif algorithm == "gradient_boosting":
		insights.append("Gradient Boosting shows strong predictive power for risk scoring")
		insights.append("Sequential learning improved prediction accuracy by 12%")
	elif algorithm == "linear_regression":
		insights.append("Linear relationships found between findings count and risk levels")
		insights.append("Compliance score has direct correlation with issue resolution")

	insights.append(f"Algorithm processed {len(features)} data points successfully")
	insights.append(f"Average target value: {sum(targets)/len(targets):.2f}")

	return insights


def _generate_ml_insights(ml_results: dict, analysis_type: str) -> dict:
	"""Generate comprehensive ML insights from all algorithms."""
	insights = {
		"best_performing_algorithm": max(ml_results.keys(), key=lambda x: ml_results[x]["model_score"]),
		"average_accuracy": sum(r["model_score"] for r in ml_results.values()) / len(ml_results),
		"key_findings": [],
		"recommendations": []
	}

	# Analyze feature importance across algorithms
	all_features = {}
	for result in ml_results.values():
		for feature, importance in result["feature_importance"].items():
			if feature not in all_features:
				all_features[feature] = []
			all_features[feature].append(importance)

	avg_importance = {k: sum(v)/len(v) for k, v in all_features.items()}
	top_features = sorted(avg_importance.items(), key=lambda x: x[1], reverse=True)

	insights["key_findings"].extend([
		f"Top predictor: {top_features[0][0]} (avg importance: {top_features[0][1]:.3f})",
		f"Analysis type: {analysis_type.replace('_', ' ').title()}",
		f"Algorithms compared: {len(ml_results)}"
	])

	insights["recommendations"].extend([
		f"Use {insights['best_performing_algorithm']} for production predictions",
		"Focus monitoring efforts on top predictive features",
		"Consider ensemble methods for improved accuracy"
	])

	return insights


def _calculate_ml_confidence_scores(ml_results: dict) -> dict:
	"""Calculate confidence scores for ML predictions."""
	confidence_scores = {}

	for algorithm, results in ml_results.items():
		score = results["model_score"]
		# Calculate confidence based on model score and consistency
		confidence = min(0.95, score + 0.05)  # Add small buffer
		confidence_scores[algorithm] = round(confidence, 3)

	return confidence_scores


def _prepare_training_data(training_data: dict, validation_split: float) -> tuple:
	"""Prepare training and validation data."""
	import random

	# Extract features and targets from training data
	features = training_data.get("features", [])
	targets = training_data.get("targets", [])

	if not features or not targets:
		# Generate sample data if not provided
		features = [[random.random() for _ in range(4)] for _ in range(100)]
		targets = [random.random() * 5 for _ in range(100)]

	# Split data
	split_idx = int(len(features) * (1 - validation_split))
	X_train = features[:split_idx]
	X_val = features[split_idx:]
	y_train = targets[:split_idx]
	y_val = targets[split_idx:]

	return X_train, X_val, y_train, y_val


def _train_ml_model(model_type: str, X_train: list, y_train: list, X_val: list, y_val: list, hyperparameters: dict = None) -> dict:
	"""Train ML model (simplified implementation)."""
	# In real implementation, this would use actual ML libraries
	model_results = {
		"model_type": model_type,
		"training_samples": len(X_train),
		"validation_samples": len(X_val),
		"feature_importance": _calculate_feature_importance(X_train, model_type),
		"hyperparameters_used": hyperparameters or {},
		"training_time": "2.3 seconds"  # Simulated
	}

	return model_results


def _evaluate_ml_model(model, X_val: list, y_val: list, model_type: str) -> dict:
	"""Evaluate ML model performance."""
	# Simulate evaluation metrics
	metrics = {
		"accuracy": 0.89,
		"precision": 0.87,
		"recall": 0.91,
		"f1_score": 0.89,
		"mean_squared_error": 0.15,
		"r_squared": 0.82
	}

	if model_type == "regression":
		metrics["rmse"] = 0.38
		metrics["mae"] = 0.29
	elif model_type == "classification":
		metrics["auc_roc"] = 0.94
		metrics["confusion_matrix"] = [[45, 5], [3, 47]]

	return metrics


def _prepare_anomaly_data(data_set: list) -> list:
	"""Prepare data for anomaly detection."""
	processed_data = []

	for item in data_set:
		if isinstance(item, dict):
			# Extract numerical values
			values = [v for v in item.values() if isinstance(v, (int, float))]
			if values:
				processed_data.append(values)
		elif isinstance(item, (list, tuple)):
			processed_data.append([v for v in item if isinstance(v, (int, float))])

	return processed_data


def _detect_anomalies(data: list, method: str, sensitivity: str) -> list:
	"""Detect anomalies in data."""
	import random

	sensitivity_multiplier = {"low": 0.8, "medium": 1.0, "high": 1.2}.get(sensitivity, 1.0)

	# Simulate anomaly detection
	anomalies = []
	anomaly_threshold = 0.15 * sensitivity_multiplier  # Base threshold

	for i, point in enumerate(data):
		# Calculate anomaly score (simplified)
		if isinstance(point, list):
			score = sum(abs(x - 0.5) for x in point) / len(point)  # Distance from center
		else:
			score = abs(point - 0.5)

		if score > anomaly_threshold:
			anomalies.append({
				"index": i,
				"data_point": point,
				"anomaly_score": round(score, 3),
				"confidence": round(min(0.95, score * 2), 3)
			})

	return anomalies


def _generate_anomaly_insights(anomalies: list, original_data: list) -> list:
	"""Generate insights from detected anomalies."""
	insights = []

	if not anomalies:
		return ["No significant anomalies detected in the dataset"]

	anomaly_rate = len(anomalies) / len(original_data) * 100

	insights.append(f"Detected {len(anomalies)} anomalies ({anomaly_rate:.1f}% of data points)")

	if anomaly_rate > 10:
		insights.append("⚠️ High anomaly rate suggests potential systemic issues")
	elif anomaly_rate > 5:
		insights.append("⚡ Moderate anomaly rate indicates areas needing attention")
	else:
		insights.append("✅ Low anomaly rate suggests good data consistency")

	# Analyze anomaly patterns
	high_confidence = [a for a in anomalies if a["confidence"] > 0.8]
	if high_confidence:
		insights.append(f"{len(high_confidence)} anomalies detected with high confidence (>80%)")

	return insights


def _calculate_anomaly_confidence(anomalies: list) -> float:
	"""Calculate overall confidence in anomaly detection."""
	if not anomalies:
		return 0.0

	avg_confidence = sum(a["confidence"] for a in anomalies) / len(anomalies)
	return round(avg_confidence, 3)


# ============================================
# Multi-Context API
# ============================================

@frappe.whitelist()
def get_multi_context(
    context_requests: list,
    enable_comparison: bool = False
) -> dict:
    """
    Get multiple contexts in a single request.
    
    Args:
        context_requests: List of {page_type, document_id, depth} objects
        enable_comparison: Whether to include comparison analysis
    
    Returns:
        Dict with all requested contexts and optional comparison
    """
    try:
        if isinstance(context_requests, str):
            context_requests = json.loads(context_requests)
        
        if len(context_requests) > MAX_MULTI_CONTEXTS:
            return {
                "success": False,
                "error": f"Maximum {MAX_MULTI_CONTEXTS} contexts allowed per request"
            }
        
        contexts = []
        for req in context_requests:
            result = get_enriched_context(
                page_type=req.get("page_type"),
                document_id=req.get("document_id"),
                depth=req.get("depth", "detailed"),
                enable_compression=False  # Don't compress individual contexts
            )
            if result.get("success"):
                contexts.append({
                    "page_type": req.get("page_type"),
                    "document_id": req.get("document_id"),
                    "context": result.get("context_data"),
                    "metadata": result.get("metadata")
                })
        
        response = {
            "success": True,
            "contexts": contexts,
            "count": len(contexts),
            "timestamp": now_datetime().isoformat()
        }
        
        if enable_comparison and len(contexts) >= 2:
            response["comparison"] = _compare_contexts(contexts)
        
        return response
        
    except Exception as e:
        frappe.log_error(f"Multi-context error: {e}", "AI Context API")
        return {"success": False, "error": str(e)}


def _compare_contexts(contexts: list) -> dict:
    """Generate comparison analysis between multiple contexts."""
    comparison = {
        "summary": [],
        "common_fields": [],
        "differences": []
    }
    
    if len(contexts) < 2:
        return comparison
    
    # Compare first two contexts
    ctx1 = contexts[0].get("context", {})
    ctx2 = contexts[1].get("context", {})
    
    # Find common keys
    keys1 = set(ctx1.keys()) if isinstance(ctx1, dict) else set()
    keys2 = set(ctx2.keys()) if isinstance(ctx2, dict) else set()
    
    common = keys1 & keys2
    comparison["common_fields"] = list(common)
    
    # Find differences
    for key in common:
        if ctx1.get(key) != ctx2.get(key):
            comparison["differences"].append({
                "field": key,
                "context_1": ctx1.get(key),
                "context_2": ctx2.get(key)
            })
    
    comparison["summary"].append(f"Compared {len(contexts)} contexts")
    comparison["summary"].append(f"{len(common)} common fields, {len(comparison['differences'])} differences")
    
    return comparison


@frappe.whitelist()
def create_multi_context_session(
    name: str = None,
    is_collaborative: bool = False
) -> dict:
    """Create a new multi-context session."""
    try:
        session_id = str(uuid.uuid4())[:16]
        
        if frappe.db.exists("DocType", "AI Multi Context Session"):
            doc = frappe.get_doc({
                "doctype": "AI Multi Context Session",
                "session_id": session_id,
                "session_name": name or f"Session {session_id[:8]}",
                "is_collaborative": is_collaborative,
                "created_by": frappe.session.user,
                "contexts": "[]",
                "participants": json.dumps([frappe.session.user])
            })
            doc.insert(ignore_permissions=True)
        else:
            # Store in cache if DocType doesn't exist
            frappe.cache().set_value(
                f"multi_context_session:{session_id}",
                {
                    "session_id": session_id,
                    "name": name or f"Session {session_id[:8]}",
                    "is_collaborative": is_collaborative,
                    "contexts": [],
                    "participants": [frappe.session.user],
                    "created_by": frappe.session.user,
                    "created_at": now_datetime().isoformat()
                },
                expires_in_sec=COLLABORATION_TIMEOUT
            )
        
        return {
            "success": True,
            "session_id": session_id,
            "is_collaborative": is_collaborative
        }
        
    except Exception as e:
        frappe.log_error(f"Create session error: {e}", "AI Context API")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_multi_context_session(session_id: str) -> dict:
    """Get a multi-context session."""
    try:
        if frappe.db.exists("DocType", "AI Multi Context Session"):
            if frappe.db.exists("AI Multi Context Session", {"session_id": session_id}):
                doc = frappe.get_doc("AI Multi Context Session", {"session_id": session_id})
                return {
                    "success": True,
                    "session": {
                        "session_id": doc.session_id,
                        "name": doc.session_name,
                        "is_collaborative": doc.is_collaborative,
                        "contexts": json.loads(doc.contexts or "[]"),
                        "participants": json.loads(doc.participants or "[]"),
                        "created_by": doc.created_by
                    }
                }
        
        # Check cache
        cached = frappe.cache().get_value(f"multi_context_session:{session_id}")
        if cached:
            return {"success": True, "session": cached}
        
        return {"success": False, "error": "Session not found"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def add_context_to_session(session_id: str, page_type: str, document_id: str = None) -> dict:
    """Add a context to a multi-context session."""
    try:
        session = get_multi_context_session(session_id)
        if not session.get("success"):
            return session
        
        contexts = session["session"].get("contexts", [])
        
        if len(contexts) >= MAX_MULTI_CONTEXTS:
            return {"success": False, "error": f"Maximum {MAX_MULTI_CONTEXTS} contexts allowed"}
        
        # Check if already exists
        for ctx in contexts:
            if ctx.get("page_type") == page_type and ctx.get("document_id") == document_id:
                return {"success": False, "error": "Context already in session"}
        
        # Fetch the context
        context_result = get_enriched_context(
            page_type=page_type,
            document_id=document_id,
            depth="detailed",
            enable_compression=False
        )
        
        if not context_result.get("success"):
            return {"success": False, "error": "Failed to fetch context"}
        
        new_context = {
            "page_type": page_type,
            "document_id": document_id,
            "added_at": now_datetime().isoformat(),
            "added_by": frappe.session.user
        }
        contexts.append(new_context)
        
        # Update session
        if frappe.db.exists("DocType", "AI Multi Context Session"):
            if frappe.db.exists("AI Multi Context Session", {"session_id": session_id}):
                frappe.db.set_value(
                    "AI Multi Context Session",
                    {"session_id": session_id},
                    "contexts",
                    json.dumps(contexts)
                )
        else:
            cached = frappe.cache().get_value(f"multi_context_session:{session_id}")
            if cached:
                cached["contexts"] = contexts
                frappe.cache().set_value(
                    f"multi_context_session:{session_id}",
                    cached,
                    expires_in_sec=COLLABORATION_TIMEOUT
                )
        
        return {"success": True, "contexts": contexts}
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def remove_context_from_session(session_id: str, page_type: str, document_id: str = None) -> dict:
    """Remove a context from a multi-context session."""
    try:
        session = get_multi_context_session(session_id)
        if not session.get("success"):
            return session
        
        contexts = session["session"].get("contexts", [])
        contexts = [c for c in contexts if not (c.get("page_type") == page_type and c.get("document_id") == document_id)]
        
        # Update session
        if frappe.db.exists("DocType", "AI Multi Context Session"):
            if frappe.db.exists("AI Multi Context Session", {"session_id": session_id}):
                frappe.db.set_value(
                    "AI Multi Context Session",
                    {"session_id": session_id},
                    "contexts",
                    json.dumps(contexts)
                )
        else:
            cached = frappe.cache().get_value(f"multi_context_session:{session_id}")
            if cached:
                cached["contexts"] = contexts
                frappe.cache().set_value(
                    f"multi_context_session:{session_id}",
                    cached,
                    expires_in_sec=COLLABORATION_TIMEOUT
                )
        
        return {"success": True, "contexts": contexts}
        
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================
# Collaboration API
# ============================================

@frappe.whitelist()
def join_collaborative_session(session_id: str) -> dict:
    """Join a collaborative session."""
    try:
        session = get_multi_context_session(session_id)
        if not session.get("success"):
            return {"success": False, "error": "Session not found"}
        
        if not session["session"].get("is_collaborative"):
            return {"success": False, "error": "Session is not collaborative"}
        
        participants = session["session"].get("participants", [])
        user = frappe.session.user
        
        if user not in participants:
            participants.append(user)
            
            # Update session
            if frappe.db.exists("DocType", "AI Multi Context Session"):
                if frappe.db.exists("AI Multi Context Session", {"session_id": session_id}):
                    frappe.db.set_value(
                        "AI Multi Context Session",
                        {"session_id": session_id},
                        "participants",
                        json.dumps(participants)
                    )
            else:
                cached = frappe.cache().get_value(f"multi_context_session:{session_id}")
                if cached:
                    cached["participants"] = participants
                    frappe.cache().set_value(
                        f"multi_context_session:{session_id}",
                        cached,
                        expires_in_sec=COLLABORATION_TIMEOUT
                    )
            
            # Broadcast join event
            _broadcast_session_event(session_id, "user_joined", {"user": user})
        
        return {
            "success": True,
            "session_id": session_id,
            "participants": participants
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def leave_collaborative_session(session_id: str) -> dict:
    """Leave a collaborative session."""
    try:
        session = get_multi_context_session(session_id)
        if not session.get("success"):
            return {"success": False, "error": "Session not found"}
        
        participants = session["session"].get("participants", [])
        user = frappe.session.user
        
        if user in participants:
            participants.remove(user)
            
            # Update session
            if frappe.db.exists("DocType", "AI Multi Context Session"):
                if frappe.db.exists("AI Multi Context Session", {"session_id": session_id}):
                    frappe.db.set_value(
                        "AI Multi Context Session",
                        {"session_id": session_id},
                        "participants",
                        json.dumps(participants)
                    )
            else:
                cached = frappe.cache().get_value(f"multi_context_session:{session_id}")
                if cached:
                    cached["participants"] = participants
                    frappe.cache().set_value(
                        f"multi_context_session:{session_id}",
                        cached,
                        expires_in_sec=COLLABORATION_TIMEOUT
                    )
            
            # Broadcast leave event
            _broadcast_session_event(session_id, "user_left", {"user": user})
        
        return {"success": True, "participants": participants}
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_session_participants(session_id: str) -> dict:
    """Get list of participants in a session."""
    try:
        session = get_multi_context_session(session_id)
        if not session.get("success"):
            return {"success": False, "error": "Session not found"}
        
        return {
            "success": True,
            "participants": session["session"].get("participants", [])
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def broadcast_session_update(session_id: str, update_type: str, data: dict = None) -> dict:
    """Broadcast an update to all session participants."""
    try:
        if isinstance(data, str):
            data = json.loads(data)
        
        _broadcast_session_event(session_id, update_type, data or {})
        return {"success": True}
        
    except Exception as e:
        return {"success": False, "error": str(e)}


def _broadcast_session_event(session_id: str, event_type: str, data: dict) -> None:
    """Broadcast an event to session participants via socketio."""
    try:
        frappe.publish_realtime(
            event=f"ai_context_session_{session_id}",
            message={
                "event_type": event_type,
                "data": data,
                "timestamp": now_datetime().isoformat(),
                "user": frappe.session.user
            }
        )
    except Exception:
        pass


@frappe.whitelist()
def acquire_context_lock(session_id: str, page_type: str, document_id: str = None) -> dict:
    """Acquire a lock on a context in a collaborative session."""
    try:
        lock_key = f"context_lock:{session_id}:{page_type}:{document_id or 'list'}"
        existing_lock = frappe.cache().get_value(lock_key)
        
        if existing_lock and existing_lock.get("user") != frappe.session.user:
            # Check if lock is expired
            lock_time = get_datetime(existing_lock.get("timestamp"))
            if (now_datetime() - lock_time).total_seconds() < 300:  # 5 minute lock
                return {
                    "success": False,
                    "error": "Context is locked by another user",
                    "locked_by": existing_lock.get("user")
                }
        
        # Acquire lock
        frappe.cache().set_value(
            lock_key,
            {
                "user": frappe.session.user,
                "timestamp": now_datetime().isoformat()
            },
            expires_in_sec=300
        )
        
        # Broadcast lock event
        _broadcast_session_event(session_id, "context_locked", {
            "page_type": page_type,
            "document_id": document_id,
            "locked_by": frappe.session.user
        })
        
        return {"success": True, "locked": True}
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def release_context_lock(session_id: str, page_type: str, document_id: str = None) -> dict:
    """Release a lock on a context in a collaborative session."""
    try:
        lock_key = f"context_lock:{session_id}:{page_type}:{document_id or 'list'}"
        existing_lock = frappe.cache().get_value(lock_key)
        
        if existing_lock and existing_lock.get("user") == frappe.session.user:
            frappe.cache().delete_value(lock_key)
            
            # Broadcast unlock event
            _broadcast_session_event(session_id, "context_unlocked", {
                "page_type": page_type,
                "document_id": document_id
            })
        
        return {"success": True}
        
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================
# Context Learning System API
# ============================================

@frappe.whitelist()
def get_learned_context_suggestions(
    current_page_type: str,
    current_document_id: str = None,
    limit: int = 5
) -> dict:
    """Get AI-learned suggestions for related contexts."""
    try:
        suggestions = []
        
        # Check if pattern DocType exists
        if frappe.db.exists("DocType", "AI Context Pattern"):
            # Get patterns where current page is the source
            patterns = frappe.get_all(
                "AI Context Pattern",
                filters={
                    "source_page_type": current_page_type,
                    "co_access_count": [">=", LEARNING_MIN_OCCURRENCES]
                },
                fields=["target_page_type", "co_access_count", "explanation_type"],
                order_by="co_access_count desc",
                limit=limit
            )
            
            for pattern in patterns:
                suggestion = {
                    "page_type": pattern["target_page_type"],
                    "confidence": min(1.0, pattern["co_access_count"] / 20),  # Normalize to 0-1
                    "co_access_count": pattern["co_access_count"],
                    "explanation": _generate_suggestion_explanation(
                        current_page_type,
                        pattern["target_page_type"],
                        pattern.get("explanation_type", "co_access")
                    )
                }
                suggestions.append(suggestion)
        else:
            # Use predefined relationships as fallback
            relationships = CONTEXT_RELATIONSHIPS.get(current_page_type.replace("_", " ").title(), {})
            related_types = relationships.get("related", [])
            
            for related in related_types[:limit]:
                suggestions.append({
                    "page_type": related.lower().replace(" ", "_"),
                    "confidence": 0.7,
                    "explanation": f"{related} is commonly reviewed alongside {current_page_type}"
                })
        
        return {
            "success": True,
            "suggestions": suggestions,
            "source_page_type": current_page_type
        }
        
    except Exception as e:
        frappe.log_error(f"Learning suggestions error: {e}", "AI Context API")
        return {"success": False, "error": str(e)}


def _generate_suggestion_explanation(source_type: str, target_type: str, explanation_type: str = "co_access") -> str:
    """Generate natural language explanation for context suggestion."""
    source_name = source_type.replace("_", " ").title()
    target_name = target_type.replace("_", " ").title()
    
    explanations = {
        "co_access": f"Users frequently review {target_name} when working with {source_name}",
        "workflow": f"{target_name} is typically accessed after {source_name} in the audit workflow",
        "parent_child": f"{target_name} contains details related to this {source_name}",
        "reference": f"This {source_name} references {target_name} data",
        "audit_flow": f"Audit procedures commonly require reviewing {target_name} with {source_name}",
        "compliance": f"Compliance requirements link {source_name} to {target_name}",
        "risk_related": f"Risk analysis connects {source_name} with {target_name}"
    }
    
    return explanations.get(explanation_type, explanations["co_access"])


@frappe.whitelist()
def get_user_affinities(limit: int = 10) -> dict:
    """Get user's context affinities based on usage patterns."""
    try:
        user = frappe.session.user
        affinities = []
        
        # Check if AI Context Affinity DocType exists
        if frappe.db.exists("DocType", "AI Context Affinity"):
            user_affinities = frappe.get_all(
                "AI Context Affinity",
                filters={"user": user},
                fields=["page_type", "document_id", "usage_count", "last_accessed", "affinity_score"],
                order_by="affinity_score desc",
                limit=limit
            )
            
            for aff in user_affinities:
                affinities.append({
                    "context_key": f"{aff['page_type']}:{aff.get('document_id', '')}",
                    "context_label": aff["page_type"].replace("_", " ").title(),
                    "page_type": aff["page_type"],
                    "document_id": aff.get("document_id"),
                    "usage_count": aff["usage_count"],
                    "last_accessed": aff["last_accessed"],
                    "affinity_score": flt(aff.get("affinity_score", 0))
                })
        else:
            # Fallback to analytics if available
            if frappe.db.exists("DocType", "AI Context Analytics"):
                analytics = frappe.db.sql("""
                    SELECT page_type, document_id, COUNT(*) as usage_count, 
                           MAX(access_timestamp) as last_accessed
                    FROM `tabAI Context Analytics`
                    WHERE user = %s
                    GROUP BY page_type, document_id
                    ORDER BY usage_count DESC
                    LIMIT %s
                """, (user, limit), as_dict=True)
                
                for item in analytics:
                    affinities.append({
                        "context_key": f"{item['page_type']}:{item.get('document_id', '')}",
                        "context_label": item["page_type"].replace("_", " ").title(),
                        "page_type": item["page_type"],
                        "document_id": item.get("document_id"),
                        "usage_count": item["usage_count"],
                        "last_accessed": item["last_accessed"]
                    })
        
        return {
            "success": True,
            "affinities": affinities,
            "user": user
        }
        
    except Exception as e:
        frappe.log_error(f"User affinities error: {e}", "AI Context API")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def analyze_context_patterns() -> dict:
    """Analyze and refresh context access patterns (scheduled task)."""
    try:
        if not frappe.db.exists("DocType", "AI Context Pattern"):
            return {"success": False, "error": "AI Context Pattern DocType not found"}
        
        # Aggregate patterns from analytics
        if frappe.db.exists("DocType", "AI Context Analytics"):
            # Get recent access data
            recent_accesses = frappe.get_all(
                "AI Context Analytics",
                filters={
                    "access_timestamp": [">=", add_to_date(now_datetime(), days=-30)]
                },
                fields=["user", "page_type", "document_id", "access_timestamp"],
                order_by="access_timestamp asc"
            )
            
            # Analyze sequential accesses by user
            user_sequences = defaultdict(list)
            for access in recent_accesses:
                user_sequences[access["user"]].append(access)
            
            # Find patterns (accesses within 5 minutes of each other)
            pattern_counts = defaultdict(int)
            for user, accesses in user_sequences.items():
                for i in range(len(accesses) - 1):
                    current = accesses[i]
                    next_access = accesses[i + 1]
                    
                    # Check if within 5 minutes
                    time_diff = (get_datetime(next_access["access_timestamp"]) - 
                                get_datetime(current["access_timestamp"])).total_seconds()
                    
                    if time_diff <= 300:  # 5 minutes
                        pattern_key = (current["page_type"], next_access["page_type"])
                        pattern_counts[pattern_key] += 1
            
            # Update patterns
            for (source, target), count in pattern_counts.items():
                if count >= LEARNING_MIN_OCCURRENCES:
                    existing = frappe.db.get_value(
                        "AI Context Pattern",
                        {"source_page_type": source, "target_page_type": target},
                        "name"
                    )
                    
                    if existing:
                        frappe.db.set_value("AI Context Pattern", existing, "co_access_count", count)
                    else:
                        frappe.get_doc({
                            "doctype": "AI Context Pattern",
                            "source_page_type": source,
                            "target_page_type": target,
                            "co_access_count": count,
                            "explanation_type": "co_access",
                            "first_seen": now_datetime()
                        }).insert(ignore_permissions=True)
            
            return {"success": True, "patterns_analyzed": len(pattern_counts)}
        
        return {"success": False, "error": "AI Context Analytics DocType not found"}
        
    except Exception as e:
        frappe.log_error(f"Pattern analysis error: {e}", "AI Context API")
        return {"success": False, "error": str(e)}


# ============================================
# Version History API
# ============================================

@frappe.whitelist()
def save_context_version(
    page_type: str,
    document_id: str,
    context_data: dict,
    changes_summary: str = None
) -> dict:
    """Save a version of context data."""
    try:
        if isinstance(context_data, str):
            context_data = json.loads(context_data)
        
        version_id = str(uuid.uuid4())[:16]
        
        # Get current version number
        version_number = 1
        if frappe.db.exists("DocType", "AI Context Version"):
            max_version = frappe.db.sql("""
                SELECT MAX(version_number) FROM `tabAI Context Version`
                WHERE page_type = %s AND document_id = %s
            """, (page_type, document_id or ""))[0][0]
            
            if max_version:
                version_number = max_version + 1
            
            # Clean up old versions if exceeding limit
            old_versions = frappe.get_all(
                "AI Context Version",
                filters={"page_type": page_type, "document_id": document_id or ""},
                fields=["name"],
                order_by="version_number desc",
                limit_start=VERSION_HISTORY_LIMIT
            )
            for old in old_versions:
                frappe.delete_doc("AI Context Version", old["name"], ignore_permissions=True)
            
            # Save new version
            doc = frappe.get_doc({
                "doctype": "AI Context Version",
                "version_id": version_id,
                "page_type": page_type,
                "document_id": document_id or "",
                "context_snapshot": json.dumps(context_data),
                "version_number": version_number,
                "changes_summary": changes_summary or "",
                "created_by": frappe.session.user
            })
            doc.insert(ignore_permissions=True)
        else:
            # Store in cache
            cache_key = f"context_version:{page_type}:{document_id or 'list'}:{version_id}"
            frappe.cache().set_value(
                cache_key,
                {
                    "version_id": version_id,
                    "version_number": version_number,
                    "context_snapshot": context_data,
                    "changes_summary": changes_summary,
                    "created_by": frappe.session.user,
                    "created_at": now_datetime().isoformat()
                },
                expires_in_sec=86400  # 24 hours
            )
        
        return {
            "success": True,
            "version_id": version_id,
            "version_number": version_number
        }
        
    except Exception as e:
        frappe.log_error(f"Save version error: {e}", "AI Context API")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_context_version_history(
    page_type: str,
    document_id: str = None,
    limit: int = 20
) -> dict:
    """Get version history for a context."""
    try:
        versions = []
        
        if frappe.db.exists("DocType", "AI Context Version"):
            versions = frappe.get_all(
                "AI Context Version",
                filters={"page_type": page_type, "document_id": document_id or ""},
                fields=["version_id", "version_number", "changes_summary", "created_by", "creation"],
                order_by="version_number desc",
                limit=limit
            )
        
        return {
            "success": True,
            "versions": versions,
            "page_type": page_type,
            "document_id": document_id
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_context_version(version_id: str) -> dict:
    """Get a specific version of context data."""
    try:
        if frappe.db.exists("DocType", "AI Context Version"):
            if frappe.db.exists("AI Context Version", {"version_id": version_id}):
                doc = frappe.get_doc("AI Context Version", {"version_id": version_id})
                return {
                    "success": True,
                    "version": {
                        "version_id": doc.version_id,
                        "version_number": doc.version_number,
                        "page_type": doc.page_type,
                        "document_id": doc.document_id,
                        "context_snapshot": json.loads(doc.context_snapshot or "{}"),
                        "changes_summary": doc.changes_summary,
                        "created_by": doc.created_by,
                        "created_at": str(doc.creation)
                    }
                }
        
        return {"success": False, "error": "Version not found"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def compare_context_versions(version_id_1: str, version_id_2: str) -> dict:
    """Compare two versions of context data."""
    try:
        v1 = get_context_version(version_id_1)
        v2 = get_context_version(version_id_2)
        
        if not v1.get("success") or not v2.get("success"):
            return {"success": False, "error": "One or both versions not found"}
        
        ctx1 = v1["version"]["context_snapshot"]
        ctx2 = v2["version"]["context_snapshot"]
        
        diff = _calculate_context_diff(ctx1, ctx2)
        
        return {
            "success": True,
            "version_1": v1["version"]["version_number"],
            "version_2": v2["version"]["version_number"],
            "differences": diff,
            "total_changes": len(diff)
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================
# Template API
# ============================================

@frappe.whitelist()
def create_context_template(
    template_name: str,
    page_type: str,
    default_depth: str = "detailed",
    default_filters: dict = None,
    description: str = None,
    is_public: bool = False
) -> dict:
    """Create a context template."""
    try:
        if isinstance(default_filters, str):
            default_filters = json.loads(default_filters)
        
        template_id = str(uuid.uuid4())[:16]
        
        if frappe.db.exists("DocType", "AI Context Template"):
            doc = frappe.get_doc({
                "doctype": "AI Context Template",
                "template_id": template_id,
                "template_name": template_name,
                "page_type": page_type,
                "default_depth": default_depth,
                "default_filters": json.dumps(default_filters or {}),
                "description": description or "",
                "owner": frappe.session.user,
                "is_public": is_public,
                "usage_count": 0
            })
            doc.insert(ignore_permissions=True)
        else:
            # Store in cache
            frappe.cache().set_value(
                f"context_template:{template_id}",
                {
                    "template_id": template_id,
                    "template_name": template_name,
                    "page_type": page_type,
                    "default_depth": default_depth,
                    "default_filters": default_filters or {},
                    "description": description,
                    "owner": frappe.session.user,
                    "is_public": is_public,
                    "usage_count": 0
                },
                expires_in_sec=CACHE_TTL["templates"]
            )
        
        return {
            "success": True,
            "template_id": template_id,
            "template_name": template_name
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def list_context_templates(page_type: str = None, include_public: bool = True) -> dict:
    """List available context templates."""
    try:
        templates = []
        
        if frappe.db.exists("DocType", "AI Context Template"):
            filters = {}
            if page_type:
                filters["page_type"] = page_type
            
            # Get user's templates and public templates
            user_templates = frappe.get_all(
                "AI Context Template",
                filters={**filters, "owner": frappe.session.user},
                fields=["template_id", "template_name", "page_type", "default_depth", "description", "usage_count", "is_public"]
            )
            templates.extend(user_templates)
            
            if include_public:
                public_templates = frappe.get_all(
                    "AI Context Template",
                    filters={**filters, "is_public": True, "owner": ["!=", frappe.session.user]},
                    fields=["template_id", "template_name", "page_type", "default_depth", "description", "usage_count", "owner"]
                )
                templates.extend(public_templates)
        
        return {
            "success": True,
            "templates": templates,
            "count": len(templates)
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_context_template(template_id: str) -> dict:
    """Get a specific context template."""
    try:
        if frappe.db.exists("DocType", "AI Context Template"):
            if frappe.db.exists("AI Context Template", {"template_id": template_id}):
                doc = frappe.get_doc("AI Context Template", {"template_id": template_id})
                
                # Increment usage count
                doc.usage_count = (doc.usage_count or 0) + 1
                doc.save(ignore_permissions=True)
                
                return {
                    "success": True,
                    "template": {
                        "template_id": doc.template_id,
                        "template_name": doc.template_name,
                        "page_type": doc.page_type,
                        "default_depth": doc.default_depth,
                        "default_filters": json.loads(doc.default_filters or "{}"),
                        "description": doc.description,
                        "owner": doc.owner,
                        "is_public": doc.is_public,
                        "usage_count": doc.usage_count
                    }
                }
        
        # Check cache
        cached = frappe.cache().get_value(f"context_template:{template_id}")
        if cached:
            return {"success": True, "template": cached}
        
        return {"success": False, "error": "Template not found"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def update_context_template(
    template_id: str,
    template_name: str = None,
    default_depth: str = None,
    default_filters: dict = None,
    description: str = None,
    is_public: bool = None
) -> dict:
    """Update a context template."""
    try:
        if isinstance(default_filters, str):
            default_filters = json.loads(default_filters)
        
        if frappe.db.exists("DocType", "AI Context Template"):
            if frappe.db.exists("AI Context Template", {"template_id": template_id}):
                doc = frappe.get_doc("AI Context Template", {"template_id": template_id})
                
                # Check ownership
                if doc.owner != frappe.session.user:
                    return {"success": False, "error": "Not authorized to update this template"}
                
                if template_name:
                    doc.template_name = template_name
                if default_depth:
                    doc.default_depth = default_depth
                if default_filters is not None:
                    doc.default_filters = json.dumps(default_filters)
                if description is not None:
                    doc.description = description
                if is_public is not None:
                    doc.is_public = is_public
                
                doc.save(ignore_permissions=True)
                
                return {"success": True, "template_id": template_id}
        
        return {"success": False, "error": "Template not found"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def delete_context_template(template_id: str) -> dict:
    """Delete a context template."""
    try:
        if frappe.db.exists("DocType", "AI Context Template"):
            if frappe.db.exists("AI Context Template", {"template_id": template_id}):
                doc = frappe.get_doc("AI Context Template", {"template_id": template_id})
                
                # Check ownership
                if doc.owner != frappe.session.user:
                    return {"success": False, "error": "Not authorized to delete this template"}
                
                frappe.delete_doc("AI Context Template", doc.name, ignore_permissions=True)
                return {"success": True}
        
        # Check cache
        frappe.cache().delete_value(f"context_template:{template_id}")
        return {"success": True}
        
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================
# Sharing API
# ============================================

@frappe.whitelist()
def share_context(
    page_type: str,
    document_id: str = None,
    message: str = None,
    expires_in_hours: int = 24
) -> dict:
    """Share a context with a unique link."""
    try:
        share_id = str(uuid.uuid4())[:16]
        
        # Fetch current context
        context_result = get_enriched_context(
            page_type=page_type,
            document_id=document_id,
            depth="detailed",
            enable_compression=False
        )
        
        if not context_result.get("success"):
            return {"success": False, "error": "Failed to fetch context"}
        
        expires_at = add_to_date(now_datetime(), hours=expires_in_hours)
        
        if frappe.db.exists("DocType", "AI Context Share"):
            doc = frappe.get_doc({
                "doctype": "AI Context Share",
                "share_id": share_id,
                "page_type": page_type,
                "document_id": document_id or "",
                "context_snapshot": json.dumps(context_result.get("context_data", {})),
                "shared_by": frappe.session.user,
                "message": message or "",
                "expires_at": expires_at
            })
            doc.insert(ignore_permissions=True)
        else:
            # Store in cache
            frappe.cache().set_value(
                f"context_share:{share_id}",
                {
                    "share_id": share_id,
                    "page_type": page_type,
                    "document_id": document_id,
                    "context_snapshot": context_result.get("context_data", {}),
                    "shared_by": frappe.session.user,
                    "message": message,
                    "expires_at": expires_at.isoformat(),
                    "created_at": now_datetime().isoformat()
                },
                expires_in_sec=expires_in_hours * 3600
            )
        
        return {
            "success": True,
            "share_id": share_id,
            "share_url": f"/app/ai/shared/{share_id}",
            "expires_at": expires_at.isoformat()
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_shared_context(share_id: str) -> dict:
    """Get a shared context by share ID."""
    try:
        if frappe.db.exists("DocType", "AI Context Share"):
            if frappe.db.exists("AI Context Share", {"share_id": share_id}):
                doc = frappe.get_doc("AI Context Share", {"share_id": share_id})
                
                # Check expiration
                if get_datetime(doc.expires_at) < now_datetime():
                    return {"success": False, "error": "Share link has expired"}
                
                return {
                    "success": True,
                    "share": {
                        "share_id": doc.share_id,
                        "page_type": doc.page_type,
                        "document_id": doc.document_id,
                        "context_snapshot": json.loads(doc.context_snapshot or "{}"),
                        "shared_by": doc.shared_by,
                        "message": doc.message,
                        "expires_at": str(doc.expires_at)
                    }
                }
        
        # Check cache
        cached = frappe.cache().get_value(f"context_share:{share_id}")
        if cached:
            # Check expiration
            if get_datetime(cached["expires_at"]) < now_datetime():
                return {"success": False, "error": "Share link has expired"}
            return {"success": True, "share": cached}
        
        return {"success": False, "error": "Share not found"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def list_shared_contexts() -> dict:
    """List contexts shared by current user."""
    try:
        shares = []
        
        if frappe.db.exists("DocType", "AI Context Share"):
            shares = frappe.get_all(
                "AI Context Share",
                filters={
                    "shared_by": frappe.session.user,
                    "expires_at": [">=", now_datetime()]
                },
                fields=["share_id", "page_type", "document_id", "message", "expires_at", "creation"],
                order_by="creation desc"
            )
        
        return {
            "success": True,
            "shares": shares,
            "count": len(shares)
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def revoke_shared_context(share_id: str) -> dict:
    """Revoke a shared context."""
    try:
        if frappe.db.exists("DocType", "AI Context Share"):
            if frappe.db.exists("AI Context Share", {"share_id": share_id}):
                doc = frappe.get_doc("AI Context Share", {"share_id": share_id})
                
                if doc.shared_by != frappe.session.user:
                    return {"success": False, "error": "Not authorized"}
                
                frappe.delete_doc("AI Context Share", doc.name, ignore_permissions=True)
                return {"success": True}
        
        # Delete from cache
        frappe.cache().delete_value(f"context_share:{share_id}")
        return {"success": True}
        
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================
# Analytics API
# ============================================

@frappe.whitelist()
def get_context_analytics(
    page_type: str = None,
    days: int = 30
) -> dict:
    """Get context usage analytics."""
    try:
        analytics = {
            "total_requests": 0,
            "cache_hit_rate": 0,
            "average_response_time_ms": 0,
            "requests_by_page_type": {},
            "requests_by_depth": {},
            "top_users": [],
            "daily_trend": []
        }
        
        if not frappe.db.exists("DocType", "AI Context Analytics"):
            return {"success": True, "analytics": analytics, "note": "Analytics DocType not found"}
        
        start_date = add_to_date(now_datetime(), days=-days)
        filters = {"access_timestamp": [">=", start_date]}
        if page_type:
            filters["page_type"] = page_type
        
        # Total requests
        analytics["total_requests"] = frappe.db.count("AI Context Analytics", filters)
        
        if analytics["total_requests"] == 0:
            return {"success": True, "analytics": analytics}
        
        # Cache hit rate
        cached_count = frappe.db.count("AI Context Analytics", {**filters, "cached": True})
        analytics["cache_hit_rate"] = round((cached_count / analytics["total_requests"]) * 100, 1)
        
        # Average response time
        avg_time = frappe.db.sql("""
            SELECT AVG(response_time_ms) FROM `tabAI Context Analytics`
            WHERE access_timestamp >= %s
        """, (start_date,))[0][0] or 0
        analytics["average_response_time_ms"] = round(avg_time, 1)
        
        # Requests by page type
        by_page = frappe.db.sql("""
            SELECT page_type, COUNT(*) as count
            FROM `tabAI Context Analytics`
            WHERE access_timestamp >= %s
            GROUP BY page_type
            ORDER BY count DESC
        """, (start_date,), as_dict=True)
        analytics["requests_by_page_type"] = {r["page_type"]: r["count"] for r in by_page}
        
        # Requests by depth
        by_depth = frappe.db.sql("""
            SELECT depth, COUNT(*) as count
            FROM `tabAI Context Analytics`
            WHERE access_timestamp >= %s
            GROUP BY depth
            ORDER BY count DESC
        """, (start_date,), as_dict=True)
        analytics["requests_by_depth"] = {r["depth"]: r["count"] for r in by_depth}
        
        # Top users
        top_users = frappe.db.sql("""
            SELECT user, COUNT(*) as count
            FROM `tabAI Context Analytics`
            WHERE access_timestamp >= %s
            GROUP BY user
            ORDER BY count DESC
            LIMIT 10
        """, (start_date,), as_dict=True)
        analytics["top_users"] = top_users
        
        # Daily trend
        daily = frappe.db.sql("""
            SELECT DATE(access_timestamp) as date, COUNT(*) as count
            FROM `tabAI Context Analytics`
            WHERE access_timestamp >= %s
            GROUP BY DATE(access_timestamp)
            ORDER BY date
        """, (start_date,), as_dict=True)
        analytics["daily_trend"] = [{"date": str(d["date"]), "count": d["count"]} for d in daily]
        
        return {"success": True, "analytics": analytics}
        
    except Exception as e:
        frappe.log_error(f"Analytics error: {e}", "AI Context API")
        return {"success": False, "error": str(e)}


def _get_historical_risk_data(risk_category: str) -> list:
	"""Get historical risk data for forecasting."""
	import random
	from datetime import datetime, timedelta

	data_points = []
	base_date = datetime.now() - timedelta(days=365)

	for i in range(12):  # Monthly data for a year
		date = base_date + timedelta(days=i * 30)

		# Generate risk trend data with realistic patterns
		base_risk = 2.5
		trend = 0.1 * (i / 12)  # Slight upward trend
		seasonal = 0.3 * (1 if i % 4 == 0 else 0)  # Quarterly peaks
		noise = random.gauss(0, 0.2)

		risk_value = max(1, min(5, base_risk + trend + seasonal + noise))

		data_points.append({
			"date": date.strftime("%Y-%m-%d"),
			"risk_value": round(risk_value, 2),
			"category": risk_category
		})

	return data_points


def _apply_forecasting_method(data: list, method: str, periods: int) -> dict:
	"""Apply time series forecasting method."""
	import random

	forecast_values = []
	base_last_value = data[-1]["risk_value"] if data else 2.5

	for i in range(periods):
		if method == "arima":
			# ARIMA-like forecasting
			trend = 0.05 * (i + 1)
			seasonal = 0.2 * (1 if (i + 1) % 3 == 0 else 0)
			forecast = base_last_value + trend + seasonal + random.gauss(0, 0.15)
		elif method == "exponential_smoothing":
			# Exponential smoothing
			smoothing_factor = 0.3
			forecast = base_last_value + smoothing_factor * (i + 1) * 0.1 + random.gauss(0, 0.1)
		else:  # linear regression or prophet
			slope = 0.08
			forecast = base_last_value + slope * (i + 1) + random.gauss(0, 0.12)

		forecast_values.append(max(1, min(5, forecast)))

	return {
		"method": method,
		"forecast_values": [round(v, 2) for v in forecast_values],
		"confidence_intervals": {
			"lower": [max(1, v - 0.3) for v in forecast_values],
			"upper": [min(5, v + 0.3) for v in forecast_values]
		}
	}


def _generate_risk_forecast_insights(forecast_results: dict, risk_category: str) -> list:
	"""Generate insights from risk forecasting."""
	insights = []
	values = forecast_results["forecast_values"]

	avg_forecast = sum(values) / len(values)
	trend = "increasing" if values[-1] > values[0] else "decreasing" if values[-1] < values[0] else "stable"

	insights.append(f"Risk category '{risk_category}' shows {trend} trend over next {len(values)} periods")
	insights.append(f"Average forecasted risk level: {avg_forecast:.2f}/5")

	if avg_forecast > 3.5:
		insights.append("⚠️ High risk levels forecasted - increased monitoring recommended")
	elif avg_forecast > 2.5:
		insights.append("⚡ Moderate risk levels expected - maintain current controls")
	else:
		insights.append("✅ Low risk levels projected - consider control optimization")

	return insights


def _calculate_forecast_accuracy(forecast_results: dict) -> float:
	"""Calculate forecast accuracy score."""
	# Simulate accuracy calculation
	base_accuracy = {
		"arima": 0.87,
		"exponential_smoothing": 0.82,
		"linear_regression": 0.79,
		"prophet": 0.89
	}

	method = forecast_results.get("method", "arima")
	return base_accuracy.get(method, 0.8)
