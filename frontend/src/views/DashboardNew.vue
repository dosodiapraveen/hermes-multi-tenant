<template>
  <div class="dashboard">
    <div class="page-header">
      <h1>Dashboard</h1>
      <p>Overview of your platform metrics</p>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-grid">
      <div v-for="i in 4" :key="i" class="skeleton-card"></div>
    </div>

    <!-- Stats Cards -->
    <div v-else class="stats-grid">
      <router-link to="/users" class="stat-card">
        <div class="stat-icon users">
          <BaseIcon name="users" :size="22" />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.active_users }}</div>
          <div class="stat-label">Active Users</div>
        </div>
        <div class="stat-trend up">
          <BaseIcon name="chevron-up" :size="14" />
          <span>12%</span>
        </div>
      </router-link>

      <router-link to="/users" class="stat-card">
        <div class="stat-icon agents">
          <BaseIcon name="settings" :size="22" />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.total_agents }}</div>
          <div class="stat-label">Total Agents</div>
        </div>
      </router-link>

      <router-link to="/settings" class="stat-card">
        <div class="stat-icon tokens">
          <BaseIcon name="activity" :size="22" />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ formatTokens(stats.tokens_today) }}</div>
          <div class="stat-label">Tokens Today</div>
        </div>
        <div class="stat-trend" :class="tokensTrend > 0 ? 'up' : 'down'">
          <BaseIcon :name="tokensTrend > 0 ? 'chevron-up' : 'chevron-down'" :size="14" />
          <span>{{ Math.abs(tokensTrend) }}%</span>
        </div>
      </router-link>

      <router-link to="/users" class="stat-card">
        <div class="stat-icon total">
          <BaseIcon name="user" :size="22" />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.total_users }}</div>
          <div class="stat-label">Total Users</div>
        </div>
      </router-link>
    </div>

    <!-- Charts Section -->
    <div v-if="!loading" class="charts-section">
      <!-- Token Usage Chart -->
      <BaseCard title="Token Usage (Last 7 Days)" icon="activity">
        <BaseChart
          type="line"
          :data="tokenChartData"
          :height="220"
          color="var(--color-primary-500)"
          :format-value="formatTokens"
        />
      </BaseCard>

      <!-- User Activity Chart -->
      <BaseCard title="User Activity" icon="users">
        <BaseChart
          type="bar"
          :data="activityChartData"
          :height="220"
          color="var(--color-success-500)"
        />
      </BaseCard>
    </div>

    <!-- Recent Activity -->
    <div v-if="!loading" class="recent-section">
      <BaseCard title="Recent Activity" icon="clock">
        <div v-if="recentActivity.length" class="activity-list">
          <div v-for="item in recentActivity" :key="item.id" class="activity-item">
            <div :class="['activity-icon', item.type]">
              <BaseIcon :name="getActivityIcon(item.type)" :size="16" />
            </div>
            <div class="activity-content">
              <span class="activity-text">{{ item.text }}</span>
              <span class="activity-time">{{ item.time }}</span>
            </div>
          </div>
        </div>
        <BaseEmptyState
          v-else
          compact
          icon="activity"
          title="No recent activity"
          description="Activity will appear here as users interact with the platform."
        />
      </BaseCard>

      <!-- Quick Actions -->
      <BaseCard title="Quick Actions" icon="settings">
        <div class="quick-actions">
          <router-link to="/invites" class="action-btn">
            <BaseIcon name="mail" :size="18" />
            <span>Send Invite</span>
          </router-link>
          <router-link to="/users" class="action-btn">
            <BaseIcon name="user" :size="18" />
            <span>Manage Users</span>
          </router-link>
          <router-link to="/registration-requests" class="action-btn">
            <BaseIcon name="clock" :size="18" />
            <span>Review Requests</span>
          </router-link>
          <router-link to="/settings" class="action-btn">
            <BaseIcon name="settings" :size="18" />
            <span>Settings</span>
          </router-link>
        </div>
      </BaseCard>
    </div>
  </div>
</template>

<script>
import { BaseIcon, BaseCard, BaseEmptyState } from '../components/ui'
import BaseChart from '../components/ui/BaseChart.vue'

