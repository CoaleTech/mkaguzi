# Copyright (c) 2025, mkaguzi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class AuditEngagementDataPeriod(Document):
    def validate(self):
        # Validate date range
        if self.start_date and self.end_date:
            if self.start_date >= self.end_date:
                frappe.throw("Start date must be before end date")

    def before_save(self):
        pass

    def after_insert(self):
        pass

    def on_update(self):
        pass

    def on_submit(self):
        pass

    def on_cancel(self):
        pass