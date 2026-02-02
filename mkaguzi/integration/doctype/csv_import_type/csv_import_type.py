# -*- coding: utf-8 -*-
# Copyright (c) 2026, Coale Tech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CSVImportType(Document):
    def validate(self):
        if self.field_mapping:
            try:
                import json
                json.loads(self.field_mapping)
            except json.JSONDecodeError:
                frappe.throw("Field Mapping must be valid JSON")
