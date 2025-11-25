<template>
  <div class="bg-white rounded-lg border border-gray-200">
    <!-- Header -->
    <div class="px-6 py-4 border-b border-gray-200">
      <div class="flex items-center justify-between">
        <div>
          <h3 class="text-lg font-medium text-gray-900">
            Project Timeline
          </h3>
          <p class="text-sm text-gray-500 mt-1">
            Gantt chart view of audit activities and milestones
          </p>
        </div>
        <div class="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            @click="zoomOut"
            :disabled="zoomLevel <= 1"
          >
            <ZoomOutIcon class="h-4 w-4" />
          </Button>
          <span class="text-sm text-gray-500">{{ zoomLevel }}x</span>
          <Button
            variant="outline"
            size="sm"
            @click="zoomIn"
            :disabled="zoomLevel >= 4"
          >
            <ZoomInIcon class="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="sm"
            @click="exportGantt"
          >
            <DownloadIcon class="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>
    </div>

    <!-- Controls -->
    <div class="px-6 py-3 border-b border-gray-200 bg-gray-50">
      <div class="flex flex-wrap items-center gap-4">
        <!-- Date Range -->
        <div class="flex items-center space-x-2">
          <label class="text-sm font-medium text-gray-700">Period:</label>
          <Select
            v-model="selectedPeriod"
            :options="periodOptions"
            class="w-32"
          />
        </div>

        <!-- View Toggle -->
        <div class="flex items-center space-x-2">
          <label class="text-sm font-medium text-gray-700">View:</label>
          <div class="flex rounded-md">
            <button
              v-for="view in viewOptions"
              :key="view.value"
              :class="[
                'px-3 py-1 text-sm font-medium rounded-l-md first:rounded-l-md last:rounded-r-md border',
                selectedView === view.value
                  ? 'bg-blue-600 text-white border-blue-600'
                  : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
              ]"
              @click="selectedView = view.value"
            >
              {{ view.label }}
            </button>
          </div>
        </div>

        <!-- Filter -->
        <div class="flex items-center space-x-2">
          <label class="text-sm font-medium text-gray-700">Filter:</label>
          <Select
            v-model="selectedFilter"
            :options="filterOptions"
            placeholder="All Tasks"
            class="w-40"
          />
        </div>
      </div>
    </div>

    <!-- Gantt Chart -->
    <div class="relative overflow-auto" style="max-height: 600px;">
      <div class="min-w-full">
        <!-- Timeline Header -->
        <div class="sticky top-0 bg-white border-b border-gray-200 z-10">
          <div class="flex">
            <!-- Task Column Header -->
            <div class="w-80 flex-shrink-0 p-4 border-r border-gray-200">
              <div class="text-sm font-medium text-gray-700">Task</div>
            </div>
            <!-- Timeline Columns -->
            <div class="flex flex-1">
              <div
                v-for="date in timelineDates"
                :key="date.toISOString()"
                :class="[
                  'flex-shrink-0 text-center py-2 px-1 border-r border-gray-100',
                  'text-xs text-gray-500'
                ]"
                :style="{ width: `${columnWidth}px` }"
              >
                {{ formatDateLabel(date) }}
              </div>
            </div>
          </div>
        </div>

        <!-- Tasks -->
        <div
          v-for="(task, index) in filteredTasks"
          :key="task.id"
          :class="[
            'flex border-b border-gray-100 hover:bg-gray-50',
            selectedTask?.id === task.id ? 'bg-blue-50' : ''
          ]"
          @click="selectTask(task)"
        >
          <!-- Task Info -->
          <div class="w-80 flex-shrink-0 p-4 border-r border-gray-200">
            <div class="flex items-start space-x-3">
              <!-- Task Indicator -->
              <div
                :class="[
                  'w-3 h-3 rounded-full mt-1.5',
                  getTaskColor(task)
                ]"
              ></div>

              <!-- Task Details -->
              <div class="flex-1 min-w-0">
                <div class="flex items-center space-x-2">
                  <h4 class="text-sm font-medium text-gray-900 truncate">
                    {{ task.title }}
                  </h4>
                  <Badge
                    :variant="getTaskStatusVariant(task.status)"
                    size="sm"
                  >
                    {{ task.status }}
                  </Badge>
                </div>
                <p class="text-xs text-gray-500 mt-1">
                  {{ task.assignee || 'Unassigned' }}
                </p>
                <div class="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                  <span>Start: {{ formatDate(task.start_date) }}</span>
                  <span>End: {{ formatDate(task.end_date) }}</span>
                  <span>Duration: {{ getDuration(task) }} days</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Timeline Bars -->
          <div class="flex flex-1 relative">
            <!-- Grid Lines -->
            <div
              v-for="date in timelineDates"
              :key="`grid-${date.toISOString()}`"
              class="absolute top-0 bottom-0 border-r border-gray-100"
              :style="{ left: `${getDatePosition(date)}px` }"
            ></div>

            <!-- Task Bar -->
            <div
              :class="[
                'absolute top-4 h-8 rounded cursor-pointer transition-all hover:opacity-80',
                getTaskBarColor(task),
                task.status === 'completed' ? 'opacity-60' : ''
              ]"
              :style="{
                left: `${getTaskBarPosition(task)}px`,
                width: `${getTaskBarWidth(task)}px`
              }"
              @click.stop="editTask(task)"
            >
              <!-- Progress Indicator -->
              <div
                v-if="task.progress > 0"
                :class="[
                  'h-full rounded-l',
                  getTaskProgressColor(task)
                ]"
                :style="{ width: `${task.progress}%` }"
              ></div>

              <!-- Task Label -->
              <div class="absolute inset-0 flex items-center justify-center">
                <span class="text-xs font-medium text-white px-2 truncate">
                  {{ task.title }}
                </span>
              </div>

              <!-- Resize Handles -->
              <div
                v-if="canEditTask(task)"
                class="absolute left-0 top-0 bottom-0 w-2 cursor-ew-resize opacity-0 hover:opacity-100"
                @mousedown="startResize(task, 'start')"
              ></div>
              <div
                v-if="canEditTask(task)"
                class="absolute right-0 top-0 bottom-0 w-2 cursor-ew-resize opacity-0 hover:opacity-100"
                @mousedown="startResize(task, 'end')"
              ></div>
            </div>

            <!-- Dependencies -->
            <svg
              v-if="task.dependencies && task.dependencies.length > 0"
              class="absolute inset-0 pointer-events-none"
              style="z-index: 1;"
            >
              <defs>
                <marker
                  id="arrowhead"
                  markerWidth="10"
                  markerHeight="7"
                  refX="9"
                  refY="3.5"
                  orient="auto"
                >
                  <polygon
                    points="0 0, 10 3.5, 0 7"
                    fill="#6b7280"
                  />
                </marker>
              </defs>

              <line
                v-for="depId in task.dependencies"
                :key="depId"
                :x1="getDependencyStartX(depId)"
                :y1="getDependencyY(task)"
                :x2="getTaskBarPosition(task)"
                :y2="getDependencyY(task)"
                stroke="#6b7280"
                stroke-width="2"
                marker-end="url(#arrowhead)"
              />
            </svg>

            <!-- Today Line -->
            <div
              v-if="isTodayVisible"
              class="absolute top-0 bottom-0 w-0.5 bg-red-500 z-20"
              :style="{ left: `${getTodayPosition()}px` }"
            >
              <div class="absolute -top-6 left-1/2 transform -translate-x-1/2">
                <div class="bg-red-500 text-white text-xs px-2 py-1 rounded">
                  Today
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Legend -->
    <div class="px-6 py-4 border-t border-gray-200 bg-gray-50">
      <div class="flex flex-wrap items-center gap-6">
        <div class="flex items-center space-x-2">
          <div class="w-3 h-3 rounded-full bg-blue-500"></div>
          <span class="text-sm text-gray-600">Not Started</span>
        </div>
        <div class="flex items-center space-x-2">
          <div class="w-3 h-3 rounded-full bg-yellow-500"></div>
          <span class="text-sm text-gray-600">In Progress</span>
        </div>
        <div class="flex items-center space-x-2">
          <div class="w-3 h-3 rounded-full bg-green-500"></div>
          <span class="text-sm text-gray-600">Completed</span>
        </div>
        <div class="flex items-center space-x-2">
          <div class="w-3 h-3 rounded-full bg-red-500"></div>
          <span class="text-sm text-gray-600">Overdue</span>
        </div>
        <div class="flex items-center space-x-2">
          <div class="w-3 h-3 rounded-full bg-purple-500"></div>
          <span class="text-sm text-gray-600">Milestone</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Badge, Button, Select } from "frappe-ui"
