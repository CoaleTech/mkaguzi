<template>
  <div class="space-y-6">
    <!-- Page Header with Enhanced Actions -->
    <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
      <div>
        <div class="flex items-center space-x-3">
          <div class="p-2 bg-gray-100 rounded-lg">
            <FileTextIcon class="h-6 w-6 text-gray-900" />
          </div>
          <div>
            <h1 class="text-2xl font-bold text-gray-900">Working Papers</h1>
            <p class="text-gray-600 mt-1">
              Manage audit working papers and documentation with advanced tracking
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
            @click="exportWorkingPapers"
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
            theme="gray"
            size="sm"
            @click="createNewWorkingPaper"
          >
            <template #prefix>
              <PlusIcon class="h-3.5 w-3.5" />
            </template>
            New Working Paper
          </Button>
        </div>
      </div>
    </div>

    <!-- Enhanced Stats Dashboard -->
    <WorkingPapersStats :working-papers="workingPapers" />

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
              placeholder="Search working papers..."
              class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-900 focus:border-transparent"
            />
          </div>

          <!-- Filters -->
          <div class="flex gap-2">
            <select
              v-model="filters.engagement"
              class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-900 focus:border-transparent"
            >
              <option value="">All Engagements</option>
              <option v-for="engagement in auditStore.engagements" :key="engagement.name" :value="engagement.name">
                {{ engagement.engagement_title }}
              </option>
            </select>

            <select
              v-model="filters.type"
              class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-900 focus:border-transparent"
            >
              <option value="">All Types</option>
              <option value="Planning Memo">Planning Memo</option>
              <option value="Risk Assessment">Risk Assessment</option>
              <option value="Walkthrough">Walkthrough</option>
              <option value="Test of Controls">Test of Controls</option>
              <option value="Substantive Test">Substantive Test</option>
              <option value="Analytical Review">Analytical Review</option>
              <option value="Data Analytics">Data Analytics</option>
              <option value="Summary">Summary</option>
              <option value="Other">Other</option>
            </select>

            <select
              v-model="filters.status"
              class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-900 focus:border-transparent"
            >
              <option value="">All Status</option>
              <option value="Not Reviewed">Not Reviewed</option>
              <option value="Under Review">Under Review</option>
              <option value="Review Complete">Review Complete</option>
              <option value="Revision Required">Revision Required</option>
            </select>

            <select
              v-model="filters.preparedBy"
              class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-900 focus:border-transparent"
            >
              <option value="">All Preparers</option>
              <option v-for="preparer in Array.from(new Set(workingPapers.map(p => p.prepared_by).filter(Boolean)))" :key="preparer" :value="preparer">
                {{ preparer }}
              </option>
            </select>

            <select
              v-model="filters.reviewer"
              class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-900 focus:border-transparent"
            >
              <option value="">All Reviewers</option>
              <option v-for="reviewer in Array.from(new Set(workingPapers.map(p => p.reviewed_by).filter(Boolean)))" :key="reviewer" :value="reviewer">
                {{ reviewer }}
              </option>
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
                  ? 'bg-white text-gray-700 shadow-sm'
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
                  ? 'bg-white text-gray-700 shadow-sm'
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
            :disabled="selectedPapers.length === 0"
          >
            <LayersIcon class="h-4 w-4" />
            Bulk Actions
          </Button>

          <Button
            @click="showCapacityModal = true"
            variant="solid"
            class="flex items-center gap-2 bg-gray-900 hover:bg-gray-800"
          >
            <BarChart3Icon class="h-4 w-4" />
            Capacity
          </Button>

          <Button
            @click="createNewWorkingPaper"
            variant="solid"
            class="flex items-center gap-2 bg-gray-900 hover:bg-gray-800"
          >
            <PlusIcon class="h-4 w-4" />
            New Paper
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
              :modelValue="selectAllPapers"
              @update:modelValue="toggleSelectAllPapers"
            />
            <span class="text-sm font-medium text-gray-700">
              {{ selectedPapers.length }} of {{ filteredWorkingPapers.length }} selected
            </span>
          </div>
          <div class="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              @click="sortBy = sortBy === 'preparation_date' ? 'wp_title' : 'preparation_date'"
            >
              <ArrowUpDownIcon class="h-4 w-4 mr-2" />
              Sort by {{ sortBy === 'preparation_date' ? 'Title' : 'Date' }}
            </Button>
          </div>
        </div>
      </div>

      <!-- Table View -->
      <div v-if="viewMode === 'table'">
        <!-- Table Content -->
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  <Checkbox
                    :modelValue="selectAllPapers"
                    @update:modelValue="toggleSelectAllPapers"
                  />
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  WP ID
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Title
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Engagement
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Prepared By
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date
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
                v-for="paper in paginatedPapers"
                :key="paper.name"
                class="hover:bg-gray-50 transition-colors"
                :class="{ 'bg-gray-50': selectedPapers.includes(paper.name) }"
              >
                <td class="px-6 py-4 whitespace-nowrap">
                  <Checkbox
                    :modelValue="selectedPapers.includes(paper.name)"
                    @update:modelValue="togglePaperSelection(paper.name)"
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
                        {{ paper.working_paper_id }}
                      </div>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm font-medium text-gray-900">
                    {{ paper.wp_title || 'Untitled' }}
                  </div>
                  <div class="text-sm text-gray-500">
                    {{ paper.wp_reference_no || 'No reference' }}
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <Badge :theme="getTypeTheme(paper.wp_type)">
                    {{ paper.wp_type }}
                  </Badge>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ getEngagementTitle(paper.engagement_reference) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ paper.prepared_by || 'Unassigned' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ formatDate(paper.preparation_date) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <Badge :theme="getStatusTheme(paper.review_status)">
                    {{ paper.review_status }}
                  </Badge>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <div class="flex items-center space-x-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      @click="viewWorkingPaper(paper)"
                    >
                      <EyeIcon class="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      @click="editWorkingPaper(paper)"
                    >
                      <EditIcon class="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      @click="duplicateWorkingPaper(paper)"
                      theme="gray"
                    >
                      <CopyIcon class="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      @click="deleteWorkingPaper(paper)"
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
              Showing {{ (currentPage - 1) * itemsPerPage + 1 }} to {{ Math.min(currentPage * itemsPerPage, filteredWorkingPapers.length) }} of {{ filteredWorkingPapers.length }} results
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

      <!-- Card View -->
      <div v-else class="p-6">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div
            v-for="paper in paginatedPapers"
            :key="paper.name"
            class="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow cursor-pointer"
            :class="{ 'ring-2 ring-gray-900 bg-gray-50': selectedPapers.includes(paper.name) }"
            @click="togglePaperSelection(paper.name)"
          >
            <!-- Card Header -->
            <div class="flex items-start justify-between mb-4">
              <div class="flex items-center space-x-3">
                <div class="flex-shrink-0">
                  <div class="h-12 w-12 rounded-lg bg-gray-100 flex items-center justify-center">
                    <FileTextIcon class="h-6 w-6 text-gray-900" />
                  </div>
                </div>
                <div>
                  <h3 class="text-lg font-semibold text-gray-900">
                    {{ paper.wp_title || 'Untitled' }}
                  </h3>
                  <p class="text-sm text-gray-500">{{ paper.working_paper_id }}</p>
                </div>
              </div>
              <Checkbox
                :modelValue="selectedPapers.includes(paper.name)"
                @update:modelValue="togglePaperSelection(paper.name)"
                @click.stop
              />
            </div>

            <!-- Card Content -->
            <div class="space-y-3 mb-4">
              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-600">Type:</span>
                <Badge :theme="getTypeTheme(paper.wp_type)">
                  {{ paper.wp_type }}
                </Badge>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-600">Status:</span>
                <Badge :theme="getStatusTheme(paper.review_status)">
                  {{ paper.review_status }}
                </Badge>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-600">Engagement:</span>
                <span class="text-sm text-gray-900">{{ getEngagementTitle(paper.engagement_reference) }}</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-600">Prepared By:</span>
                <span class="text-sm text-gray-900">{{ paper.prepared_by || 'Unassigned' }}</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-600">Date:</span>
                <span class="text-sm text-gray-900">{{ formatDate(paper.preparation_date) }}</span>
              </div>
            </div>

            <!-- Card Actions -->
            <div class="flex items-center justify-between pt-4 border-t border-gray-200">
              <div class="flex space-x-2">
                <Button
                  variant="ghost"
                  size="sm"
                  @click.stop="viewWorkingPaper(paper)"
                >
                  <EyeIcon class="h-4 w-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  @click.stop="editWorkingPaper(paper)"
                >
                  <EditIcon class="h-4 w-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  @click.stop="duplicateWorkingPaper(paper)"
                  theme="gray"
                >
                  <CopyIcon class="h-4 w-4" />
                </Button>
              </div>
              <Button
                variant="ghost"
                size="sm"
                @click.stop="deleteWorkingPaper(paper)"
                theme="red"
              >
                <TrashIcon class="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>

        <!-- Pagination for Cards -->
        <div class="mt-6 flex items-center justify-between">
          <div class="text-sm text-gray-700">
            Showing {{ (currentPage - 1) * itemsPerPage + 1 }} to {{ Math.min(currentPage * itemsPerPage, filteredWorkingPapers.length) }} of {{ filteredWorkingPapers.length }} results
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
    <div v-if="filteredWorkingPapers.length === 0" class="bg-white rounded-xl border border-gray-200 p-12 text-center">
      <div class="max-w-md mx-auto">
        <div class="mx-auto h-24 w-24 text-gray-400 mb-4">
          <FileTextIcon class="h-24 w-24" />
        </div>
        <h3 class="text-lg font-semibold text-gray-900 mb-2">No working papers found</h3>
        <p class="text-gray-600 mb-6">
          {{ filters.search || filters.engagement || filters.type || filters.status
             ? 'Try adjusting your filters or search terms to find what you\'re looking for.'
             : 'Get started by creating your first working paper for audit documentation.' }}
        </p>
        <div class="space-y-3">
          <Button
            @click="createNewWorkingPaper"
            variant="solid"
            class="bg-gray-900 hover:bg-gray-800"
          >
            <PlusIcon class="h-4 w-4 mr-2" />
            Create Working Paper
          </Button>
          <div class="text-sm text-gray-500">
            <p class="mb-1">💡 <strong>Quick Tips:</strong></p>
            <ul class="text-left space-y-1">
              <li>• Use templates to standardize your documentation</li>
              <li>• Link working papers to specific audit engagements</li>
              <li>• Track review status to ensure quality control</li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- Working Paper Modal -->
    <WorkingPapersForm
      v-model="showWorkingPaperModal"
      :working-paper="currentWorkingPaper"
      @created="handleWorkingPaperCreated"
      @updated="handleWorkingPaperUpdated"
      @cancelled="showWorkingPaperModal = false"
    />

	<!-- Templates Modal -->
	<Dialog v-model="showTemplateModal" :options="{ title: 'Apply Template' }">
		<template #body-content>
			<div class="space-y-4">
				<p class="text-sm text-gray-600">
					Select a template to apply to the selected working papers:
				</p>
				<div class="space-y-2">
					<label class="flex items-center space-x-2">
						<input type="radio" v-model="selectedTemplate" value="planning-memo" class="text-blue-600">
						<span class="text-sm">Planning Memo Template</span>
					</label>
					<label class="flex items-center space-x-2">
						<input type="radio" v-model="selectedTemplate" value="test-of-controls" class="text-blue-600">
						<span class="text-sm">Test of Controls Template</span>
					</label>
					<label class="flex items-center space-x-2">
						<input type="radio" v-model="selectedTemplate" value="substantive-test" class="text-blue-600">
						<span class="text-sm">Substantive Test Template</span>
					</label>
					<label class="flex items-center space-x-2">
						<input type="radio" v-model="selectedTemplate" value="analytical-review" class="text-blue-600">
						<span class="text-sm">Analytical Review Template</span>
					</label>
					<label class="flex items-center space-x-2">
						<input type="radio" v-model="selectedTemplate" value="summary-memo" class="text-blue-600">
						<span class="text-sm">Summary Memo Template</span>
					</label>
				</div>
			</div>
		</template>
		<template #actions>
			<Button variant="ghost" @click="showTemplateModal = false">
				Cancel
			</Button>
			<Button variant="solid" @click="applyTemplate" :disabled="!selectedTemplate">
				Apply Template
			</Button>
		</template>
	</Dialog>

	<!-- Bulk Actions Modal -->
	<Dialog v-model="showBulkModal" :options="{ title: 'Bulk Actions' }">
		<template #body-content>
			<div class="space-y-4">
				<p class="text-sm text-gray-600">
					Apply bulk action to {{ selectedPapers.length }} selected working papers:
				</p>
				<div class="space-y-3">
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-1">
							Update Status
						</label>
						<Select v-model="bulkStatusUpdate" :options="reviewStatusOptions" />
					</div>
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-1">
							Assign Reviewer
						</label>
						<Select v-model="bulkReviewerUpdate" :options="userOptions" />
					</div>
					<div class="flex items-center space-x-2">
						<Checkbox v-model="bulkDeleteConfirm" />
						<span class="text-sm text-red-600">
							Delete selected working papers (this action cannot be undone)
						</span>
					</div>
				</div>
			</div>
		</template>
		<template #actions>
			<Button variant="ghost" @click="showBulkModal = false">
				Cancel
			</Button>
			<Button variant="solid" @click="applyBulkActions" :disabled="!bulkStatusUpdate && !bulkReviewerUpdate && !bulkDeleteConfirm">
				Apply Changes
			</Button>
		</template>
	</Dialog>

	<!-- Capacity Planning Modal -->
	<Dialog v-model="showCapacityModal" :options="{ title: 'Review Capacity Planning' }">
		<template #body-content>
			<div class="space-y-4">
				<div class="grid grid-cols-2 gap-4">
					<div class="bg-gray-50 p-4 rounded-lg">
						<h4 class="font-medium text-gray-900">Papers Under Review</h4>
						<p class="text-2xl font-bold text-gray-900">{{ underReviewCount }}</p>
						<p class="text-sm text-gray-700">Pending approval</p>
					</div>
					<div class="bg-green-50 p-4 rounded-lg">
						<h4 class="font-medium text-green-900">Review Capacity</h4>
						<p class="text-2xl font-bold text-green-600">{{ Math.max(0, 50 - underReviewCount) }}</p>
						<p class="text-sm text-green-700">Available slots</p>
					</div>
				</div>
				<div class="space-y-2">
					<h4 class="font-medium">Reviewer Workload</h4>
					<div class="space-y-2 max-h-40 overflow-y-auto">
						<div v-for="reviewer in reviewerWorkload" :key="reviewer.name" class="flex justify-between items-center p-2 bg-gray-50 rounded">
							<span class="text-sm">{{ reviewer.name }}</span>
							<div class="flex items-center space-x-2">
								<div class="w-20 bg-gray-200 rounded-full h-2">
									<div class="bg-gray-900 h-2 rounded-full" :style="{ width: `${reviewer.load}%` }"></div>
								</div>
								<span class="text-xs text-gray-600">{{ reviewer.load }}%</span>
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
  </div>
