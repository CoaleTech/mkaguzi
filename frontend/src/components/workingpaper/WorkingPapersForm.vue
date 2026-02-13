<template>
  <Dialog
    v-model="isOpen"
    :options="{
      title: isEditMode ? 'Edit Working Paper' : 'Create New Working Paper',
      size: 'full'
    }"
  >
    <template #body-content>
      <div class="h-[80vh] flex">
        <!-- Progress Sidebar -->
        <div class="w-64 bg-gray-50 border-r border-gray-200 flex-shrink-0 overflow-y-auto">
          <div class="p-5">
            <h4 class="text-sm font-semibold text-gray-900 mb-4">Form Sections</h4>
            <nav class="space-y-1">
              <button
                v-for="(section, index) in formSections"
                :key="section.id"
                @click="activeSection = section.id"
                class="w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-left transition-all"
                :class="[
                  activeSection === section.id
                    ? 'bg-gray-100 border border-gray-300 text-gray-800'
                    : 'hover:bg-gray-100 text-gray-700'
                ]"
              >
                <div
                  class="w-6 h-6 rounded-full flex items-center justify-center text-xs font-semibold flex-shrink-0"
                  :class="getSectionStatusClass(section.id)"
                >
                  <CheckIcon v-if="getSectionStatus(section.id) === 'complete'" class="h-3 w-3" />
                  <span v-else>{{ index + 1 }}</span>
                </div>
                <div class="flex-1 min-w-0">
                  <div class="text-sm font-medium truncate">{{ section.label }}</div>
                  <div class="text-xs text-gray-500">{{ section.description }}</div>
                </div>
              </button>
            </nav>

            <!-- Progress Summary -->
            <div class="mt-6 p-4 bg-white rounded-lg border border-gray-200">
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-medium text-gray-700">Progress</span>
                <span class="text-sm font-bold text-gray-900">{{ formProgress }}%</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div
                  class="bg-gray-900 h-2 rounded-full transition-all duration-300"
                  :style="{ width: `${formProgress}%` }"
                ></div>
              </div>
              <p class="text-xs text-gray-500 mt-2">
                {{ completedSections }} of {{ formSections.length }} sections complete
              </p>
            </div>
          </div>
        </div>

        <!-- Main Form Content -->
        <div class="flex-1 overflow-y-auto">
          <div class="p-6 max-w-5xl mx-auto">
            <!-- Section: Basic Information -->
            <div v-show="activeSection === 'basic'" class="space-y-6">
              <SectionHeader
                title="Basic Information"
                description="Essential working paper details and identification"
                icon="file-text"
                step="1"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <!-- Working Paper ID -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Working Paper ID <span class="text-red-500">*</span>
                    </label>
                    <input
                      v-model="form.working_paper_id"
                      type="text"
                      placeholder="Auto-generated if left blank"
                      class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-gray-900 focus:border-transparent transition"
                      :class="errors.working_paper_id ? 'border-red-300' : 'border-gray-300'"
                    />
                    <p v-if="errors.working_paper_id" class="mt-1 text-xs text-red-500">{{ errors.working_paper_id }}</p>
                    <p v-else class="mt-1 text-xs text-gray-500">Format: WP-YYYY-XXX</p>
                  </div>

                  <!-- Status -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Review Status <span class="text-red-500">*</span>
                    </label>
                    <select
                      v-model="form.review_status"
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                    >
                      <option v-for="opt in reviewStatusOptions" :key="opt.value" :value="opt.value">
                        {{ opt.label }}
                      </option>
                    </select>
                  </div>

                  <!-- Type -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Type <span class="text-red-500">*</span>
                    </label>
                    <select
                      v-model="form.wp_type"
                      class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-gray-900 focus:border-transparent transition"
                      :class="errors.wp_type ? 'border-red-300' : 'border-gray-300'"
                    >
                      <option value="">Select type</option>
                      <option v-for="opt in wpTypeOptions" :key="opt.value" :value="opt.value">
                        {{ opt.label }}
                      </option>
                    </select>
                    <p v-if="errors.wp_type" class="mt-1 text-xs text-red-500">{{ errors.wp_type }}</p>
                  </div>
                </div>

                <!-- Title -->
                <div class="mt-6">
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">
                    Title <span class="text-red-500">*</span>
                  </label>
                  <input
                    v-model="form.wp_title"
                    type="text"
                    placeholder="Enter working paper title"
                    class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-gray-900 focus:border-transparent transition"
                    :class="errors.wp_title ? 'border-red-300' : 'border-gray-300'"
                  />
                  <p v-if="errors.wp_title" class="mt-1 text-xs text-red-500">{{ errors.wp_title }}</p>
                </div>

                <!-- Reference Number -->
                <div class="mt-6">
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">
                    Reference Number
                  </label>
                  <input
                    v-model="form.wp_reference_no"
                    type="text"
                    placeholder="REF-001"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                  />
                </div>

                <!-- References Row -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
                  <!-- Engagement Reference -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Engagement Reference <span class="text-red-500">*</span>
                    </label>
                    <LinkField
                      v-model="form.engagement_reference"
                      doctype="Audit Engagement"
                      placeholder="Select audit engagement"
                      :required="true"
                      :error="errors.engagement_reference"
                    />
                  </div>

                  <!-- Procedure Reference -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Procedure Reference
                    </label>
                    <LinkField
                      v-model="form.procedure_reference"
                      doctype="Audit Procedure"
                      placeholder="Link to audit procedure"
                    />
                  </div>
                </div>
              </div>
            </div>

            <!-- Section: Content & Work Performed -->
            <div v-show="activeSection === 'content'" class="space-y-6">
              <SectionHeader
                title="Content & Work Performed"
                description="Document the work performed and findings"
                icon="clipboard-list"
                step="2"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6 space-y-6">
                <!-- Work Performed -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">
                    Work Performed <span class="text-red-500">*</span>
                  </label>
                  <textarea
                    v-model="form.work_performed"
                    rows="6"
                    placeholder="Describe the work performed, procedures followed, and methodology used..."
                    class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-gray-900 focus:border-transparent transition"
                    :class="errors.work_performed ? 'border-red-300' : 'border-gray-300'"
                  ></textarea>
                  <p v-if="errors.work_performed" class="mt-1 text-xs text-red-500">{{ errors.work_performed }}</p>
                </div>

                <!-- Objective -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">
                    Objective
                  </label>
                  <textarea
                    v-model="form.objective"
                    rows="3"
                    placeholder="What was the objective of this working paper?"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                  ></textarea>
                </div>

                <!-- Scope -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">
                    Scope
                  </label>
                  <textarea
                    v-model="form.scope"
                    rows="3"
                    placeholder="Define the scope and boundaries of this working paper..."
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                  ></textarea>
                </div>
              </div>
            </div>

            <!-- Section: Assignment & Timeline -->
            <div v-show="activeSection === 'assignment'" class="space-y-6">
              <SectionHeader
                title="Assignment & Timeline"
                description="Assign team members and track progress"
                icon="users"
                step="3"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6 space-y-6">
                <!-- Assignment Row -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <!-- Prepared By -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Prepared By <span class="text-red-500">*</span>
                    </label>
                    <LinkField
                      v-model="form.prepared_by"
                      doctype="User"
                      :filters="{ enabled: 1 }"
                      placeholder="Select preparer"
                      :required="true"
                      :error="errors.prepared_by"
                    />
                  </div>

                  <!-- Reviewed By -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Reviewed By
                    </label>
                    <LinkField
                      v-model="form.reviewed_by"
                      doctype="User"
                      :filters="{ enabled: 1 }"
                      placeholder="Select reviewer"
                    />
                  </div>
                </div>

                <!-- Dates Row -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <!-- Preparation Date -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Preparation Date <span class="text-red-500">*</span>
                    </label>
                    <input
                      v-model="form.preparation_date"
                      type="date"
                      class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                      :class="errors.preparation_date ? 'border-red-300' : 'border-gray-300'"
                    />
                    <p v-if="errors.preparation_date" class="mt-1 text-xs text-red-500">{{ errors.preparation_date }}</p>
                  </div>

                  <!-- Review Date -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Review Date
                    </label>
                    <input
                      v-model="form.review_date"
                      type="date"
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                    />
                  </div>

                  <!-- Due Date -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Due Date
                    </label>
                    <input
                      v-model="form.due_date"
                      type="date"
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                    />
                  </div>
                </div>
              </div>
            </div>

            <!-- Section: Quality & Documentation -->
            <div v-show="activeSection === 'quality'" class="space-y-6">
              <SectionHeader
                title="Quality Control & Documentation"
                description="Quality assessment and documentation references"
                icon="check-circle"
                step="4"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6 space-y-6">
                <!-- Quality Assessment -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <!-- Quality Score -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Quality Score
                    </label>
                    <select
                      v-model="form.quality_score"
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                    >
                      <option value="">Select score</option>
                      <option value="1">1 - Poor</option>
                      <option value="2">2 - Below Average</option>
                      <option value="3">3 - Average</option>
                      <option value="4">4 - Good</option>
                      <option value="5">5 - Excellent</option>
                    </select>
                  </div>

                  <!-- Review Comments -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Review Comments
                    </label>
                    <textarea
                      v-model="form.review_comments"
                      rows="3"
                      placeholder="Reviewer feedback and comments..."
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                    ></textarea>
                  </div>
                </div>

                <!-- Documentation References -->
                <div class="border-t border-gray-200 pt-6">
                  <h4 class="text-sm font-semibold text-gray-900 mb-4">Documentation References</h4>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <!-- Supporting Documents -->
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1.5">
                        Supporting Documents
                      </label>
                      <textarea
                        v-model="form.supporting_documents"
                        rows="3"
                        placeholder="List supporting documents, references, and evidence..."
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                      ></textarea>
                    </div>

                    <!-- File Attachments -->
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1.5">
                        File Attachments
                      </label>
                      <FileUploader
                        v-model="form.attachments"
                        :multiple="true"
                        accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png"
                        placeholder="Upload working paper files"
                      />
                    </div>
                  </div>
                </div>

                <!-- Additional Notes -->
                <div class="border-t border-gray-200 pt-6">
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">
                    Additional Notes
                  </label>
                  <textarea
                    v-model="form.notes"
                    rows="3"
                    placeholder="Any additional notes or observations..."
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                  ></textarea>
                </div>
              </div>
            </div>

            <!-- Section: Sample Selection -->
            <div v-show="activeSection === 'samples'" class="space-y-6">
              <SectionHeader
                title="Sample Selection"
                description="Define and track sample items tested"
                icon="list-checks"
                step="5"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6 space-y-6">
                <!-- Summary Stats -->
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div class="bg-gray-50 rounded-lg p-3 text-center">
                    <p class="text-2xl font-bold text-gray-900">{{ form.sample_selection.length }}</p>
                    <p class="text-xs text-gray-500">Total Samples</p>
                  </div>
                  <div class="bg-green-50 rounded-lg p-3 text-center">
                    <p class="text-2xl font-bold text-green-600">{{ samplePassCount }}</p>
                    <p class="text-xs text-gray-500">Passed</p>
                  </div>
                  <div class="bg-red-50 rounded-lg p-3 text-center">
                    <p class="text-2xl font-bold text-red-600">{{ sampleFailCount }}</p>
                    <p class="text-xs text-gray-500">Failed</p>
                  </div>
                  <div class="bg-amber-50 rounded-lg p-3 text-center">
                    <p class="text-2xl font-bold text-amber-600">{{ sampleExceptionCount }}</p>
                    <p class="text-xs text-gray-500">Exceptions</p>
                  </div>
                </div>

                <!-- Sample Items Table -->
                <div class="border border-gray-200 rounded-lg overflow-hidden">
                  <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                      <tr>
                        <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Item ID</th>
                        <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                        <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                        <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Result</th>
                        <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Exception</th>
                        <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
                      </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-200">
                      <tr v-for="(item, idx) in form.sample_selection" :key="idx" class="hover:bg-gray-50">
                        <td class="px-4 py-3">
                          <input
                            v-model="item.item_id"
                            type="text"
                            placeholder="ITEM-001"
                            class="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                          />
                        </td>
                        <td class="px-4 py-3">
                          <input
                            v-model="item.item_description"
                            type="text"
                            placeholder="Description..."
                            class="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                          />
                        </td>
                        <td class="px-4 py-3">
                          <input
                            v-model="item.sample_amount"
                            type="number"
                            step="0.01"
                            placeholder="0.00"
                            class="w-24 px-2 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                          />
                        </td>
                        <td class="px-4 py-3">
                          <select
                            v-model="item.test_result"
                            class="px-2 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                          >
                            <option value="">Select</option>
                            <option value="Pass">Pass</option>
                            <option value="Fail">Fail</option>
                            <option value="Not Tested">Not Tested</option>
                          </select>
                        </td>
                        <td class="px-4 py-3">
                          <div class="flex items-center space-x-2">
                            <input type="checkbox" v-model="item.exception_found" class="rounded text-gray-900" />
                            <input
                              v-if="item.exception_found"
                              v-model="item.exception_details"
                              type="text"
                              placeholder="Details..."
                              class="flex-1 px-2 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                            />
                          </div>
                        </td>
                        <td class="px-4 py-3 text-right">
                          <button
                            @click="removeSampleItem(idx)"
                            class="text-red-500 hover:text-red-700 text-sm"
                          >
                            <TrashIcon class="h-4 w-4" />
                          </button>
                        </td>
                      </tr>
                      <tr v-if="form.sample_selection.length === 0">
                        <td colspan="6" class="px-4 py-8 text-center text-gray-500 text-sm">
                          No sample items added yet. Click "Add Sample" to begin.
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                <Button variant="outline" size="sm" @click="addSampleItem">
                  <template #prefix><PlusIcon class="h-3.5 w-3.5" /></template>
                  Add Sample
                </Button>
              </div>
            </div>

            <!-- Section: Analytical Procedures -->
            <div v-show="activeSection === 'analytical'" class="space-y-6">
              <SectionHeader
                title="Analytical Procedures"
                description="Document analytical procedures and variance analysis"
                icon="bar-chart"
                step="6"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6 space-y-6">
                <!-- Procedure Items -->
                <div v-for="(proc, idx) in form.analytical_procedures" :key="idx" class="border border-gray-200 rounded-lg p-4 space-y-4">
                  <div class="flex items-center justify-between">
                    <h5 class="text-sm font-semibold text-gray-900">Procedure {{ idx + 1 }}</h5>
                    <button @click="removeAnalyticalProcedure(idx)" class="text-red-500 hover:text-red-700">
                      <TrashIcon class="h-4 w-4" />
                    </button>
                  </div>

                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label class="block text-xs font-medium text-gray-600 mb-1">Procedure Name *</label>
                      <input
                        v-model="proc.procedure_name"
                        type="text"
                        placeholder="e.g., Revenue Trend Analysis"
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label class="block text-xs font-medium text-gray-600 mb-1">Procedure Type</label>
                      <select
                        v-model="proc.procedure_type"
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                      >
                        <option value="">Select type</option>
                        <option value="Ratio Analysis">Ratio Analysis</option>
                        <option value="Trend Analysis">Trend Analysis</option>
                        <option value="Reasonableness Test">Reasonableness Test</option>
                        <option value="Regression Analysis">Regression Analysis</option>
                        <option value="Other">Other</option>
                      </select>
                    </div>
                  </div>

                  <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div>
                      <label class="block text-xs font-medium text-gray-600 mb-1">Expected Result</label>
                      <input
                        v-model="proc.expected_result"
                        type="number"
                        step="0.01"
                        placeholder="0.00"
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label class="block text-xs font-medium text-gray-600 mb-1">Actual Result *</label>
                      <input
                        v-model="proc.actual_result"
                        type="number"
                        step="0.01"
                        placeholder="0.00"
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label class="block text-xs font-medium text-gray-600 mb-1">Variance</label>
                      <div class="px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm text-gray-700">
                        {{ computeVariance(proc) }}
                      </div>
                    </div>
                    <div>
                      <label class="block text-xs font-medium text-gray-600 mb-1">Threshold %</label>
                      <input
                        v-model="proc.threshold"
                        type="number"
                        step="0.1"
                        placeholder="5.0"
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                      />
                    </div>
                  </div>

                  <!-- Variance Status Badge -->
                  <div class="flex items-center space-x-2">
                    <span class="text-xs font-medium text-gray-600">Status:</span>
                    <span
                      class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium"
                      :class="getVarianceStatusClass(proc)"
                    >
                      {{ getVarianceStatus(proc) }}
                    </span>
                  </div>

                  <div>
                    <label class="block text-xs font-medium text-gray-600 mb-1">Analysis Notes</label>
                    <textarea
                      v-model="proc.analysis_notes"
                      rows="2"
                      placeholder="Document analysis observations..."
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                    ></textarea>
                  </div>
                </div>

                <div v-if="form.analytical_procedures.length === 0" class="text-center py-8 text-gray-500 text-sm">
                  No analytical procedures added yet.
                </div>

                <Button variant="outline" size="sm" @click="addAnalyticalProcedure">
                  <template #prefix><PlusIcon class="h-3.5 w-3.5" /></template>
                  Add Procedure
                </Button>
              </div>
            </div>

            <!-- Section: Errors & Exceptions -->
            <div v-show="activeSection === 'errors'" class="space-y-6">
              <SectionHeader
                title="Errors & Exceptions"
                description="Track errors and exceptions found during testing"
                icon="alert-triangle"
                step="7"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6 space-y-6">
                <!-- Error Items -->
                <div v-for="(err, idx) in form.errors_found" :key="idx" class="border border-gray-200 rounded-lg p-4 space-y-4">
                  <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-2">
                      <h5 class="text-sm font-semibold text-gray-900">{{ err.error_id || `Error ${idx + 1}` }}</h5>
                      <span
                        v-if="err.severity"
                        class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium"
                        :class="{
                          'bg-red-100 text-red-800': err.severity === 'Critical',
                          'bg-orange-100 text-orange-800': err.severity === 'High',
                          'bg-amber-100 text-amber-800': err.severity === 'Medium',
                          'bg-gray-100 text-gray-800': err.severity === 'Low',
                        }"
                      >
                        {{ err.severity }}
                      </span>
                    </div>
                    <button @click="removeError(idx)" class="text-red-500 hover:text-red-700">
                      <TrashIcon class="h-4 w-4" />
                    </button>
                  </div>

                  <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label class="block text-xs font-medium text-gray-600 mb-1">Error ID *</label>
                      <input
                        v-model="err.error_id"
                        type="text"
                        placeholder="ERR-001"
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label class="block text-xs font-medium text-gray-600 mb-1">Error Type *</label>
                      <select
                        v-model="err.error_type"
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                      >
                        <option value="">Select type</option>
                        <option value="Mathematical Error">Mathematical Error</option>
                        <option value="Omission">Omission</option>
                        <option value="Duplication">Duplication</option>
                        <option value="Misclassification">Misclassification</option>
                        <option value="Timing Difference">Timing Difference</option>
                        <option value="Other">Other</option>
                      </select>
                    </div>
                    <div>
                      <label class="block text-xs font-medium text-gray-600 mb-1">Severity</label>
                      <select
                        v-model="err.severity"
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                      >
                        <option value="">Select severity</option>
                        <option value="Low">Low</option>
                        <option value="Medium">Medium</option>
                        <option value="High">High</option>
                        <option value="Critical">Critical</option>
                      </select>
                    </div>
                  </div>

                  <div>
                    <label class="block text-xs font-medium text-gray-600 mb-1">Error Description *</label>
                    <textarea
                      v-model="err.error_description"
                      rows="2"
                      placeholder="Describe the error or exception..."
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                    ></textarea>
                  </div>

                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label class="block text-xs font-medium text-gray-600 mb-1">Impact Amount</label>
                      <input
                        v-model="err.impact_amount"
                        type="number"
                        step="0.01"
                        placeholder="0.00"
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label class="block text-xs font-medium text-gray-600 mb-1">Status</label>
                      <select
                        v-model="err.status"
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                      >
                        <option value="Open">Open</option>
                        <option value="Resolved">Resolved</option>
                        <option value="Accepted">Accepted</option>
                      </select>
                    </div>
                  </div>

                  <div>
                    <label class="block text-xs font-medium text-gray-600 mb-1">Root Cause</label>
                    <textarea
                      v-model="err.root_cause"
                      rows="2"
                      placeholder="Identify the root cause..."
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                    ></textarea>
                  </div>

                  <div>
                    <label class="block text-xs font-medium text-gray-600 mb-1">Corrective Action</label>
                    <textarea
                      v-model="err.corrective_action"
                      rows="2"
                      placeholder="Describe corrective action taken or recommended..."
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                    ></textarea>
                  </div>
                </div>

                <div v-if="form.errors_found.length === 0" class="text-center py-8 text-gray-500 text-sm">
                  No errors or exceptions recorded. Click "Add Error" to document findings.
                </div>

                <Button variant="outline" size="sm" @click="addError">
                  <template #prefix><PlusIcon class="h-3.5 w-3.5" /></template>
                  Add Error
                </Button>
              </div>
            </div>

            <!-- Section: Cross References -->
            <div v-show="activeSection === 'references'" class="space-y-6">
              <SectionHeader
                title="Cross References"
                description="Link related documents and working papers"
                icon="link"
                step="8"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6 space-y-6">
                <div class="border border-gray-200 rounded-lg overflow-hidden">
                  <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                      <tr>
                        <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                        <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reference ID</th>
                        <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Title</th>
                        <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Page #</th>
                        <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Notes</th>
                        <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
                      </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-200">
                      <tr v-for="(xref, idx) in form.cross_references" :key="idx" class="hover:bg-gray-50">
                        <td class="px-4 py-3">
                          <select
                            v-model="xref.reference_type"
                            class="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                          >
                            <option value="">Select</option>
                            <option value="Working Paper">Working Paper</option>
                            <option value="Audit Program">Audit Program</option>
                            <option value="Risk Assessment">Risk Assessment</option>
                            <option value="Audit Report">Audit Report</option>
                            <option value="Other Document">Other Document</option>
                          </select>
                        </td>
                        <td class="px-4 py-3">
                          <input
                            v-model="xref.reference_id"
                            type="text"
                            placeholder="REF-001"
                            class="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                          />
                        </td>
                        <td class="px-4 py-3">
                          <input
                            v-model="xref.reference_title"
                            type="text"
                            placeholder="Document title..."
                            class="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                          />
                        </td>
                        <td class="px-4 py-3">
                          <input
                            v-model="xref.page_number"
                            type="text"
                            placeholder="p.12"
                            class="w-20 px-2 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                          />
                        </td>
                        <td class="px-4 py-3">
                          <input
                            v-model="xref.notes"
                            type="text"
                            placeholder="Notes..."
                            class="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                          />
                        </td>
                        <td class="px-4 py-3 text-right">
                          <button @click="removeCrossReference(idx)" class="text-red-500 hover:text-red-700 text-sm">
                            <TrashIcon class="h-4 w-4" />
                          </button>
                        </td>
                      </tr>
                      <tr v-if="form.cross_references.length === 0">
                        <td colspan="6" class="px-4 py-8 text-center text-gray-500 text-sm">
                          No cross references added yet.
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                <Button variant="outline" size="sm" @click="addCrossReference">
                  <template #prefix><PlusIcon class="h-3.5 w-3.5" /></template>
                  Add Reference
                </Button>
              </div>
            </div>

            <!-- Section: Revision History -->
            <div v-show="activeSection === 'revisions'" class="space-y-6">
              <SectionHeader
                title="Revision History"
                description="Track changes and version history"
                icon="history"
                step="9"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6 space-y-6">
                <div v-for="(rev, idx) in form.revision_history" :key="idx" class="border border-gray-200 rounded-lg p-4 space-y-4">
                  <div class="flex items-center justify-between">
                    <h5 class="text-sm font-semibold text-gray-900">Version {{ rev.version_number || idx + 1 }}</h5>
                    <button @click="removeRevision(idx)" class="text-red-500 hover:text-red-700">
                      <TrashIcon class="h-4 w-4" />
                    </button>
                  </div>

                  <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label class="block text-xs font-medium text-gray-600 mb-1">Version Number *</label>
                      <input
                        v-model="rev.version_number"
                        type="number"
                        step="0.1"
                        placeholder="1.0"
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label class="block text-xs font-medium text-gray-600 mb-1">Revision Date *</label>
                      <input
                        v-model="rev.revision_date"
                        type="date"
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label class="block text-xs font-medium text-gray-600 mb-1">Reason</label>
                      <select
                        v-model="rev.revision_reason"
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                      >
                        <option value="">Select reason</option>
                        <option value="Content Update">Content Update</option>
                        <option value="Review Feedback">Review Feedback</option>
                        <option value="Error Correction">Error Correction</option>
                        <option value="Additional Information">Additional Information</option>
                        <option value="Other">Other</option>
                      </select>
                    </div>
                  </div>

                  <div>
                    <label class="block text-xs font-medium text-gray-600 mb-1">Revised By *</label>
                    <input
                      v-model="rev.revised_by"
                      type="text"
                      placeholder="User email"
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                    />
                  </div>

                  <div>
                    <label class="block text-xs font-medium text-gray-600 mb-1">Changes Made *</label>
                    <textarea
                      v-model="rev.changes_made"
                      rows="2"
                      placeholder="Describe changes made in this revision..."
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                    ></textarea>
                  </div>
                </div>

                <div v-if="form.revision_history.length === 0" class="text-center py-8 text-gray-500 text-sm">
                  No revision history recorded.
                </div>

                <Button variant="outline" size="sm" @click="addRevision">
                  <template #prefix><PlusIcon class="h-3.5 w-3.5" /></template>
                  Add Revision
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <template #actions>
      <div class="flex items-center justify-between w-full">
        <!-- Left: Status and Navigation -->
        <div class="flex items-center space-x-4">
          <div class="flex items-center space-x-2">
            <div
              class="w-3 h-3 rounded-full"
              :class="isFormValid ? 'bg-green-500' : 'bg-amber-500'"
            ></div>
            <span class="text-sm font-medium" :class="isFormValid ? 'text-green-700' : 'text-amber-700'">
              {{ isFormValid ? 'Ready to save' : 'Complete required fields' }}
            </span>
          </div>

          <!-- Section Navigation -->
          <div class="flex items-center space-x-2">
            <Button
              variant="ghost"
              size="sm"
              :disabled="currentSectionIndex === 0"
              @click="goToPreviousSection"
            >
              <ChevronLeftIcon class="h-4 w-4 mr-1" />
              Previous
            </Button>
            <Button
              variant="ghost"
              size="sm"
              :disabled="currentSectionIndex === formSections.length - 1"
              @click="goToNextSection"
            >
              Next
              <ChevronRightIcon class="h-4 w-4 ml-1" />
            </Button>
          </div>
        </div>

        <!-- Right: Action Buttons -->
        <div class="flex items-center space-x-3">
          <Button variant="outline" @click="handleCancel" :disabled="isSaving">
            Cancel
          </Button>
          <Button
            v-if="!isEditMode"
            variant="outline"
            theme="gray"
            @click="saveAsDraft"
            :loading="isSavingDraft"
            :disabled="isSaving"
          >
            Save as Draft
          </Button>
          <Button
            variant="solid"
            theme="gray"
            @click="handleSubmit"
            :loading="isSaving"
          >
            <template #prefix>
              <PlusIcon v-if="!isEditMode" class="h-4 w-4" />
              <CheckIcon v-else class="h-4 w-4" />
            </template>
            {{ isEditMode ? 'Update Working Paper' : 'Create Working Paper' }}
          </Button>
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { Button, Dialog } from 'frappe-ui'
import {
  AlertTriangleIcon,
  BarChartIcon,
  CheckIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  ClipboardListIcon,
  FileTextIcon,
  HistoryIcon,
  LinkIcon,
  ListChecksIcon,
  PlusIcon,
  TrashIcon,
  UsersIcon,
  CheckCircleIcon,
} from 'lucide-vue-next'

