# Copyright (c) 2025, Coale Tech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AIContextTemplate(Document):
    def before_insert(self):
        if not self.owner:
            self.owner = frappe.session.user
    
    def validate(self):
        # Validate JSON in default_filters
        if self.default_filters:
            import json
            try:
                json.loads(self.default_filters)
            except json.JSONDecodeError:
                frappe.throw("Default Filters must be valid JSON")
