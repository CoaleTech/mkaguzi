# Copyright (c) 2024, Coale Tech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class VATReconciliation(Document):
    def before_insert(self):
        """Set prepared_by to current user"""
        self.prepared_by = frappe.session.user
        self.status = "Draft"

    def validate(self):
        """Validate reconciliation document"""
        self.validate_files_for_reconciliation_type()
        self.update_file_statuses()

    def validate_files_for_reconciliation_type(self):
        """Ensure required files are uploaded based on reconciliation type"""
        if self.status in ["Draft", "Files Uploaded"]:
            # Only validate when ready to process
            return

        required_files = self.get_required_files()
        missing_files = []

        for file_field, file_name in required_files.items():
            if not getattr(self, file_field):
                missing_files.append(file_name)

        if missing_files:
            frappe.throw(
                _("Please upload the following files: {0}").format(", ".join(missing_files))
            )

    def get_required_files(self):
        """Get required files based on reconciliation type"""
        if self.reconciliation_type == "System vs iTax":
            return {
                "system_data_file": "System Data",
                "itax_data_file": "iTax Data"
            }
        elif self.reconciliation_type == "System vs TIMs":
            return {
                "system_data_file": "System Data",
                "tims_data_file": "TIMs Data"
            }
        elif self.reconciliation_type == "iTax vs TIMs":
            return {
                "itax_data_file": "iTax Data",
                "tims_data_file": "TIMs Data"
            }
        return {}

    def update_file_statuses(self):
        """Update file upload statuses"""
        if self.system_data_file and self.system_data_status == "Not Uploaded":
            self.system_data_status = "Uploaded"
        elif not self.system_data_file:
            self.system_data_status = "Not Uploaded"
            self.system_data_rows = 0

        if self.itax_data_file and self.itax_data_status == "Not Uploaded":
            self.itax_data_status = "Uploaded"
        elif not self.itax_data_file:
            self.itax_data_status = "Not Uploaded"
            self.itax_data_rows = 0

        if self.tims_data_file and self.tims_data_status == "Not Uploaded":
            self.tims_data_status = "Uploaded"
        elif not self.tims_data_file:
            self.tims_data_status = "Not Uploaded"
            self.tims_data_rows = 0

        # Update overall status
        self.update_overall_status()

    def update_overall_status(self):
        """Update overall status based on file uploads"""
        if self.status == "Draft":
            required_files = self.get_required_files()
            all_uploaded = all(
                getattr(self, file_field) for file_field in required_files.keys()
            )
            if all_uploaded:
                self.status = "Files Uploaded"

    def on_update(self):
        """After update, check if we need to find previous reconciliation"""
        if self.compare_with_previous and not self.previous_reconciliation:
            self.find_previous_reconciliation()

    def find_previous_reconciliation(self):
        """Find the previous month's reconciliation for comparison"""
        months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        
        current_month_idx = months.index(self.reconciliation_month)
        
        if current_month_idx == 0:
            # January - look for December of previous year
            prev_month = "December"
            # Would need to get previous fiscal year
            prev_year = None  # Handle this based on fiscal year logic
        else:
            prev_month = months[current_month_idx - 1]
            prev_year = self.fiscal_year

        if prev_year:
            previous = frappe.db.get_value(
                "VAT Reconciliation",
                {
                    "reconciliation_month": prev_month,
                    "fiscal_year": prev_year,
                    "reconciliation_type": self.reconciliation_type,
                    "status": ["in", ["Completed", "Reviewed", "Approved"]],
                    "name": ["!=", self.name]
                },
                "name"
            )
            
            if previous:
                self.db_set("previous_reconciliation", previous)

    def calculate_summary(self):
        """Calculate summary statistics from reconciliation items"""
        matched = 0
        unmatched_a = 0
        unmatched_b = 0
        discrepancies = 0
        total_variance = 0

        for item in self.reconciliation_items:
            if item.match_status == "Matched":
                matched += 1
            elif item.match_status == "Unmatched Source A":
                unmatched_a += 1
            elif item.match_status == "Unmatched Source B":
                unmatched_b += 1
            elif item.match_status == "Amount Discrepancy":
                discrepancies += 1
            
            total_variance += abs(item.variance or 0)

        self.total_matched = matched
        self.total_unmatched_source_a = unmatched_a
        self.total_unmatched_source_b = unmatched_b
        self.total_amount_discrepancies = discrepancies
        self.total_variance_amount = total_variance

        total_records = matched + unmatched_a + unmatched_b + discrepancies
        if total_records > 0:
            self.match_percentage = (matched / total_records) * 100
        else:
            self.match_percentage = 0

        # Determine reconciliation status
        if self.match_percentage == 100:
            self.reconciliation_status = "Fully Reconciled"
        elif self.match_percentage > 0:
            self.reconciliation_status = "Partially Reconciled"
        else:
            self.reconciliation_status = "Not Reconciled"

    def compare_with_previous_month(self):
        """Compare current reconciliation with previous month"""
        if not self.previous_reconciliation:
            return None

        prev_doc = frappe.get_doc("VAT Reconciliation", self.previous_reconciliation)
        
        comparison = {
            "current_variance": self.total_variance_amount,
            "previous_variance": prev_doc.total_variance_amount,
            "variance_change": self.total_variance_amount - prev_doc.total_variance_amount,
            "current_match_percent": self.match_percentage,
            "previous_match_percent": prev_doc.match_percentage,
            "match_percent_change": self.match_percentage - prev_doc.match_percentage,
            "current_discrepancies": self.total_amount_discrepancies,
            "previous_discrepancies": prev_doc.total_amount_discrepancies
        }

        # Determine trend
        if comparison["variance_change"] < 0:
            self.db_set("variance_trend", "Improved")
        elif comparison["variance_change"] > 0:
            self.db_set("variance_trend", "Worsened")
        else:
            self.db_set("variance_trend", "No Change")

        return comparison
