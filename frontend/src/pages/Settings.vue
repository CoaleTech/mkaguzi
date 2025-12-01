<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">System Settings</h1>
        <p class="text-gray-600 mt-1">
          Configure audit system preferences, data imports, and compliance settings
        </p>
      </div>
      <div class="flex items-center space-x-3">
        <Button variant="outline">
          <DownloadIcon class="h-4 w-4 mr-2" />
          Export Settings
        </Button>
        <Button variant="outline">
          <UploadIcon class="h-4 w-4 mr-2" />
          Import Settings
        </Button>
      </div>
    </div>

    <!-- Settings Tabs -->
    <div class="bg-white rounded-lg border border-gray-200">
      <div class="border-b border-gray-200">
        <nav class="flex overflow-x-auto">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            :class="[
              'px-4 py-3 text-sm font-medium border-b-2 whitespace-nowrap transition-colors',
              activeTab === tab.id
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
            @click="activeTab = tab.id"
          >
            <component :is="tab.icon" class="h-4 w-4 mr-2 inline" />
            {{ tab.name }}
          </button>
        </nav>
      </div>

      <div class="p-6">
        <!-- Loading State -->
        <div v-if="loading" class="flex items-center justify-center py-12">
          <div class="text-center">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p class="mt-2 text-sm text-gray-600">Loading settings...</p>
          </div>
        </div>

        <!-- Settings Content -->
        <div v-else>
        <div v-if="activeTab === 'general'" class="space-y-6">
          <div>
            <h3 class="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <SettingsIcon class="h-5 w-5 mr-2" />
              General Settings
            </h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">System Name</label>
                  <Input
                    v-model="settings.systemName"
                    placeholder="Internal Audit Management System"
                    class="w-full"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Organization Name</label>
                  <Input
                    v-model="settings.organizationName"
                    placeholder="Your Organization Name"
                    class="w-full"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Default Date Format</label>
                  <Select
                    v-model="settings.dateFormat"
                    :options="dateFormatOptions"
                    class="w-full"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Timezone</label>
                  <Select
                    v-model="settings.timezone"
                    :options="timezoneOptions"
                    class="w-full"
                  />
                </div>
              </div>

              <div class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Audit Year Start</label>
                  <Select
                    v-model="settings.auditYearStart"
                    :options="monthOptions"
                    class="w-full"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Default Currency</label>
                  <Select
                    v-model="settings.currency"
                    :options="currencyOptions"
                    class="w-full"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Working Days</label>
                  <div class="flex flex-wrap gap-2">
                    <Checkbox
                      v-for="day in weekDays"
                      :key="day.value"
                      v-model="settings.workingDays"
                      :value="day.value"
                      :label="day.label"
                      class="text-sm"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Audit Settings -->
        <div v-if="activeTab === 'audit'" class="space-y-6">
          <div>
            <h3 class="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <FileCheckIcon class="h-5 w-5 mr-2" />
              Audit Configuration
            </h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Risk Assessment Thresholds</label>
                  <div class="space-y-2">
                    <div class="flex items-center justify-between">
                      <span class="text-sm text-gray-600">High Risk</span>
                      <Input
                        v-model="settings.riskThresholds.high"
                        type="number"
                        min="0"
                        max="100"
                        class="w-20"
                      />
                      <span class="text-sm text-gray-600">%</span>
                    </div>
                    <div class="flex items-center justify-between">
                      <span class="text-sm text-gray-600">Medium Risk</span>
                      <Input
                        v-model="settings.riskThresholds.medium"
                        type="number"
                        min="0"
                        max="100"
                        class="w-20"
                      />
                      <span class="text-sm text-gray-600">%</span>
                    </div>
                  </div>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Audit Planning Period</label>
                  <Select
                    v-model="settings.auditPlanningPeriod"
                    :options="planningPeriodOptions"
                    class="w-full"
                  />
                </div>

                <div class="flex items-center justify-between">
                  <div>
                    <label class="text-sm font-medium text-gray-700">Auto-assign Audit Tasks</label>
                    <p class="text-sm text-gray-500">Automatically assign tasks based on workload</p>
                  </div>
                  <Checkbox v-model="settings.autoAssignTasks" />
                </div>
              </div>

              <div class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Default Finding Severity</label>
                  <Select
                    v-model="settings.defaultFindingSeverity"
                    :options="severityOptions"
                    class="w-full"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Follow-up Reminder Days</label>
                  <Input
                    v-model="settings.followUpReminderDays"
                    type="number"
                    min="1"
                    max="365"
                    class="w-full"
                  />
                </div>

                <div class="flex items-center justify-between">
                  <div>
                    <label class="text-sm font-medium text-gray-700">Require Management Response</label>
                    <p class="text-sm text-gray-500">Management must respond to all findings</p>
                  </div>
                  <Checkbox v-model="settings.requireManagementResponse" />
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- AI Chat Settings -->
        <div v-if="activeTab === 'ai'" class="space-y-6">
          <div>
            <h3 class="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <BotIcon class="h-5 w-5 mr-2" />
              AI Chat Configuration
            </h3>
            <div class="space-y-6">
              <!-- OpenRouter API Settings -->
              <div class="p-4 border border-gray-200 rounded-lg bg-gray-50">
                <h4 class="text-md font-medium text-gray-900 mb-4">OpenRouter API</h4>
                <div class="space-y-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">API Key</label>
                    <div class="flex space-x-2">
                      <Input
                        :type="showApiKey ? 'text' : 'password'"
                        v-model="settings.openrouterApiKey"
                        placeholder="sk-or-v1-..."
                        class="flex-1"
                      />
                      <Button variant="outline" size="sm" @click="showApiKey = !showApiKey">
                        {{ showApiKey ? 'Hide' : 'Show' }}
                      </Button>
                      <Button variant="outline" size="sm" @click="testAiConnection" :loading="testingAi">
                        Test
                      </Button>
                    </div>
                    <p class="text-xs text-gray-500 mt-1">
                      Get your free API key from <a href="https://openrouter.ai" target="_blank" class="text-blue-600 hover:underline">openrouter.ai</a>
                    </p>
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">AI Model</label>
                    <Select
                      v-model="settings.selectedModel"
                      :options="aiModelOptions"
                      class="w-full"
                    />
                    <p class="text-xs text-gray-500 mt-1">Free tier models with good performance</p>
                  </div>

                  <div class="flex items-center justify-between">
                    <div>
                      <label class="text-sm font-medium text-gray-700">Enable AI Assistant</label>
                      <p class="text-sm text-gray-500">Allow AI-powered responses in chat rooms</p>
                    </div>
                    <Checkbox v-model="settings.enableAiAssistant" />
                  </div>
                </div>
              </div>

              <!-- RAG Settings -->
              <div class="p-4 border border-gray-200 rounded-lg">
                <h4 class="text-md font-medium text-gray-900 mb-4">RAG (Retrieval-Augmented Generation)</h4>
                <div class="space-y-4">
                  <div class="flex items-center justify-between">
                    <div>
                      <label class="text-sm font-medium text-gray-700">Enable RAG</label>
                      <p class="text-sm text-gray-500">Use audit documents as context for AI responses</p>
                    </div>
                    <Checkbox v-model="settings.ragEnabled" />
                  </div>

                  <div v-if="settings.ragEnabled" class="space-y-4 pl-4 border-l-2 border-blue-200">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-2">Max Context Chunks</label>
                      <Input
                        v-model="settings.maxContextChunks"
                        type="number"
                        min="1"
                        max="20"
                        class="w-32"
                      />
                      <p class="text-xs text-gray-500 mt-1">Number of relevant document sections to include</p>
                    </div>

                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-2">Embedding Model</label>
                      <Select
                        v-model="settings.embeddingModel"
                        :options="embeddingModelOptions"
                        class="w-full"
                      />
                    </div>
                  </div>
                </div>
              </div>

              <!-- Document Indexing -->
              <div class="p-4 border border-gray-200 rounded-lg">
                <h4 class="text-md font-medium text-gray-900 mb-4">Document Indexing</h4>
                <p class="text-sm text-gray-500 mb-4">Select which document types to index for AI context</p>
                <div class="grid grid-cols-2 gap-4">
                  <div class="flex items-center space-x-2">
                    <Checkbox v-model="settings.indexAuditFindings" />
                    <span class="text-sm text-gray-700">Audit Findings</span>
                  </div>
                  <div class="flex items-center space-x-2">
                    <Checkbox v-model="settings.indexWorkingPapers" />
                    <span class="text-sm text-gray-700">Working Papers</span>
                  </div>
                  <div class="flex items-center space-x-2">
                    <Checkbox v-model="settings.indexAuditPrograms" />
                    <span class="text-sm text-gray-700">Audit Programs</span>
                  </div>
                  <div class="flex items-center space-x-2">
                    <Checkbox v-model="settings.indexTestExecutions" />
                    <span class="text-sm text-gray-700">Test Executions</span>
                  </div>
                  <div class="flex items-center space-x-2">
                    <Checkbox v-model="settings.indexRiskAssessments" />
                    <span class="text-sm text-gray-700">Risk Assessments</span>
                  </div>
                  <div class="flex items-center space-x-2">
                    <Checkbox v-model="settings.indexComplianceRequirements" />
                    <span class="text-sm text-gray-700">Compliance Requirements</span>
                  </div>
                </div>

                <div class="mt-4 pt-4 border-t border-gray-200">
                  <div class="flex items-center justify-between">
                    <div>
                      <p class="text-sm font-medium text-gray-700">Index Statistics</p>
                      <p class="text-xs text-gray-500">{{ indexStats.totalDocuments || 0 }} documents indexed</p>
                    </div>
                    <Button variant="outline" size="sm" @click="rebuildIndex" :loading="rebuildingIndex">
                      Rebuild Index
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Data Import Settings -->
        <div v-if="activeTab === 'data-import'" class="space-y-6">
          <div>
            <h3 class="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <DatabaseIcon class="h-5 w-5 mr-2" />
              Data Import Configuration
            </h3>
            <div class="space-y-6">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="space-y-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Default Import Type</label>
                    <Select
                      v-model="settings.defaultImportType"
                      :options="importTypeOptions"
                      class="w-full"
                    />
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">CSV Delimiter</label>
                    <Select
                      v-model="settings.csvDelimiter"
                      :options="delimiterOptions"
                      class="w-full"
                    />
                  </div>

                  <div class="flex items-center justify-between">
                    <div>
                      <label class="text-sm font-medium text-gray-700">Auto-detect Encoding</label>
                      <p class="text-sm text-gray-500">Automatically detect file encoding</p>
                    </div>
                    <Checkbox v-model="settings.autoDetectEncoding" />
                  </div>
                </div>

                <div class="space-y-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Max File Size (MB)</label>
                    <Input
                      v-model="settings.maxFileSize"
                      type="number"
                      min="1"
                      max="100"
                      class="w-full"
                    />
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Import Batch Size</label>
                    <Input
                      v-model="settings.importBatchSize"
                      type="number"
                      min="100"
                      max="10000"
                      class="w-full"
                    />
                  </div>

                  <div class="flex items-center justify-between">
                    <div>
                      <label class="text-sm font-medium text-gray-700">Validate Data on Import</label>
                      <p class="text-sm text-gray-500">Perform data validation during import</p>
                    </div>
                    <Checkbox v-model="settings.validateOnImport" />
                  </div>
                </div>
              </div>

              <!-- Business Central Integration -->
              <div class="border-t pt-6">
                <h4 class="text-md font-medium text-gray-900 mb-4">Business Central Integration</h4>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div class="space-y-4">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-2">BC API Endpoint</label>
                      <Input
                        v-model="settings.bcApiEndpoint"
                        placeholder="https://api.businesscentral.dynamics.com"
                        class="w-full"
                      />
                    </div>

                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-2">Company Name</label>
                      <Input
                        v-model="settings.bcCompanyName"
                        placeholder="CRONUS International Ltd."
                        class="w-full"
                      />
                    </div>
                  </div>

                  <div class="space-y-4">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-2">Sync Frequency</label>
                      <Select
                        v-model="settings.bcSyncFrequency"
                        :options="syncFrequencyOptions"
                        class="w-full"
                      />
                    </div>

                    <div class="flex items-center justify-between">
                      <div>
                        <label class="text-sm font-medium text-gray-700">Auto-sync Enabled</label>
                        <p class="text-sm text-gray-500">Automatically sync data from BC</p>
                      </div>
                      <Checkbox v-model="settings.bcAutoSync" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Compliance Settings -->
        <div v-if="activeTab === 'compliance'" class="space-y-6">
          <div>
            <h3 class="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <ShieldCheckIcon class="h-5 w-5 mr-2" />
              Compliance Settings
            </h3>
            <div class="space-y-6">
              <!-- Kenyan Regulatory Bodies -->
              <div>
                <h4 class="text-md font-medium text-gray-900 mb-4">Kenyan Regulatory Bodies</h4>
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  <div
                    v-for="body in kenyanRegulatoryBodies"
                    :key="body.id"
                    class="flex items-center justify-between p-3 border border-gray-200 rounded-lg"
                  >
                    <div class="flex items-center space-x-3">
                      <div class="p-2 bg-blue-100 rounded-lg">
                        <component :is="body.icon" class="h-4 w-4 text-blue-600" />
                      </div>
                      <div>
                        <p class="text-sm font-medium text-gray-900">{{ body.name }}</p>
                        <p class="text-xs text-gray-500">{{ body.description }}</p>
                      </div>
                    </div>
                    <Checkbox v-model="settings.enabledRegulatoryBodies" :value="body.id" />
                  </div>
                </div>
              </div>

              <!-- Compliance Periods -->
              <div class="border-t pt-6">
                <h4 class="text-md font-medium text-gray-900 mb-4">Compliance Periods</h4>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Tax Filing Period</label>
                    <Select
                      v-model="settings.taxFilingPeriod"
                      :options="compliancePeriodOptions"
                      class="w-full"
                    />
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Audit Report Period</label>
                    <Select
                      v-model="settings.auditReportPeriod"
                      :options="compliancePeriodOptions"
                      class="w-full"
                    />
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Compliance Review Period</label>
                    <Select
                      v-model="settings.complianceReviewPeriod"
                      :options="compliancePeriodOptions"
                      class="w-full"
                    />
                  </div>
                </div>
              </div>

              <!-- Alert Settings -->
              <div class="border-t pt-6">
                <h4 class="text-md font-medium text-gray-900 mb-4">Compliance Alerts</h4>
                <div class="space-y-4">
                  <div class="flex items-center justify-between">
                    <div>
                      <label class="text-sm font-medium text-gray-700">Deadline Alerts</label>
                      <p class="text-sm text-gray-500">Send alerts before compliance deadlines</p>
                    </div>
                    <div class="flex items-center space-x-2">
                      <Checkbox v-model="settings.deadlineAlerts" />
                      <Input
                        v-if="settings.deadlineAlerts"
                        v-model="settings.deadlineAlertDays"
                        type="number"
                        min="1"
                        max="30"
                        class="w-16"
                        placeholder="7"
                      />
                      <span v-if="settings.deadlineAlerts" class="text-sm text-gray-600">days before</span>
                    </div>
                  </div>

                  <div class="flex items-center justify-between">
                    <div>
                      <label class="text-sm font-medium text-gray-700">Violation Alerts</label>
                      <p class="text-sm text-gray-500">Alert on compliance violations</p>
                    </div>
                    <Checkbox v-model="settings.violationAlerts" />
                  </div>

                  <div class="flex items-center justify-between">
                    <div>
                      <label class="text-sm font-medium text-gray-700">Escalation Alerts</label>
                      <p class="text-sm text-gray-500">Escalate unresolved compliance issues</p>
                    </div>
                    <Checkbox v-model="settings.escalationAlerts" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- User Preferences -->
        <div v-if="activeTab === 'preferences'" class="space-y-6">
          <div>
            <h3 class="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <UserIcon class="h-5 w-5 mr-2" />
              User Preferences
            </h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Theme</label>
                  <Select
                    v-model="settings.theme"
                    :options="themeOptions"
                    class="w-full"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Language</label>
                  <Select
                    v-model="settings.language"
                    :options="languageOptions"
                    class="w-full"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Dashboard Layout</label>
                  <Select
                    v-model="settings.dashboardLayout"
                    :options="dashboardLayoutOptions"
                    class="w-full"
                  />
                </div>
              </div>

              <div class="space-y-4">
                <div class="flex items-center justify-between">
                  <div>
                    <label class="text-sm font-medium text-gray-700">Email Notifications</label>
                    <p class="text-sm text-gray-500">Receive email notifications</p>
                  </div>
                  <Checkbox v-model="settings.emailNotifications" />
                </div>

                <div class="flex items-center justify-between">
                  <div>
                    <label class="text-sm font-medium text-gray-700">Push Notifications</label>
                    <p class="text-sm text-gray-500">Receive browser push notifications</p>
                  </div>
                  <Checkbox v-model="settings.pushNotifications" />
                </div>

                <div class="flex items-center justify-between">
                  <div>
                    <label class="text-sm font-medium text-gray-700">Auto-save</label>
                    <p class="text-sm text-gray-500">Automatically save changes</p>
                  </div>
                  <Checkbox v-model="settings.autoSave" />
                </div>

                <div class="flex items-center justify-between">
                  <div>
                    <label class="text-sm font-medium text-gray-700">Compact Mode</label>
                    <p class="text-sm text-gray-500">Use compact UI elements</p>
                  </div>
                  <Checkbox v-model="settings.compactMode" />
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Security Settings -->
        <div v-if="activeTab === 'security'" class="space-y-6">
          <div>
            <h3 class="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <ShieldIcon class="h-5 w-5 mr-2" />
              Security Settings
            </h3>
            <div class="space-y-6">
              <!-- Authentication -->
              <div>
                <h4 class="text-md font-medium text-gray-900 mb-4">Authentication</h4>
                <div class="space-y-4">
                  <div class="flex items-center justify-between">
                    <div>
                      <label class="text-sm font-medium text-gray-700">Two-Factor Authentication</label>
                      <p class="text-sm text-gray-500">Enable 2FA for enhanced security</p>
                    </div>
                    <div class="flex items-center space-x-2">
                      <Badge :variant="settings.twoFactorEnabled ? 'success' : 'secondary'">
                        {{ settings.twoFactorEnabled ? 'Enabled' : 'Disabled' }}
                      </Badge>
                      <Button
                        variant="outline"
                        size="sm"
                        @click="toggleTwoFactor"
                      >
                        {{ settings.twoFactorEnabled ? 'Disable' : 'Enable' }}
                      </Button>
                    </div>
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Session Timeout</label>
                    <Select
                      v-model="settings.sessionTimeout"
                      :options="sessionTimeoutOptions"
                      class="w-full md:w-64"
                    />
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Password Policy</label>
                    <div class="space-y-2">
                      <div class="flex items-center justify-between">
                        <span class="text-sm text-gray-600">Minimum Length</span>
                        <Input
                          v-model="settings.passwordPolicy.minLength"
                          type="number"
                          min="8"
                          max="32"
                          class="w-20"
                        />
                      </div>
                      <div class="flex items-center space-x-2">
                        <Checkbox v-model="settings.passwordPolicy.requireUppercase" />
                        <span class="text-sm text-gray-600">Require uppercase</span>
                      </div>
                      <div class="flex items-center space-x-2">
                        <Checkbox v-model="settings.passwordPolicy.requireNumbers" />
                        <span class="text-sm text-gray-600">Require numbers</span>
                      </div>
                      <div class="flex items-center space-x-2">
                        <Checkbox v-model="settings.passwordPolicy.requireSpecialChars" />
                        <span class="text-sm text-gray-600">Require special characters</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Data Security -->
              <div class="border-t pt-6">
                <h4 class="text-md font-medium text-gray-900 mb-4">Data Security</h4>
                <div class="space-y-4">
                  <div class="flex items-center justify-between">
                    <div>
                      <label class="text-sm font-medium text-gray-700">Audit Data Encryption</label>
                      <p class="text-sm text-gray-500">Encrypt sensitive audit data at rest</p>
                    </div>
                    <Checkbox v-model="settings.auditDataEncryption" />
                  </div>

                  <div class="flex items-center justify-between">
                    <div>
                      <label class="text-sm font-medium text-gray-700">Data Retention Policy</label>
                      <p class="text-sm text-gray-500">Automatically delete old audit data</p>
                    </div>
                    <div class="flex items-center space-x-2">
                      <Checkbox v-model="settings.dataRetentionEnabled" />
                      <Input
                        v-if="settings.dataRetentionEnabled"
                        v-model="settings.dataRetentionYears"
                        type="number"
                        min="1"
                        max="10"
                        class="w-16"
                        placeholder="7"
                      />
                      <span v-if="settings.dataRetentionEnabled" class="text-sm text-gray-600">years</span>
                    </div>
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Access Logging</label>
                    <Select
                      v-model="settings.accessLogging"
                      :options="accessLoggingOptions"
                      class="w-full md:w-64"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Integrations -->
        <div v-if="activeTab === 'integrations'" class="space-y-6">
          <div>
            <h3 class="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <LinkIcon class="h-5 w-5 mr-2" />
              Integrations
            </h3>
            <div class="space-y-4">
              <!-- Business Central -->
              <div class="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                <div class="flex items-center space-x-3">
                  <div class="p-2 bg-blue-100 rounded-lg">
                    <DatabaseIcon class="h-5 w-5 text-blue-600" />
                  </div>
                  <div>
                    <h4 class="text-sm font-medium text-gray-900">Microsoft Business Central</h4>
                    <p class="text-sm text-gray-500">Connect to Dynamics 365 Business Central for financial data</p>
                  </div>
                </div>
                <div class="flex items-center space-x-2">
                  <Badge :variant="settings.bcIntegration ? 'success' : 'secondary'">
                    {{ settings.bcIntegration ? 'Connected' : 'Disconnected' }}
                  </Badge>
                  <Button
                    variant="outline"
                    size="sm"
                    @click="toggleBCIntegration"
                  >
                    {{ settings.bcIntegration ? 'Disconnect' : 'Connect' }}
                  </Button>
                </div>
              </div>

              <!-- Email Service -->
              <div class="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                <div class="flex items-center space-x-3">
                  <div class="p-2 bg-green-100 rounded-lg">
                    <MailIcon class="h-5 w-5 text-green-600" />
                  </div>
                  <div>
                    <h4 class="text-sm font-medium text-gray-900">Email Service</h4>
                    <p class="text-sm text-gray-500">Configure email notifications and reports</p>
                  </div>
                </div>
                <Button variant="outline" size="sm">
                  Configure
                </Button>
              </div>

              <!-- Cloud Storage -->
              <div class="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                <div class="flex items-center space-x-3">
                  <div class="p-2 bg-purple-100 rounded-lg">
                    <CloudIcon class="h-5 w-5 text-purple-600" />
                  </div>
                  <div>
                    <h4 class="text-sm font-medium text-gray-900">Cloud Storage</h4>
                    <p class="text-sm text-gray-500">Store audit files and backups in the cloud</p>
                  </div>
                </div>
                <Button variant="outline" size="sm">
                  Configure
                </Button>
              </div>

              <!-- API Access -->
              <div class="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                <div class="flex items-center space-x-3">
                  <div class="p-2 bg-orange-100 rounded-lg">
                    <CodeIcon class="h-5 w-5 text-orange-600" />
                  </div>
                  <div>
                    <h4 class="text-sm font-medium text-gray-900">API Access</h4>
                    <p class="text-sm text-gray-500">Enable API access for external integrations</p>
                  </div>
                </div>
                <div class="flex items-center space-x-2">
                  <Badge :variant="settings.apiAccess ? 'success' : 'secondary'">
                    {{ settings.apiAccess ? 'Enabled' : 'Disabled' }}
                  </Badge>
                  <Button
                    variant="outline"
                    size="sm"
                    @click="toggleApiAccess"
                  >
                    {{ settings.apiAccess ? 'Disable' : 'Enable' }}
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Reports Settings -->
        <div v-if="activeTab === 'reports'" class="space-y-6">
          <div>
            <h3 class="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <BarChart3Icon class="h-5 w-5 mr-2" />
              Reports & Analytics
            </h3>
            <div class="space-y-6">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="space-y-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Default Report Format</label>
                    <Select
                      v-model="settings.defaultReportFormat"
                      :options="reportFormatOptions"
                      class="w-full"
                    />
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Chart Library</label>
                    <Select
                      v-model="settings.chartLibrary"
                      :options="chartLibraryOptions"
                      class="w-full"
                    />
                  </div>

                  <div class="flex items-center justify-between">
                    <div>
                      <label class="text-sm font-medium text-gray-700">Auto-generate Reports</label>
                      <p class="text-sm text-gray-500">Automatically generate periodic reports</p>
                    </div>
                    <Checkbox v-model="settings.autoGenerateReports" />
                  </div>
                </div>

                <div class="space-y-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Report Retention Period</label>
                    <Select
                      v-model="settings.reportRetentionPeriod"
                      :options="retentionPeriodOptions"
                      class="w-full"
                    />
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Dashboard Refresh Rate</label>
                    <Select
                      v-model="settings.dashboardRefreshRate"
                      :options="refreshRateOptions"
                      class="w-full"
                    />
                  </div>

                  <div class="flex items-center justify-between">
                    <div>
                      <label class="text-sm font-medium text-gray-700">Export Raw Data</label>
                      <p class="text-sm text-gray-500">Allow exporting raw audit data</p>
                    </div>
                    <Checkbox v-model="settings.exportRawData" />
                  </div>
                </div>
              </div>

              <!-- Report Templates -->
              <div class="border-t pt-6">
                <h4 class="text-md font-medium text-gray-900 mb-4">Report Templates</h4>
                <div class="space-y-3">
                  <div
                    v-for="template in reportTemplates"
                    :key="template.id"
                    class="flex items-center justify-between p-3 border border-gray-200 rounded-lg"
                  >
                    <div class="flex items-center space-x-3">
                      <component :is="template.icon" class="h-4 w-4 text-gray-600" />
                      <div>
                        <p class="text-sm font-medium text-gray-900">{{ template.name }}</p>
                        <p class="text-xs text-gray-500">{{ template.description }}</p>
                      </div>
                    </div>
                    <div class="flex items-center space-x-2">
                      <Badge :variant="template.enabled ? 'success' : 'secondary'" size="sm">
                        {{ template.enabled ? 'Enabled' : 'Disabled' }}
                      </Badge>
                      <Button variant="ghost" size="sm">
                        Configure
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <!-- End of settings content -->
        </div>
      </div>

      <!-- Save Button -->
      <div class="px-6 py-4 border-t border-gray-200 bg-gray-50">
        <div class="flex justify-between items-center">
          <div class="text-sm text-gray-600">
            Last updated: {{ formatDate(settings.lastUpdated) }}
          </div>
          <div class="flex space-x-3">
            <Button variant="outline" @click="resetToDefaults">
              Reset to Defaults
            </Button>
            <Button @click="saveSettings" :loading="saving">
              <SaveIcon class="h-4 w-4 mr-2" />
              Save Changes
            </Button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Badge, Button, Checkbox, Input, Select, call } from "frappe-ui"
