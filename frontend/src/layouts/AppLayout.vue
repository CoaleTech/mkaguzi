<template>
  <div class="flex h-screen w-full flex-col bg-surface-white">
    <!-- Top Header Bar -->
    <header class="flex h-16 items-center justify-between border-b border-outline-gray-200 bg-surface-white px-6 shadow-sm">
      <!-- Organization Logo -->
      <div class="flex items-center space-x-4">
        <img
          src="https://raw.githubusercontent.com/frappe/erpnext/develop/erpnext/public/images/erpnext-logo.svg"
          alt="Organization Logo"
          class="h-8 w-8"
        />
        <div>
          <h1 class="text-lg font-semibold text-gray-900">Internal Audit Management</h1>
          <p class="text-sm text-gray-500">{{ session.user }}</p>
        </div>
      </div>

      <!-- Header Actions -->
      <div class="flex items-center space-x-4">


        <!-- Notifications Bell -->
        <Button variant="ghost" @click="toggleNotifications">
          <BellIcon class="h-5 w-5" />
          <Badge v-if="notificationCount > 0" variant="destructive" class="ml-1">
            {{ notificationCount }}
          </Badge>
        </Button>

        <!-- Theme Toggle -->
        <Button variant="ghost" @click="toggleTheme">
          <MoonIcon v-if="isDarkTheme" class="h-5 w-5" />
          <SunIcon v-else class="h-5 w-5" />
        </Button>

        <!-- Settings Dropdown -->
        <Dropdown :options="settingsOptions">
          <Button variant="ghost">
            <SettingsIcon class="h-5 w-5" />
          </Button>
        </Dropdown>

        <!-- User Menu -->
        <Dropdown :options="userMenuOptions">
          <Avatar :label="session.user" size="sm" />
        </Dropdown>
      </div>
    </header>

    <div class="flex flex-1 overflow-hidden">
      <!-- Sidebar Navigation -->
      <aside
        :class="[
          'flex flex-col border-r border-outline-gray-200 bg-surface-white transition-all duration-300',
          isSidebarCollapsed ? 'w-16' : 'w-64'
        ]"
      >
        <!-- Sidebar Header -->
        <div class="flex h-16 items-center justify-between px-4">
          <h2
            v-if="!isSidebarCollapsed"
            class="text-sm font-semibold text-gray-900"
          >
            Navigation
          </h2>
          <Button
            variant="ghost"
            size="sm"
            @click="toggleSidebar"
          >
            <ChevronLeftIcon
              :class="[
                'h-4 w-4 transition-transform',
                isSidebarCollapsed ? 'rotate-180' : ''
              ]"
            />
          </Button>
        </div>

        <!-- Navigation Menu -->
        <nav class="flex-1 space-y-1 px-2 py-4">
          <!-- Dashboard -->
          <router-link
            to="/"
            class="nav-item"
            :class="{ 'nav-item-active': $route.path === '/' }"
          >
            <HomeIcon class="h-5 w-5" />
            <span v-if="!isSidebarCollapsed">Dashboard</span>
          </router-link>

          <!-- Audit Planning -->
          <div class="nav-group">
            <div
              class="nav-group-header"
              @click="toggleNavGroup('auditPlanning')"
            >
              <div class="flex items-center space-x-2">
                <FileTextIcon class="h-5 w-5" />
                <span v-if="!isSidebarCollapsed">Audit Planning</span>
              </div>
              <ChevronDownIcon
                v-if="!isSidebarCollapsed"
                :class="[
                  'h-4 w-4 transition-transform',
                  expandedGroups.auditPlanning ? 'rotate-180' : ''
                ]"
              />
            </div>
            <div v-if="expandedGroups.auditPlanning || isSidebarCollapsed" class="nav-group-items">
              <router-link
                to="/audit-planning/universe"
                class="nav-subitem"
                :class="{ 'nav-subitem-active': $route.path === '/audit-planning/universe' }"
              >
                <GlobeIcon class="h-4 w-4" />
                <span v-if="!isSidebarCollapsed">Audit Universe</span>
              </router-link>
              <router-link
                to="/audit-planning/risk-assessment"
                class="nav-subitem"
                :class="{ 'nav-subitem-active': $route.path === '/audit-planning/risk-assessment' }"
              >
                <AlertTriangleIcon class="h-4 w-4" />
                <span v-if="!isSidebarCollapsed">Risk Assessments</span>
              </router-link>
              <router-link
                to="/audit-planning/annual-plan"
                class="nav-subitem"
                :class="{ 'nav-subitem-active': $route.path === '/audit-planning/annual-plan' }"
              >
                <CalendarIcon class="h-4 w-4" />
                <span v-if="!isSidebarCollapsed">Annual Audit Plan</span>
              </router-link>
              <router-link
                to="/audit-planning/programs"
                class="nav-subitem"
                :class="{ 'nav-subitem-active': $route.path === '/audit-planning/programs' }"
              >
                <FileTextIcon class="h-4 w-4" />
                <span v-if="!isSidebarCollapsed">Audit Programs</span>
              </router-link>
              <router-link
                to="/audit-planning/calendar"
                class="nav-subitem"
                :class="{ 'nav-subitem-active': $route.path === '/audit-planning/calendar' }"
              >
                <CalendarDaysIcon class="h-4 w-4" />
                <span v-if="!isSidebarCollapsed">Audit Calendar</span>
              </router-link>
            </div>
          </div>

          <!-- Audit Execution -->
          <div class="nav-group">
            <div
              class="nav-group-header"
              @click="toggleNavGroup('auditExecution')"
            >
              <div class="flex items-center space-x-2">
                <ClipboardListIcon class="h-5 w-5" />
                <span v-if="!isSidebarCollapsed">Audit Execution</span>
              </div>
              <ChevronDownIcon
                v-if="!isSidebarCollapsed"
                :class="[
                  'h-4 w-4 transition-transform',
                  expandedGroups.auditExecution ? 'rotate-180' : ''
                ]"
              />
            </div>
            <div v-if="expandedGroups.auditExecution || isSidebarCollapsed" class="nav-group-items">
              <router-link
                to="/audit-execution/engagements"
                class="nav-subitem"
                :class="{ 'nav-subitem-active': $route.path === '/audit-execution/engagements' }"
              >
                <BriefcaseIcon class="h-4 w-4" />
                <span v-if="!isSidebarCollapsed">Audit Engagements</span>
              </router-link>
              <router-link
                to="/audit-execution/working-papers"
                class="nav-subitem"
                :class="{ 'nav-subitem-active': $route.path === '/audit-execution/working-papers' }"
              >
                <FolderIcon class="h-4 w-4" />
                <span v-if="!isSidebarCollapsed">Working Papers</span>
              </router-link>
              <router-link
                to="/audit-execution/data-analytics"
                class="nav-subitem"
                :class="{ 'nav-subitem-active': $route.path === '/audit-execution/data-analytics' }"
              >
                <BarChartIcon class="h-4 w-4" />
                <span v-if="!isSidebarCollapsed">Data Analytics</span>
              </router-link>
              <router-link
                to="/audit-execution/test-library"
                class="nav-subitem"
                :class="{ 'nav-subitem-active': $route.path === '/audit-execution/test-library' }"
              >
                <TestTubeIcon class="h-4 w-4" />
                <span v-if="!isSidebarCollapsed">Test Library</span>
              </router-link>
              <router-link
                to="/audit-execution/test-execution"
                class="nav-subitem"
                :class="{ 'nav-subitem-active': $route.path === '/audit-execution/test-execution' }"
              >
                <PlayCircleIcon class="h-4 w-4" />
                <span v-if="!isSidebarCollapsed">Test Execution</span>
              </router-link>
            </div>
          </div>

          <!-- Findings & Follow-up -->
          <div class="nav-group">
            <div
              class="nav-group-header"
              @click="toggleNavGroup('findings')"
            >
              <div class="flex items-center space-x-2">
                <AlertCircleIcon class="h-5 w-5" />
                <span v-if="!isSidebarCollapsed">Findings & Follow-up</span>
              </div>
              <ChevronDownIcon
                v-if="!isSidebarCollapsed"
                :class="[
                  'h-4 w-4 transition-transform',
                  expandedGroups.findings ? 'rotate-180' : ''
                ]"
              />
            </div>
            <div v-if="expandedGroups.findings || isSidebarCollapsed" class="nav-group-items">
              <router-link
                to="/findings/list"
                class="nav-subitem"
                :class="{ 'nav-subitem-active': $route.path === '/findings/list' }"
              >
                <SearchIcon class="h-4 w-4" />
                <span v-if="!isSidebarCollapsed">Audit Findings</span>
              </router-link>
              <router-link
                to="/findings/corrective-actions"
                class="nav-subitem"
                :class="{ 'nav-subitem-active': $route.path === '/findings/corrective-actions' }"
              >
                <CheckCircleIcon class="h-4 w-4" />
                <span v-if="!isSidebarCollapsed">Corrective Actions</span>
              </router-link>
              <router-link
                to="/findings/follow-up"
                class="nav-subitem"
                :class="{ 'nav-subitem-active': $route.path === '/findings/follow-up' }"
              >
                <ClockIcon class="h-4 w-4" />
                <span v-if="!isSidebarCollapsed">Follow-up Tracker</span>
              </router-link>
            </div>
          </div>

          <!-- Data Management -->
          <div class="nav-group">
            <div
              class="nav-group-header"
              @click="toggleNavGroup('dataManagement')"
            >
              <div class="flex items-center space-x-2">
                <DatabaseIcon class="h-5 w-5" />
                <span v-if="!isSidebarCollapsed">Data Management</span>
              </div>
              <ChevronDownIcon
                v-if="!isSidebarCollapsed"
                :class="[
                  'h-4 w-4 transition-transform',
                  expandedGroups.dataManagement ? 'rotate-180' : ''
                ]"
              />
            </div>
            <div v-if="expandedGroups.dataManagement || isSidebarCollapsed" class="nav-group-items">
              <router-link
                to="/data-management/import-wizard"
                class="nav-subitem"
                :class="{ 'nav-subitem-active': $route.path === '/data-management/import-wizard' }"
              >
                <UploadIcon class="h-4 w-4" />
                <span v-if="!isSidebarCollapsed">Import Data</span>
              </router-link>
              <router-link
                to="/data-management/import-history"
                class="nav-subitem"
                :class="{ 'nav-subitem-active': $route.path === '/data-management/import-history' }"
              >
                <HistoryIcon class="h-4 w-4" />
                <span v-if="!isSidebarCollapsed">Import History</span>
              </router-link>
              <router-link
                to="/data-management/periods"
                class="nav-subitem"
                :class="{ 'nav-subitem-active': $route.path === '/data-management/periods' }"
              >
                <CalendarDaysIcon class="h-4 w-4" />
                <span v-if="!isSidebarCollapsed">Data Periods</span>
              </router-link>
              <router-link
                to="/data-management/quality"
                class="nav-subitem"
                :class="{ 'nav-subitem-active': $route.path === '/data-management/quality' }"
              >
                <ShieldCheckIcon class="h-4 w-4" />
                <span v-if="!isSidebarCollapsed">Data Quality</span>
              </router-link>
              <router-link
                to="/data-management/explorer"
                class="nav-subitem"
                :class="{ 'nav-subitem-active': $route.path === '/data-management/explorer' }"
              >
                <SearchIcon class="h-4 w-4" />
                <span v-if="!isSidebarCollapsed">BC Data Explorer</span>
              </router-link>
            </div>
          </div>

          <!-- Compliance -->
          <div class="nav-group">
            <div
              class="nav-group-header"
              @click="toggleNavGroup('compliance')"
            >
              <div class="flex items-center space-x-2">
                <CheckSquareIcon class="h-5 w-5" />
                <span v-if="!isSidebarCollapsed">Compliance</span>
              </div>
              <ChevronDownIcon
                v-if="!isSidebarCollapsed"
                :class="[
                  'h-4 w-4 transition-transform',
                  expandedGroups.compliance ? 'rotate-180' : ''
                ]"
              />
            </div>
            <div v-if="expandedGroups.compliance || isSidebarCollapsed" class="nav-group-items">
              <router-link
                to="/compliance/requirements"
                class="nav-subitem"
                :class="{ 'nav-subitem-active': $route.path === '/compliance/requirements' }"
              >
                <FileCheckIcon class="h-4 w-4" />
                <span v-if="!isSidebarCollapsed">Requirements</span>
              </router-link>
              <router-link
                to="/compliance/checklist"
                class="nav-subitem"
                :class="{ 'nav-subitem-active': $route.path === '/compliance/checklist' }"
              >
                <ClipboardListIcon class="h-4 w-4" />
                <span v-if="!isSidebarCollapsed">Compliance Checklist</span>
              </router-link>
              <router-link
                to="/compliance/tax-tracker"
                class="nav-subitem"
                :class="{ 'nav-subitem-active': $route.path === '/compliance/tax-tracker' }"
              >
                <CalculatorIcon class="h-4 w-4" />
                <span v-if="!isSidebarCollapsed">Tax Tracker</span>
              </router-link>
              <router-link
                to="/compliance/calendar"
                class="nav-subitem"
                :class="{ 'nav-subitem-active': $route.path === '/compliance/calendar' }"
              >
                <CalendarIcon class="h-4 w-4" />
                <span v-if="!isSidebarCollapsed">Regulatory Calendar</span>
              </router-link>
            </div>
          </div>

          <!-- Reports -->
          <div class="nav-group">
            <div
              class="nav-group-header"
              @click="toggleNavGroup('reports')"
            >
              <div class="flex items-center space-x-2">
                <FileBarChartIcon class="h-5 w-5" />
                <span v-if="!isSidebarCollapsed">Reports</span>
              </div>
              <ChevronDownIcon
                v-if="!isSidebarCollapsed"
                :class="[
                  'h-4 w-4 transition-transform',
                  expandedGroups.reports ? 'rotate-180' : ''
                ]"
              />
            </div>
            <div v-if="expandedGroups.reports || isSidebarCollapsed" class="nav-group-items">
              <router-link
                to="/reports/builder"
                class="nav-subitem"
                :class="{ 'nav-subitem-active': $route.path === '/reports/builder' }"
              >
                <WrenchIcon class="h-4 w-4" />
                <span v-if="!isSidebarCollapsed">Report Builder</span>
              </router-link>
              <router-link
                to="/reports/audit-reports"
                class="nav-subitem"
                :class="{ 'nav-subitem-active': $route.path === '/reports/audit-reports' }"
              >
                <FileTextIcon class="h-4 w-4" />
                <span v-if="!isSidebarCollapsed">Audit Reports</span>
              </router-link>
              <router-link
                to="/reports/board-reports"
                class="nav-subitem"
                :class="{ 'nav-subitem-active': $route.path === '/reports/board-reports' }"
              >
                <PresentationIcon class="h-4 w-4" />
                <span v-if="!isSidebarCollapsed">Board Reports</span>
              </router-link>
              <router-link
                to="/reports/standard"
                class="nav-subitem"
                :class="{ 'nav-subitem-active': $route.path === '/reports/standard' }"
              >
                <FileBarChartIcon class="h-4 w-4" />
                <span v-if="!isSidebarCollapsed">Standard Reports</span>
              </router-link>
            </div>
          </div>

          <!-- Inventory Audit -->
          <div class="nav-group">
            <div
              class="nav-group-header"
              @click="toggleNavGroup('inventoryAudit')"
            >
              <div class="flex items-center space-x-2">
                <PackageIcon class="h-5 w-5" />
                <span v-if="!isSidebarCollapsed">Inventory Audit</span>
              </div>
              <ChevronDownIcon
                v-if="!isSidebarCollapsed"
                :class="[
                  'h-4 w-4 transition-transform',
                  expandedGroups.inventoryAudit ? 'rotate-180' : ''
                ]"
              />
            </div>
            <div v-if="expandedGroups.inventoryAudit || isSidebarCollapsed" class="nav-group-items">
              <router-link
                to="/inventory-audit"
                class="nav-subitem"
                :class="{ 'nav-subitem-active': $route.path === '/inventory-audit' }"
              >
                <LayoutDashboardIcon class="h-4 w-4" />
                <span v-if="!isSidebarCollapsed">Dashboard</span>
              </router-link>
              <router-link
                to="/inventory-audit/items"
                class="nav-subitem"
                :class="{ 'nav-subitem-active': $route.path.startsWith('/inventory-audit/items') }"
              >
                <PackageIcon class="h-4 w-4" />
                <span v-if="!isSidebarCollapsed">Item Master</span>
              </router-link>
              <router-link
                to="/inventory-audit/plans"
                class="nav-subitem"
                :class="{ 'nav-subitem-active': $route.path.startsWith('/inventory-audit/plans') }"
              >
                <ClipboardListIcon class="h-4 w-4" />
                <span v-if="!isSidebarCollapsed">Audit Plans</span>
              </router-link>
              <router-link
                to="/inventory-audit/sessions"
                class="nav-subitem"
                :class="{ 'nav-subitem-active': $route.path.startsWith('/inventory-audit/sessions') }"
              >
                <ClipboardCheckIcon class="h-4 w-4" />
                <span v-if="!isSidebarCollapsed">Stock Take Sessions</span>
              </router-link>
              <router-link
                to="/inventory-audit/variance-cases"
                class="nav-subitem"
                :class="{ 'nav-subitem-active': $route.path.startsWith('/inventory-audit/variance-cases') }"
              >
                <AlertTriangleIcon class="h-4 w-4" />
                <span v-if="!isSidebarCollapsed">Variance Cases</span>
              </router-link>
              <router-link
                to="/inventory-audit/stock-take"
                class="nav-subitem"
                :class="{ 'nav-subitem-active': $route.path.startsWith('/inventory-audit/stock-take') }"
              >
                <RotateCcwIcon class="h-4 w-4" />
                <span v-if="!isSidebarCollapsed">Stock Take</span>
              </router-link>
              <router-link
                to="/inventory-audit/issues"
                class="nav-subitem"
                :class="{ 'nav-subitem-active': $route.path.startsWith('/inventory-audit/issues') }"
              >
                <AlertCircleIcon class="h-4 w-4" />
                <span v-if="!isSidebarCollapsed">Issue Log</span>
              </router-link>
              <router-link
                to="/inventory-audit/scorecards"
                class="nav-subitem"
                :class="{ 'nav-subitem-active': $route.path.startsWith('/inventory-audit/scorecards') }"
              >
                <BarChart2Icon class="h-4 w-4" />
                <span v-if="!isSidebarCollapsed">Scorecards</span>
              </router-link>
              <router-link
                to="/inventory-audit/settings"
                class="nav-subitem"
                :class="{ 'nav-subitem-active': $route.path === '/inventory-audit/settings' }"
              >
                <SettingsIcon class="h-4 w-4" />
                <span v-if="!isSidebarCollapsed">Settings</span>
              </router-link>
            </div>
          </div>



          <!-- Chat -->
          <router-link
            to="/chat"
            class="nav-item"
            :class="{ 'nav-item-active': $route.path.startsWith('/chat') }"
          >
            <MessageCircleIcon class="h-5 w-5" />
            <span v-if="!isSidebarCollapsed">AI Chat</span>
          </router-link>

          <!-- Settings -->
          <div class="nav-group">
            <div
              class="nav-group-header"
              @click="toggleNavGroup('settings')"
            >
              <div class="flex items-center space-x-2">
                <SettingsIcon class="h-5 w-5" />
                <span v-if="!isSidebarCollapsed">Settings</span>
              </div>
              <ChevronDownIcon
                v-if="!isSidebarCollapsed"
                :class="[
                  'h-4 w-4 transition-transform',
                  expandedGroups.settings ? 'rotate-180' : ''
                ]"
              />
            </div>
            <div v-if="expandedGroups.settings || isSidebarCollapsed" class="nav-group-items">
              <router-link
                to="/settings/users"
                class="nav-subitem"
                :class="{ 'nav-subitem-active': $route.path === '/settings/users' }"
              >
                <UsersIcon class="h-4 w-4" />
                <span v-if="!isSidebarCollapsed">Users & Roles</span>
              </router-link>
              <router-link
                to="/settings/templates"
                class="nav-subitem"
                :class="{ 'nav-subitem-active': $route.path === '/settings/templates' }"
              >
                <FileTextIcon class="h-4 w-4" />
                <span v-if="!isSidebarCollapsed">Templates</span>
              </router-link>
              <router-link
                to="/settings/configuration"
                class="nav-subitem"
                :class="{ 'nav-subitem-active': $route.path === '/settings/configuration' }"
              >
                <CogIcon class="h-4 w-4" />
                <span v-if="!isSidebarCollapsed">Configuration</span>
              </router-link>
            </div>
          </div>
        </nav>
      </aside>

      <!-- Main Content Area -->
      <main class="flex-1 overflow-hidden flex flex-col">
        <!-- Breadcrumbs (hide for fullHeight pages like chat) -->
        <div 
          v-if="!isFullHeightPage" 
          class="flex h-12 items-center border-b border-outline-gray-200 bg-surface-white px-6"
        >
          <Breadcrumbs :items="breadcrumbItems" />
        </div>

        <!-- Page Content -->
        <div :class="[
          'flex-1 overflow-auto',
          isFullHeightPage ? '' : 'p-6'
        ]">
          <router-view />
        </div>
      </main>
    </div>

    <!-- Footer (optional) -->
    <footer class="flex h-10 items-center justify-center border-t border-outline-gray-200 bg-surface-white px-6">
      <p class="text-sm text-gray-500">
        © 2025 Internal Audit Management System. All rights reserved.
      </p>
    </footer>
  </div>
