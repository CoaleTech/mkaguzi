# Copyright (c) 2025, Coale Tech and contributors
# For license information, please see license.txt

"""
Add database indexes for AI Context API performance optimization.

This patch adds indexes to:
- AI Context Analytics: For query optimization on access patterns
- AI Context Pattern: For efficient pattern matching
- AI Context Share: For quick share lookups
- AI Context Version: For version history queries
- AI Multi Context Session: For session management
- VAT Reconciliation: Additional indexes for context queries
- Audit Finding: Additional indexes for context queries
"""

import frappe


def execute():
    """Execute the patch to add database indexes."""
    
    indexes_to_add = [
        # AI Context Analytics indexes
        {
            "doctype": "AI Context Analytics",
            "index_name": "idx_ai_analytics_user_timestamp",
            "columns": ["user", "access_timestamp"],
            "unique": False
        },
        {
            "doctype": "AI Context Analytics",
            "index_name": "idx_ai_analytics_page_type",
            "columns": ["page_type", "access_timestamp"],
            "unique": False
        },
        {
            "doctype": "AI Context Analytics",
            "index_name": "idx_ai_analytics_document",
            "columns": ["page_type", "document_id"],
            "unique": False
        },
        
        # AI Context Pattern indexes
        {
            "doctype": "AI Context Pattern",
            "index_name": "idx_ai_pattern_source",
            "columns": ["source_page_type", "co_access_count"],
            "unique": False
        },
        {
            "doctype": "AI Context Pattern",
            "index_name": "idx_ai_pattern_pair",
            "columns": ["source_page_type", "target_page_type"],
            "unique": True
        },
        
        # AI Context Share indexes
        {
            "doctype": "AI Context Share",
            "index_name": "idx_ai_share_id",
            "columns": ["share_id"],
            "unique": True
        },
        {
            "doctype": "AI Context Share",
            "index_name": "idx_ai_share_expires",
            "columns": ["shared_by", "expires_at"],
            "unique": False
        },
        
        # AI Context Version indexes
        {
            "doctype": "AI Context Version",
            "index_name": "idx_ai_version_id",
            "columns": ["version_id"],
            "unique": True
        },
        {
            "doctype": "AI Context Version",
            "index_name": "idx_ai_version_doc",
            "columns": ["page_type", "document_id", "version_number"],
            "unique": False
        },
        
        # AI Multi Context Session indexes
        {
            "doctype": "AI Multi Context Session",
            "index_name": "idx_ai_session_id",
            "columns": ["session_id"],
            "unique": True
        },
        {
            "doctype": "AI Multi Context Session",
            "index_name": "idx_ai_session_creator",
            "columns": ["created_by", "is_collaborative"],
            "unique": False
        },
        
        # AI Context Template indexes
        {
            "doctype": "AI Context Template",
            "index_name": "idx_ai_template_id",
            "columns": ["template_id"],
            "unique": True
        },
        {
            "doctype": "AI Context Template",
            "index_name": "idx_ai_template_page_public",
            "columns": ["page_type", "is_public"],
            "unique": False
        },
        
        # AI Context Affinity indexes
        {
            "doctype": "AI Context Affinity",
            "index_name": "idx_ai_affinity_pair",
            "columns": ["source_page_type", "target_page_type"],
            "unique": True
        },
    ]
    
    # Also add indexes to existing key DocTypes if they exist
    existing_doctype_indexes = [
        {
            "doctype": "VAT Reconciliation",
            "index_name": "idx_vat_recon_status_year",
            "columns": ["status", "fiscal_year"],
            "unique": False
        },
        {
            "doctype": "VAT Reconciliation",
            "index_name": "idx_vat_recon_company",
            "columns": ["company", "reconciliation_month"],
            "unique": False
        },
        {
            "doctype": "Audit Finding",
            "index_name": "idx_finding_status_risk",
            "columns": ["status", "risk_level"],
            "unique": False
        },
        {
            "doctype": "Audit Finding",
            "index_name": "idx_finding_engagement",
            "columns": ["engagement", "status"],
            "unique": False
        },
        {
            "doctype": "Risk Assessment",
            "index_name": "idx_risk_assess_status",
            "columns": ["status", "fiscal_year"],
            "unique": False
        },
        {
            "doctype": "Engagement",
            "index_name": "idx_engagement_status",
            "columns": ["status", "engagement_type"],
            "unique": False
        },
        {
            "doctype": "Corrective Action Plan",
            "index_name": "idx_cap_status_due",
            "columns": ["status", "due_date"],
            "unique": False
        },
    ]
    
    # Add indexes for AI Context DocTypes
    for idx in indexes_to_add:
        add_index_safely(idx)
    
    # Add indexes for existing DocTypes (only if DocType exists)
    for idx in existing_doctype_indexes:
        if frappe.db.exists("DocType", idx["doctype"]):
            add_index_safely(idx)
    
    frappe.db.commit()
    print("AI Context API indexes created successfully.")


def add_index_safely(index_config):
    """Add an index safely, handling errors if it already exists."""
    doctype = index_config["doctype"]
    index_name = index_config["index_name"]
    columns = index_config["columns"]
    unique = index_config.get("unique", False)
    
    # Check if DocType exists
    if not frappe.db.exists("DocType", doctype):
        print(f"DocType {doctype} does not exist, skipping index {index_name}")
        return
    
    table_name = f"tab{doctype}"
    
    # Check if index already exists
    try:
        existing_indexes = frappe.db.sql(f"SHOW INDEX FROM `{table_name}` WHERE Key_name = %s", index_name)
        if existing_indexes:
            print(f"Index {index_name} already exists on {doctype}")
            return
    except Exception:
        # Table might not exist yet
        print(f"Table for {doctype} might not exist yet, skipping index {index_name}")
        return
    
    # Create index
    try:
        columns_str = ", ".join([f"`{col}`" for col in columns])
        unique_str = "UNIQUE" if unique else ""
        
        frappe.db.sql(f"""
            CREATE {unique_str} INDEX `{index_name}` ON `{table_name}` ({columns_str})
        """)
        print(f"Created index {index_name} on {doctype}")
    except Exception as e:
        # Index might already exist with different name, or other error
        print(f"Could not create index {index_name} on {doctype}: {str(e)}")
