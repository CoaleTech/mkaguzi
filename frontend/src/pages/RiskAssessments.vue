<template>
  <div class="space-y-6">
    <!-- Page Header with Enhanced Actions -->
    <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
      <div>
        <div class="flex items-center space-x-3">
          <div class="p-2 bg-red-100 rounded-lg">
            <AlertTriangleIcon class="h-6 w-6 text-red-600" />
          </div>
          <div>
            <h1 class="text-2xl font-bold text-gray-900">Risk Assessments</h1>
            <p class="text-gray-600 mt-1">
              Conduct and manage comprehensive risk assessments with advanced analytics
            </p>
          </div>
        </div>
      </div>

      <div class="flex flex-wrap items-center gap-3">
        <!-- Action Buttons -->
        <div class="flex items-center space-x-2">
          <div class="p-1">
            <Button
              variant="solid"
              theme="gray"
              size="sm"
              @click="exportAssessments"
              :loading="exporting"
            >
              <template #prefix>
                <DownloadIcon class="h-3.5 w-3.5" />
              </template>
              Export
            </Button>
          </div>

          <div class="p-1">
            <Button
              variant="solid"
              theme="gray"
              size="sm"
              @click="showTemplatesModal = true"
            >
              <template #prefix>
                <FileTextIcon class="h-3.5 w-3.5" />
              </template>
              Templates
            </Button>
          </div>

          <div class="p-1">
            <Button
              variant="solid"
              theme="gray"
              size="sm"
              @click="refreshData"
              :loading="loading"
            >
              <template #prefix>
                <RefreshCwIcon class="h-3.5 w-3.5" />
              </template>
              Refresh
            </Button>
          </div>

          <div class="p-1">
            <Button
              variant="solid"
              theme="red"
              size="sm"
              @click="createNewAssessment"
            >
              <template #prefix>
                <PlusIcon class="h-3.5 w-3.5" />
              </template>
              New Assessment
            </Button>
          </div>
        </div>
      </div>
    </div>

    <!-- Stats Dashboard Component -->
    <RiskAssessmentStats :stats="statsData" />

    <!-- Filters Component -->
    <RiskAssessmentFilters
      v-model:searchQuery="searchQuery"
      v-model:filterStatus="filterStatus"
      v-model:filterPeriod="filterPeriod"
      v-model:filterYear="filterYear"
      :viewMode="viewMode"
      :selectedCount="selectedAssessments.length"
      :filteredCount="filteredAssessments.length"
      :totalCount="riskAssessments.length"
      @bulk-action="showBulkModal = true"
      @show-analytics="showAnalyticsModal = true"
      @toggle-view="viewMode = viewMode === 'table' ? 'cards' : 'table'"
      @clear-filters="clearFilters"
    />

    <!-- Assessments Display - Table or Card View -->
    <div class="bg-white rounded-xl border border-gray-200 shadow-sm">
      <div class="px-6 py-4 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-semibold text-gray-900">Risk Assessments</h3>
          <div class="flex items-center space-x-2">
            <div class="p-1" v-if="viewMode === 'table' && filteredAssessments.length > 0">
              <Button
                variant="solid"
                theme="gray"
                size="sm"
                @click="selectAllAssessments"
              >
                {{ selectedAssessments.length === filteredAssessments.length ? 'Deselect All' : 'Select All' }}
              </Button>
            </div>
          </div>
        </div>
      </div>

      <!-- Table View -->
      <div v-if="viewMode === 'table'" class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left">
                <input
                  type="checkbox"
                  class="rounded border-gray-300 text-red-600 focus:ring-red-500"
                  :checked="selectedAssessments.length === filteredAssessments.length && filteredAssessments.length > 0"
                  @change="selectAllAssessments"
                />
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  @click="sortBy('assessment_id')">
                <div class="flex items-center space-x-1">
                  <span>Assessment ID</span>
                  <ArrowUpDownIcon class="h-3 w-3" />
                </div>
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  @click="sortBy('assessment_name')">
                <div class="flex items-center space-x-1">
                  <span>Name</span>
                  <ArrowUpDownIcon class="h-3 w-3" />
                </div>
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Period
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Risk Score
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Critical Risks
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr
              v-for="assessment in filteredAssessments"
              :key="assessment.name"
              class="hover:bg-gray-50 transition-colors"
              :class="{ 'bg-red-50': selectedAssessments.includes(assessment.name) }"
            >
              <td class="px-6 py-4">
                <input
                  type="checkbox"
                  class="rounded border-gray-300 text-red-600 focus:ring-red-500"
                  :checked="selectedAssessments.includes(assessment.name)"
                  @change="toggleAssessmentSelection(assessment.name)"
                />
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="flex-shrink-0 h-10 w-10">
                    <div class="h-10 w-10 rounded-lg bg-red-500 flex items-center justify-center text-white font-bold text-sm">
                      {{ assessment.assessment_id?.charAt(0)?.toUpperCase() || 'R' }}
                    </div>
                  </div>
                  <div class="ml-4">
                    <div class="text-sm font-semibold text-gray-900">{{ assessment.assessment_id }}</div>
                    <div class="text-sm text-gray-500">{{ formatDate(assessment.assessment_date) }}</div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4">
                <div class="text-sm font-medium text-gray-900">{{ assessment.assessment_name }}</div>
                <div class="text-sm text-gray-500">{{ assessment.fiscal_year }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ assessment.assessment_period }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <span class="text-sm font-medium text-gray-900">{{ getAverageRiskScore(assessment) }}</span>
                  <div class="ml-2 w-12 bg-gray-200 rounded-full h-1.5">
                    <div
                      class="h-1.5 rounded-full transition-all duration-300"
                      :class="getRiskScoreColor(getAverageRiskScore(assessment))"
                      :style="{ width: `${Math.min(getAverageRiskScore(assessment), 25) * 4}%` }"
                    ></div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center space-x-2">
                  <span class="text-sm font-medium text-gray-900">{{ assessment.top_risks?.length || 0 }}</span>
                  <span class="text-xs text-red-600">critical</span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <Badge
                  :variant="getStatusVariant(assessment.status)"
                  size="sm"
                  class="font-medium"
                >
                  {{ assessment.status }}
                </Badge>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div class="flex items-center space-x-1">
                  <Button
                    variant="solid"
                    theme="gray"
                    size="sm"
                    @click="viewAssessment(assessment)"
                    class="!p-1.5"
                  >
                    <EyeIcon class="h-3.5 w-3.5" />
                  </Button>
                  <Button
                    variant="solid"
                    theme="gray"
                    size="sm"
                    @click="editAssessment(assessment)"
                    class="!p-1.5"
                  >
                    <EditIcon class="h-3.5 w-3.5" />
                  </Button>
                  <Button
                    variant="solid"
                    theme="gray"
                    size="sm"
                    @click="duplicateAssessment(assessment)"
                    class="!p-1.5"
                  >
                    <CopyIcon class="h-3.5 w-3.5" />
                  </Button>
                  <Button
                    variant="solid"
                    theme="gray"
                    size="sm"
                    @click="showAssessmentMenu(assessment, $event)"
                    class="!p-1.5"
                  >
                    <MoreHorizontalIcon class="h-3.5 w-3.5" />
                  </Button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Card View -->
      <div v-else class="p-6">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div
            v-for="assessment in filteredAssessments"
            :key="assessment.name"
            class="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-lg transition-all duration-200 cursor-pointer group"
            :class="{ 'ring-2 ring-red-500 bg-red-50': selectedAssessments.includes(assessment.name) }"
            @click="toggleAssessmentSelection(assessment.name)"
          >
            <div class="flex items-start justify-between mb-4">
              <div class="flex items-center space-x-3">
                <div class="h-12 w-12 rounded-xl bg-red-500 flex items-center justify-center text-white font-bold">
                  {{ assessment.assessment_id?.charAt(0)?.toUpperCase() || 'R' }}
                </div>
                <div>
                  <h3 class="text-lg font-semibold text-gray-900 group-hover:text-red-900">{{ assessment.assessment_name }}</h3>
                  <p class="text-sm text-gray-600">{{ assessment.assessment_period }} {{ assessment.fiscal_year }}</p>
                </div>
              </div>
              <Badge
                :variant="getStatusVariant(assessment.status)"
                size="sm"
                class="font-medium"
              >
                {{ assessment.status }}
              </Badge>
            </div>

            <div class="space-y-3">
              <div>
                <div class="flex justify-between items-center mb-1">
                  <span class="text-sm text-gray-600">Risk Score</span>
                  <span class="text-sm font-medium">{{ getAverageRiskScore(assessment) }}</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2">
                  <div
                    class="bg-red-500 h-2 rounded-full transition-all duration-300"
                    :style="{ width: `${Math.min(getAverageRiskScore(assessment), 25) * 4}%` }"
                  ></div>
                </div>
              </div>

              <div class="flex justify-between items-center">
                <span class="text-sm text-gray-600">Critical Risks</span>
                <span class="text-sm font-medium">{{ assessment.top_risks?.length || 0 }}</span>
              </div>

              <div class="flex justify-between items-center">
                <span class="text-sm text-gray-600">Total Risks</span>
                <span class="text-sm font-medium">{{ assessment.risk_register?.length || 0 }}</span>
              </div>
            </div>

            <div class="flex items-center justify-between mt-6 pt-4 border-t border-gray-200">
              <div class="flex items-center space-x-1">
                <Button
                  variant="solid"
                  theme="gray"
                  size="sm"
                  @click.stop="viewAssessment(assessment)"
                  class="!p-1.5"
                >
                  <EyeIcon class="h-3.5 w-3.5" />
                </Button>
                <Button
                  variant="solid"
                  theme="gray"
                  size="sm"
                  @click.stop="editAssessment(assessment)"
                  class="!p-1.5"
                >
                  <EditIcon class="h-3.5 w-3.5" />
                </Button>
                <Button
                  variant="solid"
                  theme="gray"
                  size="sm"
                  @click.stop="duplicateAssessment(assessment)"
                  class="!p-1.5"
                >
                  <CopyIcon class="h-3.5 w-3.5" />
                </Button>
              </div>
              <div class="text-xs text-gray-500">
                {{ formatDate(assessment.modified) }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="filteredAssessments.length === 0 && riskAssessments.length === 0" class="px-6 py-20 text-center">
        <div class="mx-auto h-20 w-20 rounded-2xl bg-red-50 border-2 border-red-100 flex items-center justify-center mb-8 shadow-sm">
          <AlertTriangleIcon class="h-10 w-10 text-red-500" />
        </div>
        <div class="max-w-md mx-auto">
          <h3 class="text-2xl font-bold text-gray-900 mb-3">Welcome to Risk Assessments</h3>
          <p class="text-gray-600 mb-8 leading-relaxed">
            Conduct comprehensive risk assessments to identify, evaluate, and prioritize organizational risks. Build a robust risk management framework.
          </p>
          <div class="flex flex-col sm:flex-row justify-center gap-3">
            <Button
              variant="solid"
              theme="red"
              size="lg"
              @click="createNewAssessment"
              class="shadow-sm hover:shadow-md transition-shadow"
            >
              <template #prefix>
                <PlusIcon class="h-5 w-5" />
              </template>
              Create Your First Assessment
            </Button>
            <Button
              variant="outline"
              theme="gray"
              size="lg"
              @click="showTemplatesModal = true"
              class="border-gray-300 hover:border-gray-400"
            >
              <template #prefix>
                <FileTextIcon class="h-5 w-5" />
              </template>
              Browse Templates
            </Button>
          </div>
        </div>

        <!-- Quick Start Tips -->
        <div class="mt-12 max-w-2xl mx-auto">
          <div class="bg-gray-50 border border-gray-200 rounded-xl p-6">
            <h4 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <div class="h-2 w-2 bg-red-500 rounded-full mr-3"></div>
              Quick Start Tips
            </h4>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div class="flex items-start space-x-3">
                <div class="flex-shrink-0 h-6 w-6 bg-red-100 rounded-lg flex items-center justify-center mt-0.5">
                  <span class="text-red-600 font-semibold text-xs">1</span>
                </div>
                <div>
                  <p class="font-medium text-gray-900">Define Scope</p>
                  <p class="text-gray-600">Set clear assessment boundaries and objectives</p>
                </div>
              </div>
              <div class="flex items-start space-x-3">
                <div class="flex-shrink-0 h-6 w-6 bg-orange-100 rounded-lg flex items-center justify-center mt-0.5">
                  <span class="text-orange-600 font-semibold text-xs">2</span>
                </div>
                <div>
                  <p class="font-medium text-gray-900">Identify Risks</p>
                  <p class="text-gray-600">Use multiple methodologies to identify risks</p>
                </div>
              </div>
              <div class="flex items-start space-x-3">
                <div class="flex-shrink-0 h-6 w-6 bg-green-100 rounded-lg flex items-center justify-center mt-0.5">
                  <span class="text-green-600 font-semibold text-xs">3</span>
                </div>
                <div>
                  <p class="font-medium text-gray-900">Assess & Prioritize</p>
                  <p class="text-gray-600">Evaluate impact and likelihood for prioritization</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- No Results State -->
      <div v-else-if="filteredAssessments.length === 0" class="px-6 py-12 text-center">
        <SearchIcon class="mx-auto h-12 w-12 text-gray-400 mb-4" />
        <h3 class="text-lg font-medium text-gray-900 mb-2">No assessments found</h3>
        <p class="text-gray-600 mb-6">
          Try adjusting your search or filter criteria to find the assessments you're looking for.
        </p>
        <div class="p-1">
          <Button
            variant="solid"
            theme="gray"
            @click="clearFilters"
          >
            Clear Filters
          </Button>
        </div>
      </div>
    </div>

    <!-- Templates Modal -->
    <Dialog
      v-model="showTemplatesModal"
      title="Assessment Templates"
      :options="{ size: 'custom', width: '70vw' }"
    >
      <template #body>
        <div class="space-y-6 p-6 bg-gray-50">
          <div class="bg-red-50 border border-red-200 rounded-lg p-4">
            <p class="text-red-800 text-sm">
              💡 <strong>Pro Tip:</strong> Templates provide a structured starting point with predefined risk categories and assessment methodologies.
            </p>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6">
            <div class="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-lg hover:border-red-300 cursor-pointer transition-all duration-200 group">
              <div class="flex items-start space-x-4 mb-5">
                <div class="flex-shrink-0 p-3 bg-red-50 rounded-xl group-hover:bg-red-100 transition-colors">
                  <AlertTriangleIcon class="h-6 w-6 text-red-600" />
                </div>
                <div class="flex-1">
                  <h3 class="font-bold text-gray-900 text-lg mb-2 group-hover:text-red-900 transition-colors">Comprehensive Risk Assessment</h3>
                  <p class="text-gray-600 text-sm leading-relaxed">Complete risk assessment covering all major risk categories</p>
                </div>
              </div>

              <div class="mb-6">
                <h4 class="text-sm font-semibold text-gray-900 mb-3">Includes:</h4>
                <ul class="text-sm text-gray-600 space-y-2">
                  <li class="flex items-center space-x-2">
                    <div class="h-1.5 w-1.5 bg-red-400 rounded-full"></div>
                    <span>Strategic risks</span>
                  </li>
                  <li class="flex items-center space-x-2">
                    <div class="h-1.5 w-1.5 bg-red-400 rounded-full"></div>
                    <span>Operational risks</span>
                  </li>
                  <li class="flex items-center space-x-2">
                    <div class="h-1.5 w-1.5 bg-red-400 rounded-full"></div>
                    <span>Financial risks</span>
                  </li>
                  <li class="flex items-center space-x-2">
                    <div class="h-1.5 w-1.5 bg-red-400 rounded-full"></div>
                    <span>Compliance risks</span>
                  </li>
                </ul>
              </div>

              <Button
                variant="solid"
                theme="red"
                size="md"
                class="w-full shadow-sm hover:shadow-md transition-shadow"
              >
                <template #prefix>
                  <PlusIcon class="h-4 w-4" />
                </template>
                Use This Template
              </Button>
            </div>

            <div class="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-lg hover:border-orange-300 cursor-pointer transition-all duration-200 group">
              <div class="flex items-start space-x-4 mb-5">
                <div class="flex-shrink-0 p-3 bg-orange-50 rounded-xl group-hover:bg-orange-100 transition-colors">
                  <BarChart3Icon class="h-6 w-6 text-orange-600" />
                </div>
                <div class="flex-1">
                  <h3 class="font-bold text-gray-900 text-lg mb-2 group-hover:text-orange-900 transition-colors">IT Risk Assessment</h3>
                  <p class="text-gray-600 text-sm leading-relaxed">Technology-focused risk assessment with cybersecurity emphasis</p>
                </div>
              </div>

              <div class="mb-6">
                <h4 class="text-sm font-semibold text-gray-900 mb-3">Includes:</h4>
                <ul class="text-sm text-gray-600 space-y-2">
                  <li class="flex items-center space-x-2">
                    <div class="h-1.5 w-1.5 bg-orange-400 rounded-full"></div>
                    <span>Cybersecurity risks</span>
                  </li>
                  <li class="flex items-center space-x-2">
                    <div class="h-1.5 w-1.5 bg-orange-400 rounded-full"></div>
                    <span>Data privacy risks</span>
                  </li>
                  <li class="flex items-center space-x-2">
                    <div class="h-1.5 w-1.5 bg-orange-400 rounded-full"></div>
                    <span>System availability risks</span>
                  </li>
                  <li class="flex items-center space-x-2">
                    <div class="h-1.5 w-1.5 bg-orange-400 rounded-full"></div>
                    <span>Technology change risks</span>
                  </li>
                </ul>
              </div>

              <Button
                variant="solid"
                theme="gray"
                size="md"
                class="w-full shadow-sm hover:shadow-md transition-shadow bg-orange-500 hover:bg-orange-600 text-white border-orange-500"
              >
                <template #prefix>
                  <BarChart3Icon class="h-4 w-4" />
                </template>
                Use This Template
              </Button>
            </div>
          </div>
        </div>
      </template>
    </Dialog>

    <!-- Bulk Actions Modal -->
    <Dialog
      v-model="showBulkModal"
      title="Bulk Actions"
      size="xl"
    >
      <template #body>
        <div class="space-y-6">
          <div class="bg-red-50 border border-red-200 rounded-lg p-4">
            <p class="text-red-800">
              <span class="font-semibold">{{ selectedAssessments.length }}</span> assessment(s) selected for bulk action.
            </p>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="p-1">
              <Button
                variant="solid"
                theme="gray"
                class="h-20 w-full"
                @click="bulkUpdateStatus"
              >
                <div class="flex flex-col items-center justify-center space-y-2">
                  <CheckCircleIcon class="h-5 w-5" />
                  <span class="text-sm font-medium">Update Status</span>
                </div>
              </Button>
            </div>

            <div class="p-1">
              <Button
                variant="solid"
                theme="gray"
                class="h-20 w-full"
                @click="bulkExport"
              >
                <div class="flex flex-col items-center justify-center space-y-2">
                  <DownloadIcon class="h-5 w-5" />
                  <span class="text-sm font-medium">Export Selected</span>
                </div>
              </Button>
            </div>

            <div class="p-1">
              <Button
                variant="solid"
                theme="gray"
                class="h-20 w-full"
                @click="bulkGenerateReport"
              >
                <div class="flex flex-col items-center justify-center space-y-2">
                  <FileTextIcon class="h-5 w-5" />
                  <span class="text-sm font-medium">Generate Reports</span>
                </div>
              </Button>
            </div>

            <div class="p-1">
              <Button
                variant="solid"
                theme="red"
                class="h-20 w-full"
                @click="bulkDelete"
              >
                <div class="flex flex-col items-center justify-center space-y-2">
                  <TrashIcon class="h-5 w-5" />
                  <span class="text-sm font-medium">Delete Selected</span>
                </div>
              </Button>
            </div>
          </div>
        </div>
      </template>
    </Dialog>

    <!-- Risk Analytics Modal -->
    <Dialog
      v-model="showAnalyticsModal"
      title="Risk Analytics Dashboard"
      size="5xl"
    >
      <template #body>
        <div class="space-y-6">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="bg-red-50 rounded-lg p-6">
              <h3 class="text-lg font-semibold text-red-900 mb-4">Risk Distribution</h3>
              <div class="space-y-3">
                <div class="flex justify-between">
                  <span class="text-red-700">Critical Risks</span>
                  <span class="font-medium text-red-900">{{ criticalRiskCount }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-red-700">High Risks</span>
                  <span class="font-medium text-red-900">{{ highRiskCount }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-red-700">Medium Risks</span>
                  <span class="font-medium text-red-900">{{ mediumRiskCount }}</span>
                </div>
              </div>
            </div>

            <div class="bg-orange-50 rounded-lg p-6">
              <h3 class="text-lg font-semibold text-orange-900 mb-4">Assessment Progress</h3>
              <div class="space-y-3">
                <div class="flex justify-between">
                  <span class="text-orange-700">Completed</span>
                  <span class="font-medium text-orange-900">{{ approvedCount }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-orange-700">In Progress</span>
                  <span class="font-medium text-orange-900">{{ inProgressCount }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-orange-700">Planning</span>
                  <span class="font-medium text-orange-900">{{ planningCount }}</span>
                </div>
              </div>
            </div>

            <div class="bg-gray-50 rounded-lg p-6">
              <h3 class="text-lg font-semibold text-gray-900 mb-4">Risk Trends</h3>
              <div class="space-y-3">
                <div class="flex justify-between">
                  <span class="text-gray-700">Average Score</span>
                  <span class="font-medium text-gray-900">{{ averageRiskScore }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-700">Trend</span>
                  <span class="font-medium text-gray-900">{{ riskTrend }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-700">Top Category</span>
                  <span class="font-medium text-gray-900">{{ topRiskCategory }}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="bg-white border border-gray-200 rounded-lg p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Risk Heat Map</h3>
            <div class="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
              <p class="text-gray-500">Risk heat map visualization would be displayed here</p>
            </div>
          </div>
        </div>
      </template>
    </Dialog>

    <!-- Risk Assessment Form Modal -->
    <RiskAssessmentForm
      v-model="showFormModal"
      :assessment="editingAssessment"
      :mode="formMode"
      @submit="handleFormSubmit"
      @cancel="handleFormCancel"
    />
  </div>
</template>

<script setup>
import RiskAssessmentFilters from "@/components/risk/RiskAssessmentFilters.vue"
import RiskAssessmentForm from "@/components/risk/RiskAssessmentForm.vue"
import RiskAssessmentStats from "@/components/risk/RiskAssessmentStats.vue"
import { useAuditStore } from "@/stores/audit"
import { Badge, Button, Dialog, FormControl, Select } from "frappe-ui"
import {
	AlertCircleIcon,
	AlertTriangleIcon,
	ArrowUpDownIcon,
	BarChart3Icon,
	CheckCircleIcon,
	CopyIcon,
	DownloadIcon,
	EditIcon,
	EyeIcon,
	FileTextIcon,
	LayersIcon,
	LayoutGridIcon,
	MoreHorizontalIcon,
	PlusIcon,
	RefreshCwIcon,
	SearchIcon,
	TableIcon,
	TrashIcon,
} from "lucide-vue-next"
import { computed, onMounted, ref, watch } from "vue"
import { useRouter } from "vue-router"

const router = useRouter()
const auditStore = useAuditStore()

// Reactive state
const loading = ref(false)
const saving = ref(false)
const exporting = ref(false)
const showTemplatesModal = ref(false)
const showBulkModal = ref(false)
const showAnalyticsModal = ref(false)
const showCreateModal = ref(false)
const showFormModal = ref(false)
const editingAssessment = ref(null)
const formMode = ref("create") // 'create' or 'edit'

// UI state
const viewMode = ref("table") // 'table' or 'cards'
const searchQuery = ref("")
const filterStatus = ref("")
const filterPeriod = ref("")
const filterYear = ref("")
const selectedAssessments = ref([])
const sortField = ref("assessment_id")
const sortDirection = ref("asc")

// Options
const periodOptions = [
	{ label: "Annual", value: "Annual" },
	{ label: "Mid-Year", value: "Mid-Year" },
	{ label: "Quarterly", value: "Quarterly" },
	{ label: "Ad-hoc", value: "Ad-hoc" },
]

const statusOptions = [
	{ label: "Planning", value: "Planning" },
	{ label: "In Progress", value: "In Progress" },
	{ label: "Review", value: "Review" },
	{ label: "Finalized", value: "Finalized" },
	{ label: "Approved", value: "Approved" },
]

const methodologyOptions = [
	{ label: "Interview", value: "interview" },
	{ label: "Workshop", value: "workshop" },
	{ label: "Survey", value: "survey" },
	{ label: "Document Review", value: "document_review" },
	{ label: "Data Analysis", value: "data_analysis" },
]

const actionStatusOptions = [
	{ label: "Planned", value: "Planned" },
	{ label: "In Progress", value: "In Progress" },
	{ label: "Completed", value: "Completed" },
	{ label: "Overdue", value: "Overdue" },
]

const priorityOptions = [
	{ label: "Low", value: "Low" },
	{ label: "Medium", value: "Medium" },
	{ label: "High", value: "High" },
	{ label: "Critical", value: "Critical" },
]

// Computed properties
const riskAssessments = computed(() => auditStore.riskAssessments || [])

const criticalRiskCount = computed(() => {
	return riskAssessments.value.reduce((count, assessment) => {
		return (
			count +
			(assessment.top_risks?.filter((risk) => risk.inherent_risk_score >= 20)
				.length || 0)
		)
	}, 0)
})

const highRiskCount = computed(() => {
	return riskAssessments.value.reduce((count, assessment) => {
		return (
			count +
			(assessment.top_risks?.filter(
				(risk) =>
					risk.inherent_risk_score >= 15 && risk.inherent_risk_score < 20,
			).length || 0)
		)
	}, 0)
})

const approvedCount = computed(() => {
	return riskAssessments.value.filter(
		(assessment) => assessment.status === "Approved",
	).length
})

const averageRiskScore = computed(() => {
	const assessments = riskAssessments.value
	if (assessments.length === 0) return 0

	const totalScore = assessments.reduce((sum, assessment) => {
		return sum + getAverageRiskScore(assessment)
	}, 0)

	return Math.round(totalScore / assessments.length)
})

// Aggregated stats for the stats component
const statsData = computed(() => ({
	total: riskAssessments.value.length,
	criticalRisks: criticalRiskCount.value,
	highRisks: highRiskCount.value,
	approved: approvedCount.value,
	averageRiskScore: averageRiskScore.value,
}))

const mediumRiskCount = computed(() => {
	return riskAssessments.value.reduce((count, assessment) => {
		return (
			count +
			(assessment.top_risks?.filter(
				(risk) =>
					risk.inherent_risk_score >= 10 && risk.inherent_risk_score < 15,
			).length || 0)
		)
	}, 0)
})

const inProgressCount = computed(() => {
	return riskAssessments.value.filter(
		(assessment) => assessment.status === "In Progress",
	).length
})

const planningCount = computed(() => {
	return riskAssessments.value.filter(
		(assessment) => assessment.status === "Planning",
	).length
})

const riskTrend = computed(() => {
	// Simple trend calculation - in a real app this would be more sophisticated
	return averageRiskScore.value > 15 ? "Increasing" : "Stable"
})

const topRiskCategory = computed(() => {
	// Simple calculation - in a real app this would analyze actual risk categories
	return "Operational"
})

const yearOptions = computed(() => {
	const currentYear = new Date().getFullYear()
	const years = []
	for (let i = currentYear - 2; i <= currentYear + 2; i++) {
		years.push({ label: i.toString(), value: i.toString() })
	}
	return years
})

const filteredAssessments = computed(() => {
	let assessments = riskAssessments.value

	// Search filter
	if (searchQuery.value) {
		const query = searchQuery.value.toLowerCase()
		assessments = assessments.filter(
			(a) =>
				a.assessment_id?.toLowerCase().includes(query) ||
				a.assessment_name?.toLowerCase().includes(query) ||
				a.assessment_period?.toLowerCase().includes(query),
		)
	}

	// Status filter
	if (filterStatus.value) {
		assessments = assessments.filter((a) => a.status === filterStatus.value)
	}

	// Period filter
	if (filterPeriod.value) {
		assessments = assessments.filter(
			(a) => a.assessment_period === filterPeriod.value,
		)
	}

	// Year filter
	if (filterYear.value) {
		assessments = assessments.filter((a) => a.fiscal_year === filterYear.value)
	}

	return assessments
})

// Methods
const clearFilters = () => {
	searchQuery.value = ""
	filterStatus.value = ""
	filterPeriod.value = ""
	filterYear.value = ""
}

const exportAssessments = () => {
	exporting.value = true
	try {
		const data = filteredAssessments.value.map((assessment) => ({
			"Assessment ID": assessment.assessment_id,
			"Assessment Name": assessment.assessment_name,
			Period: assessment.assessment_period,
			Year: assessment.fiscal_year,
			Date: formatDate(assessment.assessment_date),
			Status: assessment.status,
			"Total Risks": assessment.risk_register?.length || 0,
			"Critical Risks": assessment.top_risks?.length || 0,
			"Average Risk Score": getAverageRiskScore(assessment),
		}))

		const csv = [
			Object.keys(data[0]).join(","),
			...data.map((row) =>
				Object.values(row)
					.map((val) => `"${val}"`)
					.join(","),
			),
		].join("\n")

		const blob = new Blob([csv], { type: "text/csv" })
		const url = window.URL.createObjectURL(blob)
		const a = document.createElement("a")
		a.href = url
		a.download = `risk-assessments-${new Date().toISOString().split("T")[0]}.csv`
		a.click()
		window.URL.revokeObjectURL(url)
	} finally {
		exporting.value = false
	}
}

const selectAllAssessments = () => {
	if (selectedAssessments.value.length === filteredAssessments.value.length) {
		selectedAssessments.value = []
	} else {
		selectedAssessments.value = filteredAssessments.value.map((a) => a.name)
	}
}

const toggleAssessmentSelection = (assessmentId) => {
	const index = selectedAssessments.value.indexOf(assessmentId)
	if (index > -1) {
		selectedAssessments.value.splice(index, 1)
	} else {
		selectedAssessments.value.push(assessmentId)
	}
}

const sortBy = (field) => {
	if (sortField.value === field) {
		sortDirection.value = sortDirection.value === "asc" ? "desc" : "asc"
	} else {
		sortField.value = field
		sortDirection.value = "asc"
	}
}

const getAverageRiskScore = (assessment) => {
	if (!assessment.top_risks || assessment.top_risks.length === 0) return 0
	const totalScore = assessment.top_risks.reduce(
		(sum, risk) => sum + (risk.inherent_risk_score || 0),
		0,
	)
	return Math.round(totalScore / assessment.top_risks.length)
}

const getRiskScoreColor = (score) => {
	if (score >= 20) return "bg-red-500"
	if (score >= 15) return "bg-orange-500"
	if (score >= 10) return "bg-yellow-500"
	return "bg-green-500"
}

const showAssessmentMenu = (assessment, event) => {
	// Placeholder for context menu functionality
	console.log("Show menu for assessment:", assessment.name)
}

const bulkUpdateStatus = () => {
	// Placeholder for bulk status update
	console.log("Bulk update status for selected assessments")
}

const bulkExport = () => {
	// Placeholder for bulk export
	console.log("Bulk export selected assessments")
}

const bulkGenerateReport = () => {
	// Placeholder for bulk report generation
	console.log("Generate reports for selected assessments")
}

const bulkDelete = () => {
	// Placeholder for bulk delete
	console.log("Bulk delete selected assessments")
}

const createNewAssessment = () => {
	editingAssessment.value = null
	formMode.value = "create"
	showFormModal.value = true
}

const viewAssessment = (assessment) => {
	router.push(`/audit-planning/risk-assessment/${assessment.name}`)
}

const editAssessment = (assessment) => {
	editingAssessment.value = assessment
	formMode.value = "edit"
	showFormModal.value = true
}

const handleFormSubmit = async (formData) => {
	try {
		saving.value = true
		if (formMode.value === "create") {
			await auditStore.createRiskAssessment(formData)
		} else {
			await auditStore.updateRiskAssessment(editingAssessment.value.name, formData)
		}
		showFormModal.value = false
		await refreshData()
	} catch (error) {
		console.error("Error saving assessment:", error)
	} finally {
		saving.value = false
	}
}

const handleFormCancel = () => {
	showFormModal.value = false
	editingAssessment.value = null
}

const refreshData = async () => {
	loading.value = true
	try {
		await auditStore.fetchRiskAssessments()
	} catch (error) {
		console.error("Error refreshing data:", error)
	} finally {
		loading.value = false
	}
}

const duplicateAssessment = async (assessment) => {
	try {
		const assessmentDetails = await auditStore.fetchRiskAssessmentDetails(
			assessment.name,
		)
		if (assessmentDetails) {
			// For now, just navigate to new assessment - in future could pre-populate
			router.push("/audit-planning/risk-assessment/new")
		}
	} catch (error) {
		console.error("Error duplicating assessment:", error)
	}
}

const formatDate = (dateString) => {
	if (!dateString) return ""
	return new Date(dateString).toLocaleDateString()
}

const getStatusVariant = (status) => {
	const variants = {
		Planning: "secondary",
		"In Progress": "warning",
		Review: "info",
		Finalized: "success",
		Approved: "success",
	}
	return variants[status] || "secondary"
}

// Watchers
watch(filteredAssessments, () => {
	selectedAssessments.value = []
})

watch(searchQuery, () => {
	// Reset to first page when searching
})

watch(filterStatus, () => {
	selectedAssessments.value = []
})

watch(filterPeriod, () => {
	selectedAssessments.value = []
})

watch(filterYear, () => {
	selectedAssessments.value = []
})
</script>