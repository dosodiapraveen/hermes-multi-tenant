<template>
  <div>
    <h2>Settings</h2>
    <p class="sub">Model configuration</p>
    <div class="card" style="max-width:500px">
      <h3 style="font-size:16px;font-weight:600;margin-bottom:16px">🧠 Model Configuration</h3>
      <div class="field"><label>Primary Model</label>
        <select v-model="primary"><option value="accounts/fireworks/models/deepseek-v4-flash-0731">DeepSeek V4 Flash</option><option value="claude-sonnet-4-2026">Claude Sonnet 4</option><option value="gpt-5">GPT-5</option></select></div>
      <div class="field"><label>Backup Model</label>
        <select v-model="backup"><option value="accounts/fireworks/models/deepseek-v4-flash-0731">DeepSeek V4 Flash</option><option value="claude-sonnet-4-2026">Claude Sonnet 4</option><option value="gpt-5">GPT-5</option></select></div>
      <button @click="save" class="btn" style="margin-top:8px" :disabled="saving">{{ saving ? 'Saving...' : 'Push to All' }}</button>
      <span v-if="saved" style="margin-left:12px;color:#00B894;font-size:13px;">✓ Saved</span>
    </div>
  </div>
</template>

<script>
export default {
  data() { return { primary:'accounts/fireworks/models/deepseek-v4-flash-0731', backup:'accounts/fireworks/models/deepseek-v4-flash-0731', saving:false, saved:false }},
  methods: {
    tok() { return 'Bearer '+localStorage.getItem('token') },
    async mount() {
      const r=await fetch('/api/admin/models',{headers:{'Authorization':this.tok()}})
      const d=await r.json(); this.primary=d.primary_model; this.backup=d.backup_model
    },
    async save() {
      this.saving=true
      await fetch('/api/admin/models',{method:'POST',headers:{'Authorization':this.tok(),'Content-Type':'application/json'},body:JSON.stringify({primary_model:this.primary,backup_model:this.backup})})
      this.saved=true; this.saving=false; setTimeout(()=>this.saved=false,3000)
    }
  },
  mounted() { this.mount() }
}
</script>
