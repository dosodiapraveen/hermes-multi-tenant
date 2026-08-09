<template>
  <div>
    <h2>Dashboard</h2>
    <p class="sub">Platform overview at a glance</p>
    <div class="grid">
      <div class="stat" v-for="s in stats" :key="s.label">
        <div class="stat-label">{{ s.label }}</div>
        <div class="stat-val">{{ s.value }}</div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() { return { stats:[] }},
  async mounted() {
    const r = await fetch('/api/admin/dashboard', { headers:{'Authorization':'Bearer '+localStorage.getItem('token')} })
    const d = await r.json()
    this.stats = [
      { label:'Active Users', value:d.active_users },
      { label:'Total Agents', value:d.total_agents },
      { label:'Tokens Today', value:d.tokens_today },
      { label:'Total Users', value:d.total_users },
    ]
  }
}
</script>

<style scoped>
.grid { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; }
.stat { background:white; border:1px solid #DFE6E9; border-radius:10px; padding:20px; }
.stat-label { font-size:13px; color:#636E70; margin-bottom:6px; }
.stat-val { font-size:28px; font-weight:700; }
</style>
