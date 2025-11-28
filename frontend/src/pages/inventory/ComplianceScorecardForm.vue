<template>
  <div class="p-6">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-4">
        <Button variant="ghost" @click="goBack">
          <ArrowLeft class="w-5 h-5" />
        </Button>
        <div>
          <h1 class="text-2xl font-bold text-gray-900">
            {{ isEdit ? 'Edit Compliance Scorecard' : 'New Compliance Scorecard' }}
          </h1>
          <p class="text-gray-500 mt-1">
            {{ isEdit ? `Editing ${route.params.id}` : 'Create a new compliance scorecard' }}
          </p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <Button variant="outline" @click="goBack">Cancel</Button>
        <Button variant="solid" @click="saveScorecard" :loading="saving">
          <Save class="w-4 h-4 mr-2" />
          {{ isEdit ? 'Save Changes' : 'Create Scorecard' }}
        </Button>
      </div>
    </div>

    <!-- Form -->
    <div class="max-w-4xl">
      <div class="space-y-6">
        <!-- Basic Information -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Basic Information</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Audit Plan <span class="text-red-500">*</span>
              </label>
              <FormControl
                type="autocomplete"
                v-model="form.audit_plan"
                :options="auditPlanOptions"
                placeholder="Select audit plan"
                @change="onAuditPlanChange"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Period</label>
              <FormControl
                type="text"
                v-model="form.period"
                placeholder="e.g., Q4 2025"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
              <FormControl
                type="select"
                v-model="form.status"
                :options="statusOptions"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Overall Score (%)</label>
              <FormControl
                type="number"
                v-model="form.overall_score"
                placeholder="0"
                min="0"
                max="100"
                @input="calculateOverallScore"
              />
            </div>
          </div>
        </div>

        <!-- Compliance Categories -->
        <div class="bg-white rounded-lg border p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-gray-900">Compliance Categories</h3>
            <div class="flex items-center gap-2">
              <Button variant="outline" size="sm" @click="loadFromAuditPlan">
                <Download class="w-4 h-4 mr-2" />
                Load from Plan
              </Button>
              <Button variant="outline" size="sm" @click="addCategory">
                <Plus class="w-4 h-4 mr-2" />
                Add Category
              </Button>
            </div>
          </div>

          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Category Name</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Score (%)</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total Checks</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Passed</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Failed</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Weight (%)</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Findings</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="(category, index) in form.compliance_categories" :key="index" class="hover:bg-gray-50">
                  <td class="px-4 py-4">
                    <FormControl
                      type="text"
                      v-model="category.category_name"
                      placeholder="Category name"
                      class="w-full"
                    />
                  </td>
                  <td class="px-4 py-4">
                    <FormControl
                      type="number"
                      v-model="category.score"
                      placeholder="0"
                      min="0"
                      max="100"
                      class="w-full"
                      @input="calculateOverallScore"
                    />
                  </td>
                  <td class="px-4 py-4">
                    <FormControl
                      type="number"
                      v-model="category.total_checks"
                      placeholder="0"
                      min="0"
                      class="w-full"
                    />
                  </td>
                  <td class="px-4 py-4">
                    <FormControl
                      type="number"
                      v-model="category.passed_checks"
                      placeholder="0"
                      min="0"
                      class="w-full"
                      @input="updateFailedChecks(index)"
                    />
                  </td>
                  <td class="px-4 py-4">
                    <FormControl
                      type="number"
                      v-model="category.failed_checks"
                      placeholder="0"
                      min="0"
                      class="w-full"
                      @input="updateScoreFromChecks(index)"
                    />
                  </td>
                  <td class="px-4 py-4">
                    <FormControl
                      type="number"
                      v-model="category.weight"
                      placeholder="0"
                      min="0"
                      max="100"
                      class="w-full"
                      @input="calculateOverallScore"
                    />
                  </td>
                  <td class="px-4 py-4">
                    <FormControl
                      type="text"
                      v-model="category.findings"
                      placeholder="Key findings"
                      class="w-full"
                    />
                  </td>
                  <td class="px-4 py-4">
                    <Button variant="ghost" size="sm" @click="removeCategory(index)">
                      <Trash2 class="w-4 h-4 text-red-600" />
                    </Button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Summary -->
          <div class="mt-4 pt-4 border-t">
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span class="text-gray-500">Total Categories:</span>
                <span class="font-medium ml-2">{{ form.compliance_categories.length }}</span>
              </div>
              <div>
                <span class="text-gray-500">Total Weight:</span>
                <span class="font-medium ml-2">{{ totalWeight }}%</span>
              </div>
              <div>
                <span class="text-gray-500">Weighted Score:</span>
                <span class="font-medium ml-2 text-blue-600">{{ weightedScore }}%</span>
              </div>
              <div>
                <span class="text-gray-500">Auto-calculated:</span>
                <span class="font-medium ml-2 text-green-600">{{ calculatedScore }}%</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Key Findings -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Key Findings</h3>
          <FormControl
            type="textarea"
            v-model="form.key_findings"
            placeholder="Summarize the key findings from the compliance assessment..."
            :rows="4"
          />
        </div>

        <!-- Recommendations -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Recommendations</h3>
          <FormControl
            type="textarea"
            v-model="form.recommendations"
            placeholder="Provide recommendations for improving compliance..."
            :rows="4"
          />
        </div>

        <!-- Additional Notes -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Additional Notes</h3>
          <FormControl
            type="textarea"
            v-model="form.notes"
            placeholder="Any additional notes or observations..."
            :rows="3"
          />
        </div>
      </div>

      <!-- Form Actions (Bottom) -->
      <div class="flex items-center justify-end gap-3 mt-6 pt-6 border-t">
        <Button variant="outline" @click="goBack">Cancel</Button>
        <Button variant="solid" @click="saveScorecard" :loading="saving">
          <Save class="w-4 h-4 mr-2" />
          {{ isEdit ? 'Save Changes' : 'Create Scorecard' }}
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Button, FormControl } from 'frappe-ui'
import { call } from 'frappe-ui'
import { ArrowLeft, Save, Download, Plus, Trash2 } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

