<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">User Management</h1>
        <p class="text-gray-600 mt-1">
          Manage system users, roles, and permissions
        </p>
      </div>
      <div class="flex items-center space-x-3">
        <Button variant="outline">
          <DownloadIcon class="h-4 w-4 mr-2" />
          Export Users
        </Button>
        <Button @click="showAddUserModal = true">
          <PlusIcon class="h-4 w-4 mr-2" />
          Add User
        </Button>
      </div>
    </div>

    <!-- Filters and Search -->
    <div class="bg-white rounded-lg border border-gray-200 p-4">
      <div class="flex flex-col sm:flex-row gap-4">
        <div class="flex-1">
          <Input
            v-model="searchQuery"
            placeholder="Search users by name, email, or role..."
            class="w-full"
          >
            <SearchIcon class="h-4 w-4 text-gray-400" />
          </Input>
        </div>
        <div class="flex gap-2">
          <Select
            v-model="roleFilter"
            :options="roleFilterOptions"
            placeholder="All Roles"
            class="w-40"
          />
          <Select
            v-model="statusFilter"
            :options="statusFilterOptions"
            placeholder="All Status"
            class="w-40"
          />
        </div>
      </div>
    </div>

    <!-- Users Table -->
    <div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                User
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Email
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Role
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Last Login
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="user in filteredUsers" :key="user.name" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="flex-shrink-0 h-10 w-10">
                    <div class="h-10 w-10 rounded-full bg-blue-500 flex items-center justify-center">
                      <UserIcon class="h-5 w-5 text-white" />
                    </div>
                  </div>
                  <div class="ml-4">
                    <div class="text-sm font-medium text-gray-900">
                      {{ user.full_name || user.name }}
                    </div>
                    <div class="text-sm text-gray-500">
                      {{ user.username }}
                    </div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{{ user.email }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex flex-wrap gap-1">
                  <Badge
                    v-for="role in user.roles"
                    :key="role"
                    :variant="getRoleVariant(role)"
                    size="sm"
                  >
                    {{ role }}
                  </Badge>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <Badge :variant="user.enabled ? 'success' : 'secondary'">
                  {{ user.enabled ? 'Active' : 'Inactive' }}
                </Badge>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(user.last_login) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div class="flex items-center space-x-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    @click="editUser(user)"
                  >
                    <EditIcon class="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    @click="toggleUserStatus(user)"
                  >
                    <component
                      :is="user.enabled ? BanIcon : CheckCircleIcon"
                      class="h-4 w-4"
                      :class="user.enabled ? 'text-red-500' : 'text-green-500'"
                    />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    @click="resetPassword(user)"
                  >
                    <KeyIcon class="h-4 w-4" />
                  </Button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div class="bg-white px-4 py-3 border-t border-gray-200 sm:px-6">
        <div class="flex items-center justify-between">
          <div class="text-sm text-gray-700">
            Showing {{ (currentPage - 1) * pageSize + 1 }} to {{ Math.min(currentPage * pageSize, totalUsers) }} of {{ totalUsers }} users
          </div>
          <div class="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              :disabled="currentPage === 1"
              @click="currentPage--"
            >
              <ChevronLeftIcon class="h-4 w-4" />
              Previous
            </Button>
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
      </div>
    </div>

    <!-- Add/Edit User Modal -->
    <div
      v-if="showAddUserModal || showEditUserModal"
      class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50"
      @click="closeModals"
    >
      <div class="relative top-20 mx-auto p-5 border w-11/12 max-w-2xl shadow-lg rounded-md bg-white" @click.stop>
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-medium text-gray-900">
            {{ showEditUserModal ? 'Edit User' : 'Add New User' }}
          </h3>
          <Button variant="ghost" @click="closeModals">
            <XIcon class="h-5 w-5" />
          </Button>
        </div>

        <form @submit.prevent="saveUser" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Full Name</label>
              <Input
                v-model="userForm.full_name"
                placeholder="Enter full name"
                required
                class="w-full"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Username</label>
              <Input
                v-model="userForm.username"
                placeholder="Enter username"
                required
                class="w-full"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Email</label>
              <Input
                v-model="userForm.email"
                type="email"
                placeholder="Enter email address"
                required
                class="w-full"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Role</label>
              <Select
                v-model="userForm.role_profile_name"
                :options="roleOptions"
                placeholder="Select role"
                required
                class="w-full"
              />
            </div>
          </div>

          <div v-if="!showEditUserModal">
            <label class="block text-sm font-medium text-gray-700 mb-2">Password</label>
            <Input
              v-model="userForm.password"
              type="password"
              placeholder="Enter password"
              required
              class="w-full"
            />
          </div>

          <div class="flex items-center space-x-2">
            <Checkbox v-model="userForm.enabled" />
            <label class="text-sm text-gray-700">User is active</label>
          </div>

          <div class="flex justify-end space-x-3 pt-4">
            <Button variant="outline" @click="closeModals">
              Cancel
            </Button>
            <Button type="submit" :loading="saving">
              {{ showEditUserModal ? 'Update User' : 'Create User' }}
            </Button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Badge, Button, Checkbox, Input, Select } from "frappe-ui"
import {
	BanIcon,
	CheckCircleIcon,
	ChevronLeftIcon,
	ChevronRightIcon,
	DownloadIcon,
	EditIcon,
	KeyIcon,
	PlusIcon,
	SearchIcon,
	UserIcon,
	XIcon,
} from "lucide-vue-next"
import { computed, onMounted, ref } from "vue"

// Reactive state
const searchQuery = ref("")
const roleFilter = ref("")
const statusFilter = ref("")
const currentPage = ref(1)
const pageSize = ref(10)
const showAddUserModal = ref(false)
const showEditUserModal = ref(false)
const saving = ref(false)

