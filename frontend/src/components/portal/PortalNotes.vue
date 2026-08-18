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
      <!-- FIX: Removed direct emit - debounced via watcher -->
      <BaseInput
        v-model="searchTerm"
        placeholder="Search notes..."
        prefix-icon="search"
        clearable
      />
      <BaseSelect
        v-model="categoryFilter"
        :options="categoryOptions"
        placeholder="All categories"
        @change="$emit('update:category', $event?.value || '')"
      />
    </div>

    <!-- Swipe hint (shown once) -->
    <p v-if="filteredNotes.length && showSwipeHint" class="swipe-hint">
      <BaseIcon name="arrow-left" :size="14" />
      Swipe left to delete
    </p>

    <!-- Notes List -->
    <div v-if="filteredNotes.length" class="notes-list">
      <SwipeableItem
        v-for="note in filteredNotes"
        :key="note.id"
        action-icon="trash"
        action-label="Delete"
        action-variant="danger"
        :keep-open-on-threshold="true"
        @action="confirmDelete(note)"
        @swipe-start="closeOtherSwipes(note.id)"
        :ref="el => setSwipeRef(note.id, el)"
      >
        <BaseCard
          clickable
          :class="{ expanded: expandedId === note.id }"
          @click="toggleExpand(note.id)"
        >
          <div class="note-header">
            <BaseBadge :label="note.category" variant="primary" size="sm" />
            <span class="note-title">{{ note.title }}</span>
            <span class="note-date">{{ formatDate(note.updated_at) }}</span>
          </div>

          <!-- Full content, shown once (hidden when expanded to avoid duplication) -->
          <p v-if="expandedId !== note.id && note.content" class="note-preview">
            {{ note.content }}
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
      </SwipeableItem>
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

    <!-- Delete Confirmation Dialog -->
    <BaseConfirmDialog
      v-model="showDeleteConfirm"
      title="Delete Note"
      :message="`Are you sure you want to delete '${deleteTarget?.title || 'this note'}'?`"
      confirm-label="Delete"
      variant="danger"
      @confirm="handleConfirmedDelete"
      @cancel="cancelDelete"
    />
  </section>
</template>

<script>
import { BaseCard, BaseIcon, BaseBadge, BaseButton, BaseInput, BaseSelect, BaseEmptyState, SwipeableItem, BaseConfirmDialog } from '@design-system/components/ui'
import { useHaptics } from '@design-system/composables'

export default {
  name: 'PortalNotes',
  components: { BaseCard, BaseIcon, BaseBadge, BaseButton, BaseInput, BaseSelect, BaseEmptyState, SwipeableItem, BaseConfirmDialog },
  props: {
    notes: { type: Array, default: () => [] },
    search: { type: String, default: '' },
    category: { type: String, default: '' }
  },
  emits: ['openModal', 'delete', 'update:search', 'update:category'],
  setup() {
    const haptics = useHaptics()
    return { haptics }
  },
  data() {
    return {
      expandedId: null,
      searchTerm: this.search,
      categoryFilter: this.category,
      swipeRefs: {},
      showSwipeHint: !localStorage.getItem('notes-swipe-hint-dismissed'),
      showDeleteConfirm: false,
      deleteTarget: null,
      // FIX: Debounce timer for search input
      searchDebounceTimer: null
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
    },
    // FIX: Debounce search input to prevent API flooding
    searchTerm(val) {
      if (this.searchDebounceTimer) {
        clearTimeout(this.searchDebounceTimer)
      }
      this.searchDebounceTimer = setTimeout(() => {
        this.$emit('update:search', val)
      }, 300) // 300ms debounce
    }
  },
  beforeUnmount() {
    // Clean up debounce timer
    if (this.searchDebounceTimer) {
      clearTimeout(this.searchDebounceTimer)
    }
  },
  watch: {
    // Auto-expand the newest note so a just-added note shows its FULL content
    // (otherwise the dashboard preview truncates to 120 chars and looks truncated).
    notes: {
      immediate: true,
      handler(list) {
        if (Array.isArray(list) && list.length && !this.expandedId) {
          const newest = [...list].sort((a, b) => (b.updated_at || '').localeCompare(a.updated_at || ''))[0]
          if (newest) this.expandedId = newest.id
        }
      }
    }
  },
  methods: {
    toggleExpand(id) {
      this.expandedId = this.expandedId === id ? null : id
    },
    formatDate(date) {
      if (!date) return ''
      const d = new Date(date); const p = (n) => String(n).padStart(2, '0')
      return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`
    },
    truncateContent(content, maxLength = 120) {
      if (!content) return ''
      const cleaned = content.replace(/\n+/g, ' ').trim()
      if (cleaned.length <= maxLength) return cleaned
      return cleaned.slice(0, maxLength).trim() + '...'
    },
    setSwipeRef(id, el) {
      if (el) {
        this.swipeRefs[id] = el
      } else {
        delete this.swipeRefs[id]
      }
    },
    closeOtherSwipes(activeId) {
      Object.entries(this.swipeRefs).forEach(([id, ref]) => {
        if (id !== String(activeId) && ref?.close) {
          ref.close()
        }
      })
      // Dismiss hint on first swipe
      if (this.showSwipeHint) {
        this.showSwipeHint = false
        localStorage.setItem('notes-swipe-hint-dismissed', 'true')
      }
      // Haptic feedback when swipe starts
      this.haptics.vibrateSwipeThreshold()
    },
    confirmDelete(note) {
      // Haptic feedback on tapping delete
      this.haptics.vibrate('medium')
      this.deleteTarget = note
      this.showDeleteConfirm = true
    },
    handleConfirmedDelete() {
      if (this.deleteTarget) {
        // Haptic feedback on delete
        this.haptics.vibrateDelete()
        this.$emit('delete', this.deleteTarget.id)
        // Close the swipeable item
        const ref = this.swipeRefs[this.deleteTarget.id]
        if (ref?.close) ref.close()
      }
      this.deleteTarget = null
      this.showDeleteConfirm = false
    },
    cancelDelete() {
      // Close the swipeable item when canceling
      if (this.deleteTarget) {
        const ref = this.swipeRefs[this.deleteTarget.id]
        if (ref?.close) ref.close()
      }
      this.deleteTarget = null
      this.showDeleteConfirm = false
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
  white-space: pre-wrap;
  word-break: break-word;
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

/* Swipe hint */
.swipe-hint {
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
  margin: 0;
  padding: var(--spacing-2) var(--spacing-3);
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
  background: var(--color-surface-hover);
  border-radius: var(--radius-md);
  animation: hint-pulse 2s ease-in-out infinite;
}

@keyframes hint-pulse {
  0%, 100% { opacity: 0.7; }
  50% { opacity: 1; }
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

/* Hide swipe hint on devices without touch */
@media (hover: hover) and (pointer: fine) {
  .swipe-hint {
    display: none;
  }
}
</style>
