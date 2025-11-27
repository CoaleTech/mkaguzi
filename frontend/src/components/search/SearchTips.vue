<template>
  <div class="search-tips">
    <div class="tips-section">
      <h5>Search Operators</h5>
      <div class="tips-list">
        <div class="tip-item">
          <code>"exact phrase"</code>
          <span>Search for exact phrases using quotes</span>
        </div>
        <div class="tip-item">
          <code>word1 AND word2</code>
          <span>Both terms must be present</span>
        </div>
        <div class="tip-item">
          <code>word1 OR word2</code>
          <span>Either term can be present</span>
        </div>
        <div class="tip-item">
          <code>-word</code>
          <span>Exclude results containing this word</span>
        </div>
        <div class="tip-item">
          <code>word*</code>
          <span>Wildcard search (word, words, working, etc.)</span>
        </div>
      </div>
    </div>
    
    <div class="tips-section">
      <h5>Field-Specific Search</h5>
      <div class="tips-list">
        <div class="tip-item">
          <code>title:"finding name"</code>
          <span>Search in specific fields</span>
        </div>
        <div class="tip-item">
          <code>status:open</code>
          <span>Filter by field values</span>
        </div>
        <div class="tip-item">
          <code>created:2024</code>
          <span>Search by date ranges</span>
        </div>
      </div>
    </div>
    
    <div class="tips-section">
      <h5>Pro Tips</h5>
      <div class="tips-list">
        <div class="tip-item">
          <LightbulbIcon class="h-4 w-4 text-yellow-500" />
          <span>Use filters to narrow down results quickly</span>
        </div>
        <div class="tip-item">
          <LightbulbIcon class="h-4 w-4 text-yellow-500" />
          <span>Save frequently used searches for quick access</span>
        </div>
        <div class="tip-item">
          <LightbulbIcon class="h-4 w-4 text-yellow-500" />
          <span>Search is case-insensitive by default</span>
        </div>
        <div class="tip-item">
          <LightbulbIcon class="h-4 w-4 text-yellow-500" />
          <span>Use partial words - the search will find matches</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { LightbulbIcon } from "lucide-vue-next"
</script>

<style scoped>
.search-tips {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.tips-section h5 {
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 1rem 0;
}

.tips-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.tip-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: var(--background-color);
  border-radius: 0.375rem;
}

.tip-item code {
  background: white;
  border: 1px solid var(--border-color);
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-family: 'Courier New', monospace;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--primary-color);
  white-space: nowrap;
  min-width: 120px;
}

.tip-item span {
  color: var(--text-muted);
  font-size: 0.875rem;
}

@media (max-width: 768px) {
  .tip-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .tip-item code {
    min-width: auto;
  }
}
</style>