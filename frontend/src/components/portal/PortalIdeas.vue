<template>
  <section class="ideas-section">
    <div class="section-header">
      <h2>
        <BaseIcon name="lightbulb" :size="24" />
        Ideas
      </h2>
      <BaseButton icon="plus" @click="$emit('openModal')">
        New Idea
      </BaseButton>
    </div>

    <!-- Ideas Grid -->
    <div v-if="ideas.length" class="ideas-grid">
      <BaseCard
        v-for="idea in ideas"
        :key="idea.id"
        class="idea-card"
      >
        <template #header>
          <div class="idea-header">
            <strong>{{ idea.title }}</strong>
            <BaseBadge :label="statusLabel(idea.status)" :variant="idea.status" size="sm" />
          </div>
        </template>

        <p class="idea-content">{{ truncate(idea.content, 100) }}</p>

        <template #footer>
          <div class="idea-footer">
            <span v-if="idea.tags" class="idea-tags">
              <BaseIcon name="tag" :size="12" />
              {{ idea.tags }}
            </span>
            <div class="idea-actions">
              <BaseButton variant="ghost" size="sm" icon="edit" icon-only @click="$emit('openModal', idea)" />
              <BaseButton variant="ghost" size="sm" icon="trash" icon-only @click="$emit('delete', idea.id)" />
            </div>
          </div>
        </template>
      </BaseCard>
    </div>

    <!-- Empty State -->
    <BaseEmptyState
      v-else
      icon="lightbulb"
      variant="warning"
      title="No ideas yet"
      description="Capture your brilliant ideas and track them from brainstorm to reality."
      action-label="Create Your First Idea"
      @action="$emit('openModal')"
    />
  </section>
</template>

<script>
import { BaseCard, BaseIcon, BaseBadge, BaseButton, BaseEmptyState } from '../ui'

export default {
  name: 'PortalIdeas',
  components: { BaseCard, BaseIcon, BaseBadge, BaseButton, BaseEmptyState },
  props: {
    ideas: { type: Array, default: () => [] }
  },
  emits: ['openModal', 'delete'],
  methods: {
    statusLabel(s) {
      const labels = {
        brainstorm: 'Brainstorm',
        developing: 'Developing',
        ready: 'Ready',
        archived: 'Archived'
      }
      return labels[s] || s
    },
    truncate(text, length) {
      if (!text) return ''
      return text.length > length ? text.slice(0, length) + '...' : text
    }
  }
}
</script>

<style scoped>
.ideas-section {
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

.ideas-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--spacing-4);
}

.idea-card {
  height: 100%;
}

.idea-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--spacing-3);
}

.idea-header strong {
  flex: 1;
  font-size: var(--font-size-md);
  line-height: var(--line-height-tight);
}

.idea-content {
  margin: 0;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: var(--line-height-relaxed);
  min-height: 3em;
}

.idea-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-2);
  width: 100%;
}

.idea-tags {
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
  font-style: italic;
}

.idea-actions {
  display: flex;
  gap: var(--spacing-1);
}

/* Responsive */
@media (max-width: 640px) {
  .section-header {
    flex-direction: column;
    align-items: stretch;
  }

  .ideas-grid {
    grid-template-columns: 1fr;
  }
}
</style>
