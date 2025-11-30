import { computed, reactive, ref, watch } from "vue"

/**
 * Composable for managing multi-section forms with progress tracking,
 * validation, and section navigation.
 *
 * @param {Object} options - Configuration options
 * @param {Array} options.sections - Array of section definitions { id, label, description, icon, requiredFields }
 * @param {Object} options.form - Reactive form data object
 * @param {Function} options.validateSection - Function to validate a specific section
 * @param {Object} options.childTables - Map of child table field names to their doctype names
 */
export function useMultiSectionForm(options = {}) {
	const {
		sections = [],
		form = reactive({}),
		validateSection = null,
		childTables = {},
	} = options

	// State
	const activeSection = ref(sections[0]?.id || "")
	const errors = reactive({})
	const sectionErrors = reactive({})
	const isSaving = ref(false)
	const isSavingDraft = ref(false)
	const hasUnsavedChanges = ref(false)

	// Track form changes
	watch(
		() => form,
		() => {
			hasUnsavedChanges.value = true
		},
		{ deep: true },
	)

	/**
	 * Get the status of a section based on required fields completion
	 * @param {string} sectionId - The section ID to check
	 * @returns {'complete' | 'partial' | 'incomplete' | 'error'}
	 */
	const getSectionStatus = (sectionId) => {
		// Check for validation errors in section
		if (sectionErrors[sectionId]?.length > 0) {
			return "error"
		}

		const section = sections.find((s) => s.id === sectionId)
		if (!section?.requiredFields) return "incomplete"

		const requiredFields = section.requiredFields
		const filledFields = requiredFields.filter((field) => {
			const value = form[field]
			if (Array.isArray(value)) return value.length > 0
			if (typeof value === "boolean") return true
			return value !== null && value !== undefined && value !== ""
		})

		if (filledFields.length === 0) return "incomplete"
		if (filledFields.length === requiredFields.length) return "complete"
		return "partial"
	}

	/**
	 * Get CSS class for section status indicator
	 */
	const getSectionStatusClass = (sectionId) => {
		const status = getSectionStatus(sectionId)
		const classes = {
			complete: "bg-green-500 text-white",
			partial: "bg-yellow-400 text-white",
			incomplete: "bg-gray-200 text-gray-600",
			error: "bg-red-500 text-white",
		}
		return classes[status] || classes.incomplete
	}

	/**
	 * Calculate completed sections count
	 */
	const completedSections = computed(() => {
		return sections.filter((s) => getSectionStatus(s.id) === "complete").length
	})

	/**
	 * Calculate form progress percentage
	 */
	const formProgress = computed(() => {
		if (sections.length === 0) return 0
		return Math.round((completedSections.value / sections.length) * 100)
	})

	/**
	 * Check if form is valid (all required sections complete)
	 */
	const isFormValid = computed(() => {
		const requiredSections = sections.filter((s) => s.required !== false)
		return requiredSections.every((s) => getSectionStatus(s.id) === "complete")
	})

	/**
	 * Navigate to a specific section
	 */
	const navigateToSection = (sectionId) => {
		if (sections.find((s) => s.id === sectionId)) {
			activeSection.value = sectionId
		}
	}

	/**
	 * Navigate to next section
	 */
	const nextSection = () => {
		const currentIndex = sections.findIndex((s) => s.id === activeSection.value)
		if (currentIndex < sections.length - 1) {
			activeSection.value = sections[currentIndex + 1].id
		}
	}

	/**
	 * Navigate to previous section
	 */
	const prevSection = () => {
		const currentIndex = sections.findIndex((s) => s.id === activeSection.value)
		if (currentIndex > 0) {
			activeSection.value = sections[currentIndex - 1].id
		}
	}

	/**
	 * Check if current section is first
	 */
	const isFirstSection = computed(() => {
		return sections.findIndex((s) => s.id === activeSection.value) === 0
	})

	/**
	 * Check if current section is last
	 */
	const isLastSection = computed(() => {
		return (
			sections.findIndex((s) => s.id === activeSection.value) ===
			sections.length - 1
		)
	})

	/**
	 * Navigate to first section with errors or incomplete status
	 */
	const navigateToFirstError = () => {
		const errorSection = sections.find((s) => {
			const status = getSectionStatus(s.id)
			return status === "error" || status === "incomplete"
		})
		if (errorSection) {
			activeSection.value = errorSection.id
		}
	}

	/**
	 * Validate the entire form
	 * @returns {boolean} True if form is valid
	 */
	const validateForm = () => {
		// Clear previous errors
		Object.keys(errors).forEach((key) => delete errors[key])
		Object.keys(sectionErrors).forEach((key) => delete sectionErrors[key])

		let isValid = true

		// Validate each section
		for (const section of sections) {
			if (validateSection) {
				const sectionResult = validateSection(section.id, form)
				if (sectionResult && Object.keys(sectionResult).length > 0) {
					sectionErrors[section.id] = Object.keys(sectionResult)
					Object.assign(errors, sectionResult)
					isValid = false
				}
			}
		}

		if (!isValid) {
			navigateToFirstError()
		}

		return isValid
	}

	/**
	 * Clear a specific field error
	 */
	const clearError = (fieldName) => {
		if (errors[fieldName]) {
			delete errors[fieldName]
		}
	}

	/**
	 * Clear all errors
	 */
	const clearAllErrors = () => {
		Object.keys(errors).forEach((key) => delete errors[key])
		Object.keys(sectionErrors).forEach((key) => delete sectionErrors[key])
	}

	/**
	 * Prepare form data for submission, adding doctype to child table rows
	 * @returns {Object} Form data ready for API submission
	 */
	const prepareFormData = () => {
		const data = { ...form }

		// Add doctype to child table rows
		for (const [fieldName, doctype] of Object.entries(childTables)) {
			if (Array.isArray(data[fieldName])) {
				data[fieldName] = data[fieldName].map((row) => ({
					...row,
					doctype,
				}))
			}
		}

		return data
	}

	/**
	 * Reset form to initial state
	 */
	const resetForm = (initialData = {}) => {
		Object.keys(form).forEach((key) => {
			if (Array.isArray(form[key])) {
				form[key] = []
			} else if (typeof form[key] === "object" && form[key] !== null) {
				form[key] = {}
			} else {
				form[key] = ""
			}
		})

		// Apply initial data if provided
		Object.assign(form, initialData)

		// Reset state
		activeSection.value = sections[0]?.id || ""
		clearAllErrors()
		hasUnsavedChanges.value = false
	}

	/**
	 * Load existing data into form
	 */
	const loadFormData = (data) => {
		if (!data) return

		Object.keys(form).forEach((key) => {
			if (data[key] !== undefined) {
				form[key] = data[key]
			}
		})

		hasUnsavedChanges.value = false
	}

	/**
	 * Get section by ID
	 */
	const getSection = (sectionId) => {
		return sections.find((s) => s.id === sectionId)
	}

	/**
	 * Get current section index (1-based)
	 */
	const currentSectionIndex = computed(() => {
		return sections.findIndex((s) => s.id === activeSection.value) + 1
	})

	return {
		// State
		activeSection,
		errors,
		sectionErrors,
		isSaving,
		isSavingDraft,
		hasUnsavedChanges,

		// Computed
		completedSections,
		formProgress,
		isFormValid,
		isFirstSection,
		isLastSection,
		currentSectionIndex,

		// Methods
		getSectionStatus,
		getSectionStatusClass,
		navigateToSection,
		nextSection,
		prevSection,
		navigateToFirstError,
		validateForm,
		clearError,
		clearAllErrors,
		prepareFormData,
		resetForm,
		loadFormData,
		getSection,
	}
}
