<template>
  <section class="activity-section">
    <div class="section-header">
      <h2>
        <BaseIcon name="activity" :size="24" />
        Activity
      </h2>
    </div>

    <!-- Activity Timeline -->
    <div v-if="groupedActivity.length" class="activity-timeline">
      <div v-for="group in groupedActivity" :key="group.date" class="activity-day">
        <div class="day-header">{{ group.label }}</div>

        <div class="day-items">
          <div v-for="item in group.items" :key="item.key" class="activity-item">
            <div :class="['activity-icon', `icon-${item.type}`]">
              <BaseIcon :name="item.icon" :size="14" />
            </div>
            <div class="activity-content">
              <span class="activity-title">
                {{ item.title }}
                <em v-if="item.count > 1" class="activity-count">x{{ item.count }}</em>
              </span>
              <span class="activity-time">{{ item.time }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <BaseEmptyState
      v-else
      icon="activity"
      variant="info"
      title="No activity yet"
      description="Your activity timeline will appear here as you use the dashboard."
    />
  </section>
</template>

<script>
import { BaseIcon, BaseEmptyState } from '../ui'

export default {
  name: 'PortalActivity',
  components: { BaseIcon, BaseEmptyState },
  props: {
    activity: { type: Array, default: () => [] }
  },
  computed: {
    groupedActivity() {
      const days = {}

      for (const a of this.activity || []) {
        const date = (a.time || '').slice(0, 10)
        if (!date) continue

        if (!days[date]) {
          days[date] = { map: {}, arr: [] }
        }

        const d = days[date]
        const key = a.action || ''

        if (d.map[key]) {
          d.map[key].count++
        } else {
          const item = {
            key,
            title: a.action || 'Activity',
            icon: this.getIcon(a.action),
            type: this.getType(a.action),
            time: (a.time || '').slice(11, 16),
            count: 1
          }
          d.map[key] = item
          d.arr.push(item)
        }
      }

      return Object.keys(days)
        .sort((x, y) => y.localeCompare(x))
        .map(k => ({
          date: k,
          label: this.dayLabel(k),
          items: days[k].arr
        }))
    }
  },
  methods: {
    getIcon(action) {
      const s = (action || '').toLowerCase()
      if (s.includes('note')) return 'file-text'
      if (s.includes('project')) return 'folder'
      if (s.includes('search')) return 'search'
      if (s.includes('remind')) return 'clock'
      if (s.includes('idea')) return 'lightbulb'
      if (s.includes('event') || s.includes('calendar') || s.includes('schedule')) return 'calendar'
      if (s.includes('upload') || s.includes('document') || s.includes('pdf')) return 'file-text'
      if (s.includes('message') || s.includes('chat') || s.includes('telegram') || s.includes('sent')) return 'mail'
      if (s.includes('login') || s.includes('auth')) return 'user'
      return 'activity'
    },
    getType(action) {
      const s = (action || '').toLowerCase()
      if (s.includes('note')) return 'notes'
      if (s.includes('project')) return 'projects'
      if (s.includes('idea')) return 'ideas'
      if (s.includes('remind')) return 'reminders'
      if (s.includes('event') || s.includes('schedule')) return 'schedule'
      return 'default'
    },
    dayLabel(date) {
      const today = new Date().toISOString().slice(0, 10)
      if (date === today) return 'Today'

      const d = new Date(Date.UTC(+date.slice(0, 4), +date.slice(5, 7) - 1, +date.slice(8, 10)))
      return d.toLocaleDateString(undefined, { weekday: 'long', month: 'short', day: 'numeric' })
    }
  }
}
</script>

<style scoped>
.activity-section {
  display: flex;
  flex-direction: column;
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

.activity-timeline {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-6);
}

.activity-day {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}

.day-header {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-bold);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--color-text-tertiary);
}

.day-items {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.activity-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  padding: var(--spacing-3) var(--spacing-4);
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xs);
}

.activity-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: var(--radius-md);
  flex-shrink: 0;
}

.activity-icon.icon-default {
  background: var(--color-gray-100);
  color: var(--color-gray-600);
}

.activity-icon.icon-notes {
  background: var(--color-primary-100);
  color: var(--color-primary-600);
}

.activity-icon.icon-projects {
  background: var(--color-success-100);
  color: var(--color-success-600);
}

.activity-icon.icon-ideas {
  background: var(--color-warning-100);
  color: var(--color-warning-600);
}

.activity-icon.icon-reminders {
  background: var(--color-error-100);
  color: var(--color-error-600);
}

.activity-icon.icon-schedule {
  background: var(--color-info-100);
  color: var(--color-info-600);
}

.activity-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-1);
  min-width: 0;
}

.activity-title {
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
}

.activity-count {
  font-style: normal;
  color: var(--color-text-tertiary);
  font-size: var(--font-size-xs);
  margin-left: var(--spacing-1);
}

.activity-time {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}
</style>
