// Copyright (c) 2025, mkaguzi and contributors
// For license information, please see license.txt

frappe.ui.form.on('Agent Execution Log', {
    refresh: function(frm) {
        // Add custom buttons based on status
        if (frm.doc.status === 'Failed' && frm.doc.retry_count < frm.doc.max_retries) {
            frm.add_custom_button(__('Retry Execution'), function() {
                frappe.call({
                    method: 'mkaguzi.agents.doctype.agent_execution_log.agent_execution_log.retry_agent_execution',
                    args: {
                        log_name: frm.doc.name
                    },
                    callback: function(r) {
                        frappe.msgprint(r.message);
                        frm.reload_doc();
                    }
                });
            }, __('Actions'));
        }

        if (frm.doc.status === 'Running' || frm.doc.status === 'Pending') {
            frm.add_custom_button(__('Cancel Execution'), function() {
                frappe.confirm(
                    __('Are you sure you want to cancel this execution?'),
                    function() {
                        frappe.call({
                            method: 'mkaguzi.agents.doctype.agent_execution_log.agent_execution_log.cancel_agent_execution',
                            args: {
                                log_name: frm.doc.name
                            },
                            callback: function(r) {
                                frappe.msgprint(r.message);
                                frm.reload_doc();
                            }
                        });
                    }
                );
            }, __('Actions'));
        }

        // Add button to view related findings
        if (frm.doc.findings_generated && frm.doc.finding_ids) {
            frm.add_custom_button(__('View Findings'), function() {
                const finding_ids = frm.doc.finding_ids.split(',');
                finding_ids.forEach(function(id) {
                    frappe.set_route('Form', 'Audit Finding', id.trim());
                });
            }, __('Actions'));
        }

        // Add dashboard button
        frm.add_custom_button(__('View Dashboard'), function() {
            frappe.set_route('List', 'Agent Execution Log', {
                agent_type: frm.doc.agent_type
            });
        }, __('Navigation'));

        // Format status indicator
        if (frm.doc.status) {
            const status_colors = {
                'Pending': 'gray',
                'Running': 'blue',
                'Completed': 'green',
                'Failed': 'red',
                'Cancelled': 'gray',
                'Timeout': 'orange'
            };

            $(frm.wrapper).find('.form-layout')
                .find('[data-fieldname="status"]')
                .find('.static-area')
                .addClass('indicator ' + (status_colors[frm.doc.status] || 'gray'));
        }

        // Auto-refresh for running executions
        if (frm.doc.status === 'Running') {
            if (!frm.refresh_interval) {
                frm.refresh_interval = setInterval(function() {
                    frm.reload_doc();
                }, 5000); // Refresh every 5 seconds
            }
        } else {
            if (frm.refresh_interval) {
                clearInterval(frm.refresh_interval);
                frm.refresh_interval = null;
            }
        }
    },

    onload: function(frm) {
        // Parse JSON fields for display
        if (frm.doc.input_data) {
            try {
                frm._input_data_parsed = JSON.parse(frm.doc.input_data);
            } catch (e) {
                frm._input_data_parsed = null;
            }
        }

        if (frm.doc.output_data) {
            try {
                frm._output_data_parsed = JSON.parse(frm.doc.output_data);
            } catch (e) {
                frm._output_data_parsed = null;
            }
        }

        if (frm.doc.result_json) {
            try {
                frm._result_json_parsed = JSON.parse(frm.doc.result_json);
            } catch (e) {
                frm._result_json_parsed = null;
            }
        }
    },

    agent_type: function(frm) {
        // Set agent name based on type
        const agent_names = {
            'Financial': 'Financial Agent',
            'Risk': 'Risk Assessment Agent',
            'Compliance': 'Compliance Verification Agent',
            'Discovery': 'Discovery Agent',
            'Notification': 'Notification Agent'
        };

        if (agent_names[frm.doc.agent_type]) {
            frm.set_value('agent_name', agent_names[frm.doc.agent_type]);
        }
    }
});

// Real-time event handlers
frappe.realtime.on('agent_execution_started', function(data) {
    // Refresh if viewing the same agent
    if (cur_frm && cur_frm.doctype === 'Agent Execution Log' &&
        cur_frm.doc.agent_id === data.agent_id) {
        cur_frm.reload_doc();
    }
});

frappe.realtime.on('agent_execution_completed', function(data) {
    // Refresh if viewing the same agent
    if (cur_frm && cur_frm.doctype === 'Agent Execution Log' &&
        cur_frm.doc.agent_id === data.agent_id) {
        cur_frm.reload_doc();
    }

    // Show notification
    frappe.msgprint(
        __('Agent execution {0} completed with status: {1}').format(
            data.agent_id,
            data.status
        )
    );
});

frappe.realtime.on('agent_execution_cancelled', function(data) {
    // Refresh if viewing the same execution
    if (cur_frm && cur_frm.doctype === 'Agent Execution Log' &&
        cur_frm.doc.name === data.name) {
        cur_frm.reload_doc();
    }
});
