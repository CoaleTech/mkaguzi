<template>
  <div class="base-template" :class="templateClasses">
    <!-- Header Section -->
    <div v-if="showHeader" class="template-header">
      <slot name="header" :data="templateData" :config="config">
        <div class="default-header">
          <h1 v-if="config.title" class="template-title">{{ config.title }}</h1>
          <div v-if="config.subtitle" class="template-subtitle">{{ config.subtitle }}</div>
        </div>
      </slot>
    </div>

    <!-- Content Section -->
    <div class="template-content">
      <slot name="content" :data="templateData" :config="config">
        <!-- Default content structure -->
        <div class="content-sections">
          <div
            v-for="(section, index) in config.sections"
            :key="index"
            class="content-section"
            :class="`section-${section.id || section}`"
          >
            <slot :name="`section-${section.id || section}`" :data="templateData" :section="section">
              <div class="default-section">
                <h2 class="section-title">{{ section.title || section }}</h2>
                <div class="section-content">
                  {{ templateData[section.id || section] || `Content for ${section.title || section}` }}
                </div>
              </div>
            </slot>
          </div>
        </div>
      </slot>
    </div>

    <!-- Footer Section -->
    <div v-if="showFooter" class="template-footer">
      <slot name="footer" :data="templateData" :config="config">
        <div class="default-footer">
          <div v-if="config.footerText" class="footer-text">{{ config.footerText }}</div>
          <div v-if="config.showTimestamp" class="footer-timestamp">
            Generated on {{ new Date().toLocaleString() }}
          </div>
        </div>
      </slot>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue"

const props = defineProps({
	templateData: {
		type: Object,
		default: () => ({}),
	},
	config: {
		type: Object,
		default: () => ({
			title: "",
			subtitle: "",
			sections: [],
			showHeader: true,
			showFooter: true,
			footerText: "",
			showTimestamp: true,
			theme: "default",
			layout: "standard",
		}),
	},
})

const emit = defineEmits(["section-click", "header-click", "footer-click"])

const showHeader = computed(() => {
	return props.config.showHeader !== false
})

const showFooter = computed(() => {
	return props.config.showFooter !== false
})

const templateClasses = computed(() => {
	return [
		`template-theme-${props.config.theme || "default"}`,
		`template-layout-${props.config.layout || "standard"}`,
		{ "has-header": showHeader.value },
		{ "has-footer": showFooter.value },
	]
})
</script>

<style scoped>
.base-template {
  min-height: 100vh;
  background-color: white;
}

.template-header {
  border-bottom: 1px solid #e5e7eb;
  background-color: #f9fafb;
  padding: 1.5rem;
}

.template-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #111827;
  margin-bottom: 0.5rem;
}

.template-subtitle {
  font-size: 1.125rem;
  color: #4b5563;
}

.template-content {
  flex: 1;
  padding: 1.5rem;
}

.content-sections {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.content-section {
  background-color: white;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
  padding: 1.5rem;
}

.section-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.section-content {
  color: #374151;
  line-height: 1.625;
}

.template-footer {
  border-top: 1px solid #e5e7eb;
  background-color: #f9fafb;
  padding: 1rem 1.5rem;
  margin-top: 2rem;
}

.default-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.875rem;
  color: #4b5563;
}

.footer-text {
  flex: 1;
}

.footer-timestamp {
  text-align: right;
}

/* Theme variants */
.template-theme-professional .template-header {
  background-color: #eff6ff;
  border-color: #bfdbfe;
}

.template-theme-professional .template-title {
  color: #1e3a8a;
}

.template-theme-professional .section-title {
  color: #1e40af;
  border-color: #bfdbfe;
}

.template-theme-compact .template-content {
  padding: 1rem;
}

.template-theme-compact .content-section {
  padding: 1rem;
}

.template-theme-print .base-template {
  background-color: white;
  color: black;
}

.template-theme-print .content-section {
  border: none;
  box-shadow: none;
}
</style>