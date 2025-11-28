# Copyright (c) 2025, mkaguzi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ReportRevision(Document):
    def validate(self):
        pass
    
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
