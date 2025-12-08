<template>
  <Dialog
    v-model="showDialog"
    :options="{
      size: 'full',
      title: isEditing ? 'Edit Audit Finding' : 'Create Audit Finding',
    }"
  >
    <template #body>
      <div class="h-[80vh] flex">
        <!-- Progress Sidebar -->
        <div class="w-64 bg-gray-50 border-r border-gray-200 flex-shrink-0 overflow-y-auto">
          <div class="p-4">
            <h4 class="text-sm font-semibold text-gray-900 mb-3">Progress</h4>
            <div class="space-y-2">
              <div
                v-for="(section, index) in sectionsList"
                :key="section.key"
                class="flex items-center space-x-2 p-2 rounded-lg cursor-pointer transition-all"
                :class="activeSection === section.key ? 'bg-blue-100 border border-blue-300' : 'hover:bg-gray-100'"
                @click="setActiveSection(section.key)"
              >
                <div
                  class="w-6 h-6 rounded-full flex items-center justify-center text-xs font-semibold"
                  :class="getSectionStatusClass(section.key)"
                >
                  <CheckIcon v-if="isSectionComplete(section.key)" class="h-3 w-3" />
                  <span v-else>{{ index + 1 }}</span>
                </div>
                <div class="flex-1 min-w-0">
                  <div class="text-sm font-medium text-gray-900 truncate">{{ section.label }}</div>
                  <div class="text-xs text-gray-500 truncate">{{ section.description }}</div>
                </div>
              </div>
            </div>

            <!-- Overall Progress -->
            <div class="mt-4 p-3 bg-white rounded-lg border border-gray-200">
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs font-medium text-gray-700">Overall Progress</span>
                <span class="text-xs font-semibold text-blue-600">{{ overallProgress }}%</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-1.5">
                <div
                  class="bg-blue-600 h-1.5 rounded-full transition-all duration-500"
                  :style="{ width: `${overallProgress}%` }"
                ></div>
              </div>
            </div>

            <!-- Auto-save Status -->
            <div v-if="lastSaved" class="mt-3 text-xs text-gray-500 text-center">
              Last saved: {{ formatTimeAgo(lastSaved) }}
            </div>
          </div>
        </div>

        <!-- Main Form Content -->
        <div class="flex-1 overflow-y-auto">
          <div class="p-6 space-y-8">
            <!-- Section 0: Template Selection -->
            <div v-show="activeSection === 'template'" class="space-y-6">
              <SectionHeader
                title="Template Selection"
                description="Choose a finding template to speed up the process (optional)"
                :sectionNumber="0"
                color="emerald"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                <FindingTemplateSelector
                  @template-selected="applyTemplate"
                  @create-custom="setActiveSection('basic')"
                />
              </div>
            </div>

            <!-- Section 1: Basic Information -->
            <div v-show="activeSection === 'basic'" class="space-y-6">
              <SectionHeader
                title="Basic Information"
                description="Essential finding identification and classification details"
                :sectionNumber="1"
                color="blue"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Finding ID <span class="text-red-500">*</span>
                    </label>
                    <div class="flex gap-2">
                      <FormControl
                        v-model="formData.finding_id"
                        placeholder="e.g., FND-2024-001"
                        class="flex-1"
                      />
                      <Button variant="outline" size="sm" @click="generateFindingId">
                        <RefreshCwIcon class="h-4 w-4" />
                      </Button>
                    </div>
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Engagement Reference <span class="text-red-500">*</span>
                    </label>
                    <LinkField
                      v-model="formData.engagement_reference"
                      doctype="Audit Engagement"
                      placeholder="Select related engagement"
                    />
                  </div>

                  <FormControl
                    v-model="formData.finding_title"
                    label="Finding Title"
                    placeholder="Enter a descriptive finding title"
                    :required="true"
                  />
                </div>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Finding Category <span class="text-red-500">*</span>
                    </label>
                    <FormControl
                      type="select"
                      v-model="formData.finding_category"
                      :options="categoryOptions"
                      placeholder="Select category"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Risk Rating</label>
                    <FormControl
                      type="select"
                      v-model="formData.risk_rating"
                      :options="riskRatingOptions"
                      placeholder="Select risk rating"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Business Impact</label>
                    <FormControl
                      type="select"
                      v-model="formData.business_impact_rating"
                      :options="impactOptions"
                      placeholder="Select impact"
                    />
                  </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
                  <FormControl
                    v-model="formData.date_identified"
                    type="date"
                    label="Date Identified"
                  />
                  <FormControl
                    v-model="formData.source_document"
                    label="Source Document"
                    placeholder="Reference to source workpaper"
                  />
                </div>
              </div>

              <!-- Affected Locations -->
              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                <InlineChildTable
                  v-model="formData.affected_locations"
                  title="Affected Locations"
                  modal-title="Location"
                  :columns="affectedLocationsColumns"
                  :auto-add-row="false"
                />
              </div>
            </div>

            <!-- Section 2: Finding Details -->
            <div v-show="activeSection === 'details'" class="space-y-6">
              <SectionHeader
                title="Finding Details"
                description="Document the condition, criteria, cause, and effect of the finding"
                :sectionNumber="2"
                color="purple"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                <div class="space-y-6">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Condition <span class="text-red-500">*</span>
                    </label>
                    <p class="text-xs text-gray-500 mb-2">What is the actual situation or state observed?</p>
                    <TextEditor
                      :content="formData.condition"
                      @change="formData.condition = $event"
                      placeholder="Describe the current condition or situation found during the audit..."
                      :editable="true"
                      editorClass="min-h-[120px] prose-sm"
                    />
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Criteria <span class="text-red-500">*</span>
                    </label>
                    <p class="text-xs text-gray-500 mb-2">What should be the expected state or standard?</p>
                    <TextEditor
                      :content="formData.criteria"
                      @change="formData.criteria = $event"
                      placeholder="Describe the standard, policy, or expectation that should be met..."
                      :editable="true"
                      editorClass="min-h-[120px] prose-sm"
                    />
                  </div>

                  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">Cause</label>
                      <p class="text-xs text-gray-500 mb-2">Why did the condition occur?</p>
                      <TextEditor
                        :content="formData.cause"
                        @change="formData.cause = $event"
                        placeholder="Describe the root cause..."
                        :editable="true"
                        editorClass="min-h-[100px] prose-sm"
                      />
                    </div>

                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">Effect</label>
                      <p class="text-xs text-gray-500 mb-2">What is the impact or consequence?</p>
                      <TextEditor
                        :content="formData.effect"
                        @change="formData.effect = $event"
                        placeholder="Describe the actual or potential impact..."
                        :editable="true"
                        editorClass="min-h-[100px] prose-sm"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Section 3: Evidence & Recommendation -->
            <div v-show="activeSection === 'evidence'" class="space-y-6">
              <SectionHeader
                title="Evidence & Recommendation"
                description="Supporting evidence and proposed corrective actions"
                :sectionNumber="3"
                color="green"
              />

              <!-- Evidence Table -->
              <InlineChildTable
                v-model="formData.evidence"
                title="Supporting Evidence"
                modalTitle="Evidence"
                :columns="inlineEvidenceColumns"
                :autoAddRow="false"
              />

              <!-- Sampling & Recommendation -->
              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                <h4 class="text-sm font-medium text-gray-900 mb-4">Sampling & Recommendation</h4>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                  <FormControl
                    v-model="formData.sample_size"
                    type="number"
                    label="Sample Size Tested"
                    placeholder="Number of items tested"
                  />
                  <FormControl
                    v-model="formData.exceptions_found"
                    type="number"
                    label="Exceptions Found"
                    placeholder="Number of exceptions identified"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    Recommendation <span class="text-red-500">*</span>
                  </label>
                  <TextEditor
                    :content="formData.recommendation"
                    @change="formData.recommendation = $event"
                    placeholder="Provide specific, actionable recommendations to address the finding..."
                    :editable="true"
                    editorClass="min-h-[150px] prose-sm"
                  />
                </div>
              </div>
            </div>

            <!-- Section 4: Management Response -->
            <div v-show="activeSection === 'response'" class="space-y-6">
              <SectionHeader
                title="Management Response"
                description="Management's agreement and response to the finding"
                :sectionNumber="4"
                color="amber"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Management Agrees</label>
                    <div class="flex items-center gap-6 mt-2">
                      <label class="inline-flex items-center cursor-pointer">
                        <input
                          type="radio"
                          v-model="formData.management_agrees"
                          :value="1"
                          class="form-radio h-4 w-4 text-blue-600"
                        />
                        <span class="ml-2 text-sm text-gray-700">Yes</span>
                      </label>
                      <label class="inline-flex items-center cursor-pointer">
                        <input
                          type="radio"
                          v-model="formData.management_agrees"
                          :value="0"
                          class="form-radio h-4 w-4 text-blue-600"
                        />
                        <span class="ml-2 text-sm text-gray-700">No</span>
                      </label>
                    </div>
                  </div>
                  <FormControl
                    v-model="formData.response_date"
                    type="date"
                    label="Response Date"
                  />
                </div>

                <div class="mt-6">
                  <label class="block text-sm font-medium text-gray-700 mb-1">Management Comments</label>
                  <TextEditor
                    :content="formData.management_comments"
                    @change="formData.management_comments = $event"
                    placeholder="Enter management's response and comments..."
                    :editable="true"
                    editorClass="min-h-[120px] prose-sm"
                  />
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Responding Manager</label>
                    <LinkField
                      v-model="formData.management_response_by"
                      doctype="User"
                      placeholder="Select responding manager"
                    />
                  </div>
                  <FormControl
                    v-model="formData.management_response_date"
                    type="date"
                    label="Response Received On"
                  />
                </div>
              </div>
            </div>

            <!-- Section 5: Corrective Action Plan -->
            <div v-show="activeSection === 'action'" class="space-y-6">
              <SectionHeader
                title="Corrective Action Plan"
                description="Planned actions to address and resolve the finding"
                :sectionNumber="5"
                color="indigo"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Action Plan Description</label>
                  <TextEditor
                    :content="formData.action_plan_description"
                    @change="formData.action_plan_description = $event"
                    placeholder="Describe the corrective action plan in detail..."
                    :editable="true"
                    editorClass="min-h-[120px] prose-sm"
                  />
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Responsible Person</label>
                    <LinkField
                      v-model="formData.responsible_person"
                      doctype="User"
                      placeholder="Select person responsible"
                    />
                  </div>
                  <FormControl
                    v-model="formData.target_date"
                    type="date"
                    label="Target Completion Date"
                  />
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
                  <FormControl
                    v-model="formData.revised_target_date"
                    type="date"
                    label="Revised Target Date"
                  />
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Priority</label>
                    <FormControl
                      type="select"
                      v-model="formData.priority"
                      :options="priorityOptions"
                      placeholder="Select priority"
                    />
                  </div>
                </div>
              </div>

              <!-- Action Milestones -->
              <InlineChildTable
                v-model="formData.milestones"
                title="Action Milestones"
                modalTitle="Milestone"
                :columns="inlineMilestoneColumns"
                :autoAddRow="false"
              />
            </div>

            <!-- Section 6: Follow-up & Status -->
            <div v-show="activeSection === 'followup'" class="space-y-6">
              <SectionHeader
                title="Follow-up & Status"
                description="Track finding status and follow-up activities"
                :sectionNumber="6"
                color="cyan"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                <h4 class="text-sm font-medium text-gray-900 mb-4">Current Status</h4>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Finding Status <span class="text-red-500">*</span>
                    </label>
                    <FormControl
                      type="select"
                      v-model="formData.finding_status"
                      :options="statusOptions"
                    />
                  </div>
                  <FormControl
                    v-model="formData.status_date"
                    type="date"
                    label="Status Date"
                  />
                </div>
              </div>

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                <h4 class="text-sm font-medium text-gray-900 mb-4">Follow-up Settings</h4>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Follow-up Required</label>
                    <div class="flex items-center gap-6 mt-2">
                      <label class="inline-flex items-center cursor-pointer">
                        <input
                          type="radio"
                          v-model="formData.follow_up_required"
                          :value="1"
                          class="form-radio h-4 w-4 text-blue-600"
                        />
                        <span class="ml-2 text-sm text-gray-700">Yes</span>
                      </label>
                      <label class="inline-flex items-center cursor-pointer">
                        <input
                          type="radio"
                          v-model="formData.follow_up_required"
                          :value="0"
                          class="form-radio h-4 w-4 text-blue-600"
                        />
                        <span class="ml-2 text-sm text-gray-700">No</span>
                      </label>
                    </div>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Follow-up Frequency</label>
                    <FormControl
                      type="select"
                      v-model="formData.follow_up_frequency"
                      :options="frequencyOptions"
                      :disabled="!formData.follow_up_required"
                      placeholder="Select frequency"
                    />
                  </div>
                  <FormControl
                    v-model="formData.next_follow_up_date"
                    type="date"
                    label="Next Follow-up Date"
                    :disabled="!formData.follow_up_required"
                  />
                </div>
              </div>

              <!-- Follow-up History -->
              <InlineChildTable
                v-model="formData.follow_up_history"
                title="Follow-up History"
                modalTitle="Follow-up Activity"
                :columns="inlineFollowUpHistoryColumns"
                :autoAddRow="false"
              />
            </div>

            <!-- Section 7: Verification -->
            <div v-show="activeSection === 'verification'" class="space-y-6">
              <SectionHeader
                title="Verification"
                description="Verification of corrective action implementation"
                :sectionNumber="7"
                color="teal"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <FormControl
                    v-model="formData.verification_date"
                    type="date"
                    label="Verification Date"
                  />
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Verified By</label>
                    <LinkField
                      v-model="formData.verified_by"
                      doctype="User"
                      placeholder="Select verifier"
                    />
                  </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Verification Method</label>
                    <FormControl
                      type="select"
                      v-model="formData.verification_method"
                      :options="verificationMethodOptions"
                      placeholder="Select method"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Verification Status</label>
                    <FormControl
                      type="select"
                      v-model="formData.verification_status"
                      :options="verificationStatusOptions"
                      placeholder="Select status"
                    />
                  </div>
                </div>

                <div class="mt-6">
                  <label class="block text-sm font-medium text-gray-700 mb-1">Verification Results</label>
                  <TextEditor
                    :content="formData.verification_results"
                    @change="formData.verification_results = $event"
                    placeholder="Document the results of the verification testing..."
                    :editable="true"
                    editorClass="min-h-[150px] prose-sm"
                  />
                </div>
              </div>
            </div>

            <!-- Section 8: Closure & Reporting -->
            <div v-show="activeSection === 'closure'" class="space-y-6">
              <SectionHeader
                title="Closure & Reporting"
                description="Finding closure details and reporting preferences"
                :sectionNumber="8"
                color="rose"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                <h4 class="text-sm font-medium text-gray-900 mb-4">Closure Information</h4>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <FormControl
                    v-model="formData.closure_date"
                    type="date"
                    label="Closure Date"
                  />
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Closed By</label>
                    <LinkField
                      v-model="formData.closed_by"
                      doctype="User"
                      placeholder="Select person closing the finding"
                    />
                  </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Closure Reason</label>
                    <FormControl
                      type="select"
                      v-model="formData.closure_reason"
                      :options="closureReasonOptions"
                      placeholder="Select reason"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Final Disposition</label>
                    <FormControl
                      type="select"
                      v-model="formData.final_disposition"
                      :options="dispositionOptions"
                      placeholder="Select disposition"
                    />
                  </div>
                </div>

                <div class="mt-6">
                  <label class="block text-sm font-medium text-gray-700 mb-1">Closure Notes</label>
                  <TextEditor
                    :content="formData.closure_notes"
                    @change="formData.closure_notes = $event"
                    placeholder="Document any final notes regarding the closure..."
                    :editable="true"
                    editorClass="min-h-[100px] prose-sm"
                  />
                </div>
              </div>

              <!-- Reporting Options -->
              <div class="bg-blue-50 rounded-xl border border-blue-200 p-6">
                <h4 class="text-sm font-medium text-gray-900 mb-4">Reporting Options</h4>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <label class="inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      v-model="formData.include_in_report"
                      class="form-checkbox h-4 w-4 text-blue-600 rounded"
                    />
                    <span class="ml-2 text-sm text-gray-700">Include in Final Report</span>
                  </label>
                  <label class="inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      v-model="formData.reported_to_management"
                      class="form-checkbox h-4 w-4 text-blue-600 rounded"
                    />
                    <span class="ml-2 text-sm text-gray-700">Reported to Management</span>
                  </label>
                  <label class="inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      v-model="formData.reported_to_audit_committee"
                      class="form-checkbox h-4 w-4 text-blue-600 rounded"
                    />
                    <span class="ml-2 text-sm text-gray-700">Reported to Audit Committee</span>
                  </label>
                  <label class="inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      v-model="formData.reported_to_board"
                      class="form-checkbox h-4 w-4 text-blue-600 rounded"
                    />
                    <span class="ml-2 text-sm text-gray-700">Reported to Board</span>
                  </label>
                </div>

                <div class="mt-4">
                  <FormControl
                    v-model="formData.report_reference"
                    label="Report Reference"
                    placeholder="Reference to the report containing this finding"
                  />
                </div>
              </div>

              <!-- Repeat Finding Information -->
              <div class="bg-yellow-50 rounded-xl border border-yellow-200 p-6">
                <h4 class="text-sm font-medium text-gray-900 mb-4">Repeat Finding Information</h4>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Repeat Finding</label>
                    <div class="flex items-center gap-6 mt-2">
                      <label class="inline-flex items-center cursor-pointer">
                        <input
                          type="radio"
                          v-model="formData.repeat_finding"
                          :value="1"
                          class="form-radio h-4 w-4 text-yellow-600"
                        />
                        <span class="ml-2 text-sm text-gray-700">Yes</span>
                      </label>
                      <label class="inline-flex items-center cursor-pointer">
                        <input
                          type="radio"
                          v-model="formData.repeat_finding"
                          :value="0"
                          class="form-radio h-4 w-4 text-yellow-600"
                        />
                        <span class="ml-2 text-sm text-gray-700">No</span>
                      </label>
                    </div>
                  </div>
                  <div v-if="formData.repeat_finding">
                    <label class="block text-sm font-medium text-gray-700 mb-1">Previous Finding Reference</label>
                    <LinkField
                      v-model="formData.previous_finding_reference"
                      doctype="Audit Finding"
                      placeholder="Link to previous finding"
                    />
                  </div>
                </div>
              </div>

              <!-- Related Findings -->
              <InlineChildTable
                v-model="formData.related_findings"
                title="Related Findings"
                modalTitle="Related Finding"
                :columns="inlineRelatedFindingsColumns"
                :autoAddRow="false"
              />
            </div>

            <!-- Section 9: Review & Submit -->
            <div v-show="activeSection === 'review'" class="space-y-6">
              <SectionHeader
                title="Review & Submit"
                description="Review your finding and submit"
                :sectionNumber="9"
                color="blue"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                <h4 class="text-lg font-semibold text-gray-900 mb-4">Finding Summary</h4>
                
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
                  <div class="bg-gray-50 rounded-lg p-4">
                    <p class="text-xs text-gray-500 uppercase tracking-wide">Finding ID</p>
                    <p class="text-lg font-semibold text-gray-900 mt-1">{{ formData.finding_id || 'Not set' }}</p>
                  </div>
                  <div class="bg-gray-50 rounded-lg p-4">
                    <p class="text-xs text-gray-500 uppercase tracking-wide">Risk Rating</p>
                    <Badge
                      v-if="formData.risk_rating"
                      :variant="getRiskBadgeVariant(formData.risk_rating)"
                      class="mt-1"
                    >
                      {{ formData.risk_rating }}
                    </Badge>
                    <p v-else class="text-lg font-semibold text-gray-400 mt-1">Not set</p>
                  </div>
                  <div class="bg-gray-50 rounded-lg p-4">
                    <p class="text-xs text-gray-500 uppercase tracking-wide">Category</p>
                    <p class="text-lg font-semibold text-gray-900 mt-1">{{ formData.finding_category || 'Not set' }}</p>
                  </div>
                  <div class="bg-gray-50 rounded-lg p-4">
                    <p class="text-xs text-gray-500 uppercase tracking-wide">Status</p>
                    <Badge variant="subtle" class="mt-1">{{ formData.finding_status || 'Open' }}</Badge>
                  </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                  <div class="bg-gray-50 rounded-lg p-4 text-center">
                    <p class="text-2xl font-bold text-blue-600">{{ formData.evidence?.length || 0 }}</p>
                    <p class="text-xs text-gray-500 mt-1">Evidence Items</p>
                  </div>
                  <div class="bg-gray-50 rounded-lg p-4 text-center">
                    <p class="text-2xl font-bold text-indigo-600">{{ formData.milestones?.length || 0 }}</p>
                    <p class="text-xs text-gray-500 mt-1">Action Milestones</p>
                  </div>
                  <div class="bg-gray-50 rounded-lg p-4 text-center">
                    <p class="text-2xl font-bold text-cyan-600">{{ formData.follow_up_history?.length || 0 }}</p>
                    <p class="text-xs text-gray-500 mt-1">Follow-up Activities</p>
                  </div>
                </div>

                <!-- Validation Status -->
                <div class="border-t border-gray-200 pt-4">
                  <h5 class="text-sm font-medium text-gray-900 mb-3">Validation Status</h5>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
                    <div v-for="check in validationChecks" :key="check.label" class="flex items-center">
                      <component
                        :is="check.valid ? CheckCircle2Icon : XCircleIcon"
                        :class="check.valid ? 'text-green-500' : 'text-red-500'"
                        class="h-5 w-5 mr-2 flex-shrink-0"
                      />
                      <span :class="check.valid ? 'text-gray-700' : 'text-red-600'" class="text-sm">
                        {{ check.label }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <template #actions>
      <div class="flex items-center justify-between w-full">
        <div class="flex items-center gap-2">
          <Button
            v-if="activeSection !== 'basic'"
            variant="outline"
            @click="previousSection"
          >
            <template #prefix><ChevronLeftIcon class="h-4 w-4" /></template>
            Previous
          </Button>
        </div>

        <div class="flex items-center gap-2">
          <Button variant="outline" @click="saveDraft" :loading="saving">
            <template #prefix><SaveIcon class="h-4 w-4" /></template>
            Save Draft
          </Button>

          <Button
            v-if="activeSection !== 'review'"
            variant="solid"
            theme="blue"
            @click="nextSection"
          >
            Next
            <template #suffix><ChevronRightIcon class="h-4 w-4" /></template>
          </Button>

          <Button
            v-else
            variant="solid"
            theme="blue"
            @click="submitForm"
            :loading="submitting"
            :disabled="!isFormValid"
          >
            <template #prefix><CheckIcon class="h-4 w-4" /></template>
            {{ isEditing ? 'Update Finding' : 'Create Finding' }}
          </Button>
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import InlineChildTable from "@/components/Common/InlineChildTable.vue"
import SectionHeader from "@/components/Common/SectionHeader.vue"
import LinkField from "@/components/Common/fields/LinkField.vue"
import FindingTemplateSelector from "@/components/findings/FindingTemplateSelector.vue"
import { useAuditStore } from "@/stores/audit"
import { Badge, Button, Dialog, FormControl, TextEditor } from "frappe-ui"
import {
	CheckCircle2Icon,
	CheckIcon,
	ChevronLeftIcon,
	ChevronRightIcon,
	FileSearchIcon,
	FlagIcon,
	LinkIcon,
	MapPinIcon,
	PlusIcon,
	RefreshCwIcon,
	SaveIcon,
	TrashIcon,
	XCircleIcon,
} from "lucide-vue-next"
import { computed, onMounted, reactive, ref, watch } from "vue"

// Props
const props = defineProps({
	modelValue: {
		type: Boolean,
		default: false,
	},
	finding: {
		type: Object,
		default: null,
	},
})

// Emits
const emit = defineEmits(["update:modelValue", "saved", "close"])

// Store
const auditStore = useAuditStore()

// Dialog visibility
const showDialog = computed({
	get: () => props.modelValue,
	set: (value) => emit("update:modelValue", value),
})

const isEditing = computed(() => !!props.finding?.name)
const saving = ref(false)
const submitting = ref(false)
const lastSaved = ref(null)
const activeSection = ref("template")

// Section definitions with descriptions
const sectionsList = [
	{
		key: "template",
		label: "Template Selection",
		description: "Choose a finding template",
	},
	{
		key: "basic",
		label: "Basic Information",
		description: "Finding ID and classification",
	},
	{
		key: "details",
		label: "Finding Details",
		description: "Condition, criteria, cause, effect",
	},
	{
		key: "evidence",
		label: "Evidence & Recommendation",
		description: "Supporting evidence",
	},
	{
		key: "response",
		label: "Management Response",
		description: "Management agreement",
	},
	{
		key: "action",
		label: "Corrective Action Plan",
		description: "Action plan and milestones",
	},
	{
		key: "followup",
		label: "Follow-up & Status",
		description: "Status tracking",
	},
	{
		key: "verification",
		label: "Verification",
		description: "Implementation verification",
	},
	{
		key: "closure",
		label: "Closure & Reporting",
		description: "Closure details",
	},
	{ key: "review", label: "Review & Submit", description: "Final review" },
]

// Section field mappings for validation
const sectionFields = {
	template: [], // Template selection is optional
	basic: [
		"finding_id",
		"engagement_reference",
		"finding_title",
		"finding_category",
	],
	details: ["condition", "criteria"],
	evidence: ["recommendation"],
	response: [],
	action: [],
	followup: ["finding_status"],
	verification: [],
	closure: [],
	review: [],
}

// Form data with all fields
const formData = reactive({
	// Basic Information
	finding_id: "",
	engagement_reference: "",
	finding_title: "",
	finding_category: "",
	risk_rating: "",
	business_impact_rating: "",
	date_identified: "",
	source_document: "",
	affected_locations: [],

	// Finding Details
	condition: "",
	criteria: "",
	cause: "",
	effect: "",

	// Evidence & Recommendation
	evidence: [],
	sample_size: null,
	exceptions_found: null,
	recommendation: "",

	// Management Response
	management_agrees: null,
	management_comments: "",
	response_date: "",
	management_response_by: "",
	management_response_date: "",

	// Corrective Action Plan
	action_plan_description: "",
	responsible_person: "",
	target_date: "",
	revised_target_date: "",
	priority: "",
	milestones: [],

	// Follow-up & Status
	finding_status: "Open",
	status_date: "",
	status_history: [],
	follow_up_required: 0,
	follow_up_frequency: "",
	next_follow_up_date: "",
	follow_up_history: [],

	// Verification
	verification_date: "",
	verified_by: "",
	verification_method: "",
	verification_status: "",
	verification_results: "",

	// Closure & Reporting
	closure_date: "",
	closed_by: "",
	closure_reason: "",
	final_disposition: "",
	closure_notes: "",
	include_in_report: false,
	reported_to_management: false,
	reported_to_audit_committee: false,
	reported_to_board: false,
	report_reference: "",

	// Related Findings
	related_findings: [],
	repeat_finding: 0,
	previous_finding_reference: "",
})

// Options for dropdowns
const categoryOptions = [
	{ label: "Control Weakness", value: "Control Weakness" },
	{ label: "Process Inefficiency", value: "Process Inefficiency" },
	{ label: "Compliance Gap", value: "Compliance Gap" },
	{ label: "Policy Violation", value: "Policy Violation" },
	{ label: "Documentation Issue", value: "Documentation Issue" },
	{ label: "Fraud Indicator", value: "Fraud Indicator" },
	{ label: "IT/System Issue", value: "IT/System Issue" },
	{ label: "Operational Risk", value: "Operational Risk" },
]

const riskRatingOptions = [
	{ label: "Critical", value: "Critical" },
	{ label: "High", value: "High" },
	{ label: "Medium", value: "Medium" },
	{ label: "Low", value: "Low" },
]

const impactOptions = [
	{ label: "Severe", value: "Severe" },
	{ label: "Major", value: "Major" },
	{ label: "Moderate", value: "Moderate" },
	{ label: "Minor", value: "Minor" },
	{ label: "Insignificant", value: "Insignificant" },
]

const statusOptions = [
	{ label: "Open", value: "Open" },
	{ label: "Action in Progress", value: "Action in Progress" },
	{ label: "Pending Verification", value: "Pending Verification" },
	{ label: "Closed", value: "Closed" },
	{ label: "Accepted as Risk", value: "Accepted as Risk" },
	{ label: "Management Override", value: "Management Override" },
]

const priorityOptions = [
	{ label: "Urgent", value: "Urgent" },
	{ label: "High", value: "High" },
	{ label: "Medium", value: "Medium" },
	{ label: "Low", value: "Low" },
]

const frequencyOptions = [
	{ label: "Weekly", value: "Weekly" },
	{ label: "Bi-weekly", value: "Bi-weekly" },
	{ label: "Monthly", value: "Monthly" },
	{ label: "Quarterly", value: "Quarterly" },
	{ label: "Semi-annually", value: "Semi-annually" },
	{ label: "Annually", value: "Annually" },
]

const verificationMethodOptions = [
	{ label: "Document Review", value: "Document Review" },
	{ label: "Re-testing", value: "Re-testing" },
	{ label: "Observation", value: "Observation" },
	{ label: "Interview", value: "Interview" },
	{ label: "Walkthrough", value: "Walkthrough" },
	{ label: "Data Analysis", value: "Data Analysis" },
]

const verificationStatusOptions = [
	{ label: "Not Started", value: "Not Started" },
	{ label: "In Progress", value: "In Progress" },
	{ label: "Verified - Effective", value: "Verified - Effective" },
	{
		label: "Verified - Partially Effective",
		value: "Verified - Partially Effective",
	},
	{ label: "Verified - Not Effective", value: "Verified - Not Effective" },
]

const closureReasonOptions = [
	{
		label: "Corrective Action Implemented",
		value: "Corrective Action Implemented",
	},
	{ label: "Risk Accepted", value: "Risk Accepted" },
	{ label: "Duplicate Finding", value: "Duplicate Finding" },
	{ label: "No Longer Applicable", value: "No Longer Applicable" },
	{ label: "Management Override", value: "Management Override" },
]

const dispositionOptions = [
	{ label: "Resolved", value: "Resolved" },
	{ label: "Partially Resolved", value: "Partially Resolved" },
	{ label: "Transferred", value: "Transferred" },
	{ label: "Deferred", value: "Deferred" },
]

// Placeholder options - would be fetched from API
const engagementOptions = ref([])
const userOptions = ref([])
const findingOptions = ref([])

// Child Table Configurations

// Affected Locations (simple - inline)
const affectedLocationColumns = [
	{
		key: "location",
		label: "Location",
		fieldType: "text",
		required: true,
		width: "200px",
	},
	{ key: "extent", label: "Extent/Notes", fieldType: "text", width: "300px" },
]

// Evidence (complex - modal)
const evidenceColumns = [
	{ key: "evidence_type", label: "Type", width: "120px" },
	{ key: "description", label: "Description", width: "250px" },
	{ key: "source", label: "Source", width: "150px" },
]

const evidenceFields = [
	{
		key: "evidence_type",
		label: "Evidence Type",
		type: "select",
		required: true,
		options: [
			{ label: "Document", value: "Document" },
			{ label: "Photo", value: "Photo" },
			{ label: "Data Analysis", value: "Data Analysis" },
			{ label: "Interview", value: "Interview" },
			{ label: "Observation", value: "Observation" },
			{ label: "Confirmation", value: "Confirmation" },
		],
	},
	{ key: "description", label: "Description", type: "text", required: true },
	{ key: "file", label: "Attachment", type: "attach" },
	{ key: "source", label: "Source", type: "text" },
	{ key: "reference", label: "Reference", type: "text" },
]

// Milestones (modal)
const milestoneColumns = [
	{ key: "milestone_description", label: "Description", width: "250px" },
	{ key: "due_date", label: "Due Date", width: "120px" },
	{ key: "status", label: "Status", width: "120px", component: "Badge" },
]

const milestoneFields = [
	{
		key: "milestone_description",
		label: "Milestone Description",
		type: "text",
		required: true,
	},
	{ key: "due_date", label: "Due Date", type: "date", required: true },
	{
		key: "status",
		label: "Status",
		type: "select",
		required: true,
		options: [
			{ label: "Not Started", value: "Not Started" },
			{ label: "In Progress", value: "In Progress" },
			{ label: "Completed", value: "Completed" },
			{ label: "Delayed", value: "Delayed" },
		],
	},
	{ key: "completion_date", label: "Completion Date", type: "date" },
	{ key: "notes", label: "Notes", type: "textarea" },
]

// Status History (modal, read-mostly)
const statusHistoryColumns = [
	{ key: "previous_status", label: "From", width: "120px" },
	{ key: "new_status", label: "To", width: "120px" },
	{ key: "changed_on", label: "Changed On", width: "150px" },
	{ key: "changed_by", label: "Changed By", width: "150px" },
]

const statusHistoryFields = [
	{
		key: "previous_status",
		label: "Previous Status",
		type: "select",
		options: statusOptions,
	},
	{
		key: "new_status",
		label: "New Status",
		type: "select",
		required: true,
		options: statusOptions,
	},
	{ key: "changed_on", label: "Changed On", type: "datetime", required: true },
	{
		key: "changed_by",
		label: "Changed By",
		type: "link",
		doctype: "User",
		required: true,
	},
	{ key: "reason", label: "Reason", type: "textarea" },
]

// Follow-up History (modal)
const followUpHistoryColumns = [
	{ key: "follow_up_date", label: "Date", width: "100px" },
	{ key: "follow_up_type", label: "Type", width: "150px" },
	{ key: "follow_up_by", label: "By", width: "150px" },
	{ key: "status", label: "Status", width: "100px", component: "Badge" },
]

const followUpHistoryFields = [
	{
		key: "follow_up_date",
		label: "Follow-up Date",
		type: "date",
		required: true,
	},
	{
		key: "follow_up_type",
		label: "Type",
		type: "select",
		required: true,
		options: [
			{ label: "Status Check", value: "Status Check" },
			{ label: "Progress Review", value: "Progress Review" },
			{
				label: "Implementation Verification",
				value: "Implementation Verification",
			},
			{ label: "Effectiveness Assessment", value: "Effectiveness Assessment" },
			{ label: "Closure Review", value: "Closure Review" },
		],
	},
	{
		key: "follow_up_by",
		label: "Follow-up By",
		type: "link",
		doctype: "User",
		required: true,
	},
	{ key: "findings", label: "Findings/Observations", type: "textarea" },
	{ key: "actions_taken", label: "Actions Taken", type: "textarea" },
	{ key: "next_follow_up_date", label: "Next Follow-up Date", type: "date" },
	{
		key: "status",
		label: "Status",
		type: "select",
		required: true,
		options: [
			{ label: "Open", value: "Open" },
			{ label: "In Progress", value: "In Progress" },
			{ label: "Completed", value: "Completed" },
			{ label: "Overdue", value: "Overdue" },
		],
	},
]

// Related Findings (modal)
const relatedFindingColumns = [
	{ key: "related_finding", label: "Related Finding", width: "200px" },
	{ key: "relationship_type", label: "Relationship", width: "150px" },
]

const relationshipTypeOptions = [
	{ label: "Duplicate", value: "Duplicate" },
	{ label: "Similar Issue", value: "Similar Issue" },
	{ label: "Root Cause", value: "Root Cause" },
	{ label: "Contributing Factor", value: "Contributing Factor" },
	{ label: "Follow-up Action", value: "Follow-up Action" },
	{ label: "Related Control", value: "Related Control" },
]

const evidenceTypeOptions = [
	{ label: "Document", value: "Document" },
	{ label: "Photo", value: "Photo" },
	{ label: "Data Analysis", value: "Data Analysis" },
	{ label: "Interview", value: "Interview" },
	{ label: "Observation", value: "Observation" },
	{ label: "Confirmation", value: "Confirmation" },
]

const milestoneStatusOptions = [
	{ label: "Not Started", value: "Not Started" },
	{ label: "In Progress", value: "In Progress" },
	{ label: "Completed", value: "Completed" },
	{ label: "Delayed", value: "Delayed" },
]

const followUpTypeOptions = [
	{ label: "Status Check", value: "Status Check" },
	{ label: "Progress Review", value: "Progress Review" },
	{
		label: "Implementation Verification",
		value: "Implementation Verification",
	},
	{ label: "Effectiveness Assessment", value: "Effectiveness Assessment" },
	{ label: "Closure Review", value: "Closure Review" },
]

// InlineChildTable Column Definitions
const inlineEvidenceColumns = [
	{
		key: "evidence_type",
		label: "Type",
		fieldType: "select",
		width: "130px",
		required: true,
		options: [
			{ label: "Document", value: "Document" },
			{ label: "Photo", value: "Photo" },
			{ label: "Data Analysis", value: "Data Analysis" },
			{ label: "Interview", value: "Interview" },
			{ label: "Observation", value: "Observation" },
			{ label: "Confirmation", value: "Confirmation" },
		],
	},
	{
		key: "description",
		label: "Description",
		fieldType: "text",
		width: "200px",
		required: true,
	},
	{ key: "source", label: "Source", fieldType: "text", width: "150px" },
	{ key: "reference", label: "Reference", fieldType: "text", width: "150px" },
]

const inlineMilestoneColumns = [
	{
		key: "milestone_description",
		label: "Description",
		fieldType: "text",
		width: "200px",
		required: true,
	},
	{
		key: "due_date",
		label: "Due Date",
		fieldType: "date",
		width: "120px",
		required: true,
	},
	{
		key: "status",
		label: "Status",
		fieldType: "select",
		width: "130px",
		required: true,
		options: [
			{ label: "Not Started", value: "Not Started" },
			{ label: "In Progress", value: "In Progress" },
			{ label: "Completed", value: "Completed" },
			{ label: "Delayed", value: "Delayed" },
		],
	},
	{ key: "notes", label: "Notes", fieldType: "text", width: "180px" },
]

const inlineFollowUpHistoryColumns = [
	{
		key: "follow_up_date",
		label: "Date",
		fieldType: "date",
		width: "120px",
		required: true,
	},
	{
		key: "follow_up_type",
		label: "Type",
		fieldType: "select",
		width: "160px",
		required: true,
		options: [
			{ label: "Status Check", value: "Status Check" },
			{ label: "Progress Review", value: "Progress Review" },
			{
				label: "Implementation Verification",
				value: "Implementation Verification",
			},
			{ label: "Effectiveness Assessment", value: "Effectiveness Assessment" },
			{ label: "Closure Review", value: "Closure Review" },
		],
	},
	{
		key: "follow_up_by",
		label: "Follow-up By",
		fieldType: "link",
		doctype: "User",
		width: "150px",
	},
	{ key: "findings", label: "Findings", fieldType: "text", width: "200px" },
]

const inlineRelatedFindingsColumns = [
	{
		key: "related_finding",
		label: "Related Finding",
		fieldType: "link",
		doctype: "Audit Finding",
		width: "200px",
		required: true,
	},
	{
		key: "relationship_type",
		label: "Relationship Type",
		fieldType: "select",
		width: "160px",
		required: true,
		options: [
			{ label: "Duplicate", value: "Duplicate" },
			{ label: "Similar Issue", value: "Similar Issue" },
			{ label: "Root Cause", value: "Root Cause" },
			{ label: "Contributing Factor", value: "Contributing Factor" },
			{ label: "Follow-up Action", value: "Follow-up Action" },
			{ label: "Related Control", value: "Related Control" },
		],
	},
]

// Computed properties
const overallProgress = computed(() => {
	let completed = 0
	completed += 10 // Template section always counts as complete
	if (
		formData.finding_id &&
		formData.finding_title &&
		formData.finding_category
	)
		completed += 12
	if (formData.condition && formData.criteria) completed += 12
	if (formData.recommendation) completed += 12
	if (formData.management_comments || formData.management_agrees !== null)
		completed += 12
	if (formData.action_plan_description || formData.milestones?.length > 0)
		completed += 12
	if (formData.finding_status) completed += 12
	if (formData.verification_date || formData.verification_status)
		completed += 12
	if (formData.closure_date || formData.closure_reason) completed += 12
	completed += 4 // Review section always counts
	return Math.min(100, completed)
})

const isFormValid = computed(() => {
	return (
		formData.finding_id &&
		formData.finding_title &&
		formData.finding_category &&
		formData.condition &&
		formData.criteria &&
		formData.recommendation &&
		formData.finding_status
	)
})

const validationChecks = computed(() => [
	{ label: "Finding ID is set", valid: !!formData.finding_id },
	{ label: "Finding Title is set", valid: !!formData.finding_title },
	{ label: "Category is selected", valid: !!formData.finding_category },
	{ label: "Condition is documented", valid: !!formData.condition },
	{ label: "Criteria is documented", valid: !!formData.criteria },
	{ label: "Recommendation is provided", valid: !!formData.recommendation },
	{ label: "Finding Status is set", valid: !!formData.finding_status },
	{ label: "Evidence is documented", valid: formData.evidence?.length > 0 },
])

// Section completion helpers
const isSectionComplete = (sectionKey) => {
	switch (sectionKey) {
		case "template":
			return true // Template selection is always complete (optional)
		case "basic":
			return (
				formData.finding_id &&
				formData.finding_title &&
				formData.finding_category
			)
		case "details":
			return formData.condition && formData.criteria
		case "evidence":
			return formData.recommendation
		case "response":
			return formData.management_agrees !== null || formData.management_comments
		case "action":
			return formData.action_plan_description || formData.milestones?.length > 0
		case "followup":
			return !!formData.finding_status
		case "verification":
			return formData.verification_date || formData.verification_status
		case "closure":
			return formData.closure_date || formData.closure_reason
		case "review":
			return true
		default:
			return false
	}
}

const getSectionStatusClass = (sectionKey) => {
	if (isSectionComplete(sectionKey)) {
		return "bg-green-500 text-white"
	}
	return "bg-gray-300 text-gray-600"
}

const setActiveSection = (sectionKey) => {
	activeSection.value = sectionKey
}

// Navigation methods
const previousSection = () => {
	const currentIndex = sectionsList.findIndex(
		(s) => s.key === activeSection.value,
	)
	if (currentIndex > 0) {
		activeSection.value = sectionsList[currentIndex - 1].key
	}
}

const nextSection = () => {
	const currentIndex = sectionsList.findIndex(
		(s) => s.key === activeSection.value,
	)
	if (currentIndex < sectionsList.length - 1) {
		activeSection.value = sectionsList[currentIndex + 1].key
	}
}

// Apply template method
const applyTemplate = async (template) => {
	try {
		// Apply template content to form
		if (template.condition_template) {
			formData.condition = template.condition_template
		}
		if (template.criteria_template) {
			formData.criteria = template.criteria_template
		}
		if (template.cause_template) {
			formData.cause = template.cause_template
		}
		if (template.effect_template) {
			formData.effect = template.effect_template
		}
		if (template.recommendation_template) {
			formData.recommendation = template.recommendation_template
		}

		// Apply default values
		if (template.finding_category) {
			formData.finding_category = template.finding_category
		}
		if (template.typical_risk_rating) {
			formData.risk_rating = template.typical_risk_rating
		}
		if (template.default_priority) {
			formData.priority = template.default_priority
		}
		if (template.default_business_unit) {
			// This would be set in the business unit field if it exists
		}
		if (template.default_responsible_person) {
			formData.responsible_person = template.default_responsible_person
		}
		if (template.default_target_days) {
			// Calculate target date from days
			const targetDate = new Date()
			targetDate.setDate(
				targetDate.getDate() + Number.parseInt(template.default_target_days),
			)
			formData.target_date = targetDate.toISOString().split("T")[0]
		}
		if (template.repeat_finding_default) {
			formData.repeat_finding = template.repeat_finding_default ? 1 : 0
		}

		// Auto-generate finding ID if not set
		if (!formData.finding_id) {
			generateFindingId()
		}

		// Move to basic information section
		setActiveSection("basic")
	} catch (error) {
		console.error("Error applying template:", error)
	}
}

// Child table methods - Locations
const addLocation = () => {
	formData.affected_locations.push({
		location: "",
		extent: "",
	})
}

const removeLocation = (index) => {
	formData.affected_locations.splice(index, 1)
}

// Child table methods - Evidence
const addEvidence = () => {
	formData.evidence.push({
		evidence_type: "",
		description: "",
		source: "",
		reference: "",
	})
}

const removeEvidence = (index) => {
	formData.evidence.splice(index, 1)
}

const getEvidenceBadgeTheme = (type) => {
	const themes = {
		Document: "blue",
		Photo: "green",
		"Data Analysis": "purple",
		Interview: "amber",
		Observation: "cyan",
		Confirmation: "teal",
	}
	return themes[type] || "gray"
}

// Child table methods - Milestones
const addMilestone = () => {
	formData.milestones.push({
		milestone_description: "",
		due_date: "",
		status: "Not Started",
		notes: "",
	})
}

const removeMilestone = (index) => {
	formData.milestones.splice(index, 1)
}

const getMilestoneStatusVariant = (status) => {
	const variants = {
		"Not Started": "subtle",
		"In Progress": "subtle",
		Completed: "subtle",
		Delayed: "subtle",
	}
	return variants[status] || "subtle"
}

// Child table methods - Follow-up History
const addFollowUp = () => {
	formData.follow_up_history.push({
		follow_up_date: "",
		follow_up_type: "",
		follow_up_by: "",
		findings: "",
	})
}

const removeFollowUp = (index) => {
	formData.follow_up_history.splice(index, 1)
}

// Child table methods - Related Findings
const addRelatedFinding = () => {
	formData.related_findings.push({
		related_finding: "",
		relationship_type: "",
	})
}

const removeRelatedFinding = (index) => {
	formData.related_findings.splice(index, 1)
}

// Risk badge helper
const getRiskBadgeVariant = (rating) => {
	const variants = {
		Critical: "subtle",
		High: "subtle",
		Medium: "subtle",
		Low: "subtle",
	}
	return variants[rating] || "subtle"
}

// Time formatting helper
const formatTimeAgo = (date) => {
	if (!date) return ""
	const seconds = Math.floor((new Date() - new Date(date)) / 1000)
	if (seconds < 60) return "just now"
	const minutes = Math.floor(seconds / 60)
	if (minutes < 60) return `${minutes}m ago`
	const hours = Math.floor(minutes / 60)
	if (hours < 24) return `${hours}h ago`
	const days = Math.floor(hours / 24)
	return `${days}d ago`
}

// Draft save
const saveDraft = async () => {
	saving.value = true
	try {
		if (isEditing.value && props.finding?.name) {
			await auditStore.updateAuditFinding(props.finding.name, formData)
		} else {
			await auditStore.createAuditFinding(formData)
		}
		lastSaved.value = new Date()
	} catch (error) {
		console.error("Failed to save draft:", error)
	} finally {
		saving.value = false
	}
}

// Submit form
const submitForm = async () => {
	if (!isFormValid.value) {
		// Navigate to first section with errors
		const firstIncomplete = sectionsList.find(
			(s) => !isSectionComplete(s.key) && sectionFields[s.key]?.length > 0,
		)
		if (firstIncomplete) {
			activeSection.value = firstIncomplete.key
		}
		return
	}

	submitting.value = true
	try {
		if (isEditing.value && props.finding?.name) {
			await auditStore.updateAuditFinding(props.finding.name, formData)
		} else {
			await auditStore.createAuditFinding(formData)
		}
		emit("saved", formData)
		showDialog.value = false
	} catch (error) {
		console.error("Failed to save finding:", error)
	} finally {
		submitting.value = false
	}
}

// Watch for finding prop changes (editing mode)
watch(
	() => props.finding,
	(newFinding) => {
		if (newFinding) {
			Object.keys(formData).forEach((key) => {
				if (newFinding[key] !== undefined) {
					formData[key] = newFinding[key]
				}
			})
		}
	},
	{ immediate: true, deep: true },
)

// Reset form when dialog closes
watch(
	() => props.modelValue,
	(newShow) => {
		if (!newShow) {
			activeSection.value = "basic"
			lastSaved.value = null
		}
	},
)

// Lifecycle
onMounted(() => {
	// Fetch options data if needed
})
</script>

<style scoped>
/* Custom styles for the form */
:deep(.ProseMirror) {
  min-height: 120px;
  padding: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

:deep(.ProseMirror:focus) {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}
</style>
