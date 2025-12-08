/**
 * Template Engine Utility
 * Handles template loading, rendering, and management for the Mkaguzi app
 */

import { call } from "frappe-ui"

export class TemplateEngine {
	/**
	 * Load template from backend
	 * @param {string} templateName - Name of the template
	 * @returns {Promise<Object>} Template data with content, engine, and config
	 */
	static async loadTemplate(templateName) {
		try {
			const response = await call(
				"mkaguzi.core.doctype.template_registry.template_registry.get_template_content",
				{
					template_name: templateName,
				},
			)

			return {
				content: response.content,
				engine: response.engine,
				config: response.config,
			}
		} catch (error) {
			console.error("Error loading template:", error)
			throw new Error(`Failed to load template: ${templateName}`)
		}
	}

	/**
	 * Render template with data
	 * @param {string} template - Template content
	 * @param {Object} data - Data to render
	 * @param {string} engine - Template engine (Jinja2, Vue, Handlebars, etc.)
	 * @returns {string} Rendered template
	 */
	static renderTemplate(template, data, engine = "Jinja2") {
		switch (engine.toLowerCase()) {
			case "jinja2":
				return this.renderJinja2Template(template, data)
			case "vue":
				return this.renderVueTemplate(template, data)
			case "handlebars":
				return this.renderHandlebarsTemplate(template, data)
			case "plain html":
			default:
				return this.renderPlainTemplate(template, data)
		}
	}

	/**
	 * Render Jinja2-style template (simplified implementation)
	 * @param {string} template - Template string
	 * @param {Object} data - Data object
	 * @returns {string} Rendered template
	 */
	static renderJinja2Template(template, data) {
		let rendered = template

		// Simple variable replacement {{ variable }}
		const variableRegex = /\{\{\s*(\w+)\s*\}\}/g
		rendered = rendered.replace(variableRegex, (match, varName) => {
			return data[varName] !== undefined ? data[varName] : match
		})

		// Simple loop {% for item in items %}...{% endfor %}
		const forLoopRegex =
			/\{\%\s*for\s+(\w+)\s+in\s+(\w+)\s*\%\}([\s\S]*?)\{\%\s*endfor\s*\%\}/g
		rendered = rendered.replace(
			forLoopRegex,
			(match, itemVar, arrayVar, content) => {
				const array = data[arrayVar] || []
				return array
					.map((item) => {
						let itemContent = content
						itemContent = itemContent.replace(
							new RegExp(`\{\{\s*${itemVar}(\.(\w+))?\s*\}\}`, "g"),
							(match, _, prop) => (prop ? item[prop] : item),
						)
						return itemContent
					})
					.join("")
			},
		)

		// Simple conditionals {% if condition %}...{% endif %}
		const ifRegex = /\{\%\s*if\s+(\w+)\s*\%\}([\s\S]*?)\{\%\s*endif\s*\%\}/g
		rendered = rendered.replace(ifRegex, (match, condition, content) => {
			return data[condition] ? content : ""
		})

		return rendered
	}

	/**
	 * Render Vue template (placeholder - would need Vue compiler)
	 * @param {string} template - Vue template
	 * @param {Object} data - Data object
	 * @returns {string} Rendered template
	 */
	static renderVueTemplate(template, data) {
		// For now, just do basic variable replacement
		// In a real implementation, this would use Vue's compiler
		console.warn("Vue template rendering not fully implemented")
		return this.renderPlainTemplate(template, data)
	}

	/**
	 * Render Handlebars template
	 * @param {string} template - Handlebars template
	 * @param {Object} data - Data object
	 * @returns {string} Rendered template
	 */
	static renderHandlebarsTemplate(template, data) {
		// Check if Handlebars is available
		if (typeof Handlebars !== "undefined") {
			const compiledTemplate = Handlebars.compile(template)
			return compiledTemplate(data)
		} else {
			console.warn("Handlebars not available, falling back to plain template")
			return this.renderPlainTemplate(template, data)
		}
	}

