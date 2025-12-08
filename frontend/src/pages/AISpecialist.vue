<template>
  <div class="ai-specialist-container">
    <div class="flex h-screen bg-gray-50">
      <!-- Sidebar -->
      <div class="w-80 bg-white border-r border-gray-200 flex flex-col">
        <!-- Header -->
        <div class="p-6 border-b border-gray-200">
          <div class="flex items-center gap-3">
            <div class="h-12 w-12 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg">
              <BrainIcon class="h-6 w-6 text-white" />
            </div>
            <div>
              <h2 class="text-lg font-bold text-gray-900">AI Audit Specialist</h2>
              <p class="text-sm text-gray-600">Intelligent audit assistance</p>
            </div>
          </div>
        </div>

        <!-- Capabilities -->
        <div class="flex-1 overflow-y-auto p-4">
          <!-- Category Groups -->
          <div v-for="category in capabilityCategories" :key="category.id" class="mb-4">
            <!-- Category Header -->
            <button
              @click="toggleCategory(category.id)"
              class="w-full flex items-center justify-between py-2 px-1 text-xs font-semibold text-gray-500 uppercase tracking-wider hover:text-gray-700 transition-colors"
            >
              <div class="flex items-center gap-2">
                <component :is="category.icon" class="h-3.5 w-3.5" />
                <span>{{ category.label }}</span>
              </div>
              <ChevronDownIcon
                class="h-3.5 w-3.5 transition-transform duration-200"
                :class="{ 'rotate-180': !expandedCategories.includes(category.id) }"
              />
            </button>

            <!-- Capability Cards Grid -->
            <div
              v-show="expandedCategories.includes(category.id)"
              class="grid grid-cols-2 gap-2 mt-2"
            >
              <div
                v-for="capability in getCapabilitiesByCategory(category.id)"
                :key="capability.id"
                @click="selectCapability(capability)"
                class="group relative p-3 rounded-lg border cursor-pointer transition-all duration-200"
                :class="[
                  selectedCapability?.id === capability.id
                    ? 'bg-blue-50 border-blue-300 ring-1 ring-blue-200'
                    : 'bg-white border-gray-200 hover:border-gray-300 hover:shadow-sm'
                ]"
              >
                <!-- Icon -->
                <div
                  class="w-8 h-8 rounded-lg flex items-center justify-center mb-2 transition-colors"
                  :class="[
                    selectedCapability?.id === capability.id
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-100 text-gray-600 group-hover:bg-gray-200'
                  ]"
                >
                  <component :is="capability.icon" class="h-4 w-4" />
                </div>
                <!-- Title -->
                <div
                  class="text-xs font-medium leading-tight"
                  :class="[
                    selectedCapability?.id === capability.id
                      ? 'text-blue-900'
                      : 'text-gray-700'
                  ]"
                >
                  {{ capability.title }}
                </div>
                <!-- Tooltip on hover -->
                <div class="absolute left-full ml-2 top-1/2 -translate-y-1/2 z-50 hidden group-hover:block w-48">
                  <div class="bg-gray-900 text-white text-xs rounded-lg py-2 px-3 shadow-lg">
                    {{ capability.description }}
                    <div class="absolute right-full top-1/2 -translate-y-1/2 border-4 border-transparent border-r-gray-900"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Recent Conversations -->
          <div class="mt-6">
            <div class="text-sm font-medium text-gray-700 mb-3">Recent Sessions</div>
            <div class="space-y-2">
              <div
                v-for="session in recentSessions"
                :key="session.id"
                class="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50 cursor-pointer"
                @click="loadSession(session)"
              >
                <div class="w-2 h-2 rounded-full bg-green-500 flex-shrink-0"></div>
                <div class="flex-1 min-w-0">
                  <div class="text-sm font-medium text-gray-900 truncate">{{ session.title }}</div>
                  <div class="text-xs text-gray-500">{{ session.timestamp }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Settings -->
        <div class="p-4 border-t border-gray-200">
          <Button variant="outline" class="w-full" @click="showSettings = true">
            <template #prefix>
              <SettingsIcon class="h-4 w-4" />
            </template>
            Settings
          </Button>
        </div>
      </div>

      <!-- Main Content -->
      <div class="flex-1 flex flex-col">
        <!-- Top Bar -->
        <div class="bg-white border-b border-gray-200 p-4">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-lg font-semibold text-gray-900">
                {{ selectedCapability?.title || 'Select a capability' }}
              </h3>
              <p class="text-sm text-gray-600">
                {{ selectedCapability?.description || 'Choose an AI capability to get started' }}
              </p>
            </div>
            <div class="flex items-center gap-2">
              <Button variant="outline" size="sm" @click="clearConversation">
                <template #prefix>
                  <Trash2Icon class="h-4 w-4" />
                </template>
                Clear
              </Button>
              <Button variant="solid" theme="blue" size="sm" @click="startNewSession">
                <template #prefix>
                  <PlusIcon class="h-4 w-4" />
                </template>
                New Session
              </Button>
            </div>
          </div>
        </div>

        <!-- Chat Area -->
        <div class="flex-1 overflow-y-auto p-4 space-y-4">
          <!-- Welcome Message -->
          <div v-if="messages.length === 0" class="text-center py-12">
            <BrainIcon class="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <h3 class="text-lg font-medium text-gray-900 mb-2">Welcome to AI Audit Specialist</h3>
            <p class="text-gray-600 mb-6">
              Select a capability from the sidebar to begin your AI-assisted audit session.
            </p>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl mx-auto">
              <div
                v-for="capability in capabilities.slice(0, 4)"
                :key="capability.id"
                @click="selectCapability(capability)"
                class="p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 cursor-pointer transition-all"
              >
                <component :is="capability.icon" class="h-8 w-8 text-blue-600 mb-2" />
                <h4 class="font-medium text-gray-900">{{ capability.title }}</h4>
                <p class="text-sm text-gray-600">{{ capability.description }}</p>
              </div>
            </div>
          </div>

          <!-- Messages -->
          <div
            v-for="message in messages"
            :key="message.id"
            class="flex gap-3"
            :class="{ 'justify-end': message.sender === 'user' }"
          >
            <div
              class="max-w-3xl rounded-lg p-4"
              :class="message.sender === 'user'
                ? 'bg-blue-600 text-white ml-auto'
                : 'bg-white border border-gray-200 text-gray-900'"
            >
              <div class="flex items-start gap-3">
                <div
                  class="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0"
                  :class="message.sender === 'user'
                    ? 'bg-blue-700'
                    : 'bg-blue-100'"
                >
                  <component
                    :is="message.sender === 'user' ? UserIcon : BrainIcon"
                    class="h-4 w-4"
                    :class="message.sender === 'user' ? 'text-white' : 'text-blue-600'"
                  />
                </div>
                <div class="flex-1">
                  <div class="text-sm whitespace-pre-wrap">{{ message.content }}</div>
                  <div class="text-xs mt-2 opacity-70">
                    {{ formatTime(message.timestamp) }}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Typing Indicator -->
          <div v-if="isTyping" class="flex gap-3">
            <div class="bg-white border border-gray-200 rounded-lg p-4">
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                  <BrainIcon class="h-4 w-4 text-blue-600" />
                </div>
                <div class="flex space-x-1">
                  <div class="w-2 h-2 bg-blue-600 rounded-full animate-bounce"></div>
                  <div class="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                  <div class="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Input Area -->
        <div class="bg-white border-t border-gray-200 p-4">
          <div class="flex gap-3">
            <div class="flex-1">
              <textarea
                v-model="inputMessage"
                @keydown.enter.exact.prevent="sendMessage"
                placeholder="Ask the AI specialist..."
                class="w-full p-3 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                rows="1"
                :disabled="!selectedCapability"
              ></textarea>
            </div>
            <Button
              variant="solid"
              theme="blue"
              aria-label="Send message"
              @click="sendMessage"
              :disabled="!inputMessage.trim() || !selectedCapability || isTyping"
              :loading="isTyping"
            >
              <SendIcon class="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>

    <!-- Settings Modal -->
    <Dialog v-model="showSettings" :options="{ title: 'AI Settings', size: 'md' }">
      <template #body>
        <div class="space-y-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">AI Model</label>
            <Select
              v-model="aiSettings.model"
              :options="modelOptions"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Response Style</label>
            <Select
              v-model="aiSettings.responseStyle"
              :options="responseStyleOptions"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Context Window</label>
            <Select
              v-model="aiSettings.contextWindow"
              :options="contextWindowOptions"
            />
          </div>
        </div>
      </template>
      <template #actions>
        <Button variant="outline" @click="showSettings = false">Cancel</Button>
        <Button variant="solid" theme="blue" @click="saveSettings">Save Settings</Button>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { Button, Dialog, call } from 'frappe-ui'
import {
  BrainIcon,
  FileTextIcon,
  LightbulbIcon,
  SearchIcon,
  TrendingUpIcon,
  AlertTriangleIcon,
  CheckCircleIcon,
  SettingsIcon,
  Trash2Icon,
  PlusIcon,
  SendIcon,
  UserIcon,
  BarChart3Icon,
  FileBarChartIcon,
  ChevronDownIcon,
  ShieldCheckIcon,
  CpuIcon,
  BookOpenIcon,
} from 'lucide-vue-next'
import { ref, computed, nextTick, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAIContextStore } from '@/stores/useAIContextStore'

// Reactive state
const selectedCapability = ref(null)
const messages = ref([])
const inputMessage = ref('')
const isTyping = ref(false)
const showSettings = ref(false)
const currentSession = ref(null)
const expandedCategories = ref(['core-audit', 'ai-ml', 'knowledge'])

const route = useRoute()
const aiContextStore = useAIContextStore()

// Capability Categories
const capabilityCategories = ref([
  { id: 'core-audit', label: 'Core Audit', icon: ShieldCheckIcon },
  { id: 'ai-ml', label: 'AI & Analytics', icon: CpuIcon },
  { id: 'knowledge', label: 'Knowledge Base', icon: BookOpenIcon },
])

// AI Settings
const aiSettings = ref({
  model: 'gpt-4',
  responseStyle: 'professional',
  contextWindow: 'medium',
})

// Capabilities
const capabilities = ref([
  {
    id: 'risk-analysis',
    title: 'Risk Analysis',
    description: 'Analyze audit risks and provide mitigation strategies',
    icon: AlertTriangleIcon,
    category: 'core-audit',
    prompt: 'You are an expert risk analyst. Analyze the following audit scenario and provide detailed risk assessment and mitigation recommendations.',
  },
  {
    id: 'finding-review',
    title: 'Finding Review',
    description: 'Review audit findings for completeness and accuracy',
    icon: CheckCircleIcon,
    category: 'core-audit',
    prompt: 'You are an experienced audit reviewer. Review the following audit finding and provide feedback on its completeness, accuracy, and suggest improvements.',
  },
  {
    id: 'compliance-check',
    title: 'Compliance',
    description: 'Check compliance with standards and regulations',
    icon: FileTextIcon,
    category: 'core-audit',
    prompt: 'You are a compliance expert. Analyze the following scenario for compliance with relevant standards and regulations, highlighting any gaps or concerns.',
  },
  {
    id: 'audit-planning',
    title: 'Planning',
    description: 'Assist with audit planning and resource allocation',
    icon: TrendingUpIcon,
    category: 'core-audit',
    prompt: 'You are an audit planning specialist. Help plan the audit engagement, including scope definition, resource allocation, and timeline planning.',
  },
  {
    id: 'control-testing',
    title: 'Controls',
    description: 'Design and evaluate control testing procedures',
    icon: SearchIcon,
    category: 'core-audit',
    prompt: 'You are a control testing expert. Design appropriate testing procedures for the following control and evaluate its effectiveness.',
  },
  {
    id: 'insights',
    title: 'Insights',
    description: 'Generate insights from audit data and trends',
    icon: LightbulbIcon,
    category: 'core-audit',
    prompt: 'You are a data analyst specializing in audit insights. Analyze the provided audit data and generate meaningful insights and recommendations.',
  },
  {
    id: 'predictive-analytics',
    title: 'Predictive',
    description: 'AI-powered risk prediction and trend analysis',
    icon: BarChart3Icon,
    category: 'ai-ml',
    prompt: 'You are a predictive analytics expert. Analyze historical audit data to predict future risks and trends.',
  },
  {
    id: 'automated-reports',
    title: 'Auto Reports',
    description: 'Generate comprehensive AI-powered audit reports',
    icon: FileBarChartIcon,
    category: 'ai-ml',
    prompt: 'You are a report generation specialist. Create comprehensive audit reports with AI-powered insights and recommendations.',
  },
  {
    id: 'domain-training',
    title: 'Training',
    description: 'Access audit-specific knowledge and training data',
    icon: BrainIcon,
    category: 'knowledge',
    prompt: 'You are an audit domain expert. Provide comprehensive audit knowledge, terminology, and training examples.',
  },
  {
    id: 'model-fine-tuning',
    title: 'Fine-tuning',
    description: 'Fine-tune AI models with custom audit training data',
    icon: SettingsIcon,
    category: 'ai-ml',
    prompt: 'You are an AI training specialist. Help fine-tune AI models with audit-specific training data and validation.',
  },
  {
    id: 'terminology-guide',
    title: 'Terminology',
    description: 'Access comprehensive audit terminology and definitions',
    icon: FileTextIcon,
    category: 'knowledge',
    prompt: 'You are a terminology expert. Provide definitions, examples, and context for audit-specific terms and concepts.',
  },
  {
    id: 'advanced-ml-analytics',
    title: 'ML Analytics',
    description: 'Machine learning-powered predictive analytics and insights',
    icon: TrendingUpIcon,
    category: 'ai-ml',
    prompt: 'You are an advanced ML analyst. Apply sophisticated machine learning algorithms to audit data for predictive insights.',
  },
  {
    id: 'anomaly-detection',
    title: 'Anomalies',
    description: 'AI-powered detection of unusual patterns and outliers',
    icon: AlertTriangleIcon,
    category: 'ai-ml',
    prompt: 'You are an anomaly detection specialist. Identify unusual patterns and potential issues in audit data.',
  },
  {
    id: 'risk-forecasting',
    title: 'Forecasting',
    description: 'Time series forecasting for risk trend analysis',
    icon: BarChart3Icon,
    category: 'ai-ml',
    prompt: 'You are a risk forecasting expert. Predict future risk trends using advanced time series analysis.',
  },
])

// Options
const modelOptions = [
  { label: 'GPT-4 (Recommended)', value: 'gpt-4' },
  { label: 'GPT-3.5 Turbo', value: 'gpt-3.5-turbo' },
  { label: 'Claude 3', value: 'claude-3' },
]

const responseStyleOptions = [
  { label: 'Professional', value: 'professional' },
  { label: 'Conversational', value: 'conversational' },
  { label: 'Technical', value: 'technical' },
]

const contextWindowOptions = [
  { label: 'Short (5 messages)', value: 'short' },
  { label: 'Medium (20 messages)', value: 'medium' },
  { label: 'Long (50 messages)', value: 'long' },
]

// Recent sessions (mock data)
const recentSessions = ref([
  { id: 1, title: 'Q4 Risk Assessment Review', timestamp: '2 hours ago' },
  { id: 2, title: 'IT Controls Testing', timestamp: '1 day ago' },
  { id: 3, title: 'Compliance Gap Analysis', timestamp: '3 days ago' },
])

// Load context on mount
onMounted(() => {
  const contextKey = route.query.context
  const contextType = route.query.type

  if (contextKey) {
    // Load context from localStorage using the store
    const context = aiContextStore.loadContextFromStorage(contextKey)

    if (context) {
      // Auto-select a relevant capability based on context type
      const suggestedCapabilityId = aiContextStore.getSuggestedCapability(context.page_type)
      const suggestedCapability = capabilities.value.find(cap => cap.id === suggestedCapabilityId) || capabilities.value[0]
      selectCapability(suggestedCapability)

      // Add welcome message with context information
      const contextPrompt = aiContextStore.getSuggestedQuestions(context.page_type)[0] || 'How can I help you with this data?'
      addMessage('assistant', `I've loaded the context from your ${aiContextStore.contextTitle}. ${aiContextStore.getContextPrompt(context.page_type)} What would you like to know?`)
    }
  }
})

// Methods
const selectCapability = (capability) => {
  selectedCapability.value = capability
  if (messages.value.length === 0) {
    addMessage('assistant', `Hello! I'm ready to help with ${capability.title.toLowerCase()}. How can I assist you today?`)
  }
}

const sendMessage = async () => {
  if (!inputMessage.value.trim() || !selectedCapability.value) return

  const userMessage = inputMessage.value.trim()
  addMessage('user', userMessage)
  inputMessage.value = ''

  isTyping.value = true

  try {
    // Simulate AI response (replace with actual AI API call)
    await new Promise(resolve => setTimeout(resolve, 2000))

    const aiResponse = await generateAIResponse(userMessage)
    addMessage('assistant', aiResponse)
  } catch (error) {
    console.error('AI response error:', error)
    addMessage('assistant', 'I apologize, but I encountered an error processing your request. Please try again.')
  } finally {
    isTyping.value = false
  }
}

const generateAIResponse = async (userMessage) => {
  // Handle advanced AI features
  if (selectedCapability.value.id === 'predictive-analytics') {
    return await generatePredictiveAnalytics(userMessage)
  } else if (selectedCapability.value.id === 'automated-reports') {
    return await generateAutomatedReport(userMessage)
  } else if (selectedCapability.value.id === 'domain-training') {
    return await generateDomainTraining(userMessage)
  } else if (selectedCapability.value.id === 'model-fine-tuning') {
    return await generateModelFineTuning(userMessage)
  } else if (selectedCapability.value.id === 'terminology-guide') {
    return await generateTerminologyGuide(userMessage)
  } else if (selectedCapability.value.id === 'advanced-ml-analytics') {
    return await generateAdvancedMLAnalytics(userMessage)
  } else if (selectedCapability.value.id === 'anomaly-detection') {
    return await generateAnomalyDetection(userMessage)
  } else if (selectedCapability.value.id === 'risk-forecasting') {
    return await generateRiskForecasting(userMessage)
  }

  // Use real AI API for standard capabilities
  try {
    const response = await call("mkaguzi.api.ai_specialist.get_ai_specialist_response", {
      capability: selectedCapability.value.id,
      user_message: userMessage,
      context_data: aiContextStore.getContextForAI() // Pass current context from store
    })

    if (response.success) {
      return response.response
    } else {
      console.error('AI API Error:', response.error)
      return `I apologize, but I encountered an error: ${response.error}. Please try again.`
    }
  } catch (error) {
    console.error('AI API Call Error:', error)
    return `I apologize, but I encountered a connection error. Please check your internet connection and try again.`
  }
}

const addMessage = (sender, content) => {
  messages.value.push({
    id: Date.now(),
    sender,
    content,
    timestamp: new Date(),
  })

  nextTick(() => {
    scrollToBottom()
  })
}

const scrollToBottom = () => {
  const chatContainer = document.querySelector('.flex-1.overflow-y-auto')
  if (chatContainer) {
    chatContainer.scrollTop = chatContainer.scrollHeight
  }
}

const clearConversation = () => {
  messages.value = []
}

const startNewSession = () => {
  currentSession.value = {
    id: Date.now(),
    title: `Session ${new Date().toLocaleDateString()}`,
    messages: [],
  }
  messages.value = []
  selectedCapability.value = null
}

const loadSession = (session) => {
  // Load session messages (mock implementation)
  console.log('Loading session:', session)
}

const toggleCategory = (categoryId) => {
  const index = expandedCategories.value.indexOf(categoryId)
  if (index > -1) {
    expandedCategories.value.splice(index, 1)
  } else {
    expandedCategories.value.push(categoryId)
  }
}

const getCapabilitiesByCategory = (categoryId) => {
  return capabilities.value.filter(cap => cap.category === categoryId)
}

const saveSettings = () => {
  // Save AI settings
  console.log('Saving settings:', aiSettings.value)
  showSettings.value = false
}

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

// Advanced AI Feature Functions
const generatePredictiveAnalytics = async (userMessage) => {
  try {
    const response = await call("mkaguzi.api.ai_specialist.get_predictive_analytics", {
      engagement_id: null, // Can be made configurable
      time_period: "6_months",
      analysis_type: "risk_trends"
    })

    if (response.success) {
      const insights = response.insights
      return `**Predictive Analytics Report**

**Risk Distribution:**
- Low: ${insights.risk_distribution?.Low || 0}
- Medium: ${insights.risk_distribution?.Medium || 0}
- High: ${insights.risk_distribution?.High || 0}
- Critical: ${insights.risk_distribution?.Critical || 0}

**Key Insights:**
${insights.key_insights?.map(insight => `- ${insight}`).join('\n') || 'Analysis completed'}

**Confidence Level:** ${response.confidence_level}

**Recommendations:**
${response.recommendations?.map(rec => `- ${rec}`).join('\n') || 'No specific recommendations at this time'}

*Based on ${response.analysis_type} analysis over ${response.time_period}*`
    } else {
      return `Unable to generate predictive analytics: ${response.error || 'Unknown error'}`
    }
  } catch (error) {
    console.error('Predictive Analytics Error:', error)
    return 'I apologize, but I encountered an error generating predictive analytics. Please try again.'
  }
}

const generateAutomatedReport = async (userMessage) => {
  try {
    // Determine report type from user message
    let reportType = 'audit_summary'
    if (userMessage.toLowerCase().includes('risk')) {
      reportType = 'risk_assessment'
    } else if (userMessage.toLowerCase().includes('compliance')) {
      reportType = 'compliance_status'
    }

    const response = await call("mkaguzi.api.ai_specialist.generate_ai_report", {
      report_type: reportType,
      parameters: {},
      include_visualizations: true
    })

    if (response.success) {
      return `**${response.title}**

**Executive Summary:**
${response.executive_summary}

**Key Sections:**
${response.sections?.map(section => `### ${section.title}\n${section.content}`).join('\n\n') || 'Report sections generated'}

**Conclusions:**
${response.conclusions}

**Recommendations:**
${response.recommendations?.map(rec => `- ${rec}`).join('\n') || 'Recommendations generated'}

**Visualizations Suggested:** ${response.visualizations?.length || 0} charts recommended

*Report generated on ${new Date(response.generated_at).toLocaleDateString()}*`
    } else {
      return `Unable to generate automated report: ${response.error || 'Unknown error'}`
    }
  } catch (error) {
    console.error('Automated Report Error:', error)
    return 'I apologize, but I encountered an error generating the automated report. Please try again.'
  }
}

const generateDomainTraining = async (userMessage) => {
  try {
    // Extract topic from user message
    let topic = null
    const topicKeywords = ['GAAS', 'COSO', 'IIA', 'SOX', 'risk', 'control', 'compliance', 'fraud']
    for (const keyword of topicKeywords) {
      if (userMessage.toLowerCase().includes(keyword.toLowerCase())) {
        topic = keyword
        break
      }
    }

    const response = await call("mkaguzi.api.ai_specialist.get_audit_domain_knowledge", {
      topic: topic,
      context_type: 'general'
    })

    if (response.success) {
      let result = '**Audit Domain Knowledge**\n\n'

      if (response.domain_knowledge?.length > 0) {
        result += '**Key Knowledge Areas:**\n'
        response.domain_knowledge.forEach(item => {
          result += `### ${item.topic}\n`
          result += `${item.definition}\n\n`
          result += `**Key Principles:** ${item.key_principles?.join(', ') || 'N/A'}\n`
          result += `**Application:** ${item.application}\n\n`
        })
      }

      if (response.training_examples?.length > 0) {
        result += '**Training Examples:**\n'
        response.training_examples.forEach(example => {
          result += `- **Question:** ${example.question}\n`
          result += `  **Expected Response:** ${example.expected_response}\n\n`
        })
      }

      result += `*Knowledge items: ${response.total_knowledge_items}, Examples: ${response.total_examples}*`

      return result
    } else {
      return `Unable to access domain knowledge: ${response.error || 'Unknown error'}`
    }
  } catch (error) {
    console.error('Domain Training Error:', error)
    return 'I apologize, but I encountered an error accessing audit domain knowledge. Please try again.'
  }
}

