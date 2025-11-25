import { createResource } from "frappe-ui"

export function useFrappeResource(doctype, name = null) {
	const resource = createResource({
		url: name ? "frappe.client.get" : "frappe.client.get_list",
		params: name
			? { doctype, name }
			: { doctype, fields: ["*"], limit_page_length: 20 },
		auto: true,
	})

	return resource
}
