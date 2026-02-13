<template>
  <div class="risk-list">
    <div class="list-header">
      <div class="list-controls">
        <div class="selection-controls">
          <input
            type="checkbox"
            :checked="allSelected"
            :indeterminate="someSelected"
            @change="toggleSelectAll"
          />
          <span v-if="selectedRisks.length > 0">
            {{ selectedRisks.length }} selected
          </span>
        </div>
        
        <div class="sort-controls">
          <FormControl
            type="select"
            v-model="sortBy"
            :options="sortOptions"
            placeholder="Sort by..."
            size="sm"
          />
          <Button
            variant="outline"
            size="sm"
            @click="sortOrder = sortOrder === 'asc' ? 'desc' : 'asc'"
          >
            <ArrowUpIcon v-if="sortOrder === 'asc'" class="h-4 w-4" />
            <ArrowDownIcon v-else class="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading risks...</p>
    </div>

    <div v-else-if="sortedRisks.length === 0" class="empty-state">
      <AlertTriangleIcon class="h-16 w-16 text-gray-300" />
      <h3>No Risks Found</h3>
      <p>No risks match the current filters</p>
    </div>

    <div v-else class="risks-container">
      <div
        v-for="risk in paginatedRisks"
        :key="risk.name"
        class="risk-item"
        :class="{
          'selected': selectedRisks.includes(risk.name),
          'high-priority': getRiskLevel(risk.likelihood, risk.impact).priority >= 3
        }"
        @click="$emit('risk-click', risk)"
      >
        <div class="risk-checkbox">
          <input
            type="checkbox"
            :checked="selectedRisks.includes(risk.name)"
            @click.stop
            @change="$emit('risk-select', risk.name)"
          />
        </div>

        <div class="risk-priority">
          <div
            class="priority-indicator"
            :style="{ backgroundColor: getRiskLevel(risk.likelihood, risk.impact).color }"
            :title="getRiskLevel(risk.likelihood, risk.impact).level"
          ></div>
        </div>

        <div class="risk-category">
          <div class="category-icon">
            <component 
              :is="getCategoryIcon(risk.category)" 
              class="h-5 w-5"
              :style="{ color: getCategoryColor(risk.category) }"
            />
          </div>
        </div>

        <div class="risk-content">
          <div class="risk-header">
            <h4 class="risk-title">{{ risk.title }}</h4>
            <div class="risk-badges">
              <span class="risk-level-badge" :class="getRiskLevel(risk.likelihood, risk.impact).level.toLowerCase()">
                {{ getRiskLevel(risk.likelihood, risk.impact).level }}
              </span>
              <span class="status-badge" :class="risk.status.toLowerCase().replace(' ', '-')">
                {{ risk.status }}
              </span>
            </div>
          </div>

          <p class="risk-description">{{ risk.description }}</p>

          <div class="risk-details">
            <div class="detail-item">
              <span class="detail-label">Owner:</span>
              <span class="detail-value">{{ risk.risk_owner || 'Unassigned' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Likelihood:</span>
              <span class="detail-value">{{ risk.likelihood }}/5</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Impact:</span>
              <span class="detail-value">{{ risk.impact }}/5</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Score:</span>
              <span class="detail-value score">{{ risk.likelihood * risk.impact }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Created:</span>
              <span class="detail-value">{{ formatDate(risk.creation) }}</span>
            </div>
          </div>

          <div v-if="risk.mitigation_count > 0" class="mitigation-info">
            <CheckCircleIcon class="h-4 w-4" />
            <span>{{ risk.mitigation_count }} mitigation action(s)</span>
          </div>
        </div>

        <div class="risk-actions">
          <Dropdown :options="getRiskActions(risk)">
            <template #default="{ toggle }">
              <Button
                variant="ghost"
                size="sm"
                @click.stop="toggle()"
              >
                <MoreVerticalIcon class="h-4 w-4" />
              </Button>
            </template>
          </Dropdown>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="pagination">
      <Button
        variant="outline"
        size="sm"
        :disabled="currentPage === 1"
        @click="currentPage--"
      >
        <ChevronLeftIcon class="h-4 w-4" />
        Previous
      </Button>
      
      <div class="page-info">
        Page {{ currentPage }} of {{ totalPages }} ({{ sortedRisks.length }} total)
      </div>
      
      <Button
        variant="outline"
        size="sm"
        :disabled="currentPage === totalPages"
        @click="currentPage++"
      >
        Next
        <ChevronRightIcon class="h-4 w-4" />
      </Button>
    </div>
  </div>
</template>

<script setup>
import { Button, Dropdown, FormControl } from "frappe-ui"
import {
	AlertTriangleIcon,
	ArrowDownIcon,
	ArrowUpIcon,
	CheckCircleIcon,
	ChevronLeftIcon,
	ChevronRightIcon,
	CopyIcon,
	DollarSignIcon,
	EditIcon,
	EyeIcon,
	MonitorIcon,
	MoreVerticalIcon,
	SettingsIcon,
	ShieldIcon,
	TargetIcon,
	TrashIcon,
} from "lucide-vue-next"
import { computed, ref } from "vue"

const props = defineProps({
	risks: {
		type: Array,
		default: () => [],
	},
	categories: {
		type: Array,
		default: () => [],
	},
	selectedRisks: {
		type: Array,
		default: () => [],
	},
	loading: {
		type: Boolean,
		default: false,
	},
})

const emit = defineEmits([
	"risk-click",
	"risk-select",
	"risk-edit",
	"risk-delete",
	"risk-duplicate",
])

// Local state
const sortBy = ref("priority")
const sortOrder = ref("desc")
const currentPage = ref(1)
const itemsPerPage = 10

// Sort options
const sortOptions = [
	{ label: "Risk Level (Priority)", value: "priority" },
	{ label: "Title", value: "title" },
	{ label: "Created Date", value: "creation" },
	{ label: "Risk Score", value: "score" },
	{ label: "Status", value: "status" },
	{ label: "Owner", value: "risk_owner" },
]

// Category configuration
const categoryConfig = {
	operational: { icon: SettingsIcon, color: "#3b82f6" },
	financial: { icon: DollarSignIcon, color: "#10b981" },
	compliance: { icon: ShieldIcon, color: "#f59e0b" },
	strategic: { icon: TargetIcon, color: "#525252" },
	reputational: { icon: AlertTriangleIcon, color: "#ef4444" },
	technology: { icon: MonitorIcon, color: "#06b6d4" },
}

// Computed
const allSelected = computed(() => {
	return (
		props.risks.length > 0 && props.selectedRisks.length === props.risks.length
	)
})

const someSelected = computed(() => {
	return (
		props.selectedRisks.length > 0 &&
		props.selectedRisks.length < props.risks.length
	)
})

const sortedRisks = computed(() => {
	const sorted = [...props.risks]

	sorted.sort((a, b) => {
		let aValue, bValue

		switch (sortBy.value) {
			case "priority":
				aValue = getRiskLevel(a.likelihood, a.impact).priority
				bValue = getRiskLevel(b.likelihood, b.impact).priority
				break
			case "score":
				aValue = a.likelihood * a.impact
				bValue = b.likelihood * b.impact
				break
			case "title":
				aValue = a.title?.toLowerCase() || ""
				bValue = b.title?.toLowerCase() || ""
				break
			case "creation":
				aValue = new Date(a.creation)
				bValue = new Date(b.creation)
				break
			default:
				aValue = a[sortBy.value] || ""
				bValue = b[sortBy.value] || ""
		}

		if (aValue < bValue) return sortOrder.value === "asc" ? -1 : 1
		if (aValue > bValue) return sortOrder.value === "asc" ? 1 : -1
		return 0
	})

	return sorted
})

const totalPages = computed(() => {
	return Math.ceil(sortedRisks.value.length / itemsPerPage)
})

const paginatedRisks = computed(() => {
	const start = (currentPage.value - 1) * itemsPerPage
	const end = start + itemsPerPage
	return sortedRisks.value.slice(start, end)
})

// Methods
const getRiskLevel = (likelihood, impact) => {
	const score = likelihood * impact
	if (score <= 5) return { level: "Low", color: "#22c55e", priority: 1 }
	if (score <= 12) return { level: "Medium", color: "#eab308", priority: 2 }
	if (score <= 20) return { level: "High", color: "#f97316", priority: 3 }
	return { level: "Critical", color: "#ef4444", priority: 4 }
}

const getCategoryIcon = (category) => {
	return categoryConfig[category]?.icon || AlertTriangleIcon
}

const getCategoryColor = (category) => {
	return categoryConfig[category]?.color || "#6b7280"
}

const formatDate = (dateString) => {
	return new Date(dateString).toLocaleDateString()
}

const toggleSelectAll = () => {
	if (allSelected.value) {
		// Deselect all
		props.risks.forEach((risk) => {
			if (props.selectedRisks.includes(risk.name)) {
				emit("risk-select", risk.name)
			}
		})
	} else {
		// Select all
		props.risks.forEach((risk) => {
			if (!props.selectedRisks.includes(risk.name)) {
				emit("risk-select", risk.name)
			}
		})
	}
}

const getRiskActions = (risk) => {
	return [
		{
			label: "View Details",
			icon: EyeIcon,
			onClick: () => emit("risk-click", risk),
		},
		{
			label: "Edit Risk",
			icon: EditIcon,
			onClick: () => emit("risk-edit", risk),
		},
		{
			label: "Duplicate Risk",
			icon: CopyIcon,
			onClick: () => emit("risk-duplicate", risk),
		},
		{
			label: "Delete Risk",
			icon: TrashIcon,
			onClick: () => emit("risk-delete", risk),
			class: "text-red-600",
		},
	]
}
</script>

<style scoped>
.risk-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
}

.list-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  gap: 1rem;
}

.selection-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--text-muted);
}