</template>

<script setup>
import Breadcrumbs from "@/components/Common/Breadcrumbs.vue"
import { session } from "@/data/session"
import { Avatar, Badge, Button, Dropdown } from "frappe-ui"
import {
	AlertCircleIcon,
	AlertTriangleIcon,
	BarChart2Icon,
	BarChartIcon,
	BellIcon,
	BriefcaseIcon,
	CalculatorIcon,
	CalendarDaysIcon,
	CalendarIcon,
	CheckCircleIcon,
	CheckSquareIcon,
	ChevronDownIcon,
	ChevronLeftIcon,
	ClipboardCheckIcon,
	ClipboardListIcon,
	ClockIcon,
	CogIcon,
	DatabaseIcon,
	FileBarChartIcon,
	FileCheckIcon,
	FileTextIcon,
	FolderIcon,
	GlobeIcon,
	HistoryIcon,
	HomeIcon,
	LayoutDashboardIcon,
	MessageCircleIcon,
	MoonIcon,
	PackageIcon,
	PlayCircleIcon,
	PresentationIcon,
	RotateCcwIcon,
	SearchIcon,
	SettingsIcon,
	ShieldCheckIcon,
	SunIcon,
	TestTubeIcon,
	UploadIcon,
	UsersIcon,
	WrenchIcon,
} from "lucide-vue-next"
import { computed, onMounted, ref } from "vue"
import { useRoute, useRouter } from "vue-router"

