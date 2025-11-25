<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="max-w-md w-full text-center">
      <div class="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-red-100">
        <XCircleIcon class="h-6 w-6 text-red-600" />
      </div>
      <h1 class="mt-4 text-2xl font-bold text-gray-900">Access Denied</h1>
      <p class="mt-2 text-gray-600">
        You don't have permission to access this page.
      </p>
      <div class="mt-6">
        <router-link
          to="/"
          class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
        >
          Go to Dashboard
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { XCircleIcon } from "lucide-vue-next"
</script>