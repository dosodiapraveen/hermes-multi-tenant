<template>
  <div>
    <div class="header-row"><h2>Invite Links</h2><button @click="showForm=!showForm" class="btn">+ Generate</button></div>
    <div v-if="showForm" class="card" style="margin-bottom:16px">
      <div class="row">
        <div class="field"><label>User Label</label><input v-model="form.label" placeholder="e.g. Dr. Ananya Sharma"></div>
        <div class="field"><label>Agent Name</label><input v-model="form.agent_name" placeholder="My Assistant"></div>
      </div>
      <div class="row">
        <div class="field"><label>Plan</label>
          <select v-model="form.plan"><option value="trial">Trial</option><option value="basic">Basic ($5)</option><option value="pro" selected>Pro ($15)</option><option value="business">Business ($35)</option><option value="vip">VIP</option></select></div>
        <div class="field"><label>Trial Days</label>
          <select v-model="form.trial_days"><option :value="7">7 days</option><option :value="14">14 days</option><option :value="30">30 days</option><option value="">No expiry</option></select></div>
      </div>
      <button @click="generate" class="btn" :disabled="loading">{{ loading ? 'Generating...' : 'Generate' }}</button>
    </div>
    <div v-for="link in links" :key="link.id" class="link-row">
      <div class="link-info"><div class="link-name">{{ link.label }}</div><div class="link-url">{{ link.link_url }}</div></div>
      <span class="status" :class="link.claimed ? 'claimed' : 'active'">{{ link.claimed ? 'Claimed' : 'Active' }}</span>
      <button @click="copy(link.link_url)" class="btn-copy">Copy</button>
    </div>
    <p v-if="!links.length" style="color:#B2BEC3;text-align:center;padding:40px">No invite links yet</p>
  </div>
</template>

<script>
export default {
  data() { return { showForm:false, loading:false, links:[], form:{ label:'', agent_name:'My Assistant', plan:'pro', trial_days:7, is_vip:false }}},
  methods: {
    tok() { return 'Bearer '+localStorage.getItem('token') },
    async load() { const r=await fetch('/api/admin/invite-links',{headers:{'Authorization':this.tok()}}); this.links=await r.json() },
    async generate() {
      this.loading=true
      const r=await fetch('/api/admin/invite-links',{method:'POST',headers:{'Authorization':this.tok(),'Content-Type':'application/json'},body:JSON.stringify({...this.form,trial_days:this.form.trial_days||null})})
      this.links.unshift(await r.json()); this.showForm=false; this.loading=false
    },
    copy(url) { navigator.clipboard.writeText(url) }
  },
  mounted() { this.load() }
}
</script>

<style scoped>
.header-row { display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; }
.link-row { display:flex; align-items:center; gap:12px; padding:12px 16px; background:white; border:1px solid #DFE6E9; border-radius:8px; margin-bottom:8px; }
.link-info { flex:1; }
.link-name { font-size:14px; font-weight:600; }
.link-url { font-size:12px; color:#6C5CE7; word-break:break-all; font-family:monospace; }
.status { font-size:11px; font-weight:500; padding:2px 8px; border-radius:4px; }
.status.active { background:rgba(0,184,148,0.1); color:#00B894; }
.status.claimed { background:rgba(108,92,231,0.1); color:#6C5CE7; }
.btn-copy { padding:6px 12px; background:#6C5CE7; color:white; border:none; border-radius:6px; font-size:11px; cursor:pointer; }
</style>