</template><script setup>
import { useAuditStore } from "@/stores/audit"
import { Badge, Button, Checkbox, Dialog, FormControl, Select } from "frappe-ui"
import {
	AlertTriangleIcon,
	ArrowUpDownIcon,
	BarChart3Icon,
	CheckCircleIcon,
	ChevronLeftIcon,
	ChevronRightIcon,
	ClockIcon,
	CopyIcon,
	DownloadIcon,
	EditIcon,
	EyeIcon,
	FileTextIcon,
	GridIcon,
	LayersIcon,
	PlusIcon,
	RefreshCwIcon,
	SearchIcon,
	TableIcon,
	TrashIcon,
} from "lucide-vue-next"
import { computed, onMounted, ref } from "vue"
import { useRouter } from "vue-router"
import WorkingPapersForm from "@/components/workingpaper/WorkingPapersForm.vue"
import WorkingPapersStats from "@/components/workingpaper/WorkingPapersStats.vue"

const router = useRouter()
const auditStore = useAuditStore()

// Reactive state
const loading = ref(false)
const showWorkingPaperModal = ref(false)
const isEditing = ref(false)
const currentWorkingPaper = ref(null)
const exporting = ref(false)

// New reactive variables for enhanced functionality
const selectedPapers = ref([])
const sortBy = ref("preparation_date")
const currentPage = ref(1)
const itemsPerPage = ref(10)
const viewMode = ref("table")
const showBulkModal = ref(false)
const showCapacityModal = ref(false)
const showTemplateModal = ref(false)