.sort-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 3rem;
  text-align: center;
}

.loading-spinner {
  width: 2rem;
  height: 2rem;
  border: 2px solid var(--border-color);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 3rem;
  text-align: center;
  color: var(--text-muted);
}

.empty-state h3 {
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
}

.risks-container {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.risk-item {
  display: grid;
  grid-template-columns: auto auto auto 1fr auto;
  gap: 1rem;
  padding: 1.5rem;
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
  align-items: flex-start;
}

.risk-item:hover {
  border-color: var(--primary-color);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.risk-item.selected {
  background: var(--primary-light);
  border-color: var(--primary-color);
}

.risk-item.high-priority {
  border-left: 4px solid #f97316;
}

.risk-item.high-priority.critical {
  border-left-color: #ef4444;
}

.priority-indicator {
  width: 0.75rem;
  height: 0.75rem;
  border-radius: 50%;
  margin-top: 0.25rem;
}

.category-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  background: var(--background-color);
  border-radius: 0.375rem;
  margin-top: 0.25rem;
}

.risk-content {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  min-width: 0;
}

.risk-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.risk-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
}

.risk-badges {
  display: flex;
  gap: 0.5rem;
  flex-shrink: 0;
}

.risk-level-badge,
.status-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 0.75rem;
  font-size: 0.75rem;
  font-weight: 600;
  white-space: nowrap;
}

.risk-level-badge.critical {
  background: #fef2f2;
  color: #dc2626;
}

.risk-level-badge.high {
  background: #fff7ed;
  color: #ea580c;
}

.risk-level-badge.medium {
  background: #fefce8;
  color: #ca8a04;
}

.risk-level-badge.low {
  background: #f0fdf4;
  color: #16a34a;
}

.status-badge.open {
  background: #fef2f2;
  color: #dc2626;
}

.status-badge.in-progress {
  background: #fff7ed;
  color: #ea580c;
}

.status-badge.under-review {
  background: #fefce8;
  color: #ca8a04;
}

.status-badge.closed {
  background: #f0fdf4;
  color: #16a34a;
}

.risk-description {
  color: var(--text-muted);
  line-height: 1.5;
  margin: 0;
}

.risk-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 0.75rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.detail-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--text-muted);
}

.detail-value {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-color);
}

.detail-value.score {
  color: var(--primary-color);
}

.mitigation-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--primary-color);
}

.risk-actions {
  display: flex;
  align-items: flex-start;
}

.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
}

.page-info {
  font-size: 0.875rem;
  color: var(--text-muted);
}

@media (max-width: 768px) {
  .risk-item {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .risk-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .risk-details {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .list-controls {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .pagination {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>