// Import custom components
import FileUploader from '@/components/Common/FileUploader.vue'
import LinkField from '@/components/Common/fields/LinkField.vue'
import SectionHeader from '@/components/workingpaper/SectionHeader.vue'

// Props
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  workingPaper: {
    type: Object,
    default: null
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'created', 'updated', 'cancelled'])

// Dialog visibility
const isOpen = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

// Edit mode detection
const isEditMode = computed(() => !!props.workingPaper?.name)

// Form Sections
const formSections = [
  { id: 'basic', label: 'Basic Information', description: 'Core details', icon: 'file-text' },
  { id: 'content', label: 'Content & Work', description: 'Documentation', icon: 'clipboard-list' },
  { id: 'assignment', label: 'Assignment', description: 'Team & timeline', icon: 'users' },
  { id: 'quality', label: 'Quality Control', description: 'Review & docs', icon: 'check-circle' },
  { id: 'samples', label: 'Sample Selection', description: 'Test samples', icon: 'list-checks' },
  { id: 'analytical', label: 'Analytical Procedures', description: 'Variance analysis', icon: 'bar-chart' },
  { id: 'errors', label: 'Errors & Exceptions', description: 'Issues found', icon: 'alert-triangle' },
  { id: 'references', label: 'Cross References', description: 'Related docs', icon: 'link' },
  { id: 'revisions', label: 'Revision History', description: 'Version tracking', icon: 'history' },
]

