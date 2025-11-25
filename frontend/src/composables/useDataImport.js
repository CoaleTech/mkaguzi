import { createResource } from "frappe-ui"

export function useDataImport() {
	const uploadCSV = async (file, importType) => {
		const formData = new FormData()
		formData.append("file", file)
		formData.append("import_type", importType)

		const resource = createResource({
			url: "iams.api.data_imports.upload_csv",
			params: formData,
		})

		await resource.submit()
		return resource.data
	}

	const validateImport = async (importId) => {
		const resource = createResource({
			url: "iams.api.data_imports.validate_import",
			params: { import_id: importId },
		})

		await resource.submit()
		return resource.data
	}

	const processImport = async (importId) => {
		const resource = createResource({
			url: "iams.api.data_imports.process_import",
			params: { import_id: importId },
		})

		await resource.submit()
		return resource.data
	}

	return { uploadCSV, validateImport, processImport }
}
