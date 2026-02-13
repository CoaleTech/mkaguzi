<template>
  <div class="grid grid-cols-5 gap-4">
    <!-- Total Trackers -->
    <div class="bg-white rounded-xl border p-4">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-gray-500">Total Trackers</p>
          <p class="text-2xl font-bold text-gray-900">{{ stats.total }}</p>
        </div>
        <div class="h-10 w-10 rounded-lg bg-blue-50 flex items-center justify-center">
          <FileText class="h-5 w-5 text-blue-600" />
        </div>
      </div>
      <div class="mt-2 flex items-center gap-1 text-xs">
        <span class="text-gray-500">{{ stats.periodsCount }} periods covered</span>
      </div>
    </div>

    <!-- VAT Compliance -->
    <div class="bg-white rounded-xl border p-4">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-gray-500">VAT Filed</p>
          <p class="text-2xl font-bold text-green-600">{{ stats.vatFiled }}</p>
        </div>
        <div class="h-10 w-10 rounded-lg bg-green-50 flex items-center justify-center">
          <Receipt class="h-5 w-5 text-green-600" />
        </div>
      </div>
      <div class="mt-2">
        <div class="flex items-center justify-between text-xs">
          <span class="text-gray-500">Compliance Rate</span>
          <span class="font-medium text-green-600">{{ stats.vatRate }}%</span>
        </div>
        <div class="w-full bg-gray-100 rounded-full h-1.5 mt-1">
          <div
            class="bg-green-500 h-1.5 rounded-full"
            :style="{ width: `${stats.vatRate}%` }"
          />
        </div>
      </div>
    </div>

    <!-- PAYE Compliance -->
    <div class="bg-white rounded-xl border p-4">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-gray-500">PAYE Filed</p>
          <p class="text-2xl font-bold text-gray-900">{{ stats.payeFiled }}</p>
        </div>
        <div class="h-10 w-10 rounded-lg bg-gray-50 flex items-center justify-center">
          <Briefcase class="h-5 w-5 text-gray-900" />
        </div>
      </div>
      <div class="mt-2">
        <div class="flex items-center justify-between text-xs">
          <span class="text-gray-500">Compliance Rate</span>
          <span class="font-medium text-gray-900">{{ stats.payeRate }}%</span>
        </div>
        <div class="w-full bg-gray-100 rounded-full h-1.5 mt-1">
          <div
            class="bg-gray-900 h-1.5 rounded-full"
            :style="{ width: `${stats.payeRate}%` }"
          />
        </div>
      </div>
    </div>

    <!-- Statutory Deductions -->
    <div class="bg-white rounded-xl border p-4">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-gray-500">Statutory Filed</p>
          <p class="text-2xl font-bold text-indigo-600">{{ stats.statutoryFiled }}</p>
        </div>
        <div class="h-10 w-10 rounded-lg bg-indigo-50 flex items-center justify-center">
          <Building class="h-5 w-5 text-indigo-600" />
        </div>
      </div>
      <div class="mt-2 flex items-center gap-2 text-xs">
        <span class="text-gray-500">NSSF: {{ stats.nssfFiled }}</span>
        <span class="text-gray-300">|</span>
        <span class="text-gray-500">NHIF: {{ stats.nhifFiled }}</span>
      </div>
    </div>

    <!-- Issues & Score -->
    <div class="bg-white rounded-xl border p-4">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-gray-500">Open Issues</p>
          <p class="text-2xl font-bold" :class="stats.openIssues > 0 ? 'text-red-600' : 'text-green-600'">
            {{ stats.openIssues }}
          </p>
        </div>
        <div
          class="h-10 w-10 rounded-lg flex items-center justify-center"
          :class="stats.openIssues > 0 ? 'bg-red-50' : 'bg-green-50'"
        >
          <AlertCircle
            class="h-5 w-5"
            :class="stats.openIssues > 0 ? 'text-red-600' : 'text-green-600'"
          />
        </div>
      </div>
      <div class="mt-2 flex items-center justify-between text-xs">
        <span class="text-gray-500">Avg Score</span>
        <Badge :theme="getScoreTheme(stats.avgScore)" size="sm">
          {{ stats.avgScore }}%
        </Badge>
      </div>
    </div>
  </div>

  <!-- Additional Stats Row -->
  <div class="grid grid-cols-4 gap-4 mt-4">
    <!-- Total Tax Liability -->
    <div class="bg-gradient-to-r from-blue-500 to-blue-600 rounded-xl p-4 text-white">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-blue-100">Total VAT Payable</p>
          <p class="text-xl font-bold">KES {{ formatNumber(stats.totalVatPayable) }}</p>
        </div>
        <DollarSign class="h-8 w-8 text-blue-200" />
      </div>
    </div>

    <!-- Total PAYE -->
    <div class="bg-gradient-to-r from-gray-900 to-gray-700 rounded-xl p-4 text-white">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-gray-100">Total PAYE</p>
          <p class="text-xl font-bold">KES {{ formatNumber(stats.totalPaye) }}</p>
        </div>
        <Users class="h-8 w-8 text-gray-200" />
      </div>
    </div>

    <!-- Total WHT -->
    <div class="bg-gradient-to-r from-orange-500 to-orange-600 rounded-xl p-4 text-white">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-orange-100">Total WHT</p>
          <p class="text-xl font-bold">KES {{ formatNumber(stats.totalWht) }}</p>
        </div>
        <Percent class="h-8 w-8 text-orange-200" />
      </div>
    </div>

    <!-- Total Statutory -->
    <div class="bg-gradient-to-r from-teal-500 to-teal-600 rounded-xl p-4 text-white">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-teal-100">Total Statutory</p>
          <p class="text-xl font-bold">KES {{ formatNumber(stats.totalStatutory) }}</p>
        </div>
        <Shield class="h-8 w-8 text-teal-200" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Badge } from 'frappe-ui'
