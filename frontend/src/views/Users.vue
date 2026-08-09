<template>
  <div class="users-page">
    <div class="page-header">
      <h1>Users</h1>
      <p>Manage all registered users</p>
    </div>
    <div v-if="loading" class="loading-state">Loading users...</div>
    <div v-else class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>Phone</th>
            <th>Agent</th>
            <th>Plan</th>
            <th>Status</th>
            <th>Model</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="users.length === 0">
            <td colspan="5" class="empty-state">No users found</td>
          </tr>
          <tr v-for="user in users" :key="user.id || user.phone">
            <td class="cell-phone">{{ user.phone || user.phone_number || '-' }}</td>
            <td class="cell-agent">{{ user.agent_name || user.agent || '-' }}</td>
            <td>
              <span class="plan-badge" :class="planClass(user.plan || user.subscription_plan)">
                {{ user.plan || user.subscription_plan || 'free' }}
              </span>
            </td>
            <td>
              <span class="status-badge" :class="statusClass(user.status || user.is_active)">
                {{ formatStatus(user.status || user.is_active) }}
              </span>
            </td>
            <td class="cell-model">{{ user.model || '-' }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
export default {
  name: 'UsersView',
  data() {
    return {
      loading: true,
      users: [],
    }
  },
  async mounted() {
    await this.fetchUsers()
  },
  methods: {
    async fetchUsers() {
      this.loading = true
      try {
        const token = localStorage.getItem('access_token')
        const res = await fetch('/api/admin/users', {
          headers: { Authorization: `Bearer ${token}` },
        })
        if (res.status === 401) {
          localStorage.removeItem('access_token')
          this.$router.push('/login')
          return
        }
        if (!res.ok) throw new Error('Failed to fetch users')
        const data = await res.json()
        this.users = Array.isArray(data) ? data : (data.users || data.data || [])
      } catch (err) {
        console.error('Users error:', err)
      } finally {
        this.loading = false
      }
    },
    planClass(plan) {
      if (!plan) return ''
      const p = plan.toLowerCase()
      if (p === 'pro' || p === 'business') return 'badge-pro'
      if (p === 'basic') return 'badge-basic'
      if (p === 'trial') return 'badge-trial'
      return ''
    },
    statusClass(status) {
      if (status === true || status === 'active' || status === 1) return 'status-active'
      return 'status-inactive'
    },
    formatStatus(status) {
      if (status === true || status === 1) return 'Active'
      if (status === false || status === 0) return 'Inactive'
      return status || 'Unknown'
    },
  },
}
</script>

<style scoped>
.users-page {
  max-width: 1100px;
}

.page-header {
  margin-bottom: 24px;
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

.table-container {
  background: #fff;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.data-table thead {
  background: #F8FAFC;
}

.data-table th {
  padding: 14px 20px;
  text-align: left;
  font-weight: 600;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #636E70;
  border-bottom: 1px solid #E2E8F0;
}

.data-table td {
  padding: 14px 20px;
  color: #1A1A2E;
  border-bottom: 1px solid #F0F2F5;
}

.data-table tbody tr:last-child td {
  border-bottom: none;
}

.data-table tbody tr:hover {
  background: #FAFBFC;
}

.cell-phone {
  font-family: 'SF Mono', 'Menlo', monospace;
  font-size: 13px;
}

.cell-agent {
  font-weight: 500;
}

.cell-model {
  font-family: 'SF Mono', 'Menlo', monospace;
  font-size: 13px;
  color: #636E70;
}

.plan-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  text-transform: capitalize;
  background: #F0F2F5;
  color: #636E70;
}

.plan-badge.badge-trial {
  background: rgba(108, 92, 231, 0.1);
  color: #6C5CE7;
}

.plan-badge.badge-basic {
  background: rgba(59, 130, 246, 0.1);
  color: #3B82F6;
}

.plan-badge.badge-pro {
  background: rgba(0, 200, 117, 0.1);
  color: #00C875;
}

.status-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.status-active {
  background: rgba(0, 200, 117, 0.1);
  color: #00C875;
}

.status-inactive {
  background: rgba(255, 107, 107, 0.1);
  color: #E53E3E;
}

.empty-state {
  text-align: center;
  padding: 40px 20px !important;
  color: #636E70;
  font-size: 14px;
}
</style>
