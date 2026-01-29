<template>
  <div class="space-y-6">
    <!-- Page Header with Enhanced Actions -->
    <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
      <div>
        <div class="flex items-center space-x-3">
          <div class="p-2 bg-blue-100 rounded-lg">
            <TargetIcon class="h-6 w-6 text-blue-600" />
          </div>
          <div>
            <h1 class="text-2xl font-bold text-gray-900">Audit Universe</h1>
            <p class="text-gray-600 mt-1">
              Manage auditable entities, risk areas, and audit planning scope
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
              @click="exportEntities"
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
              theme="blue"
              size="sm"
              @click="createNewEntity"
            >
              <template #prefix>
                <PlusIcon class="h-3.5 w-3.5" />
              </template>
              Add Entity
            </Button>
          </div>
        </div>
      </div>
    </div>

    <!-- Enhanced Stats Dashboard -->
    <UniverseStats :stats="universeStats" />

    <!-- Quick Actions Bar -->
    <UniverseFilters
      v-model="filters"
      @refresh="refreshData"
      @export="exportEntities"
      @create="showFormModal = true"
    />

    <!-- Audit Universe Display - Table or Card View -->
    <div class="bg-white rounded-xl border border-gray-200 shadow-sm">
      <div class="px-6 py-4 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-semibold text-gray-900">Auditable Entities</h3>
          <div class="flex items-center space-x-2">
            <div class="p-1" v-if="viewMode === 'table' && filteredEntities.length > 0">
              <Button
                variant="solid"
                theme="gray"
                size="sm"
                @click="selectAllEntities"
              >
                {{ selectedEntities.length === filteredEntities.length ? 'Deselect All' : 'Select All' }}
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
                  class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  :checked="selectedEntities.length === filteredEntities.length && filteredEntities.length > 0"
                  @change="selectAllEntities"
                />
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  @click="sortBy('auditable_entity')">
                <div class="flex items-center space-x-1">
                  <span>Entity Name</span>
                  <ArrowUpDownIcon class="h-3 w-3" />
                </div>
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  @click="sortBy('entity_type')">
                <div class="flex items-center space-x-1">
                  <span>Type</span>
                  <ArrowUpDownIcon class="h-3 w-3" />
                </div>
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Risk Level
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Last Audit
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Next Due
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr
              v-for="entity in filteredEntities"
              :key="entity.universe_id"
              class="hover:bg-gray-50 transition-colors"
              :class="{ 'bg-blue-50': selectedEntities.includes(entity.universe_id) }"
            >
              <td class="px-6 py-4">
                <input
                  type="checkbox"
                  class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  :checked="selectedEntities.includes(entity.universe_id)"
                  @change="toggleEntitySelection(entity.universe_id)"
                />
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="flex-shrink-0 h-10 w-10">
                    <div class="h-10 w-10 rounded-lg bg-blue-500 flex items-center justify-center text-white font-bold text-sm">
                      {{ entity.universe_id.slice(-2) }}
                    </div>
                  </div>
                  <div class="ml-4">
                    <div class="text-sm font-semibold text-gray-900">{{ entity.auditable_entity }}</div>
                    <div class="text-sm text-gray-500">{{ entity.department }}</div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ entity.entity_type }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <Badge :variant="getRiskVariant(entity.residual_risk_rating)">
                  {{ entity.residual_risk_rating }}
                </Badge>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <Badge :variant="entity.is_active ? 'success' : 'secondary'">
                  {{ entity.is_active ? 'Active' : 'Inactive' }}
                </Badge>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div v-if="entity.last_audit_date">
                  <p class="text-sm font-medium">{{ formatDate(entity.last_audit_date) }}</p>
                  <p class="text-xs text-gray-600">{{ entity.last_audit_opinion }}</p>
                </div>
                <span v-else class="text-gray-400 text-sm">Never</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div v-if="entity.next_scheduled_audit">
                  <p class="text-sm font-medium">{{ formatDate(entity.next_scheduled_audit) }}</p>
                  <Badge
                    v-if="isOverdue(entity.next_scheduled_audit)"
                    variant="danger"
                    size="sm"
                    class="mt-1"
                  >
                    Overdue
                  </Badge>
                </div>
                <span v-else class="text-gray-400 text-sm">Not scheduled</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div class="flex items-center space-x-1">
                  <Button
                    variant="solid"
                    theme="gray"
                    size="sm"
                    @click="viewEntity(entity)"
                    class="!p-1.5"
                  >
                    <EyeIcon class="h-3.5 w-3.5" />
                  </Button>
                  <Button
                    variant="solid"
                    theme="gray"
                    size="sm"
                    @click="editEntity(entity)"
                    class="!p-1.5"
                  >
                    <EditIcon class="h-3.5 w-3.5" />
                  </Button>
                  <Button
                    variant="solid"
                    theme="gray"
                    size="sm"
                    @click="scheduleAudit(entity)"
                    class="!p-1.5"
                  >
                    <CalendarIcon class="h-3.5 w-3.5" />
                  </Button>
                  <Button
                    variant="solid"
                    theme="gray"
                    size="sm"
                    @click="toggleEntityStatus(entity)"
                    class="!p-1.5"
                    :class="entity.is_active ? 'text-orange-600' : 'text-green-600'"
                  >
                    <PowerIcon class="h-3.5 w-3.5" />
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
            v-for="entity in filteredEntities"
            :key="entity.universe_id"
            class="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-lg transition-all duration-200 cursor-pointer group"
            :class="{ 'ring-2 ring-blue-500 bg-blue-50': selectedEntities.includes(entity.universe_id) }"
            @click="toggleEntitySelection(entity.universe_id)"
          >
            <div class="flex items-start justify-between mb-4">
              <div class="flex items-center space-x-3">
                <div class="h-12 w-12 rounded-xl bg-blue-500 flex items-center justify-center text-white font-bold">
                  {{ entity.universe_id.slice(-2) }}
                </div>
                <div>
                  <h3 class="text-lg font-semibold text-gray-900 group-hover:text-blue-900">{{ entity.auditable_entity }}</h3>
                  <p class="text-sm text-gray-600">{{ entity.entity_type }}</p>
                </div>
              </div>
              <Badge :variant="getRiskVariant(entity.residual_risk_rating)" size="sm">
                {{ entity.residual_risk_rating }}
              </Badge>
            </div>

            <div class="space-y-3">
              <div class="flex justify-between items-center">
                <span class="text-sm text-gray-600">Department</span>
                <span class="text-sm font-medium">{{ entity.department }}</span>
              </div>

              <div class="flex justify-between items-center">
                <span class="text-sm text-gray-600">Location</span>
                <span class="text-sm font-medium">{{ entity.location }}</span>
              </div>

              <div v-if="entity.next_scheduled_audit" class="flex justify-between items-center">
                <span class="text-sm text-gray-600">Next Audit</span>
                <span class="text-sm font-medium" :class="isOverdue(entity.next_scheduled_audit) ? 'text-red-600' : ''">
                  {{ formatDate(entity.next_scheduled_audit) }}
                </span>
              </div>

              <div class="flex justify-between items-center">
                <span class="text-sm text-gray-600">Risk Score</span>
                <span class="text-sm font-medium">{{ entity.residual_risk_score }}</span>
              </div>
            </div>

            <div class="flex items-center justify-between mt-6 pt-4 border-t border-gray-200">
              <Badge :variant="entity.is_active ? 'success' : 'secondary'" size="sm">
                {{ entity.is_active ? 'Active' : 'Inactive' }}
              </Badge>
              <div class="flex items-center space-x-1">
                <Button
                  variant="solid"
                  theme="gray"
                  size="sm"
                  @click.stop="viewEntity(entity)"
                  class="!p-1.5"
                >
                  <EyeIcon class="h-3.5 w-3.5" />
                </Button>
                <Button
                  variant="solid"
                  theme="gray"
                  size="sm"
                  @click.stop="editEntity(entity)"
                  class="!p-1.5"
                >
                  <EditIcon class="h-3.5 w-3.5" />
                </Button>
                <Button
                  variant="solid"
                  theme="gray"
                  size="sm"
                  @click.stop="scheduleAudit(entity)"
                  class="!p-1.5"
                >
                  <CalendarIcon class="h-3.5 w-3.5" />
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="filteredEntities.length === 0 && entities.length === 0" class="px-6 py-20 text-center">
        <div class="mx-auto h-20 w-20 rounded-2xl bg-blue-50 border-2 border-blue-100 flex items-center justify-center mb-8 shadow-sm">
          <TargetIcon class="h-10 w-10 text-blue-500" />
        </div>
        <div class="max-w-md mx-auto">
          <h3 class="text-2xl font-bold text-gray-900 mb-3">Welcome to Audit Universe</h3>
          <p class="text-gray-600 mb-8 leading-relaxed">
            Define your auditable entities and establish the foundation for comprehensive audit planning.
          </p>
          <div class="flex flex-col sm:flex-row justify-center gap-3">
            <Button
              variant="solid"
              theme="blue"
              size="lg"
              @click="createNewEntity"
              class="shadow-sm hover:shadow-md transition-shadow"
            >
              <template #prefix>
                <PlusIcon class="h-5 w-5" />
              </template>
              Add Your First Entity
            </Button>
            <Button
              variant="outline"
              theme="gray"
              size="lg"
              @click="showTemplateModal = true"
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
              <div class="h-2 w-2 bg-blue-500 rounded-full mr-3"></div>
              Quick Start Tips
            </h4>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div class="flex items-start space-x-3">
                <div class="flex-shrink-0 h-6 w-6 bg-blue-100 rounded-lg flex items-center justify-center mt-0.5">
                  <span class="text-blue-600 font-semibold text-xs">1</span>
                </div>
                <div>
                  <p class="font-medium text-gray-900">Define Entities</p>
                  <p class="text-gray-600">Identify all auditable processes and systems</p>
                </div>
              </div>
              <div class="flex items-start space-x-3">
                <div class="flex-shrink-0 h-6 w-6 bg-green-100 rounded-lg flex items-center justify-center mt-0.5">
                  <span class="text-green-600 font-semibold text-xs">2</span>
                </div>
                <div>
                  <p class="font-medium text-gray-900">Assess Risk</p>
                  <p class="text-gray-600">Evaluate inherent and residual risk levels</p>
                </div>
              </div>
              <div class="flex items-start space-x-3">
                <div class="flex-shrink-0 h-6 w-6 bg-purple-100 rounded-lg flex items-center justify-center mt-0.5">
                  <span class="text-purple-600 font-semibold text-xs">3</span>
                </div>
                <div>
                  <p class="font-medium text-gray-900">Plan Audits</p>
                  <p class="text-gray-600">Schedule audits based on risk and frequency</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- No Results State -->
      <div v-else-if="filteredEntities.length === 0" class="px-6 py-12 text-center">
        <SearchIcon class="mx-auto h-12 w-12 text-gray-400 mb-4" />
        <h3 class="text-lg font-medium text-gray-900 mb-2">No entities found</h3>
        <p class="text-gray-600 mb-6">
          Try adjusting your search or filter criteria to find the entities you're looking for.
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
      v-model="showTemplateModal"
      title="Entity Templates"
      :options="{ size: 'custom', width: '70vw' }"
    >
      <template #body>
        <div class="space-y-6 p-6 bg-gray-50">
          <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p class="text-blue-800 text-sm">
              💡 <strong>Pro Tip:</strong> Templates provide a structured starting point with pre-configured risk assessments and audit frequencies.
            </p>
          </div>
          
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6">
            <div class="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-lg hover:border-blue-300 cursor-pointer transition-all duration-200 group">
              <div class="flex items-start space-x-4 mb-5">
                <div class="flex-shrink-0 p-3 bg-blue-50 rounded-xl group-hover:bg-blue-100 transition-colors">
                  <BuildingIcon class="h-6 w-6 text-blue-600" />
                </div>
                <div class="flex-1">
                  <h3 class="font-bold text-gray-900 text-lg mb-2 group-hover:text-blue-900 transition-colors">Financial Process Template</h3>
                  <p class="text-gray-600 text-sm leading-relaxed">Pre-configured template for financial processes with standard risk assessments</p>
                </div>
              </div>
              
              <div class="mb-6">
                <h4 class="text-sm font-semibold text-gray-900 mb-3">Includes:</h4>
                <ul class="text-sm text-gray-600 space-y-2">
                  <li class="flex items-center space-x-2">
                    <div class="h-1.5 w-1.5 bg-blue-400 rounded-full"></div>
                    <span>Revenue cycle processes</span>
                  </li>
                  <li class="flex items-center space-x-2">
                    <div class="h-1.5 w-1.5 bg-blue-400 rounded-full"></div>
                    <span>Expenditure management</span>
                  </li>
                  <li class="flex items-center space-x-2">
                    <div class="h-1.5 w-1.5 bg-blue-400 rounded-full"></div>
                    <span>Financial reporting</span>
                  </li>
                  <li class="flex items-center space-x-2">
                    <div class="h-1.5 w-1.5 bg-blue-400 rounded-full"></div>
                    <span>Quarterly audit frequency</span>
                  </li>
                </ul>
              </div>
              
              <Button
                variant="solid"
                theme="blue"
                size="md"
                class="w-full shadow-sm hover:shadow-md transition-shadow"
              >
                <template #prefix>
                  <PlusIcon class="h-4 w-4" />
                </template>
                Use This Template
              </Button>
            </div>

            <div class="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-lg hover:border-green-300 cursor-pointer transition-all duration-200 group">
              <div class="flex items-start space-x-4 mb-5">
                <div class="flex-shrink-0 p-3 bg-green-50 rounded-xl group-hover:bg-green-100 transition-colors">
                  <TargetIcon class="h-6 w-6 text-green-600" />
                </div>
                <div class="flex-1">
                  <h3 class="font-bold text-gray-900 text-lg mb-2 group-hover:text-green-900 transition-colors">IT Systems Template</h3>
                  <p class="text-gray-600 text-sm leading-relaxed">Template for IT systems and cybersecurity controls</p>
                </div>
              </div>
              
              <div class="mb-6">
                <h4 class="text-sm font-semibold text-gray-900 mb-3">Includes:</h4>
                <ul class="text-sm text-gray-600 space-y-2">
                  <li class="flex items-center space-x-2">
                    <div class="h-1.5 w-1.5 bg-green-400 rounded-full"></div>
                    <span>Access controls</span>
                  </li>
                  <li class="flex items-center space-x-2">
                    <div class="h-1.5 w-1.5 bg-green-400 rounded-full"></div>
                    <span>Data protection</span>
                  </li>
                  <li class="flex items-center space-x-2">
                    <div class="h-1.5 w-1.5 bg-green-400 rounded-full"></div>
                    <span>System security</span>
                  </li>
                  <li class="flex items-center space-x-2">
                    <div class="h-1.5 w-1.5 bg-green-400 rounded-full"></div>
                    <span>Quarterly audit frequency</span>
                  </li>
                </ul>
              </div>
              
              <Button
                variant="solid"
                theme="green"
                size="md"
                class="w-full shadow-sm hover:shadow-md transition-shadow"
              >
                <template #prefix>
                  <TargetIcon class="h-4 w-4" />
                </template>
                Use This Template
              </Button>
            </div>

            <div class="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-lg hover:border-purple-300 cursor-pointer transition-all duration-200 group">
              <div class="flex items-start space-x-4 mb-5">
                <div class="flex-shrink-0 p-3 bg-purple-50 rounded-xl group-hover:bg-purple-100 transition-colors">
                  <UserIcon class="h-6 w-6 text-purple-600" />
                </div>
                <div class="flex-1">
                  <h3 class="font-bold text-gray-900 text-lg mb-2 group-hover:text-purple-900 transition-colors">HR Operations Template</h3>
                  <p class="text-gray-600 text-sm leading-relaxed">Template for HR processes and compliance requirements</p>
                </div>
              </div>
              
              <div class="mb-6">
                <h4 class="text-sm font-semibold text-gray-900 mb-3">Includes:</h4>
                <ul class="text-sm text-gray-600 space-y-2">
                  <li class="flex items-center space-x-2">
                    <div class="h-1.5 w-1.5 bg-purple-400 rounded-full"></div>
                    <span>Payroll processing</span>
                  </li>
                  <li class="flex items-center space-x-2">
                    <div class="h-1.5 w-1.5 bg-purple-400 rounded-full"></div>
                    <span>Employee records</span>
                  </li>
                  <li class="flex items-center space-x-2">
                    <div class="h-1.5 w-1.5 bg-purple-400 rounded-full"></div>
                    <span>Benefits administration</span>
                  </li>
                  <li class="flex items-center space-x-2">
                    <div class="h-1.5 w-1.5 bg-purple-400 rounded-full"></div>
                    <span>Annual audit frequency</span>
                  </li>
                </ul>
              </div>
              
              <Button
                variant="solid"
                theme="gray"
                size="md"
                class="w-full shadow-sm hover:shadow-md transition-shadow bg-purple-600 hover:bg-purple-700 text-white border-purple-600"
              >
                <template #prefix>
                  <UserIcon class="h-4 w-4" />
                </template>
                Use This Template
              </Button>
            </div>

            <div class="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-lg hover:border-amber-300 cursor-pointer transition-all duration-200 group">
              <div class="flex items-start space-x-4 mb-5">
                <div class="flex-shrink-0 p-3 bg-amber-50 rounded-xl group-hover:bg-amber-100 transition-colors">
                  <ClockIcon class="h-6 w-6 text-amber-600" />
                </div>
                <div class="flex-1">
                  <h3 class="font-bold text-gray-900 text-lg mb-2 group-hover:text-amber-900 transition-colors">Operations Template</h3>
                  <p class="text-gray-600 text-sm leading-relaxed">Template for operational processes and efficiency controls</p>
                </div>
              </div>
              
              <div class="mb-6">
                <h4 class="text-sm font-semibold text-gray-900 mb-3">Includes:</h4>
                <ul class="text-sm text-gray-600 space-y-2">
                  <li class="flex items-center space-x-2">
                    <div class="h-1.5 w-1.5 bg-amber-400 rounded-full"></div>
                    <span>Procurement processes</span>
                  </li>
                  <li class="flex items-center space-x-2">
                    <div class="h-1.5 w-1.5 bg-amber-400 rounded-full"></div>
                    <span>Inventory management</span>
                  </li>
                  <li class="flex items-center space-x-2">
                    <div class="h-1.5 w-1.5 bg-amber-400 rounded-full"></div>
                    <span>Quality control</span>
                  </li>
                  <li class="flex items-center space-x-2">
                    <div class="h-1.5 w-1.5 bg-amber-400 rounded-full"></div>
                    <span>Semi-annual audit frequency</span>
                  </li>
                </ul>
              </div>
              
              <Button
                variant="solid"
                theme="gray"
                size="md"
                class="w-full shadow-sm hover:shadow-md transition-shadow bg-amber-500 hover:bg-amber-600 text-white border-amber-500"
              >
                <template #prefix>
                  <ClockIcon class="h-4 w-4" />
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
          <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p class="text-blue-800">
              <span class="font-semibold">{{ selectedEntities.length }}</span> entit(ies) selected for bulk action.
            </p>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="p-1">
              <Button
                variant="solid"
                theme="green"
                class="h-20 w-full"
                @click="bulkUpdateStatus"
              >
                <div class="flex flex-col items-center justify-center space-y-2">
                  <PowerIcon class="h-5 w-5" />
                  <span class="text-sm font-medium">Update Status</span>
                </div>
              </Button>
            </div>

            <div class="p-1">
              <Button
                variant="solid"
                theme="blue"
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
                theme="purple"
                class="h-20 w-full"
                @click="showRiskModal = true; showBulkModal = false"
              >
                <div class="flex flex-col items-center justify-center space-y-2">
                  <BarChart3Icon class="h-5 w-5" />
                  <span class="text-sm font-medium">Risk Analysis</span>
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

    <!-- Risk Analysis Modal -->
    <Dialog
      v-model="showRiskModal"
      title="Risk Analysis Dashboard"
      size="5xl"
    >
      <template #body>
        <div class="space-y-6">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="bg-red-50 rounded-lg p-6">
              <h3 class="text-lg font-semibold text-red-900 mb-4">Critical Risk Entities</h3>
              <div class="space-y-3">
                <div class="flex justify-between">
                  <span class="text-red-700">Count</span>
                  <span class="font-medium text-red-900">{{ criticalRiskCount }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-red-700">Percentage</span>
                  <span class="font-medium text-red-900">{{ ((criticalRiskCount / Math.max(totalEntities, 1)) * 100).toFixed(1) }}%</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-red-700">Priority Level</span>
                  <span class="font-medium text-red-900">High</span>
                </div>
              </div>
            </div>

            <div class="bg-amber-50 rounded-lg p-6">
              <h3 class="text-lg font-semibold text-amber-900 mb-4">High Risk Entities</h3>
              <div class="space-y-3">
                <div class="flex justify-between">
                  <span class="text-amber-700">Count</span>
                  <span class="font-medium text-amber-900">{{ highRiskCount }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-amber-700">Percentage</span>
                  <span class="font-medium text-amber-900">{{ ((highRiskCount / Math.max(totalEntities, 1)) * 100).toFixed(1) }}%</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-amber-700">Priority Level</span>
                  <span class="font-medium text-amber-900">Medium</span>
                </div>
              </div>
            </div>

            <div class="bg-green-50 rounded-lg p-6">
              <h3 class="text-lg font-semibold text-green-900 mb-4">Low Risk Entities</h3>
              <div class="space-y-3">
                <div class="flex justify-between">
                  <span class="text-green-700">Count</span>
                  <span class="font-medium text-green-900">{{ entities.value.filter(e => e.residual_risk_rating === 'Low').length }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-green-700">Percentage</span>
                  <span class="font-medium text-green-900">{{ ((entities.value.filter(e => e.residual_risk_rating === 'Low').length / Math.max(totalEntities, 1)) * 100).toFixed(1) }}%</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-green-700">Priority Level</span>
                  <span class="font-medium text-green-900">Low</span>
                </div>
              </div>
            </div>
          </div>

          <div class="bg-white border border-gray-200 rounded-lg p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Risk Distribution</h3>
            <div class="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
              <p class="text-gray-500">Risk distribution chart would be displayed here</p>
            </div>
          </div>
        </div>
      </template>
    </Dialog>
  </div>

  <!-- Audit Universe Form Modal -->
  <AuditUniverseForm
    :show="showFormModal"
    :entity="selectedEntity"
    :mode="formMode"
    @update:show="showFormModal = $event"
    @saved="onEntitySaved"
  />
</template>

<script setup>
import { Badge, Button, Dialog, FormControl, Select } from "frappe-ui"
import {
	AlertTriangleIcon,
	ArrowUpDownIcon,
	BarChart3Icon,
	BuildingIcon,
	CalendarIcon,
	CheckCircleIcon,
	ClockIcon,
	DownloadIcon,
	EditIcon,
	EyeIcon,
	FileTextIcon,
	GridIcon,
	LayersIcon,
	LayoutGridIcon,
	ListIcon,
	MapPinIcon,
	PlusIcon,
	PowerIcon,
	RefreshCwIcon,
	SearchIcon,
	TableIcon,
	TargetIcon,
	TrashIcon,
	UserIcon,
} from "lucide-vue-next"
import { computed, ref } from "vue"
import { useRouter } from "vue-router"
import UniverseStats from "@/components/universe/UniverseStats.vue"
import UniverseFilters from "@/components/universe/UniverseFilters.vue"
import AuditUniverseForm from "@/components/universe/AuditUniverseForm.vue"

const router = useRouter()

// Reactive state
const loading = ref(false)
const exporting = ref(false)
const viewMode = ref("table") // "table" or "cards"
const selectedEntities = ref([])
const sortField = ref("auditable_entity")
const sortDirection = ref("asc")
const showTemplateModal = ref(false)
const showBulkModal = ref(false)
const showRiskModal = ref(false)
const showFormModal = ref(false)
const selectedEntity = ref(null)
const formMode = ref("create")

// Filters object for UniverseFilters component
const filters = ref({
  search: "",
  entityType: "",
  riskRating: "",
  department: "",
  status: "",
})

const entities = ref([
	{
		universe_id: "AU-001",
		auditable_entity: "Accounts Payable",
		entity_type: "Process",
		department: "Finance",
		location: "Head Office",
		description: "Processing of vendor payments and expense reimbursements",
		process_owner: "John Doe",
		inherent_risk_rating: "High",
		inherent_risk_score: 15,
		control_environment_rating: "Adequate",
		control_effectiveness_score: 3,
		residual_risk_rating: "Medium",
		residual_risk_score: 5,
		risk_factors: [],
		key_controls: [],
		audit_frequency: "Quarterly",
		last_audit_date: "2023-10-15",
		last_audit_opinion: "Satisfactory",
		next_scheduled_audit: "2024-01-15",
		mandatory_audit: false,
		regulatory_reference: "",
		bc_data_sources: [],
		notes: "",
		is_active: true,
	},
	{
		universe_id: "AU-002",
		auditable_entity: "IT Security Controls",
		entity_type: "System",
		department: "IT",
		location: "Head Office",
		description: "Access controls, data protection, and cybersecurity measures",
		process_owner: "Jane Smith",
		inherent_risk_rating: "Critical",
		inherent_risk_score: 25,
		control_environment_rating: "Strong",
		control_effectiveness_score: 4,
		residual_risk_rating: "High",
		residual_risk_score: 6,
		risk_factors: [],
		key_controls: [],
		audit_frequency: "Quarterly",
		last_audit_date: "2023-08-20",
		last_audit_opinion: "Needs Improvement",
		next_scheduled_audit: "2023-11-20",
		mandatory_audit: true,
		regulatory_reference: "CBK Cybersecurity Guidelines",
		bc_data_sources: [],
		notes: "",
		is_active: true,
	},
	{
		universe_id: "AU-003",
		auditable_entity: "Inventory Management",
		entity_type: "Process",
		department: "Operations",
		location: "Warehouse",
		description: "Stock control, valuation, and warehouse operations",
		process_owner: "Bob Johnson",
		inherent_risk_rating: "Medium",
		inherent_risk_score: 8,
		control_environment_rating: "Adequate",
		control_effectiveness_score: 3,
		residual_risk_rating: "Low",
		residual_risk_score: 3,
		risk_factors: [],
		key_controls: [],
		audit_frequency: "Semi-Annual",
		last_audit_date: "2023-09-10",
		last_audit_opinion: "Satisfactory",
		next_scheduled_audit: "2024-03-10",
		mandatory_audit: false,
		regulatory_reference: "",
		bc_data_sources: [],
		notes: "",
		is_active: true,
	},
	{
		universe_id: "AU-004",
		auditable_entity: "HR Payroll",
		entity_type: "Process",
		department: "HR",
		location: "Head Office",
		description: "Employee compensation, benefits, and payroll processing",
		process_owner: "Alice Brown",
		inherent_risk_rating: "High",
		inherent_risk_score: 15,
		control_environment_rating: "Weak",
		control_effectiveness_score: 2,
		residual_risk_rating: "High",
		residual_risk_score: 8,
		risk_factors: [],
		key_controls: [],
		audit_frequency: "Quarterly",
		last_audit_date: null,
		last_audit_opinion: "",
		next_scheduled_audit: "2023-12-01",
		mandatory_audit: true,
		regulatory_reference: "Employment Act, PAYE Regulations",
		bc_data_sources: [],
		notes: "",
		is_active: true,
	},
	{
		universe_id: "AU-005",
		auditable_entity: "Sales Order Processing",
		entity_type: "Process",
		department: "Sales",
		location: "Head Office",
		description: "Customer order processing and fulfillment",
		process_owner: "Charlie Wilson",
		inherent_risk_rating: "Medium",
		inherent_risk_score: 8,
		control_environment_rating: "Adequate",
		control_effectiveness_score: 3,
		residual_risk_rating: "Low",
		residual_risk_score: 3,
		risk_factors: [],
		key_controls: [],
		audit_frequency: "Semi-Annual",
		last_audit_date: "2023-07-15",
		last_audit_opinion: "Satisfactory",
		next_scheduled_audit: "2024-01-15",
		mandatory_audit: false,
		regulatory_reference: "",
		bc_data_sources: [],
		notes: "",
		is_active: false,
	},
])

// Computed properties
const totalEntities = computed(() => entities.value.length)
const criticalRiskCount = computed(
	() =>
		entities.value.filter((e) => e.residual_risk_rating === "Critical").length,
)
const highRiskCount = computed(
	() => entities.value.filter((e) => e.residual_risk_rating === "High").length,
)
const dueThisQuarter = computed(() => {
	const now = new Date()
	const quarterEnd = new Date(
		now.getFullYear(),
		Math.floor(now.getMonth() / 3) * 3 + 3,
		0,
	)
	return entities.value.filter((e) => {
		if (!e.next_scheduled_audit) return false
		const dueDate = new Date(e.next_scheduled_audit)
		return dueDate <= quarterEnd
	}).length
})
const inactiveCount = computed(
	() => entities.value.filter((e) => !e.is_active).length,
)

const filteredEntities = computed(() => {
	let filtered = [...entities.value]

	// Apply search filter
	if (filters.value.search) {
		const query = filters.value.search.toLowerCase()
		filtered = filtered.filter(
			(entity) =>
				entity.auditable_entity?.toLowerCase().includes(query) ||
				entity.description?.toLowerCase().includes(query) ||
				entity.process_owner?.toLowerCase().includes(query) ||
				entity.department?.toLowerCase().includes(query),
		)
	}

	// Apply risk filter
	if (filters.value.riskRating) {
		filtered = filtered.filter(
			(entity) => entity.residual_risk_rating === filters.value.riskRating,
		)
	}

	// Apply type filter
	if (filters.value.entityType) {
		filtered = filtered.filter(
			(entity) => entity.entity_type === filters.value.entityType,
		)
	}

	// Apply department filter
	if (filters.value.department) {
		filtered = filtered.filter(
			(entity) => entity.department === filters.value.department,
		)
	}

	// Apply status filter
	if (filters.value.status) {
		filtered = filtered.filter(
			(entity) =>
				(filters.value.status === "active" && entity.is_active) ||
				(filters.value.status === "inactive" && !entity.is_active),
		)
	}

	// Apply sorting
	filtered.sort((a, b) => {
		const aVal = a[sortField.value] || ""
		const bVal = b[sortField.value] || ""

		if (sortDirection.value === "asc") {
			return aVal > bVal ? 1 : -1
		} else {
			return aVal < bVal ? 1 : -1
		}
	})

	return filtered
})

// Stats for UniverseStats component
const universeStats = computed(() => {
  const total = entities.value.length
  const criticalRisk = entities.value.filter(e => e.residual_risk_rating === "Critical").length
  const highRisk = entities.value.filter(e => e.residual_risk_rating === "High").length
  const mediumRisk = entities.value.filter(e => e.residual_risk_rating === "Medium").length
  const lowRisk = entities.value.filter(e => e.residual_risk_rating === "Low").length
  const active = entities.value.filter(e => e.is_active).length
  const inactive = entities.value.filter(e => !e.is_active).length

  const now = new Date()
  const quarterEnd = new Date(now.getFullYear(), Math.floor(now.getMonth() / 3) * 3 + 3, 0)
  const dueThisQuarter = entities.value.filter(e => {
    if (!e.next_scheduled_audit) return false
    const dueDate = new Date(e.next_scheduled_audit)
    return dueDate <= quarterEnd
  }).length

  const dueThisMonth = entities.value.filter(e => {
    if (!e.next_scheduled_audit) return false
    const dueDate = new Date(e.next_scheduled_audit)
    const nextMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0)
    return dueDate <= nextMonth
  }).length

  const overdue = entities.value.filter(e => {
    if (!e.next_scheduled_audit) return false
    const dueDate = new Date(e.next_scheduled_audit)
    return dueDate < now
  }).length

  const mandatory = entities.value.filter(e => e.mandatory_audit).length

  // Group by entity type
  const byType = {}
  entities.value.forEach(e => {
    byType[e.entity_type] = (byType[e.entity_type] || 0) + 1
  })

  // Group by control environment
  const byControlEnvironment = {}
  entities.value.forEach(e => {
    byControlEnvironment[e.control_environment_rating] = (byControlEnvironment[e.control_environment_rating] || 0) + 1
  })

  return {
    total,
    criticalRisk,
    highRisk,
    mediumRisk,
    lowRisk,
    active,
    inactive,
    dueThisQuarter,
    dueThisMonth,
    overdue,
    mandatory,
    byType,
    byControlEnvironment,
  }
})

// Methods
const getRiskVariant = (risk) => {
	const variants = {
		Critical: "danger",
		High: "danger",
		Medium: "warning",
		Low: "success",
	}
	return variants[risk] || "secondary"
}

const formatDate = (date) => {
	return new Date(date).toLocaleDateString()
}

const isOverdue = (dateString) => {
	if (!dateString) return false
	const dueDate = new Date(dateString)
	const today = new Date()
	return dueDate < today
}

const refreshData = async () => {
	loading.value = true
	try {
		// Fetch fresh data from backend
		await auditStore.fetchAuditUniverse()

		// Update the local universeList with fresh data
		const freshData = auditStore.auditUniverse || []
		universeList.value = freshData.map((entity) => ({
			...entity,
			riskLevel: calculateRiskLevel(entity),
			lastAudit: formatLastAuditDate(entity.last_audit_date),
		}))
	} catch (error) {
		console.error("Error refreshing audit universe data:", error)
	} finally {
		loading.value = false
	}
}

const viewEntity = (entity) => {
	router.push(`/audit-planning/universe/${entity.universe_id}`)
}

const scheduleAudit = (entity) => {
	// Navigate to audit scheduling
	console.log("Schedule audit for:", entity.universe_id)
}

const toggleEntityStatus = (entity) => {
	entity.is_active = !entity.is_active
	// In a real app, this would update the backend
	console.log(
		"Toggled status for:",
		entity.universe_id,
		"to:",
		entity.is_active,
	)
}

// Selection methods
const toggleEntitySelection = (entityId) => {
	const index = selectedEntities.value.indexOf(entityId)
	if (index > -1) {
		selectedEntities.value.splice(index, 1)
	} else {
		selectedEntities.value.push(entityId)
	}
}

const selectAllEntities = () => {
	if (selectedEntities.value.length === filteredEntities.value.length) {
		selectedEntities.value = []
	} else {
		selectedEntities.value = filteredEntities.value.map(
			(entity) => entity.universe_id,
		)
	}
}

// Sorting methods
const sortBy = (field) => {
	if (sortField.value === field) {
		sortDirection.value = sortDirection.value === "asc" ? "desc" : "asc"
	} else {
		sortField.value = field
		sortDirection.value = "asc"
	}
}

// Filter methods
const clearFilters = () => {
	filters.value = {
    search: "",
    entityType: "",
    riskRating: "",
    department: "",
    status: "",
  }
	selectedEntities.value = []
}

// Form methods
const createNewEntity = () => {
	selectedEntity.value = null
	formMode.value = "create"
	showFormModal.value = true
}

const editEntity = (entity) => {
	selectedEntity.value = entity
	formMode.value = "edit"
	showFormModal.value = true
}

const onEntitySaved = () => {
	// Refresh data after entity is saved
	refreshData()
	showFormModal.value = false
	selectedEntity.value = null
}

// Bulk action methods
const bulkUpdateStatus = () => {
	console.log("Bulk update status for:", selectedEntities.value)
	showBulkModal.value = false
}

const bulkExport = () => {
	console.log("Bulk export for:", selectedEntities.value)
	showBulkModal.value = false
}

const bulkDelete = () => {
	console.log("Bulk delete for:", selectedEntities.value)
	showBulkModal.value = false
}
</script>