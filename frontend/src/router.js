import { createRouter, createWebHistory } from "vue-router"

// Layouts
import AppLayout from "@/layouts/AppLayout.vue"

import AnnualPlan from "@/pages/AnnualPlan.vue"
import AuditCalendar from "@/pages/AuditCalendar.vue"
import AuditPrograms from "@/pages/AuditPrograms.vue"
import AuditUniverse from "@/pages/AuditUniverse.vue"
import BoardReports from "@/pages/BoardReports.vue"
import ComplianceChecklist from "@/pages/ComplianceChecklist.vue"
import ComplianceRequirements from "@/pages/ComplianceRequirements.vue"
import CorrectiveActions from "@/pages/CorrectiveActions.vue"
// Pages
import Dashboard from "@/pages/Dashboard.vue"
import DataAnalytics from "@/pages/DataAnalytics.vue"
import DataPeriods from "@/pages/DataPeriods.vue"
import DataQuality from "@/pages/DataQuality.vue"
import EngagementList from "@/pages/EngagementList.vue"
import FindingsList from "@/pages/FindingsList.vue"
import FollowUpTracker from "@/pages/FollowUpTracker.vue"
import ImportData from "@/pages/ImportData.vue"
import RegulatoryCalendar from "@/pages/RegulatoryCalendar.vue"
import ReportBuilder from "@/pages/ReportBuilder.vue"
import Reports from "@/pages/Reports.vue"
import RiskAssessments from "@/pages/RiskAssessments.vue"
import Settings from "@/pages/Settings.vue"
import TaxCompliance from "@/pages/TaxCompliance.vue"
import TestExecution from "@/pages/TestExecution.vue"
import TestLibrary from "@/pages/TestLibrary.vue"
import UserManagement from "@/pages/UserManagement.vue"
import WorkingPapers from "@/pages/WorkingPapers.vue"

// Inventory Audit Pages
import InventoryAuditDashboard from "@/pages/inventory/InventoryAuditDashboard.vue"
import InventoryItemMaster from "@/pages/inventory/InventoryItemMaster.vue"
import InventoryAuditSettings from "@/pages/inventory/InventoryAuditSettings.vue"
import AuditPlanList from "@/pages/inventory/AuditPlanList.vue"
import AuditPlanDetail from "@/pages/inventory/AuditPlanDetail.vue"
import AuditPlanForm from "@/pages/inventory/AuditPlanForm.vue"
import StockTakeSessionList from "@/pages/inventory/StockTakeSessionList.vue"
import StockTakeSessionDetail from "@/pages/inventory/StockTakeSessionDetail.vue"
import StockTakeSessionForm from "@/pages/inventory/StockTakeSessionForm.vue"
import VarianceCaseList from "@/pages/inventory/VarianceCaseList.vue"
import VarianceCaseDetail from "@/pages/inventory/VarianceCaseDetail.vue"
import VarianceCaseForm from "@/pages/inventory/VarianceCaseForm.vue"
import StockTakeList from "@/pages/inventory/StockTakeList.vue"
import StockTakeDetail from "@/pages/inventory/StockTakeDetail.vue"
import StockTakeForm from "@/pages/inventory/StockTakeForm.vue"
import IssueLogList from "@/pages/inventory/IssueLogList.vue"
import IssueLogDetail from "@/pages/inventory/IssueLogDetail.vue"
import IssueLogForm from "@/pages/inventory/IssueLogForm.vue"
import ComplianceScorecardList from "@/pages/inventory/ComplianceScorecardList.vue"
import ComplianceScorecardDetail from "@/pages/inventory/ComplianceScorecardDetail.vue"
import ComplianceScorecardForm from "@/pages/inventory/ComplianceScorecardForm.vue"

// Error pages
import NotFound from "@/pages/NotFound.vue"
import Unauthorized from "@/pages/Unauthorized.vue"