import {
	BarChart3Icon,
	BotIcon,
	CloudIcon,
	CodeIcon,
	DatabaseIcon,
	DownloadIcon,
	FileCheckIcon,
	LinkIcon,
	MailIcon,
	SaveIcon,
	SettingsIcon,
	ShieldCheckIcon,
	ShieldIcon,
	UploadIcon,
	UserIcon,
} from "lucide-vue-next"
import { onMounted, ref } from "vue"

// Props
const props = defineProps({
	defaultTab: {
		type: String,
		default: "general",
	},
})

// Reactive state
const activeTab = ref(props.defaultTab)
const saving = ref(false)
const showApiKey = ref(false)
const testingAi = ref(false)
const rebuildingIndex = ref(false)
const indexStats = ref({ totalDocuments: 0 })
const loading = ref(true)

const settings = ref({
	// General Settings
	systemName: "Internal Audit Management System",
	organizationName: "",
	dateFormat: "MM/dd/yyyy",
	timezone: "UTC",
	auditYearStart: "January",
	currency: "KES",
	workingDays: ["monday", "tuesday", "wednesday", "thursday", "friday"],

	// Audit Settings
	riskThresholds: {
		high: 80,
		medium: 50,
	},
	auditPlanningPeriod: "quarterly",
	autoAssignTasks: false,
	defaultFindingSeverity: "medium",
	followUpReminderDays: 30,
	requireManagementResponse: true,

	// AI Chat Settings
	openrouterApiKey: "",
	selectedModel: "meta-llama/llama-3.1-8b-instruct:free",
	enableAiAssistant: true,
	ragEnabled: true,
	maxContextChunks: 5,
	embeddingModel: "all-MiniLM-L6-v2",
	indexAuditFindings: true,
	indexWorkingPapers: true,
	indexAuditPrograms: true,
	indexTestExecutions: true,
	indexRiskAssessments: true,
	indexComplianceRequirements: true,

	// Data Import Settings
	defaultImportType: "csv",
	csvDelimiter: ",",
	autoDetectEncoding: true,
	maxFileSize: 50,
	importBatchSize: 1000,
	validateOnImport: true,
	bcApiEndpoint: "",
	bcCompanyName: "",
	bcSyncFrequency: "daily",
	bcAutoSync: false,

	// Compliance Settings
	enabledRegulatoryBodies: ["kra", "cmak"],
	taxFilingPeriod: "annually",
	auditReportPeriod: "annually",
	complianceReviewPeriod: "quarterly",
	deadlineAlerts: true,
	deadlineAlertDays: 7,
	violationAlerts: true,
	escalationAlerts: true,

	// User Preferences
	theme: "light",
	language: "en",
	dashboardLayout: "grid",
	emailNotifications: true,
	pushNotifications: false,
	autoSave: true,
	compactMode: false,

	// Security Settings
	twoFactorEnabled: false,
	sessionTimeout: "30",
	passwordPolicy: {
		minLength: 8,
		requireUppercase: true,
		requireNumbers: true,
		requireSpecialChars: false,
	},
	auditDataEncryption: true,
	dataRetentionEnabled: true,
	dataRetentionYears: 7,
	accessLogging: "detailed",

	// Integration Settings
	bcIntegration: false,
	apiAccess: false,

	// Reports Settings
	defaultReportFormat: "pdf",
	chartLibrary: "chartjs",
	autoGenerateReports: false,
	reportRetentionPeriod: "1year",
	dashboardRefreshRate: "5min",
	exportRawData: false,

	// Metadata
	lastUpdated: new Date().toISOString(),
})