// Modal reactive variables
const selectedTemplate = ref("")
const bulkStatusUpdate = ref("")
const bulkReviewerUpdate = ref("")
const bulkDeleteConfirm = ref(false)

const filters = ref({
	search: "",
	engagement: "",
	type: "",
	status: "",
	preparedBy: "",
})

const workingPaperForm = ref({
	working_paper_id: "",
	wp_title: "",
	wp_reference_no: "",
	wp_type: "Planning Memo",
	engagement_reference: "",
	procedure_reference: "",
	prepared_by: "",
	preparation_date: "",
	reviewed_by: "",
	review_date: "",
	review_status: "Not Reviewed",
	work_performed: "",
	objective: "",
	scope: "",
})

// Computed properties
const workingPapers = computed(() => auditStore.workingPapers)

const filteredWorkingPapers = computed(() => {
	let filtered = workingPapers.value

	if (filters.value.search) {
		filtered = filtered.filter(
			(paper) =>
				paper.wp_title
					?.toLowerCase()
					.includes(filters.value.search.toLowerCase()) ||
				paper.working_paper_id
					?.toLowerCase()
					.includes(filters.value.search.toLowerCase()),
		)
	}

	if (filters.value.engagement) {
		filtered = filtered.filter(
			(paper) => paper.engagement_reference === filters.value.engagement,
		)
	}

	if (filters.value.type) {
		filtered = filtered.filter((paper) => paper.wp_type === filters.value.type)
	}

	if (filters.value.status) {
		filtered = filtered.filter(
			(paper) => paper.review_status === filters.value.status,
		)
	}

	if (filters.value.preparedBy) {
		filtered = filtered.filter(
			(paper) => paper.prepared_by === filters.value.preparedBy,
		)
	}

	return filtered
})

