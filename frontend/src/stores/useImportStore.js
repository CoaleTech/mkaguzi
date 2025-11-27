import { createResource } from "frappe-ui"
import { defineStore } from "pinia"
import { computed, ref } from "vue"

export const useImportStore = defineStore("import", () => {
	// State
	const imports = ref([])
	const importHistory = ref([])
	const activeImport = ref(null)
	const loading = ref({
		list: false,
		create: false,
		process: false,
		validate: false,
		templates: false,
	})
	const error = ref(null)

	// Import Templates
	const importTemplates = ref([
		{
			id: "audit_findings",
			name: "Audit Findings",
			doctype: "Audit Finding",
			description: "Import audit findings with all required fields",
			required_fields: [
				{ field: "finding_title", label: "Finding Title", type: "Data" },
				{ field: "finding_type", label: "Finding Type", type: "Select" },
				{ field: "severity", label: "Severity", type: "Select" },
				{ field: "status", label: "Status", type: "Select" },
				{ field: "description", label: "Description", type: "Text Editor" },
			],
			optional_fields: [
				{ field: "audit_plan", label: "Audit Plan", type: "Link" },
				{
					field: "control_procedure",
					label: "Control Procedure",
					type: "Link",
				},
				{ field: "due_date", label: "Due Date", type: "Date" },
				{ field: "assignee", label: "Assignee", type: "Link" },
				{ field: "department", label: "Department", type: "Link" },
				{ field: "risk_level", label: "Risk Level", type: "Select" },
			],
			sample_data: [
				{
					"Finding Title": "Inadequate Access Controls",
					"Finding Type": "Control Deficiency",
					Severity: "High",
					Status: "Open",
					Description: "User access permissions not properly segregated",
				},
			],
		},
		{
			id: "control_procedures",
			name: "Control Procedures",
			doctype: "Control Procedure",
			description: "Import control procedures and testing requirements",
			required_fields: [
				{ field: "procedure_name", label: "Procedure Name", type: "Data" },
				{ field: "control_type", label: "Control Type", type: "Select" },
				{ field: "frequency", label: "Frequency", type: "Select" },
				{ field: "owner", label: "Owner", type: "Link" },
			],
			optional_fields: [
				{ field: "process_area", label: "Process Area", type: "Link" },
				{ field: "risk_category", label: "Risk Category", type: "Select" },
				{ field: "description", label: "Description", type: "Text Editor" },
				{
					field: "testing_approach",
					label: "Testing Approach",
					type: "Text Editor",
				},
				{ field: "automated", label: "Automated", type: "Check" },
			],
			sample_data: [
				{
					"Procedure Name": "Monthly Bank Reconciliation",
					"Control Type": "Detective",
					Frequency: "Monthly",
					Owner: "Finance Manager",
				},
			],
		},
		{
			id: "audit_tests",
			name: "Audit Tests",
			doctype: "Audit Test",
			description: "Import audit test cases and procedures",
			required_fields: [
				{ field: "test_name", label: "Test Name", type: "Data" },
				{ field: "test_type", label: "Test Type", type: "Select" },
				{ field: "audit_plan", label: "Audit Plan", type: "Link" },
				{ field: "procedure", label: "Procedure", type: "Text Editor" },
			],
			optional_fields: [
				{
					field: "control_procedure",
					label: "Control Procedure",
					type: "Link",
				},
				{ field: "sample_size", label: "Sample Size", type: "Int" },
				{ field: "population_size", label: "Population Size", type: "Int" },
				{
					field: "expected_result",
					label: "Expected Result",
					type: "Text Editor",
				},
				{ field: "risk_assessment", label: "Risk Assessment", type: "Select" },
			],
			sample_data: [
				{
					"Test Name": "Segregation of Duties Test",
					"Test Type": "Controls Testing",
					Procedure:
						"Review user access matrix and validate separation of duties",
				},
			],
		},
	])

	// Resources
	const importResource = createResource({
		url: "mkaguzi.api.imports.get_imports",
		auto: false,
	})

	const processImportResource = createResource({
		url: "mkaguzi.api.imports.process_import",
		auto: false,
	})

	const validateDataResource = createResource({
		url: "mkaguzi.api.imports.validate_import_data",
		auto: false,
	})

	// Actions
	const fetchImports = async (filters = {}) => {
		try {
			loading.value.list = true
			error.value = null

			const response = await importResource.fetch({
				params: {
					filters,
					fields: [
						"name",
						"import_type",
						"status",
						"file_name",
						"total_rows",
						"processed_rows",
						"success_count",
						"error_count",
						"creation",
						"modified",
						"owner",
					],
				},
			})

			imports.value = response || []
			return response
		} catch (err) {
			error.value = err.message
			console.error("Failed to fetch imports:", err)
		} finally {
			loading.value.list = false
		}
	}

	const createImport = async (importData) => {
		try {
			loading.value.create = true
			error.value = null

			const response = await createResource({
				url: "mkaguzi.api.imports.create_import",
				auto: false,
			}).fetch({
				params: importData,
			})

			if (response) {
				activeImport.value = response
				await fetchImports()
				return response
			}
		} catch (err) {
			error.value = err.message
			console.error("Failed to create import:", err)
			throw err
		} finally {
			loading.value.create = false
		}
	}

	const uploadFile = async (file, importType) => {
		try {
			loading.value.create = true
			error.value = null

			const formData = new FormData()
			formData.append("file", file)
			formData.append("import_type", importType)

			const response = await fetch(
				"/api/method/mkaguzi.api.imports.upload_import_file",
				{
					method: "POST",
					body: formData,
				},
			)

			if (!response.ok) {
				throw new Error(`Upload failed: ${response.statusText}`)
			}

			const data = await response.json()

			if (data.message) {
				activeImport.value = data.message
				return data.message
			} else {
				throw new Error(data.exc || "Upload failed")
			}
		} catch (err) {
			error.value = err.message
			console.error("Failed to upload file:", err)
			throw err
		} finally {
			loading.value.create = false
		}
	}

	const validateImportData = async (importId, mappings) => {
		try {
			loading.value.validate = true
			error.value = null

			const response = await validateDataResource.fetch({
				params: {
					import_id: importId,
					field_mappings: mappings,
				},
			})

			if (response) {
				// Update active import with validation results
				if (activeImport.value?.name === importId) {
					activeImport.value = {
						...activeImport.value,
						validation_results: response.validation_results,
						field_mappings: mappings,
						is_valid: response.is_valid,
						validation_summary: response.validation_summary,
					}
				}
				return response
			}
		} catch (err) {
			error.value = err.message
			console.error("Failed to validate import data:", err)
			throw err
		} finally {
			loading.value.validate = false
		}
	}

	const processImport = async (importId, options = {}) => {
		try {
			loading.value.process = true
			error.value = null

			const response = await processImportResource.fetch({
				params: {
					import_id: importId,
					...options,
				},
			})

			if (response) {
				// Update active import
				if (activeImport.value?.name === importId) {
					activeImport.value = {
						...activeImport.value,
						...response,
					}
				}
				await fetchImports()
				return response
			}
		} catch (err) {
			error.value = err.message
			console.error("Failed to process import:", err)
			throw err
		} finally {
			loading.value.process = false
		}
	}

	const cancelImport = async (importId) => {
		try {
			const response = await createResource({
				url: "mkaguzi.api.imports.cancel_import",
				auto: false,
			}).fetch({
				params: { import_id: importId },
			})

			if (response) {
				await fetchImports()
				if (activeImport.value?.name === importId) {
					activeImport.value = null
				}
				return response
			}
		} catch (err) {
			error.value = err.message
			console.error("Failed to cancel import:", err)
			throw err
		}
	}

	const downloadTemplate = async (templateId) => {
		try {
			loading.value.templates = true

			const template = importTemplates.value.find((t) => t.id === templateId)
			if (!template) {
				throw new Error("Template not found")
			}

			const response = await createResource({
				url: "mkaguzi.api.imports.generate_template",
				auto: false,
			}).fetch({
				params: {
					template_id: templateId,
					doctype: template.doctype,
					fields: [...template.required_fields, ...template.optional_fields],
				},
			})

			if (response?.download_url) {
				// Trigger download
				const link = document.createElement("a")
				link.href = response.download_url
				link.download = `${template.name}_Template.xlsx`
				link.click()
				return response
			}
		} catch (err) {
			error.value = err.message
			console.error("Failed to download template:", err)
			throw err
		} finally {
			loading.value.templates = false
		}
	}

	const getImportHistory = async (filters = {}) => {
		try {
			const response = await createResource({
				url: "mkaguzi.api.imports.get_import_history",
				auto: false,
			}).fetch({
				params: { filters },
			})

			importHistory.value = response || []
			return response
		} catch (err) {
			error.value = err.message
			console.error("Failed to fetch import history:", err)
		}
	}

	const getFieldSuggestions = (doctype, fieldName) => {
		// Returns field mapping suggestions based on doctype and field patterns
		const suggestions = {
			audit_finding: {
				patterns: {
					"title|name|finding": "finding_title",
					"type|category": "finding_type",
					"severity|priority|level": "severity",
					"status|state": "status",
					"description|details|comment": "description",
					"due|date": "due_date",
					"assign|owner|responsible": "assignee",
					"dept|department": "department",
				},
			},
			control_procedure: {
				patterns: {
					"name|title|procedure": "procedure_name",
					"type|category": "control_type",
					"frequency|period": "frequency",
					"owner|responsible": "owner",
					"process|area": "process_area",
					"risk|category": "risk_category",
				},
			},
		}

		const doctypeKey = doctype.toLowerCase().replace(" ", "_")
		const patterns = suggestions[doctypeKey]?.patterns || {}

		const fieldLower = fieldName.toLowerCase()
		for (const [pattern, mappedField] of Object.entries(patterns)) {
			if (pattern.split("|").some((p) => fieldLower.includes(p))) {
				return mappedField
			}
		}

		return null
	}

	// Computed
	const activeImports = computed(() =>
		imports.value.filter((imp) =>
			["Draft", "Processing", "Validating"].includes(imp.status),
		),
	)

	const completedImports = computed(() =>
		imports.value.filter((imp) =>
			["Completed", "Failed", "Cancelled"].includes(imp.status),
		),
	)

	const importStats = computed(() => {
		const total = imports.value.length
		const completed = imports.value.filter(
			(imp) => imp.status === "Completed",
		).length
		const failed = imports.value.filter((imp) => imp.status === "Failed").length
		const processing = imports.value.filter(
			(imp) => imp.status === "Processing",
		).length

		return {
			total,
			completed,
			failed,
			processing,
			success_rate: total > 0 ? ((completed / total) * 100).toFixed(1) : 0,
		}
	})

	const availableTemplates = computed(() => importTemplates.value)

	// Initialize
	const initialize = async () => {
		await fetchImports()
	}

	return {
		// State
		imports,
		importHistory,
		activeImport,
		loading,
		error,
		importTemplates,

		// Actions
		fetchImports,
		createImport,
		uploadFile,
		validateImportData,
		processImport,
		cancelImport,
		downloadTemplate,
		getImportHistory,
		getFieldSuggestions,
		initialize,

		// Computed
		activeImports,
		completedImports,
		importStats,
		availableTemplates,
	}
})