	/**
	 * Render plain template with basic variable replacement
	 * @param {string} template - Template string
	 * @param {Object} data - Data object
	 * @returns {string} Rendered template
	 */
	static renderPlainTemplate(template, data) {
		let rendered = template

		// Replace {{variable}} with data.variable
		Object.keys(data).forEach((key) => {
			const regex = new RegExp(`\\{\\{\\s*${key}\\s*\\}\\}`, "g")
			rendered = rendered.replace(regex, data[key] || "")
		})

		return rendered
	}

	/**
	 * Validate template syntax
	 * @param {string} template - Template content
	 * @param {string} engine - Template engine
	 * @returns {Object} Validation result
	 */
	static validateTemplate(template, engine = "Jinja2") {
		try {
			switch (engine.toLowerCase()) {
				case "jinja2":
					// Basic validation - check for balanced tags
					const openTags = (template.match(/\{\%/g) || []).length
					const closeTags = (template.match(/\%\}/g) || []).length
					if (openTags !== closeTags) {
						return { valid: false, error: "Unbalanced Jinja2 tags" }
					}
					break
				case "vue":
					// Basic Vue template validation
					if (!template.includes("<template>")) {
						return { valid: false, error: "Missing template tag" }
					}
					break
			}

			return { valid: true }
		} catch (error) {
			return { valid: false, error: error.message }
		}
	}

	/**
	 * Get default template for a type/category
	 * @param {string} templateType - Type of template
	 * @param {string} category - Template category
	 * @returns {Promise<Object>} Default template info
	 */
	static async getDefaultTemplate(templateType, category = null) {
		try {
			const response = await call(
				"mkaguzi.core.doctype.template_registry.template_registry.get_default_template",
				{
					template_type: templateType,
					category: category,
				},
			)

			return response
		} catch (error) {
			console.error("Error getting default template:", error)
			return null
		}
	}

	/**
	 * Get all templates by category
	 * @param {string} templateType - Type of template
	 * @param {string} category - Template category
	 * @returns {Promise<Array>} List of templates
	 */
	static async getTemplatesByCategory(templateType = null, category = null) {
		try {
			const response = await call(
				"mkaguzi.core.doctype.template_registry.template_registry.get_templates_by_category",
				{
					template_type: templateType,
					category: category,
				},
			)

			return response
		} catch (error) {
			console.error("Error getting templates by category:", error)
			return []
		}
	}

	/**
	 * Update template usage statistics
	 * @param {string} templateName - Name of the template
	 * @returns {Promise<Object>} Usage update result
	 */
	static async updateTemplateUsage(templateName) {
		try {
			const response = await call(
				"mkaguzi.core.doctype.template_registry.template_registry.update_template_usage",
				{
					template_name: templateName,
				},
			)

			return response
		} catch (error) {
			console.error("Error updating template usage:", error)
			return null
		}
	}

	/**
	 * Cache for loaded templates
	 */
	static templateCache = new Map()

	/**
	 * Load template with caching
	 * @param {string} templateName - Name of the template
	 * @param {boolean} useCache - Whether to use cache
	 * @returns {Promise<Object>} Template data
	 */
	static async loadTemplateCached(templateName, useCache = true) {
		if (useCache && this.templateCache.has(templateName)) {
			return this.templateCache.get(templateName)
		}

		const template = await this.loadTemplate(templateName)

		if (useCache) {
			this.templateCache.set(templateName, template)
		}

		return template
	}

	/**
	 * Clear template cache
	 */
	static clearCache() {
		this.templateCache.clear()
	}

	/**
	 * Render template with caching and usage tracking
	 * @param {string} templateName - Name of the template
	 * @param {Object} data - Data to render
	 * @returns {Promise<string>} Rendered template
	 */
	static async renderTemplateWithTracking(templateName, data) {
		const template = await this.loadTemplateCached(templateName)

		// Update usage statistics
		await this.updateTemplateUsage(templateName)

		return this.renderTemplate(template.content, data, template.engine)
	}
}

export default TemplateEngine
