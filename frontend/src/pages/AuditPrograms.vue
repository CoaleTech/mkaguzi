<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Audit Programs</h1>
        <p class="text-gray-600 mt-1">
          Create and manage audit programs and procedures
        </p>
      </div>
      <div class="flex items-center space-x-3">
        <Button
          variant="outline"
          @click="exportPrograms"
          :disabled="auditPrograms.length === 0"
        >
          <DownloadIcon class="h-4 w-4 mr-2" />
          Export
        </Button>
        <Button
          variant="outline"
          @click="refreshData"
          :loading="loading"
        >
          <RefreshCwIcon class="h-4 w-4 mr-2" />
          Refresh
        </Button>
        <Button
          @click="showCreateModal = true"
          class="bg-blue-600 hover:bg-blue-700 text-white"
        >
          <PlusIcon class="h-4 w-4 mr-2" />
          New Program
        </Button>
      </div>
    </div>

    <!-- Notification Messages -->
    <div v-if="errorMessage" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
      <div class="flex items-center">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3">
          <p class="text-sm text-red-800">{{ errorMessage }}</p>
        </div>
        <div class="ml-auto pl-3">
          <div class="-mx-1.5 -my-1.5">
            <button
              @click="errorMessage = ''"
              class="inline-flex bg-red-50 rounded-md p-1.5 text-red-500 hover:bg-red-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-red-50 focus:ring-red-600"
            >
              <span class="sr-only">Dismiss</span>
              <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="successMessage" class="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
      <div class="flex items-center">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3">
          <p class="text-sm text-green-800">{{ successMessage }}</p>
        </div>
        <div class="ml-auto pl-3">
          <div class="-mx-1.5 -my-1.5">
            <button
              @click="successMessage = ''"
              class="inline-flex bg-green-50 rounded-md p-1.5 text-green-500 hover:bg-green-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-green-50 focus:ring-green-600"
            >
              <span class="sr-only">Dismiss</span>
              <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions Bar -->
    <div class="bg-white rounded-lg border border-gray-200 p-4 mb-6">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <span class="text-sm font-medium text-gray-700">Quick Actions:</span>
          <Button
            variant="outline"
            size="sm"
            @click="createProgramFromTemplate"
            :disabled="templatePrograms.length === 0"
          >
            <CopyIcon class="h-4 w-4 mr-2" />
            Use Template
          </Button>
          <Button
            variant="outline"
            size="sm"
            @click="bulkCreateTemplates"
            :disabled="selectedPrograms.length === 0"
          >
            <FileTextIcon class="h-4 w-4 mr-2" />
            Create Templates
          </Button>
        </div>
        <div class="text-sm text-gray-500">
          Press <kbd class="px-2 py-1 bg-gray-100 rounded text-xs">Ctrl+N</kbd> to create new program
        </div>
      </div>
    </div>
    <div class="bg-white rounded-lg border border-gray-200 p-4">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <FormControl
          v-model="searchQuery"
          placeholder="Search programs..."
          class="md:col-span-2"
        >
          <template #prefix>
            <SearchIcon class="h-4 w-4 text-gray-400" />
          </template>
        </FormControl>
        <Select
          v-model="filterType"
          :options="typeFilterOptions"
          placeholder="All Types"
        />
        <Select
          v-model="filterTemplate"
          :options="templateFilterOptions"
          placeholder="All Programs"
        />
        <Select
          v-model="filterStatus"
          :options="statusFilterOptions"
          placeholder="All Statuses"
        />
      </div>
    </div>

    <!-- Bulk Actions -->
    <div v-if="selectedPrograms.length > 0" class="bg-blue-50 border border-blue-200 rounded-lg p-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <span class="text-sm font-medium text-blue-900">
            {{ selectedPrograms.length }} program{{ selectedPrograms.length > 1 ? 's' : '' }} selected
          </span>
        </div>
        <div class="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            @click="clearSelection"
          >
            Clear Selection
          </Button>
          <Button
            variant="outline"
            size="sm"
            @click="bulkDeletePrograms"
            class="text-red-600 hover:text-red-700"
          >
            <TrashIcon class="h-4 w-4 mr-2" />
            Delete Selected
          </Button>
        </div>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Total Programs</p>
            <p class="text-3xl font-bold text-gray-900">{{ auditPrograms.length }}</p>
          </div>
          <div class="p-3 bg-blue-100 rounded-full">
            <FileTextIcon class="h-6 w-6 text-blue-600" />
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Templates</p>
            <p class="text-3xl font-bold text-gray-900">{{ templatePrograms.length }}</p>
          </div>
          <div class="p-3 bg-green-100 rounded-full">
            <CopyIcon class="h-6 w-6 text-green-600" />
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Active Programs</p>
            <p class="text-3xl font-bold text-gray-900">{{ activePrograms.length }}</p>
          </div>
          <div class="p-3 bg-yellow-100 rounded-full">
            <PlayIcon class="h-6 w-6 text-yellow-600" />
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Overdue Programs</p>
            <p class="text-3xl font-bold text-red-600">{{ overduePrograms.length }}</p>
          </div>
          <div class="p-3 bg-red-100 rounded-full">
            <AlertTriangleIcon class="h-6 w-6 text-red-600" />
          </div>
        </div>
        <div v-if="overduePrograms.length > 0" class="mt-2">
          <p class="text-xs text-red-600">Programs not updated in 30+ days</p>
        </div>
      </div>
    </div>

    <!-- Programs List -->
    <div class="bg-white rounded-lg border border-gray-200">
      <div class="px-6 py-4 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-medium text-gray-900">Audit Programs</h3>
          <div class="flex items-center space-x-2">
            <span class="text-sm text-gray-500">
              {{ filteredPrograms.length }} program{{ filteredPrograms.length !== 1 ? 's' : '' }}
            </span>
          </div>
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                <Checkbox
                  v-model="selectAll"
                  @change="toggleSelectAll"
                />
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Program ID
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Name
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Type
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Template
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Progress
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
              v-for="program in paginatedPrograms"
              :key="program.name"
              class="hover:bg-gray-50"
              :class="{
                'bg-blue-50': selectedPrograms.includes(program.name),
                'bg-red-50 border-l-4 border-red-400': isOverdue(program)
              }"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <Checkbox
                  :model-value="selectedPrograms.includes(program.name)"
                  @change="toggleProgramSelection(program.name)"
                />
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                {{ program.program_id }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                <div class="flex items-center">
                  <div class="flex-1">
                    <div class="font-medium">{{ program.program_name }}</div>
                    <div class="text-xs text-gray-500">
                      Created {{ formatDate(program.creation) }}
                    </div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <Badge :variant="getTypeVariant(program.audit_type)">
                  {{ program.audit_type }}
                </Badge>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <Badge
                  :variant="program.is_template ? 'success' : 'secondary'"
                  size="sm"
                >
                  {{ program.is_template ? 'Template' : 'Program' }}
                </Badge>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center space-x-2">
                  <div class="flex-1 bg-gray-200 rounded-full h-2">
                    <div
                      class="h-2 rounded-full transition-all duration-300"
                      :class="getProgressBarColor(program.completion_percent || 0)"
                      :style="{ width: `${program.completion_percent || 0}%` }"
                    ></div>
                  </div>
                  <div class="text-xs text-gray-500 min-w-[3rem] text-right">
                    {{ program.completion_percent || 0 }}%
                  </div>
                </div>
                <div class="text-xs text-gray-400 mt-1">
                  {{ program.completed_procedures || 0 }}/{{ program.total_procedures || 0 }} procedures
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <Badge :variant="getStatusVariant(program.status || 'Draft')">
                  {{ program.status || 'Draft' }}
                </Badge>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div class="flex items-center space-x-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    @click="viewProgram(program)"
                    title="View Program"
                  >
                    <EyeIcon class="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    @click="editProgram(program)"
                    title="Edit Program"
                  >
                    <EditIcon class="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    @click="duplicateProgram(program)"
                    title="Duplicate Program"
                  >
                    <CopyIcon class="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    @click="useAsTemplate(program)"
                    v-if="!program.is_template"
                    title="Use as Template"
                  >
                    <CopyIcon class="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    @click="deleteProgram(program)"
                    class="text-red-600 hover:text-red-700"
                    title="Delete Program"
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
      <div v-if="totalPages > 1" class="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
        <div class="text-sm text-gray-500">
          Showing {{ startIndex + 1 }} to {{ Math.min(endIndex, filteredPrograms.length) }} of {{ filteredPrograms.length }} programs
        </div>
        <div class="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            @click="currentPage--"
            :disabled="currentPage === 1"
          >
            <ChevronLeftIcon class="h-4 w-4" />
          </Button>
          <span class="text-sm text-gray-700">
            Page {{ currentPage }} of {{ totalPages }}
          </span>
          <Button
            variant="outline"
            size="sm"
            @click="currentPage++"
            :disabled="currentPage === totalPages"
          >
            <ChevronRightIcon class="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div v-if="filteredPrograms.length === 0" class="px-6 py-12 text-center">
        <FileTextIcon class="mx-auto h-12 w-12 text-gray-400" />
        <h3 class="mt-2 text-sm font-medium text-gray-900">No audit programs found</h3>
        <p class="mt-1 text-sm text-gray-500">
          {{ searchQuery || filterType || filterTemplate ? 'Try adjusting your search or filters.' : 'Get started by creating a new audit program or template.' }}
        </p>
        <div class="mt-6">
          <Button @click="showCreateModal = true">
            <PlusIcon class="h-4 w-4 mr-2" />
            New Program
          </Button>
        </div>
      </div>
    </div>

    <!-- View Program Modal -->
    <Dialog
      v-model="showViewModal"
      :title="viewingProgram?.program_name || 'Program Details'"
      size="6xl"
    >
      <template #body>
        <div v-if="viewingProgram" class="space-y-6">
          <!-- Program Header -->
          <div class="bg-gray-50 rounded-lg p-6">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <h3 class="text-sm font-medium text-gray-500">Program ID</h3>
                <p class="text-lg font-semibold text-gray-900">{{ viewingProgram.program_id }}</p>
              </div>
              <div>
                <h3 class="text-sm font-medium text-gray-500">Audit Type</h3>
                <Badge :variant="getTypeVariant(viewingProgram.audit_type)">
                  {{ viewingProgram.audit_type }}
                </Badge>
              </div>
              <div>
                <h3 class="text-sm font-medium text-gray-500">Status</h3>
                <Badge :variant="getStatusVariant(viewingProgram.status || 'Draft')">
                  {{ viewingProgram.status || 'Draft' }}
                </Badge>
              </div>
            </div>
          </div>

          <!-- Program Objectives -->
          <div>
            <h3 class="text-lg font-medium text-gray-900 mb-3">Program Objectives</h3>
            <div class="bg-white border border-gray-200 rounded-lg p-4">
              <p class="text-gray-700 whitespace-pre-wrap">{{ viewingProgram.program_objectives }}</p>
            </div>
          </div>

          <!-- Progress Summary -->
          <div>
            <h3 class="text-lg font-medium text-gray-900 mb-3">Progress Summary</h3>
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div class="bg-white border border-gray-200 rounded-lg p-4">
                <div class="flex items-center justify-between">
                  <div>
                    <p class="text-sm font-medium text-gray-600">Total Procedures</p>
                    <p class="text-2xl font-bold text-gray-900">{{ viewingProgram.total_procedures || 0 }}</p>
                  </div>
                </div>
              </div>
              <div class="bg-white border border-gray-200 rounded-lg p-4">
                <div class="flex items-center justify-between">
                  <div>
                    <p class="text-sm font-medium text-gray-600">Completed</p>
                    <p class="text-2xl font-bold text-green-600">{{ viewingProgram.completed_procedures || 0 }}</p>
                  </div>
                </div>
              </div>
              <div class="bg-white border border-gray-200 rounded-lg p-4">
                <div class="flex items-center justify-between">
                  <div>
                    <p class="text-sm font-medium text-gray-600">Not Applicable</p>
                    <p class="text-2xl font-bold text-gray-500">{{ viewingProgram.not_applicable_procedures || 0 }}</p>
                  </div>
                </div>
              </div>
              <div class="bg-white border border-gray-200 rounded-lg p-4">
                <div class="flex items-center justify-between">
                  <div>
                    <p class="text-sm font-medium text-gray-600">Completion</p>
                    <p class="text-2xl font-bold text-blue-600">{{ viewingProgram.completion_percent || 0 }}%</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Audit Procedures -->
          <div>
            <h3 class="text-lg font-medium text-gray-900 mb-3">Audit Procedures</h3>
            <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Procedure</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Assigned To</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="procedure in viewingProgram.program_procedures" :key="procedure.name">
                    <td class="px-6 py-4">
                      <div>
                        <div class="font-medium text-gray-900">{{ procedure.procedure_no }}</div>
                        <div class="text-sm text-gray-500">{{ procedure.procedure_description }}</div>
                      </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {{ procedure.procedure_type }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <Badge :variant="getProcedureStatusVariant(procedure.status)">
                        {{ procedure.status }}
                      </Badge>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {{ procedure.assigned_to }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Risk Areas -->
          <div v-if="viewingProgram.risk_areas && viewingProgram.risk_areas.length > 0">
            <h3 class="text-lg font-medium text-gray-900 mb-3">Risk Areas</h3>
            <div class="space-y-4">
              <div v-for="risk in viewingProgram.risk_areas" :key="risk.name" class="bg-white border border-gray-200 rounded-lg p-4">
                <div class="flex items-center justify-between mb-2">
                  <h4 class="font-medium text-gray-900">{{ risk.risk_description }}</h4>
                  <Badge :variant="getRiskVariant(risk.risk_rating)">
                    {{ risk.risk_rating }}
                  </Badge>
                </div>
                <p class="text-sm text-gray-600 whitespace-pre-wrap">{{ risk.procedures_addressing_risk }}</p>
              </div>
            </div>
          </div>
        </div>
      </template>
      <template #footer>
        <div class="flex justify-end space-x-3">
          <Button variant="outline" @click="showViewModal = false">
            Close
          </Button>
          <Button
            @click="editProgram(viewingProgram)"
            class="bg-blue-600 hover:bg-blue-700 text-white"
          >
            Edit Program
          </Button>
        </div>
      </template>
    </Dialog>

    <!-- Create/Edit Program Modal -->
    <Dialog
      v-model="showCreateModal"
      :title="editingProgram ? 'Edit Audit Program' : 'Create Audit Program'"
      size="4xl"
      @close="resetForm"
    >
      <template #body>
        <div class="space-y-6">
          <!-- Basic Information -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <FormControl
              v-model="programForm.program_id"
              label="Program ID"
              placeholder="Enter program ID"
              required
            />
            <FormControl
              v-model="programForm.program_name"
              label="Program Name"
              placeholder="Enter program name"
              required
            />
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Select
              v-model="programForm.audit_type"
              :options="auditTypeOptions"
              label="Audit Type"
              placeholder="Select audit type"
              required
            />
            <Select
              v-model="programForm.engagement_reference"
              :options="engagementOptions"
              label="Engagement Reference"
              placeholder="Select engagement (optional)"
              :disabled="programForm.is_template"
            />
          </div>

          <div class="flex items-center space-x-2">
            <Checkbox v-model="programForm.is_template" />
            <label class="text-sm font-medium">This is a template</label>
          </div>

          <FormControl
            v-model="programForm.program_objectives"
            label="Program Objectives"
            type="textarea"
            placeholder="Enter program objectives"
            rows="3"
          />

          <!-- Program Procedures Section -->
          <div class="border-t pt-6">
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-lg font-semibold">Audit Procedures</h3>
              <Button
                @click="addProcedure"
                variant="outline"
                size="sm"
                class="flex items-center space-x-2"
              >
                <PlusIcon class="w-4 h-4" />
                <span>Add Procedure</span>
              </Button>
            </div>

            <div class="space-y-4">
              <div
                v-for="(procedure, index) in programForm.program_procedures"
                :key="index"
                class="border rounded-lg p-4 bg-gray-50"
              >
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
                  <FormControl
                    v-model="procedure.procedure_no"
                    label="Procedure No"
                    placeholder="e.g., 1.1"
                  />
                  <Select
                    v-model="procedure.procedure_type"
                    :options="procedureTypeOptions"
                    label="Procedure Type"
                    placeholder="Select type"
                  />
                  <Select
                    v-model="procedure.assertion"
                    :options="assertionOptions"
                    label="Assertion"
                    placeholder="Select assertion"
                  />
                </div>

                <FormControl
                  v-model="procedure.procedure_description"
                  label="Procedure Description"
                  type="textarea"
                  placeholder="Describe the audit procedure"
                  rows="2"
                  class="mb-4"
                />

                <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                  <FormControl
                    v-model="procedure.control_objective"
                    label="Control Objective"
                    placeholder="Enter control objective"
                  />
                  <FormControl
                    v-model.number="procedure.budgeted_hours"
                    label="Budgeted Hours"
                    type="number"
                    min="0"
                    step="0.5"
                  />
                  <Select
                    v-model="procedure.status"
                    :options="procedureStatusOptions"
                    label="Status"
                  />
                </div>

                <FormControl
                  v-model="procedure.assigned_to"
                  label="Assigned To"
                  placeholder="Enter assignee name"
                />

                <div class="flex justify-end mt-4">
                  <Button
                    @click="removeProcedure(index)"
                    variant="outline"
                    size="sm"
                    class="text-red-600 hover:text-red-700"
                  >
                    <TrashIcon class="w-4 h-4" />
                  </Button>
                </div>
              </div>

              <div v-if="programForm.program_procedures.length === 0" class="text-center py-8 text-gray-500">
                No procedures added yet. Click "Add Procedure" to get started.
              </div>
            </div>
          </div>

          <!-- Risk Areas Section -->
          <div class="border-t pt-6">
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-lg font-semibold">Risk Areas</h3>
              <Button
                @click="addRiskArea"
                variant="outline"
                size="sm"
                class="flex items-center space-x-2"
              >
                <PlusIcon class="w-4 h-4" />
                <span>Add Risk Area</span>
              </Button>
            </div>

            <div class="space-y-4">
              <div
                v-for="(risk, index) in programForm.risk_areas"
                :key="index"
                class="border rounded-lg p-4 bg-gray-50"
              >
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  <FormControl
                    v-model="risk.risk_description"
                    label="Risk Description"
                    type="textarea"
                    placeholder="Describe the risk"
                    rows="2"
                  />
                  <Select
                    v-model="risk.risk_rating"
                    :options="riskRatingOptions"
                    label="Risk Rating"
                    placeholder="Select risk rating"
                  />
                </div>

                <FormControl
                  v-model="risk.procedures_addressing_risk"
                  label="Procedures Addressing Risk"
                  type="textarea"
                  placeholder="List procedures that address this risk"
                  rows="2"
                />

                <div class="flex justify-end mt-4">
                  <Button
                    @click="removeRiskArea(index)"
                    variant="outline"
                    size="sm"
                    class="text-red-600 hover:text-red-700"
                  >
                    <TrashIcon class="w-4 h-4" />
                  </Button>
                </div>
              </div>

              <div v-if="programForm.risk_areas.length === 0" class="text-center py-8 text-gray-500">
                No risk areas added yet. Click "Add Risk Area" to get started.
              </div>
            </div>
          </div>
        </div>
      </template>

      <template #footer>
        <div class="flex justify-end space-x-3">
          <Button
            variant="outline"
            @click="showCreateModal = false"
          >
            Cancel
          </Button>
          <Button
            @click="saveProgram"
            :loading="saving"
            class="bg-blue-600 hover:bg-blue-700 text-white"
          >
            {{ editingProgram ? 'Update' : 'Create' }} Program
          </Button>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { useAuditStore } from "@/stores/audit"
import { Badge, Button, Checkbox, Dialog, FormControl, Select } from "frappe-ui"
import { createResource } from "frappe-ui"
import {
	BarChartIcon,
	ChevronLeftIcon,
	ChevronRightIcon,
	CopyIcon,
	DownloadIcon,
	EditIcon,
	EyeIcon,
	FileTextIcon,
	PlayIcon,
	PlusIcon,
	RefreshCwIcon,
	SearchIcon,
	TrashIcon,
	AlertTriangleIcon,
} from "lucide-vue-next"
import { computed, onMounted, onUnmounted, ref, watch } from "vue"
import { useRouter } from "vue-router"

const router = useRouter()
const auditStore = useAuditStore()

// Reactive state
const loading = ref(false)
const saving = ref(false)
const showCreateModal = ref(false)
const showViewModal = ref(false)
const editingProgram = ref(null)
const viewingProgram = ref(null)
const searchQuery = ref("")
const filterType = ref("")
const filterTemplate = ref("")
const filterStatus = ref("")
const selectedPrograms = ref([])
const selectAll = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const errorMessage = ref("")
const successMessage = ref("")

// Form data
const programForm = ref({
	program_id: "",
	program_name: "",
	audit_type: "",
	is_template: false,
	engagement_reference: "",
	program_objectives: "",
	program_procedures: [],
	risk_areas: [],
})

// Options
const auditTypeOptions = [
	{ label: "Financial", value: "Financial" },
	{ label: "Operational", value: "Operational" },
	{ label: "Compliance", value: "Compliance" },
	{ label: "IT", value: "IT" },
	{ label: "Inventory", value: "Inventory" },
	{ label: "Cash", value: "Cash" },
	{ label: "Sales", value: "Sales" },
	{ label: "Procurement", value: "Procurement" },
]

const procedureTypeOptions = [
	{ label: "Inquiry", value: "Inquiry" },
	{ label: "Observation", value: "Observation" },
	{ label: "Inspection", value: "Inspection" },
	{ label: "Recalculation", value: "Recalculation" },
	{ label: "Reperformance", value: "Reperformance" },
	{ label: "Analytical Procedures", value: "Analytical Procedures" },
]

const riskAreaOptions = [
	{ label: "Financial Reporting", value: "Financial Reporting" },
	{ label: "Internal Controls", value: "Internal Controls" },
	{ label: "Compliance", value: "Compliance" },
	{ label: "Operations", value: "Operations" },
	{ label: "IT Security", value: "IT Security" },
	{ label: "Fraud Risk", value: "Fraud Risk" },
]

const typeFilterOptions = [
	{ label: "All Types", value: "" },
	...auditTypeOptions,
]

const templateFilterOptions = [
	{ label: "All Programs", value: "" },
	{ label: "Programs Only", value: "program" },
	{ label: "Templates Only", value: "template" },
]

const statusFilterOptions = [
	{ label: "All Statuses", value: "" },
	{ label: "Overdue", value: "overdue" },
	{ label: "In Progress", value: "in_progress" },
	{ label: "Completed", value: "completed" },
]

const procedureStatusOptions = [
	{ label: "Not Started", value: "Not Started" },
	{ label: "In Progress", value: "In Progress" },
	{ label: "Completed", value: "Completed" },
	{ label: "Not Applicable", value: "Not Applicable" },
]

const assertionOptions = [
	{ label: "Existence", value: "Existence" },
	{ label: "Completeness", value: "Completeness" },
	{ label: "Accuracy", value: "Accuracy" },
	{ label: "Valuation", value: "Valuation" },
	{ label: "Rights", value: "Rights" },
	{ label: "Presentation", value: "Presentation" },
	{ label: "Occurrence", value: "Occurrence" },
	{ label: "Cutoff", value: "Cutoff" },
]

const riskRatingOptions = [
	{ label: "Low", value: "Low" },
	{ label: "Medium", value: "Medium" },
	{ label: "High", value: "High" },
	{ label: "Critical", value: "Critical" },
]

// Computed properties
const auditPrograms = computed(() => auditStore.auditPrograms)
const templatePrograms = computed(() => auditStore.auditProgramTemplates)
const activePrograms = computed(() =>
	auditStore.auditPrograms.filter((p) => !p.is_template),
)

const averageCompletion = computed(() => {
	const programs = auditStore.auditPrograms.filter((p) => !p.is_template)
	if (programs.length === 0) return 0
	const total = programs.reduce(
		(sum, program) => sum + (program.completion_percent || 0),
		0,
	)
	return Math.round(total / programs.length)
})

const filteredPrograms = computed(() => {
	let programs = auditStore.auditPrograms

	// Search filter
	if (searchQuery.value) {
		const query = searchQuery.value.toLowerCase()
		programs = programs.filter(
			(p) =>
				p.program_id?.toLowerCase().includes(query) ||
				p.program_name?.toLowerCase().includes(query) ||
				p.audit_type?.toLowerCase().includes(query),
		)
	}

	// Type filter
	if (filterType.value) {
		programs = programs.filter((p) => p.audit_type === filterType.value)
	}

	// Template filter
	if (filterTemplate.value === "template") {
		programs = programs.filter((p) => p.is_template)
	} else if (filterTemplate.value === "program") {
		programs = programs.filter((p) => !p.is_template)
	}

	// Status filter
	if (filterStatus.value) {
		const now = new Date()
		if (filterStatus.value === "overdue") {
			programs = programs.filter((p) => {
				if (!p.modified || p.is_template) return false
				const lastModified = new Date(p.modified)
				const daysSinceModified = (now - lastModified) / (1000 * 60 * 60 * 24)
				return daysSinceModified > 30 && (p.completion_percent || 0) < 100
			})
		} else if (filterStatus.value === "in_progress") {
			programs = programs.filter((p) => !p.is_template && (p.completion_percent || 0) > 0 && (p.completion_percent || 0) < 100)
		} else if (filterStatus.value === "completed") {
			programs = programs.filter((p) => !p.is_template && (p.completion_percent || 0) >= 100)
		}
	}

	return programs
})

const paginatedPrograms = computed(() => {
	const start = (currentPage.value - 1) * pageSize.value
	const end = start + pageSize.value
	return filteredPrograms.value.slice(start, end)
})

const totalPages = computed(() => {
	return Math.ceil(filteredPrograms.value.length / pageSize.value)
})

const startIndex = computed(() => {
	return (currentPage.value - 1) * pageSize.value
})

const endIndex = computed(() => {
	return startIndex.value + pageSize.value
})

const overduePrograms = computed(() => {
	const now = new Date()
	return auditPrograms.value.filter((program) => {
		if (!program.modified) return false
		const lastModified = new Date(program.modified)
		const daysSinceModified = (now - lastModified) / (1000 * 60 * 60 * 24)
		return daysSinceModified > 30 && (program.completion_percent || 0) < 100
	})
})

// Methods
const refreshData = async () => {
	loading.value = true
	errorMessage.value = ""
	try {
		await Promise.all([
			auditStore.fetchAuditPrograms(),
			auditStore.fetchEngagements(),
		])
	} catch (error) {
		console.error("Error refreshing data:", error)
		errorMessage.value = "Failed to refresh data. Please try again."
	} finally {
		loading.value = false
	}
}

const viewProgram = async (program) => {
	try {
		const programDetails = await auditStore.fetchAuditProgramDetails(
			program.name,
		)
		if (programDetails) {
			viewingProgram.value = programDetails
			showViewModal.value = true
		}
	} catch (error) {
		console.error("Error fetching program details:", error)
	}
}

const editProgram = (program) => {
	editingProgram.value = program
	// Load program data into form
	programForm.value = { ...program }
	showCreateModal.value = true
}

const duplicateProgram = async (program) => {
	try {
		const programDetails = await auditStore.fetchAuditProgramDetails(
			program.name,
		)
		if (programDetails) {
			editingProgram.value = null
			programForm.value = {
				...programDetails,
				program_id: `${programDetails.program_id}_copy`,
				program_name: `${programDetails.program_name} (Copy)`,
				is_template: false,
			}
			showCreateModal.value = true
		}
	} catch (error) {
		console.error("Error duplicating program:", error)
	}
}

const useAsTemplate = async (program) => {
	try {
		const programDetails = await auditStore.fetchAuditProgramDetails(
			program.name,
		)
		if (programDetails) {
			editingProgram.value = null
			programForm.value = {
				...programDetails,
				program_id: `${programDetails.program_id}_template`,
				program_name: `${programDetails.program_name} (Template)`,
				is_template: true,
				engagement_reference: "",
			}
			showCreateModal.value = true
		}
	} catch (error) {
		console.error("Error creating template:", error)
	}
}

const addProcedure = () => {
	programForm.value.program_procedures.push({
		procedure_no: "",
		procedure_description: "",
		procedure_type: "",
		control_objective: "",
		assertion: "",
		budgeted_hours: 0,
		status: "Not Started",
		assigned_to: "",
	})
}

const removeProcedure = (index) => {
	programForm.value.program_procedures.splice(index, 1)
}

const addRiskArea = () => {
	programForm.value.risk_areas.push({
		risk_description: "",
		risk_rating: "",
		procedures_addressing_risk: "",
	})
}

const removeRiskArea = (index) => {
	programForm.value.risk_areas.splice(index, 1)
}

const saveProgram = async () => {
	// Basic validation
	if (!programForm.value.program_id.trim()) {
		errorMessage.value = "Program ID is required"
		return
	}
	if (!programForm.value.program_name.trim()) {
		errorMessage.value = "Program Name is required"
		return
	}
	if (!programForm.value.audit_type) {
		errorMessage.value = "Audit Type is required"
		return
	}

	// Clear any previous messages
	errorMessage.value = ""
	successMessage.value = ""

	saving.value = true
	try {
		if (editingProgram.value) {
			await auditStore.updateAuditProgram(
				editingProgram.value.name,
				programForm.value,
			)
			successMessage.value = "Program updated successfully"
		} else {
			await auditStore.createAuditProgram(programForm.value)
			successMessage.value = "Program created successfully"
		}

		showCreateModal.value = false
		resetForm()
		await refreshData()

		// Clear success message after 3 seconds
		setTimeout(() => {
			successMessage.value = ""
		}, 3000)
	} catch (error) {
		console.error("Error saving program:", error)
		errorMessage.value = error.message || "Failed to save program. Please try again."
	} finally {
		saving.value = false
	}
}

const resetForm = () => {
	programForm.value = {
		program_id: "",
		program_name: "",
		audit_type: "",
		is_template: false,
		engagement_reference: "",
		program_objectives: "",
		program_procedures: [],
		risk_areas: [],
	}
	editingProgram.value = null
	errorMessage.value = ""
}

// Keyboard shortcuts
const handleKeydown = (event) => {
	// Ctrl/Cmd + N for new program
	if ((event.ctrlKey || event.metaKey) && event.key === 'n') {
		event.preventDefault()
		showCreateModal.value = true
	}
	// Escape to close modals
	if (event.key === 'Escape') {
		if (showCreateModal.value) {
			showCreateModal.value = false
			resetForm()
		} else if (showViewModal.value) {
			showViewModal.value = false
		}
	}
}

// New enhanced methods
const formatDate = (dateString) => {
	if (!dateString) return ""
	return new Date(dateString).toLocaleDateString()
}

const getTypeVariant = (type) => {
	const variants = {
		Financial: "primary",
		Operational: "secondary",
		Compliance: "warning",
		IT: "info",
		Inventory: "success",
		Cash: "danger",
		Sales: "primary",
		Procurement: "secondary",
	}
	return variants[type] || "secondary"
}

const getStatusVariant = (status) => {
	const variants = {
		Draft: "secondary",
		"In Progress": "warning",
		Completed: "success",
		Approved: "primary",
		Cancelled: "danger",
	}
	return variants[status] || "secondary"
}

const getProcedureStatusVariant = (status) => {
	const variants = {
		"Not Started": "secondary",
		"In Progress": "warning",
		"Completed": "success",
		"Not Applicable": "info",
	}
	return variants[status] || "secondary"
}

const isOverdue = (program) => {
	if (program.is_template) return false
	const now = new Date()
	if (!program.modified) return false
	const lastModified = new Date(program.modified)
	const daysSinceModified = (now - lastModified) / (1000 * 60 * 60 * 24)
	return daysSinceModified > 30 && (program.completion_percent || 0) < 100
}

const toggleProgramSelection = (programId) => {
	const index = selectedPrograms.value.indexOf(programId)
	if (index > -1) {
		selectedPrograms.value.splice(index, 1)
	} else {
		selectedPrograms.value.push(programId)
	}
	selectAll.value =
		selectedPrograms.value.length === paginatedPrograms.value.length
}

const toggleSelectAll = () => {
	if (selectAll.value) {
		selectedPrograms.value = []
	} else {
		selectedPrograms.value = paginatedPrograms.value.map((p) => p.name)
	}
}

const clearSelection = () => {
	selectedPrograms.value = []
	selectAll.value = false
}

const deleteProgram = async (program) => {
	if (
		!confirm(
			`Are you sure you want to delete "${program.program_name}"? This action cannot be undone.`,
		)
	) {
		return
	}

	try {
		await createResource({
			url: "frappe.client.delete",
			params: {
				doctype: "Audit Program",
				name: program.name,
			},
		}).fetch()
		await refreshData()
	} catch (error) {
		console.error("Error deleting program:", error)
		alert("Failed to delete program. Please try again.")
	}
}

const bulkDeletePrograms = async () => {
	if (selectedPrograms.value.length === 0) return

	const count = selectedPrograms.value.length
	if (
		!confirm(
			`Are you sure you want to delete ${count} program${count > 1 ? "s" : ""}? This action cannot be undone.`,
		)
	) {
		return
	}

	try {
		for (const programId of selectedPrograms.value) {
			await createResource({
				url: "frappe.client.delete",
				params: {
					doctype: "Audit Program",
					name: programId,
				},
			}).fetch()
		}
		selectedPrograms.value = []
		selectAll.value = false
		await refreshData()
	} catch (error) {
		console.error("Error deleting programs:", error)
		alert("Failed to delete some programs. Please try again.")
	}
}

const bulkCreateTemplates = async () => {
	if (selectedPrograms.value.length === 0) return

	const count = selectedPrograms.value.length
	if (!confirm(`Create templates for ${count} selected program${count > 1 ? 's' : ''}?`)) {
		return
	}

	try {
		for (const programId of selectedPrograms.value) {
			const program = auditPrograms.value.find(p => p.name === programId)
			if (program && !program.is_template) {
				await useAsTemplate(program)
			}
		}
		selectedPrograms.value = []
		selectAll.value = false
		successMessage.value = `Created templates for ${count} program${count > 1 ? 's' : ''}`
		setTimeout(() => {
			successMessage.value = ""
		}, 3000)
	} catch (error) {
		console.error("Error creating templates:", error)
		errorMessage.value = "Failed to create some templates. Please try again."
	}
}

const createProgramFromTemplate = () => {
	// This would open a template selection modal
	// For now, just show the create modal with template option
	showCreateModal.value = true
}

const exportPrograms = () => {
	const data = filteredPrograms.value.map((program) => ({
		"Program ID": program.program_id,
		"Program Name": program.program_name,
		"Audit Type": program.audit_type,
		"Is Template": program.is_template ? "Yes" : "No",
		Status: program.status || "Draft",
		"Completion %": program.completion_percent || 0,
		Created: formatDate(program.creation),
		Modified: formatDate(program.modified),
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
	a.download = `audit-programs-${new Date().toISOString().split("T")[0]}.csv`
	a.click()
	window.URL.revokeObjectURL(url)
}

// Watchers
watch(filteredPrograms, () => {
	currentPage.value = 1
	selectedPrograms.value = []
	selectAll.value = false
})

watch(searchQuery, () => {
	currentPage.value = 1
})

watch(filterType, () => {
	currentPage.value = 1
})

watch(filterTemplate, () => {
	currentPage.value = 1
})

watch(filterStatus, () => {
	currentPage.value = 1
})

// Lifecycle
onMounted(async () => {
	await refreshData()
	// Add keyboard event listener
	document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
	// Remove keyboard event listener
	document.removeEventListener('keydown', handleKeydown)
})
</script>