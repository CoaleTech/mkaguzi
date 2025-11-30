<template>
  <div class="team-member-table">
    <div class="flex items-center justify-between mb-3">
      <h4 class="text-sm font-medium text-gray-700">{{ title || 'Team Members' }}</h4>
      <Button
        v-if="!readonly"
        size="sm"
        variant="outline"
        @click="addMember"
      >
        <Plus class="w-4 h-4 mr-1" />
        Add Member
      </Button>
    </div>

    <div v-if="members.length === 0" class="text-center py-6 text-gray-500 bg-gray-50 rounded-lg">
      <Users class="w-8 h-8 mx-auto mb-2 text-gray-300" />
      <p class="text-sm">No team members assigned</p>
      <Button v-if="!readonly" size="sm" variant="ghost" class="mt-2" @click="addMember">
        Add First Member
      </Button>
    </div>

    <div v-else class="space-y-2">
      <div
        v-for="(member, index) in members"
        :key="index"
        class="flex items-center gap-3 p-3 bg-gray-50 rounded-lg group"
      >
        <!-- Avatar -->
        <div class="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
          <span class="text-sm font-medium text-blue-700">
            {{ getInitials(member.user_name || member.user) }}
          </span>
        </div>

        <!-- User Select -->
        <div class="flex-1 min-w-0">
          <FormControl
            v-if="!readonly"
            type="autocomplete"
            :options="userOptions"
            v-model="member.user"
            placeholder="Select user..."
            @change="(val) => onUserChange(index, val)"
          />
          <div v-else>
            <p class="text-sm font-medium text-gray-900 truncate">{{ member.user_name || member.user }}</p>
          </div>
        </div>

        <!-- Role Select -->
        <div class="w-32">
          <FormControl
            v-if="!readonly"
            type="select"
            :options="roleOptions"
            v-model="member.role"
            placeholder="Role"
          />
          <Badge v-else :variant="getRoleBadgeVariant(member.role)">
            {{ member.role }}
          </Badge>
        </div>

        <!-- Is Lead Checkbox -->
        <div class="flex items-center gap-1">
          <input
            type="checkbox"
            :checked="member.is_lead"
            :disabled="readonly"
            @change="(e) => member.is_lead = e.target.checked ? 1 : 0"
            class="h-4 w-4 text-blue-600 rounded border-gray-300"
          />
          <span class="text-xs text-gray-500">Lead</span>
        </div>

        <!-- Remove Button -->
        <Button
          v-if="!readonly"
          size="sm"
          variant="ghost"
          class="opacity-0 group-hover:opacity-100 transition-opacity"
          @click="removeMember(index)"
        >
          <Trash2 class="w-4 h-4 text-red-500" />
        </Button>
      </div>
    </div>

    <!-- Summary -->
    <div v-if="members.length > 0" class="mt-3 flex items-center gap-4 text-xs text-gray-500">
      <span>{{ members.length }} member{{ members.length !== 1 ? 's' : '' }}</span>
      <span v-if="leadCount > 0">{{ leadCount }} lead{{ leadCount !== 1 ? 's' : '' }}</span>
      <span v-if="roleBreakdown">{{ roleBreakdown }}</span>
    </div>
  </div>
</template>

<script setup>
import { Badge, Button, FormControl } from "frappe-ui"
import { call } from "frappe-ui"
import { Plus, Trash2, Users } from "lucide-vue-next"
import { computed, onMounted, ref } from "vue"

const props = defineProps({
	modelValue: {
		type: Array,
		default: () => [],
	},
	readonly: {
		type: Boolean,
		default: false,
	},
	title: {
		type: String,
		default: "Team Members",
	},
	roleOptions: {
		type: Array,
		default: () => [
			{ label: "Counter", value: "Counter" },
			{ label: "Verifier", value: "Verifier" },
			{ label: "Supervisor", value: "Supervisor" },
			{ label: "Auditor", value: "Auditor" },
		],
	},
})

const emit = defineEmits(["update:modelValue"])

const members = computed({
	get: () => props.modelValue || [],
	set: (val) => emit("update:modelValue", val),
})

const userOptions = ref([])

onMounted(async () => {
	await loadUsers()
})

async function loadUsers() {
	try {
		const users = await call("frappe.client.get_list", {
			doctype: "User",
			filters: { enabled: 1, user_type: "System User" },
			fields: ["name", "full_name"],
			limit_page_length: 0,
		})
		userOptions.value = users.map((u) => ({
			label: u.full_name || u.name,
			value: u.name,
		}))
	} catch (error) {
		console.error("Error loading users:", error)
	}
}

function addMember() {
	const newMembers = [
		...members.value,
		{
			user: "",
			user_name: "",
			role: "Counter",
			is_lead: 0,
		},
	]
	emit("update:modelValue", newMembers)
}

function removeMember(index) {
	const newMembers = members.value.filter((_, i) => i !== index)
	emit("update:modelValue", newMembers)
}

function onUserChange(index, userId) {
	const user = userOptions.value.find((u) => u.value === userId)
	if (user) {
		const newMembers = [...members.value]
		newMembers[index] = {
			...newMembers[index],
			user: userId,
			user_name: user.label,
		}
		emit("update:modelValue", newMembers)
	}
}

function getInitials(name) {
	if (!name) return "?"
	return name
		.split(" ")
		.map((n) => n[0])
		.join("")
		.toUpperCase()
		.slice(0, 2)
}

function getRoleBadgeVariant(role) {
	const variants = {
		Counter: "blue",
		Verifier: "green",
		Supervisor: "yellow",
		Auditor: "purple",
	}
	return variants[role] || "gray"
}

const leadCount = computed(() => {
	return members.value.filter((m) => m.is_lead).length
})

const roleBreakdown = computed(() => {
	const counts = {}
	members.value.forEach((m) => {
		if (m.role) {
			counts[m.role] = (counts[m.role] || 0) + 1
		}
	})
	return Object.entries(counts)
		.map(([role, count]) => `${count} ${role}${count !== 1 ? "s" : ""}`)
		.join(", ")
})
</script>
