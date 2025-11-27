<template>
  <div class="search-result-item" @click="$emit('click', result)">
    <div class="result-header">
      <div class="result-icon">
        <component :is="getDocTypeIcon(result.doctype)" class="h-5 w-5" />
      </div>
      <div class="result-info">
        <h4 class="result-title">
          <HighlightedText :text="result.title" :search-query="searchQuery" />
        </h4>
        <p class="result-meta">
          <span class="doctype-label">{{ result.doctype }}</span>
          <span class="separator">•</span>
          <span class="result-date">{{ formatDate(result.modified) }}</span>
          <span v-if="result.status" class="separator">•</span>
          <span v-if="result.status" class="result-status" :class="getStatusClass(result.status)">
            {{ result.status }}
          </span>
        </p>
      </div>
      <div class="result-score">
        <div class="relevance-score" :title="`Relevance: ${result.score}%`">
          {{ Math.round(result.score || 0) }}%
        </div>
      </div>
    </div>
    
    <div v-if="result.description" class="result-description">
      <HighlightedText 
        :text="result.description" 
        :search-query="searchQuery"
        :max-length="200"
      />
    </div>
    
    <div v-if="result.highlights && result.highlights.length" class="result-highlights">
      <div class="highlights-label">Matches found in:</div>
      <div class="highlight-chips">
        <span 
          v-for="highlight in result.highlights.slice(0, 3)"
          :key="highlight.field"
          class="highlight-chip"
        >
          {{ highlight.field }}: 
          <HighlightedText 
            :text="highlight.snippet" 
            :search-query="searchQuery"
            :max-length="50"
          />
        </span>
      </div>
    </div>
    
    <div class="result-actions">
      <div class="result-tags">
        <span 
          v-for="tag in getTags(result)"
          :key="tag.label"
          class="result-tag"
          :class="tag.type"
        >
          <component v-if="tag.icon" :is="tag.icon" class="h-3 w-3" />
          {{ tag.label }}
        </span>
      </div>
      
      <div class="action-buttons">
        <Button
          variant="ghost"
          size="sm"
          @click.stop="viewDetails(result)"
        >
          <EyeIcon class="h-4 w-4" />
        </Button>
        <Button
          variant="ghost"
          size="sm"
          @click.stop="editRecord(result)"
        >
          <EditIcon class="h-4 w-4" />
        </Button>
        <Dropdown>
          <template #trigger>
            <Button variant="ghost" size="sm" @click.stop>
              <MoreVerticalIcon class="h-4 w-4" />
            </Button>
          </template>
          <template #content>
            <div class="dropdown-menu">
              <button @click="copyLink(result)" class="dropdown-item">
                <LinkIcon class="h-4 w-4" />
                Copy Link
              </button>
              <button @click="addToBookmarks(result)" class="dropdown-item">
                <BookmarkIcon class="h-4 w-4" />
                Bookmark
              </button>
              <button @click="exportRecord(result)" class="dropdown-item">
                <DownloadIcon class="h-4 w-4" />
                Export
              </button>
            </div>
          </template>
        </Dropdown>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Button, Dropdown } from "frappe-ui"
import {
	AlertCircleIcon,
	AlertTriangleIcon,
	BookmarkIcon,
	CalendarIcon,
	CheckCircleIcon,
	CheckSquareIcon,
	ClockIcon,
	DownloadIcon,
	EditIcon,
	EyeIcon,
	FileIcon,
	LinkIcon,
	MoreVerticalIcon,
	ShieldIcon,
	XCircleIcon,
} from "lucide-vue-next"
import { computed } from "vue"
import HighlightedText from "./HighlightedText.vue"

const props = defineProps({
	result: {
		type: Object,
		required: true,
	},
	searchQuery: {
		type: String,
		default: "",
	},
})

const emit = defineEmits(["click"])

// Methods
const getDocTypeIcon = (doctype) => {
	const iconMap = {
		"Audit Finding": AlertTriangleIcon,
		"Control Procedure": ShieldIcon,
		"Audit Test": CheckSquareIcon,
		"Audit Plan": CalendarIcon,
		Evidence: FileIcon,
	}
	return iconMap[doctype] || FileIcon
}

const formatDate = (dateString) => {
	if (!dateString) return ""
	const date = new Date(dateString)
	const now = new Date()
	const diffTime = Math.abs(now - date)
	const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))

	if (diffDays === 0) return "Today"
	if (diffDays === 1) return "Yesterday"
	if (diffDays < 7) return `${diffDays} days ago`
	if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`
	if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`

	return date.toLocaleDateString()
}

const getStatusClass = (status) => {
	const statusMap = {
		Open: "status-open",
		"In Progress": "status-progress",
		Completed: "status-completed",
		Closed: "status-closed",
		Draft: "status-draft",
		Approved: "status-approved",
		Rejected: "status-rejected",
	}
	return statusMap[status] || "status-default"
}