const generateModelFineTuning = async (userMessage) => {
  try {
    // Determine capability to fine-tune
    let capability = 'risk-analysis' // default
    const capabilityMap = {
      'risk': 'risk-analysis',
      'finding': 'finding-review',
      'compliance': 'compliance-check',
      'planning': 'audit-planning',
      'control': 'control-testing',
      'insights': 'insights'
    }

    for (const [keyword, cap] of Object.entries(capabilityMap)) {
      if (userMessage.toLowerCase().includes(keyword)) {
        capability = cap
        break
      }
    }

    const response = await call("mkaguzi.api.ai_specialist.fine_tune_ai_model", {
      capability: capability,
      training_data: {
        terminology: {
          'Materiality': 'The magnitude of an omission or misstatement that could influence economic decisions',
          'Internal Controls': 'Processes designed to provide reasonable assurance regarding achievement of objectives'
        },
        industry_context: 'General business operations',
        regulatory_focus: 'GAAS, IIA Standards'
      },
      validation_examples: [
        {
          question: 'What is materiality?',
          expected_keywords: ['magnitude', 'omission', 'misstatement', 'influence']
        }
      ]
    })

    if (response.success) {
      return `**AI Model Fine-tuning Results**

**Capability:** ${response.capability}
**Training Data Used:** ${response.training_data_used ? 'Yes' : 'No'}
**Model Updated:** ${response.model_updated ? 'Yes' : 'No'}

**Enhanced Prompt Preview:**
${response.enhanced_prompt?.substring(0, 200)}...

**Validation Results:**
${response.validation_results?.length || 0} examples validated

**Fine-tuned at:** ${new Date(response.fine_tuned_at).toLocaleString()}

The AI model has been successfully fine-tuned with audit-specific knowledge and terminology.`
    } else {
      return `Unable to fine-tune AI model: ${response.error || 'Unknown error'}`
    }
  } catch (error) {
    console.error('Model Fine-tuning Error:', error)
    return 'I apologize, but I encountered an error during AI model fine-tuning. Please try again.'
  }
}