const activeSection = ref('basic')

// Form State
const form = reactive({
  // Basic Information
  working_paper_id: '',
  wp_title: '',
  wp_reference_no: '',
  wp_type: '',
  engagement_reference: '',
  procedure_reference: '',

  // Content & Work Performed
  work_performed: '',
  objective: '',
  scope: '',

  // Assignment & Timeline
  prepared_by: '',
  reviewed_by: '',
  preparation_date: '',
  review_date: '',
  due_date: '',
  review_status: 'Not Reviewed',

  // Quality & Documentation
  quality_score: '',
  review_comments: '',
  supporting_documents: '',
  attachments: [],
  notes: '',

  // Child Tables
  sample_selection: [],
  analytical_procedures: [],
  errors_found: [],
  cross_references: [],
  revision_history: [],
})

const errors = reactive({})
const isSaving = ref(false)
const isSavingDraft = ref(false)

// Options
const reviewStatusOptions = [
  { label: 'Not Reviewed', value: 'Not Reviewed' },
  { label: 'Under Review', value: 'Under Review' },
  { label: 'Review Complete', value: 'Review Complete' },
  { label: 'Revision Required', value: 'Revision Required' },
]

const wpTypeOptions = [
  { label: 'Planning Memo', value: 'Planning Memo' },
  { label: 'Risk Assessment', value: 'Risk Assessment' },
  { label: 'Walkthrough', value: 'Walkthrough' },
  { label: 'Test of Controls', value: 'Test of Controls' },
  { label: 'Substantive Test', value: 'Substantive Test' },
  { label: 'Analytical Review', value: 'Analytical Review' },
  { label: 'Data Analytics', value: 'Data Analytics' },
  { label: 'Summary', value: 'Summary' },
  { label: 'Other', value: 'Other' },
]