import { DownloadIcon, ZoomInIcon, ZoomOutIcon } from "lucide-vue-next"
import { computed, onMounted, onUnmounted, ref } from "vue"

// Props
const props = defineProps({
	tasks: {
		type: Array,
		default: () => [],
	},
	startDate: {
		type: Date,
		default: () => new Date(),
	},
	endDate: {
		type: Date,
		default: () => new Date(Date.now() + 90 * 24 * 60 * 60 * 1000), // 90 days from now
	},
})

// Emits
const emit = defineEmits(["task-select", "task-edit", "task-resize", "export"])

// Reactive state
const zoomLevel = ref(2)
const selectedPeriod = ref("quarter")
const selectedView = ref("all")
const selectedFilter = ref("")
const selectedTask = ref(null)
const isResizing = ref(false)
const resizeData = ref(null)

// Constants
const periodOptions = [
	{ label: "Week", value: "week" },
	{ label: "Month", value: "month" },
	{ label: "Quarter", value: "quarter" },
	{ label: "Year", value: "year" },
]

const viewOptions = [
	{ value: "all", label: "All Tasks" },
	{ value: "active", label: "Active Only" },
	{ value: "overdue", label: "Overdue" },
]

const filterOptions = computed(() => {
	const options = [{ label: "All Tasks", value: "" }]
	const assignees = [
		...new Set(props.tasks.map((task) => task.assignee).filter(Boolean)),
	]
	assignees.forEach((assignee) => {
		options.push({ label: assignee, value: assignee })
	})
	return options
})

