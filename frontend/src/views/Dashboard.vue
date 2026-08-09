<template>
  <div class="dashboard">
    <div class="page-header">
      <h1>Dashboard</h1>
      <p>Overview of your platform metrics</p>
    </div>
    <div v-if="loading" class="loading-state">Loading dashboard data...</div>
    <div v-else class="stat-cards">
      <div class="stat-card">
        <div class="stat-icon active-users">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/></svg>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.active_users }}</span>
          <span class="stat-label">Active Users</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon total-agents">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.total_agents }}</span>
          <span class="stat-label">Total Agents</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon tokens-today">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.tokens_today }}</span>
          <span class="stat-label">Tokens Today</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon total-users">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.total_users }}</span>
          <span class="stat-label">Total Users</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DashboardView',
  data() {
    return {
      loading: true,
      stats: {
        active_users: 0,
        total_agents: 0,
        tokens_today: 0,
        total_users: 0,
      },
    }
  },
  async mounted() {
    await this.fetchDashboard()
  },
  methods: {
    async fetchDashboard() {
      this.loading = true
      try {
        const token = localStorage.getItem('access_token')
        const res = await fetch('/api/admin/dashboard', {
          headers: { Authorization: `Bearer ${token}` },
        })
        if (res.status === 401) {
          localStorage.removeItem('access_token')
          this.$router.push('/login')
          return
        }
        if (!res.ok) throw new Error('Failed to fetch dashboard')
        const data = await res.json()
        this.stats = {
          active_users: data.active_users ?? 0,
          total_agents: data.total_agents ?? 0,
          tokens_today: data.tokens_today ?? 0,
          total_users: data.total_users ?? 0,
        }
      } catch (err) {
        console.error('Dashboard error:', err)
      } finally {
        this.loading = false
      }
    },
  },
}
</script>

<style scoped>
.dashboard {
  max-width: 1000px;
}

.page-header {
  margin-bottom: 28px;
}

.page-header h1 {
  font-size: 26px;
  font-weight: 700;
  color: #1A1A2E;
  margin-bottom: 4px;
}

.page-header p {
  font-size: 14px;
  color: #636E70;
}

.loading-state {
  text-align: center;
  padding: 60px 20px;
  color: #636E70;
  font-size: 15px;
}

.stat-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.stat-card {
  background: #fff;
  border-radius: 14px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon.active-users {
  background: rgba(108, 92, 231, 0.1);
  color: #6C5CE7;
}

.stat-icon.total-agents {
  background: rgba(0, 200, 117, 0.1);
  color: #00C875;
}

.stat-icon.tokens-today {
  background: rgba(255, 170, 0, 0.1);
  color: #FFAA00;
}

.stat-icon.total-users {
  background: rgba(59, 130, 246, 0.1);
  color: #3B82F6;
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-value {
  font-size: 28px;
  font-weight: 800;
  color: #1A1A2E;
  line-height: 1.1;
}

.stat-label {
  font-size: 13px;
  font-weight: 500;
  color: #636E70;
}
</style>