// Computed Properties
const currentSectionIndex = computed(() =>
  formSections.findIndex(s => s.id === activeSection.value)
)

const getSectionStatus = (sectionId) => {
  switch (sectionId) {
    case 'basic':
      return (form.wp_title && form.wp_type && form.engagement_reference) ? 'complete' :
             (form.wp_title || form.wp_type) ? 'partial' : 'incomplete'
    case 'content':
      return form.work_performed ? 'complete' : 'incomplete'
    case 'assignment':
      return (form.prepared_by && form.preparation_date) ? 'complete' :
             (form.prepared_by || form.preparation_date) ? 'partial' : 'incomplete'
    case 'quality':
      return 'complete' // Optional section
    case 'samples':
      return form.sample_selection.length > 0 ? 'complete' : 'complete' // Optional
    case 'analytical':
      return form.analytical_procedures.length > 0 ? 'complete' : 'complete' // Optional
    case 'errors':
      return form.errors_found.length > 0 ? 'complete' : 'complete' // Optional
    case 'references':
      return form.cross_references.length > 0 ? 'complete' : 'complete' // Optional
    case 'revisions':
      return form.revision_history.length > 0 ? 'complete' : 'complete' // Optional
    default:
      return 'incomplete'
  }
}

const getSectionStatusClass = (sectionId) => {
  const status = getSectionStatus(sectionId)
  if (status === 'complete') return 'bg-gray-900 text-white'
  if (status === 'partial') return 'bg-amber-500 text-white'
  return 'bg-gray-300 text-gray-600'
}