// New computed properties for enhanced functionality
const selectAllPapers = computed({
	get: () =>
		filteredWorkingPapers.value.length > 0 &&
		selectedPapers.value.length === filteredWorkingPapers.value.length,
	set: (value) => {
		if (value) {
			selectedPapers.value = filteredWorkingPapers.value.map(
				(paper) => paper.name,
			)
		} else {
			selectedPapers.value = []
		}
	},
})

const paginatedPapers = computed(() => {
	const start = (currentPage.value - 1) * itemsPerPage.value
	const end = start + itemsPerPage.value
	return filteredWorkingPapers.value.slice(start, end)
})

const totalPages = computed(() =>
	Math.ceil(filteredWorkingPapers.value.length / itemsPerPage.value),
)

// Enhanced stats computed properties
const totalWorkingPapers = computed(() => workingPapers.value.length)

const reviewCompleteCount = computed(
	() =>
		workingPapers.value.filter(
			(paper) => paper.review_status === "Review Complete",
		).length,
)

const underReviewCount = computed(
	() =>
		workingPapers.value.filter(
			(paper) => paper.review_status === "Under Review",
		).length,
)

const revisionRequiredCount = computed(
	() =>
		workingPapers.value.filter(
			(paper) => paper.review_status === "Revision Required",
		).length,
)

