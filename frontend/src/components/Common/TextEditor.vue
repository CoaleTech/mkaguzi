<template>
  <div class="text-editor-wrapper">
    <TextEditor
      v-model:content="internalContent"
      :placeholder="placeholder"
      :editable="editable"
      :class="editorClass"
      @change="$emit('change', $event)"
    />
  </div>
</template>

<script setup>
import { TextEditor } from 'frappe-ui'
import { ref, watch } from 'vue'

// Props
const props = defineProps({
  content: {
    type: String,
    default: '',
  },
  placeholder: {
    type: String,
    default: '',
  },
  editable: {
    type: Boolean,
    default: true,
  },
  editorClass: {
    type: String,
    default: '',
  },
})

// Emits
const emit = defineEmits(['change'])

// Reactive
const internalContent = ref(props.content)

// Watchers
watch(() => props.content, (newContent) => {
  internalContent.value = newContent
})
</script>