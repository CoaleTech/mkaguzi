# Copyright (c) 2025, Coale Tech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AIMultiContextSession(Document):
    def before_insert(self):
        if not self.created_by:
            self.created_by = frappe.session.user
