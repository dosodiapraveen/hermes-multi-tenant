<template>
  <div class="dashboard">
    <div class="page-header">
      <h1>Dashboard</h1>
      <p>Overview of your platform metrics</p>
    </div>
    <div v-if="loading" class="loading">Loading...</div>
    <div v-else class="cards">
      <router-link to="/users" class="card">
        <div class="icon" style="background:rgba(108,92,231,0.1);color:#6C5CE7">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/></svg>
        </div>
        <div class="info"><div class="val">{{ stats.active_users }}</div><div class="lbl">Active Users</div></div>
      </router-link>
      <router-link to="/users" class="card">
        <div class="icon" style="background:rgba(0,200,117,0.1);color:#00C875">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
        </div>
        <div class="info"><div class="val">{{ stats.total_agents }}</div><div class="lbl">Total Agents</div></div>
      </router-link>
      <router-link to="/settings" class="card">
        <div class="icon" style="background:rgba(255,170,0,0.1);color:#FFAA00">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
        </div>
        <div class="info"><div class="val">{{ stats.tokens_today }}</div><div class="lbl">Tokens Today</div></div>
      </router-link>
      <router-link to="/users" class="card">
        <div class="icon" style="background:rgba(59,130,246,0.1);color:#3B82F6">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
        </div>
        <div class="info"><div class="val">{{ stats.total_users }}</div><div class="lbl">Total Users</div></div>
      </router-link>
    </div>
  </div>
</template>
<script>
export default {
  data() { return { loading:true, stats:{ active_users:0, total_agents:0, tokens_today:0, total_users:0 } }},
  async mounted() {
    try {
      const r = await fetch('/api/admin/dashboard', { headers:{'Authorization':'Bearer '+localStorage.getItem('token')} })
      if (r.status===401) { localStorage.removeItem('token'); this.$router.push('/login'); return }
      const d = await r.json()
      this.stats = { active_users:d.active_users||0, total_agents:d.total_agents||0, tokens_today:d.tokens_today||0, total_users:d.total_users||0 }
    } catch(e) { console.error(e) }
    finally { this.loading = false }
  }
}
</script>
<style scoped>
.dashboard { max-width:1000px; }
.page-header { margin-bottom:28px; }
.page-header h1 { font-size:26px; font-weight:700; margin-bottom:4px; }
.page-header p { font-size:14px; color:#636E70; }
.loading { text-align:center; padding:60px; color:#636E70; }
.cards { display:grid; grid-template-columns:repeat(2,1fr); gap:16px; }
.card { background:#fff; border-radius:12px; padding:24px; display:flex; align-items:center; gap:16px; text-decoration:none; color:inherit; cursor:pointer; border:1px solid #e8eaed; transition:all .15s; }
.card:hover { border-color:#6C5CE7; box-shadow:0 2px 12px rgba(108,92,231,0.08); transform:translateY(-1px); }
.icon { width:48px; height:48px; border-radius:12px; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.info { display:flex; flex-direction:column; gap:2px; }
.val { font-size:28px; font-weight:800; line-height:1.1; }
.lbl { font-size:13px; font-weight:500; color:#636E70; }
</style>
