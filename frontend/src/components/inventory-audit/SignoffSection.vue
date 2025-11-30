<template>
  <div class="signoff-section">
    <h4 class="text-sm font-medium text-gray-700 mb-3">{{ title || 'Signoff Status' }}</h4>
    
    <div class="space-y-3">
      <!-- Team Signoff -->
      <div 
        class="flex items-center justify-between p-3 rounded-lg border"
        :class="getSignoffClass('team')"
      >
        <div class="flex items-center gap-3">
          <div 
            class="w-8 h-8 rounded-full flex items-center justify-center"
            :class="signoffs.team_signoff ? 'bg-green-100' : 'bg-gray-100'"
          >
            <CheckCircle v-if="signoffs.team_signoff" class="w-5 h-5 text-green-600" />
            <Circle v-else class="w-5 h-5 text-gray-400" />
          </div>
          <div>
            <p class="text-sm font-medium text-gray-900">Team Lead</p>
            <p v-if="signoffs.team_signoff" class="text-xs text-gray-500">
              {{ signoffs.team_signoff_by_name || signoffs.team_signoff_by }} • {{ formatDate(signoffs.team_signoff_date) }}
            </p>
            <p v-else class="text-xs text-gray-400">Pending</p>
          </div>
        </div>
        <Button
          v-if="!signoffs.team_signoff && !readonly && canSignoff('team')"
          size="sm"
          variant="outline"
          @click="$emit('signoff', 'team')"
          :loading="signingOff === 'team'"
        >
          Sign Off
        </Button>
      </div>

      <!-- Supervisor Signoff -->
      <div 
        class="flex items-center justify-between p-3 rounded-lg border"
        :class="getSignoffClass('supervisor')"
      >
        <div class="flex items-center gap-3">
          <div 
            class="w-8 h-8 rounded-full flex items-center justify-center"
            :class="signoffs.supervisor_signoff ? 'bg-green-100' : 'bg-gray-100'"
          >
            <CheckCircle v-if="signoffs.supervisor_signoff" class="w-5 h-5 text-green-600" />
            <Circle v-else class="w-5 h-5 text-gray-400" />
          </div>
          <div>
            <p class="text-sm font-medium text-gray-900">Supervisor</p>
            <p v-if="signoffs.supervisor_signoff" class="text-xs text-gray-500">
              {{ signoffs.supervisor_signoff_by_name || signoffs.supervisor_signoff_by }} • {{ formatDate(signoffs.supervisor_signoff_date) }}
            </p>
            <p v-else class="text-xs text-gray-400">
              {{ signoffs.team_signoff ? 'Pending' : 'Awaiting Team Signoff' }}
            </p>
          </div>
        </div>
        <Button
          v-if="!signoffs.supervisor_signoff && signoffs.team_signoff && !readonly && canSignoff('supervisor')"
          size="sm"
          variant="outline"
          @click="$emit('signoff', 'supervisor')"
          :loading="signingOff === 'supervisor'"
        >
          Sign Off
        </Button>
      </div>

      <!-- Auditor Signoff -->
      <div 
        class="flex items-center justify-between p-3 rounded-lg border"
        :class="getSignoffClass('auditor')"
      >
        <div class="flex items-center gap-3">
          <div 
            class="w-8 h-8 rounded-full flex items-center justify-center"
            :class="signoffs.auditor_signoff ? 'bg-green-100' : 'bg-gray-100'"
          >
            <CheckCircle v-if="signoffs.auditor_signoff" class="w-5 h-5 text-green-600" />
            <Circle v-else class="w-5 h-5 text-gray-400" />
          </div>
          <div>
            <p class="text-sm font-medium text-gray-900">Auditor</p>
            <p v-if="signoffs.auditor_signoff" class="text-xs text-gray-500">
              {{ signoffs.auditor_signoff_by_name || signoffs.auditor_signoff_by }} • {{ formatDate(signoffs.auditor_signoff_date) }}
            </p>
            <p v-else class="text-xs text-gray-400">
              {{ signoffs.supervisor_signoff ? 'Pending' : 'Awaiting Supervisor Signoff' }}
            </p>
          </div>
        </div>
        <Button
          v-if="!signoffs.auditor_signoff && signoffs.supervisor_signoff && !readonly && canSignoff('auditor')"
          size="sm"
          variant="outline"
          @click="$emit('signoff', 'auditor')"
          :loading="signingOff === 'auditor'"
        >
          Sign Off
        </Button>
      </div>
    </div>

    <!-- Progress indicator -->
    <div class="mt-4">
      <div class="flex items-center justify-between text-xs text-gray-500 mb-1">
        <span>Signoff Progress</span>
        <span>{{ completedCount }}/3</span>
      </div>
      <div class="w-full bg-gray-200 rounded-full h-2">
        <div 
          class="h-2 rounded-full transition-all duration-300"
          :class="progressBarClass"
          :style="{ width: `${(completedCount / 3) * 100}%` }"
        ></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Button } from "frappe-ui"