// Reactive state
const route = useRoute()
const router = useRouter()
const isSidebarCollapsed = ref(false)
const isDarkTheme = ref(false)
const notificationCount = ref(3)

const expandedGroups = ref({
	auditPlanning: true,
	auditExecution: false,
	findings: false,
	dataManagement: false,
	compliance: false,
	reports: false,
	inventoryAudit: false,

	settings: false,
})

// Computed properties
// Check if current page should use full height (no padding/breadcrumbs)
const isFullHeightPage = computed(() => {
	return route.meta?.fullHeight === true
})

const breadcrumbItems = computed(() => {
	const items = []
	const pathSegments = route.path.split("/").filter(Boolean)

	let currentPath = ""
	pathSegments.forEach((segment, index) => {
		currentPath += `/${segment}`
		const matchedRoute = router.getRoutes().find((r) => r.path === currentPath)
		if (matchedRoute) {
			items.push({
				label:
					matchedRoute.meta?.title ||
					segment.charAt(0).toUpperCase() + segment.slice(1),
				to: currentPath,
				isActive: index === pathSegments.length - 1,
			})
		}
	})

	return items
})

const settingsOptions = [
	{
		label: "Profile Settings",
		icon: "user",
		onClick: () => console.log("Profile settings"),
	},
	{
		label: "System Preferences",
		icon: "settings",
		onClick: () => console.log("System preferences"),
	},
	{
		label: "Help & Support",
		icon: "help-circle",
		onClick: () => console.log("Help & support"),
	},
]