// Constants
const tabs = [
	{ id: "general", name: "General", icon: SettingsIcon },
	{ id: "audit", name: "Audit", icon: FileCheckIcon },
	{ id: "ai", name: "AI Chat", icon: BotIcon },
	{ id: "data-import", name: "Data Import", icon: DatabaseIcon },
	{ id: "compliance", name: "Compliance", icon: ShieldCheckIcon },
	{ id: "preferences", name: "Preferences", icon: UserIcon },
	{ id: "security", name: "Security", icon: ShieldIcon },
	{ id: "integrations", name: "Integrations", icon: LinkIcon },
	{ id: "reports", name: "Reports", icon: BarChart3Icon },
]

const dateFormatOptions = [
	{ label: "MM/DD/YYYY", value: "MM/dd/yyyy" },
	{ label: "DD/MM/YYYY", value: "dd/MM/yyyy" },
	{ label: "YYYY-MM-DD", value: "yyyy-MM-dd" },
]

const timezoneOptions = [
	{ label: "UTC", value: "UTC" },
	{ label: "EAT (UTC+3)", value: "EAT" },
	{ label: "EST (UTC-5)", value: "EST" },
	{ label: "PST (UTC-8)", value: "PST" },
	{ label: "GMT", value: "GMT" },
]

const monthOptions = [
	{ label: "January", value: "January" },
	{ label: "February", value: "February" },
	{ label: "March", value: "March" },
	{ label: "April", value: "April" },
	{ label: "May", value: "May" },
	{ label: "June", value: "June" },
	{ label: "July", value: "July" },
	{ label: "August", value: "August" },
	{ label: "September", value: "September" },
	{ label: "October", value: "October" },
	{ label: "November", value: "November" },
	{ label: "December", value: "December" },
]

