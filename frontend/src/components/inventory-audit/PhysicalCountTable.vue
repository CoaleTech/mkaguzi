<template>
  <div class="physical-count-table">
    <div class="flex items-center justify-between mb-3">
      <div>
        <h4 class="text-sm font-medium text-gray-700">{{ title || 'Count Items' }}</h4>
        <p class="text-xs text-gray-500">{{ items.length }} items • {{ varianceCount }} with variance</p>
      </div>
      <div class="flex items-center gap-2">
        <Button
          v-if="!readonly"
          size="sm"
          variant="outline"
          @click="addItem"
        >
          <Plus class="w-4 h-4 mr-1" />
          Add Item
        </Button>
        <Button
          v-if="!readonly && items.length > 0"
          size="sm"
          variant="outline"
          @click="calculateAllVariances"
        >
          <Calculator class="w-4 h-4 mr-1" />
          Calculate Variances
        </Button>
      </div>
    </div>

    <!-- Summary Cards -->
    <div v-if="items.length > 0" class="grid grid-cols-4 gap-3 mb-4">
      <div class="bg-blue-50 rounded-lg p-3">
        <p class="text-xs text-blue-600">Total Items</p>
        <p class="text-lg font-bold text-blue-700">{{ items.length }}</p>
      </div>
      <div class="bg-green-50 rounded-lg p-3">
        <p class="text-xs text-green-600">No Variance</p>
        <p class="text-lg font-bold text-green-700">{{ noVarianceCount }}</p>
      </div>
      <div class="bg-yellow-50 rounded-lg p-3">
        <p class="text-xs text-yellow-600">With Variance</p>
        <p class="text-lg font-bold text-yellow-700">{{ varianceCount }}</p>
      </div>
      <div class="bg-red-50 rounded-lg p-3">
        <p class="text-xs text-red-600">Material Variance</p>
        <p class="text-lg font-bold text-red-700">{{ materialCount }}</p>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="items.length === 0" class="text-center py-8 text-gray-500 bg-gray-50 rounded-lg">
      <Package class="w-10 h-10 mx-auto mb-2 text-gray-300" />
      <p class="text-sm">No count items added</p>
      <Button v-if="!readonly" size="sm" variant="ghost" class="mt-2" @click="addItem">
        Add First Item
      </Button>
    </div>

    <!-- Table -->
    <div v-else class="overflow-x-auto border rounded-lg">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-8">#</th>
            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Item Code</th>
            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
            <th class="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider w-24">System Qty</th>
            <th class="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider w-24">Counted Qty</th>
            <th class="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider w-24">Variance</th>
            <th class="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider w-20">Var %</th>
            <th class="px-3 py-2 text-center text-xs font-medium text-gray-500 uppercase tracking-wider w-24">Condition</th>
            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Remarks</th>
            <th v-if="!readonly" class="px-3 py-2 w-10"></th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr 
            v-for="(item, index) in items" 
            :key="index"
            :class="getRowClass(item)"
          >
            <td class="px-3 py-2 text-sm text-gray-500">{{ index + 1 }}</td>
            
            <!-- Item Code -->
            <td class="px-3 py-2">
              <input
                v-if="!readonly"
                type="text"
                v-model="item.item_code"
                class="w-full px-2 py-1 text-sm border rounded focus:ring-1 focus:ring-blue-500"
                placeholder="Item code"
              />
              <span v-else class="text-sm font-medium text-gray-900">{{ item.item_code }}</span>
            </td>

            <!-- Description -->
            <td class="px-3 py-2">
              <input
                v-if="!readonly"
                type="text"
                v-model="item.item_description"
                class="w-full px-2 py-1 text-sm border rounded focus:ring-1 focus:ring-blue-500"
                placeholder="Description"
              />
              <span v-else class="text-sm text-gray-600">{{ item.item_description }}</span>
            </td>

            <!-- System Qty -->
            <td class="px-3 py-2 text-right">
              <input
                v-if="!readonly"
                type="number"
                v-model.number="item.system_qty"
                class="w-full px-2 py-1 text-sm text-right border rounded focus:ring-1 focus:ring-blue-500"
                @change="calculateVariance(index)"
              />
              <span v-else class="text-sm text-gray-900">{{ formatNumber(item.system_qty) }}</span>
            </td>

            <!-- Counted Qty -->
            <td class="px-3 py-2 text-right">
              <input
                v-if="!readonly"
                type="number"
                v-model.number="item.counted_qty"
                class="w-full px-2 py-1 text-sm text-right border rounded focus:ring-1 focus:ring-blue-500 font-medium"
                @change="calculateVariance(index)"
              />
              <span v-else class="text-sm font-medium text-gray-900">{{ formatNumber(item.counted_qty) }}</span>
            </td>

            <!-- Variance -->
            <td class="px-3 py-2 text-right">
              <span 
                class="text-sm font-medium"
                :class="getVarianceClass(item.variance_qty)"
              >
                {{ formatNumber(item.variance_qty) }}
              </span>
            </td>

            <!-- Variance % -->
            <td class="px-3 py-2 text-right">
              <span 
                class="text-sm"
                :class="getVarianceClass(item.variance_percent)"
              >
                {{ formatPercent(item.variance_percent) }}
              </span>
              <AlertTriangle 
                v-if="item.is_material" 
                class="inline w-4 h-4 ml-1 text-red-500" 
                title="Material Variance"
              />
            </td>

            <!-- Condition -->
            <td class="px-3 py-2 text-center">
              <select
                v-if="!readonly"
                v-model="item.condition"
                class="px-2 py-1 text-xs border rounded focus:ring-1 focus:ring-blue-500"
              >
                <option value="">-</option>
                <option value="Good">Good</option>
                <option value="Damaged">Damaged</option>
                <option value="Expired">Expired</option>
                <option value="Misplaced">Misplaced</option>
                <option value="Zero Stock">Zero Stock</option>
                <option value="Not Found">Not Found</option>
              </select>
              <Badge v-else-if="item.condition" :variant="getConditionVariant(item.condition)" size="sm">
                {{ item.condition }}
              </Badge>
            </td>

            <!-- Remarks -->
            <td class="px-3 py-2">
              <input
                v-if="!readonly"
                type="text"
                v-model="item.remarks"
                class="w-full px-2 py-1 text-sm border rounded focus:ring-1 focus:ring-blue-500"
                placeholder="Remarks"
              />
              <span v-else class="text-sm text-gray-600">{{ item.remarks }}</span>
            </td>

            <!-- Remove -->
            <td v-if="!readonly" class="px-3 py-2 text-center">
              <Button
                size="sm"
                variant="ghost"
                @click="removeItem(index)"
              >
                <Trash2 class="w-4 h-4 text-red-500" />
              </Button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Totals Row -->
    <div v-if="items.length > 0" class="mt-3 flex items-center justify-end gap-6 text-sm">
      <div>
        <span class="text-gray-500">Total Variance Qty:</span>
        <span class="ml-2 font-medium" :class="getVarianceClass(totalVarianceQty)">
          {{ formatNumber(totalVarianceQty) }}
        </span>
      </div>
      <div>
        <span class="text-gray-500">Total Variance Value:</span>
        <span class="ml-2 font-medium" :class="getVarianceClass(totalVarianceValue)">
          {{ formatCurrency(totalVarianceValue) }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Badge, Button } from "frappe-ui"
