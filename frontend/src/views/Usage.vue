<template>
  <div>
    <h2>Usage</h2>
    <p class="sub">Message and token analytics</p>

    <div v-if="loading" class="loading">Loading...</div>
    <div v-else-if="error" class="error">{{ error }}</div>

    <template v-else>
      <div class="summary">
        <div class="card"><div class="val">{{ totals.messages }}</div><div class="lbl">Total Messages</div></div>
        <div class="card"><div class="val">{{ totals.tokens }}</div><div class="lbl">Total Tokens</div></div>
        <div class="card"><div class="val">{{ activeUsers }}</div><div class="lbl">Active Users (30d)</div></div>
      </div>

      <h3 style="margin:24px 0 12px">Messages per Day (Last 7 Days)</h3>
      <div class="chart">
        <div v-for="d in daily" :key="d.date" class="bar-wrap">
          <div class="bar" :style="{ height: barHeight(d.messages) + 'px' }"></div>
          <div class="bar-val">{{ d.messages }}</div>
          <div class="bar-lbl">{{ formatDate(d.date) }}</div>
        </div>
        <p v-if="!daily.length" style="color:#B2BEC3;padding:20px">No data yet</p>
      </div>

      <h3 style="margin:24px 0 12px">Per User (Last 30 Days)</h3>
      <table>
        <thead><tr><th>Agent</th><th>Phone</th><th>Messages</th><th>Tokens</th><th>Last Active</th></tr></thead>
        <tbody>
          <tr v-for="u in perUser" :key="u.phone">
            <td>{{ u.agent_name }}</td><td>{{ u.phone || '—' }}</td>
            <td>{{ u.messages }}</td><td>{{ u.tokens }}</td>
            <td>{{ u.last_active ? timeAgo(u.last_active) : '—' }}</td>
          </tr>
          <tr v-if="!perUser.length"><td colspan="5" style="text-align:center;color:#B2BEC3;padding:20px">No usage data yet</td></tr>
        </tbody>
      </table>
    </template>
  </div>
</template>

<script>
export default {
  data() { return { daily:[], perUser:[], totals:{messages:0,tokens:0}, activeUsers:0, loading:true, error:null }},
  methods: {
    tok() { return 'Bearer '+localStorage.getItem('token') },
    barHeight(n) { return Math.min(Math.max(n * 20, 4), 120) },
    formatDate(d) { return d ? d.slice(5) : '' },
    timeAgo(ts) {
      const min = Math.floor((Date.now() - new Date(ts).getTime()) / 60000)
      if (min < 60) return min + 'm ago'
      const hrs = Math.floor(min / 60)
      if (hrs < 24) return hrs + 'h ago'
      return Math.floor(hrs / 24) + 'd ago'
    }
  },
  async mounted() {
    try {
      const r = await fetch('/api/admin/usage', { headers:{'Authorization':this.tok()} })
      if (r.status === 401) {
        localStorage.removeItem('token')
        this.$router.push('/internal/admin-login')
        return
      }
      if (!r.ok) {
        this.error = 'Failed to load usage data'
        return
      }
      const d = await r.json()
      this.daily = d.daily || []
      this.perUser = d.per_user || []
      this.totals = d.totals || {messages:0,tokens:0}
      this.activeUsers = (d.per_user || []).length
    } catch (e) {
      console.error('Usage fetch error:', e)
      this.error = 'Failed to load usage data'
    } finally {
      this.loading = false
    }
  }
}
</script>

<style scoped>
.loading { padding:40px; text-align:center; color:var(--color-text-tertiary); }
.error { padding:20px; background:var(--color-error-50); color:var(--color-error-600); border-radius:8px; margin-bottom:16px; }
.summary { display:grid; grid-template-columns:repeat(3,1fr); gap:16px; }
.card { background:var(--color-surface); border:1px solid var(--color-border); border-radius:10px; padding:20px; }
.val { font-size:28px; font-weight:800; color:var(--color-text-primary); }
.lbl { font-size:13px; color:var(--color-text-tertiary); margin-top:2px; }
.chart { display:flex; gap:12px; align-items:flex-end; background:var(--color-surface); border:1px solid var(--color-border); border-radius:10px; padding:20px; min-height:160px; }
.bar-wrap { display:flex; flex-direction:column; align-items:center; flex:1; }
.bar { width:32px; background:var(--color-primary-500); border-radius:4px 4px 0 0; min-height:4px; }
.bar-val { font-size:12px; font-weight:600; margin-top:4px; color:var(--color-text-primary); }
.bar-lbl { font-size:10px; color:var(--color-text-tertiary); margin-top:2px; }
table { width:100%; border-collapse:collapse; background:var(--color-surface); border-radius:10px; overflow:hidden; }
th { text-align:left; padding:12px 16px; font-size:11px; text-transform:uppercase; color:var(--color-text-tertiary); background:var(--color-gray-50); border-bottom:1px solid var(--color-border); }
td { padding:12px 16px; border-bottom:1px solid var(--color-border); font-size:13px; color:var(--color-text-primary); }
</style>