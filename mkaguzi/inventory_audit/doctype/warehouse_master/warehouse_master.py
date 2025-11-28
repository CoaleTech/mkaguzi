# Copyright (c) 2025, CoaleTech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class WarehouseMaster(Document):
    def validate(self):
        self.validate_warehouse_code()
    
    def validate_warehouse_code(self):
        """Ensure warehouse code is uppercase and trimmed"""
        if self.warehouse_code:
            self.warehouse_code = self.warehouse_code.strip().upper()
    
    def before_save(self):
        """Set store manager name if not fetched"""
        if self.store_manager and not self.store_manager_name:
            self.store_manager_name = frappe.db.get_value("User", self.store_manager, "full_name")


def get_warehouse_assignments(warehouse_code):
    """Get default assignments for a warehouse"""
    if not warehouse_code:
        return {}
    
    warehouse = frappe.get_cached_doc("Warehouse Master", warehouse_code)
    return {
        "stock_analyst": warehouse.default_stock_analyst,
        "stock_taker": warehouse.default_stock_taker,
        "store_manager": warehouse.store_manager,
        "hod_approver": warehouse.hod_approver
    }