import {
  FileText,
  Receipt,
  Briefcase,
  Building,
  AlertCircle,
  DollarSign,
  Users,
  Percent,
  Shield,
} from 'lucide-vue-next'

const props = defineProps({
  trackers: {
    type: Array,
    default: () => [],
  },
})

const stats = computed(() => {
  const total = props.trackers.length

  // Filing counts
  const vatFiled = props.trackers.filter((t) => t.vat_return_filed).length
  const payeFiled = props.trackers.filter((t) => t.paye_return_filed).length
  const whtFiled = props.trackers.filter((t) => t.wht_return_filed).length
  const nssfFiled = props.trackers.filter((t) => t.nssf_return_filed).length
  const nhifFiled = props.trackers.filter((t) => t.nhif_return_filed).length

  // Rates
  const vatRate = total > 0 ? Math.round((vatFiled / total) * 100) : 0
  const payeRate = total > 0 ? Math.round((payeFiled / total) * 100) : 0

  // Financial totals
  const totalVatPayable = props.trackers.reduce((sum, t) => sum + (t.net_vat_payable || 0), 0)
  const totalPaye = props.trackers.reduce((sum, t) => sum + (t.total_paye || 0), 0)
  const totalWht = props.trackers.reduce((sum, t) => sum + (t.total_wht || 0), 0)
  const totalNssf = props.trackers.reduce((sum, t) => sum + (t.total_nssf || 0), 0)
  const totalNhif = props.trackers.reduce((sum, t) => sum + (t.total_nhif || 0), 0)
  const totalStatutory = totalNssf + totalNhif

  // Issues
  const openIssues = props.trackers.reduce((sum, t) => {
    return sum + (t.issues_identified?.filter((i) => i.resolution_status === 'Open').length || 0)
  }, 0)

  // Average compliance score
  const scoresWithValue = props.trackers.filter((t) => t.compliance_score !== null && t.compliance_score !== undefined)
  const avgScore =
    scoresWithValue.length > 0
      ? Math.round(scoresWithValue.reduce((sum, t) => sum + (t.compliance_score || 0), 0) / scoresWithValue.length)
      : 0

  // Unique periods
  const periodsCount = new Set(props.trackers.map((t) => t.tax_period)).size

  return {
    total,
    vatFiled,
    payeFiled,
    whtFiled,
    nssfFiled,
    nhifFiled,
    statutoryFiled: Math.min(nssfFiled, nhifFiled),
    vatRate,
    payeRate,
    totalVatPayable,
    totalPaye,
    totalWht,
    totalStatutory,
    openIssues,
    avgScore,
    periodsCount,
  }
})

function formatNumber(num) {
  return new Intl.NumberFormat('en-KE').format(num || 0)
}

function getScoreTheme(score) {
  if (score >= 90) return 'green'
  if (score >= 70) return 'blue'
  if (score >= 50) return 'orange'
  return 'red'
}
</script>
