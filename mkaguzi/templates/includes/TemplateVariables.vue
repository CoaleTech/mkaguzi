<template>
  <div class="template-variables-manager">
    <div class="variables-header">
      <h3>Template Variables</h3>
      <Button @click="showAddVariableDialog = true" variant="solid" size="sm">
        <template #prefix>
          <PlusIcon class="w-4 h-4" />
        </template>
        Add Variable
      </Button>
    </div>

    <div class="variables-list">
      <div v-if="variables.length === 0" class="empty-state">
        <p>No variables defined for this template.</p>
        <Button @click="createDefaultVariables" variant="outline" size="sm">
          Create Default Variables
        </Button>
      </div>

      <div v-else class="variables-grid">
        <div
          v-for="variable in variables"
          :key="variable.name"
          class="variable-card"
        >
          <div class="variable-header">
            <div class="variable-info">
              <h4>{{ variable.variable_name }}</h4>
              <Badge :variant="getTypeVariant(variable.variable_type)">
                {{ variable.variable_type }}
              </Badge>
              <Badge v-if="variable.is_required" variant="destructive">Required</Badge>
              <Badge v-if="variable.is_global" variant="secondary">Global</Badge>
            </div>
            <div class="variable-actions">
              <Button @click="editVariable(variable)" variant="ghost" size="sm">
                <EditIcon class="w-4 h-4" />
              </Button>
              <Button @click="deleteVariable(variable)" variant="ghost" size="sm" class="text-red-600">
                <TrashIcon class="w-4 h-4" />
              </Button>
            </div>
          </div>

          <div class="variable-details">
            <p v-if="variable.description" class="description">
              {{ variable.description }}
            </p>
            <div v-if="variable.default_value" class="default-value">
              <span class="label">Default:</span>
              <code>{{ variable.default_value }}</code>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add/Edit Variable Dialog -->
    <Dialog v-model="showAddVariableDialog">
      <DialogPanel>
        <div class="dialog-header">
          <DialogTitle>{{ editingVariable ? 'Edit Variable' : 'Add Variable' }}</DialogTitle>
          <DialogDescription>
            {{ editingVariable ? 'Update the variable properties' : 'Create a new template variable' }}
          </DialogDescription>
        </div>

        <div class="dialog-content">
          <div class="form-grid">
            <div class="form-field">
              <label for="variable_name">Variable Name *</label>
              <Input
                id="variable_name"
                v-model="variableForm.variable_name"
                placeholder="e.g., company_name"
                :disabled="editingVariable"
              />
            </div>

            <div class="form-field">
              <label for="variable_type">Variable Type *</label>
              <Select v-model="variableForm.variable_type">
                <SelectTrigger>
                  <SelectValue placeholder="Select type" />
                </SelectTrigger>
                <SelectList>
                  <SelectListItem value="Text">Text</SelectListItem>
                  <SelectListItem value="Number">Number</SelectListItem>
                  <SelectListItem value="Date">Date</SelectListItem>
                  <SelectListItem value="Boolean">Boolean</SelectListItem>
                  <SelectListItem value="List">List (JSON Array)</SelectListItem>
                  <SelectListItem value="Object">Object (JSON)</SelectListItem>
                  <SelectListItem value="File">File</SelectListItem>
                </SelectList>
              </Select>
            </div>

            <div class="form-field">
              <label for="default_value">Default Value</label>
              <Input
                id="default_value"
                v-model="variableForm.default_value"
                :placeholder="getDefaultPlaceholder(variableForm.variable_type)"
              />
            </div>

            <div class="form-field">
              <label for="description">Description</label>
              <Textarea
                id="description"
                v-model="variableForm.description"
                placeholder="Describe what this variable is used for"
                rows="2"
              />
            </div>

            <div class="form-field">
              <div class="checkbox-group">
                <Checkbox
                  id="is_required"
                  v-model:checked="variableForm.is_required"
                />
                <label for="is_required">Required variable</label>
              </div>
            </div>

            <div class="form-field">
              <div class="checkbox-group">
                <Checkbox
                  id="is_global"
                  v-model:checked="variableForm.is_global"
                />
                <label for="is_global">Global variable (available to all templates)</label>
              </div>
            </div>

            <div v-if="variableForm.variable_type === 'List' || variableForm.variable_type === 'Object'" class="form-field">
              <label for="validation_rules">Validation Rules (JSON)</label>
              <Textarea
                id="validation_rules"
                v-model="variableForm.validation_rules"
                placeholder='{"min": 1, "max": 100}'
                rows="3"
              />
            </div>
          </div>
        </div>

        <div class="dialog-footer">
          <Button @click="showAddVariableDialog = false" variant="outline">
            Cancel
          </Button>
          <Button @click="saveVariable" :disabled="!canSaveVariable" variant="solid">
            {{ editingVariable ? 'Update' : 'Create' }} Variable
          </Button>
        </div>
      </DialogPanel>
    </Dialog>

    <!-- Delete Confirmation Dialog -->
    <Dialog v-model="showDeleteDialog">
      <DialogPanel>
        <div class="dialog-header">
          <DialogTitle>Delete Variable</DialogTitle>
          <DialogDescription>
            Are you sure you want to delete the variable "{{ variableToDelete?.variable_name }}"?
            This action cannot be undone.
          </DialogDescription>
        </div>

        <div class="dialog-footer">
          <Button @click="showDeleteDialog = false" variant="outline">
            Cancel
          </Button>
          <Button @click="confirmDelete" variant="destructive">
            Delete Variable
          </Button>
        </div>
      </DialogPanel>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import {
  Button,
  Dialog,
  DialogPanel,
  DialogTitle,
  DialogDescription,
  Input,
  Textarea,
  Select,
  SelectTrigger,
  SelectValue,
  SelectList,
  SelectListItem,
  Checkbox,
  Badge
} from 'frappe-ui'
import { PlusIcon, EditIcon, TrashIcon } from 'lucide-vue-next'