const notReviewedCount = computed(
	() =>
		workingPapers.value.filter(
			(paper) => paper.review_status === "Not Reviewed",
		).length,
)

// Additional computed properties for stats
const averageReviewTime = computed(() => {
	const reviewedPapers = workingPapers.value.filter(
		(paper) => paper.review_date && paper.preparation_date,
	)
	if (reviewedPapers.length === 0) return 0

	const totalDays = reviewedPapers.reduce((sum, paper) => {
		const prepDate = new Date(paper.preparation_date)
		const reviewDate = new Date(paper.review_date)
		const diffTime = Math.abs(reviewDate - prepDate)
		const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
		return sum + diffDays
	}, 0)

	return Math.round(totalDays / reviewedPapers.length)
})

const averageQualityScore = computed(() => {
	const scoredPapers = workingPapers.value.filter(
		(paper) => paper.quality_score,
	)
	if (scoredPapers.length === 0) return 0

	const totalScore = scoredPapers.reduce(
		(sum, paper) => sum + (paper.quality_score || 0),
		0,
	)
	return Math.round(totalScore / scoredPapers.length)
})

// Capacity planning computed properties
const reviewerWorkload = computed(() => {
	const workload = {}
	workingPapers.value.forEach((paper) => {
		if (paper.reviewed_by) {
			if (!workload[paper.reviewed_by]) {
				workload[paper.reviewed_by] = { name: paper.reviewed_by, count: 0 }
			}
			workload[paper.reviewed_by].count++
		}
	})

	return Object.values(workload).map((reviewer) => ({
		...reviewer,
		load: Math.min(100, Math.round((reviewer.count / 10) * 100)), // Assuming max 10 papers per reviewer
	}))
})

