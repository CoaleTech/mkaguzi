<template>
  <div class="finding-template-preview">
    <div class="space-y-6">
      <!-- Template Header -->
      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <div class="flex items-start justify-between mb-4">
          <div>
            <h3 class="text-xl font-semibold text-gray-900">{{ template.template_name }}</h3>
            <p class="text-gray-600 mt-1">{{ template.description }}</p>
          </div>
          <div class="flex items-center space-x-2">
            <Badge :theme="getCategoryTheme(template.finding_category)">
              {{ template.finding_category }}
            </Badge>
            <Badge variant="outline">
              {{ template.risk_category }}
            </Badge>
          </div>
        </div>

        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <span class="font-medium text-gray-700">Category:</span>
            <span class="ml-2">{{ template.finding_category }}</span>
          </div>
          <div>
            <span class="font-medium text-gray-700">Usage Count:</span>
            <span class="ml-2">{{ template.usage_count || 0 }}</span>
          </div>
          <div>
            <span class="font-medium text-gray-700">Status:</span>
            <Badge :theme="template.is_active ? 'green' : 'red'" class="ml-2">
              {{ template.is_active ? 'Active' : 'Inactive' }}
            </Badge>
          </div>
          <div>
            <span class="font-medium text-gray-700">Last Modified:</span>
            <span class="ml-2">{{ formatDate(template.modified) }}</span>
          </div>
        </div>
      </div>

      <!-- Template Content Preview -->
      <div class="space-y-6">
        <!-- Condition -->
        <div class="bg-white rounded-lg border border-gray-200 p-6">
          <h4 class="text-lg font-semibold text-gray-900 mb-3 flex items-center">
            <AlertCircle class="w-5 h-5 mr-2 text-blue-600" />
            Condition
          </h4>
          <div v-if="template.condition_template" class="prose prose-sm max-w-none">
            <div v-html="template.condition_template"></div>
          </div>
          <p v-else class="text-gray-500 italic">No condition template defined</p>
        </div>

        <!-- Criteria -->
        <div class="bg-white rounded-lg border border-gray-200 p-6">
          <h4 class="text-lg font-semibold text-gray-900 mb-3 flex items-center">
            <CheckSquare class="w-5 h-5 mr-2 text-purple-600" />
            Criteria
          </h4>
          <div v-if="template.criteria_template" class="prose prose-sm max-w-none">
            <div v-html="template.criteria_template"></div>
          </div>
          <p v-else class="text-gray-500 italic">No criteria template defined</p>
        </div>

        <!-- Cause -->
        <div class="bg-white rounded-lg border border-gray-200 p-6">
          <h4 class="text-lg font-semibold text-gray-900 mb-3 flex items-center">
            <Search class="w-5 h-5 mr-2 text-orange-600" />
            Cause
          </h4>
          <div v-if="template.cause_template" class="prose prose-sm max-w-none">
            <div v-html="template.cause_template"></div>
          </div>
          <p v-else class="text-gray-500 italic">No cause template defined</p>
        </div>

        <!-- Effect -->
        <div class="bg-white rounded-lg border border-gray-200 p-6">
          <h4 class="text-lg font-semibold text-gray-900 mb-3 flex items-center">
            <TrendingUp class="w-5 h-5 mr-2 text-red-600" />
            Effect
          </h4>
          <div v-if="template.effect_template" class="prose prose-sm max-w-none">
            <div v-html="template.effect_template"></div>
          </div>
          <p v-else class="text-gray-500 italic">No effect template defined</p>
        </div>

        <!-- Recommendation -->
        <div class="bg-white rounded-lg border border-gray-200 p-6">
          <h4 class="text-lg font-semibold text-gray-900 mb-3 flex items-center">
            <Lightbulb class="w-5 h-5 mr-2 text-green-600" />
            Recommendation
          </h4>
          <div v-if="template.recommendation_template" class="prose prose-sm max-w-none">
            <div v-html="template.recommendation_template"></div>
          </div>
          <p v-else class="text-gray-500 italic">No recommendation template defined</p>
        </div>
      </div>

      <!-- Default Values -->
      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <h4 class="text-lg font-semibold text-gray-900 mb-4">Default Values</h4>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <span class="font-medium text-gray-700">Priority Level:</span>
            <span class="ml-2">{{ template.default_priority || 'Not set' }}</span>
          </div>
          <div>
            <span class="font-medium text-gray-700">Business Unit:</span>
            <span class="ml-2">{{ template.default_business_unit || 'Not set' }}</span>
          </div>
          <div>
            <span class="font-medium text-gray-700">Responsible Person:</span>
            <span class="ml-2">{{ template.default_responsible_person || 'Not set' }}</span>
          </div>
          <div>
            <span class="font-medium text-gray-700">Target Days:</span>
            <span class="ml-2">{{ template.default_target_days || 'Not set' }}</span>
          </div>
        </div>

        <div class="mt-4">
          <span class="font-medium text-gray-700">Repeat Finding:</span>
          <Badge :theme="template.repeat_finding_default ? 'red' : 'green'" class="ml-2">
            {{ template.repeat_finding_default ? 'Yes' : 'No' }}
          </Badge>
        </div>

        <div v-if="template.tags" class="mt-4">
          <span class="font-medium text-gray-700">Tags:</span>
          <div class="flex flex-wrap gap-2 mt-2">
            <Badge v-for="tag in template.tags.split(',')" :key="tag" variant="outline">
              {{ tag.trim() }}
            </Badge>
          </div>
        </div>
      </div>

      <!-- Usage Statistics -->
      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <h4 class="text-lg font-semibold text-gray-900 mb-4">Usage Statistics</h4>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="text-center p-4 bg-blue-50 rounded-lg">
            <div class="text-3xl font-bold text-blue-900">{{ template.usage_count || 0 }}</div>
            <div class="text-sm text-blue-600">Total Uses</div>
          </div>

          <div class="text-center p-4 bg-green-50 rounded-lg">
            <div class="text-3xl font-bold text-green-900">85%</div>
            <div class="text-sm text-green-600">Resolution Rate</div>
          </div>

          <div class="text-center p-4 bg-purple-50 rounded-lg">
            <div class="text-3xl font-bold text-purple-900">4.2</div>
            <div class="text-sm text-purple-600">Avg Rating</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="flex items-center justify-end space-x-3 mt-6">
      <Button @click="$emit('close')" variant="outline">
        Close
      </Button>
      <Button @click="useTemplate" variant="solid">
        Use This Template
      </Button>
    </div>
  </div>
