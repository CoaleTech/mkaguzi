<template>
  <div class="bg-white rounded-lg border border-gray-200">
    <!-- Header -->
    <div class="px-6 py-4 border-b border-gray-200">
      <div class="flex items-center justify-between">
        <div>
          <h3 class="text-lg font-medium text-gray-900">
            Approval Workflow
          </h3>
          <p class="text-sm text-gray-500 mt-1">
            {{ workflow.description || 'Manage approval process for this item' }}
          </p>
        </div>
        <div class="flex items-center space-x-2">
          <Badge
            :variant="statusVariant"
            class="capitalize"
          >
            {{ workflow.status }}
          </Badge>
        </div>
      </div>
    </div>

    <!-- Workflow Steps -->
    <div class="px-6 py-4">
      <div class="space-y-4">
        <div
          v-for="(step, index) in workflow.steps"
          :key="step.id"
          class="relative"
        >
          <!-- Connector Line -->
          <div
            v-if="index < workflow.steps.length - 1"
            class="absolute left-6 top-12 w-0.5 h-8 bg-gray-200"
            :class="{ 'bg-green-400': step.status === 'approved' }"
          ></div>

          <!-- Step Card -->
          <div
            :class="[
              'relative flex items-start space-x-4 p-4 rounded-lg border transition-colors',
              step.status === 'pending' ? 'border-blue-200 bg-blue-50' :
              step.status === 'approved' ? 'border-green-200 bg-green-50' :
              step.status === 'rejected' ? 'border-red-200 bg-red-50' :
              'border-gray-200 bg-white'
            ]"
          >
            <!-- Step Indicator -->
            <div
              :class="[
                'flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center',
                step.status === 'pending' ? 'bg-blue-100 text-blue-600' :
                step.status === 'approved' ? 'bg-green-100 text-green-600' :
                step.status === 'rejected' ? 'bg-red-100 text-red-600' :
                'bg-gray-100 text-gray-400'
              ]"
            >
              <CheckCircleIcon
                v-if="step.status === 'approved'"
                class="h-6 w-6"
              />
              <XCircleIcon
                v-if="step.status === 'rejected'"
                class="h-6 w-6"
              />
              <ClockIcon
                v-if="step.status === 'pending'"
                class="h-6 w-6"
              />
              <UserIcon
                v-else
                class="h-6 w-6"
              />
            </div>

            <!-- Step Content -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center justify-between">
                <div>
                  <h4 class="text-sm font-medium text-gray-900">
                    {{ step.title }}
                  </h4>
                  <p class="text-sm text-gray-500">
                    {{ step.description }}
                  </p>
                </div>
                <div class="flex items-center space-x-2">
                  <span class="text-xs text-gray-400">
                    Step {{ index + 1 }} of {{ workflow.steps.length }}
                  </span>
                </div>
              </div>

              <!-- Assigned User -->
              <div class="mt-2 flex items-center space-x-2">
                <UserIcon class="h-4 w-4 text-gray-400" />
                <span class="text-sm text-gray-600">
                  {{ step.assigned_to || 'Unassigned' }}
                </span>
                <Badge
                  v-if="step.role"
                  variant="outline"
                  size="sm"
                >
                  {{ step.role }}
                </Badge>
              </div>

              <!-- Action Buttons -->
              <div v-if="canActOnStep(step)" class="mt-3 flex space-x-2">
                <Button
                  size="sm"
                  variant="outline"
                  @click="approveStep(step)"
                  :loading="step.loading"
                >
                  <CheckIcon class="h-4 w-4 mr-1" />
                  Approve
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  color="red"
                  @click="rejectStep(step)"
                  :loading="step.loading"
                >
                  <XIcon class="h-4 w-4 mr-1" />
                  Reject
                </Button>
                <Button
                  v-if="step.can_reassign"
                  size="sm"
                  variant="ghost"
                  @click="reassignStep(step)"
                >
                  <UserPlusIcon class="h-4 w-4 mr-1" />
                  Reassign
                </Button>
              </div>

              <!-- Comments -->
              <div v-if="step.comments && step.comments.length > 0" class="mt-3">
                <div class="space-y-2">
                  <div
                    v-for="comment in step.comments"
                    :key="comment.id"
                    class="bg-gray-50 rounded p-3"
                  >
                    <div class="flex items-start space-x-2">
                      <UserIcon class="h-4 w-4 text-gray-400 mt-0.5" />
                      <div class="flex-1">
                        <div class="flex items-center space-x-2">
                          <span class="text-sm font-medium text-gray-900">
                            {{ comment.author }}
                          </span>
                          <span class="text-xs text-gray-500">
                            {{ formatDate(comment.created_at) }}
                          </span>
                        </div>
                        <p class="text-sm text-gray-700 mt-1">
                          {{ comment.content }}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Add Comment -->
              <div v-if="canCommentOnStep(step)" class="mt-3">
                <div class="flex space-x-2">
                  <Input
                    v-model="step.newComment"
                    placeholder="Add a comment..."
                    class="flex-1"
                    @keyup.enter="addComment(step)"
                  />
                  <Button
                    size="sm"
                    @click="addComment(step)"
                    :disabled="!step.newComment?.trim()"
                  >
                    <MessageCircleIcon class="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Workflow Actions -->
    <div v-if="canManageWorkflow" class="px-6 py-4 border-t border-gray-200 bg-gray-50">
      <div class="flex justify-between items-center">
        <div class="text-sm text-gray-600">
          Workflow managed by {{ workflow.created_by }}
        </div>
        <div class="flex space-x-2">
          <Button
            v-if="workflow.status === 'draft'"
            size="sm"
            @click="startWorkflow"
          >
            Start Workflow
          </Button>
          <Button
            v-if="workflow.status === 'in_progress'"
            size="sm"
            variant="outline"
            @click="pauseWorkflow"
          >
            Pause
          </Button>
          <Button
            v-if="workflow.can_cancel"
            size="sm"
            variant="outline"
            color="red"
            @click="cancelWorkflow"
          >
            Cancel
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { usePermissions } from "@/composables/usePermissions"
import { Badge, Button, Input } from "frappe-ui"
import {
	CheckCircleIcon,
	CheckIcon,
	ClockIcon,
	MessageCircleIcon,
	UserIcon,
	UserPlusIcon,
	XCircleIcon,
	XIcon,
} from "lucide-vue-next"
import { computed, onMounted, ref } from "vue"