// Props
const props = defineProps({
  templateId: {
    type: String,
    default: null
  },
  category: {
    type: String,
    default: null
  }
})

// Emits
const emit = defineEmits(['variables-updated'])

// Reactive data
const variables = ref([])
const showAddVariableDialog = ref(false)
const showDeleteDialog = ref(false)
const editingVariable = ref(null)
const variableToDelete = ref(null)

const variableForm = ref({
  variable_name: '',
  variable_type: 'Text',
  default_value: '',
  description: '',
  is_required: false,
  is_global: false,
  validation_rules: ''
})

// Computed
const canSaveVariable = computed(() => {
  return variableForm.value.variable_name.trim() &&
         variableForm.value.variable_type
})

// Methods
const loadVariables = async () => {
  try {
    const response = await frappe.call({
      method: 'mkaguzi.api.templates.get_template_variables',
      args: {
        template_id: props.templateId,
        category: props.category,
        include_global: true
      }
    })

    if (response.message.success) {
      variables.value = response.message.variables
    }
  } catch (error) {
    console.error('Error loading variables:', error)
    frappe.msgprint('Error loading template variables')
  }
}

const getTypeVariant = (type) => {
  const variants = {
    'Text': 'blue',
    'Number': 'green',
    'Date': 'orange',
    'Boolean': 'purple',
    'List': 'yellow',
    'Object': 'indigo',
    'File': 'gray'
  }
  return variants[type] || 'gray'
}

const getDefaultPlaceholder = (type) => {
  const placeholders = {
    'Text': 'Default text value',
    'Number': '0',
    'Date': '2025-01-01',
    'Boolean': 'false',
    'List': '["item1", "item2"]',
    'Object': '{"key": "value"}',
    'File': 'path/to/file'
  }
  return placeholders[type] || 'Default value'
}

const resetVariableForm = () => {
  variableForm.value = {
    variable_name: '',
    variable_type: 'Text',
    default_value: '',
    description: '',
    is_required: false,
    is_global: false,
    validation_rules: ''
  }
  editingVariable.value = null
}