const engagementOptions = computed(() => {
	const engagements = auditStore.engagements
	return [
		{ label: "All Engagements", value: "" },
		...engagements.map((eng) => ({
			label: eng.engagement_title,
			value: eng.name,
		})),
	]
})

const typeOptions = [
	{ label: "All Types", value: "" },
	{ label: "Planning Memo", value: "Planning Memo" },
	{ label: "Risk Assessment", value: "Risk Assessment" },
	{ label: "Walkthrough", value: "Walkthrough" },
	{ label: "Test of Controls", value: "Test of Controls" },
	{ label: "Substantive Test", value: "Substantive Test" },
	{ label: "Analytical Review", value: "Analytical Review" },
	{ label: "Data Analytics", value: "Data Analytics" },
	{ label: "Summary", value: "Summary" },
	{ label: "Other", value: "Other" },
]

const statusOptions = [
	{ label: "All Status", value: "" },
	{ label: "Not Reviewed", value: "Not Reviewed" },
	{ label: "Under Review", value: "Under Review" },
	{ label: "Review Complete", value: "Review Complete" },
	{ label: "Revision Required", value: "Revision Required" },
]

const preparedByOptions = computed(() => {
	const preparers = new Set()
	workingPapers.value.forEach((paper) => {
		if (paper.prepared_by) {
			preparers.add(paper.prepared_by)
		}
	})

	return [
		{ label: "All Preparers", value: "" },
		...Array.from(preparers).map((preparer) => ({
			label: preparer,
			value: preparer,
		})),
	]
})

const wpTypeOptions = typeOptions.slice(1) // Remove "All Types" option
const reviewStatusOptions = statusOptions.slice(1) // Remove "All Status" option

const procedureOptions = computed(() => {
	// This would be populated from audit procedures related to the selected engagement
	return [{ label: "Select Procedure", value: "" }]
})

const userOptions = computed(() => {
	// This would be populated from system users
	return [
		{ label: "Select User", value: "" },
		{ label: "John Doe", value: "john.doe@example.com" },
		{ label: "Jane Smith", value: "jane.smith@example.com" },
	]
})

// Methods
const getStatusVariant = (status) => {
	const variants = {
		"Not Reviewed": "secondary",
		"Under Review": "warning",
		"Review Complete": "success",
		"Revision Required": "danger",
	}
	return variants[status] || "secondary"
}

const getTypeTheme = (type) => {
	const themes = {
		"Planning Memo": "blue",
		"Risk Assessment": "red",
		Walkthrough: "green",
		"Test of Controls": "gray",
		"Substantive Test": "orange",
		"Analytical Review": "yellow",
		"Data Analytics": "indigo",
		Summary: "gray",
		Other: "gray",
	}
	return themes[type] || "gray"
}

const getStatusTheme = (status) => {
	const themes = {
		"Not Reviewed": "gray",
		"Under Review": "yellow",
		"Review Complete": "green",
		"Revision Required": "red",
	}
	return themes[status] || "gray"
}

const getEngagementTitle = (engagementRef) => {
	const engagement = auditStore.engagements.find(
		(eng) => eng.name === engagementRef,
	)
	return engagement ? engagement.engagement_title : "Unknown Engagement"
}

const formatDate = (dateString) => {
	if (!dateString) return ""
	return new Date(dateString).toLocaleDateString("en-US", {
		month: "short",
		day: "numeric",
		year: "numeric",
	})
}

const onWorkingPaperClick = (paper) => {
	router.push(`/working-papers/${paper.name}`)
}

const viewWorkingPaper = (paper) => {
	router.push(`/working-papers/${paper.name}`)
}

const editWorkingPaper = (paper) => {
	currentWorkingPaper.value = paper
	isEditing.value = true
	showWorkingPaperModal.value = true
}

const duplicateWorkingPaper = (paper) => {
	currentWorkingPaper.value = null
	isEditing.value = false

	// Populate form with duplicated data
	workingPaperForm.value = {
		working_paper_id: "",
		wp_title: `${paper.wp_title} (Copy)`,
		wp_reference_no: "",
		wp_type: paper.wp_type || "Planning Memo",
		engagement_reference: paper.engagement_reference || "",
		procedure_reference: paper.procedure_reference || "",
		prepared_by: "",
		preparation_date: new Date().toISOString().split("T")[0],
		reviewed_by: "",
		review_date: "",
		review_status: "Not Reviewed",
		work_performed: paper.work_performed || "",
		objective: paper.objective || "",
		scope: paper.scope || "",
	}

	showWorkingPaperModal.value = true
}

