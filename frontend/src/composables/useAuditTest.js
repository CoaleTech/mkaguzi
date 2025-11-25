import { createResource } from "frappe-ui"

export function useAuditTest() {
	const executeTest = async (testId, parameters) => {
		const resource = createResource({
			url: "iams.api.analytics.execute_test",
			params: { test_id: testId, parameters },
		})

		await resource.submit()
		return resource.data
	}

	const getTestResults = async (executionId) => {
		const resource = createResource({
			url: "iams.api.analytics.get_test_results",
			params: { execution_id: executionId },
		})

		await resource.submit()
		return resource.data
	}

	return { executeTest, getTestResults }
}