import {
	AlertTriangle,
	Calculator,
	Package,
	Plus,
	Trash2,
} from "lucide-vue-next"
import { computed } from "vue"

const props = defineProps({
	modelValue: {
		type: Array,
		default: () => [],
	},
	readonly: {
		type: Boolean,
		default: false,
	},
	title: {
		type: String,
		default: "Count Items",
	},
	materialityThreshold: {
		type: Object,
		default: () => ({
			qty: 0,
			amount: 0,
			percent: 5,
		}),
	},
	valuationRates: {
		type: Object,
		default: () => ({}),
	},
})

const emit = defineEmits(["update:modelValue"])

const items = computed({
	get: () => props.modelValue || [],
	set: (val) => emit("update:modelValue", val),
})

const varianceCount = computed(() => {
	return items.value.filter((i) => i.variance_qty && i.variance_qty !== 0)
		.length
})

const noVarianceCount = computed(() => {
	return items.value.filter((i) => !i.variance_qty || i.variance_qty === 0)
		.length
})

const materialCount = computed(() => {
	return items.value.filter((i) => i.is_material).length
})

const totalVarianceQty = computed(() => {
	return items.value.reduce((sum, item) => sum + (item.variance_qty || 0), 0)
})

const totalVarianceValue = computed(() => {
	return items.value.reduce((sum, item) => sum + (item.variance_value || 0), 0)
})