const deleteWorkingPaper = (paper) => {
	if (confirm("Are you sure you want to delete this working paper?")) {
		// Delete logic will be implemented with API call
		// For now, we'll refresh the list
		auditStore.fetchWorkingPapers()
	}
}

const createNewWorkingPaper = () => {
	currentWorkingPaper.value = null
	isEditing.value = false
	showWorkingPaperModal.value = true
}

const closeWorkingPaperModal = () => {
	showWorkingPaperModal.value = false
	currentWorkingPaper.value = null
	isEditing.value = false
}

const saveWorkingPaper = async () => {
	try {
		if (isEditing.value) {
			// Update existing working paper
			await auditStore.updateWorkingPaper(
				currentWorkingPaper.value.name,
				workingPaperForm.value,
			)
		} else {
			// Create new working paper
			await auditStore.createWorkingPaper(workingPaperForm.value)
		}

		closeWorkingPaperModal()
	} catch (error) {
		console.error("Error saving working paper:", error)
	}
}

// Event handlers for WorkingPapersForm component
const handleWorkingPaperCreated = async (workingPaper) => {
	showWorkingPaperModal.value = false
	currentWorkingPaper.value = null
	isEditing.value = false
	await refreshData()
}

const handleWorkingPaperUpdated = async (workingPaper) => {
	showWorkingPaperModal.value = false
	currentWorkingPaper.value = null
	isEditing.value = false
	await refreshData()
}

// New methods for enhanced functionality
const toggleSelectAllPapers = (value) => {
	if (value) {
		selectedPapers.value = filteredWorkingPapers.value.map(
			(paper) => paper.name,
		)
	} else {
		selectedPapers.value = []
	}
}

const togglePaperSelection = (paperName) => {
	const index = selectedPapers.value.indexOf(paperName)
	if (index > -1) {
		selectedPapers.value.splice(index, 1)
	} else {
		selectedPapers.value.push(paperName)
	}
}

const refreshData = async () => {
	loading.value = true
	try {
		await auditStore.fetchWorkingPapers()
		await auditStore.fetchEngagements()
	} catch (error) {
		console.error("Error loading data:", error)
	} finally {
		loading.value = false
	}
}

const exportWorkingPapers = async () => {
	exporting.value = true
	try {
		// Implement export functionality
		console.log("Exporting working papers data...")
		// This would typically call an API to export the data
	} finally {
		exporting.value = false
	}
}

// Modal methods
const applyTemplate = async () => {
	if (!selectedTemplate.value) return

	try {
		// Implement template application logic
		console.log(
			"Applying template:",
			selectedTemplate.value,
			"to working papers:",
			selectedPapers.value,
		)
		// This would typically call an API to apply the template
		showTemplateModal.value = false
		selectedTemplate.value = ""
		selectedPapers.value = []
		await refreshData()
	} catch (error) {
		console.error("Error applying template:", error)
	}
}

const applyBulkActions = async () => {
	try {
		if (bulkStatusUpdate.value) {
			console.log(
				"Updating status to:",
				bulkStatusUpdate.value,
				"for working papers:",
				selectedPapers.value,
			)
			// Implement bulk status update
		}

		if (bulkReviewerUpdate.value) {
			console.log(
				"Assigning reviewer:",
				bulkReviewerUpdate.value,
				"to working papers:",
				selectedPapers.value,
			)
			// Implement bulk reviewer assignment
		}

		if (bulkDeleteConfirm.value) {
			if (
				confirm(
					`Are you sure you want to delete ${selectedPapers.value.length} working papers? This action cannot be undone.`,
				)
			) {
				console.log("Deleting working papers:", selectedPapers.value)
				// Implement bulk delete
			}
		}

		showBulkModal.value = false
		bulkStatusUpdate.value = ""
		bulkReviewerUpdate.value = ""
		bulkDeleteConfirm.value = false
		selectedPapers.value = []
		await refreshData()
	} catch (error) {
		console.error("Error applying bulk actions:", error)
	}
}

// Lifecycle
onMounted(async () => {
	loading.value = true
	try {
		await auditStore.fetchEngagements()
		await auditStore.fetchWorkingPapers()
	} catch (error) {
		console.error("Error loading data:", error)
	} finally {
		loading.value = false
	}
})
</script>