export default {
  name: 'Dashboard',
  components: { BaseIcon, BaseCard, BaseChart, BaseEmptyState },
  data() {
    return {
      loading: true,
      stats: {
        active_users: 0,
        total_agents: 0,
        tokens_today: 0,
        total_users: 0
      },
      tokensTrend: 8,
      tokenChartData: [],
      activityChartData: [],
      recentActivity: []
    }
  },
  async mounted() {
    try {
      const r = await fetch('/api/admin/dashboard', {
        headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token') }
      })
      if (r.status === 401) {
        localStorage.removeItem('token')
        this.$router.push('/login')
        return
      }
      const d = await r.json()
      this.stats = {
        active_users: d.active_users || 0,
        total_agents: d.total_agents || 0,
        tokens_today: d.tokens_today || 0,
        total_users: d.total_users || 0
      }

      // Generate sample chart data (replace with real API data)
      this.generateChartData()
      this.generateActivityData()
    } catch (e) {
      console.error(e)
    } finally {
      this.loading = false
    }
  },
  methods: {
    formatTokens(value) {
      if (value >= 1000000) return (value / 1000000).toFixed(1) + 'M'
      if (value >= 1000) return (value / 1000).toFixed(1) + 'K'
      return value.toString()
    },

    generateChartData() {
      const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
      const baseValue = this.stats.tokens_today || 1000

      this.tokenChartData = days.map((day, i) => ({
        label: day,
        value: Math.round(baseValue * (0.5 + Math.random() * 0.8))
      }))

      this.activityChartData = days.map((day, i) => ({
        label: day,
        value: Math.round((this.stats.active_users || 10) * (0.6 + Math.random() * 0.6))
      }))
    },

    generateActivityData() {
      this.recentActivity = [
        { id: 1, type: 'user', text: 'New user registered', time: '2 minutes ago' },
        { id: 2, type: 'agent', text: 'Agent configuration updated', time: '15 minutes ago' },
        { id: 3, type: 'message', text: '125 messages processed', time: '1 hour ago' },
        { id: 4, type: 'user', text: 'User verification completed', time: '2 hours ago' },
        { id: 5, type: 'system', text: 'System backup completed', time: '6 hours ago' }
      ]
    },

    getActivityIcon(type) {
      const icons = {
        user: 'user',
        agent: 'settings',
        message: 'mail',
        system: 'activity'
      }
      return icons[type] || 'activity'
    }
  }
}
</script>

<style scoped>
.dashboard {
  max-width: 1100px;
}

.page-header {
  margin-bottom: var(--spacing-6);
}

.page-header h1 {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  margin: 0 0 var(--spacing-1);
}

.page-header p {
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
  margin: 0;
}

/* Loading */
.loading-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--spacing-4);
}

.skeleton-card {
  height: 120px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  border-radius: var(--radius-xl);
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--spacing-4);
  margin-bottom: var(--spacing-6);
}

.stat-card {
  display: flex;
  align-items: center;
  gap: var(--spacing-4);
  padding: var(--spacing-5);
  background: var(--color-surface);
  border-radius: var(--radius-xl);
  border: 1px solid var(--color-border-light);
  text-decoration: none;
  color: inherit;
  transition: all var(--transition-fast);
}

.stat-card:hover {
  border-color: var(--color-primary-300);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-xl);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon.users {
  background: var(--color-primary-200);
  color: var(--color-primary-700);
}

.stat-icon.agents {
  background: var(--color-success-200);
  color: var(--color-success-700);
}

.stat-icon.tokens {
  background: var(--color-warning-200);
  color: var(--color-warning-700);
}

.stat-icon.total {
  background: var(--color-info-200);
  color: var(--color-info-700);
}

.stat-info {
  flex: 1;
  min-width: 0;
}

.stat-value {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  line-height: 1.1;
}

.stat-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
  margin-top: var(--spacing-1);
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 2px;
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  padding: var(--spacing-1) var(--spacing-2);
  border-radius: var(--radius-full);
}

.stat-trend.up {
  background: var(--color-success-200);
  color: var(--color-success-700);
}

.stat-trend.down {
  background: var(--color-error-200);
  color: var(--color-error-700);
}

/* Charts Section */
.charts-section {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-4);
  margin-bottom: var(--spacing-6);
}

/* Recent Section */
.recent-section {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: var(--spacing-4);
}

/* Activity List */
.activity-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}

.activity-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  padding: var(--spacing-3);
  background: var(--color-gray-50);
  border-radius: var(--radius-lg);
}

.activity-icon {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.activity-icon.user {
  background: var(--color-primary-200);
  color: var(--color-primary-700);
}

.activity-icon.agent {
  background: var(--color-success-200);
  color: var(--color-success-700);
}

.activity-icon.message {
  background: var(--color-info-200);
  color: var(--color-info-700);
}

.activity-icon.system {
  background: var(--color-gray-200);
  color: var(--color-gray-600);
}

.activity-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.activity-text {
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
}

.activity-time {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

/* Quick Actions */
.quick-actions {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-3);
}

.action-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-2);
  padding: var(--spacing-4);
  background: var(--color-gray-50);
  border-radius: var(--radius-lg);
  text-decoration: none;
  color: var(--color-text-secondary);
  transition: all var(--transition-fast);
}

.action-btn:hover {
  background: var(--color-primary-50);
  color: var(--color-primary-600);
}

.action-btn span {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
}

/* Responsive */
@media (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .charts-section {
    grid-template-columns: 1fr;
  }

  .recent-section {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .loading-grid {
    grid-template-columns: 1fr;
  }
}
</style>