function addItem() {
	const newItems = [
		...items.value,
		{
			item_code: "",
			item_description: "",
			barcode: "",
			batch_no: "",
			serial_no: "",
			system_qty: 0,
			counted_qty: 0,
			variance_qty: 0,
			variance_percent: 0,
			variance_value: 0,
			is_material: false,
			condition: "",
			photo_attachment: "",
			remarks: "",
		},
	]
	emit("update:modelValue", newItems)
}

function removeItem(index) {
	const newItems = items.value.filter((_, i) => i !== index)
	emit("update:modelValue", newItems)
}

function calculateVariance(index) {
	const newItems = [...items.value]
	const item = newItems[index]

	const systemQty = item.system_qty || 0
	const countedQty = item.counted_qty || 0

	item.variance_qty = countedQty - systemQty

	if (systemQty !== 0) {
		item.variance_percent = ((countedQty - systemQty) / systemQty) * 100
	} else {
		item.variance_percent = countedQty !== 0 ? 100 : 0
	}

	// Calculate variance value if we have valuation rate
	const rate = props.valuationRates[item.item_code] || 0
	item.variance_value = item.variance_qty * rate

	// Check materiality
	item.is_material = checkMateriality(item)

	emit("update:modelValue", newItems)
}

function calculateAllVariances() {
	items.value.forEach((_, index) => calculateVariance(index))
}

function checkMateriality(item) {
	const { qty, amount, percent } = props.materialityThreshold

	if (qty && Math.abs(item.variance_qty || 0) >= qty) return true
	if (amount && Math.abs(item.variance_value || 0) >= amount) return true
	if (percent && Math.abs(item.variance_percent || 0) >= percent) return true

	return false
}

function getRowClass(item) {
	if (item.is_material) return "bg-red-50"
	if (item.variance_qty && item.variance_qty !== 0) return "bg-yellow-50"
	return ""
}

function getVarianceClass(value) {
	if (!value || value === 0) return "text-gray-600"
	return value > 0 ? "text-green-600" : "text-red-600"
}

function getConditionVariant(condition) {
	const variants = {
		Good: "green",
		Damaged: "red",
		Expired: "red",
		Misplaced: "yellow",
		"Zero Stock": "gray",
		"Not Found": "red",
	}
	return variants[condition] || "gray"
}

function formatNumber(num) {
	if (num === null || num === undefined) return "-"
	return new Intl.NumberFormat().format(num)
}

function formatPercent(num) {
	if (num === null || num === undefined) return "-"
	return `${num.toFixed(1)}%`
}

function formatCurrency(amount) {
	if (amount === null || amount === undefined) return "-"
	return new Intl.NumberFormat("en-KE", {
		style: "currency",
		currency: "KES",
		minimumFractionDigits: 0,
	}).format(amount)
}
</script>