const editVariable = (variable) => {
  editingVariable.value = variable
  variableForm.value = {
    variable_name: variable.variable_name,
    variable_type: variable.variable_type,
    default_value: variable.default_value || '',
    description: variable.description || '',
    is_required: variable.is_required || false,
    is_global: variable.is_global || false,
    validation_rules: variable.validation_rules ? JSON.stringify(variable.validation_rules, null, 2) : ''
  }
  showAddVariableDialog.value = true
}

const saveVariable = async () => {
  try {
    const formData = { ...variableForm.value }

    // Parse validation rules
    if (formData.validation_rules) {
      try {
        formData.validation_rules = JSON.parse(formData.validation_rules)
      } catch (e) {
        frappe.msgprint('Invalid JSON in validation rules')
        return
      }
    } else {
      formData.validation_rules = {}
    }

    // Add template/category info
    if (!formData.is_global) {
      formData.template = props.templateId
      formData.category = props.category
    }

    let response
    if (editingVariable.value) {
      // Update existing variable
      formData.variable_id = editingVariable.value.name
      response = await frappe.call({
        method: 'mkaguzi.api.templates.update_template_variable',
        args: formData
      })
    } else {
      // Create new variable
      response = await frappe.call({
        method: 'mkaguzi.api.templates.create_template_variable',
        args: formData
      })
    }

    if (response.message.success) {
      frappe.msgprint(response.message.message)
      showAddVariableDialog.value = false
      resetVariableForm()
      await loadVariables()
      emit('variables-updated')
    }
  } catch (error) {
    console.error('Error saving variable:', error)
    frappe.msgprint('Error saving variable')
  }
}

const deleteVariable = (variable) => {
  variableToDelete.value = variable
  showDeleteDialog.value = true
}

const confirmDelete = async () => {
  try {
    const response = await frappe.call({
      method: 'mkaguzi.api.templates.delete_template_variable',
      args: {
        variable_id: variableToDelete.value.name
      }
    })

    if (response.message.success) {
      frappe.msgprint(response.message.message)
      showDeleteDialog.value = false
      variableToDelete.value = null
      await loadVariables()
      emit('variables-updated')
    }
  } catch (error) {
    console.error('Error deleting variable:', error)
    frappe.msgprint('Error deleting variable')
  }
}

const createDefaultVariables = async () => {
  try {
    const response = await frappe.call({
      method: 'mkaguzi.mkaguzi.doctype.template_variable.template_variable.create_default_variables'
    })

    if (response.message) {
      frappe.msgprint(response.message.message)
      await loadVariables()
      emit('variables-updated')
    }
  } catch (error) {
    console.error('Error creating default variables:', error)
    frappe.msgprint('Error creating default variables')
  }
}

// Watchers
watch(() => props.templateId, () => {
  loadVariables()
})

watch(() => props.category, () => {
  loadVariables()
})

// Lifecycle
onMounted(() => {
  loadVariables()
})
</script>

<style scoped>
.template-variables-manager {
  @apply space-y-4;
}

.variables-header {
  @apply flex items-center justify-between;
}

.variables-list {
  @apply space-y-4;
}

.empty-state {
  @apply text-center py-8 text-gray-500;
}

.variables-grid {
  @apply grid gap-4 md:grid-cols-2 lg:grid-cols-3;
}

.variable-card {
  @apply border rounded-lg p-4 bg-white shadow-sm;
}

.variable-header {
  @apply flex items-start justify-between mb-3;
}

.variable-info h4 {
  @apply font-medium text-gray-900 mb-2;
}

.variable-info {
  @apply flex-1;
}

.variable-actions {
  @apply flex gap-1;
}

.variable-details {
  @apply space-y-2;
}

.description {
  @apply text-sm text-gray-600;
}

.default-value {
  @apply flex items-center gap-2;
}

.default-value .label {
  @apply text-sm font-medium text-gray-700;
}

.default-value code {
  @apply text-sm bg-gray-100 px-2 py-1 rounded;
}

.dialog-header {
  @apply mb-6;
}

.dialog-content {
  @apply space-y-4;
}

.form-grid {
  @apply grid gap-4 md:grid-cols-2;
}

.form-field {
  @apply space-y-2;
}

.checkbox-group {
  @apply flex items-center gap-2;
}

.dialog-footer {
  @apply flex justify-end gap-3 mt-6;
}
</style>