<template>
  <div class="page-break-section">
    <div v-if="preview" class="page-break-preview">
      <div class="break-indicator">
        <MinusIcon class="break-icon" />
        <span class="break-text">Page Break</span>
        <MinusIcon class="break-icon" />
      </div>
    </div>
    <div v-else class="page-break-actual">
      <!-- This would create an actual page break in PDF export -->
      <div class="break-spacer"></div>
    </div>
  </div>
</template>

<script setup>
import { MinusIcon } from "lucide-vue-next"

const props = defineProps({
	section: {
		type: Object,
		required: true,
	},
	preview: {
		type: Boolean,
		default: true,
	},
})
</script>

<style scoped>
.page-break-section {
  margin: 2rem 0;
}

.page-break-preview {
  display: flex;
  justify-content: center;
  padding: 1rem 0;
}

.break-indicator {
  display: flex;
  align-items: center;
  gap: 1rem;
  color: #6b7280;
  font-size: 0.875rem;
  font-weight: 500;
}

.break-icon {
  width: 2rem;
  height: 1rem;
}

.break-text {
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.page-break-actual {
  page-break-before: always;
}

.break-spacer {
  height: 1px;
  background: transparent;
}

@media print {
  .page-break-preview {
    display: none;
  }
  
  .page-break-actual {
    page-break-before: always;
  }
}
</style>