import { CheckCircle, Circle } from "lucide-vue-next"
import { computed } from "vue"

const props = defineProps({
	signoffs: {
		type: Object,
		required: true,
		default: () => ({
			team_signoff: false,
			team_signoff_by: null,
			team_signoff_date: null,
			supervisor_signoff: false,
			supervisor_signoff_by: null,
			supervisor_signoff_date: null,
			auditor_signoff: false,
			auditor_signoff_by: null,
			auditor_signoff_date: null,
		}),
	},
	readonly: {
		type: Boolean,
		default: false,
	},
	title: {
		type: String,
		default: "Signoff Status",
	},
	signingOff: {
		type: String,
		default: null,
	},
	userRoles: {
		type: Array,
		default: () => [],
	},
})

defineEmits(["signoff"])

const completedCount = computed(() => {
	let count = 0
	if (props.signoffs.team_signoff) count++
	if (props.signoffs.supervisor_signoff) count++
	if (props.signoffs.auditor_signoff) count++
	return count
})

const progressBarClass = computed(() => {
	if (completedCount.value === 3) return "bg-green-500"
	if (completedCount.value >= 1) return "bg-yellow-500"
	return "bg-gray-300"
})

function getSignoffClass(role) {
	const signoff = props.signoffs[`${role}_signoff`]
	if (signoff) return "border-green-200 bg-green-50"

	// Check if this is the next pending signoff
	if (role === "team" && !props.signoffs.team_signoff)
		return "border-yellow-200 bg-yellow-50"
	if (
		role === "supervisor" &&
		props.signoffs.team_signoff &&
		!props.signoffs.supervisor_signoff
	)
		return "border-yellow-200 bg-yellow-50"
	if (
		role === "auditor" &&
		props.signoffs.supervisor_signoff &&
		!props.signoffs.auditor_signoff
	)
		return "border-yellow-200 bg-yellow-50"

	return "border-gray-200 bg-gray-50"
}

function canSignoff(role) {
	// Check user roles - this can be customized based on your role structure
	if (role === "team") {
		return (
			props.userRoles.includes("Counter") ||
			props.userRoles.includes("Team Lead") ||
			props.userRoles.includes("System Manager")
		)
	}
	if (role === "supervisor") {
		return (
			props.userRoles.includes("Supervisor") ||
			props.userRoles.includes("System Manager")
		)
	}
	if (role === "auditor") {
		return (
			props.userRoles.includes("Internal Auditor") ||
			props.userRoles.includes("Auditor") ||
			props.userRoles.includes("System Manager")
		)
	}
	return false
}

function formatDate(date) {
	if (!date) return ""
	return new Date(date).toLocaleDateString("en-US", {
		month: "short",
		day: "numeric",
		hour: "2-digit",
		minute: "2-digit",
	})
}
</script>

<style scoped>
.signoff-section {
  @apply bg-white rounded-lg p-4;
}
</style>
