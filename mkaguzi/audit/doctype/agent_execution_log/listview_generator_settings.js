// List View Generator Settings for Agent Execution Log

frappe.listview_settings['Agent Execution Log'] = {
    add_fields: ['status', 'agent_type', 'start_time', 'duration_seconds', 'total_findings', 'error_occurred'],
    get_indicator: function(doc) {
        if (doc.status === 'Completed') {
            return [__('Completed'), 'green', 'status,=,Completed'];
        } else if (doc.status === 'Running') {
            return [__('Running'), 'blue', 'status,=,Running'];
        } else if (doc.status === 'Failed') {
            return [__('Failed'), 'red', 'status,=,Failed'];
        } else if (doc.status === 'Pending') {
            return [__('Pending'), 'gray', 'status,=,Pending'];
        } else if (doc.status === 'Cancelled') {
            return [__('Cancelled'), 'gray', 'status,=,Cancelled'];
        } else if (doc.status === 'Timeout') {
            return [__('Timeout'), 'orange', 'status,=,Timeout'];
        }
    },
    onload: function(listview) {
        // Add custom filters
        listview.page.add_menu_item(__('Show Running Agents'), function() {
            listview.filter_area.add([
                ['Agent Execution Log', 'status', '=', 'Running']
            ]);
        });

        listview.page.add_menu_item(__('Show Failed Executions'), function() {
            listview.filter_area.add([
                ['Agent Execution Log', 'status', '=', 'Failed']
            ]);
        });

        listview.page.add_menu_item(__('Show with Findings'), function() {
            listview.filter_area.add([
                ['Agent Execution Log', 'findings_generated', '=', 1]
            ]);
        });

        listview.page.add_menu_item(__('Show with Errors'), function() {
            listview.filter_area.add([
                ['Agent Execution Log', 'error_occurred', '=', 1]
            ]);
        });

        // Add custom button for bulk action
        listview.page.add_button(__('Cancel Selected'), function() {
            const selected_docs = listview.get_checked_items();
            if (selected_docs.length === 0) {
                frappe.msgprint(__('Please select at least one record'));
                return;
            }

            frappe.confirm(
                __('Are you sure you want to cancel {0} executions?').format(selected_docs.length),
                function() {
                    selected_docs.forEach(function(doc) {
                        if (doc.status === 'Running' || doc.status === 'Pending') {
                            frappe.call({
                                method: 'mkaguzi.agents.doctype.agent_execution_log.agent_execution_log.cancel_agent_execution',
                                args: {
                                    log_name: doc.name
                                }
                            });
                        }
                    });
                    listview.refresh();
                }
            );
        });

        // Auto-refresh for running agents
        setInterval(function() {
            const has_running = listview.data.some(function(doc) {
                return doc.status === 'Running';
            });

            if (has_running) {
                listview.refresh();
            }
        }, 10000); // Refresh every 10 seconds
    }
};