// Computed properties
const columnWidth = computed(() => {
	const baseWidth = 40
	return baseWidth * zoomLevel.value
})

const timelineDates = computed(() => {
	const dates = []
	const start = new Date(props.startDate)
	const end = new Date(props.endDate)
	const current = new Date(start)

	while (current <= end) {
		dates.push(new Date(current))
		current.setDate(current.getDate() + 1)
	}

	return dates
})

const filteredTasks = computed(() => {
	let tasks = props.tasks

	// Filter by view
	if (selectedView.value === "active") {
		tasks = tasks.filter(
			(task) => task.status === "in_progress" || task.status === "not_started",
		)
	} else if (selectedView.value === "overdue") {
		const today = new Date()
		tasks = tasks.filter(
			(task) => task.status !== "completed" && new Date(task.end_date) < today,
		)
	}

	// Filter by assignee
	if (selectedFilter.value) {
		tasks = tasks.filter((task) => task.assignee === selectedFilter.value)
	}

	// Sort by start date
	return tasks.sort((a, b) => new Date(a.start_date) - new Date(b.start_date))
})

const isTodayVisible = computed(() => {
	const today = new Date()
	return today >= props.startDate && today <= props.endDate
})

// Methods
const zoomIn = () => {
	if (zoomLevel.value < 4) zoomLevel.value++
}

const zoomOut = () => {
	if (zoomLevel.value > 1) zoomLevel.value--
}

const selectTask = (task) => {
	selectedTask.value = task
	emit("task-select", task)
}

const editTask = (task) => {
	emit("task-edit", task)
}

const canEditTask = (task) => {
	return task.status !== "completed"
}

const getTaskColor = (task) => {
	switch (task.status) {
		case "completed":
			return "bg-green-500"
		case "in_progress":
			return "bg-yellow-500"
		case "not_started":
			return "bg-blue-500"
		default:
			return "bg-gray-500"
	}
}

const getTaskStatusVariant = (status) => {
	switch (status) {
		case "completed":
			return "success"
		case "in_progress":
			return "warning"
		case "not_started":
			return "secondary"
		case "overdue":
			return "danger"
		default:
			return "secondary"
	}
}

