<template>
  <section class="schedule-section">
    <div class="section-header">
      <h2>
        <BaseIcon name="calendar" :size="24" />
        Schedule
      </h2>
      <BaseButton icon="plus" @click="$emit('openModal')">
        New Event
      </BaseButton>
    </div>

    <!-- Events List -->
    <div v-if="events.length" class="events-list">
      <BaseCard
        v-for="evt in events"
        :key="evt.id"
        class="event-card"
      >
        <div class="event-content">
          <div class="event-date-col">
            <span class="event-day">{{ formatDay(evt.event_start) }}</span>
            <span class="event-month">{{ formatMonth(evt.event_start) }}</span>
          </div>

          <div class="event-details">
            <div class="event-header">
              <strong>{{ evt.title }}</strong>
              <BaseBadge v-if="evt.is_all_day" label="All Day" variant="info" size="sm" />
              <BaseBadge v-else-if="isToday(evt.event_start)" label="Today" variant="success" size="sm" />
            </div>

            <p v-if="!evt.is_all_day" class="event-time">
              <BaseIcon name="clock" :size="14" />
              {{ formatTime(evt.event_start) }} - {{ formatTime(evt.event_end) }}
            </p>

            <p v-if="evt.description" class="event-description">
              {{ evt.description }}
            </p>

            <p v-if="evt.location" class="event-location">
              <BaseIcon name="map-pin" :size="14" />
              {{ evt.location }}
            </p>
          </div>

          <div class="event-actions">
            <BaseButton variant="ghost" size="sm" icon="edit" icon-only @click="$emit('openModal', evt)" />
            <BaseButton variant="ghost" size="sm" icon="trash" icon-only @click="$emit('delete', evt.id)" />
          </div>
        </div>
      </BaseCard>
    </div>

    <!-- Empty State -->
    <BaseEmptyState
      v-else
      icon="calendar"
      variant="info"
      title="No events scheduled"
      description="Stay organized by scheduling your events, meetings, and important dates."
      action-label="Schedule Your First Event"
      @action="$emit('openModal')"
    />
  </section>
</template>

<script>
import { BaseCard, BaseIcon, BaseBadge, BaseButton, BaseEmptyState } from '../ui'

export default {
  name: 'PortalSchedule',
  components: { BaseCard, BaseIcon, BaseBadge, BaseButton, BaseEmptyState },
  props: {
    events: { type: Array, default: () => [] }
  },
  emits: ['openModal', 'delete'],
  methods: {
    formatDay(dt) {
      if (!dt) return ''
      return new Date(dt).getDate()
    },
    formatMonth(dt) {
      if (!dt) return ''
      return new Date(dt).toLocaleDateString(undefined, { month: 'short' })
    },
    formatTime(dt) {
      if (!dt) return ''
      return new Date(dt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    },
    isToday(dt) {
      if (!dt) return false
      const today = new Date()
      const date = new Date(dt)
      return (
        date.getFullYear() === today.getFullYear() &&
        date.getMonth() === today.getMonth() &&
        date.getDate() === today.getDate()
      )
    }
  }
}
</script>

<style scoped>
.schedule-section {
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

.events-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}

.event-content {
  display: flex;
  gap: var(--spacing-4);
}

.event-date-col {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-width: 60px;
  padding: var(--spacing-2);
  background: var(--color-primary-50);
  border-radius: var(--radius-lg);
  flex-shrink: 0;
}

.event-day {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-primary-600);
  line-height: 1;
}

.event-month {
  font-size: var(--font-size-xs);
  color: var(--color-primary-500);
  text-transform: uppercase;
}

.event-details {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-1);
}

.event-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  flex-wrap: wrap;
}

.event-header strong {
  font-size: var(--font-size-md);
}

.event-time,
.event-description,
.event-location {
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
  margin: 0;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.event-time {
  color: var(--color-text-tertiary);
}

.event-actions {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-1);
  flex-shrink: 0;
}

/* Responsive */
@media (max-width: 640px) {
  .section-header {
    flex-direction: column;
    align-items: stretch;
  }

  .event-content {
    flex-direction: column;
    gap: var(--spacing-3);
  }

  .event-date-col {
    flex-direction: row;
    gap: var(--spacing-2);
    width: fit-content;
  }

  .event-actions {
    flex-direction: row;
  }
}
</style>