const completedSections = computed(() =>
  formSections.filter(s => getSectionStatus(s.id) === 'complete').length
)

const formProgress = computed(() =>
  Math.round((completedSections.value / formSections.length) * 100)
)

const isFormValid = computed(() => {
  return !!(
    form.wp_title &&
    form.wp_type &&
    form.engagement_reference &&
    form.work_performed &&
    form.prepared_by &&
    form.preparation_date
  )
})

// Methods
const goToPreviousSection = () => {
  const idx = currentSectionIndex.value
  if (idx > 0) {
    activeSection.value = formSections[idx - 1].id
  }
}

const goToNextSection = () => {
  const idx = currentSectionIndex.value
  if (idx < formSections.length - 1) {
    activeSection.value = formSections[idx + 1].id
  }
}

const validateForm = () => {
  const errs = {}

  // Required fields validation
  if (!form.wp_title) errs.wp_title = 'Working paper title is required'
  if (!form.wp_type) errs.wp_type = 'Type is required'
  if (!form.engagement_reference) errs.engagement_reference = 'Engagement reference is required'
  if (!form.work_performed) errs.work_performed = 'Work performed is required'
  if (!form.prepared_by) errs.prepared_by = 'Prepared by is required'
  if (!form.preparation_date) errs.preparation_date = 'Preparation date is required'

  Object.assign(errors, errs)
  return Object.keys(errs).length === 0
}

