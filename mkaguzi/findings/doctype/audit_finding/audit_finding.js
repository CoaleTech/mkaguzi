// License: MIT

frappe.ui.form.on('Audit Finding', {
    refresh: function(frm) {
        // Add AI Review button
        if (frm.doc.ai_review_status && ['Reviewed', 'Failed'].includes(frm.doc.ai_review_status)) {
            frm.add_custom_button(__('Re-run AI Review'), function() {
                frappe.confirm(
                    __('Are you sure you want to re-run AI review for this finding?'),
                    function() {
                        frappe.call({
                            method: 'mkaguzi.agents.ai_reviewer.rerun_ai_review',
                            args: {
                                finding_name: frm.doc.name
                            },
                            callback: function(r) {
                                if (r.message) {
                                    frappe.show_alert({
                                        message: __('AI review queued successfully'),
                                        indicator: 'green'
                                    });
                                    frm.refresh();
                                }
                            }
                        });
                    }
                );
            }, __('AI Review'));
        }

        // Show AI Review status indicator
        if (frm.doc.ai_review_status) {
            let indicator_color = 'blue';
            let indicator_text = frm.doc.ai_review_status;

            switch (frm.doc.ai_review_status) {
                case 'Pending':
                    indicator_color = 'orange';
                    break;
                case 'Reviewed':
                    indicator_color = 'green';
                    break;
                case 'Failed':
                    indicator_color = 'red';
                    break;
                case 'Skipped':
                    indicator_color = 'grey';
                    break;
            }

            frm.dashboard.add_indicator(__('AI Review: {0}', [indicator_text]), indicator_color);
        }

        // Show severity mismatch warning
        if (frm.doc.severity_mismatch) {
            frm.dashboard.add_indicator(
                __('⚠️ Severity Mismatch: Agent ({0}) vs AI ({1})', [frm.doc.risk_rating, frm.doc.ai_severity_suggestion]),
                'red'
            );
        }

        // Make AI Review section collapsible and read-only
        frm.toggle_display('ai_review_section', frm.doc.ai_review_status && frm.doc.ai_review_status !== 'Pending');
    },

    ai_review_status: function(frm) {
        // Refresh to update indicators when status changes
        frm.refresh();
    },

    severity_mismatch: function(frm) {
        // Refresh to update indicators when mismatch status changes
        frm.refresh();
    }
});