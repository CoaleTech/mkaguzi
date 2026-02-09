import frappe
from typing import Dict, List, Optional, Any
from frappe.utils import today, add_months


class ERPNextQueries:
    """Shared query layer for native ERPNext DocTypes with date-windowed filtering."""

    @staticmethod
    def get_gl_entries(
        from_date: str,
        to_date: str,
        company: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 5000
    ) -> List[Dict[str, Any]]:
        """Query GL Entry with date window and company filter."""
        base_filters = {
            "posting_date": ["between", [from_date, to_date]],
            "company": company,
            "is_cancelled": 0
        }
        if filters:
            base_filters.update(filters)

        return frappe.get_all(
            "GL Entry",
            filters=base_filters,
            fields=[
                "name", "account", "debit", "credit", "party_type", "party",
                "voucher_type", "voucher_no", "posting_date", "is_cancelled"
            ],
            order_by="posting_date desc",
            limit_page_length=limit
        )

    @staticmethod
    def get_sales_invoices(
        from_date: str,
        to_date: str,
        company: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 5000
    ) -> List[Dict[str, Any]]:
        """Query Sales Invoice with date window and company filter."""
        base_filters = {
            "posting_date": ["between", [from_date, to_date]],
            "company": company,
            "docstatus": ["!=", 2]  # Not cancelled
        }
        if filters:
            base_filters.update(filters)

        return frappe.get_all(
            "Sales Invoice",
            filters=base_filters,
            fields=[
                "name", "customer", "posting_date", "grand_total",
                "outstanding_amount", "status", "is_return", "docstatus"
            ],
            order_by="posting_date desc",
            limit_page_length=limit
        )

    @staticmethod
    def get_purchase_invoices(
        from_date: str,
        to_date: str,
        company: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 5000
    ) -> List[Dict[str, Any]]:
        """Query Purchase Invoice with date window and company filter."""
        base_filters = {
            "posting_date": ["between", [from_date, to_date]],
            "company": company,
            "docstatus": ["!=", 2]  # Not cancelled
        }
        if filters:
            base_filters.update(filters)

        return frappe.get_all(
            "Purchase Invoice",
            filters=base_filters,
            fields=[
                "name", "supplier", "posting_date", "grand_total",
                "outstanding_amount", "bill_no", "on_hold", "docstatus"
            ],
            order_by="posting_date desc",
            limit_page_length=limit
        )

    @staticmethod
    def get_payment_entries(
        from_date: str,
        to_date: str,
        company: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 5000
    ) -> List[Dict[str, Any]]:
        """Query Payment Entry with date window and company filter."""
        base_filters = {
            "posting_date": ["between", [from_date, to_date]],
            "company": company,
            "docstatus": ["!=", 2]  # Not cancelled
        }
        if filters:
            base_filters.update(filters)

        return frappe.get_all(
            "Payment Entry",
            filters=base_filters,
            fields=[
                "name", "payment_type", "posting_date", "paid_amount",
                "party_type", "party", "mode_of_payment", "docstatus"
            ],
            order_by="posting_date desc",
            limit_page_length=limit
        )

    @staticmethod
    def get_journal_entries(
        from_date: str,
        to_date: str,
        company: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 5000
    ) -> List[Dict[str, Any]]:
        """Query Journal Entry with date window and company filter."""
        base_filters = {
            "posting_date": ["between", [from_date, to_date]],
            "company": company,
            "docstatus": ["!=", 2]  # Not cancelled
        }
        if filters:
            base_filters.update(filters)

        return frappe.get_all(
            "Journal Entry",
            filters=base_filters,
            fields=[
                "name", "voucher_type", "posting_date", "total_debit",
                "total_credit", "docstatus"
            ],
            order_by="posting_date desc",
            limit_page_length=limit
        )

    @staticmethod
    def get_stock_ledger_entries(
        from_date: str,
        to_date: str,
        company: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 5000
    ) -> List[Dict[str, Any]]:
        """Query Stock Ledger Entry with date window and company filter."""
        base_filters = {
            "posting_date": ["between", [from_date, to_date]],
            "company": company
        }
        if filters:
            base_filters.update(filters)

        return frappe.get_all(
            "Stock Ledger Entry",
            filters=base_filters,
            fields=[
                "name", "item_code", "warehouse", "posting_date",
                "actual_qty", "qty_after_transaction", "valuation_rate", "stock_value"
            ],
            order_by="posting_date desc",
            limit_page_length=limit
        )

    @staticmethod
    def get_items(
        company: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 5000
    ) -> List[Dict[str, Any]]:
        """Query Item with company filter (no date window for master data)."""
        base_filters = {
            "disabled": 0
        }
        if filters:
            base_filters.update(filters)

        return frappe.get_all(
            "Item",
            filters=base_filters,
            fields=[
                "name", "item_code", "item_name", "item_group",
                "valuation_rate", "disabled"
            ],
            limit_page_length=limit
        )

    @staticmethod
    def get_assets(
        company: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 5000
    ) -> List[Dict[str, Any]]:
        """Query Asset with company filter (no date window for master data)."""
        base_filters = {
            "company": company
        }
        if filters:
            base_filters.update(filters)

        return frappe.get_all(
            "Asset",
            filters=base_filters,
            fields=[
                "name", "asset_name", "item_code", "asset_category",
                "purchase_date", "gross_purchase_amount", "value_after_depreciation",
                "status", "location", "custodian"
            ],
            limit_page_length=limit
        )


# Convenience functions for direct import
def get_gl_entries(*args, **kwargs):
    return ERPNextQueries.get_gl_entries(*args, **kwargs)

def get_sales_invoices(*args, **kwargs):
    return ERPNextQueries.get_sales_invoices(*args, **kwargs)

def get_purchase_invoices(*args, **kwargs):
    return ERPNextQueries.get_purchase_invoices(*args, **kwargs)

def get_payment_entries(*args, **kwargs):
    return ERPNextQueries.get_payment_entries(*args, **kwargs)

def get_journal_entries(*args, **kwargs):
    return ERPNextQueries.get_journal_entries(*args, **kwargs)

def get_stock_ledger_entries(*args, **kwargs):
    return ERPNextQueries.get_stock_ledger_entries(*args, **kwargs)

def get_items(*args, **kwargs):
    return ERPNextQueries.get_items(*args, **kwargs)

def get_assets(*args, **kwargs):
    return ERPNextQueries.get_assets(*args, **kwargs)