const saving = ref(false)
const auditPlanOptions = ref([])

const isEdit = computed(() => route.params.id && route.params.id !== 'new')

const form = ref({
  audit_plan: '',
  period: '',
  status: 'Draft',
  overall_score: 0,
  compliance_categories: [],
  key_findings: '',
  recommendations: '',
  notes: ''
})

const totalWeight = computed(() => {
  return form.value.compliance_categories.reduce((sum, cat) => sum + (cat.weight || 0), 0)
})

const weightedScore = computed(() => {
  if (totalWeight.value === 0) return 0
  const weightedSum = form.value.compliance_categories.reduce((sum, cat) => {
    return sum + ((cat.score || 0) * (cat.weight || 0))
  }, 0)
  return Math.round(weightedSum / totalWeight.value)
})

const calculatedScore = computed(() => {
  if (form.value.compliance_categories.length === 0) return 0
  const totalScore = form.value.compliance_categories.reduce((sum, cat) => sum + (cat.score || 0), 0)
  return Math.round(totalScore / form.value.compliance_categories.length)
})

onMounted(async () => {
  await loadAuditPlans()

  if (isEdit.value) {
    await loadScorecard()
  }
})

async function loadAuditPlans() {
  try {
    const plans = await call('frappe.client.get_list', {
      doctype: 'Audit Plan',
      fields: ['name', 'plan_title'],
      limit_page_length: 0
    })
    auditPlanOptions.value = plans.map(p => ({
      label: p.plan_title || p.name,
      value: p.name
    }))
  } catch (error) {
    console.error('Error loading audit plans:', error)
  }
}

async function loadScorecard() {
  try {
    const scorecard = await call('frappe.client.get', {
      doctype: 'Compliance Scorecard',
      name: route.params.id
    })

    form.value = {
      audit_plan: scorecard.audit_plan || '',
      period: scorecard.period || '',
      status: scorecard.status || 'Draft',
      overall_score: scorecard.overall_score || 0,
      compliance_categories: scorecard.compliance_categories || [],
      key_findings: scorecard.key_findings || '',
      recommendations: scorecard.recommendations || '',
      notes: scorecard.notes || ''
    }
  } catch (error) {
    console.error('Error loading scorecard:', error)
  }
}

