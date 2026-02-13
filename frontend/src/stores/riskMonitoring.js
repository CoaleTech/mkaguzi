import { createResource } from "frappe-ui"
import { computed, ref } from "vue"
import { defineStore } from "pinia"

export const useRiskMonitoringStore = defineStore("riskMonitoring", () => {
	const anomalyAlerts = ref([])
	const riskIndicators = ref([])
	const currentAlert = ref(null)
	const currentIndicator = ref(null)
	const loading = ref(false)
	const error = ref(null)

	const openAlerts = computed(() => anomalyAlerts.value.filter((a) => a.status === "Open"))
	const criticalAlerts = computed(() => anomalyAlerts.value.filter((a) => a.severity === "Critical"))
	const activeIndicators = computed(() => riskIndicators.value.filter((i) => i.status === "Active"))
	const alertIndicators = computed(() => riskIndicators.value.filter((i) => i.status === "Alert" || i.status === "Critical"))

	const fetchAnomalyAlerts = async (filters = {}) => {
		loading.value = true
		try {
			const res = await createResource({
				url: "frappe.client.get_list",
				params: {
					doctype: "Anomaly Alert",
					fields: [
						"name", "alert_id", "alert_type", "severity", "status",
						"detected_date", "alert_description", "source_doctype",
						"source_document", "assigned_to", "confidence_score",
						"detection_method", "false_positive",
					],
					filters,
					order_by: "detected_date desc",
					limit_page_length: 200,
				},
			}).fetch()
			anomalyAlerts.value = res || []
		} catch (err) {
			console.error("Failed to fetch anomaly alerts:", err)
			error.value = err.message
		} finally {
			loading.value = false
		}
	}

	const fetchAlertDetail = async (name) => {
		try {
			const res = await createResource({
				url: "frappe.client.get",
				params: { doctype: "Anomaly Alert", name },
			}).fetch()
			currentAlert.value = res
			return res
		} catch (err) {
			console.error("Failed to fetch alert detail:", err)
			return null
		}
	}

	const updateAlertStatus = async (name, status) => {
		try {
			await createResource({
				url: "frappe.client.set_value",
				params: { doctype: "Anomaly Alert", name, fieldname: "status", value: status },
			}).fetch()
			await fetchAnomalyAlerts()
		} catch (err) {
			console.error("Failed to update alert:", err)
			throw err
		}
	}

	const fetchRiskIndicators = async (filters = {}) => {
		loading.value = true
		try {
			const res = await createResource({
				url: "frappe.client.get_list",
				params: {
					doctype: "Risk Indicator",
					fields: [
						"name", "indicator_id", "indicator_name", "module",
						"indicator_type", "current_value", "threshold_value",
						"status", "description", "calculation_method",
						"last_updated", "frequency", "trend_direction",
					],
					filters,
					order_by: "last_updated desc",
					limit_page_length: 200,
				},
			}).fetch()
			riskIndicators.value = res || []
		} catch (err) {
			console.error("Failed to fetch risk indicators:", err)
			error.value = err.message
		} finally {
			loading.value = false
		}
	}

	const fetchIndicatorDetail = async (name) => {
		try {
			const res = await createResource({
				url: "frappe.client.get",
				params: { doctype: "Risk Indicator", name },
			}).fetch()
			currentIndicator.value = res
			return res
		} catch (err) {
			console.error("Failed to fetch indicator detail:", err)
			return null
		}
	}

	return {
		anomalyAlerts, riskIndicators, currentAlert, currentIndicator,
		loading, error, openAlerts, criticalAlerts, activeIndicators, alertIndicators,
		fetchAnomalyAlerts, fetchAlertDetail, updateAlertStatus,
		fetchRiskIndicators, fetchIndicatorDetail,
	}
})