const currencyOptions = [
	{ label: "Kenyan Shilling (KES)", value: "KES" },
	{ label: "US Dollar (USD)", value: "USD" },
	{ label: "Euro (EUR)", value: "EUR" },
	{ label: "British Pound (GBP)", value: "GBP" },
]

const weekDays = [
	{ value: "monday", label: "Mon" },
	{ value: "tuesday", label: "Tue" },
	{ value: "wednesday", label: "Wed" },
	{ value: "thursday", label: "Thu" },
	{ value: "friday", label: "Fri" },
	{ value: "saturday", label: "Sat" },
	{ value: "sunday", label: "Sun" },
]

const planningPeriodOptions = [
	{ label: "Monthly", value: "monthly" },
	{ label: "Quarterly", value: "quarterly" },
	{ label: "Semi-annually", value: "semi-annual" },
	{ label: "Annually", value: "annually" },
]

const severityOptions = [
	{ label: "Low", value: "low" },
	{ label: "Medium", value: "medium" },
	{ label: "High", value: "high" },
	{ label: "Critical", value: "critical" },
]

const aiModelOptions = [
	{
		label: "Llama 3.1 8B (Free)",
		value: "meta-llama/llama-3.1-8b-instruct:free",
	},
	{ label: "Gemma 2 9B (Free)", value: "google/gemma-2-9b-it:free" },
	{ label: "Qwen 2.5 7B (Free)", value: "qwen/qwen-2.5-7b-instruct:free" },
]

