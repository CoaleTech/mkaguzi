<template>
  <div class="compliance-stats">
    <div class="stats-grid">
      <!-- Total Requirements -->
      <div class="stat-card">
        <div class="stat-header">
          <h3>Total Requirements</h3>
          <FileText class="stat-icon" />
        </div>
        <div class="stat-value">{{ totalRequirements }}</div>
        <div class="stat-description">
          All compliance requirements
        </div>
      </div>

      <!-- Active Requirements -->
      <div class="stat-card">
        <div class="stat-header">
          <h3>Active Requirements</h3>
          <CheckCircle class="stat-icon" />
        </div>
        <div class="stat-value">{{ activeRequirementsCount }}</div>
        <div class="stat-description">
          Currently active requirements
        </div>
      </div>

      <!-- Regulatory Bodies -->
      <div class="stat-card">
        <div class="stat-header">
          <h3>Regulatory Bodies</h3>
          <Building class="stat-icon" />
        </div>
        <div class="stat-value">{{ regulatoryBodiesCount }}</div>
        <div class="stat-description">
          Different regulatory authorities
        </div>
      </div>

      <!-- Categories -->
      <div class="stat-card">
        <div class="stat-header">
          <h3>Categories</h3>
          <Tag class="stat-icon" />
        </div>
        <div class="stat-value">{{ categoriesCount }}</div>
        <div class="stat-description">
          Compliance requirement categories
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Building, CheckCircle, FileText, Tag } from "lucide-vue-next"

defineProps({
	totalRequirements: {
		type: Number,
		required: true,
		default: 0,
	},
	activeRequirementsCount: {
		type: Number,
		required: true,
		default: 0,
	},
	regulatoryBodiesCount: {
		type: Number,
		required: true,
		default: 0,
	},
	categoriesCount: {
		type: Number,
		required: true,
		default: 0,
	},
})
</script>

<style scoped>
.compliance-stats {
  margin-bottom: 1.5rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.stat-card {
  background: var(--card-background);
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1.5rem;
}

.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.stat-header h3 {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-muted);
  margin: 0;
}

.stat-icon {
  color: var(--primary-color);
  font-size: 1.25rem;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-color);
  margin-bottom: 0.5rem;
}

.stat-description {
  font-size: 0.75rem;
  color: var(--text-muted);
}

/* Responsive design */
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .stat-card {
    padding: 1rem;
  }

  .stat-value {
    font-size: 1.5rem;
  }
}
</style>