const getTags = (result) => {
	const tags = []

	// Priority/Severity tags
	if (result.severity) {
		const severityConfig = {
			Critical: { type: "severity-critical", icon: AlertCircleIcon },
			High: { type: "severity-high", icon: AlertTriangleIcon },
			Medium: { type: "severity-medium" },
			Low: { type: "severity-low" },
		}
		const config = severityConfig[result.severity]
		if (config) {
			tags.push({
				label: result.severity,
				type: config.type,
				icon: config.icon,
			})
		}
	}

	// Due date tags
	if (result.due_date) {
		const dueDate = new Date(result.due_date)
		const now = new Date()
		const diffDays = Math.floor((dueDate - now) / (1000 * 60 * 60 * 24))

		if (diffDays < 0) {
			tags.push({
				label: "Overdue",
				type: "due-overdue",
				icon: ClockIcon,
			})
		} else if (diffDays <= 3) {
			tags.push({
				label: "Due Soon",
				type: "due-soon",
				icon: ClockIcon,
			})
		}
	}

	// Department/Area tags
	if (result.department) {
		tags.push({
			label: result.department,
			type: "department",
		})
	}

	return tags.slice(0, 3) // Limit to 3 tags
}

const viewDetails = (result) => {
	// Navigate to detail view
	console.log("View details:", result)
}

const editRecord = (result) => {
	// Navigate to edit view
	console.log("Edit record:", result)
}

const copyLink = (result) => {
	const url = `${window.location.origin}/app/${result.doctype.toLowerCase().replace(" ", "-")}/${result.name}`
	navigator.clipboard.writeText(url)
}

const addToBookmarks = (result) => {
	// Add to bookmarks
	console.log("Add to bookmarks:", result)
}

const exportRecord = (result) => {
	// Export record
	console.log("Export record:", result)
}
</script>

<style scoped>
.search-result-item {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.2s;
}

.search-result-item:hover {
  border-color: var(--primary-color);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.result-header {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.result-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  background: var(--background-color);
  border-radius: 0.375rem;
  color: var(--primary-color);
  flex-shrink: 0;
}

.result-info {
  flex: 1;
  min-width: 0;
}

.result-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 0.25rem 0;
  line-height: 1.4;
}

.result-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--text-muted);
  margin: 0;
}

.doctype-label {
  font-weight: 500;
}

.separator {
  opacity: 0.5;
}

.result-status {
  padding: 0.125rem 0.5rem;
  border-radius: 0.75rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-open {
  background: #dbeafe;
  color: #1d4ed8;
}

.status-progress {
  background: #fef3c7;
  color: #d97706;
}

.status-completed {
  background: #d1fae5;
  color: #059669;
}

.status-closed {
  background: #e5e7eb;
  color: #374151;
}

.relevance-score {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 3rem;
  height: 1.5rem;
  background: var(--primary-light);
  color: var(--primary-color);
  border-radius: 0.75rem;
  font-size: 0.75rem;
  font-weight: 600;
}

.result-description {
  margin-bottom: 0.75rem;
  color: var(--text-muted);
  line-height: 1.5;
}

.result-highlights {
  margin-bottom: 0.75rem;
}

.highlights-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--text-muted);
  margin-bottom: 0.5rem;
}

.highlight-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.highlight-chip {
  background: var(--background-color);
  border: 1px solid var(--border-color);
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  color: var(--text-muted);
}

.result-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.result-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  flex: 1;
}

.result-tag {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.125rem 0.5rem;
  border-radius: 0.75rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.severity-critical {
  background: #fee2e2;
  color: #dc2626;
}

.severity-high {
  background: #fef3c7;
  color: #d97706;
}

.severity-medium {
  background: #dbeafe;
  color: #2563eb;
}

.severity-low {
  background: #d1fae5;
  color: #059669;
}

.due-overdue {
  background: #fee2e2;
  color: #dc2626;
}

.due-soon {
  background: #fef3c7;
  color: #d97706;
}

.department {
  background: var(--background-color);
  color: var(--text-muted);
  border: 1px solid var(--border-color);
}

.action-buttons {
  display: flex;
  gap: 0.25rem;
}

.dropdown-menu {
  padding: 0.5rem;
  min-width: 160px;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: none;
  background: none;
  text-align: left;
  border-radius: 0.25rem;
  cursor: pointer;
  transition: background-color 0.2s;
  font-size: 0.875rem;
}

.dropdown-item:hover {
  background: var(--background-color);
}

@media (max-width: 768px) {
  .result-header {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .result-meta {
    flex-wrap: wrap;
  }
  
  .result-actions {
    flex-direction: column;
    gap: 0.75rem;
    align-items: stretch;
  }
  
  .action-buttons {
    justify-content: flex-end;
  }
}
</style>