const embeddingModelOptions = [
	{ label: "all-MiniLM-L6-v2 (Recommended)", value: "all-MiniLM-L6-v2" },
	{ label: "all-mpnet-base-v2 (Higher quality)", value: "all-mpnet-base-v2" },
]

const importTypeOptions = [
	{ label: "CSV", value: "csv" },
	{ label: "Excel", value: "excel" },
	{ label: "JSON", value: "json" },
	{ label: "XML", value: "xml" },
]

const delimiterOptions = [
	{ label: "Comma (,)", value: "," },
	{ label: "Semicolon (;)", value: ";" },
	{ label: "Tab", value: "\t" },
	{ label: "Pipe (|)", value: "|" },
]

const syncFrequencyOptions = [
	{ label: "Real-time", value: "realtime" },
	{ label: "Hourly", value: "hourly" },
	{ label: "Daily", value: "daily" },
	{ label: "Weekly", value: "weekly" },
]

const kenyanRegulatoryBodies = [
	{
		id: "kra",
		name: "Kenya Revenue Authority",
		description: "Tax collection and administration",
		icon: ShieldCheckIcon,
	},
	{
		id: "cmak",
		name: "CMA Kenya",
		description: "Capital Markets Authority",
		icon: ShieldCheckIcon,
	},
	{
		id: "cbk",
		name: "Central Bank of Kenya",
		description: "Financial sector regulation",
		icon: ShieldCheckIcon,
	},
	{
		id: "ira",
		name: "Insurance Regulatory Authority",
		description: "Insurance sector oversight",
		icon: ShieldCheckIcon,
	},
	{
		id: "rba",
		name: "Retirement Benefits Authority",
		description: "Pension schemes regulation",
		icon: ShieldCheckIcon,
	},
	{
		id: "ppra",
		name: "Public Procurement Regulatory Authority",
		description: "Public procurement oversight",
		icon: ShieldCheckIcon,
	},
]

