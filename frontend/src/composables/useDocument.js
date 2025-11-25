import { createResource } from "frappe-ui"

export function useDocument(doctype, name) {
	const doc = createResource({
		url: "frappe.client.get",
		params: { doctype, name },
		auto: !!name,
	})

	const save = async (data) => {
		const saveResource = createResource({
			url: "frappe.client.save",
			params: { doc: { doctype, name, ...data } },
		})
		await saveResource.submit()
		return saveResource.data
	}

	const delete_ = async () => {
		const deleteResource = createResource({
			url: "frappe.client.delete",
			params: { doctype, name },
		})
		await deleteResource.submit()
	}

	return { doc, save, delete: delete_ }
}