const routes = [
	// Main application routes
	{
		path: "/",
		component: AppLayout,
		meta: { requiresAuth: true },
		children: [
			// Dashboard
			{
				path: "",
				name: "Dashboard",
				component: Dashboard,
				meta: {
					title: "Dashboard",
					icon: "LayoutDashboard",
					breadcrumb: "Dashboard",
				},
			},

			// Audit Planning
			{
				path: "audit-planning/universe",
				name: "AuditUniverse",
				component: AuditUniverse,
				meta: {
					title: "Audit Universe",
					icon: "Target",
					breadcrumb: "Audit Universe",
				},
			},
			{
				path: "audit-planning/universe/new",
				name: "NewAuditUniverse",
				component: () => import("@/pages/AuditUniverseDetail.vue"),
				meta: {
					title: "New Audit Universe Entity",
					breadcrumb: "New Entity",
				},
				props: { mode: "new" },
			},
			{
				path: "audit-planning/universe/:id",
				name: "AuditUniverseDetail",
				component: () => import("@/pages/AuditUniverseDetail.vue"),
				meta: {
					title: "Audit Universe Details",
					breadcrumb: "Entity Details",
				},
				props: (route) => ({
					entityId: route.params.id,
					mode: "view",
				}),
			},
			{
				path: "audit-planning/universe/:id/edit",
				name: "EditAuditUniverse",
				component: () => import("@/pages/AuditUniverseDetail.vue"),
				meta: {
					title: "Edit Audit Universe Entity",
					breadcrumb: "Edit Entity",
				},
				props: (route) => ({
					entityId: route.params.id,
					mode: "edit",
				}),
			},
			{
				path: "audit-planning/risk-assessment",
				name: "RiskAssessments",
				component: RiskAssessments,
				meta: {
					title: "Risk Assessments",
					icon: "AlertTriangle",
					breadcrumb: "Risk Assessments",
				},
			},
			{
				path: "audit-planning/risk-assessment/new",
				name: "NewRiskAssessment",
				component: () => import("@/pages/RiskAssessmentDetail.vue"),
				meta: {
					title: "New Risk Assessment",
					breadcrumb: "New Assessment",
				},
				props: { mode: "new" },
			},
			{
				path: "audit-planning/risk-assessment/:id",
				name: "RiskAssessmentDetail",
				component: () => import("@/pages/RiskAssessmentDetail.vue"),
				meta: {
					title: "Risk Assessment Details",
					breadcrumb: "Risk Assessment Details",
				},
				props: true,
			},
			{
				path: "audit-planning/risk-assessment/:id/edit",
				name: "EditRiskAssessment",
				component: () => import("@/pages/RiskAssessmentDetail.vue"),
				meta: {
					title: "Edit Risk Assessment",
					breadcrumb: "Edit Assessment",
				},
				props: (route) => ({
					assessmentId: route.params.id,
					mode: "edit",
				}),
			},
			{
				path: "audit-planning/annual-plan",
				name: "AnnualPlan",
				component: AnnualPlan,
				meta: {
					title: "Annual Audit Plan",
					icon: "Calendar",
					breadcrumb: "Annual Audit Plan",
				},
			},
			{
				path: "audit-planning/programs",
				name: "AuditPrograms",
				component: AuditPrograms,
				meta: {
					title: "Audit Programs",
					icon: "FileText",
					breadcrumb: "Audit Programs",
				},
			},
			{
				path: "audit-planning/calendar",
				name: "AuditCalendar",
				component: AuditCalendar,
				meta: {
					title: "Audit Calendar",
					icon: "CalendarDays",
					breadcrumb: "Audit Calendar",
				},
			},

			// Audit Execution
			{
				path: "audit-execution/engagements",
				name: "AuditEngagements",
				component: EngagementList,
				meta: {
					title: "Audit Engagements",
					icon: "ClipboardList",
					breadcrumb: "Audit Engagements",
				},
			},
			{
				path: "audit-execution/test-library",
				name: "TestLibrary",
				component: TestLibrary,
				meta: {
					title: "Test Library",
					icon: "FileText",
					breadcrumb: "Test Library",
				},
			},
			{
				path: "audit-execution/test-execution",
				name: "TestExecution",
				component: TestExecution,
				meta: {
					title: "Test Execution",
					icon: "PlayCircle",
					breadcrumb: "Test Execution",
				},
			},
			{
				path: "audit-execution/working-papers",
				name: "WorkingPapers",
				component: WorkingPapers,
				meta: {
					title: "Working Papers",
					icon: "FileText",
					breadcrumb: "Working Papers",
				},
			},
			{
				path: "audit-execution/data-analytics",
				name: "DataAnalytics",
				component: DataAnalytics,
				meta: {
					title: "Data Analytics",
					icon: "BarChart",
					breadcrumb: "Data Analytics",
				},
			},

			// Findings & Follow-up
			{
				path: "findings/list",
				name: "FindingsList",
				component: FindingsList,
				meta: {
					title: "Audit Findings",
					icon: "Search",
					breadcrumb: "Audit Findings",
				},
			},
			{
				path: "findings/corrective-actions",
				name: "CorrectiveActions",
				component: CorrectiveActions,
				meta: {
					title: "Corrective Actions",
					icon: "CheckCircle",
					breadcrumb: "Corrective Actions",
				},
			},
			{
				path: "findings/follow-up",
				name: "FollowUpTracker",
				component: FollowUpTracker,
				meta: {
					title: "Follow-up Tracker",
					icon: "Clock",
					breadcrumb: "Follow-up Tracker",
				},
			},

			// Data Management
			{
				path: "data-management/import-wizard",
				name: "ImportData",
				component: ImportData,
				meta: {
					title: "Import Data",
					icon: "Upload",
					breadcrumb: "Import Data",
				},
			},
			{
				path: "data-management/explorer",
				name: "BCDataExplorer",
				component: ImportData,
				meta: {
					title: "BC Data Explorer",
					icon: "Database",
					breadcrumb: "BC Data Explorer",
				},
				props: { defaultTab: "bc-explorer" },
			},
			{
				path: "data-management/import-history",
				name: "ImportHistory",
				component: ImportData,
				meta: {
					title: "Import History",
					icon: "History",
					breadcrumb: "Import History",
				},
				props: { defaultTab: "history" },
			},
			{
				path: "data-management/periods",
				name: "DataPeriods",
				component: DataPeriods,
				meta: {
					title: "Data Periods",
					icon: "CalendarDays",
					breadcrumb: "Data Periods",
				},
			},
			{
				path: "data-management/quality",
				name: "DataQuality",
				component: DataQuality,
				meta: {
					title: "Data Quality",
					icon: "ShieldCheck",
					breadcrumb: "Data Quality",
				},
			},

			// Compliance
			{
				path: "compliance/requirements",
				name: "ComplianceRequirements",
				component: ComplianceRequirements,
				meta: {
					title: "Compliance Requirements",
					icon: "FileCheck",
					breadcrumb: "Compliance Requirements",
				},
			},
			{
				path: "compliance/checklist",
				name: "ComplianceChecklist",
				component: ComplianceChecklist,
				meta: {
					title: "Compliance Checklist",
					icon: "CheckSquare",
					breadcrumb: "Compliance Checklist",
				},
			},
			{
				path: "compliance/tax-tracker",
				name: "TaxCompliance",
				component: TaxCompliance,
				meta: {
					title: "Tax Tracker",
					icon: "Calculator",
					breadcrumb: "Tax Tracker",
				},
			},
			{
				path: "compliance/calendar",
				name: "RegulatoryCalendar",
				component: RegulatoryCalendar,
				meta: {
					title: "Regulatory Calendar",
					icon: "Calendar",
					breadcrumb: "Regulatory Calendar",
				},
			},

			// Reports
			{
				path: "reports/audit-reports",
				name: "AuditReports",
				component: Reports,
				meta: {
					title: "Audit Reports",
					icon: "FileBarChart",
					breadcrumb: "Audit Reports",
				},
			},
			{
				path: "reports/standard",
				name: "StandardReports",
				component: BoardReports,
				meta: {
					title: "Standard Reports",
					icon: "Presentation",
					breadcrumb: "Standard Reports",
				},
			},
			{
				path: "reports/board-reports",
				name: "BoardReports",
				component: BoardReports,
				meta: {
					title: "Board Reports",
					icon: "Presentation",
					breadcrumb: "Board Reports",
				},
			},

			// Settings
			{
				path: "settings/configuration",
				name: "Settings",
				component: Settings,
				meta: {
					title: "Settings",
					icon: "Settings",
					breadcrumb: "Settings",
				},
			},
			{
				path: "settings/templates",
				name: "SettingsTemplates",
				component: Settings,
				meta: {
					title: "Settings Templates",
					icon: "FileTemplate",
					breadcrumb: "Settings Templates",
				},
				props: { defaultTab: "reports" },
			},
			{
				path: "settings/users",
				name: "UserManagement",
				component: UserManagement,
				meta: {
					title: "User Management",
					icon: "Users",
					breadcrumb: "User Management",
				},
			},

			// Detail routes (keeping existing ones)
			{
				path: "engagements/:id",
				name: "EngagementDetail",
				component: () => import("@/pages/EngagementDetail.vue"),
				meta: {
					title: "Engagement Details",
					breadcrumb: "Engagement Details",
				},
				props: true,
			},
			{
				path: "findings/:id",
				name: "FindingDetail",
				component: () => import("@/pages/FindingDetail.vue"),
				meta: {
					title: "Finding Details",
					breadcrumb: "Finding Details",
				},
				props: true,
			},

			// Import Data routes
			{
				path: "import-data/import-type/new",
				name: "NewImportType",
				component: ImportData,
				meta: {
					title: "New Import Type",
					breadcrumb: "New Import Type",
				},
				props: { defaultTab: "imports", mode: "new-import-type" },
			},
			{
				path: "import-data/import-type/:id/edit",
				name: "EditImportType",
				component: ImportData,
				meta: {
					title: "Edit Import Type",
					breadcrumb: "Edit Import Type",
				},
				props: (route) => ({
					defaultTab: "imports",
					mode: "edit-import-type",
					importTypeId: route.params.id,
				}),
			},
			{
				path: "import-data/import-type/:id/run",
				name: "RunImport",
				component: ImportData,
				meta: {
					title: "Run Import",
					breadcrumb: "Run Import",
				},
				props: (route) => ({
					defaultTab: "imports",
					mode: "run-import",
					importTypeId: route.params.id,
				}),
			},
			{
				path: "import-data/history/:id",
				name: "ImportHistoryDetail",
				component: ImportData,
				meta: {
					title: "Import History",
					breadcrumb: "Import History",
				},
				props: (route) => ({
					defaultTab: "history",
					mode: "view-history",
					historyId: route.params.id,
				}),
			},
			{
				path: "import-data/mapping/new",
				name: "NewFieldMapping",
				component: ImportData,
				meta: {
					title: "New Field Mapping",
					breadcrumb: "New Field Mapping",
				},
				props: { defaultTab: "mappings", mode: "new-mapping" },
			},
			{
				path: "import-data/mapping/:id/edit",
				name: "EditFieldMapping",
				component: ImportData,
				meta: {
					title: "Edit Field Mapping",
					breadcrumb: "Edit Field Mapping",
				},
				props: (route) => ({
					defaultTab: "mappings",
					mode: "edit-mapping",
					mappingId: route.params.id,
				}),
			},

			// Inventory Audit Module
			{
				path: "inventory-audit",
				name: "InventoryAuditDashboard",
				component: InventoryAuditDashboard,
				meta: {
					title: "Inventory Audit Dashboard",
					icon: "Package",
					breadcrumb: "Inventory Audit",
				},
			},
			{
				path: "inventory-audit/settings",
				name: "InventoryAuditSettings",
				component: InventoryAuditSettings,
				meta: {
					title: "Inventory Audit Settings",
					icon: "Settings",
					breadcrumb: "Settings",
				},
			},
			{
				path: "inventory-audit/items",
				name: "InventoryItemMaster",
				component: InventoryItemMaster,
				meta: {
					title: "Inventory Item Master",
					icon: "Package",
					breadcrumb: "Item Master",
				},
			},
			{
				path: "inventory-audit/items/new",
				name: "NewInventoryItem",
				component: InventoryItemMaster,
				meta: {
					title: "New Inventory Item",
					breadcrumb: "New Item",
				},
				props: { mode: "new" },
			},
			{
				path: "inventory-audit/items/:id",
				name: "InventoryItemDetail",
				component: InventoryItemMaster,
				meta: {
					title: "Item Details",
					breadcrumb: "Item Details",
				},
				props: true,
			},
			{
				path: "inventory-audit/plans",
				name: "AuditPlanList",
				component: AuditPlanList,
				meta: {
					title: "Audit Plans",
					icon: "ClipboardList",
					breadcrumb: "Audit Plans",
				},
			},
			{
				path: "inventory-audit/plans/new",
				name: "NewAuditPlan",
				component: AuditPlanForm,
				meta: {
					title: "New Audit Plan",
					breadcrumb: "New Plan",
				},
			},
			{
				path: "inventory-audit/plans/:id",
				name: "AuditPlanDetail",
				component: AuditPlanDetail,
				meta: {
					title: "Audit Plan Details",
					breadcrumb: "Plan Details",
				},
				props: true,
			},
			{
				path: "inventory-audit/plans/:id/edit",
				name: "EditAuditPlan",
				component: AuditPlanForm,
				meta: {
					title: "Edit Audit Plan",
					breadcrumb: "Edit Plan",
				},
				props: true,
			},
			{
				path: "inventory-audit/sessions",
				name: "StockTakeSessionList",
				component: StockTakeSessionList,
				meta: {
					title: "Stock Take Sessions",
					icon: "Clipboard",
					breadcrumb: "Stock Take Sessions",
				},
			},
			{
				path: "inventory-audit/sessions/new",
				name: "NewStockTakeSession",
				component: StockTakeSessionForm,
				meta: {
					title: "New Stock Take Session",
					breadcrumb: "New Session",
				},
			},
			{
				path: "inventory-audit/sessions/:id",
				name: "StockTakeSessionDetail",
				component: StockTakeSessionDetail,
				meta: {
					title: "Session Details",
					breadcrumb: "Session Details",
				},
				props: true,
			},
			{
				path: "inventory-audit/sessions/:id/edit",
				name: "EditStockTakeSession",
				component: StockTakeSessionForm,
				meta: {
					title: "Edit Session",
					breadcrumb: "Edit Session",
				},
				props: true,
			},
			{
				path: "inventory-audit/variance-cases",
				name: "VarianceCaseList",
				component: VarianceCaseList,
				meta: {
					title: "Variance Cases",
					icon: "AlertTriangle",
					breadcrumb: "Variance Cases",
				},
			},
			{
				path: "inventory-audit/variance-cases/new",
				name: "NewVarianceCase",
				component: VarianceCaseForm,
				meta: {
					title: "New Variance Case",
					breadcrumb: "New Case",
				},
			},
			{
				path: "inventory-audit/variance-cases/:id",
				name: "VarianceCaseDetail",
				component: VarianceCaseDetail,
				meta: {
					title: "Variance Case Details",
					breadcrumb: "Case Details",
				},
				props: true,
			},
			{
				path: "inventory-audit/variance-cases/:id/edit",
				name: "EditVarianceCase",
				component: VarianceCaseForm,
				meta: {
					title: "Edit Variance Case",
					breadcrumb: "Edit Case",
				},
				props: true,
			},
			{
				path: "inventory-audit/stock-take",
				name: "StockTakeList",
				component: StockTakeList,
				meta: {
					title: "Stock Take Audits",
					icon: "Package",
					breadcrumb: "Stock Take",
				},
			},
			{
				path: "inventory-audit/stock-take/new",
				name: "NewStockTake",
				component: StockTakeForm,
				meta: {
					title: "New Stock Take",
					breadcrumb: "New Stock Take",
				},
			},
			{
				path: "inventory-audit/stock-take/:id",
				name: "StockTakeDetail",
				component: StockTakeDetail,
				meta: {
					title: "Stock Take Details",
					breadcrumb: "Stock Take Details",
				},
				props: true,
			},
			{
				path: "inventory-audit/stock-take/:id/edit",
				name: "EditStockTake",
				component: StockTakeForm,
				meta: {
					title: "Edit Stock Take",
					breadcrumb: "Edit Stock Take",
				},
				props: true,
			},
			{
				path: "inventory-audit/issues",
				name: "IssueLogList",
				component: IssueLogList,
				meta: {
					title: "Stock Take Issues",
					icon: "AlertCircle",
					breadcrumb: "Issues",
				},
			},
			{
				path: "inventory-audit/issues/new",
				name: "NewIssueLog",
				component: IssueLogForm,
				meta: {
					title: "Log Issue",
					breadcrumb: "Log Issue",
				},
			},
			{
				path: "inventory-audit/issues/:id",
				name: "IssueLogDetail",
				component: IssueLogDetail,
				meta: {
					title: "Issue Details",
					breadcrumb: "Issue Details",
				},
				props: true,
			},
			{
				path: "inventory-audit/issues/:id/edit",
				name: "EditIssueLog",
				component: IssueLogForm,
				meta: {
					title: "Edit Issue",
					breadcrumb: "Edit Issue",
				},
				props: true,
			},
			{
				path: "inventory-audit/scorecards",
				name: "ComplianceScorecardList",
				component: ComplianceScorecardList,
				meta: {
					title: "Compliance Scorecards",
					icon: "BarChart2",
					breadcrumb: "Scorecards",
				},
			},
			{
				path: "inventory-audit/scorecards/new",
				name: "NewComplianceScorecard",
				component: ComplianceScorecardForm,
				meta: {
					title: "New Compliance Scorecard",
					breadcrumb: "New Scorecard",
				},
			},
			{
				path: "inventory-audit/scorecards/:id",
				name: "ComplianceScorecardDetail",
				component: ComplianceScorecardDetail,
				meta: {
					title: "Scorecard Details",
					breadcrumb: "Scorecard Details",
				},
				props: true,
			},
			{
				path: "inventory-audit/scorecards/:id/edit",
				name: "EditComplianceScorecard",
				component: ComplianceScorecardForm,
				meta: {
					title: "Edit Compliance Scorecard",
					breadcrumb: "Edit Scorecard",
				},
				props: true,
			},
		],
	},

	// Error routes
	{
		path: "/unauthorized",
		name: "Unauthorized",
		component: Unauthorized,
		meta: { requiresAuth: false },
	},
	{
		path: "/:pathMatch(.*)*",
		name: "NotFound",
		component: NotFound,
		meta: { requiresAuth: false },
	},
]

const router = createRouter({
	history: createWebHistory("/frontend"),
	routes,
})

// Navigation guards
router.beforeEach(async (to, from, next) => {
	// Import session here to avoid circular dependency
	const { session } = await import("@/data/session")

	// Check if route requires authentication
	if (to.meta.requiresAuth !== false) {
		// Check if user is authenticated using Frappe's session
		if (!session.isLoggedIn) {
			// Redirect to Frappe's default login page
			window.location.href = "/login"
			return
		}

		// Check if user has required permissions (if specified in route meta)
		if (to.meta.permissions) {
			// For now, we'll assume authenticated users have access
			// You can implement more sophisticated permission checking here
			// based on Frappe's user roles and permissions
		}
	}

	// Update page title
	if (to.meta.title) {
		document.title = `${to.meta.title} - Internal Audit System`
	}

	next()
})

// After each navigation, scroll to top
router.afterEach(() => {
	window.scrollTo(0, 0)
})

export default router
