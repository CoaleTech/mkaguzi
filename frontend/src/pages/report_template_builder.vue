<template>
  <div class="report-template-builder-page">
    <ReportTemplateBuilder
      :initial-template="initialTemplate"
      @save="handleSave"
      @cancel="handleCancel"
    />
  </div>
</template>

<script>
import ReportTemplateBuilder from "../components/templates/reports/TemplateBuilder.vue"

export default {
	name: "ReportTemplateBuilderPage",
	components: {
		ReportTemplateBuilder,
	},
	data() {
		return {
			initialTemplate: null,
		}
	},
	mounted() {
		// Check if we're editing an existing template
		const templateId = this.$route.query.template_id
		if (templateId) {
			this.loadTemplate(templateId)
		}
	},
	methods: {
		async loadTemplate(templateId) {
			try {
				const response = await frappe.call({
					method: "mkaguzi.api.templates.get_template",
					args: {
						template_id: templateId,
					},
				})

				if (response.message) {
					this.initialTemplate = response.message
				}
			} catch (error) {
				console.error("Error loading template:", error)
				frappe.msgprint(__("Error loading template: {0}", [error.message]))
			}
		},

		async handleSave(templateData) {
			try {
				const method = this.initialTemplate
					? "mkaguzi.api.templates.update_template"
					: "mkaguzi.api.templates.create_template"

				const response = await frappe.call({
					method: method,
					args: {
						...templateData,
						template_id: this.initialTemplate?.name,
					},
				})

				if (response.message) {
					frappe.msgprint(__("Template saved successfully"))

					// Redirect to template manager or stay on page
					if (!this.initialTemplate) {
						// New template created, redirect to edit mode
						this.$router.push({
							name: "report-template-builder",
							query: { template_id: response.message.name },
						})
					}
				}
			} catch (error) {
				console.error("Error saving template:", error)
				frappe.msgprint(__("Error saving template: {0}", [error.message]))
			}
		},

		handleCancel() {
			// Redirect back to template manager
			this.$router.push({ name: "template-manager" })
		},
	},
}
</script>

<style scoped>
.report-template-builder-page {
  min-height: 100vh;
  background-color: #f9fafb;
  padding: 1rem;
}
</style>