const compliancePeriodOptions = [
	{ label: "Monthly", value: "monthly" },
	{ label: "Quarterly", value: "quarterly" },
	{ label: "Semi-annually", value: "semi-annual" },
	{ label: "Annually", value: "annually" },
]

const themeOptions = [
	{ label: "Light", value: "light" },
	{ label: "Dark", value: "dark" },
	{ label: "Auto", value: "auto" },
]

const languageOptions = [
	{ label: "English", value: "en" },
	{ label: "Swahili", value: "sw" },
	{ label: "Spanish", value: "es" },
	{ label: "French", value: "fr" },
]

const dashboardLayoutOptions = [
	{ label: "Grid", value: "grid" },
	{ label: "List", value: "list" },
	{ label: "Cards", value: "cards" },
]

const sessionTimeoutOptions = [
	{ label: "15 minutes", value: "15" },
	{ label: "30 minutes", value: "30" },
	{ label: "1 hour", value: "60" },
	{ label: "4 hours", value: "240" },
	{ label: "8 hours", value: "480" },
]

const accessLoggingOptions = [
	{ label: "None", value: "none" },
	{ label: "Basic", value: "basic" },
	{ label: "Detailed", value: "detailed" },
	{ label: "Full Audit", value: "full" },
]

const reportFormatOptions = [
	{ label: "PDF", value: "pdf" },
	{ label: "Excel", value: "excel" },
	{ label: "Word", value: "word" },
	{ label: "HTML", value: "html" },
]

