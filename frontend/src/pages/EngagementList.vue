<template>
  <div class="space-y-6">
    <!-- Page Header with Enhanced Actions -->
    <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
      <div>
        <div class="flex items-center space-x-3">
          <div class="p-2 bg-green-100 rounded-lg">
            <FileTextIcon class="h-6 w-6 text-green-600" />
          </div>
          <div>
            <h1 class="text-2xl font-bold text-gray-900">Audit Engagements</h1>
            <p class="text-gray-600 mt-1">
              Manage and track audit engagements throughout their lifecycle
            </p>
          </div>
        </div>
      </div>

      <div class="flex flex-wrap items-center gap-3">
        <!-- Action Buttons -->
        <div class="p-1">
          <Button
            variant="solid"
            theme="gray"
            size="sm"
            @click="exportEngagements"
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
            @click="showTemplateModal = true"
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
            theme="green"
            size="sm"
            @click="createNewEngagement"
          >
            <template #prefix>
              <PlusIcon class="h-3.5 w-3.5" />
            </template>
            New Engagement
          </Button>
        </div>
      </div>
    </div>

    <!-- Enhanced Stats Dashboard -->
    <EngagementStats :engagements="engagements" />

    <!-- Quick Actions Bar -->
    <div class="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
      <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <!-- Left Section: Search and Filters -->
        <div class="flex flex-col sm:flex-row gap-4 flex-1">
          <!-- Search Input -->
          <div class="relative flex-1 max-w-md">
            <SearchIcon class="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              v-model="filters.search"
              type="text"
              placeholder="Search engagements..."
              class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            />
          </div>

          <!-- Filters -->
          <div class="flex gap-2">
            <select
              v-model="filters.status"
              class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            >
              <option value="">All Status</option>
              <option value="Planning">Planning</option>
              <option value="Fieldwork">Fieldwork</option>
              <option value="Reporting">Reporting</option>
              <option value="Management Review">Management Review</option>
              <option value="Quality Review">Quality Review</option>
              <option value="Finalized">Finalized</option>
              <option value="Issued">Issued</option>
            </select>

            <select
              v-model="filters.type"
              class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            >
              <option value="">All Types</option>
              <option value="Financial">Financial</option>
              <option value="Operational">Operational</option>
              <option value="Compliance">Compliance</option>
              <option value="IT">IT</option>
              <option value="Integrated">Integrated</option>
              <option value="Special Investigation">Special Investigation</option>
              <option value="Follow-up">Follow-up</option>
              <option value="Advisory">Advisory</option>
            </select>

            <select
              v-model="filters.auditor"
              class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            >
              <option value="">All Auditors</option>
              <option v-for="auditor in Array.from(new Set(engagements.map(e => e.lead_auditor).filter(Boolean)))" :key="auditor" :value="auditor">
                {{ auditor }}
              </option>
            </select>

            <select
              v-model="filters.approach"
              class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            >
              <option value="">All Approaches</option>
              <option value="Risk-Based">Risk-Based</option>
              <option value="Controls-Based">Controls-Based</option>
              <option value="Substantive">Substantive</option>
              <option value="Compliance">Compliance</option>
              <option value="Combined">Combined</option>
            </select>

            <select
              v-model="filters.opinion"
              class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            >
              <option value="">All Opinions</option>
              <option value="Satisfactory">Satisfactory</option>
              <option value="Satisfactory with Minor Issues">Satisfactory with Minor Issues</option>
              <option value="Needs Improvement">Needs Improvement</option>
              <option value="Unsatisfactory">Unsatisfactory</option>
            </select>
          </div>
        </div>

        <!-- Right Section: View Toggle and Actions -->
        <div class="flex items-center gap-3">
          <!-- View Mode Toggle -->
          <div class="flex items-center bg-gray-100 rounded-lg p-1">
            <button
              @click="viewMode = 'table'"
              :class="[
                'px-3 py-1.5 rounded-md text-sm font-medium transition-colors',
                viewMode === 'table'
                  ? 'bg-white text-green-700 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              ]"
            >
              <TableIcon class="h-4 w-4 inline mr-1" />
              Table
            </button>
            <button
              @click="viewMode = 'cards'"
              :class="[
                'px-3 py-1.5 rounded-md text-sm font-medium transition-colors',
                viewMode === 'cards'
                  ? 'bg-white text-green-700 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              ]"
            >
              <GridIcon class="h-4 w-4 inline mr-1" />
              Cards
            </button>
          </div>

          <!-- Action Buttons -->
          <Button
            @click="showTemplatesModal = true"
            variant="outline"
            class="flex items-center gap-2"
          >
            <FileTextIcon class="h-4 w-4" />
            Templates
          </Button>

          <Button
            @click="showBulkActionsModal = true"
            variant="outline"
            class="flex items-center gap-2"
            :disabled="selectedEngagements.length === 0"
          >
            <LayersIcon class="h-4 w-4" />
            Bulk Actions
          </Button>

          <Button
            @click="createNewEngagement"
            variant="solid"
            class="flex items-center gap-2 bg-green-600 hover:bg-green-700"
          >
            <PlusIcon class="h-4 w-4" />
            New Engagement
          </Button>
        </div>
      </div>
    </div>

    <!-- Main Content Area -->
    <div class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
      <!-- Header Controls -->
      <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <Checkbox
              :modelValue="selectAll"
              @update:modelValue="toggleSelectAll"
            />
            <span class="text-sm font-medium text-gray-700">
              {{ selectedEngagements.length }} of {{ filteredEngagements.length }} selected
            </span>
          </div>
          <div class="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              @click="sortBy = sortBy === 'period_start' ? 'period_end' : 'period_start'"
            >
              <ArrowUpDownIcon class="h-4 w-4 mr-2" />
              Sort by {{ sortBy === 'period_start' ? 'End Date' : 'Start Date' }}
            </Button>
          </div>
        </div>
      </div>

      <!-- Card View -->
      <div v-if="viewMode === 'cards'" class="p-6">
        <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          <div
            v-for="engagement in paginatedEngagements"
            :key="engagement.name"
            class="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow cursor-pointer"
            :class="{ 'ring-2 ring-green-500': selectedEngagements.includes(engagement.name) }"
            @click="viewEngagement(engagement)"
          >
            <!-- Card Header -->
            <div class="flex items-start justify-between mb-4">
              <div class="flex-1">
                <h3 class="text-lg font-semibold text-gray-900 mb-1">
                  {{ engagement.engagement_title || 'Untitled' }}
                </h3>
                <p class="text-sm text-gray-600 mb-2">{{ engagement.engagement_id }}</p>
                <div class="flex items-center space-x-2">
                  <Badge :theme="getAuditTypeTheme(engagement.audit_type)">
                    {{ engagement.audit_type }}
                  </Badge>
                  <Badge :theme="getStatusTheme(engagement.status)">
                    {{ engagement.status }}
                  </Badge>
                </div>
              </div>
              <Checkbox
                :modelValue="selectedEngagements.includes(engagement.name)"
                @update:modelValue="toggleEngagementSelection(engagement.name)"
                @click.stop
              />
            </div>

            <!-- Card Content -->
            <div class="space-y-3">
              <!-- Lead Auditor & Universe -->
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <p class="text-xs text-gray-500 uppercase tracking-wide">Lead Auditor</p>
                  <p class="text-sm font-medium text-gray-900">{{ engagement.lead_auditor || 'Unassigned' }}</p>
                </div>
                <div>
                  <p class="text-xs text-gray-500 uppercase tracking-wide">Audit Universe</p>
                  <p class="text-sm font-medium text-gray-900">{{ engagement.audit_universe || 'N/A' }}</p>
                </div>
              </div>

              <!-- Period & Approach -->
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <p class="text-xs text-gray-500 uppercase tracking-wide">Period</p>
                  <p class="text-sm font-medium text-gray-900">
                    {{ formatDate(engagement.period_start) }} - {{ formatDate(engagement.period_end) }}
                  </p>
                </div>
                <div>
                  <p class="text-xs text-gray-500 uppercase tracking-wide">Approach</p>
                  <Badge theme="gray">{{ engagement.audit_approach || 'Not Set' }}</Badge>
                </div>
              </div>

              <!-- Budget & Findings -->
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <p class="text-xs text-gray-500 uppercase tracking-wide">Budget Hours</p>
                  <p class="text-sm font-medium text-gray-900">
                    {{ engagement.budgeted_hours || 0 }}h
                    <span v-if="engagement.actual_hours" class="text-xs text-gray-500">
                      ({{ engagement.actual_hours }}h used)
                    </span>
                  </p>
                </div>
                <div>
                  <p class="text-xs text-gray-500 uppercase tracking-wide">Findings</p>
                  <div class="flex items-center space-x-2">
                    <span class="text-sm font-medium text-gray-900">{{ engagement.findings_count || 0 }}</span>
                    <span v-if="engagement.high_risk_findings_count" class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                      {{ engagement.high_risk_findings_count }} High
                    </span>
                  </div>
                </div>
              </div>

              <!-- Opinion -->
              <div v-if="engagement.overall_audit_opinion">
                <p class="text-xs text-gray-500 uppercase tracking-wide">Audit Opinion</p>
                <Badge :theme="getOpinionTheme(engagement.overall_audit_opinion)">
                  {{ engagement.overall_audit_opinion }}
                </Badge>
              </div>
            </div>

            <!-- Card Actions -->
            <div class="flex items-center justify-end space-x-2 mt-4 pt-4 border-t border-gray-200">
              <Button
                variant="ghost"
                size="sm"
                @click.stop="viewEngagement(engagement)"
              >
                <EyeIcon class="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                @click.stop="editEngagement(engagement)"
              >
                <EditIcon class="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                @click.stop="deleteEngagement(engagement)"
                theme="red"
              >
                <TrashIcon class="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>

      <!-- Table Content -->
      <div v-if="viewMode === 'table'" class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                <Checkbox
                  :modelValue="selectAll"
                  @update:modelValue="toggleSelectAll"
                />
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Engagement ID
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Title
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Type
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Lead Auditor
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Audit Universe
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Approach
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Period
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Budget Hours
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Opinion
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Findings
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr
              v-for="engagement in paginatedEngagements"
              :key="engagement.name"
              class="hover:bg-gray-50 transition-colors"
              :class="{ 'bg-green-50': selectedEngagements.includes(engagement.name) }"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <Checkbox
                  :modelValue="selectedEngagements.includes(engagement.name)"
                  @update:modelValue="toggleEngagementSelection(engagement.name)"
                />
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="flex-shrink-0 h-10 w-10">
                    <div class="h-10 w-10 rounded-full bg-gray-200 flex items-center justify-center">
                      <FileTextIcon class="h-5 w-5 text-gray-600" />
                    </div>
                  </div>
                  <div class="ml-4">
                    <div class="text-sm font-medium text-gray-900">
                      {{ engagement.engagement_id }}
                    </div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">
                  {{ engagement.engagement_title || 'Untitled' }}
                </div>
                <div class="text-sm text-gray-500">
                  {{ engagement.audit_universe || 'No universe specified' }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <Badge :theme="getAuditTypeTheme(engagement.audit_type)">
                  {{ engagement.audit_type }}
                </Badge>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <Badge :theme="getStatusTheme(engagement.status)">
                  {{ engagement.status }}
                </Badge>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ engagement.lead_auditor || 'Unassigned' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ engagement.audit_universe || 'N/A' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <Badge theme="gray">
                  {{ engagement.audit_approach || 'Not Set' }}
                </Badge>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                <div>{{ formatDate(engagement.period_start) }}</div>
                <div class="text-xs text-gray-500">to {{ formatDate(engagement.period_end) }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                <div class="flex items-center">
                  <span class="font-medium">{{ engagement.budgeted_hours || 0 }}h</span>
                  <span v-if="engagement.actual_hours" class="text-xs text-gray-500 ml-1">
                    ({{ engagement.actual_hours }}h used)
                  </span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <Badge v-if="engagement.overall_audit_opinion" :theme="getOpinionTheme(engagement.overall_audit_opinion)">
                  {{ engagement.overall_audit_opinion }}
                </Badge>
                <span v-else class="text-sm text-gray-400">Pending</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center space-x-2">
                  <span class="text-sm font-medium text-gray-900">{{ engagement.findings_count || 0 }}</span>
                  <span v-if="engagement.high_risk_findings_count" class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                    {{ engagement.high_risk_findings_count }} High
                  </span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div class="flex items-center space-x-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    @click="viewEngagement(engagement)"
                  >
                    <EyeIcon class="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    @click="editEngagement(engagement)"
                  >
                    <EditIcon class="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    @click="deleteEngagement(engagement)"
                    theme="red"
                  >
                    <TrashIcon class="h-4 w-4" />
                  </Button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div class="px-6 py-4 border-t border-gray-200 bg-gray-50">
        <div class="flex items-center justify-between">
          <div class="text-sm text-gray-700">
            Showing {{ (currentPage - 1) * itemsPerPage + 1 }} to {{ Math.min(currentPage * itemsPerPage, filteredEngagements.length) }} of {{ filteredEngagements.length }} results
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
            <span class="text-sm text-gray-700">
              Page {{ currentPage }} of {{ totalPages }}
            </span>
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

    <!-- Empty State -->
    <div
      v-if="filteredEngagements.length === 0"
      class="text-center py-12 bg-white rounded-xl border border-gray-200"
    >
      <FileTextIcon class="mx-auto h-12 w-12 text-gray-400" />
      <h3 class="mt-2 text-sm font-medium text-gray-900">No engagements found</h3>
      <p class="mt-1 text-sm text-gray-500">
        {{ filters.search || filters.status || filters.type || filters.auditor ? 'No engagements match your current filters.' : 'Get started by creating your first audit engagement.' }}
      </p>
      <div class="mt-6">
        <Button
          @click="createNewEngagement"
          class="bg-green-600 hover:bg-green-700 text-white"
        >
          <PlusIcon class="h-4 w-4 mr-2" />
          Create Engagement
        </Button>
      </div>
    </div>

	<!-- Templates Modal -->
	<Dialog v-model="showTemplatesModal" :options="{ title: 'Apply Template' }">
		<template #body-content>
			<div class="space-y-4">
				<p class="text-sm text-gray-600">
					Select a template to apply to the selected engagements:
				</p>
				<div class="space-y-2">
					<label class="flex items-center space-x-2">
						<input type="radio" v-model="selectedTemplate" value="financial-audit" class="text-blue-600">
						<span class="text-sm">Financial Audit Template</span>
					</label>
					<label class="flex items-center space-x-2">
						<input type="radio" v-model="selectedTemplate" value="operational-audit" class="text-blue-600">
						<span class="text-sm">Operational Audit Template</span>
					</label>
					<label class="flex items-center space-x-2">
						<input type="radio" v-model="selectedTemplate" value="compliance-audit" class="text-blue-600">
						<span class="text-sm">Compliance Audit Template</span>
					</label>
					<label class="flex items-center space-x-2">
						<input type="radio" v-model="selectedTemplate" value="it-audit" class="text-blue-600">
						<span class="text-sm">IT Audit Template</span>
					</label>
				</div>
			</div>
		</template>
		<template #actions>
			<Button variant="ghost" @click="showTemplatesModal = false">
				Cancel
			</Button>
			<Button variant="solid" @click="applyTemplate" :disabled="!selectedTemplate">
				Apply Template
			</Button>
		</template>
	</Dialog>

	<!-- Bulk Actions Modal -->
	<Dialog v-model="showBulkActionsModal" :options="{ title: 'Bulk Actions' }">
		<template #body-content>
			<div class="space-y-4">
				<p class="text-sm text-gray-600">
					Apply bulk action to {{ selectedEngagements.length }} selected engagements:
				</p>
				<div class="space-y-3">
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-1">
							Update Status
						</label>
						<Select v-model="bulkStatusUpdate" :options="statusOptions" />
					</div>
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-1">
							Assign Auditor
						</label>
						<Select v-model="bulkAuditorUpdate" :options="auditorOptions" />
					</div>
					<div class="flex items-center space-x-2">
						<Checkbox v-model="bulkDeleteConfirm" />
						<span class="text-sm text-red-600">
							Delete selected engagements (this action cannot be undone)
						</span>
					</div>
				</div>
			</div>
		</template>
		<template #actions>
			<Button variant="ghost" @click="showBulkActionsModal = false">
				Cancel
			</Button>
			<Button variant="solid" @click="applyBulkActions" :disabled="!bulkStatusUpdate && !bulkAuditorUpdate && !bulkDeleteConfirm">
				Apply Changes
			</Button>
		</template>
	</Dialog>

	<!-- Capacity Planning Modal -->
	<Dialog v-model="showCapacityModal" :options="{ title: 'Capacity Planning' }">
		<template #body-content>
			<div class="space-y-4">
				<div class="grid grid-cols-2 gap-4">
					<div class="bg-blue-50 p-4 rounded-lg">
						<h4 class="font-medium text-blue-900">Current Capacity</h4>
						<p class="text-2xl font-bold text-blue-600">{{ currentCapacity }}</p>
						<p class="text-sm text-blue-700">Active engagements</p>
					</div>
					<div class="bg-green-50 p-4 rounded-lg">
						<h4 class="font-medium text-green-900">Available Capacity</h4>
						<p class="text-2xl font-bold text-green-600">{{ availableCapacity }}</p>
						<p class="text-sm text-green-700">Available slots</p>
					</div>
				</div>
				<div class="space-y-2">
					<h4 class="font-medium">Auditor Workload</h4>
					<div class="space-y-2 max-h-40 overflow-y-auto">
						<div v-for="auditor in auditorWorkload" :key="auditor.name" class="flex justify-between items-center p-2 bg-gray-50 rounded">
							<span class="text-sm">{{ auditor.name }}</span>
							<div class="flex items-center space-x-2">
								<div class="w-20 bg-gray-200 rounded-full h-2">
									<div class="bg-blue-600 h-2 rounded-full" :style="{ width: `${auditor.load}%` }"></div>
								</div>
								<span class="text-xs text-gray-600">{{ auditor.load }}%</span>
							</div>
						</div>
					</div>
				</div>
			</div>
		</template>
		<template #actions>
			<Button variant="solid" @click="showCapacityModal = false">
				Close
			</Button>
		</template>
	</Dialog>

	<!-- New Engagement Form Component -->
    <EngagementForm
      v-model="showNewEngagementModal"
      :engagement="editingEngagement"
      @created="handleEngagementCreated"
      @updated="handleEngagementUpdated"
      @cancelled="showNewEngagementModal = false"
    />
</div>
</template>

<script setup>
import { useAuditStore } from "@/stores/audit"
import { Badge, Button, Checkbox, Dialog, FeatherIcon, Select } from "frappe-ui"
import {
	ArrowUpDownIcon,
	BarChart3Icon,
	BarChartIcon,
	CheckCircleIcon,
	ChevronLeftIcon,
	ChevronRightIcon,
	DownloadIcon,
	EditIcon,
	EyeIcon,
	FileTextIcon,
	GridIcon,
	LayersIcon,
	PlayIcon,
	PlusIcon,
	RefreshCwIcon,
	SearchIcon,
	TableIcon,
	TrashIcon,
} from "lucide-vue-next"
import { computed, onMounted, ref } from "vue"
import { useRouter } from "vue-router"

// Import the engagement form component
import EngagementForm from "@/components/engagement/EngagementForm.vue"
import EngagementStats from "@/components/engagements/EngagementStats.vue"

const router = useRouter()
const auditStore = useAuditStore()

// Reactive state
const loading = ref(false)
const filters = ref({
	search: "",
	status: "",
	type: "",
	auditor: "",
	approach: "",
	opinion: "",
})

// New reactive variables for enhanced functionality
const selectedEngagements = ref([])
const sortBy = ref("period_start")
const currentPage = ref(1)
const itemsPerPage = ref(10)
const viewMode = ref("table")
const showBulkModal = ref(false)
const showCapacityModal = ref(false)
const showTemplateModal = ref(false)
const exporting = ref(false)

// Modal reactive variables
const showTemplatesModal = ref(false)
const showBulkActionsModal = ref(false)
const showNewEngagementModal = ref(false)
const selectedTemplate = ref("")
const bulkStatusUpdate = ref("")
const bulkAuditorUpdate = ref("")
const bulkDeleteConfirm = ref(false)

// Engagement form state
const editingEngagement = ref(null)

// Computed properties
const engagements = computed(() => auditStore.engagements)

const filteredEngagements = computed(() => {
	let filtered = engagements.value

	if (filters.value.search) {
		filtered = filtered.filter(
			(engagement) =>
				engagement.engagement_title
					?.toLowerCase()
					.includes(filters.value.search.toLowerCase()) ||
				engagement.engagement_id
					?.toLowerCase()
					.includes(filters.value.search.toLowerCase()),
		)
	}

	if (filters.value.status) {
		filtered = filtered.filter(
			(engagement) => engagement.status === filters.value.status,
		)
	}

	if (filters.value.type) {
		filtered = filtered.filter(
			(engagement) => engagement.audit_type === filters.value.type,
		)
	}

	if (filters.value.approach) {
		filtered = filtered.filter(
			(engagement) => engagement.audit_approach === filters.value.approach,
		)
	}

	if (filters.value.opinion) {
		filtered = filtered.filter(
			(engagement) =>
				engagement.overall_audit_opinion === filters.value.opinion,
		)
	}

	return filtered
})

const columns = [
	{ key: "engagement_id", label: "Engagement ID", sortable: true },
	{ key: "engagement_title", label: "Engagement Title", sortable: true },
	{ key: "audit_type", label: "Type", sortable: true },
	{ key: "status", label: "Status", sortable: true },
	{ key: "lead_auditor", label: "Lead Auditor", sortable: true },
	{ key: "audit_universe", label: "Audit Universe", sortable: true },
	{ key: "audit_approach", label: "Approach", sortable: true },
	{ key: "period_start", label: "Period", sortable: true },
	{ key: "budgeted_hours", label: "Budget Hours", sortable: true },
	{ key: "overall_audit_opinion", label: "Opinion", sortable: true },
	{ key: "findings_count", label: "Findings", sortable: true },
	{ key: "actions", label: "Actions", width: "120px" },
]

const statusOptions = [
	{ label: "All Status", value: "" },
	{ label: "Planning", value: "Planning" },
	{ label: "Fieldwork", value: "Fieldwork" },
	{ label: "Reporting", value: "Reporting" },
	{ label: "Management Review", value: "Management Review" },
	{ label: "Quality Review", value: "Quality Review" },
	{ label: "Finalized", value: "Finalized" },
	{ label: "Issued", value: "Issued" },
]

const typeOptions = [
	{ label: "All Types", value: "" },
	{ label: "Financial", value: "Financial" },
	{ label: "Operational", value: "Operational" },
	{ label: "Compliance", value: "Compliance" },
	{ label: "IT", value: "IT" },
	{ label: "Integrated", value: "Integrated" },
	{ label: "Special Investigation", value: "Special Investigation" },
	{ label: "Follow-up", value: "Follow-up" },
	{ label: "Advisory", value: "Advisory" },
]

const auditorOptions = computed(() => {
	const auditors = new Set()
	engagements.value.forEach((engagement) => {
		if (engagement.lead_auditor) {
			auditors.add(engagement.lead_auditor)
		}
	})

	return [
		{ label: "All Auditors", value: "" },
		...Array.from(auditors).map((auditor) => ({
			label: auditor,
			value: auditor,
		})),
	]
})

// New computed properties for enhanced functionality
const selectAll = computed({
	get: () =>
		filteredEngagements.value.length > 0 &&
		selectedEngagements.value.length === filteredEngagements.value.length,
	set: (value) => {
		if (value) {
			selectedEngagements.value = filteredEngagements.value.map(
				(engagement) => engagement.name,
			)
		} else {
			selectedEngagements.value = []
		}
	},
})

const paginatedEngagements = computed(() => {
	const start = (currentPage.value - 1) * itemsPerPage.value
	const end = start + itemsPerPage.value
	return filteredEngagements.value.slice(start, end)
})

const totalPages = computed(() =>
	Math.ceil(filteredEngagements.value.length / itemsPerPage.value),
)

// Enhanced stats computed properties
const totalEngagements = computed(() => engagements.value.length)

const inProgressCount = computed(
	() => engagements.value.filter((item) => item.status === "Fieldwork").length,
)

const reportingCount = computed(
	() => engagements.value.filter((item) => item.status === "Reporting").length,
)

const completedCount = computed(
	() =>
		engagements.value.filter(
			(item) => item.status === "Issued" || item.status === "Finalized",
		).length,
)

const averageProgress = computed(() => {
	if (engagements.value.length === 0) return 0
	const totalProgress = engagements.value.reduce(
		(sum, engagement) => sum + calculateProgress(engagement),
		0,
	)
	return Math.round(totalProgress / engagements.value.length)
})

const qualityReviewCount = computed(
	() =>
		engagements.value.filter((item) => item.status === "Quality Review").length,
)

const averageQualityScore = computed(() => {
	const scoredEngagements = engagements.value.filter(
		(item) => item.quality_score,
	)
	if (scoredEngagements.length === 0) return 0
	const totalScore = scoredEngagements.reduce(
		(sum, engagement) => sum + (engagement.quality_score || 0),
		0,
	)
	return Math.round(totalScore / scoredEngagements.length)
})

// Capacity planning computed properties
const currentCapacity = computed(
	() => inProgressCount.value + reportingCount.value,
)
const availableCapacity = computed(() =>
	Math.max(0, 20 - currentCapacity.value),
) // Assuming max capacity of 20

const auditorWorkload = computed(() => {
	const workload = {}
	engagements.value.forEach((engagement) => {
		if (engagement.lead_auditor) {
			if (!workload[engagement.lead_auditor]) {
				workload[engagement.lead_auditor] = {
					name: engagement.lead_auditor,
					count: 0,
				}
			}
			workload[engagement.lead_auditor].count++
		}
	})

	return Object.values(workload).map((auditor) => ({
		...auditor,
		load: Math.min(100, Math.round((auditor.count / 5) * 100)), // Assuming max 5 engagements per auditor
	}))
})

// Methods
const getStatusVariant = (status) => {
	const variants = {
		Planning: "secondary",
		Fieldwork: "warning",
		Reporting: "primary",
		"Management Review": "info",
		"Quality Review": "info",
		Finalized: "success",
		Issued: "success",
	}
	return variants[status] || "secondary"
}

const getStatusLabel = (status) => {
	return status || "Planning"
}

const calculateProgress = (engagement) => {
	// Calculate progress based on engagement timeline
	const now = new Date()
	const start = engagement.planning_start
		? new Date(engagement.planning_start)
		: null
	const end = engagement.actual_completion_date
		? new Date(engagement.actual_completion_date)
		: engagement.reporting_end
			? new Date(engagement.reporting_end)
			: engagement.fieldwork_end
				? new Date(engagement.fieldwork_end)
				: null

	if (!start || !end) return 0

	if (now < start) return 0
	if (now > end) return 100

	const total = end - start
	const elapsed = now - start
	return Math.round((elapsed / total) * 100)
}

const onEngagementClick = (engagement) => {
	router.push(`/engagements/${engagement.name}`)
}

const viewEngagement = (engagement) => {
	router.push(`/engagements/${engagement.name}`)
}

const editEngagement = (engagement) => {
	router.push(`/engagements/${engagement.name}/edit`)
}

const deleteEngagement = (engagement) => {
	if (confirm("Are you sure you want to delete this engagement?")) {
		// Delete logic will be implemented
	}
}

// ============================================================================
// ENGAGEMENT FORM HANDLERS
// ============================================================================
const createNewEngagement = () => {
	editingEngagement.value = null
	showNewEngagementModal.value = true
}

const handleEngagementCreated = async (engagement) => {
	showNewEngagementModal.value = false
	editingEngagement.value = null
	await loadEngagements()
}

const handleEngagementUpdated = async (engagement) => {
	showNewEngagementModal.value = false
	editingEngagement.value = null
	await loadEngagements()
}

// Load engagements
const loadEngagements = async () => {
	try {
		loading.value = true
		await auditStore.fetchEngagements()
	} catch (error) {
		console.error("Error loading engagements:", error)
	} finally {
		loading.value = false
	}
}

// Lifecycle
onMounted(() => {
	loadEngagements()
})
</script>