const generateTerminologyGuide = async (userMessage) => {
  try {
    // Determine domain from user message
    let domain = 'general'
    const domainKeywords = {
      'financial': 'financial',
      'operational': 'operational',
      'compliance': 'compliance',
      'it': 'IT',
      'information technology': 'IT'
    }

    for (const [keyword, dom] of Object.entries(domainKeywords)) {
      if (userMessage.toLowerCase().includes(keyword)) {
        domain = dom
        break
      }
    }

    const response = await call("mkaguzi.api.ai_specialist.get_audit_terminology_guide", {
      domain: domain,
      include_examples: true
    })

    if (response.success) {
      let result = `**Audit Terminology Guide - ${response.domain}**\n\n`

      if (response.terminology?.length > 0) {
        response.terminology.forEach(term => {
          result += `### ${term.term}\n`
          result += `**Definition:** ${term.definition}\n`
          result += `**Domains:** ${term.domains?.join(', ') || 'General'}\n`
          result += `**Usage Context:** ${term.usage_context}\n`

          if (term.examples?.length > 0) {
            result += `**Examples:**\n`
            term.examples.forEach(example => {
              result += `- ${example}\n`
            })
          }
          result += '\n'
        })
      }

      result += `*Total terms: ${response.total_terms}, Examples included: ${response.examples_included}*`

      return result
    } else {
      return `Unable to access terminology guide: ${response.error || 'Unknown error'}`
    }
  } catch (error) {
    console.error('Terminology Guide Error:', error)
    return 'I apologize, but I encountered an error accessing the audit terminology guide. Please try again.'
  }
}

