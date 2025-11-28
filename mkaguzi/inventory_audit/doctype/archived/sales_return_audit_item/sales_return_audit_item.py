# Copyright (c) 2025, CoaleTech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SalesReturnAuditItem(Document):
    def validate(self):
        self.calculate_variance()
    
    def calculate_variance(self):
        """Calculate variance quantity and value"""
        system_qty = self.system_quantity or 0
        physical_qty = self.physical_quantity or 0
        unit_value = self.unit_value or 0
        
        # Variance = Physical - System (negative means shortage)
        self.variance_quantity = physical_qty - system_qty
        
        # Calculate variance percentage
        if system_qty != 0:
            self.variance_percent = (self.variance_quantity / system_qty) * 100
        else:
            self.variance_percent = 0 if physical_qty == 0 else 100
        
        # Calculate variance value
        self.variance_value = self.variance_quantity * unit_value
        
        # Calculate return value (system qty × unit value)
        self.return_value = system_qty * unit_value