const prepareFormData = () => {
  return {
    ...form,
    // Ensure arrays are properly formatted
    attachments: Array.isArray(form.attachments) ? form.attachments : [],
  }
}

const handleSubmit = async () => {
  if (!validateForm()) {
    // Navigate to the first section with errors
    const firstErrorSection = formSections.find(s => {
      const status = getSectionStatus(s.id)
      return status !== 'complete'
    })
    if (firstErrorSection) {
      activeSection.value = firstErrorSection.id
    }
    return
  }

  try {
    isSaving.value = true
    const formData = prepareFormData()

    if (isEditMode.value) {
      emit('updated', { ...formData, name: props.workingPaper.name })
    } else {
      emit('created', formData)
    }

    isOpen.value = false
  } catch (error) {
    console.error('Error saving working paper:', error)
  } finally {
    isSaving.value = false
  }
}

const saveAsDraft = async () => {
  try {
    isSavingDraft.value = true
    const formData = prepareFormData()
    emit('created', { ...formData, review_status: 'Not Reviewed' })
    isOpen.value = false
  } catch (error) {
    console.error('Error saving draft:', error)
  } finally {
    isSavingDraft.value = false
  }
}

const handleCancel = () => {
  emit('cancelled')
  isOpen.value = false
}

// --- Sample Selection ---
const samplePassCount = computed(() => form.sample_selection.filter(s => s.test_result === 'Pass').length)
const sampleFailCount = computed(() => form.sample_selection.filter(s => s.test_result === 'Fail').length)
const sampleExceptionCount = computed(() => form.sample_selection.filter(s => s.exception_found).length)

