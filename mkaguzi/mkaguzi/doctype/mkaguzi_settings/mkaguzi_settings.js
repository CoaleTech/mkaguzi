// License: MIT
// Copyright (c) 2025, Coale Tech and contributors

frappe.ui.form.on("Mkaguzi Settings", {
	refresh(frm) {
		// Dashboard indicators
		if (frm.doc.system_enabled) {
			frm.dashboard.set_headline_alert(
				'<span class="indicator green">Mkaguzi System Active</span>'
			);
		} else {
			frm.dashboard.set_headline_alert(
				'<span class="indicator red">Mkaguzi System Disabled</span>'
			);
		}

		if (frm.doc.ai_enabled) {
			frm.dashboard.add_indicator(
				__("AI Review: Enabled ({0})", [frm.doc.use_paid_model ? "Paid + Free Fallback" : "Free Model"]),
				"green"
			);
		} else {
			frm.dashboard.add_indicator(__("AI Review: Disabled"), "orange");
		}

		// Add custom buttons for AI section
		if (frm.doc.ai_enabled && frm.doc.api_key) {
			frm.add_custom_button(__("Test Connection"), function () {
				frappe.call({
					method: "mkaguzi.api.openrouter.test_openrouter_connection",
					freeze: true,
					freeze_message: __("Testing OpenRouter connection..."),
					callback: function (r) {
						if (r.message) {
							if (r.message.success) {
								let msg = r.message.message || "Connection successful";
								if (r.message.credits_remaining !== undefined) {
									msg += `<br/>Credits remaining: ${r.message.credits_remaining}`;
								}
								frappe.show_alert({
									message: msg,
									indicator: "green",
								});
							} else {
								frappe.show_alert({
									message: r.message.error || "Connection failed",
									indicator: "red",
								});
							}
						}
					},
					error: function (err) {
						frappe.show_alert({
							message: __("Failed to test connection"),
							indicator: "red",
						});
					}
				});
			}, __("AI Tools"));

			frm.add_custom_button(__("Refresh Available Models"), function () {
				frappe.call({
					method: "mkaguzi.api.openrouter.fetch_available_models",
					freeze: true,
					freeze_message: __("Fetching models from OpenRouter..."),
					callback: function (r) {
						if (r.message) {
							frappe.show_alert({
								message: __("Models refreshed successfully"),
								indicator: "green",
							});
							frm.reload_doc();
						}
					},
				});
			}, __("AI Tools"));

			frm.add_custom_button(__("Get Recommendations"), function () {
				frappe.call({
					method: "mkaguzi.api.openrouter.get_recommended_models",
					freeze: true,
					callback: function (r) {
						if (r.message) {
							let msg = "<h4>Recommended Models</h4>";
							msg += "<p><b>Free:</b></p><ul>";
							(r.message.free || []).forEach(function (m) {
								msg += `<li>${m.id} - ${m.name}</li>`;
							});
							msg += "</ul><p><b>Paid:</b></p><ul>";
							(r.message.paid || []).forEach(function (m) {
								msg += `<li>${m.id} - ${m.name}</li>`;
							});
							msg += "</ul>";
							frappe.msgprint(msg, __("Model Recommendations"));
						}
					},
				});
			}, __("AI Tools"));
		}

		// Button to clear all caches
		frm.add_custom_button(__("Clear All Caches"), function () {
			frappe.call({
				method: "frappe.client.delete_cache",
				callback: function () {
					frappe.show_alert({
						message: __("All caches cleared"),
						indicator: "green",
					});
				},
			});
		}, __("Maintenance"));
	},
});
