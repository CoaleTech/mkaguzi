# License: MIT
# Copyright (c) 2025, Coale Tech and contributors
"""
Centralized settings access layer for Mkaguzi.

Usage:
    from mkaguzi.utils.settings import get_mkaguzi_settings, get_ai_config

All consumers should call these helpers rather than `frappe.get_single()`
directly, so caching and fallback logic live in one place.
"""

import frappe
from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from frappe.model.document import Document


# ---------------------------------------------------------------------------
# Core accessor
# ---------------------------------------------------------------------------

def get_mkaguzi_settings() -> "Document":
    """Return the cached Mkaguzi Settings singleton.

    Returns the Frappe document object. Results are cached in the
    Frappe request cache so repeated calls in the same request are free.
    """
    return frappe.get_single("Mkaguzi Settings")


def _get_field(field: str, default: Any = None) -> Any:
    """Safely read a single field from Mkaguzi Settings."""
    try:
        val = getattr(get_mkaguzi_settings(), field, None)
        return val if val is not None else default
    except Exception:
        return default


# ---------------------------------------------------------------------------
# AI / OpenRouter config
# ---------------------------------------------------------------------------

def get_ai_config() -> Dict[str, Any]:
    """Return dict of all AI/OpenRouter related settings."""
    s = get_mkaguzi_settings()
    return {
        "enabled": bool(s.ai_enabled),
        "api_key": s.get_password("api_key") if s.api_key else None,
        "use_paid_model": bool(s.use_paid_model),
        "free_model": s.free_model or "meta-llama/llama-3.3-70b-instruct:free",
        "paid_model": s.paid_model or "anthropic/claude-sonnet-4",
        "max_tokens": s.max_tokens or 1024,
        "temperature": s.temperature if s.temperature is not None else 0.3,
        "max_findings_per_run": s.max_findings_per_run or 20,
        "min_severity_for_review": s.min_severity_for_review or "All",
        "review_prompt_template": s.review_prompt_template,
        "severity_mismatch_notify": bool(s.severity_mismatch_notify),
        "mismatch_notification_roles": s.mismatch_notification_roles or "Audit Manager,System Manager",
    }


def is_ai_enabled() -> bool:
    """Quick check whether AI review is turned on."""
    return bool(_get_field("ai_enabled", False))


# ---------------------------------------------------------------------------
# Agent defaults
# ---------------------------------------------------------------------------

def get_agent_defaults() -> Dict[str, Any]:
    """Return global agent default configuration."""
    s = get_mkaguzi_settings()
    return {
        "max_batch_size": s.default_max_batch_size or 1000,
        "timeout_seconds": s.default_agent_timeout or 300,
        "retry_count": s.default_retry_count or 3,
        "log_level": s.default_log_level or "INFO",
        "scan_interval_hours": s.default_scan_interval_hours or 24,
        "aggregation_window_minutes": s.default_aggregation_window or 15,
        "max_digest_size": s.default_max_digest_size or 50,
    }


def get_agent_config_for_type(agent_type: str) -> Dict[str, Any]:
    """Return merged config for a specific agent type.

    Per-agent fields override global defaults when set (non-zero/non-empty).
    """
    defaults = get_agent_defaults()
    s = get_mkaguzi_settings()

    if agent_type == "financial":
        return {
            **defaults,
            "max_batch_size": s.financial_max_batch_size or defaults["max_batch_size"],
            "timeout_seconds": s.financial_timeout or defaults["timeout_seconds"],
            "retry_count": s.financial_retry_count or defaults["retry_count"],
            "benford_deviation_threshold": s.benford_deviation_threshold if s.benford_deviation_threshold else 0.05,
            "duplicate_similarity_threshold": s.duplicate_similarity_threshold if s.duplicate_similarity_threshold else 0.9,
            "large_transaction_multiplier": s.large_transaction_multiplier if s.large_transaction_multiplier else 3.0,
        }
    elif agent_type == "risk":
        return {
            **defaults,
            "prediction_horizon_days": s.risk_prediction_horizon_days or 30,
            "threshold_sensitivity": s.risk_threshold_sensitivity if s.risk_threshold_sensitivity is not None else 0.5,
            "min_data_points": s.risk_min_data_points or 100,
            "high_threshold": s.risk_high_threshold if s.risk_high_threshold else 0.8,
            "medium_threshold": s.risk_medium_threshold if s.risk_medium_threshold else 0.5,
            "low_threshold": s.risk_low_threshold if s.risk_low_threshold else 0.2,
        }
    elif agent_type == "compliance":
        return {
            **defaults,
            "auto_update_checks": bool(s.compliance_auto_update_checks),
            "severity_threshold": s.compliance_severity_threshold or "Medium",
            "gap_weight": s.compliance_gap_weight if s.compliance_gap_weight else 1.0,
            "overdue_escalation_days": s.compliance_overdue_escalation_days or 14,
        }
    elif agent_type == "discovery":
        return {
            **defaults,
            "scan_interval_hours": s.discovery_scan_interval_hours or defaults["scan_interval_hours"],
            "auto_update_catalog": bool(s.discovery_auto_update_catalog),
            "detect_schema_changes": bool(s.discovery_detect_schema_changes),
        }
    elif agent_type == "notification":
        return {
            **defaults,
            "aggregation_window_minutes": s.notification_aggregation_window or defaults["aggregation_window_minutes"],
            "max_digest_size": s.notification_max_digest_size or defaults["max_digest_size"],
            "escalation_enabled": bool(s.notification_escalation_enabled),
        }
    else:
        return defaults