const addSampleItem = () => {
  form.sample_selection.push({
    item_id: '',
    item_description: '',
    sample_amount: null,
    test_result: '',
    exception_found: false,
    exception_details: '',
  })
}

const removeSampleItem = (idx) => {
  form.sample_selection.splice(idx, 1)
}

// --- Analytical Procedures ---
const computeVariance = (proc) => {
  if (proc.expected_result != null && proc.actual_result != null && proc.expected_result !== '') {
    const variance = Number(proc.actual_result) - Number(proc.expected_result)
    return variance.toFixed(2)
  }
  return '—'
}

const getVarianceStatus = (proc) => {
  if (proc.expected_result == null || proc.actual_result == null || proc.expected_result === '' || proc.actual_result === '') return 'N/A'
  const expected = Number(proc.expected_result)
  const actual = Number(proc.actual_result)
  if (expected === 0) return actual === 0 ? 'Within Threshold' : 'Above Threshold'
  const variancePct = Math.abs(((actual - expected) / expected) * 100)
  const threshold = Number(proc.threshold) || 5
  if (variancePct <= threshold) return 'Within Threshold'
  return actual > expected ? 'Above Threshold' : 'Below Threshold'
}

const getVarianceStatusClass = (proc) => {
  const status = getVarianceStatus(proc)
  if (status === 'Within Threshold') return 'bg-green-100 text-green-800'
  if (status === 'Above Threshold' || status === 'Below Threshold') return 'bg-red-100 text-red-800'
  return 'bg-gray-100 text-gray-600'
}

