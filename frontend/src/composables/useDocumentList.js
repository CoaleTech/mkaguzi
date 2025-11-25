import { createResource } from "frappe-ui"

export function useDocumentList(doctype, options = {}) {
	const {
		filters = {},
		fields = ["*"],
		orderBy = "modified desc",
		pageLength = 20,
	} = options

	const list = createResource({
		url: "frappe.client.get_list",
		params: {
			doctype,
			fields,
			filters,
			order_by: orderBy,
			limit_page_length: pageLength,
		},
		auto: true,
	})

	const refresh = () => list.reload()

	return { list, refresh }
}
