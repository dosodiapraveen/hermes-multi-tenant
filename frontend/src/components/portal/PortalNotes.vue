<template>
  <section class="notes-section">
    <div class="section-header">
      <h2>
        <BaseIcon name="file-text" :size="24" />
        Notes
      </h2>
      <BaseButton icon="plus" @click="$emit('openModal')">
        New Note
      </BaseButton>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <BaseInput
        v-model="searchTerm"
        placeholder="Search notes..."
        prefix-icon="search"
        clearable
        @update:modelValue="$emit('update:search', $event)"
      />
      <BaseSelect
        v-model="categoryFilter"
        :options="categoryOptions"
        placeholder="All categories"
        @change="$emit('update:category', $event?.value || '')"
      />
    </div>

    <!-- Notes List -->
    <div v-if="filteredNotes.length" class="notes-list">
      <BaseCard
        v-for="note in filteredNotes"
        :key="note.id"
        clickable
        :class="{ expanded: expandedId === note.id }"
        @click="toggleExpand(note.id)"
      >
        <div class="note-header">
          <BaseBadge :label="note.category" variant="primary" size="sm" />
          <span class="note-title">{{ note.title }}</span>
          <span class="note-date">{{ formatDate(note.updated_at) }}</span>
        </div>

        <!-- Content Preview (when collapsed) -->
        <p v-if="expandedId !== note.id && note.content" class="note-preview">
          {{ truncateContent(note.content) }}
        </p>

        <Transition name="expand">
          <div v-if="expandedId === note.id" class="note-body">
            <p>{{ note.content }}</p>
            <div class="note-actions">
              <BaseButton variant="outline" size="sm" icon="edit" @click.stop="$emit('openModal', note)">
                Edit
              </BaseButton>
              <BaseButton variant="danger" size="sm" icon="trash" @click.stop="$emit('delete', note.id)">
                Delete
              </BaseButton>
            </div>
          </div>
        </Transition>
      </BaseCard>
    </div>

    <!-- Empty State -->
    <BaseEmptyState
      v-else
      icon="file-text"
      variant="primary"
      title="No notes yet"
      description="Create your first note to get started. Your notes are synced with your AI assistant."
      action-label="Create Your First Note"
      @action="$emit('openModal')"
    />
  </section>
</template>

<script>
import { BaseCard, BaseIcon, BaseBadge, BaseButton, BaseInput, BaseSelect, BaseEmptyState } from '@design-system/components/ui'

export default {
  name: 'PortalNotes',
  components: { BaseCard, BaseIcon, BaseBadge, BaseButton, BaseInput, BaseSelect, BaseEmptyState },
  props: {
    notes: { type: Array, default: () => [] },
    search: { type: String, default: '' },
    category: { type: String, default: '' }
  },
  emits: ['openModal', 'delete', 'update:search', 'update:category'],
  data() {
    return {
      expandedId: null,
      searchTerm: this.search,
      categoryFilter: this.category
    }
  },
  computed: {
    categoryOptions() {
      const cats = [...new Set(this.notes.map(n => n.category).filter(Boolean))]
      return [
        { value: '', label: 'All categories' },
        ...cats.map(c => ({ value: c, label: c }))
      ]
    },
    filteredNotes() {
      let result = this.notes
      if (this.searchTerm) {
        const q = this.searchTerm.toLowerCase()
        result = result.filter(n =>
          n.title.toLowerCase().includes(q) ||
          n.content?.toLowerCase().includes(q)
        )
      }
      if (this.categoryFilter) {
        result = result.filter(n => n.category === this.categoryFilter)
      }
      return result
    }
  },
  watch: {
    search(val) {
      this.searchTerm = val
    },
    category(val) {
      this.categoryFilter = val
    }
  },
  methods: {
    toggleExpand(id) {
      this.expandedId = this.expandedId === id ? null : id
    },
    formatDate(date) {
      if (!date) return ''
      return date.slice(0, 10)
    },
    truncateContent(content, maxLength = 120) {
      if (!content) return ''
      const cleaned = content.replace(/\n+/g, ' ').trim()
      if (cleaned.length <= maxLength) return cleaned
      return cleaned.slice(0, maxLength).trim() + '...'
    }
  }
}
</script>

<style scoped>
.notes-section {
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

.filter-bar {
  display: flex;
  gap: var(--spacing-3);
}

.filter-bar > :first-child {
  flex: 1;
}

.filter-bar > :last-child {
  min-width: 180px;
}

.notes-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.note-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  flex-wrap: wrap;
}

.note-title {
  flex: 1;
  font-weight: var(--font-weight-medium);
  min-width: 0;
}

.note-date {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.note-preview {
  margin: var(--spacing-2) 0 0;
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
  line-height: var(--line-height-normal);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.note-body {
  margin-top: var(--spacing-4);
  padding-top: var(--spacing-4);
  border-top: 1px solid var(--color-border-light);
}

.note-body p {
  margin: 0 0 var(--spacing-4);
  white-space: pre-wrap;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: var(--line-height-relaxed);
}

.note-actions {
  display: flex;
  gap: var(--spacing-2);
}

/* Expand animation */
.expand-enter-active,
.expand-leave-active {
  transition: all var(--transition-base);
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  max-height: 0;
  margin-top: 0;
  padding-top: 0;
}

.expand-enter-to,
.expand-leave-from {
  max-height: 500px;
}

/* Responsive */
@media (max-width: 640px) {
  .section-header {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-bar {
    flex-direction: column;
  }

  .filter-bar > :last-child {
    min-width: 100%;
  }
}
</style>
