<template>
  <div class="template-detail">
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Main Content -->
      <div class="lg:col-span-2 space-y-6">
        <!-- Header -->
        <div>
          <div class="flex items-start justify-between mb-4">
            <div>
              <h2 class="text-2xl font-bold text-gray-900">{{ template.template_name }}</h2>
              <p class="text-gray-600">Version {{ template.version }} • by {{ template.author }}</p>
            </div>
            <div class="flex items-center space-x-3">
              <div class="flex items-center text-yellow-500">
                <Star class="w-5 h-5 fill-current mr-1" />
                <span class="font-medium">{{ template.rating || 0 }}</span>
              </div>
              <Button
                @click="$emit('import', template)"
                :loading="importing"
                variant="solid"
                size="lg"
              >
                <Download class="w-4 h-4 mr-2" />
                Import Template
              </Button>
            </div>
          </div>

          <div class="flex items-center space-x-4 text-sm text-gray-500">
            <span>{{ template.template_type }}</span>
            <span>•</span>
            <span>{{ template.category }}</span>
            <span>•</span>
            <span>{{ template.download_count || 0 }} downloads</span>
            <span>•</span>
            <span>{{ template.license_type }}</span>
          </div>
        </div>

        <!-- Description -->
        <div>
          <h3 class="text-lg font-medium text-gray-900 mb-2">Description</h3>
          <p class="text-gray-700">{{ template.description }}</p>
        </div>

        <!-- Tags -->
        <div v-if="template.tags">
          <h3 class="text-lg font-medium text-gray-900 mb-2">Tags</h3>
          <div class="flex flex-wrap gap-2">
            <span
              v-for="tag in tagsList"
              :key="tag"
              class="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full"
            >
              {{ tag }}
            </span>
          </div>
        </div>

        <!-- Compatibility -->
        <div>
          <h3 class="text-lg font-medium text-gray-900 mb-2">Compatibility</h3>
          <div class="space-y-2">
            <p class="text-gray-700">{{ template.compatibility || 'ERPNext v14+' }}</p>
            <p v-if="template.required_modules" class="text-gray-700">
              <strong>Required Modules:</strong> {{ template.required_modules }}
            </p>
          </div>
        </div>

        <!-- Preview -->
        <div v-if="template.preview_image">
          <h3 class="text-lg font-medium text-gray-900 mb-2">Preview</h3>
          <img
            :src="template.preview_image"
            :alt="template.template_name"
            class="w-full max-w-md rounded-lg border border-gray-200"
          />
        </div>
      </div>

      <!-- Sidebar -->
      <div class="space-y-6">
        <!-- Pricing -->
        <div class="bg-gray-50 rounded-lg p-4">
          <h3 class="text-lg font-medium text-gray-900 mb-3">Pricing</h3>
          <div class="text-center">
            <div class="text-3xl font-bold text-gray-900">
              {{ template.price > 0 ? `$${template.price}` : 'Free' }}
            </div>
            <p class="text-sm text-gray-600 mt-1">{{ template.license_type }} License</p>
          </div>
        </div>

        <!-- Stats -->
        <div class="bg-white border border-gray-200 rounded-lg p-4">
          <h3 class="text-lg font-medium text-gray-900 mb-3">Statistics</h3>
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-gray-600">Downloads</span>
              <span class="font-medium">{{ template.download_count || 0 }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-gray-600">Rating</span>
              <div class="flex items-center">
                <Star class="w-4 h-4 text-yellow-500 fill-current mr-1" />
                <span class="font-medium">{{ template.rating || 0 }}/5</span>
              </div>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-gray-600">Last Updated</span>
              <span class="font-medium text-sm">{{ formatDate(template.last_updated) }}</span>
            </div>
          </div>
        </div>

        <!-- Rate Template -->
        <div class="bg-white border border-gray-200 rounded-lg p-4">
          <h3 class="text-lg font-medium text-gray-900 mb-3">Rate this Template</h3>
          <div class="flex items-center space-x-1">
            <button
              v-for="star in 5"
              :key="star"
              @click="rateTemplate(star)"
              :class="[
                'w-8 h-8 flex items-center justify-center rounded',
                star <= userRating ? 'text-yellow-500 bg-yellow-50' : 'text-gray-300 hover:text-yellow-400'
              ]"
            >
              <Star class="w-5 h-5 fill-current" />
            </button>
          </div>
          <p class="text-sm text-gray-600 mt-2">
            {{ userRating ? `You rated this ${userRating} star${userRating > 1 ? 's' : ''}` : 'Click to rate' }}
          </p>
        </div>

        <!-- Actions -->
        <div class="space-y-3">
          <Button
            @click="$emit('import', template)"
            :loading="importing"
            variant="solid"
            class="w-full"
            size="lg"
          >
            <Download class="w-4 h-4 mr-2" />
            Import to Local Registry
          </Button>

          <Button
            v-if="template.demo_url"
            @click="openDemo"
            variant="outline"
            class="w-full"
          >
            <ExternalLink class="w-4 h-4 mr-2" />
            View Demo
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { call } from "frappe-ui"
import { Download, ExternalLink, Star } from "lucide-vue-next"
import { computed, onMounted, ref } from "vue"

// Props
const props = defineProps({
	template: {
		type: Object,
		required: true,
	},
})

// Emits
const emit = defineEmits(["import", "close"])

// Reactive data
const importing = ref(false)
const userRating = ref(0)

// Computed
const tagsList = computed(() => {
	return props.template.tags
		? props.template.tags
				.split(",")
				.map((tag) => tag.trim())
				.filter((tag) => tag)
		: []
})

// Methods
const formatDate = (dateString) => {
	if (!dateString) return "N/A"
	try {
		return new Date(dateString).toLocaleDateString()
	} catch {
		return dateString
	}
}

const rateTemplate = async (rating) => {
	userRating.value = rating
	try {
		await call(
			"mkaguzi.mkaguzi.core.doctype.template_marketplace.template_marketplace.rate_template",
			{
				marketplace_template_name: props.template.name,
				rating: rating,
			},
		)

		// Update the template's rating locally
		props.template.rating = rating
	} catch (error) {
		console.error("Error rating template:", error)
		userRating.value = 0
	}
}

const openDemo = () => {
	if (props.template.demo_url) {
		window.open(props.template.demo_url, "_blank")
	}
}

// Load existing rating if any
onMounted(() => {
	// In a real app, you'd load the user's existing rating
	// For now, we'll just initialize it
})
</script>

<style scoped>
/* Custom styles for template detail */
</style>