const getTaskBarColor = (task) => {
	if (task.type === "milestone") return "bg-purple-500"
	if (task.status === "overdue") return "bg-red-500"
	return getTaskColor(task).replace("bg-", "bg-opacity-80 bg-")
}

const getTaskProgressColor = (task) => {
	return getTaskColor(task).replace("bg-", "bg-opacity-60 bg-")
}

const getDatePosition = (date) => {
	const start = props.startDate.getTime()
	const current = date.getTime()
	const total = props.endDate.getTime() - start
	const position = current - start
	return (position / total) * (timelineDates.value.length * columnWidth.value)
}

const getTaskBarPosition = (task) => {
	const taskStart = new Date(task.start_date)
	return getDatePosition(taskStart)
}

const getTaskBarWidth = (task) => {
	const start = new Date(task.start_date)
	const end = new Date(task.end_date)
	const duration = end.getTime() - start.getTime()
	const totalDuration = props.endDate.getTime() - props.startDate.getTime()
	return (
		(duration / totalDuration) *
		(timelineDates.value.length * columnWidth.value)
	)
}

const getTodayPosition = () => {
	const today = new Date()
	return getDatePosition(today)
}

const getDuration = (task) => {
	const start = new Date(task.start_date)
	const end = new Date(task.end_date)
	return Math.ceil((end - start) / (1000 * 60 * 60 * 24))
}

const formatDate = (dateString) => {
	return new Date(dateString).toLocaleDateString()
}

const formatDateLabel = (date) => {
	switch (selectedPeriod.value) {
		case "week":
			return date.toLocaleDateString("en-US", {
				weekday: "short",
				day: "numeric",
			})
		case "month":
			return date.toLocaleDateString("en-US", { day: "numeric" })
		case "quarter":
			return date.toLocaleDateString("en-US", {
				month: "short",
				day: "numeric",
			})
		case "year":
			return date.toLocaleDateString("en-US", { month: "short" })
		default:
			return date.toLocaleDateString("en-US", {
				month: "short",
				day: "numeric",
			})
	}
}

const startResize = (task, direction) => {
	isResizing.value = true
	resizeData.value = { task, direction }
}

const getDependencyStartX = (depId) => {
	const depTask = props.tasks.find((t) => t.id === depId)
	if (!depTask) return 0
	return getTaskBarPosition(depTask) + getTaskBarWidth(depTask)
}

const getDependencyY = (task) => {
	const taskIndex = filteredTasks.value.indexOf(task)
	return (taskIndex + 1) * 60 - 30 // 60px per row, center vertically
}

const exportGantt = () => {
	emit("export", {
		tasks: filteredTasks.value,
		startDate: props.startDate,
		endDate: props.endDate,
		zoomLevel: zoomLevel.value,
	})
}

// Mouse event handlers for resizing
const handleMouseMove = (event) => {
	if (!isResizing.value || !resizeData.value) return

	// Calculate new date based on mouse position
	const rect = event.currentTarget.getBoundingClientRect()
	const x = event.clientX - rect.left
	const date = getDateFromPosition(x)

	if (resizeData.value.direction === "start") {
		resizeData.value.task.start_date = date.toISOString().split("T")[0]
	} else {
		resizeData.value.task.end_date = date.toISOString().split("T")[0]
	}
}

const handleMouseUp = () => {
	if (isResizing.value && resizeData.value) {
		emit("task-resize", {
			task: resizeData.value.task,
			direction: resizeData.value.direction,
		})
	}
	isResizing.value = false
	resizeData.value = null
}

const getDateFromPosition = (x) => {
	const totalWidth = timelineDates.value.length * columnWidth.value
	const ratio = x / totalWidth
	const totalTime = props.endDate.getTime() - props.startDate.getTime()
	const timeOffset = ratio * totalTime
	return new Date(props.startDate.getTime() + timeOffset)
}

// Lifecycle
onMounted(() => {
	document.addEventListener("mousemove", handleMouseMove)
	document.addEventListener("mouseup", handleMouseUp)
})

onUnmounted(() => {
	document.removeEventListener("mousemove", handleMouseMove)
	document.removeEventListener("mouseup", handleMouseUp)
})
</script>