const chartLibraryOptions = [
	{ label: "Chart.js", value: "chartjs" },
	{ label: "D3.js", value: "d3" },
	{ label: "Highcharts", value: "highcharts" },
]

const retentionPeriodOptions = [
	{ label: "6 months", value: "6months" },
	{ label: "1 year", value: "1year" },
	{ label: "2 years", value: "2years" },
	{ label: "5 years", value: "5years" },
	{ label: "10 years", value: "10years" },
]

const refreshRateOptions = [
	{ label: "30 seconds", value: "30sec" },
	{ label: "1 minute", value: "1min" },
	{ label: "5 minutes", value: "5min" },
	{ label: "15 minutes", value: "15min" },
	{ label: "1 hour", value: "1hour" },
]

const reportTemplates = [
	{
		id: "audit-summary",
		name: "Audit Summary Report",
		description: "Comprehensive audit findings and recommendations",
		icon: FileCheckIcon,
		enabled: true,
	},
	{
		id: "compliance-status",
		name: "Compliance Status Report",
		description: "Regulatory compliance status and gaps",
		icon: ShieldCheckIcon,
		enabled: true,
	},
	{
		id: "risk-assessment",
		name: "Risk Assessment Report",
		description: "Risk analysis and mitigation strategies",
		icon: BarChart3Icon,
		enabled: true,
	},
	{
		id: "financial-audit",
		name: "Financial Audit Report",
		description: "Financial controls and transaction reviews",
		icon: DatabaseIcon,
		enabled: false,
	},
]