const generateAdvancedMLAnalytics = async (userMessage) => {
  try {
    // Determine analysis type and algorithms
    let analysisType = 'comprehensive'
    let algorithms = ['linear_regression', 'random_forest', 'gradient_boosting']

    if (userMessage.toLowerCase().includes('risk')) {
      analysisType = 'risk_focused'
    } else if (userMessage.toLowerCase().includes('trend')) {
      analysisType = 'trend_focused'
    }

    if (userMessage.toLowerCase().includes('neural')) {
      algorithms.push('neural_network')
    }

    const response = await call("mkaguzi.api.ai_specialist.get_advanced_predictive_analytics", {
      time_period: "12_months",
      analysis_type: analysisType,
      ml_algorithms: algorithms
    })

    if (response.success) {
      let result = `**Advanced Machine Learning Analytics**

**Analysis Type:** ${response.analysis_type.replace('_', ' ').toUpperCase()}
**Time Period:** ${response.time_period.replace('_', ' ').toUpperCase()}
**Data Points Analyzed:** ${response.data_points_analyzed}

**ML Algorithms Used:**
${response.ml_algorithms_used.map(algo => `- ${algo.replace('_', ' ').toUpperCase()}`).join('\n')}

**Best Performing Algorithm:** ${response.comprehensive_insights.best_performing_algorithm.replace('_', ' ').toUpperCase()}
**Average Accuracy:** ${(response.comprehensive_insights.average_accuracy * 100).toFixed(1)}%

**Key Findings:**
${response.comprehensive_insights.key_findings.map(finding => `- ${finding}`).join('\n')}

**Recommendations:**
${response.comprehensive_insights.recommendations.map(rec => `- ${rec}`).join('\n')}

**Confidence Scores:**
${Object.entries(response.confidence_scores).map(([algo, score]) => `- ${algo.replace('_', ' ').toUpperCase()}: ${(score * 100).toFixed(1)}%`).join('\n')}

**Algorithm Insights:**
`

      // Add insights from each algorithm
      for (const [algo, results] of Object.entries(response.ml_results)) {
        result += `\n### ${algo.replace('_', ' ').toUpperCase()}`
        result += `\n- Model Score: ${(results.model_score * 100).toFixed(1)}%`
        result += `\n- Key Insights: ${results.insights.slice(0, 2).join(', ')}`
      }

      result += `\n\n*Advanced ML analysis completed on ${new Date(response.generated_at).toLocaleString()}*`

      return result
    } else {
      return `Unable to generate advanced ML analytics: ${response.error || 'Unknown error'}`
    }
  } catch (error) {
    console.error('Advanced ML Analytics Error:', error)
    return 'I apologize, but I encountered an error generating advanced ML analytics. Please try again.'
  }
}

