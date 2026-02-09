// Copyright (c) 2025, Coale Tech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Audit GL Entry', {
	refresh: function(frm) {
		// Add custom buttons based on status
		if (frm.doc.docstatus === 1) {
			if (frm.doc.status === 'Pending') {
				frm.add_custom_button(__('Mark as Reviewed'), function() {
					frm.set_value('status', 'Reviewed');
					frm.set_value('reviewed_by', frappe.session.user);
					frm.set_value('reviewed_date', frappe.datetime.now_datetime());
					frm.save();
				}, __('Status'));
			}

			if (frm.doc.status === 'Reviewed') {
				frm.add_custom_button(__('Acknowledge'), function() {
					frm.set_value('status', 'Acknowledged');
					frm.set_value('acknowledged_by', frappe.session.user);
					frm.set_value('acknowledged_date', frappe.datetime.now_datetime());
					frm.save();
				}, __('Status'));
			}
		}

		// Add View GL Entry button
		if (frm.doc.gl_entry_link) {
			frm.add_custom_button(__('View GL Entry'), function() {
				frappe.set_route('Form', 'GL Entry', frm.doc.gl_entry_link);
			}, __('Actions'));

			// Add View Voucher button if voucher type and no exist
			if (frm.doc.voucher_type && frm.doc.voucher_no) {
				frm.add_custom_button(__('View Voucher'), function() {
					frappe.set_route('Form', frm.doc.voucher_type, frm.doc.voucher_no);
				}, __('Actions'));
			}
		}

		// Highlight risk score
		if (frm.doc.risk_score >= 70) {
			$(frm.fields_dict['risk_score'].wrapper).css('color', 'red').css('font-weight', 'bold');
		} else if (frm.doc.risk_score >= 40) {
			$(frm.fields_dict['risk_score'].wrapper).css('color', 'orange').css('font-weight', 'bold');
		}

		// Set status indicator
		if (frm.doc.status) {
			let status_color = {
				'Pending': 'orange',
				'Reviewed': 'blue',
				'Acknowledged': 'green'
			};
			frm.dashboard.set_indicator(status_color[frm.doc.status] || 'gray');
		}
	},

	gl_entry_link: function(frm) {
		// Fetch GL Entry details when selected
		if (frm.doc.gl_entry_link) {
			frappe.call({
				method: 'mkaguzi.doctype.audit_gl_entry.audit_gl_entry.get_gl_entry_details',
				args: {
					gl_entry_name: frm.doc.gl_entry_link
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

	risk_score: function(frm) {
		// Validate risk score on change
		if (frm.doc.risk_score < 0 || frm.doc.risk_score > 100) {
			frappe.msgprint(__('Risk Score must be between 0 and 100'));
			frm.set_value('risk_score', 0);
		}
	}
});
