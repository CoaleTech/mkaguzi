<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white border-b border-gray-200 px-6 py-4">
      <div class="flex justify-between items-center">
        <div class="flex items-center gap-4">
          <Button 
            variant="ghost" 
            size="sm" 
            @click="goBack"
            class="text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft class="w-5 h-5" />
          </Button>
          <div>
            <div class="flex items-center gap-3">
              <h1 class="text-2xl font-bold text-gray-900">
                {{ isNewMode ? 'New VAT Reconciliation' : reconciliation?.name || 'VAT Reconciliation' }}
              </h1>
              <Badge v-if="!isNewMode && reconciliation" :variant="getStatusVariant(reconciliation.status)">
                {{ reconciliation.status }}
              </Badge>
            </div>
            <p class="text-gray-600 mt-1">
              {{ isNewMode ? 'Create a new VAT reconciliation record' : 'Manage VAT data reconciliation' }}
            </p>
          </div>
        </div>
        <div class="flex gap-3">
          <Button 
            v-if="!isNewMode && canRunReconciliation"
            variant="solid" 
            size="sm" 
            @click="runReconciliation"
            :loading="runningReconciliation"
            class="bg-blue-600 hover:bg-blue-700 shadow-sm"
          >
            <div class="flex items-center gap-2">
              <Play class="w-4 h-4" />
              <span>Run Reconciliation</span>
            </div>
          </Button>
          <div v-if="!isNewMode" class="relative" ref="exportDropdownRef">
            <Button 
              variant="solid" 
              size="sm" 
              @click="showExportDropdown = !showExportDropdown"
              class="bg-gray-600 hover:bg-gray-700 shadow-sm"
            >
              <div class="flex items-center gap-2">
                <Download class="w-4 h-4" />
                <span>Export</span>
                <ChevronDown class="w-4 h-4" />
              </div>
            </Button>
            <div 
              v-if="showExportDropdown" 
              class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 z-10"
            >
              <button 
                @click="exportReport('excel')"
                class="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 rounded-t-lg flex items-center gap-2"
              >
                <FileSpreadsheet class="w-4 h-4" />
                Export to Excel
              </button>
              <button 
                @click="exportReport('pdf')"
                class="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 rounded-b-lg flex items-center gap-2"
              >
                <FileText class="w-4 h-4" />
                Export to PDF
              </button>
            </div>
          </div>
          <AskAIButton
            v-if="!isNewMode && reconciliation"
            contextType="vat-reconciliation"
            pageComponent="VATReconciliationDetail"
            :contextData="getVATReconciliationContext()"
            variant="solid"
            size="sm"
            theme="purple"
          />
          <Button 
            v-if="isNewMode"
            variant="solid" 
            size="sm" 
            @click="createReconciliation"
            :loading="saving"
            class="bg-green-600 hover:bg-green-700 shadow-sm"
          >
            <div class="flex items-center gap-2">
              <Save class="w-4 h-4" />
              <span>Create</span>
            </div>
          </Button>
        </div>
      </div>
    </div>

    <!-- Loading Overlay -->
    <div v-if="loading" class="flex items-center justify-center py-32">
      <div class="flex flex-col items-center gap-4">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <span class="text-gray-600 font-medium">Loading reconciliation data...</span>
      </div>
    </div>

    <div v-else class="p-6 space-y-6">
      <!-- Configuration Section - Always show, but readonly for non-Draft -->
      <div class="bg-white rounded-lg border border-gray-200 shadow-sm">
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900">Reconciliation Configuration</h3>
          <p class="text-sm text-gray-600 mt-1">
            {{ isNewMode ? 'Set up the basic parameters for this VAT reconciliation' : 'Configuration details for this reconciliation' }}
          </p>
        </div>
        <div class="p-6">
          <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-2">Reconciliation Month <span v-if="canEditConfig" class="text-red-500">*</span></label>
              <select
                v-model="form.reconciliation_month"
                class="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                :disabled="!canEditConfig"
              >
                <option value="">Select Month</option>
                <option v-for="month in months" :key="month" :value="month">{{ month }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-2">Fiscal Year <span v-if="canEditConfig" class="text-red-500">*</span></label>
              <select
                v-model="form.fiscal_year"
                class="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                :disabled="!canEditConfig"
              >
                <option value="">Select Year</option>
                <option v-for="year in fiscalYears" :key="year" :value="year">{{ year }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-2">Reconciliation Type <span v-if="canEditConfig" class="text-red-500">*</span></label>
              <select
                v-model="form.reconciliation_type"
                class="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                :disabled="!canEditConfig"
              >
                <option value="">Select Type</option>
                <option value="System vs iTax">System vs iTax</option>
                <option value="System vs TIMs">System vs TIMs</option>
                <option value="iTax vs TIMs">iTax vs TIMs</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-2">Tolerance (±)</label>
              <input
                v-model.number="form.tolerance"
                type="number"
                step="0.01"
                class="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                placeholder="0.01"
                :disabled="!canEditConfig"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Summary Cards (for existing reconciliations) -->
      <div v-if="!isNewMode && reconciliation" class="space-y-6">
        <!-- Record Count Cards - 6 equal columns -->
        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
          <div class="bg-white rounded-lg border border-gray-200 p-4 shadow-sm hover:shadow-md transition-shadow">
            <div class="flex flex-col items-center text-center">
              <div class="bg-blue-100 p-3 rounded-full mb-3">
                <Database class="w-5 h-5 text-blue-600" />
              </div>
              <p class="text-xs font-medium text-gray-500 uppercase tracking-wide">Source A</p>
              <p class="text-2xl font-bold text-blue-600 mt-1 tabular-nums">{{ reconciliation.total_source_a_records || 0 }}</p>
              <p class="text-xs text-gray-400">records</p>
            </div>
          </div>
          <div class="bg-white rounded-lg border border-gray-200 p-4 shadow-sm hover:shadow-md transition-shadow">
            <div class="flex flex-col items-center text-center">
              <div class="bg-purple-100 p-3 rounded-full mb-3">
                <Database class="w-5 h-5 text-purple-600" />
              </div>
              <p class="text-xs font-medium text-gray-500 uppercase tracking-wide">Source B</p>
              <p class="text-2xl font-bold text-purple-600 mt-1 tabular-nums">{{ reconciliation.total_source_b_records || 0 }}</p>
              <p class="text-xs text-gray-400">records</p>
            </div>
          </div>
          <div class="bg-white rounded-lg border border-gray-200 p-4 shadow-sm hover:shadow-md transition-shadow">
            <div class="flex flex-col items-center text-center">
              <div class="bg-green-100 p-3 rounded-full mb-3">
                <CheckCircle class="w-5 h-5 text-green-600" />
              </div>
              <p class="text-xs font-medium text-gray-500 uppercase tracking-wide">Matched</p>
              <p class="text-2xl font-bold text-green-600 mt-1 tabular-nums">{{ reconciliation.total_matched || 0 }}</p>
              <p class="text-xs text-gray-400">records</p>
            </div>
          </div>
          <div class="bg-white rounded-lg border border-gray-200 p-4 shadow-sm hover:shadow-md transition-shadow">
            <div class="flex flex-col items-center text-center">
              <div class="bg-yellow-100 p-3 rounded-full mb-3">
                <AlertTriangle class="w-5 h-5 text-yellow-600" />
              </div>
              <p class="text-xs font-medium text-gray-500 uppercase tracking-wide">Missing in B</p>
              <p class="text-2xl font-bold text-yellow-600 mt-1 tabular-nums">{{ reconciliation.total_unmatched_source_a || 0 }}</p>
              <p class="text-xs text-gray-400">CU Invoices</p>
            </div>
          </div>
          <div class="bg-white rounded-lg border border-gray-200 p-4 shadow-sm hover:shadow-md transition-shadow">
            <div class="flex flex-col items-center text-center">
              <div class="bg-orange-100 p-3 rounded-full mb-3">
                <AlertTriangle class="w-5 h-5 text-orange-600" />
              </div>
              <p class="text-xs font-medium text-gray-500 uppercase tracking-wide">Missing in A</p>
              <p class="text-2xl font-bold text-orange-600 mt-1 tabular-nums">{{ reconciliation.total_unmatched_source_b || 0 }}</p>
              <p class="text-xs text-gray-400">CU Invoices</p>
            </div>
          </div>
          <div class="bg-white rounded-lg border border-gray-200 p-4 shadow-sm hover:shadow-md transition-shadow">
            <div class="flex flex-col items-center text-center">
              <div class="bg-red-100 p-3 rounded-full mb-3">
                <XCircle class="w-5 h-5 text-red-600" />
              </div>
              <p class="text-xs font-medium text-gray-500 uppercase tracking-wide">Amount Mismatch</p>
              <p class="text-2xl font-bold text-red-600 mt-1 tabular-nums">{{ reconciliation.total_amount_discrepancies || 0 }}</p>
              <p class="text-xs text-gray-400">records</p>
            </div>
          </div>
        </div>

        <!-- Amount Summary Cards - 4 equal columns with consistent height -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div v-if="!loadingResults" class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg border border-blue-200 p-5 shadow-sm hover:shadow-md transition-shadow min-h-[120px] flex flex-col justify-between">
            <div class="flex items-start justify-between">
              <p class="text-xs font-semibold text-blue-700 uppercase tracking-wide">Source A Total</p>
              <DollarSign class="w-5 h-5 text-blue-500 flex-shrink-0" />
            </div>
            <div class="mt-auto">
              <p class="text-xl font-bold text-blue-800 tabular-nums truncate" :title="formatCurrency(reconciliation.total_source_a_amount || 0)">
                {{ formatCurrency(reconciliation.total_source_a_amount || 0) }}
              </p>
            </div>
          </div>
          <div v-if="!loadingResults" class="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg border border-purple-200 p-5 shadow-sm hover:shadow-md transition-shadow min-h-[120px] flex flex-col justify-between">
            <div class="flex items-start justify-between">
              <p class="text-xs font-semibold text-purple-700 uppercase tracking-wide">Source B Total</p>
              <DollarSign class="w-5 h-5 text-purple-500 flex-shrink-0" />
            </div>
            <div class="mt-auto">
              <p class="text-xl font-bold text-purple-800 tabular-nums truncate" :title="formatCurrency(reconciliation.total_source_b_amount || 0)">
                {{ formatCurrency(reconciliation.total_source_b_amount || 0) }}
              </p>
            </div>
          </div>
          <div v-if="!loadingResults" class="bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg border border-gray-300 p-5 shadow-sm hover:shadow-md transition-shadow min-h-[120px] flex flex-col justify-between">
            <div class="flex items-start justify-between">
              <p class="text-xs font-semibold text-gray-700 uppercase tracking-wide">Net Difference</p>
              <TrendingUp class="w-5 h-5 text-gray-500 flex-shrink-0" />
            </div>
            <div class="mt-auto">
              <p class="text-xl font-bold tabular-nums truncate" 
                 :class="netDifference > 0 ? 'text-orange-600' : netDifference < 0 ? 'text-red-600' : 'text-green-600'"
                 :title="formatVariance(netDifference)">
                {{ formatVariance(netDifference) }}
              </p>
              <p class="text-xs mt-1" :class="netDifference > 0 ? 'text-orange-500' : netDifference < 0 ? 'text-red-500' : 'text-green-500'">
                {{ netDifference > 0 ? '↑ Source A higher' : netDifference < 0 ? '↓ Source B higher' : '= Balanced' }}
              </p>
            </div>
          </div>
          <div v-if="!loadingResults" class="bg-gradient-to-br from-red-50 to-red-100 rounded-lg border border-red-200 p-5 shadow-sm hover:shadow-md transition-shadow min-h-[120px] flex flex-col justify-between">
            <div class="flex items-start justify-between">
              <p class="text-xs font-semibold text-red-700 uppercase tracking-wide">Total Variance</p>
              <XCircle class="w-5 h-5 text-red-500 flex-shrink-0" />
            </div>
            <div class="mt-auto">
              <p class="text-xl font-bold text-red-800 tabular-nums truncate" :title="formatCurrency(reconciliation.total_variance_amount || 0)">
                {{ formatCurrency(reconciliation.total_variance_amount || 0) }}
              </p>
              <p class="text-xs text-red-500 mt-1">Sum of all discrepancies</p>
            </div>
          </div>
          
          <!-- Loading state for summary cards -->
          <div v-else class="col-span-4 flex items-center justify-center py-8">
            <div class="flex items-center gap-3">
              <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
              <span class="text-gray-600">Loading summary data...</span>
            </div>
          </div>
        </div>

        <!-- Match Rate Progress Bar -->
        <div v-if="!loadingResults" class="bg-white rounded-lg border border-gray-200 p-5 shadow-sm">
          <div class="flex items-center justify-between mb-3">
            <div class="flex items-center gap-2">
              <div class="w-3 h-3 rounded-full" :class="matchRateBarColor"></div>
              <p class="text-sm font-semibold text-gray-700">Match Rate</p>
            </div>
            <p class="text-lg font-bold tabular-nums" :class="matchRateColor">
              {{ (reconciliation.match_percentage || 0).toFixed(1) }}%
            </p>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
            <div 
              class="h-3 rounded-full transition-all duration-700 ease-out" 
              :class="matchRateBarColor"
              :style="{ width: (reconciliation.match_percentage || 0) + '%' }"
            ></div>
          </div>
          <div class="flex justify-between mt-2 text-xs text-gray-500">
            <span>0%</span>
            <span>50%</span>
            <span>100%</span>
          </div>
        </div>
        
        <!-- Loading state for match rate -->
        <div v-else class="bg-white rounded-lg border border-gray-200 p-5 shadow-sm flex items-center justify-center">
          <div class="flex items-center gap-3">
            <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
            <span class="text-gray-600">Loading match rate...</span>
          </div>
        </div>
      </div>

      <!-- File Upload Section -->
      <div v-if="!isNewMode" class="bg-white rounded-lg border border-gray-200 shadow-sm">
        <div class="px-6 py-4 border-b border-gray-200">
          <div class="flex justify-between items-center">
            <div>
              <h3 class="text-lg font-semibold text-gray-900">Data Files</h3>
              <p class="text-sm text-gray-600 mt-1">Upload CSV files for reconciliation. Required files depend on reconciliation type.</p>
            </div>
            <div class="flex gap-2">
              <Button variant="outline" size="sm" @click="downloadAllTemplates">
                <Download class="w-4 h-4 mr-1" /> Download All Templates
              </Button>
            </div>
          </div>
        </div>
        <div class="p-6">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <!-- System Data File -->
            <div 
              v-if="requiresSystemData"
              class="border-2 border-dashed rounded-lg p-6 text-center transition-colors"
              :class="reconciliation?.system_data_file ? 'border-green-300 bg-green-50' : 'border-gray-300 hover:border-blue-400'"
            >
              <div v-if="reconciliation?.system_data_file" class="flex flex-col items-center">
                <CheckCircle class="w-12 h-12 text-green-500 mb-3" />
                <p class="font-medium text-green-700 mb-1">System Data Uploaded</p>
                <p class="text-sm text-gray-600 mb-3">{{ reconciliation.system_records_count || 0 }} records</p>
                <div class="flex gap-2">
                  <Button variant="ghost" size="sm" @click="viewFileData('system')">
                    <Eye class="w-4 h-4 mr-1" /> View
                  </Button>
                  <Button variant="ghost" size="sm" @click="triggerFileInput('system')" :disabled="!canUploadFiles">
                    <RefreshCw class="w-4 h-4 mr-1" /> Replace
                  </Button>
                </div>
              </div>
              <div v-else class="flex flex-col items-center">
                <Upload class="w-12 h-12 text-gray-400 mb-3" />
                <p class="font-medium text-gray-700 mb-1">System Data</p>
                <p class="text-sm text-gray-500 mb-3">CSV with posting_date, invoice_number, cu_invoice_number, net_amount</p>
                <div class="flex gap-2 mb-2">
                  <Button 
                    variant="solid" 
                    size="sm" 
                    @click="triggerFileInput('system')"
                    :disabled="!canUploadFiles"
                    :loading="uploadingFile === 'system'"
                    class="bg-blue-600 hover:bg-blue-700"
                  >
                    <span class="flex items-center gap-1">
                      <Upload class="w-4 h-4 shrink-0" />
                      <span>Upload CSV</span>
                    </span>
                  </Button>
                </div>
                <button 
                  @click="downloadTemplate('system')" 
                  class="text-xs text-blue-600 hover:text-blue-800 hover:underline flex items-center gap-1"
                >
                  <Download class="w-3 h-3" /> Download Template
                </button>
              </div>
              <input 
                ref="systemFileInput"
                type="file" 
                accept=".csv"
                class="hidden"
                @change="(e) => handleFileUpload(e, 'system')"
              />
            </div>

            <!-- iTax Data File -->
            <div 
              v-if="requiresItaxData"
              class="border-2 border-dashed rounded-lg p-6 text-center transition-colors"
              :class="reconciliation?.itax_data_file ? 'border-green-300 bg-green-50' : 'border-gray-300 hover:border-blue-400'"
            >
              <div v-if="reconciliation?.itax_data_file" class="flex flex-col items-center">
                <CheckCircle class="w-12 h-12 text-green-500 mb-3" />
                <p class="font-medium text-green-700 mb-1">iTax Data Uploaded</p>
                <p class="text-sm text-gray-600 mb-3">{{ reconciliation.itax_records_count || 0 }} records</p>
                <div class="flex gap-2">
                  <Button variant="ghost" size="sm" @click="viewFileData('itax')">
                    <Eye class="w-4 h-4 mr-1" /> View
                  </Button>
                  <Button variant="ghost" size="sm" @click="triggerFileInput('itax')" :disabled="!canUploadFiles">
                    <RefreshCw class="w-4 h-4 mr-1" /> Replace
                  </Button>
                </div>
              </div>
              <div v-else class="flex flex-col items-center">
                <Upload class="w-12 h-12 text-gray-400 mb-3" />
                <p class="font-medium text-gray-700 mb-1">iTax Data</p>
                <p class="text-sm text-gray-500 mb-3">CSV with posting_date, cu_invoice_number, amount</p>
                <div class="flex gap-2 mb-2">
                  <Button 
                    variant="solid" 
                    size="sm" 
                    @click="triggerFileInput('itax')"
                    :disabled="!canUploadFiles"
                    :loading="uploadingFile === 'itax'"
                    class="bg-blue-600 hover:bg-blue-700"
                  >
                    <span class="flex items-center gap-1">
                      <Upload class="w-4 h-4 shrink-0" />
                      <span>Upload CSV</span>
                    </span>
                  </Button>
                </div>
                <button 
                  @click="downloadTemplate('itax')" 
                  class="text-xs text-blue-600 hover:text-blue-800 hover:underline flex items-center gap-1"
                >
                  <Download class="w-3 h-3" /> Download Template
                </button>
              </div>
              <input 
                ref="itaxFileInput"
                type="file" 
                accept=".csv"
                class="hidden"
                @change="(e) => handleFileUpload(e, 'itax')"
              />
            </div>

            <!-- TIMs Data File -->
            <div 
              v-if="requiresTimsData"
              class="border-2 border-dashed rounded-lg p-6 text-center transition-colors"
              :class="reconciliation?.tims_data_file ? 'border-green-300 bg-green-50' : 'border-gray-300 hover:border-blue-400'"
            >
              <div v-if="reconciliation?.tims_data_file" class="flex flex-col items-center">
                <CheckCircle class="w-12 h-12 text-green-500 mb-3" />
                <p class="font-medium text-green-700 mb-1">TIMs Data Uploaded</p>
                <p class="text-sm text-gray-600 mb-3">{{ reconciliation.tims_records_count || 0 }} records</p>
                <div class="flex gap-2">
                  <Button variant="ghost" size="sm" @click="viewFileData('tims')">
                    <Eye class="w-4 h-4 mr-1" /> View
                  </Button>
                  <Button variant="ghost" size="sm" @click="triggerFileInput('tims')" :disabled="!canUploadFiles">
                    <RefreshCw class="w-4 h-4 mr-1" /> Replace
                  </Button>
                </div>
              </div>
              <div v-else class="flex flex-col items-center">
                <Upload class="w-12 h-12 text-gray-400 mb-3" />
                <p class="font-medium text-gray-700 mb-1">TIMs Device Data</p>
                <p class="text-sm text-gray-500 mb-3">CSV with posting_date, cu_invoice_number, amount</p>
                <div class="flex gap-2 mb-2">
                  <Button 
                    variant="solid" 
                    size="sm" 
                    @click="triggerFileInput('tims')"
                    :disabled="!canUploadFiles"
                    :loading="uploadingFile === 'tims'"
                    class="bg-blue-600 hover:bg-blue-700"
                  >
                    <span class="flex items-center gap-1">
                      <Upload class="w-4 h-4 shrink-0" />
                      <span>Upload CSV</span>
                    </span>
                  </Button>
                </div>
                <button 
                  @click="downloadTemplate('tims')" 
                  class="text-xs text-blue-600 hover:text-blue-800 hover:underline flex items-center gap-1"
                >
                  <Download class="w-3 h-3" /> Download Template
                </button>
              </div>
              <input 
                ref="timsFileInput"
                type="file" 
                accept=".csv"
                class="hidden"
                @change="(e) => handleFileUpload(e, 'tims')"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Debug Section - Temporarily hidden for troubleshooting -->
      <!-- 
      <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-sm">
        <div class="flex justify-between items-start mb-3">
          <div>
            <p class="font-semibold text-gray-800">Performance Optimizations Applied:</p>
            <p>✅ Database-level filtering and pagination</p>
            <p>✅ Results caching (5-minute expiry)</p>
            <p>✅ Increased page size to 100 items</p>
            <p>✅ Optimized API calls for large datasets</p>
          </div>
          <Button 
            variant="outline" 
            size="sm" 
            @click="clearCacheAndReload"
            class="text-xs"
          >
            Clear Cache
          </Button>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-3">
          <div class="bg-white p-3 rounded border">
            <p class="text-xs text-gray-600">Reconciliation Status</p>
            <p class="font-medium">{{ reconciliation?.status || 'Not loaded' }}</p>
          </div>
          <div class="bg-white p-3 rounded border">
            <p class="text-xs text-gray-600">Results Loaded</p>
            <p class="font-medium">{{ reconciliationResults.length > 0 ? 'Yes' : 'No' }} ({{ reconciliationResults.length }} items)</p>
          </div>
          <div class="bg-white p-3 rounded border">
            <p class="text-xs text-gray-600">Cache Status</p>
            <p class="font-medium">{{ Object.keys(store.resultsCache).length }} queries cached</p>
            <p class="text-xs text-gray-500 mt-1">
              {{ Object.keys(store.resultsCache).length > 0 ? 'Cache active' : 'No cached data yet' }}
            </p>
          </div>
        </div>
        
        <div class="mt-2 text-xs text-gray-600">
          <p><strong>Note:</strong> Cache populates when viewing results tabs for completed reconciliations. Switch between "All", "Matched", "Missing in A/B", or "Amount Mismatch" tabs to see caching in action.</p>
        </div>
        
        <div v-if="Object.keys(store.resultsCache).length > 0" class="mt-3">
          <p class="text-xs font-medium text-gray-700 mb-2">Cached Queries:</p>
          <div class="bg-white p-2 rounded border text-xs font-mono max-h-20 overflow-y-auto">
            <div v-for="(cacheKey, index) in Object.keys(store.resultsCache)" :key="cacheKey" class="mb-1">
              {{ index + 1 }}. {{ cacheKey }}
            </div>
          </div>
        </div>
      </div>
      -->

      <!-- Reconciliation Results -->
      <div v-if="!isNewMode && hasResults" class="bg-white rounded-lg border border-gray-200 shadow-sm">
        <div class="px-6 py-4 border-b border-gray-200">
          <div class="flex justify-between items-center">
            <div>
              <h3 class="text-lg font-semibold text-gray-900">Reconciliation Results</h3>
              <p class="text-sm text-gray-600 mt-1">
                Last reconciled: {{ reconciliation?.last_reconciled_at ? formatDate(reconciliation.last_reconciled_at) : 'Never' }}
              </p>
            </div>
            <div class="flex gap-2">
              <Button 
                v-for="tab in resultTabs" 
                :key="tab.key"
                variant="ghost" 
                size="sm"
                :class="activeResultTab === tab.key ? 'bg-blue-100 text-blue-700' : ''"
                @click="activeResultTab = tab.key"
              >
                {{ tab.label }} ({{ tab.count }})
              </Button>
            </div>
          </div>
        </div>
        <div class="overflow-x-auto">
          <table v-if="!loadingResults" class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">CU Invoice No</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Invoice No</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date (Source A)</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date (Source B)</th>
                <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Amount (Source A)</th>
                <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Amount (Source B)</th>
                <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Variance</th>
                <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="item in filteredResults" :key="item.name" class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ item.cu_invoice_number }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ item.invoice_number || '-' }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ formatDate(item.posting_date_a) }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ formatDate(item.posting_date_b) }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900 tabular-nums">{{ formatCurrency(item.amount_a) }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900 tabular-nums">{{ formatCurrency(item.amount_b) }}</td>
                <td 
                  class="px-6 py-4 whitespace-nowrap text-sm text-right font-medium tabular-nums" 
                  :class="getVarianceClass(item.variance, item.match_status)"
                  :title="getVarianceTooltip(item.variance, item.match_status)"
                >
                  {{ formatVariance(item.variance) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-center">
                  <Badge :variant="getMatchStatusVariant(item.match_status)">{{ item.match_status }}</Badge>
                </td>
              </tr>
              <tr v-if="filteredResults.length === 0 && !loadingResults">
                <td colspan="8" class="px-6 py-12 text-center text-gray-500">
                  No records found for this filter
                </td>
              </tr>
            </tbody>
          </table>
          
          <!-- Loading state -->
          <div v-else class="flex items-center justify-center py-12">
            <div class="flex items-center gap-3">
              <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
              <span class="text-gray-600">Loading reconciliation results...</span>
            </div>
          </div>
        </div>
        <!-- Results Pagination -->
        <div v-if="resultsTotalPages > 1" class="px-6 py-4 border-t border-gray-200 bg-gray-50 flex items-center justify-between">
          <p class="text-sm text-gray-700">
            Showing {{ (resultsPage - 1) * resultsPageSize + 1 }} - {{ Math.min(resultsPage * resultsPageSize, filteredResultsTotal) }} of {{ filteredResultsTotal }}
          </p>
          <div class="flex gap-2">
            <Button 
              variant="ghost" 
              size="sm" 
              :disabled="resultsPage === 1" 
              @click="changePage(resultsPage - 1)"
            >
              Previous
            </Button>
            <Button 
              variant="ghost" 
              size="sm" 
              :disabled="resultsPage === resultsTotalPages" 
              @click="changePage(resultsPage + 1)"
            >
              Next
            </Button>
          </div>
        </div>
      </div>

      <!-- Historical Comparison -->
      <div v-if="!isNewMode && reconciliation?.status === 'Reconciled'" class="bg-white rounded-lg border border-gray-200 shadow-sm">
        <div class="px-6 py-4 border-b border-gray-200">
          <div class="flex justify-between items-center">
            <div>
              <h3 class="text-lg font-semibold text-gray-900">Historical Comparison</h3>
              <p class="text-sm text-gray-600 mt-1">Compare with previous month's reconciliation</p>
            </div>
            <Button 
              variant="solid" 
              size="sm" 
              @click="fetchHistoricalComparison"
              :loading="loadingHistorical"
              class="bg-gray-600 hover:bg-gray-700"
            >
              <TrendingUp class="w-4 h-4 mr-1" /> Load Comparison
            </Button>
          </div>
        </div>
        <div v-if="historicalComparison" class="p-6">
          <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div class="text-center p-4 bg-gray-50 rounded-lg">
              <p class="text-sm text-gray-600 mb-1">Match Rate Change</p>
              <p class="text-2xl font-bold" :class="historicalComparison.match_rate_change >= 0 ? 'text-green-600' : 'text-red-600'">
                {{ historicalComparison.match_rate_change >= 0 ? '+' : '' }}{{ historicalComparison.match_rate_change?.toFixed(1) }}%
              </p>
            </div>
            <div class="text-center p-4 bg-gray-50 rounded-lg">
              <p class="text-sm text-gray-600 mb-1">Discrepancy Change</p>
              <p class="text-2xl font-bold" :class="historicalComparison.discrepancy_change <= 0 ? 'text-green-600' : 'text-red-600'">
                {{ historicalComparison.discrepancy_change >= 0 ? '+' : '' }}{{ historicalComparison.discrepancy_change }}
              </p>
            </div>
            <div class="text-center p-4 bg-gray-50 rounded-lg">
              <p class="text-sm text-gray-600 mb-1">Variance Change</p>
              <p class="text-2xl font-bold" :class="historicalComparison.variance_change <= 0 ? 'text-green-600' : 'text-red-600'">
                {{ formatCurrency(historicalComparison.variance_change) }}
              </p>
            </div>
            <div class="text-center p-4 bg-gray-50 rounded-lg">
              <p class="text-sm text-gray-600 mb-1">Previous Month</p>
              <p class="text-2xl font-bold text-gray-900">{{ historicalComparison.previous_month }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- File Preview Modal -->
    <Dialog v-model="showFilePreview" :options="{ title: `${previewFileType} Data Preview`, size: 'xl' }">
      <template #body-content>
        <div class="max-h-96 overflow-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50 sticky top-0">
              <tr>
                <th v-for="col in previewColumns" :key="col" class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                  {{ col }}
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="(row, idx) in previewData" :key="idx" class="hover:bg-gray-50">
                <td v-for="col in previewColumns" :key="col" class="px-4 py-2 text-sm text-gray-900">
                  {{ row[col] }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
      <template #actions>
        <Button variant="solid" size="sm" @click="showFilePreview = false">Close</Button>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { useVATReconciliationStore } from "@/stores/useVATReconciliationStore"
import { Badge, Button, Dialog, call } from "frappe-ui"
import AskAIButton from "@/components/AskAIButton.vue"
import {
	AlertTriangle,
	ArrowLeft,
	Brain,
	CheckCircle,
	ChevronDown,
	Database,
	DollarSign,
	Download,
	Eye,
	FileSpreadsheet,
	FileText,
	Play,
	RefreshCw,
	Save,
	TrendingUp,
	Upload,
	XCircle,
} from "lucide-vue-next"
import { computed, onMounted, ref, watch } from "vue"
import { useRoute, useRouter } from "vue-router"

const props = defineProps({
	id: String,
})

const router = useRouter()
const route = useRoute()
const store = useVATReconciliationStore()

// Refs
const systemFileInput = ref(null)
const itaxFileInput = ref(null)
const timsFileInput = ref(null)
const exportDropdownRef = ref(null)

// State
const loading = ref(false)
const saving = ref(false)
const runningReconciliation = ref(false)
const uploadingFile = ref(null)
const loadingHistorical = ref(false)
const loadingResults = ref(false)
const showExportDropdown = ref(false)
const showFilePreview = ref(false)
const previewFileType = ref("")
const previewData = ref([])
const previewColumns = ref([])
const activeResultTab = ref("all")
const resultsPage = ref(1)
const resultsPageSize = ref(100) // Increased for better performance
const historicalComparison = ref(null)

const reconciliation = ref(null)
const reconciliationResults = ref([])

const form = ref({
	reconciliation_month: "",
	fiscal_year: "",
	reconciliation_type: "",
	tolerance: 0.01,
})

const months = [
	"January",
	"February",
	"March",
	"April",
	"May",
	"June",
	"July",
	"August",
	"September",
	"October",
	"November",
	"December",
]

const fiscalYears = computed(() => {
	const currentYear = new Date().getFullYear()
	return Array.from({ length: 6 }, (_, i) => `FY ${currentYear - i}`)
})

const isNewMode = computed(() => route.path.endsWith("/new"))

const canEditConfig = computed(() => {
	return isNewMode.value || reconciliation.value?.status === "Draft"
})

const requiresSystemData = computed(() => {
	const type =
		reconciliation.value?.reconciliation_type || form.value.reconciliation_type
	// Handle both frontend format (system_vs_itax) and DocType format (System vs iTax)
	return (
		type === "system_vs_itax" ||
		type === "system_vs_tims" ||
		type === "System vs iTax" ||
		type === "System vs TIMs"
	)
})

const requiresItaxData = computed(() => {
	const type =
		reconciliation.value?.reconciliation_type || form.value.reconciliation_type
	return (
		type === "system_vs_itax" ||
		type === "itax_vs_tims" ||
		type === "System vs iTax" ||
		type === "iTax vs TIMs"
	)
})

const requiresTimsData = computed(() => {
	const type =
		reconciliation.value?.reconciliation_type || form.value.reconciliation_type
	return (
		type === "system_vs_tims" ||
		type === "itax_vs_tims" ||
		type === "System vs TIMs" ||
		type === "iTax vs TIMs"
	)
})

const canUploadFiles = computed(() => {
	if (!reconciliation.value) return false
	// Allow uploads in Draft, Files Uploaded, Validated, or Processing states
	return ["Draft", "Files Uploaded", "Validated", "Validating"].includes(
		reconciliation.value.status,
	)
})

const canRunReconciliation = computed(() => {
	if (!reconciliation.value) return false
	if (
		!["Draft", "Files Uploaded", "Validated"].includes(
			reconciliation.value.status,
		)
	)
		return false

	const type = reconciliation.value.reconciliation_type
	if (type === "system_vs_itax" || type === "System vs iTax") {
		return (
			reconciliation.value.system_data_file &&
			reconciliation.value.itax_data_file
		)
	}
	if (type === "system_vs_tims" || type === "System vs TIMs") {
		return (
			reconciliation.value.system_data_file &&
			reconciliation.value.tims_data_file
		)
	}
	if (type === "itax_vs_tims" || type === "iTax vs TIMs") {
		return (
			reconciliation.value.itax_data_file && reconciliation.value.tims_data_file
		)
	}
	return false
})

const hasResults = computed(() => {
	return (
		reconciliationResults.value.length > 0 ||
		reconciliation.value?.status === "Completed" ||
		reconciliation.value?.status === "Reconciled"
	)
})

// Use document summary counts for tabs (not the loaded subset)
const resultTabs = computed(() => {
	const doc = reconciliation.value
	const totalAll =
		(doc?.total_matched || 0) +
		(doc?.total_unmatched_source_a || 0) +
		(doc?.total_unmatched_source_b || 0) +
		(doc?.total_amount_discrepancies || 0)
	return [
		{ key: "all", label: "All", count: totalAll },
		{ key: "matched", label: "Matched", count: doc?.total_matched || 0 },
		{
			key: "unmatched_a",
			label: "Missing in B",
			count: doc?.total_unmatched_source_a || 0,
		},
		{
			key: "unmatched_b",
			label: "Missing in A",
			count: doc?.total_unmatched_source_b || 0,
		},
		{
			key: "discrepancy",
			label: "Amount Mismatch",
			count: doc?.total_amount_discrepancies || 0,
		},
	]
})

// Results are already filtered by the API based on activeResultTab
const filteredResults = computed(() => {
	const start = (resultsPage.value - 1) * resultsPageSize.value
	return reconciliationResults.value.slice(start, start + resultsPageSize.value)
})

// Total for current filter comes from document summary
const filteredResultsTotal = computed(() => {
	const doc = reconciliation.value
	if (!doc) return 0

	if (activeResultTab.value === "matched") {
		return doc.total_matched || 0
	} else if (activeResultTab.value === "unmatched_a") {
		return doc.total_unmatched_source_a || 0
	} else if (activeResultTab.value === "unmatched_b") {
		return doc.total_unmatched_source_b || 0
	} else if (activeResultTab.value === "discrepancy") {
		return doc.total_amount_discrepancies || 0
	}
	// "all" tab
	return (
		(doc.total_matched || 0) +
		(doc.total_unmatched_source_a || 0) +
		(doc.total_unmatched_source_b || 0) +
		(doc.total_amount_discrepancies || 0)
	)
})

const resultsTotalPages = computed(() =>
	Math.ceil(filteredResultsTotal.value / resultsPageSize.value),
)

// Amount difference computed properties
const netDifference = computed(() => {
	if (!reconciliation.value) return 0
	return (
		(reconciliation.value.total_source_a_amount || 0) -
		(reconciliation.value.total_source_b_amount || 0)
	)
})

const matchRateColor = computed(() => {
	const rate = reconciliation.value?.match_percentage || 0
	if (rate >= 95) return "text-green-600"
	if (rate >= 80) return "text-yellow-600"
	return "text-red-600"
})

const matchRateBarColor = computed(() => {
	const rate = reconciliation.value?.match_percentage || 0
	if (rate >= 95) return "bg-green-500"
	if (rate >= 80) return "bg-yellow-500"
	return "bg-red-500"
})

// Close export dropdown on outside click
const handleClickOutside = (event) => {
	if (
		exportDropdownRef.value &&
		!exportDropdownRef.value.contains(event.target)
	) {
		showExportDropdown.value = false
	}
}

onMounted(async () => {
	document.addEventListener("click", handleClickOutside)
	if (!isNewMode.value) {
		await loadReconciliation()
	}
})

async function loadReconciliation() {
	loading.value = true
	try {
		const id = props.id || route.params.id
		await store.fetchReconciliation(id)
		reconciliation.value = store.activeReconciliation

		// Sync form with loaded data
		if (reconciliation.value) {
			form.value = {
				reconciliation_type: reconciliation.value.reconciliation_type,
				reconciliation_month: reconciliation.value.reconciliation_month,
				fiscal_year: reconciliation.value.fiscal_year,
				tolerance: reconciliation.value.tolerance || 0.01,
			}
		}

		// Load results if completed or reconciled
		if (
			reconciliation.value?.status === "Completed" ||
			reconciliation.value?.status === "Reconciled"
		) {
			await loadResults()
		}
	} catch (error) {
		console.error("Error loading reconciliation:", error)
	} finally {
		loading.value = false
	}
}

async function loadResults(filterStatus = null, pageNum = 1) {
	try {
		loadingResults.value = true
		console.log(
			"loadResults called with filterStatus:",
			filterStatus,
			"page:",
			pageNum,
		)
		console.log("reconciliation.name:", reconciliation.value?.name)

		// Map tab key to match_status value
		let statusFilter = null
		if (filterStatus === "matched") statusFilter = "Matched"
		else if (filterStatus === "unmatched_a") statusFilter = "Unmatched Source A"
		else if (filterStatus === "unmatched_b") statusFilter = "Unmatched Source B"
		else if (filterStatus === "discrepancy") statusFilter = "Amount Discrepancy"

		console.log("statusFilter:", statusFilter)

		const fetchResult = await store.fetchResults(
			reconciliation.value.name,
			statusFilter,
			pageNum,
		)
		console.log("store.fetchResults result:", fetchResult)

		reconciliationResults.value = store.reconciliationResults
		console.log(
			"reconciliationResults set to:",
			reconciliationResults.value.length,
			"items",
		)

		return fetchResult
	} catch (error) {
		console.error("Error loading results:", error)
	} finally {
		loadingResults.value = false
	}
}

async function createReconciliation() {
	if (
		!form.value.reconciliation_month ||
		!form.value.fiscal_year ||
		!form.value.reconciliation_type
	) {
		alert("Please fill in all required fields")
		return
	}

	saving.value = true
	try {
		const result = await store.createReconciliation({
			reconciliation_month: form.value.reconciliation_month,
			fiscal_year: form.value.fiscal_year,
			reconciliation_type: form.value.reconciliation_type,
			tolerance: form.value.tolerance || 0.01,
		})

		router.push(`/compliance/vat-reconciliation/${result.name}`)
	} catch (error) {
		console.error("Error creating reconciliation:", error)
		alert("Error creating reconciliation: " + error.message)
	} finally {
		saving.value = false
	}
}

function triggerFileInput(type) {
	if (type === "system") systemFileInput.value?.click()
	else if (type === "itax") itaxFileInput.value?.click()
	else if (type === "tims") timsFileInput.value?.click()
}

// CSV Template definitions - columns must match backend EXPECTED_HEADERS
const csvTemplates = {
	system: {
		filename: "system_data_template.csv",
		headers: [
			"posting_date",
			"invoice_number",
			"cu_invoice_number",
			"net_amount",
		],
		sampleData: [
			["2024-01-15", "INV-001", "CU123456789", "10000.00"],
			["2024-01-16", "INV-002", "CU123456790", "5000.00"],
			["2024-01-17", "INV-003", "CU123456791", "15000.00"],
		],
	},
	itax: {
		filename: "itax_data_template.csv",
		headers: ["posting_date", "cu_invoice_number", "amount"],
		sampleData: [
			["2024-01-15", "CU123456789", "10000.00"],
			["2024-01-16", "CU123456790", "5000.00"],
			["2024-01-17", "CU123456791", "15000.00"],
		],
	},
	tims: {
		filename: "tims_data_template.csv",
		headers: ["posting_date", "cu_invoice_number", "amount"],
		sampleData: [
			["2024-01-15", "CU123456789", "10000.00"],
			["2024-01-16", "CU123456790", "5000.00"],
			["2024-01-17", "CU123456791", "15000.00"],
		],
	},
}

function downloadTemplate(type) {
	const template = csvTemplates[type]
	if (!template) return

	// Create CSV content
	const rows = [template.headers, ...template.sampleData]
	const csvContent = rows.map((row) => row.join(",")).join("\n")

	// Create blob and download
	const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" })
	const link = document.createElement("a")
	const url = URL.createObjectURL(blob)

	link.setAttribute("href", url)
	link.setAttribute("download", template.filename)
	link.style.visibility = "hidden"
	document.body.appendChild(link)
	link.click()
	document.body.removeChild(link)
	URL.revokeObjectURL(url)
}

function downloadAllTemplates() {
	// Download all templates based on reconciliation type
	const type =
		reconciliation.value?.reconciliation_type || form.value.reconciliation_type

	if (requiresSystemData.value) downloadTemplate("system")
	setTimeout(() => {
		if (requiresItaxData.value) downloadTemplate("itax")
	}, 100)
	setTimeout(() => {
		if (requiresTimsData.value) downloadTemplate("tims")
	}, 200)
}

async function handleFileUpload(event, fileType) {
	const file = event.target.files[0]
	if (!file) return

	uploadingFile.value = fileType
	try {
		await store.uploadFile(reconciliation.value.name, fileType, file)
		await loadReconciliation()
	} catch (error) {
		console.error("Error uploading file:", error)
		alert("Error uploading file: " + error.message)
	} finally {
		uploadingFile.value = null
		// Reset file input
		event.target.value = ""
	}
}

async function runReconciliation() {
	runningReconciliation.value = true
	try {
		await store.runReconciliation(reconciliation.value.name)
		await loadReconciliation()
		await loadResults()
	} catch (error) {
		console.error("Error running reconciliation:", error)
		alert("Error running reconciliation: " + error.message)
	} finally {
		runningReconciliation.value = false
	}
}

async function exportReport(format) {
	showExportDropdown.value = false
	try {
		const result = await store.exportReport(reconciliation.value.name, format)

		if (result.file_url) {
			window.open(result.file_url, "_blank")
		}
	} catch (error) {
		console.error("Error exporting report:", error)
		alert("Error exporting report: " + error.message)
	}
}

async function viewFileData(fileType) {
	previewFileType.value = fileType.charAt(0).toUpperCase() + fileType.slice(1)

	// Fetch data from the appropriate child table
	try {
		let doctype = ""
		if (fileType === "system") doctype = "VAT System Data"
		else if (fileType === "itax") doctype = "VAT iTax Data"
		else if (fileType === "tims") doctype = "VAT TIMs Data"

		const result = await call("frappe.client.get_list", {
			doctype: doctype,
			filters: { parent: reconciliation.value.name },
			fields: ["*"],
			limit_page_length: 100,
		})

		if (result.length > 0) {
			previewColumns.value = Object.keys(result[0]).filter(
				(k) =>
					!k.startsWith("_") &&
					k !== "name" &&
					k !== "parent" &&
					k !== "parenttype" &&
					k !== "parentfield" &&
					k !== "docstatus" &&
					k !== "idx",
			)
			previewData.value = result
		}

		showFilePreview.value = true
	} catch (error) {
		console.error("Error loading file data:", error)
	}
}

async function fetchHistoricalComparison() {
	loadingHistorical.value = true
	try {
		await store.fetchHistoricalComparison(reconciliation.value.name)
		historicalComparison.value = store.historicalComparison
	} catch (error) {
		console.error("Error fetching historical comparison:", error)
	} finally {
		loadingHistorical.value = false
	}
}

function goBack() {
	router.push("/compliance/vat-reconciliation")
}

async function clearCacheAndReload() {
	// Clear the results cache
	store.clearResultsCache(reconciliation.value?.name)

	// Reload results if we have a completed reconciliation
	if (
		reconciliation.value?.status === "Completed" ||
		reconciliation.value?.status === "Reconciled"
	) {
		await loadResults()
	}
}

async function changePage(newPage) {
	resultsPage.value = newPage
	const filterStatus =
		activeResultTab.value === "all" ? null : activeResultTab.value
	await loadResults(filterStatus, newPage)
}

function getStatusVariant(status) {
	const variants = {
		Draft: "subtle",
		"Data Uploaded": "yellow",
		Reconciled: "blue",
		Reviewed: "purple",
		Approved: "green",
	}
	return variants[status] || "gray"
}

function getMatchStatusVariant(status) {
	const variants = {
		Matched: "green",
		"Unmatched Source A": "yellow",
		"Unmatched Source B": "orange",
		"Amount Discrepancy": "red",
	}
	return variants[status] || "gray"
}

function formatDate(date) {
	if (!date) return "-"
	return new Date(date).toLocaleDateString("en-US", {
		month: "short",
		day: "numeric",
		year: "numeric",
	})
}

function formatCurrency(amount) {
	if (amount === null || amount === undefined) return "-"
	return new Intl.NumberFormat("en-KE", {
		style: "currency",
		currency: "KES",
		minimumFractionDigits: 2,
	}).format(amount)
}

function formatVariance(variance) {
	if (variance === null || variance === undefined || variance === 0)
		return "KES 0.00"
	const absAmount = Math.abs(variance)
	const formatted = new Intl.NumberFormat("en-KE", {
		style: "currency",
		currency: "KES",
		minimumFractionDigits: 2,
	}).format(absAmount)
	return variance > 0 ? `+${formatted}` : `-${formatted}`
}

function getVarianceClass(variance, matchStatus) {
	if (variance === 0 || matchStatus === "Matched") return "text-green-600"
	if (variance > 0) return "text-orange-600" // Source A higher
	return "text-red-600" // Source B higher (negative variance)
}

function getVarianceTooltip(variance, matchStatus) {
	if (matchStatus === "Matched") return "Amounts match within tolerance"
	if (matchStatus === "Unmatched Source A") return "Only exists in Source A"
	if (matchStatus === "Unmatched Source B") return "Only exists in Source B"
	if (variance > 0)
		return "Source A amount is higher by " + formatCurrency(variance)
	if (variance < 0)
		return "Source B amount is higher by " + formatCurrency(Math.abs(variance))
	return ""
}

function getVATReconciliationContext() {
	return {
		reconciliation_name: reconciliation.value?.name,
		reconciliation_month: reconciliation.value?.reconciliation_month,
		fiscal_year: reconciliation.value?.fiscal_year,
		reconciliation_type: reconciliation.value?.reconciliation_type,
		status: reconciliation.value?.status,
		tolerance: reconciliation.value?.tolerance,
		match_percentage: reconciliation.value?.match_percentage,
		total_matched: reconciliation.value?.total_matched,
		total_unmatched_source_a: reconciliation.value?.total_unmatched_source_a,
		total_unmatched_source_b: reconciliation.value?.total_unmatched_source_b,
		total_amount_discrepancies: reconciliation.value?.total_amount_discrepancies,
		total_source_a_amount: reconciliation.value?.total_source_a_amount,
		total_source_b_amount: reconciliation.value?.total_source_b_amount,
		total_variance_amount: reconciliation.value?.total_variance_amount,
		system_records_count: reconciliation.value?.system_records_count,
		itax_records_count: reconciliation.value?.itax_records_count,
		tims_records_count: reconciliation.value?.tims_records_count,
		sample_discrepancies: reconciliationResults.value?.slice(0, 5).map(item => ({
			cu_invoice_number: item.cu_invoice_number,
			invoice_number: item.invoice_number,
			amount_a: item.amount_a,
			amount_b: item.amount_b,
			variance: item.variance,
			match_status: item.match_status
		}))
	}
}

function askAISpecialist() {
	// Collect current reconciliation context
	const context = {
		reconciliation_name: reconciliation.value.name,
		reconciliation_month: reconciliation.value.reconciliation_month,
		fiscal_year: reconciliation.value.fiscal_year,
		reconciliation_type: reconciliation.value.reconciliation_type,
		status: reconciliation.value.status,
		tolerance: reconciliation.value.tolerance,
		match_percentage: reconciliation.value.match_percentage,
		total_matched: reconciliation.value.total_matched,
		total_unmatched_source_a: reconciliation.value.total_unmatched_source_a,
		total_unmatched_source_b: reconciliation.value.total_unmatched_source_b,
		total_amount_discrepancies: reconciliation.value.total_amount_discrepancies,
		total_source_a_amount: reconciliation.value.total_source_a_amount,
		total_source_b_amount: reconciliation.value.total_source_b_amount,
		total_variance_amount: reconciliation.value.total_variance_amount,
		system_records_count: reconciliation.value.system_records_count,
		itax_records_count: reconciliation.value.itax_records_count,
		tims_records_count: reconciliation.value.tims_records_count,
		last_reconciled_at: reconciliation.value.last_reconciled_at,
		// Include summary of top discrepancies if available
		sample_discrepancies: reconciliationResults.value.slice(0, 5).map(item => ({
			cu_invoice_number: item.cu_invoice_number,
			invoice_number: item.invoice_number,
			amount_a: item.amount_a,
			amount_b: item.amount_b,
			variance: item.variance,
			match_status: item.match_status
		}))
	}

	// Store context in localStorage
	localStorage.setItem('vat_reconciliation_context', JSON.stringify(context))

	// Navigate to AI Specialist with context indicator
	router.push('/ai-specialist?context=vat_reconciliation')
}

// Watch for tab changes to reload results with new filter
watch(activeResultTab, async (newTab) => {
	resultsPage.value = 1
	if (reconciliation.value?.name) {
		await loadResults(newTab === "all" ? null : newTab, resultsPage.value)
	}
})
</script>