const generateAnomalyDetection = async (userMessage) => {
  try {
    // Determine detection method and sensitivity
    let detectionMethod = 'isolation_forest'
    let sensitivity = 'medium'

    if (userMessage.toLowerCase().includes('local')) {
      detectionMethod = 'local_outlier_factor'
    } else if (userMessage.toLowerCase().includes('svm')) {
      detectionMethod = 'one_class_svm'
    } else if (userMessage.toLowerCase().includes('statistical')) {
      detectionMethod = 'statistical'
    }

    if (userMessage.toLowerCase().includes('high')) {
      sensitivity = 'high'
    } else if (userMessage.toLowerCase().includes('low')) {
      sensitivity = 'low'
    }

    // Generate sample data for demonstration
    const sampleData = Array.from({ length: 100 }, (_, i) => ({
      index: i,
      value: Math.random() * 10 + (i > 80 ? Math.random() * 20 : 0), // Add anomalies after index 80
      timestamp: new Date(Date.now() - (99 - i) * 24 * 60 * 60 * 1000).toISOString()
    }))

    const response = await call("mkaguzi.api.ai_specialist.get_anomaly_detection", {
      data_set: sampleData,
      detection_method: detectionMethod,
      sensitivity: sensitivity
    })

    if (response.success) {
      let result = `**AI-Powered Anomaly Detection**

**Detection Method:** ${response.detection_method.replace('_', ' ').toUpperCase()}
**Sensitivity Level:** ${response.sensitivity.toUpperCase()}
**Data Points Analyzed:** ${response.total_data_points}

**Results:**
- **Anomalies Detected:** ${response.anomalies_detected}
- **Anomaly Rate:** ${response.anomaly_percentage.toFixed(1)}%
- **Confidence Score:** ${(response.confidence_score * 100).toFixed(1)}%

**Key Insights:**
${response.insights.map(insight => `- ${insight}`).join('\n')}

**Detected Anomalies:**
`

      if (response.anomalies.length > 0) {
        response.anomalies.slice(0, 5).forEach(anomaly => {
          result += `- Index ${anomaly.index}: Score ${anomaly.anomaly_score}, Confidence ${(anomaly.confidence * 100).toFixed(1)}%\n`
        })

        if (response.anomalies.length > 5) {
          result += `- ... and ${response.anomalies.length - 5} more anomalies\n`
        }
      } else {
        result += `- No anomalies detected\n`
      }

      result += `\n**Recommendations:**
- ${response.anomaly_percentage > 10 ? 'High anomaly rate detected - investigate systemic issues' : 'Monitor identified anomalies closely'}
- Consider adjusting sensitivity level based on business context
- Implement automated monitoring for similar patterns

*Anomaly detection completed on ${new Date(response.detected_at).toLocaleString()}*`

      return result
    } else {
      return `Unable to perform anomaly detection: ${response.error || 'Unknown error'}`
    }
  } catch (error) {
    console.error('Anomaly Detection Error:', error)
    return 'I apologize, but I encountered an error performing anomaly detection. Please try again.'
  }
}

