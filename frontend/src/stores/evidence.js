import { createResource } from "frappe-ui"
import { defineStore } from "pinia"
import { computed, ref } from "vue"

export const useEvidenceStore = defineStore("evidence", () => {
	// State
	const evidence = ref([])
	const evidenceTypes = ref([])
	const approvals = ref([])
	const documentVersions = ref([])
	const currentEvidence = ref(null)
	const loading = ref(false)

	// Upload state
	const uploadProgress = ref({})
	const uploadQueue = ref([])

	// Evidence statistics
	const evidenceStats = ref({
		total: 0,
		pending: 0,
		approved: 0,
		rejected: 0,
		attachments: 0,
	})

	// Getters
	const evidenceByFinding = computed(() => (findingId) => {
		return evidence.value.filter((e) => e.finding_id === findingId)
	})

	const evidenceByType = computed(() => (type) => {
		return evidence.value.filter((e) => e.evidence_type === type)
	})

	const pendingApprovals = computed(() => {
		return evidence.value.filter((e) => e.approval_status === "Pending")
	})

	const recentEvidence = computed(() => {
		return evidence.value
			.sort((a, b) => new Date(b.creation) - new Date(a.creation))
			.slice(0, 10)
	})

	const evidenceByStatus = computed(() => {
		const grouped = {}
		evidence.value.forEach((ev) => {
			const status = ev.approval_status || "Unknown"
			if (!grouped[status]) grouped[status] = []
			grouped[status].push(ev)
		})
		return grouped
	})

	// Actions
	const fetchEvidence = async (filters = {}) => {
		loading.value = true
		try {
			const response = await createResource({
				url: "frappe.client.get_list",
				params: {
					doctype: "Finding Evidence",
					fields: [
						"name",
						"evidence_id",
						"evidence_name",
						"evidence_type",
						"finding_id",
						"finding_name",
						"file_url",
						"file_name",
						"file_size",
						"file_type",
						"description",
						"approval_status",
						"approved_by",
						"approved_date",
						"uploaded_by",
						"upload_date",
						"version_number",
						"is_confidential",
						"retention_period",
						"tags",
						"creation",
						"modified",
					],
					filters: filters,
					limit_page_length: 1000,
					order_by: "creation desc",
				},
			}).fetch()
			evidence.value = response || []
			updateEvidenceStats()
		} catch (error) {
			console.error("Error fetching evidence:", error)
			evidence.value = []
		} finally {
			loading.value = false
		}
	}

	const fetchEvidenceDetails = async (evidenceId) => {
		try {
			const response = await createResource({
				url: "frappe.client.get",
				params: {
					doctype: "Finding Evidence",
					name: evidenceId,
				},
			}).fetch()
			currentEvidence.value = response
			return response
		} catch (error) {
			console.error("Error fetching evidence details:", error)
			return null
		}
	}

	const uploadEvidence = async (evidenceData, file = null) => {
		try {
			let response

			if (file) {
				// Upload file first
				const uploadResponse = await uploadFile(file, evidenceData.finding_id)
				if (uploadResponse.success) {
					evidenceData.file_url = uploadResponse.file_url
					evidenceData.file_name = uploadResponse.file_name
					evidenceData.file_size = uploadResponse.file_size
					evidenceData.file_type = uploadResponse.file_type
				}
			}

			// Create evidence record
			response = await createResource({
				url: "frappe.client.insert",
				params: {
					doc: {
						doctype: "Finding Evidence",
						...evidenceData,
					},
				},
			}).fetch()

			await fetchEvidence() // Refresh the list
			return response
		} catch (error) {
			console.error("Error uploading evidence:", error)
			throw error
		}
	}

	const uploadFile = async (file, findingId) => {
		return new Promise((resolve, reject) => {
			const formData = new FormData()
			formData.append("file", file)
			formData.append("is_private", "1")
			formData.append("folder", "Home/Evidence")
			formData.append("file_name", file.name)

			// Track upload progress
			const uploadId = Date.now().toString()
			uploadProgress.value[uploadId] = { progress: 0, status: "uploading" }

			const xhr = new XMLHttpRequest()

			xhr.upload.addEventListener("progress", (e) => {
				if (e.lengthComputable) {
					const progress = (e.loaded / e.total) * 100
					uploadProgress.value[uploadId].progress = progress
				}
			})

			xhr.addEventListener("load", () => {
				if (xhr.status === 200) {
					try {
						const response = JSON.parse(xhr.responseText)
						uploadProgress.value[uploadId].status = "completed"
						resolve({
							success: true,
							file_url: response.message.file_url,
							file_name: response.message.file_name,
							file_size: file.size,
							file_type: file.type,
						})
					} catch (error) {
						uploadProgress.value[uploadId].status = "failed"
						reject(new Error("Invalid response from server"))
					}
				} else {
					uploadProgress.value[uploadId].status = "failed"
					reject(new Error(`Upload failed with status: ${xhr.status}`))
				}
				delete uploadProgress.value[uploadId]
			})

			xhr.addEventListener("error", () => {
				uploadProgress.value[uploadId].status = "failed"
				reject(new Error("Upload failed"))
				delete uploadProgress.value[uploadId]
			})

			xhr.open("POST", "/api/method/upload_file")
			xhr.setRequestHeader("Accept", "application/json")
			xhr.setRequestHeader("X-Frappe-CSRF-Token", frappe.csrf_token)
			xhr.send(formData)
		})
	}

	const updateEvidence = async (evidenceId, updates) => {
		try {
			const response = await createResource({
				url: "frappe.client.set_value",
				params: {
					doctype: "Finding Evidence",
					name: evidenceId,
					fieldname: updates,
				},
			}).fetch()
			await fetchEvidence() // Refresh the list
			return response
		} catch (error) {
			console.error("Error updating evidence:", error)
			throw error
		}
	}

	const deleteEvidence = async (evidenceId) => {
		try {
			const response = await createResource({
				url: "frappe.client.delete",
				params: {
					doctype: "Finding Evidence",
					name: evidenceId,
				},
			}).fetch()
			await fetchEvidence() // Refresh the list
			return response
		} catch (error) {
			console.error("Error deleting evidence:", error)
			throw error
		}
	}

	const approveEvidence = async (evidenceId, approvalData) => {
		try {
			const response = await createResource({
				url: "mkaguzi.api.evidence.approve_evidence",
				params: {
					evidence_id: evidenceId,
					approval_status: "Approved",
					approval_comments: approvalData.comments,
					approved_by: frappe.session.user,
				},
			}).fetch()
			await fetchEvidence() // Refresh the list
			return response
		} catch (error) {
			console.error("Error approving evidence:", error)
			throw error
		}
	}

	const rejectEvidence = async (evidenceId, rejectionData) => {
		try {
			const response = await createResource({
				url: "mkaguzi.api.evidence.approve_evidence",
				params: {
					evidence_id: evidenceId,
					approval_status: "Rejected",
					approval_comments: rejectionData.comments,
					rejection_reason: rejectionData.reason,
					approved_by: frappe.session.user,
				},
			}).fetch()
			await fetchEvidence() // Refresh the list
			return response
		} catch (error) {
			console.error("Error rejecting evidence:", error)
			throw error
		}
	}

	const createEvidenceVersion = async (
		evidenceId,
		versionData,
		file = null,
	) => {
		try {
			const originalEvidence = await fetchEvidenceDetails(evidenceId)
			if (!originalEvidence) throw new Error("Original evidence not found")

			// Increment version number
			const newVersionNumber = (originalEvidence.version_number || 1) + 1

			// Create new version with updated data
			const newVersionData = {
				...versionData,
				evidence_id: originalEvidence.evidence_id + `_v${newVersionNumber}`,
				evidence_name:
					originalEvidence.evidence_name + ` (Version ${newVersionNumber})`,
				version_number: newVersionNumber,
				parent_evidence_id: evidenceId,
				approval_status: "Pending",
			}

			return await uploadEvidence(newVersionData, file)
		} catch (error) {
			console.error("Error creating evidence version:", error)
			throw error
		}
	}

	const fetchEvidenceTypes = async () => {
		try {
			const types = [
				"Document",
				"Screenshot",
				"Report",
				"Email",
				"Invoice",
				"Contract",
				"Approval",
				"Analysis",
				"Photo",
				"Video",
				"Audio",
				"Spreadsheet",
				"Presentation",
				"Other",
			]
			evidenceTypes.value = types.map((type) => ({ label: type, value: type }))
		} catch (error) {
			console.error("Error fetching evidence types:", error)
			evidenceTypes.value = []
		}
	}

	const searchEvidence = async (searchTerm) => {
		if (!searchTerm) {
			await fetchEvidence()
			return
		}

		try {
			const response = await createResource({
				url: "mkaguzi.api.evidence.search_evidence",
				params: {
					search_term: searchTerm,
				},
			}).fetch()
			evidence.value = response || []
			return response
		} catch (error) {
			console.error("Error searching evidence:", error)
			return []
		}
	}

	const bulkUpdateEvidence = async (evidenceIds, updates) => {
		try {
			const response = await createResource({
				url: "mkaguzi.api.evidence.bulk_update",
				params: {
					evidence_ids: evidenceIds,
					updates: updates,
				},
			}).fetch()
			await fetchEvidence() // Refresh the list
			return response
		} catch (error) {
			console.error("Error bulk updating evidence:", error)
			throw error
		}
	}

	const exportEvidence = async (filters = {}, format = "excel") => {
		try {
			const response = await createResource({
				url: "mkaguzi.api.evidence.export_evidence",
				params: {
					filters: filters,
					format: format,
				},
			}).fetch()
			return response
		} catch (error) {
			console.error("Error exporting evidence:", error)
			throw error
		}
	}

	// Helper functions
	const updateEvidenceStats = () => {
		const stats = {
			total: evidence.value.length,
			pending: evidence.value.filter((e) => e.approval_status === "Pending")
				.length,
			approved: evidence.value.filter((e) => e.approval_status === "Approved")
				.length,
			rejected: evidence.value.filter((e) => e.approval_status === "Rejected")
				.length,
			attachments: evidence.value.filter((e) => e.file_url).length,
		}
		evidenceStats.value = stats
	}

	const getEvidenceById = (evidenceId) => {
		return evidence.value.find((e) => e.name === evidenceId)
	}

	const getFileIcon = (fileType) => {
		const iconMap = {
			"application/pdf": "FileText",
			"application/msword": "FileText",
			"application/vnd.openxmlformats-officedocument.wordprocessingml.document":
				"FileText",
			"application/vnd.ms-excel": "FileSpreadsheet",
			"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
				"FileSpreadsheet",
			"image/jpeg": "Image",
			"image/png": "Image",
			"image/gif": "Image",
			"video/mp4": "Video",
			"video/avi": "Video",
			"audio/mp3": "Music",
			"audio/wav": "Music",
		}
		return iconMap[fileType] || "File"
	}

	const formatFileSize = (bytes) => {
		if (bytes === 0) return "0 Bytes"
		const k = 1024
		const sizes = ["Bytes", "KB", "MB", "GB", "TB"]
		const i = Math.floor(Math.log(bytes) / Math.log(k))
		return (
			Number.parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
		)
	}

	const isValidFileType = (file) => {
		const allowedTypes = [
			"application/pdf",
			"application/msword",
			"application/vnd.openxmlformats-officedocument.wordprocessingml.document",
			"application/vnd.ms-excel",
			"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
			"image/jpeg",
			"image/png",
			"image/gif",
			"video/mp4",
			"audio/mp3",
			"text/plain",
			"text/csv",
		]
		return allowedTypes.includes(file.type)
	}

	const clearCurrentEvidence = () => {
		currentEvidence.value = null
	}

	return {
		// State
		evidence,
		evidenceTypes,
		approvals,
		documentVersions,
		currentEvidence,
		loading,
		uploadProgress,
		uploadQueue,
		evidenceStats,

		// Getters
		evidenceByFinding,
		evidenceByType,
		pendingApprovals,
		recentEvidence,
		evidenceByStatus,

		// Actions
		fetchEvidence,
		fetchEvidenceDetails,
		uploadEvidence,
		uploadFile,
		updateEvidence,
		deleteEvidence,
		approveEvidence,
		rejectEvidence,
		createEvidenceVersion,
		fetchEvidenceTypes,
		searchEvidence,
		bulkUpdateEvidence,
		exportEvidence,

		// Helper functions
		getEvidenceById,
		getFileIcon,
		formatFileSize,
		isValidFileType,
		clearCurrentEvidence,
	}
})
