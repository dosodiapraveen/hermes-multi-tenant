<template>
  <div class="invites-page">
    <div class="page-header">
      <div>
        <h1>Invite Links</h1>
        <p>Create and manage invitation links</p>
      </div>
      <button class="create-btn" @click="showForm = !showForm">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        New Invite
      </button>
    </div>

    <div v-if="showForm" class="create-form">
      <h3>Create Invite Link</h3>
      <form @submit.prevent="createInvite">
        <div class="form-row">
          <div class="form-group">
            <label>Label</label>
            <input v-model="form.label" placeholder="e.g. Beta Tester Batch 3" required />
          </div>
          <div class="form-group">
            <label>Agent Name</label>
            <input v-model="form.agent_name" placeholder="e.g. hermes-3" required />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>Plan</label>
            <select v-model="form.plan" required>
              <option value="trial">Trial</option>
              <option value="basic">Basic</option>
              <option value="pro">Pro</option>
              <option value="business">Business</option>
            </select>
          </div>
          <div class="form-group">
            <label>Trial Days</label>
            <input v-model.number="form.trial_days" type="number" min="0" placeholder="7" />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group checkbox-group">
            <label class="checkbox-label">
              <input v-model="form.is_vip" type="checkbox" />
              <span>VIP Access</span>
            </label>
          </div>
        </div>
        <div v-if="formError" class="error-message">{{ formError }}</div>
        <div class="form-actions">
          <button type="button" class="cancel-btn" @click="showForm = false">Cancel</button>
          <button type="submit" class="submit-btn" :disabled="creating">
            <span v-if="creating" class="spinner"></span>
            <span v-else>Create Link</span>
          </button>
        </div>
      </form>
    </div>

    <div v-if="loading" class="loading-state">Loading invite links...</div>
    <div v-else class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>Label</th>
            <th>Agent</th>
            <th>Plan</th>
            <th>Status</th>
            <th>Link</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="invites.length === 0">
            <td colspan="6" class="empty-state">No invite links created yet</td>
          </tr>
          <tr v-for="invite in invites" :key="invite.id || invite.code">
            <td class="cell-label">{{ invite.label || '-' }}</td>
            <td>{{ invite.agent_name || invite.agent || '-' }}</td>
            <td>
              <span class="plan-badge" :class="'badge-' + (invite.plan || 'trial')">
                {{ invite.plan || 'trial' }}
              </span>
            </td>
            <td>
              <span class="status-badge" :class="invite.claimed ? 'status-claimed' : 'status-active'">
                {{ invite.claimed ? 'Claimed' : 'Active' }}
              </span>
            </td>
            <td class="cell-link">
              <span class="link-text">{{ invite.url || invite.link_url || '-' }}</span>
            </td>
            <td>
              <button
                v-if="invite.url || invite.link_url"
                class="copy-btn"
                @click="copyLink(invite.url || invite.link_url)"
              >
                {{ copiedId === (invite.id || invite.code) ? 'Copied!' : 'Copy' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
export default {
  name: 'InvitesView',
  data() {
    return {
      loading: true,
      creating: false,
      showForm: false,
      formError: '',
      copiedId: null,
      invites: [],
      form: {
        label: '',
        agent_name: '',
        plan: 'trial',
        trial_days: 7,
        is_vip: false,
      },
    }
  },
  async mounted() {
    await this.fetchInvites()
  },
  methods: {
    async fetchInvites() {
      this.loading = true
      try {
        const token = localStorage.getItem('token')
        const res = await fetch('/api/admin/invite-links', {
          headers: { Authorization: `Bearer ${token}` },
        })
        if (res.status === 401) {
          localStorage.removeItem('token')
          this.$router.push('/login')
          return
        }
        if (!res.ok) throw new Error('Failed to fetch invites')
        const data = await res.json()
        this.invites = Array.isArray(data) ? data : (data.invites || data.data || [])
      } catch (err) {
        console.error('Invites error:', err)
      } finally {
        this.loading = false
      }
    },
    async createInvite() {
      this.creating = true
      this.formError = ''
      try {
        const token = localStorage.getItem('token')
        const res = await fetch('/api/admin/invite-links', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            label: this.form.label,
            agent_name: this.form.agent_name,
            plan: this.form.plan,
            trial_days: this.form.trial_days,
            is_vip: this.form.is_vip,
          }),
        })
        if (!res.ok) {
          const data = await res.json().catch(() => ({}))
          throw new Error(data.detail || data.message || 'Failed to create invite')
        }
        this.form = { label: '', agent_name: '', plan: 'trial', trial_days: 7, is_vip: false }
        this.showForm = false
        await this.fetchInvites()
      } catch (err) {
        this.formError = err.message
      } finally {
        this.creating = false
      }
    },
    copyLink(url) {
      navigator.clipboard.writeText(url).then(() => {
        this.copiedId = Date.now()
        setTimeout(() => { this.copiedId = null }, 2000)
      }).catch(() => {
        alert('Failed to copy link')
      })
    },
  },
}
</script>

<style scoped>
.invites-page {
  max-width: 1100px;
}

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
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

.create-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border: none;
  background: #6C5CE7;
  color: #fff;
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  font-weight: 600;
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.2s;
}

.create-btn:hover {
  background: #5A4BD1;
}

.create-form {
  background: #fff;
  border-radius: 14px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

.create-form h3 {
  font-size: 16px;
  font-weight: 700;
  color: #1A1A2E;
  margin-bottom: 20px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 13px;
  font-weight: 600;
  color: #1A1A2E;
}

.form-group input,
.form-group select {
  padding: 10px 14px;
  border: 1.5px solid #E2E8F0;
  border-radius: 8px;
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  color: #1A1A2E;
  outline: none;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group select:focus {
  border-color: #6C5CE7;
  box-shadow: 0 0 0 3px rgba(108, 92, 231, 0.1);
}

.checkbox-group {
  justify-content: center;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: #1A1A2E;
}

.checkbox-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  accent-color: #6C5CE7;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 8px;
}

.cancel-btn {
  padding: 10px 20px;
  border: 1.5px solid #E2E8F0;
  background: #fff;
  color: #636E70;
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  font-weight: 500;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s;
}

.cancel-btn:hover {
  background: #F8FAFC;
}

.submit-btn {
  padding: 10px 24px;
  border: none;
  background: #6C5CE7;
  color: #fff;
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  font-weight: 600;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.submit-btn:hover:not(:disabled) {
  background: #5A4BD1;
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  background: #FFF5F5;
  color: #E53E3E;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 12px;
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

.cell-label {
  font-weight: 500;
}

.cell-link {
  max-width: 220px;
}

.link-text {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-family: 'SF Mono', 'Menlo', monospace;
  font-size: 12px;
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

.plan-badge.badge-business {
  background: rgba(255, 170, 0, 0.1);
  color: #D69E2E;
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

.status-claimed {
  background: rgba(108, 92, 231, 0.1);
  color: #6C5CE7;
}

.copy-btn {
  padding: 6px 14px;
  border: 1.5px solid #E2E8F0;
  background: #fff;
  color: #6C5CE7;
  font-family: 'Inter', sans-serif;
  font-size: 12px;
  font-weight: 600;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s;
}

.copy-btn:hover {
  background: rgba(108, 92, 231, 0.05);
  border-color: #6C5CE7;
}

.empty-state {
  text-align: center;
  padding: 40px 20px !important;
  color: #636E70;
  font-size: 14px;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
