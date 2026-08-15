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

    <!-- Reminders List -->
    <div v-if="reminders.length" class="reminders-list">
      <BaseCard
        v-for="r in reminders"
        :key="r.id"
        :class="['reminder-card', { done: r.done }]"
      >
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
            @click.stop="$emit('delete', r.id)"
          />
        </div>
      </BaseCard>
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
import { BaseCard, BaseIcon, BaseButton, BaseEmptyState } from '../ui'

export default {
  name: 'PortalReminders',
  components: { BaseCard, BaseIcon, BaseButton, BaseEmptyState },
  props: {
    reminders: { type: Array, default: () => [] }
  },
  emits: ['openModal', 'delete', 'toggle'],
  methods: {
    formatDateTime(dt) {
      if (!dt) return ''
      return dt.slice(0, 16).replace('T', ' ')
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

/* Responsive */
@media (max-width: 640px) {
  .section-header {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
