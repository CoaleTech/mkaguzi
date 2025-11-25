import { session } from "@/data/session"
import { computed } from "vue"

export function usePermissions() {
	// For now, we'll use a simplified permission system
	// In a full implementation, you'd integrate with Frappe's role-based permissions
	const user = computed(() => session.user)
	const isLoggedIn = computed(() => session.isLoggedIn)

	const hasPermission = (permission) => {
		// Placeholder: authenticated users have basic permissions
		// You should implement proper Frappe role-based permission checking here
		return isLoggedIn.value
	}

	const canCreate = (doctype) => hasPermission(`${doctype}:create`)
	const canRead = (doctype) => hasPermission(`${doctype}:read`)
	const canWrite = (doctype) => hasPermission(`${doctype}:write`)
	const canDelete = (doctype) => hasPermission(`${doctype}:delete`)
	const canSubmit = (doctype) => hasPermission(`${doctype}:submit`)

	return {
		hasPermission,
		canCreate,
		canRead,
		canWrite,
		canDelete,
		canSubmit,
		user,
		isLoggedIn,
	}
}
