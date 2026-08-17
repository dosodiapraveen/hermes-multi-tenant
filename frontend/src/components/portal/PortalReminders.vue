<template>
  <section class="reminders-section">
    <div class="section-header">
      <h2>
        <BaseIcon name="clock" :size="24" />
        Reminders
      </h2>
      <BaseButton icon="plus" @click="$emit('openModal')">
        New Reminder
      </BaseButton>
    </div>

    <!-- Swipe hint (shown once) -->
    <p v-if="reminders.length && showSwipeHint" class="swipe-hint">
      <BaseIcon name="arrow-left" :size="14" />
      Swipe left to delete
    </p>

    <!-- Reminders List -->
    <div v-if="reminders.length" class="reminders-list">
      <SwipeableItem
        v-for="r in reminders"
        :key="r.id"
        action-icon="trash"
        action-label="Delete"
        action-variant="danger"
        @action="handleSwipeDelete(r.id)"
        @swipe-start="closeOtherSwipes(r.id)"
        :ref="el => setSwipeRef(r.id, el)"
      >
        <BaseCard :class="['reminder-card', { done: r.done }]">
          <div class="reminder-content">
            <label class="checkbox-wrapper" @click.stop>
              <input
                type="checkbox"
                :checked="r.done"
                @change="$emit('toggle', r)"
              />
              <span class="checkbox-custom">
                <BaseIcon v-if="r.done" name="check" :size="12" />
              </span>
            </label>

            <div class="reminder-details">
              <span :class="['reminder-title', { strikethrough: r.done }]">
                {{ r.title }}
              </span>
              <span v-if="r.remind_at" class="reminder-time">
                <BaseIcon name="clock" :size="12" />
                {{ formatDateTime(r.remind_at) }}
              </span>
            </div>

            <BaseButton
              variant="ghost"
              size="sm"
              icon="trash"
              icon-only
              class="delete-btn-desktop"
              @click.stop="$emit('delete', r.id)"
            />
          </div>
        </BaseCard>
      </SwipeableItem>
    </div>

    <!-- Empty State -->
    <BaseEmptyState
      v-else
      icon="clock"
      variant="error"
      title="No reminders set"
      description="Never forget important tasks. Set reminders and stay on top of everything."
      action-label="Set Your First Reminder"
      @action="$emit('openModal')"
    />
  </section>
</template>

<script>
import { BaseCard, BaseIcon, BaseButton, BaseEmptyState, SwipeableItem } from '@design-system/components/ui'

export default {
  name: 'PortalReminders',
  components: { BaseCard, BaseIcon, BaseButton, BaseEmptyState, SwipeableItem },
  props: {
    reminders: { type: Array, default: () => [] }
  },
  emits: ['openModal', 'delete', 'toggle'],
  data() {
    return {
      swipeRefs: {},
      showSwipeHint: !localStorage.getItem('reminders-swipe-hint-dismissed')
    }
  },
  methods: {
    formatDateTime(dt) {
      if (!dt) return ''
      const d = new Date(dt)   // offset-aware ISO -> browser's local timezone
      const p = (n) => String(n).padStart(2, '0')
      return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`
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
        localStorage.setItem('reminders-swipe-hint-dismissed', 'true')
      }
    },
    handleSwipeDelete(id) {
      this.$emit('delete', id)
    }
  }
}
</script>

<style scoped>
.reminders-section {
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

.reminders-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.reminder-card {
  transition: opacity var(--transition-fast);
}

.reminder-card.done {
  opacity: 0.6;
}

.reminder-content {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
}

.checkbox-wrapper {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.checkbox-wrapper input {
  display: none;
}

.checkbox-custom {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border: 2px solid var(--color-gray-300);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  color: var(--color-text-inverse);
  transition: all var(--transition-fast);
}

.checkbox-wrapper input:checked + .checkbox-custom {
  background: var(--color-primary-500);
  border-color: var(--color-primary-500);
}

.checkbox-wrapper:hover .checkbox-custom {
  border-color: var(--color-primary-400);
}

.reminder-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-1);
  min-width: 0;
}

.reminder-title {
  font-weight: var(--font-weight-medium);
  transition: all var(--transition-fast);
}

.reminder-title.strikethrough {
  text-decoration: line-through;
  color: var(--color-text-tertiary);
}

.reminder-time {
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
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

  /* Hide desktop delete button on mobile (use swipe instead) */
  .delete-btn-desktop {
    display: none;
  }
}

/* Hide swipe hint on devices without touch */
@media (hover: hover) and (pointer: fine) {
  .swipe-hint {
    display: none;
  }
}
</style>
