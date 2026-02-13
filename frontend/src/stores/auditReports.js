import { createResource } from "frappe-ui"
import { ref } from "vue"
import { defineStore } from "pinia"

export const useAuditReportsStore = defineStore("auditReports", () => {
	const currentReport = ref(null)
	const loading = ref(false)

	const fetchReportDetail = async (name) => {
		loading.value = true
		try {
			const res = await createResource({
				url: "frappe.client.get",
				params: { doctype: "Audit Report", name },
			}).fetch()
			currentReport.value = res
			return res
		} catch (err) {
			console.error("Failed to fetch report:", err)
			currentReport.value = null
			return null
		} finally {
			loading.value = false
		}
	}

	return { currentReport, loading, fetchReportDetail }
})