// Props
const props = defineProps({
	workflow: {
		type: Object,
		required: true,
	},
	currentUser: {
		type: Object,
		default: () => ({}),
	},
})

// Emits
const emit = defineEmits([
	"approve-step",
	"reject-step",
	"reassign-step",
	"add-comment",
	"start-workflow",
	"pause-workflow",
	"cancel-workflow",
])

// Composables
const { hasPermission } = usePermissions()

// Computed properties
const statusVariant = computed(() => {
	switch (props.workflow.status) {
		case "draft":
			return "secondary"
		case "in_progress":
			return "primary"
		case "completed":
			return "success"
		case "cancelled":
			return "danger"
		case "paused":
			return "warning"
		default:
			return "secondary"
	}
})

const canManageWorkflow = computed(() => {
	return (
		hasPermission("manage_workflows") ||
		props.workflow.created_by === props.currentUser.email
	)
})

const canActOnStep = (step) => {
	return (
		step.status === "pending" &&
		(step.assigned_to === props.currentUser.email ||
			hasPermission("approve_any_step"))
	)
}

const canCommentOnStep = (step) => {
	return (
		props.workflow.status !== "cancelled" &&
		(canActOnStep(step) || hasPermission("comment_on_workflows"))
	)
}

// Methods
const approveStep = async (step) => {
	step.loading = true
	try {
		await emit("approve-step", {
			stepId: step.id,
			workflowId: props.workflow.id,
		})
	} finally {
		step.loading = false
	}
}

const rejectStep = async (step) => {
	step.loading = true
	try {
		await emit("reject-step", {
			stepId: step.id,
			workflowId: props.workflow.id,
		})
	} finally {
		step.loading = false
	}
}

const reassignStep = (step) => {
	emit("reassign-step", {
		stepId: step.id,
		workflowId: props.workflow.id,
	})
}

const addComment = async (step) => {
	if (!step.newComment?.trim()) return

	const comment = {
		content: step.newComment.trim(),
		stepId: step.id,
		workflowId: props.workflow.id,
	}

	step.newComment = ""
	await emit("add-comment", comment)
}

const startWorkflow = () => {
	emit("start-workflow", props.workflow.id)
}

const pauseWorkflow = () => {
	emit("pause-workflow", props.workflow.id)
}

const cancelWorkflow = () => {
	emit("cancel-workflow", props.workflow.id)
}

const formatDate = (dateString) => {
	if (!dateString) return ""
	return new Date(dateString).toLocaleDateString()
}

// Initialize step comments
onMounted(() => {
	props.workflow.steps.forEach((step) => {
		if (!step.comments) step.comments = []
		if (!step.newComment) step.newComment = ""
	})
})
</script>