</template>

<script>
import {
	AlertCircle,
	CheckSquare,
	Lightbulb,
	Search,
	TrendingUp,
} from "lucide-vue-next"
import { computed } from "vue"

export default {
	name: "FindingTemplatePreview",
	components: {},
	props: {
		template: {
			type: Object,
			required: true,
		},
	},
	emits: ["close"],
	setup(props, { emit }) {
		// Methods
		const getCategoryTheme = (category) => {
			const themes = {
				"Financial Reporting": "blue",
				"Internal Controls": "purple",
				Compliance: "green",
				Operational: "orange",
				"IT Security": "red",
				Procurement: "yellow",
				"HR Management": "indigo",
			}
			return themes[category] || "gray"
		}

		const formatDate = (dateString) => {
			if (!dateString) return "Never"
			return new Date(dateString).toLocaleDateString()
		}

		const useTemplate = () => {
			// This would emit an event to use the template
			// For now, just close the preview
			emit("close")
		}

		return {
			getCategoryTheme,
			formatDate,
			useTemplate,

			// Icons
			AlertCircle,
			CheckSquare,
			Search,
			TrendingUp,
			Lightbulb,
		}
	},
}
</script>

<style scoped>
.prose {
  color: #374151;
}

.prose h1, .prose h2, .prose h3, .prose h4, .prose h5, .prose h6 {
  color: #111827;
}

.prose strong {
  color: #374151;
}

.prose ul {
  list-style-type: disc;
  padding-left: 1.5rem;
}

.prose ol {
  list-style-type: decimal;
  padding-left: 1.5rem;
}
</style>