// Load settings on component mount
onMounted(async () => {
	await loadSettings()
})

// Methods
const loadSettings = async () => {
	try {
		loading.value = true
		const response = await call("mkaguzi.api.chat.get_chat_settings")

		// Update settings with backend data
		if (response) {
			// Map backend field names to frontend field names
			settings.value.enableAiAssistant = response.enable_ai_chat || false
			settings.value.openrouterApiKey = response.openrouter_api_key || ""
			settings.value.selectedModel =
				response.default_model || "meta-llama/llama-3.1-8b-instruct:free"
			settings.value.ragEnabled = response.enable_rag || false
			settings.value.maxContextChunks = response.max_context_chunks || 5
			settings.value.embeddingModel =
				response.embedding_model || "all-MiniLM-L6-v2"
			settings.value.indexAuditFindings = response.index_audit_findings || false
			settings.value.indexWorkingPapers = response.index_working_papers || false
			settings.value.indexAuditPrograms = response.index_audit_programs || false
			settings.value.indexTestExecutions =
				response.index_test_executions || false
			settings.value.indexRiskAssessments =
				response.index_risk_assessments || false
			settings.value.indexComplianceRequirements =
				response.index_compliance_requirements || false
			settings.value.lastUpdated = response.modified || new Date().toISOString()
		}
	} catch (error) {
		console.error("Error loading settings:", error)
		// Keep default values if loading fails
	} finally {
		loading.value = false
	}
}
const toggleTwoFactor = () => {
	settings.value.twoFactorEnabled = !settings.value.twoFactorEnabled
}

const toggleBCIntegration = () => {
	settings.value.bcIntegration = !settings.value.bcIntegration
}

const toggleApiAccess = () => {
	settings.value.apiAccess = !settings.value.apiAccess
}

const testAiConnection = async () => {
	if (!settings.value.openrouterApiKey) {
		alert("Please enter an API key first")
		return
	}

	testingAi.value = true
	try {
		// First save the API key to backend
		await saveChatSettings()

		// Then test the connection
		const response = await call("mkaguzi.api.chat.test_ai_connection")

		if (response?.success) {
			alert(
				"✅ AI connection successful! Available models: " +
					(response.free_models_count || 0),
			)
		} else {
			alert("❌ Connection failed: " + (response?.error || "Unknown error"))
		}
	} catch (error) {
		alert("❌ Connection test failed: " + error.message)
	} finally {
		testingAi.value = false
	}
}

const rebuildIndex = async () => {
	if (
		!confirm(
			"This will rebuild the entire RAG index. This may take a few minutes. Continue?",
		)
	) {
		return
	}

	rebuildingIndex.value = true
	try {
		await call("mkaguzi.chat_system.chat_service.rebuild_rag_index")

		// Refresh stats
		const statsResponse = await call("mkaguzi.api.chat.get_index_stats")
		if (statsResponse) {
			indexStats.value = statsResponse
		}

		alert("✅ Index rebuilt successfully!")
	} catch (error) {
		alert("❌ Index rebuild failed: " + error.message)
	} finally {
		rebuildingIndex.value = false
	}
}

const saveChatSettings = async () => {
	const chatSettings = {
		enable_ai_chat: settings.value.enableAiAssistant,
		openrouter_api_key: settings.value.openrouterApiKey,
		default_model: settings.value.selectedModel,
		enable_rag: settings.value.ragEnabled,
		max_context_chunks: settings.value.maxContextChunks,
		embedding_model: settings.value.embeddingModel,
		index_audit_findings: settings.value.indexAuditFindings,
		index_working_papers: settings.value.indexWorkingPapers,
		index_audit_programs: settings.value.indexAuditPrograms,
		index_test_executions: settings.value.indexTestExecutions,
		index_risk_assessments: settings.value.indexRiskAssessments,
		index_compliance_requirements: settings.value.indexComplianceRequirements,
	}

	return await call("mkaguzi.api.chat.save_chat_settings", {
		settings_data: chatSettings,
	})
}

const saveSettings = async () => {
	saving.value = true
	try {
		// Update last updated timestamp
		settings.value.lastUpdated = new Date().toISOString()

		// Save chat settings to backend
		await saveChatSettings()

		// Show success message
		alert("Settings saved successfully!")
	} catch (error) {
		console.error("Error saving settings:", error)
		alert("Error saving settings. Please try again.")
	} finally {
		saving.value = false
	}
}

const resetToDefaults = () => {
	if (
		confirm(
			"Are you sure you want to reset all settings to defaults? This action cannot be undone.",
		)
	) {
		// Reset logic would go here
		console.log("Resetting to defaults")
	}
}

const formatDate = (dateString) => {
	if (!dateString) return "Never"
	return new Date(dateString).toLocaleString()
}
</script>