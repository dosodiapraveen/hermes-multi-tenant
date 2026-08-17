<template>
  <section class="projects-section">
    <div class="section-header">
      <h2>
        <BaseIcon name="folder" :size="24" />
        Projects
      </h2>
      <BaseButton icon="plus" @click="$emit('openModal')">
        New Project
      </BaseButton>
    </div>

    <!-- Project List View -->
    <template v-if="!selectedProject">
      <div v-if="projects.length" class="projects-grid">
        <BaseCard
          v-for="p in projects"
          :key="p.id"
          clickable
          @click="$emit('select', p)"
        >
          <div class="project-header">
            <strong>{{ p.title }}</strong>
            <BaseBadge :label="statusLabel(p.status)" :variant="p.status" size="sm" />
          </div>
          <p class="project-description">{{ truncate(p.description, 80) }}</p>
          <span class="project-meta">Updated {{ formatDate(p.updated_at) }}</span>
        </BaseCard>
      </div>

      <BaseEmptyState
        v-else
        icon="folder"
        variant="success"
        title="No projects yet"
        description="Organize your work with projects. Track progress, add research, and keep everything in one place."
        action-label="Create Your First Project"
        @action="$emit('openModal')"
      />
    </template>

    <!-- Project Detail View -->
    <div v-else class="project-detail">
      <BaseButton variant="outline" icon="arrow-left" size="sm" @click="$emit('deselect')">
        Back to projects
      </BaseButton>

      <BaseCard class="project-info-card">
        <div class="project-detail-header">
          <h2>{{ selectedProject.title }}</h2>
          <BaseSelect
            :model-value="selectedProject.status"
            :options="statusOptions"
            @change="$emit('updateStatus', selectedProject, $event.value)"
          />
        </div>
        <p class="project-description">{{ selectedProject.description }}</p>
        <div class="project-meta-row">
          <span>Created {{ formatDate(selectedProject.created_at) }}</span>
          <span>Updated {{ formatDate(selectedProject.updated_at) }}</span>
        </div>
        <div class="project-actions">
          <BaseButton variant="outline" size="sm" icon="edit" @click="$emit('openModal', selectedProject)">
            Edit
          </BaseButton>
          <BaseButton variant="danger" size="sm" icon="trash" @click="$emit('delete', selectedProject.id)">
            Delete
          </BaseButton>
        </div>
      </BaseCard>

      <!-- Research Section -->
      <div class="research-section">
        <div class="research-header">
          <h3>
            <BaseIcon name="file-text" :size="18" />
            Research
          </h3>
          <BaseButton variant="outline" size="sm" icon="plus" @click="$emit('openResearch')">
            Add Research
          </BaseButton>
        </div>

        <div v-if="selectedProject.research?.length" class="research-list">
          <BaseCard v-for="r in selectedProject.research" :key="r.id" class="research-card">
            <div class="research-content">
              <div class="research-info">
                <strong>{{ r.title }}</strong>
                <p>{{ r.content }}</p>
                <span class="research-meta">{{ formatDate(r.created_at) }}</span>
              </div>
              <BaseButton
                variant="ghost"
                size="sm"
                icon="x"
                icon-only
                @click="$emit('deleteResearch', selectedProject.id, r.id)"
              />
            </div>
          </BaseCard>
        </div>

        <BaseEmptyState
          v-else
          compact
          icon="file-text"
          title="No research added"
          description="Add research notes to keep track of project findings."
          action-label="Add Research"
          @action="$emit('openResearch')"
        />
      </div>
    </div>
  </section>
</template>

<script>
import { BaseCard, BaseIcon, BaseBadge, BaseButton, BaseSelect, BaseEmptyState } from '@design-system/components/ui'

export default {
  name: 'PortalProjects',
  components: { BaseCard, BaseIcon, BaseBadge, BaseButton, BaseSelect, BaseEmptyState },
  props: {
    projects: { type: Array, default: () => [] },
    selectedProject: { type: Object, default: null }
  },
  emits: ['openModal', 'openResearch', 'select', 'deselect', 'delete', 'deleteResearch', 'updateStatus'],
  data() {
    return {
      statusOptions: [
        { value: 'active', label: 'Active' },
        { value: 'paused', label: 'Paused' },
        { value: 'done', label: 'Done' },
        { value: 'archived', label: 'Archived' }
      ]
    }
  },
  methods: {
    statusLabel(s) {
      const labels = {
        active: 'Active',
        paused: 'Paused',
        done: 'Done',
        archived: 'Archived'
      }
      return labels[s] || s
    },
    truncate(text, length) {
      if (!text) return ''
      return text.length > length ? text.slice(0, length) + '...' : text
    },
    formatDate(date) {
      if (!date) return ''
      const d = new Date(date); const p = (n) => String(n).padStart(2, '0')
      return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`
    }
  }
}
</script>

<style scoped>
.projects-section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-4);
}

.section-header h2 {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  margin: 0;
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--spacing-4);
}

.project-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-2);
  margin-bottom: var(--spacing-2);
}

.project-header strong {
  font-size: var(--font-size-md);
}

.project-description {
  margin: 0 0 var(--spacing-2);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: var(--line-height-relaxed);
}

.project-meta {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

/* Project Detail */
.project-detail {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

.project-info-card {
  margin-top: var(--spacing-2);
}

.project-detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-4);
  margin-bottom: var(--spacing-3);
}

.project-detail-header h2 {
  margin: 0;
  font-size: var(--font-size-xl);
}

.project-detail-header .base-select-wrapper {
  min-width: 140px;
}

.project-meta-row {
  display: flex;
  gap: var(--spacing-4);
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
  margin-bottom: var(--spacing-3);
}

.project-actions {
  display: flex;
  gap: var(--spacing-2);
}

/* Research Section */
.research-section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}

.research-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-4);
}

.research-header h3 {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  margin: 0;
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
}

.research-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.research-content {
  display: flex;
  gap: var(--spacing-3);
}

.research-info {
  flex: 1;
  min-width: 0;
}

.research-info strong {
  display: block;
  margin-bottom: var(--spacing-1);
}

.research-info p {
  margin: 0 0 var(--spacing-1);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.research-meta {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

/* Responsive */
@media (max-width: 640px) {
  .section-header {
    flex-direction: column;
    align-items: stretch;
  }

  .projects-grid {
    grid-template-columns: 1fr;
  }

  .project-detail-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .project-detail-header .base-select-wrapper {
    width: 100%;
  }
}
</style>