function onAuditPlanChange() {
  // Auto-set period if audit plan is selected
  const selectedPlan = auditPlanOptions.value.find(p => p.value === form.value.audit_plan)
  if (selectedPlan && !form.value.period) {
    // Could auto-populate period from audit plan, but for now just leave it
  }
}

function addCategory() {
  form.value.compliance_categories.push({
    category_name: '',
    score: 0,
    total_checks: 0,
    passed_checks: 0,
    failed_checks: 0,
    weight: 0,
    findings: ''
  })
}

function removeCategory(index) {
  form.value.compliance_categories.splice(index, 1)
  calculateOverallScore()
}

function updateFailedChecks(index) {
  const category = form.value.compliance_categories[index]
  if (category.total_checks && category.passed_checks) {
    category.failed_checks = category.total_checks - category.passed_checks
    updateScoreFromChecks(index)
  }
}

function updateScoreFromChecks(index) {
  const category = form.value.compliance_categories[index]
  if (category.total_checks > 0) {
    category.score = Math.round((category.passed_checks / category.total_checks) * 100)
    calculateOverallScore()
  }
}

function calculateOverallScore() {
  // Use weighted average if weights are provided, otherwise simple average
  if (totalWeight.value > 0) {
    form.value.overall_score = weightedScore.value
  } else {
    form.value.overall_score = calculatedScore.value
  }
}

async function loadFromAuditPlan() {
  if (!form.value.audit_plan) {
    alert('Please select an audit plan first')
    return
  }

  try {
    // Load audit plan to get related data
    const plan = await call('frappe.client.get', {
      doctype: 'Audit Plan',
      name: form.value.audit_plan
    })

    // Auto-populate categories based on plan data
    // This is a simplified example - in reality, you'd have predefined categories
    const defaultCategories = [
      { category_name: 'Planning & Preparation', score: 0, total_checks: 0, passed_checks: 0, failed_checks: 0, weight: 20, findings: '' },
      { category_name: 'Execution & Documentation', score: 0, total_checks: 0, passed_checks: 0, failed_checks: 0, weight: 25, findings: '' },
      { category_name: 'Quality Control', score: 0, total_checks: 0, passed_checks: 0, failed_checks: 0, weight: 20, findings: '' },
      { category_name: 'Compliance & Standards', score: 0, total_checks: 0, passed_checks: 0, failed_checks: 0, weight: 20, findings: '' },
      { category_name: 'Reporting & Follow-up', score: 0, total_checks: 0, passed_checks: 0, failed_checks: 0, weight: 15, findings: '' }
    ]

    form.value.compliance_categories = defaultCategories
    calculateOverallScore()
  } catch (error) {
    console.error('Error loading from audit plan:', error)
  }
}

async function saveScorecard() {
  // Validate required fields
  if (!form.value.audit_plan) {
    alert('Audit plan is required')
    return
  }

  saving.value = true

  try {
    if (isEdit.value) {
      // Update existing
      await call('frappe.client.set_value', {
        doctype: 'Compliance Scorecard',
        name: route.params.id,
        fieldname: form.value
      })
      router.push(`/inventory-audit/scorecards/${route.params.id}`)
    } else {
      // Create new
      const result = await call('frappe.client.insert', {
        doc: {
          doctype: 'Compliance Scorecard',
          ...form.value
        }
      })
      router.push(`/inventory-audit/scorecards/${result.name}`)
    }
  } catch (error) {
    console.error('Error saving scorecard:', error)
    alert('Error saving scorecard: ' + error.message)
  } finally {
    saving.value = false
  }
}

function goBack() {
  if (isEdit.value) {
    router.push(`/inventory-audit/scorecards/${route.params.id}`)
  } else {
    router.push('/inventory-audit/scorecards')
  }
}

// Options
const statusOptions = [
  { label: 'Draft', value: 'Draft' },
  { label: 'In Progress', value: 'In Progress' },
  { label: 'Completed', value: 'Completed' },
  { label: 'Approved', value: 'Approved' },
  { label: 'Archived', value: 'Archived' }
]
</script>
