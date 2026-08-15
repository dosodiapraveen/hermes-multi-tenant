<template>
  <section class="dashboard-section">
    <!-- Smart Search -->
    <BaseCard class="search-card" no-padding>
      <div class="search-container">
        <BaseSearchFilter
          v-model:search="searchQ"
          placeholder="Search everything — notes, projects, ideas..."
          :show-search-button="true"
          @search="doSearch"
        />

        <p v-if="searching" class="search-status">
          <BaseIcon name="loader" :size="16" spin />
          Searching your data...
        </p>
        <p v-if="searchError" class="search-status error">{{ searchError }}</p>

        <div v-if="searchResults.length" class="search-results">
          <div class="results-header">Top matches</div>
          <div
            v-for="r in searchResults"
            :key="r.type + '-' + r.id"
            class="result-item"
            @click="$emit('gotoResult', r)"
          >
            <BaseBadge :label="typeLabel(r.type)" :variant="typeVariant(r.type)" size="sm" />
            <div class="result-body">
              <strong>{{ r.title || '(untitled)' }}</strong>
              <p>{{ snippet(r.content) }}</p>
            </div>
            <span class="result-score">{{ Math.round(r.score * 100) }}%</span>
          </div>
          <button class="clear-results" @click="clearSearch">Clear results</button>
        </div>
      </div>
    </BaseCard>

    <!-- Stats Grid -->
    <div class="stats-grid">
      <BaseCard clickable @click="$emit('changeTab', 'ideas')">
        <div class="stat-content">
          <div class="stat-icon ideas">
            <BaseIcon name="lightbulb" :size="24" />
          </div>
          <div class="stat-info">
            <span class="stat-label">Ideas</span>
            <span class="stat-value">{{ ideas.length }}</span>
          </div>
        </div>
      </BaseCard>

      <BaseCard clickable @click="$emit('changeTab', 'notes')">
        <div class="stat-content">
          <div class="stat-icon notes">
            <BaseIcon name="file-text" :size="24" />
          </div>
          <div class="stat-info">
            <span class="stat-label">Notes</span>
            <span class="stat-value">{{ notes.length }}</span>
          </div>
        </div>
      </BaseCard>

      <BaseCard clickable @click="$emit('changeTab', 'reminders')">
        <div class="stat-content">
          <div class="stat-icon reminders">
            <BaseIcon name="clock" :size="24" />
          </div>
          <div class="stat-info">
            <span class="stat-label">Pending</span>
            <span class="stat-value">{{ pendingReminders }}</span>
          </div>
        </div>
      </BaseCard>

      <BaseCard clickable @click="$emit('changeTab', 'projects')">
        <div class="stat-content">
          <div class="stat-icon projects">
            <BaseIcon name="folder" :size="24" />
          </div>
          <div class="stat-info">
            <span class="stat-label">Projects</span>
            <span class="stat-value">{{ projects.length }}</span>
          </div>
        </div>
      </BaseCard>
    </div>

    <!-- Upcoming Events Widget -->
    <div class="widget">
      <div class="widget-header">
        <BaseIcon name="calendar" :size="18" />
        <h3>Upcoming Events</h3>
      </div>
      <BaseCard v-if="upcomingEvents.length" no-padding>
        <div
          v-for="evt in upcomingEvents"
          :key="evt.id"
          class="widget-item"
          @click="$emit('changeTab', 'schedule')"
        >
          <BaseBadge
            :label="relativeDate(evt.event_start)"
            :variant="relativeDate(evt.event_start) === 'Today' ? 'success' : 'primary'"
            size="sm"
          />
          <strong>{{ evt.title }}</strong>
          <span v-if="evt.location" class="item-meta">
            <BaseIcon name="map-pin" :size="12" />
            {{ evt.location }}
          </span>
        </div>
      </BaseCard>
      <BaseEmptyState
        v-else
        compact
        icon="calendar"
        title="No upcoming events"
        action-label="Schedule one now"
        @action="$emit('changeTab', 'schedule')"
      />
    </div>

    <!-- Recent Ideas Widget -->
    <div class="widget">
      <div class="widget-header">
        <BaseIcon name="lightbulb" :size="18" />
        <h3>Recent Ideas</h3>
      </div>
      <BaseCard v-if="recentIdeas.length" no-padding>
        <div
          v-for="idea in recentIdeas"
          :key="idea.id"
          class="widget-item"
          @click="$emit('changeTab', 'ideas')"
        >
          <BaseBadge :label="statusLabel(idea.status)" :variant="idea.status" size="sm" />
          <strong>{{ idea.title }}</strong>
        </div>
      </BaseCard>
      <BaseEmptyState
        v-else
        compact
        icon="lightbulb"
        title="No ideas yet"
        action-label="Start brainstorming"
        @action="$emit('changeTab', 'ideas')"
      />
    </div>

    <!-- Failed Jobs Warning -->
    <div v-if="failedJobs.length" class="warning-banner">
      <BaseIcon name="alert-circle" :size="18" />
      <span><strong>{{ failedJobs.length }}</strong> background job(s) need attention</span>
      <BaseButton variant="ghost" size="sm" @click="$emit('changeTab', 'jobs')">
        View Jobs
      </BaseButton>
    </div>
  </section>
</template>

<script>
import { BaseCard, BaseIcon, BaseBadge, BaseButton, BaseEmptyState, BaseSearchFilter } from '../ui'