const addAnalyticalProcedure = () => {
  form.analytical_procedures.push({
    procedure_name: '',
    procedure_type: '',
    expected_result: null,
    actual_result: null,
    variance: null,
    variance_percentage: null,
    threshold: 5,
    result_status: '',
    analysis_notes: '',
  })
}

const removeAnalyticalProcedure = (idx) => {
  form.analytical_procedures.splice(idx, 1)
}

// --- Errors & Exceptions ---
const addError = () => {
  form.errors_found.push({
    error_id: '',
    error_type: '',
    error_description: '',
    severity: '',
    impact_amount: null,
    root_cause: '',
    corrective_action: '',
    status: 'Open',
  })
}

const removeError = (idx) => {
  form.errors_found.splice(idx, 1)
}

// --- Cross References ---
const addCrossReference = () => {
  form.cross_references.push({
    reference_type: '',
    reference_id: '',
    reference_title: '',
    page_number: '',
    notes: '',
  })
}

const removeCrossReference = (idx) => {
  form.cross_references.splice(idx, 1)
}

// --- Revision History ---
const addRevision = () => {
  form.revision_history.push({
    version_number: form.revision_history.length > 0
      ? Number(form.revision_history[form.revision_history.length - 1].version_number || 0) + 1
      : 1.0,
    revision_date: new Date().toISOString().split('T')[0],
    revised_by: '',
    revision_reason: '',
    changes_made: '',
  })
}

const removeRevision = (idx) => {
  form.revision_history.splice(idx, 1)
}

const resetForm = () => {
  Object.keys(form).forEach(key => {
    if (Array.isArray(form[key])) {
      form[key] = []
    } else if (typeof form[key] === 'number') {
      form[key] = null
    } else {
      form[key] = ''
    }
  })
  form.review_status = 'Not Reviewed'
  Object.keys(errors).forEach(key => delete errors[key])
  activeSection.value = 'basic'
}

const loadWorkingPaperData = (workingPaper) => {
  if (!workingPaper) return

  Object.keys(form).forEach(key => {
    if (workingPaper[key] !== undefined) {
      form[key] = workingPaper[key]
    }
  })
}

// Watchers
watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    if (props.workingPaper) {
      loadWorkingPaperData(props.workingPaper)
    } else {
      resetForm()
    }
  }
})

watch(() => props.workingPaper, (newVal) => {
  if (newVal && props.modelValue) {
    loadWorkingPaperData(newVal)
  }
}, { deep: true })
</script>