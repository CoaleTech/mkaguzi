<template>
  <div class="findings-section">
    <h4 v-if="section.config?.title" class="findings-title">
      {{ section.config.title }}
    </h4>

    <div v-if="preview && !data" class="findings-preview">
      <div class="preview-info">
        <AlertTriangleIcon class="preview-icon" />
        <div class="preview-text">
          <h5>Finding List</h5>
          <p>Display audit findings grouped by: {{ section.config?.group_by || 'type' }}</p>
          <p v-if="section.config?.finding_types?.length">Types: {{ section.config.finding_types.join(', ') }}</p>
        </div>
      </div>
    </div>

    <div v-else-if="data && data.length > 0" class="findings-list">
      <div v-for="finding in filteredFindings" :key="finding.name" class="finding-item">
        <div class="finding-header">
          <div class="finding-info">
            <Badge :variant="getSeverityVariant(finding.severity)" class="severity-badge">
              {{ finding.severity || 'Medium' }}
            </Badge>
            <h5 class="finding-title">{{ finding.finding_title || finding.name }}</h5>
          </div>
          <Badge variant="secondary">{{ finding.finding_type }}</Badge>
        </div>
        
        <p class="finding-description">{{ finding.description || 'No description available' }}</p>
        
        <div class="finding-details">
          <div class="detail-item">
            <span class="detail-label">Status:</span>
            <Badge :variant="getStatusVariant(finding.status)">{{ finding.status || 'Open' }}</Badge>
          </div>
          <div class="detail-item">
            <span class="detail-label">Risk Level:</span>
            <span class="detail-value">{{ finding.risk_level || 'Medium' }}</span>
          </div>
          <div v-if="finding.due_date" class="detail-item">
            <span class="detail-label">Due Date:</span>
            <span class="detail-value">{{ formatDate(finding.due_date) }}</span>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="empty-findings">
      <AlertTriangleIcon class="empty-icon" />
      <p>No findings available</p>
    </div>
  </div>
</template>

<script setup>
import { Badge } from "frappe-ui"
import { AlertTriangleIcon } from "lucide-vue-next"
import { computed } from "vue"

const props = defineProps({
	section: {
		type: Object,
		required: true,
	},
	data: {
		type: Array,
		default: () => [],
	},
	preview: {
		type: Boolean,
		default: true,
	},
})

const filteredFindings = computed(() => {
	let findings = props.data || []

	// Filter by finding types
	if (props.section.config?.finding_types?.length) {
		findings = findings.filter((f) =>
			props.section.config.finding_types.includes(f.finding_type),
		)
	}

	// Filter by status
	if (props.section.config?.status_filter) {
		findings = findings.filter(
			(f) => f.status === props.section.config.status_filter,
		)
	}

	// Filter by severity
	if (props.section.config?.severity_filter) {
		findings = findings.filter(
			(f) => f.severity === props.section.config.severity_filter,
		)
	}

	return findings
})

const getSeverityVariant = (severity) => {
	const variants = {
		Critical: "danger",
		High: "warning",
		Medium: "secondary",
		Low: "success",
	}
	return variants[severity] || "secondary"
}

const getStatusVariant = (status) => {
	const variants = {
		Open: "warning",
		"In Progress": "secondary",
		Resolved: "success",
		Closed: "secondary",
	}
	return variants[status] || "secondary"
}

const formatDate = (date) => {
	return new Date(date).toLocaleDateString()
}
</script>

<style scoped>
.findings-section {
  margin: 1.5rem 0;
}

.findings-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 1rem 0;
}

.findings-preview {
  padding: 2rem;
  border: 2px dashed #d1d5db;
  border-radius: 0.5rem;
  background: #f9fafb;
}

.preview-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  text-align: left;
}

.preview-icon {
  width: 3rem;
  height: 3rem;
  color: #6b7280;
  flex-shrink: 0;
}

.preview-text h5 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 0.5rem 0;
}

.preview-text p {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0.25rem 0;
}

.findings-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.finding-item {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.finding-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.finding-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.finding-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.severity-badge {
  font-size: 0.75rem;
  font-weight: 600;
}

.finding-description {
  color: #4b5563;
  line-height: 1.5;
  margin-bottom: 1rem;
}

.finding-details {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.detail-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
}

.detail-value {
  font-size: 0.875rem;
  color: #1f2937;
}

.empty-findings {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 2rem;
  text-align: center;
  color: #6b7280;
  border: 2px dashed #d1d5db;
  border-radius: 0.5rem;
  background: #f9fafb;
}

.empty-icon {
  width: 3rem;
  height: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

/* Responsive */
@media (max-width: 768px) {
  .finding-header {
    flex-direction: column;
    gap: 0.5rem;
    align-items: flex-start;
  }
  
  .finding-details {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>