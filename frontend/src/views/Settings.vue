<template>
  <div class="settings-page">
    <div class="page-header">
      <h1>Settings</h1>
      <p>Configure AI model preferences</p>
    </div>

    <div v-if="loading" class="loading-state">Loading settings...</div>
    <div v-else class="settings-card">
      <h3>Model Configuration</h3>
      <p class="card-desc">Select the primary and backup AI models for agent responses.</p>
      <form @submit.prevent="saveSettings">
        <div class="form-group">
          <label for="primary-model">Primary Model</label>
          <select id="primary-model" v-model="primaryModel">
            <option value="" disabled>Select primary model</option>
            <option v-for="m in models" :key="m" :value="m">{{ m }}</option>
          </select>
          <span class="help-text">This model is used by default for all agent responses.</span>
        </div>
        <div class="form-group">
          <label for="backup-model">Backup Model</label>
          <select id="backup-model" v-model="backupModel">
            <option value="" disabled>Select backup model</option>
            <option v-for="m in models" :key="m" :value="m">{{ m }}</option>
          </select>
          <span class="help-text">Falls back to this model when the primary is unavailable.</span>
        </div>
        <div v-if="saveError" class="error-message">{{ saveError }}</div>
        <div v-if="saveSuccess" class="success-message">Settings saved successfully!</div>
        <div class="form-actions">
          <button type="submit" class="save-btn" :disabled="saving">
            <span v-if="saving" class="spinner"></span>
            <span v-else>Save Changes</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SettingsView',
  data() {
    return {
      loading: true,
      saving: false,
      saveError: '',
      saveSuccess: false,
      models: [],
      primaryModel: '',
      backupModel: '',
    }
  },
  async mounted() {
    await this.fetchSettings()
  },
  methods: {
    async fetchSettings() {
      this.loading = true
      try {
        const token = localStorage.getItem('token')
        const res = await fetch('/api/admin/models', {
          headers: { Authorization: `Bearer ${token}` },
        })
        if (res.status === 401) {
          localStorage.removeItem('token')
          this.$router.push('/login')
          return
        }
        if (!res.ok) throw new Error('Failed to fetch models')
        const data = await res.json()
        this.models = Array.isArray(data) ? data : (data.models || data.available_models || [])
        this.primaryModel = data.primary_model || data.primary || (this.models[0] || '')
        this.backupModel = data.backup_model || data.backup || (this.models[1] || '')
      } catch (err) {
        console.error('Settings error:', err)
      } finally {
        this.loading = false
      }
    },
    async saveSettings() {
      this.saving = true
      this.saveError = ''
      this.saveSuccess = false
      try {
        const token = localStorage.getItem('token')
        const res = await fetch('/api/admin/models', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            primary_model: this.primaryModel,
            backup_model: this.backupModel,
          }),
        })
        if (!res.ok) {
          const data = await res.json().catch(() => ({}))
          throw new Error(data.detail || data.message || 'Failed to save settings')
        }
        this.saveSuccess = true
        setTimeout(() => { this.saveSuccess = false }, 3000)
      } catch (err) {
        this.saveError = err.message
      } finally {
        this.saving = false
      }
    },
  },
}
</script>

<style scoped>
.settings-page {
  max-width: 700px;
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

.settings-card {
  background: #fff;
  border-radius: 14px;
  padding: 28px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

.settings-card h3 {
  font-size: 18px;
  font-weight: 700;
  color: #1A1A2E;
  margin-bottom: 4px;
}

.card-desc {
  font-size: 14px;
  color: #636E70;
  margin-bottom: 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 20px;
}

.form-group label {
  font-size: 14px;
  font-weight: 600;
  color: #1A1A2E;
}

.form-group select {
  padding: 12px 16px;
  border: 1.5px solid #E2E8F0;
  border-radius: 10px;
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  color: #1A1A2E;
  outline: none;
  transition: border-color 0.2s;
  background: #fff;
  cursor: pointer;
}

.form-group select:focus {
  border-color: #6C5CE7;
  box-shadow: 0 0 0 3px rgba(108, 92, 231, 0.1);
}

.help-text {
  font-size: 12px;
  color: #A0AEC0;
}

.error-message {
  background: #FFF5F5;
  color: #E53E3E;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 16px;
}

.success-message {
  background: #F0FFF4;
  color: #00C875;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 16px;
}

.form-actions {
  margin-top: 8px;
}

.save-btn {
  padding: 12px 28px;
  border: none;
  background: #6C5CE7;
  color: #fff;
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  font-weight: 600;
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.save-btn:hover:not(:disabled) {
  background: #5A4BD1;
}

.save-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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