// User data
const users = ref([])
const userForm = ref({
	name: "",
	full_name: "",
	username: "",
	email: "",
	role_profile_name: "",
	password: "",
	enabled: true,
})

// Computed properties
const filteredUsers = computed(() => {
	let filtered = users.value

	// Search filter
	if (searchQuery.value) {
		const query = searchQuery.value.toLowerCase()
		filtered = filtered.filter(
			(user) =>
				user.full_name?.toLowerCase().includes(query) ||
				user.email?.toLowerCase().includes(query) ||
				user.username?.toLowerCase().includes(query) ||
				user.roles?.some((role) => role.toLowerCase().includes(query)),
		)
	}

	// Role filter
	if (roleFilter.value) {
		filtered = filtered.filter((user) => user.roles?.includes(roleFilter.value))
	}

	// Status filter
	if (statusFilter.value) {
		const isEnabled = statusFilter.value === "active"
		filtered = filtered.filter((user) => user.enabled === isEnabled)
	}

	return filtered
})

const totalUsers = computed(() => filteredUsers.value.length)
const totalPages = computed(() => Math.ceil(totalUsers.value / pageSize.value))

// Options
const roleFilterOptions = [
	{ label: "All Roles", value: "" },
	{ label: "System Manager", value: "System Manager" },
	{ label: "Audit Manager", value: "Audit Manager" },
	{ label: "Auditor", value: "Auditor" },
	{ label: "Compliance Officer", value: "Compliance Officer" },
	{ label: "Guest", value: "Guest" },
]

const statusFilterOptions = [
	{ label: "All Status", value: "" },
	{ label: "Active", value: "active" },
	{ label: "Inactive", value: "inactive" },
]

const roleOptions = [
	{ label: "System Manager", value: "System Manager" },
	{ label: "Audit Manager", value: "Audit Manager" },
	{ label: "Auditor", value: "Auditor" },
	{ label: "Compliance Officer", value: "Compliance Officer" },
	{ label: "Guest", value: "Guest" },
]

// Methods
const fetchUsers = async () => {
	try {
		// In a real Frappe app, this would be an API call to frappe.client.get_list
		// For now, we'll simulate with mock data representing Frappe default users
		users.value = [
			{
				name: "Administrator",
				full_name: "Administrator",
				username: "Administrator",
				email: "admin@example.com",
				roles: ["System Manager"],
				enabled: true,
				last_login: new Date().toISOString(),
			},
			{
				name: "Guest",
				full_name: "Guest",
				username: "Guest",
				email: "guest@example.com",
				roles: ["Guest"],
				enabled: true,
				last_login: null,
			},
			{
				name: "john_doe",
				full_name: "John Doe",
				username: "john_doe",
				email: "john.doe@example.com",
				roles: ["Audit Manager"],
				enabled: true,
				last_login: new Date(Date.now() - 86400000).toISOString(), // 1 day ago
			},
			{
				name: "jane_smith",
				full_name: "Jane Smith",
				username: "jane_smith",
				email: "jane.smith@example.com",
				roles: ["Auditor"],
				enabled: true,
				last_login: new Date(Date.now() - 3600000).toISOString(), // 1 hour ago
			},
			{
				name: "mike_johnson",
				full_name: "Mike Johnson",
				username: "mike_johnson",
				email: "mike.johnson@example.com",
				roles: ["Compliance Officer"],
				enabled: false,
				last_login: new Date(Date.now() - 604800000).toISOString(), // 1 week ago
			},
		]
	} catch (error) {
		console.error("Error fetching users:", error)
	}
}

const getRoleVariant = (role) => {
	const variants = {
		"System Manager": "destructive",
		"Audit Manager": "default",
		Auditor: "secondary",
		"Compliance Officer": "outline",
		Guest: "secondary",
	}
	return variants[role] || "secondary"
}

const editUser = (user) => {
	userForm.value = { ...user }
	showEditUserModal.value = true
}

const toggleUserStatus = async (user) => {
	try {
		// In a real Frappe app, this would update the user via API
		user.enabled = !user.enabled
		console.log(`User ${user.name} ${user.enabled ? "enabled" : "disabled"}`)
	} catch (error) {
		console.error("Error toggling user status:", error)
	}
}

const resetPassword = async (user) => {
	if (
		confirm(
			`Are you sure you want to reset the password for ${user.full_name}?`,
		)
	) {
		try {
			// In a real Frappe app, this would call the reset password API
			console.log(`Password reset for user ${user.name}`)
			alert("Password reset email sent successfully!")
		} catch (error) {
			console.error("Error resetting password:", error)
			alert("Error resetting password. Please try again.")
		}
	}
}

const saveUser = async () => {
	saving.value = true
	try {
		if (showEditUserModal.value) {
			// Update existing user
			const index = users.value.findIndex((u) => u.name === userForm.value.name)
			if (index !== -1) {
				users.value[index] = { ...userForm.value }
			}
		} else {
			// Add new user
			users.value.push({
				...userForm.value,
				name: userForm.value.username,
				last_login: null,
			})
		}

		closeModals()
		console.log("User saved successfully")
	} catch (error) {
		console.error("Error saving user:", error)
		alert("Error saving user. Please try again.")
	} finally {
		saving.value = false
	}
}

const closeModals = () => {
	showAddUserModal.value = false
	showEditUserModal.value = false
	userForm.value = {
		name: "",
		full_name: "",
		username: "",
		email: "",
		role_profile_name: "",
		password: "",
		enabled: true,
	}
}

const formatDate = (dateString) => {
	if (!dateString) return "Never"
	return new Date(dateString).toLocaleString()
}

// Lifecycle
onMounted(() => {
	fetchUsers()
})
</script>