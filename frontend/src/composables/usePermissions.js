import { computed } from "vue"
import { session } from "../data/session"
import { userResource } from "../data/user"

export function usePermissions() {
    const user = userResource

    const userRole = computed(() => {
        if (!session.user) return "Audit Viewer"
        return user.data?.audit_role || "Audit Viewer"
    })

    const permissions = computed(() => {
        const role = userRole.value
        const permissionMatrix = {
            "Audit Administrator": { full: true, modules: ["audit", "risk", "findings", "compliance", "reporting", "automation"] },
            "Audit Manager": { create: true, read: true, write: true, submit: true, approve: true },
            "Lead Auditor": { create: true, read: true, write: true, submit: true },
            "Auditor": { create: true, read: true, write: true, submit: true },
            "Audit Viewer": { read: true },
            "Quality Reviewer": { read: true, write: true, approve: true },
            "Compliance Officer": { full: true, modules: ["compliance"] }
        }
        return permissionMatrix[role] || permissionMatrix["Audit Viewer"]
    })

    const hasPermission = (action, doctype) => {
        if (!doctype) return false
        if (permissions.value.full) return true
        if (!permissions.value[action]) return false

        const moduleName = doctype.split(" ")[0].toLowerCase()
        return permissions.value.modules?.includes(moduleName)
    }

    const canCreate = computed(() => (doctype) => hasPermission("create", doctype))
    const canEdit = computed(() => (doctype) => hasPermission("write", doctype))
    const canSubmit = computed(() => (doctype) => hasPermission("submit", doctype))
    const canApprove = computed(() => (doctype) => hasPermission("approve", doctype))
    const canDelete = computed(() => (doctype) => hasPermission("delete", doctype))
    const canCancel = computed(() => (doctype) => hasPermission("cancel", doctype))

    return {
        userRole,
        permissions,
        hasPermission,
        canCreate,
        canEdit,
        canSubmit,
        canApprove,
        canDelete,
        canCancel
    }
}
