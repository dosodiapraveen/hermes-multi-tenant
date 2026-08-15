<template>
  <section class="jobs-section">
    <div class="section-header">
      <h2>
        <BaseIcon name="settings" :size="24" />
        Background Jobs
      </h2>
      <BaseButton icon="plus" @click="$emit('openModal')">
        New Job
      </BaseButton>
    </div>

    <!-- Jobs Table -->
    <BaseCard v-if="jobs.length" no-padding class="jobs-table-card">
      <div class="jobs-table">
        <div class="job-row job-header-row">
          <div class="job-col job-title-col">Job</div>
          <div class="job-col job-type-col">Type</div>
          <div class="job-col job-schedule-col">Schedule</div>
          <div class="job-col job-next-col">Next Run</div>
          <div class="job-col job-status-col">Status</div>
          <div class="job-col job-actions-col">Actions</div>
        </div>

        <div v-for="job in jobs" :key="job.id" class="job-row">
          <div class="job-col job-title-col">
            <strong>{{ job.title }}</strong>
            <span class="job-description">{{ job.description }}</span>
          </div>
          <div class="job-col job-type-col">
            <BaseBadge :label="job.job_type" variant="default" size="sm" />
          </div>
          <div class="job-col job-schedule-col">
            <BaseTooltip :content="cronDescription(job.cron_expression)">
              <code class="cron-code">{{ job.cron_expression }}</code>
            </BaseTooltip>
          </div>
          <div class="job-col job-next-col">
            {{ formatJobDate(job.next_run_at) }}
          </div>
          <div class="job-col job-status-col">
            <BaseToggle
              :model-value="job.is_enabled"
              @change="$emit('toggle', job)"
            />
          </div>
          <div class="job-col job-actions-col">
            <BaseButton variant="ghost" size="sm" icon="edit" icon-only @click="$emit('openModal', job)" />
            <BaseButton variant="ghost" size="sm" icon="trash" icon-only @click="$emit('delete', job.id)" />
          </div>
        </div>
      </div>
    </BaseCard>

    <!-- Empty State -->
    <BaseEmptyState
      v-else
      icon="settings"
      variant="default"
      title="No background jobs"
      description="Automate recurring tasks with scheduled background jobs."
      action-label="Create Your First Job"
      @action="$emit('openModal')"
    />
  </section>
</template>

<script>
import { BaseCard, BaseIcon, BaseBadge, BaseButton, BaseToggle, BaseTooltip, BaseEmptyState } from '@design-system/components/ui'

export default {
  name: 'PortalJobs',
  components: { BaseCard, BaseIcon, BaseBadge, BaseButton, BaseToggle, BaseTooltip, BaseEmptyState },
  props: {
    jobs: { type: Array, default: () => [] }
  },
  emits: ['openModal', 'delete', 'toggle'],
  methods: {
    formatJobDate(dt) {
      if (!dt) return 'N/A'
      const d = new Date(dt)
      return d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    },
    cronDescription(cron) {
      const descriptions = {
        '0 9 * * *': 'Every day at 9:00 AM',
        '0 0 * * 1': 'Every Monday at midnight',
        '0 0 1 * *': 'First day of every month',
        '*/30 * * * *': 'Every 30 minutes',
        '0 */6 * * *': 'Every 6 hours'
      }
      return descriptions[cron] || 'Custom schedule'
    }
  }
}
</script>

<style scoped>
.jobs-section {
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

.jobs-table-card {
  overflow-x: auto;
}

.jobs-table {
  min-width: 700px;
}

.job-row {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  padding: var(--spacing-3) var(--spacing-4);
  border-bottom: 1px solid var(--color-border-light);
}

.job-row:last-child {
  border-bottom: none;
}

.job-header-row {
  background: var(--color-gray-50);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.job-col {
  display: flex;
  align-items: center;
}

.job-title-col {
  flex: 2;
  flex-direction: column;
  align-items: flex-start;
  gap: var(--spacing-1);
}

.job-title-col strong {
  font-size: var(--font-size-sm);
}

.job-description {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.job-type-col {
  flex: 1;
}

.job-schedule-col {
  flex: 1.5;
}

.cron-code {
  font-family: var(--font-family-mono);
  font-size: var(--font-size-xs);
  padding: var(--spacing-1) var(--spacing-2);
  background: var(--color-gray-100);
  border-radius: var(--radius-md);
  cursor: help;
}

.job-next-col {
  flex: 1.2;
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.job-status-col {
  flex: 0.6;
  justify-content: center;
}

.job-actions-col {
  flex: 1;
  justify-content: flex-end;
  gap: var(--spacing-1);
}

/* Responsive */
@media (max-width: 768px) {
  .section-header {
    flex-direction: column;
    align-items: stretch;
  }

  .jobs-table {
    min-width: 600px;
  }
}
</style>
