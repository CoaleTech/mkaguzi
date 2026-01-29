// Copyright (c) 2025, Coale Tech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Data Period', {
	refresh: function(frm) {
		// Add custom buttons
		if (frm.doc.docstatus === 1 && !frm.doc.is_closed) {
			frm.add_custom_button(__('Close Period'), function() {
				frappe.call({
					method: 'mkaguzi.doctype.data_period.data_period.close_data_period',
					args: {
						period_name: frm.doc.name
					},
					callback: function(r) {
						frappe.msgprint(r.message);
						frm.reload_doc();
					}
				});
			}, __('Actions'));
		}

		if (frm.doc.docstatus === 1 && frm.doc.is_closed) {
			frm.add_custom_button(__('Reopen Period'), function() {
				frappe.call({
					method: 'mkaguzi.doctype.data_period.data_period.reopen_data_period',
					args: {
						period_name: frm.doc.name
					},
					callback: function(r) {
						frappe.msgprint(r.message);
						frm.reload_doc();
					}
				});
			}, __('Actions'));
		}
	},

	start_date: function(frm) {
		// Auto-update period name when dates change
		if (frm.doc.start_date && !frm.doc.period_name) {
			var date = frappe.datetime.str_to_obj(frm.doc.start_date);
			var month_year = frappe.datetime.obj_to_str(date).substring(0, 7);
			frm.set_value('period_name', month_year);
		}
	}
});