const generateRiskForecasting = async (userMessage) => {
  try {
    // Determine risk category and forecast parameters
    let riskCategory = 'operational'
    let forecastPeriod = 12
    let forecastMethod = 'arima'

    const categories = ['operational', 'financial', 'compliance', 'strategic', 'reputational']
    for (const category of categories) {
      if (userMessage.toLowerCase().includes(category)) {
        riskCategory = category
        break
      }
    }

    if (userMessage.toLowerCase().includes('6')) {
      forecastPeriod = 6
    } else if (userMessage.toLowerCase().includes('24')) {
      forecastPeriod = 24
    }

    if (userMessage.toLowerCase().includes('smoothing')) {
      forecastMethod = 'exponential_smoothing'
    } else if (userMessage.toLowerCase().includes('regression')) {
      forecastMethod = 'linear_regression'
    } else if (userMessage.toLowerCase().includes('prophet')) {
      forecastMethod = 'prophet'
    }

    const response = await call("mkaguzi.api.ai_specialist.get_risk_trend_forecasting", {
      risk_category: riskCategory,
      forecast_period: forecastPeriod,
      forecast_method: forecastMethod
    })

    if (response.success) {
      let result = `**Risk Trend Forecasting**

**Risk Category:** ${response.risk_category.toUpperCase()}
**Forecast Period:** ${response.forecast_period} months
**Forecast Method:** ${response.forecast_method.replace('_', ' ').toUpperCase()}
**Historical Data Points:** ${response.historical_data_points}

**Forecast Results:**
`

      // Show forecast values
      response.forecast_results.forecast_values.forEach((value, index) => {
        const month = index + 1
        const lower = response.forecast_results.confidence_intervals.lower[index]
        const upper = response.forecast_results.confidence_intervals.upper[index]
        result += `Month ${month}: ${value.toFixed(2)} (95% CI: ${lower.toFixed(2)} - ${upper.toFixed(2)})\n`
      })

      result += `
**Risk Insights:**
${response.risk_insights.map(insight => `- ${insight}`).join('\n')}

**Forecast Accuracy:** ${(response.forecast_accuracy * 100).toFixed(1)}%

**Trend Analysis:**
- **Overall Trend:** ${response.forecast_results.forecast_values[response.forecast_results.forecast_values.length - 1] > response.forecast_results.forecast_values[0] ? 'Increasing' : 'Decreasing'}
- **Average Forecast:** ${(response.forecast_results.forecast_values.reduce((a, b) => a + b, 0) / response.forecast_results.forecast_values.length).toFixed(2)}/5
- **Peak Risk Month:** ${response.forecast_results.forecast_values.indexOf(Math.max(...response.forecast_results.forecast_values)) + 1}

**Recommendations:**
- Monitor risk levels closely during high-risk periods
- Implement additional controls if risk exceeds acceptable thresholds
- Re-evaluate forecast quarterly with new data
- Consider scenario planning for high-risk projections

*Risk forecasting completed on ${new Date(response.generated_at).toLocaleString()}*`

      return result
    } else {
      return `Unable to generate risk forecasting: ${response.error || 'Unknown error'}`
    }
  } catch (error) {
    console.error('Risk Forecasting Error:', error)
    return 'I apologize, but I encountered an error generating risk forecasting. Please try again.'
  }
}

// Initialize
startNewSession()
</script>