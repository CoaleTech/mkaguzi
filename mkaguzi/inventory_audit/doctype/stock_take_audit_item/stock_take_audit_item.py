# Copyright (c) 2025, CoaleTech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class StockTakeAuditItem(Document):
    def validate(self):
        self.calculate_variance()
    
    def calculate_variance(self):
        """Calculate variance quantity and value"""
        system_qty = self.system_quantity or 0
        physical_qty = self.physical_quantity or 0
        pending_dispatch = self.pending_dispatch or 0
        unit_value = self.unit_value or 0
        
        # Variance = System Qty - Physical Qty - Pending Dispatch
        # Positive = surplus, Negative = shortage
        self.variance_quantity = system_qty - physical_qty - pending_dispatch
        
        # Calculate variance percentage
        if system_qty != 0:
            self.variance_percent = (self.variance_quantity / system_qty) * 100
        else:
            self.variance_percent = 0 if physical_qty == 0 else 100
        
        # Calculate variance value
        self.variance_value = self.variance_quantity * unit_value
        
        # Calculate system value (system qty × unit value)
        self.system_value = system_qty * unit_value