# ---------------------------------------------------------------------------
# Financial thresholds (convenience)
# ---------------------------------------------------------------------------

def get_financial_thresholds() -> Dict[str, float]:
    """Return financial agent threshold values."""
    s = get_mkaguzi_settings()
    return {
        "benford_deviation": s.benford_deviation_threshold if s.benford_deviation_threshold else 0.05,
        "duplicate_similarity": s.duplicate_similarity_threshold if s.duplicate_similarity_threshold else 0.9,
        "large_transaction_multiplier": s.large_transaction_multiplier if s.large_transaction_multiplier else 3.0,
    }


# ---------------------------------------------------------------------------
# Risk thresholds (convenience)
# ---------------------------------------------------------------------------

def get_risk_thresholds() -> Dict[str, float]:
    """Return risk agent threshold values."""
    s = get_mkaguzi_settings()
    return {
        "high": s.risk_high_threshold if s.risk_high_threshold else 0.8,
        "medium": s.risk_medium_threshold if s.risk_medium_threshold else 0.5,
        "low": s.risk_low_threshold if s.risk_low_threshold else 0.2,
        "sensitivity": s.risk_threshold_sensitivity if s.risk_threshold_sensitivity is not None else 0.5,
    }


# ---------------------------------------------------------------------------
# Cache config
# ---------------------------------------------------------------------------

def get_cache_config() -> Dict[str, Any]:
    """Return cache-related settings."""
    s = get_mkaguzi_settings()
    return {
        "default_ttl": s.cache_default_ttl or 300,
        "prefix": s.cache_prefix or "mkaguzi:",
        "agent_state_ttl": s.agent_state_ttl or 3600,
        "message_bus_ttl": s.message_bus_ttl or 86400,
    }


# ---------------------------------------------------------------------------
# Rate limiting config
# ---------------------------------------------------------------------------

def get_rate_limit_config() -> Dict[str, Any]:
    """Return rate-limiting settings."""
    s = get_mkaguzi_settings()
    bypass = s.rate_limit_bypass_roles or "System Manager"
    return {
        "default_limit": s.rate_limit_default_limit or 100,
        "default_window": s.rate_limit_default_window or 3600,
        "burst_capacity": s.rate_limit_burst_capacity or 100,
        "refill_rate": s.rate_limit_refill_rate or 10,
        "bypass_roles": [r.strip() for r in bypass.split(",") if r.strip()],
    }


# ---------------------------------------------------------------------------
# Scheduling config
# ---------------------------------------------------------------------------

def get_scheduling_config() -> Dict[str, Any]:
    """Return scheduler task limits."""
    s = get_mkaguzi_settings()
    return {
        "financial_task_limit": s.financial_task_limit or 1000,
        "fraud_detection_limit": s.fraud_detection_limit or 500,
        "risk_assessment_limit": s.risk_assessment_limit or 100,
        "risk_prediction_days": s.risk_prediction_days or 30,
    }


# ---------------------------------------------------------------------------
# AI Caching and Quota
# ---------------------------------------------------------------------------

def get_ai_cache_ttl() -> int:
    """Return AI response cache TTL in seconds (default 24 hours)."""
    s = get_mkaguzi_settings()
    return (s.ai_cache_ttl or 86400) if hasattr(s, 'ai_cache_ttl') else 86400


def check_ai_quota() -> bool:
    """Check if today's AI quota has been exceeded.
    
    Returns:
        bool: True if quota available, False if exceeded
    """
    s = get_mkaguzi_settings()
    quota_used = s.ai_quota_used or 0
    max_quota = s.max_findings_per_run or 20
    reset_date = s.ai_quota_reset_date
    
    # Check if it's a new day
    today = frappe.utils.getdate()
    if reset_date and frappe.utils.getdate(reset_date) != today:
        # Reset for new day
        s.ai_quota_used = 0
        s.ai_quota_reset_date = today
        s.save(ignore_permissions=True)
        frappe.db.commit()
        return True
    
    return quota_used < max_quota


def increment_ai_quota() -> None:
    """Increment the AI quota counter for today."""
    s = get_mkaguzi_settings()
    today = frappe.utils.getdate()
    
    # Reset if needed
    reset_date = s.ai_quota_reset_date
    if reset_date and frappe.utils.getdate(reset_date) != today:
        s.ai_quota_used = 0
        s.ai_quota_reset_date = today
    
    # Increment
    s.ai_quota_used = (s.ai_quota_used or 0) + 1
    if not s.ai_quota_reset_date:
        s.ai_quota_reset_date = today
    
    s.save(ignore_permissions=True)
    frappe.db.commit()


def reset_daily_ai_quota() -> None:
    """Reset daily AI quota counter (called by scheduler at midnight).
    
    This is called daily and resets the quota counter to 0 and updates the reset date.
    """
    s = get_mkaguzi_settings()
    s.ai_quota_used = 0
    s.ai_quota_reset_date = frappe.utils.getdate()
    s.save(ignore_permissions=True)
    frappe.db.commit()


def invalidate_ai_cache_for_finding(doc, method=None) -> None:
    """Invalidate cached AI response for a finding when it's updated.
    
    Called from Audit Finding on_update hook.
    Frappe passes (doc, method) to doc_event hooks.
    """
    try:
        cache_key = f"mkaguzi:ai_review:{frappe.generate_hash(
            (doc.finding_title or '') + (doc.condition or '') + (doc.criteria or ''), 10
        )}"
        frappe.cache().delete_value(cache_key)
    except:
        pass
