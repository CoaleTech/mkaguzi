// Copyright (c) 2025, Coale Tech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Compliance Check', {
	refresh: function(frm) {
		// Add custom buttons based on status
		if (frm.doc.docstatus === 1) {
			if (frm.doc.status !== 'Compliant') {
				frm.add_custom_button(__('Mark Compliant'), function() {
					frm.set_value('status', 'Compliant');
					frm.set_value('completed_date', frappe.datetime.now_date());
					frm.save();
				}, __('Status'));
			}
		}

		// Add View Compliance Requirement button
		if (frm.doc.compliance_requirement) {
			frm.add_custom_button(__('View Requirement'), function() {
				frappe.set_route('Form', 'Compliance Requirement', frm.doc.compliance_requirement);
			}, __('Actions'));
		}

		// Highlight severity
		if (frm.doc.severity) {
			let severity_color = {
				'High': 'red',
				'Medium': 'orange',
				'Low': 'green'
			};
			$(frm.fields_dict['severity'].wrapper).css('color', severity_color[frm.doc.severity]).css('font-weight', 'bold');
		}

		// Set status indicator
		if (frm.doc.status) {
			let status_color = {
				'Compliant': 'green',
				'Non-Compliant': 'red',
				'Partially Compliant': 'orange',
				'Not Applicable': 'gray'
			};
			frm.dashboard.set_indicator(status_color[frm.doc.status] || 'gray');
		}

		// Show overdue warning
		if (frm.doc.due_date && frm.doc.due_date < frappe.datetime.now_date() && !frm.doc.completed_date) {
			frm.page.set_primary_action(__("Overdue"), function() {
				// Default primary action
			});
			$(frm.page.wrapper).find('.btn-primary').addClass('btn-danger');
		}
	},

	compliance_requirement: function(frm) {
		// Fetch compliance requirement details when selected
		if (frm.doc.compliance_requirement) {
			frappe.call({
				method: 'mkaguzi.doctype.compliance_check.compliance_check.get_compliance_requirement_details',
				args: {
					requirement_name: frm.doc.compliance_requirement
				},
				callback: function(r) {
					if (r.message) {
						// Details are auto-fetched via fetch_from in JSON
						frm.refresh_fields();
					}
				}
			});
		}
	},

	status: function(frm) {
		// Auto-populate remediation details based on status
		if (frm.doc.status === 'Non-Compliant' || frm.doc.status === 'Partially Compliant') {
			if (!frm.doc.remediation_plan) {
				frm.set_value('remediation_plan', 'Develop and implement corrective actions to address compliance gaps.');
			}
			if (!frm.doc.remediation_owner) {
				frm.set_value('remediation_owner', frappe.session.user);
			}
			if (!frm.doc.remediation_due_date && frm.doc.due_date) {
				// Set remediation due date to 30 days after check date
				let remediation_date = frappe.datetime.add_days(frm.doc.check_date, 30);
				frm.set_value('remediation_due_date', remediation_date);
			}
		}

		// Set completed date for compliant status
		if (frm.doc.status === 'Compliant' && !frm.doc.completed_date) {
			frm.set_value('completed_date', frappe.datetime.now_date());
		}
	},

	severity: function(frm) {
		// Show warning if non-compliant with low severity
		if (frm.doc.status === 'Non-Compliant' && frm.doc.severity === 'Low') {
			frappe.msgprint(__('Warning: Non-Compliant status typically requires High or Medium severity'));
		}
	}
});