export default {
  name: 'PortalDashboard',
  components: { BaseCard, BaseIcon, BaseBadge, BaseButton, BaseEmptyState, BaseSearchFilter },
  props: {
    ideas: { type: Array, default: () => [] },
    notes: { type: Array, default: () => [] },
    reminders: { type: Array, default: () => [] },
    projects: { type: Array, default: () => [] },
    events: { type: Array, default: () => [] },
    jobs: { type: Array, default: () => [] }
  },
  emits: ['changeTab', 'gotoResult'],
  data() {
    return {
      searchQ: '',
      searchResults: [],
      searching: false,
      searchError: ''
    }
  },
  computed: {
    pendingReminders() {
      return this.reminders.filter(r => !r.done).length
    },
    upcomingEvents() {
      return this.events.slice(0, 3)
    },
    recentIdeas() {
      return this.ideas.filter(i => i.status === 'brainstorm').slice(0, 3)
    },
    failedJobs() {
      return this.jobs.filter(j => j.last_result && j.last_result.includes('fail'))
    }
  },
  methods: {
    async doSearch() {
      const q = this.searchQ.trim()
      if (!q) return

      this.searching = true
      this.searchError = ''

      try {
        const token = localStorage.getItem('portal_token')
        const r = await fetch(`/api/me/search?q=${encodeURIComponent(q)}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        const d = await r.json()

        if (d && d.results) {
          this.searchResults = d.results
        } else {
          this.searchError = d?.error || 'Search failed'
        }
      } catch (e) {
        this.searchError = 'Search failed'
      } finally {
        this.searching = false
      }
    },

    clearSearch() {
      this.searchResults = []
      this.searchQ = ''
    },

    typeLabel(t) {
      const labels = {
        note: 'Note',
        project: 'Project',
        research: 'Research',
        idea: 'Idea',
        reminder: 'Reminder',
        vault: 'Vault'
      }
      return labels[t] || t
    },

    typeVariant(t) {
      const variants = {
        note: 'primary',
        project: 'success',
        research: 'info',
        idea: 'warning',
        reminder: 'error',
        vault: 'default'
      }
      return variants[t] || 'default'
    },

    snippet(s) {
      return (s || '').replace(/\n+/g, ' ').slice(0, 160)
    },

    statusLabel(s) {
      const labels = {
        brainstorm: 'Brainstorm',
        developing: 'Developing',
        ready: 'Ready',
        archived: 'Archived'
      }
      return labels[s] || s
    },

    relativeDate(dateStr) {
      if (!dateStr) return ''
      const now = new Date()
      const target = new Date(dateStr)
      const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
      const targetDay = new Date(target.getFullYear(), target.getMonth(), target.getDate())
      const diff = Math.round((targetDay - today) / (1000 * 60 * 60 * 24))

      if (diff === 0) return 'Today'
      if (diff === 1) return 'Tomorrow'
      if (diff === -1) return 'Yesterday'
      if (diff > 1 && diff <= 7) return `In ${diff} days`
      if (diff < -1 && diff >= -7) return `${Math.abs(diff)} days ago`
      return target.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
    }
  }
}
</script>

<style scoped>
.dashboard-section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-5);
}

/* Search */
.search-card {
  padding: var(--spacing-4);
}

.search-container {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}

.search-status {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
  margin: 0;
}

.search-status.error {
  color: var(--color-error-600);
}

.search-results {
  border-top: 1px solid var(--color-border-light);
  padding-top: var(--spacing-3);
}

.results-header {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: var(--spacing-2);
}

.result-item {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-3);
  padding: var(--spacing-3);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: background var(--transition-fast);
}

.result-item:hover {
  background: var(--color-primary-50);
}

.result-body {
  flex: 1;
  min-width: 0;
}

.result-body strong {
  display: block;
  font-size: var(--font-size-sm);
}

.result-body p {
  margin: var(--spacing-1) 0 0;
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.result-score {
  font-size: var(--font-size-xs);
  color: var(--color-success-600);
  font-weight: var(--font-weight-medium);
}

.clear-results {
  margin-top: var(--spacing-2);
  padding: 0;
  background: none;
  border: none;
  color: var(--color-primary-500);
  font-size: var(--font-size-sm);
  cursor: pointer;
}

.clear-results:hover {
  text-decoration: underline;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: var(--spacing-3);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: var(--spacing-4);
}

.stat-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-xl);
  flex-shrink: 0;
}

.stat-icon.ideas {
  background: var(--color-warning-200);
  color: var(--color-warning-700);
}

.stat-icon.notes {
  background: var(--color-primary-200);
  color: var(--color-primary-700);
}

.stat-icon.reminders {
  background: var(--color-error-200);
  color: var(--color-error-700);
}

.stat-icon.projects {
  background: var(--color-success-200);
  color: var(--color-success-700);
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
}

.stat-value {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-primary-500);
}

/* Widgets */
.widget {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}

.widget-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  color: var(--color-text-secondary);
}

.widget-header h3 {
  margin: 0;
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
}

.widget-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  padding: var(--spacing-3) var(--spacing-4);
  border-bottom: 1px solid var(--color-border-light);
  cursor: pointer;
  transition: background var(--transition-fast);
}

.widget-item:last-child {
  border-bottom: none;
}

.widget-item:hover {
  background: var(--color-surface-hover);
}

.widget-item strong {
  flex: 1;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
}

.item-meta {
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

/* Warning Banner */
.warning-banner {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  padding: var(--spacing-3) var(--spacing-4);
  background: var(--color-warning-200);
  color: var(--color-warning-700);
  border-radius: var(--radius-lg);
  border-left: 4px solid var(--color-warning-500);
}

.warning-banner span {
  flex: 1;
  font-size: var(--font-size-sm);
}

/* Responsive */
@media (max-width: 640px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .stat-content {
    flex-direction: column;
    text-align: center;
    gap: var(--spacing-2);
  }
}
</style>