const userMenuOptions = [
	{
		label: "My Profile",
		icon: "user",
		onClick: () => console.log("My profile"),
	},
	{
		label: "Change Password",
		icon: "lock",
		onClick: () => console.log("Change password"),
	},
	{
		label: "Sign Out",
		icon: "log-out",
		onClick: () => session.logout.submit(),
	},
]

// Methods
const toggleSidebar = () => {
	isSidebarCollapsed.value = !isSidebarCollapsed.value
}

const toggleTheme = () => {
	isDarkTheme.value = !isDarkTheme.value
	const theme = isDarkTheme.value ? "dark" : "light"
	document.documentElement.setAttribute("data-theme", theme)
	localStorage.setItem("theme", theme)
}

const toggleNotifications = () => {
	console.log("Toggle notifications panel")
}

const toggleNavGroup = (group) => {
	if (!isSidebarCollapsed.value) {
		expandedGroups.value[group] = !expandedGroups.value[group]
	}
}

// Lifecycle
onMounted(() => {
	// Load theme preference
	const savedTheme = localStorage.getItem("theme") || "light"
	isDarkTheme.value = savedTheme === "dark"
	document.documentElement.setAttribute("data-theme", savedTheme)
})
</script>

<style scoped>
.nav-item {
  @apply flex items-center space-x-3 rounded-lg px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 hover:text-gray-900;
}

.nav-item-active {
  @apply bg-blue-50 text-blue-700;
}

.nav-group {
  @apply space-y-1;
}

.nav-group-header {
  @apply flex cursor-pointer items-center justify-between rounded-lg px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 hover:text-gray-900;
}

.nav-group-items {
  @apply space-y-1 pl-4;
}

.nav-subitem {
  @apply flex items-center space-x-3 rounded-lg px-3 py-2 text-sm text-gray-600 hover:bg-gray-100 hover:text-gray-900;
}

.nav-subitem-active {
  @apply bg-blue-50 text-blue-700;
}
</style>