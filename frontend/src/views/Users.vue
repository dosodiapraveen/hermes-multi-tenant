<template>
  <div>
    <h2>Users</h2>
    <p class="sub">Manage user profiles</p>
    <table>
      <thead><tr><th>Phone</th><th>Agent</th><th>Plan</th><th>Status</th><th>Model</th><th></th></tr></thead>
      <tbody>
        <tr v-for="u in users" :key="u.id">
          <td>{{ u.phone_number || '—' }}</td>
          <td>{{ u.agent_name }}</td>
          <td><span class="badge">{{ u.plan }}</span></td>
          <td><span :class="u.is_active ? 'green' : 'muted'">{{ u.is_active ? 'Active' : 'Inactive' }}</span></td>
          <td style="font-size:12px;max-width:160px;overflow:hidden;text-overflow:ellipsis">{{ u.primary_model }}</td>
          <td>
            <button class="btn-access" @click="genLink(u)" :disabled="u.linkBusy">{{ u.linkBusy ? '…' : 'Dashboard link' }}</button>
            <button class="btn-del" @click="confirmDelete(u)">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Confirmation Dialog -->
    <div v-if="showDialog" class="overlay" @click.self="showDialog=false">
      <div class="dialog">
        <h3>Delete User?</h3>
        <p>This will permanently delete <strong>{{ deletingUser?.agent_name }}</strong> ({{ deletingUser?.phone_number || 'no phone' }}).</p>
        <p style="font-size:13px;color:#636E70;margin-top:8px;">The Hermes profile, Obsidian vault, invite links, and all activity logs will be removed. This cannot be undone.</p>
        <div class="dialog-actions">
          <button class="btn-cancel" @click="showDialog=false">Cancel</button>
          <button class="btn-del" @click="doDelete" :disabled="deleting">{{ deleting ? 'Deleting...' : 'Delete' }}</button>
        </div>
      </div>
    </div>

    <!-- Access Link Modal -->
    <div v-if="linkResult" class="overlay" @click.self="linkResult=null">
      <div class="dialog">
        <h3>Dashboard access link</h3>
        <p style="margin-bottom:6px;">Send this to <strong>{{ linkResult.agent }}</strong>. They'll set their email &amp; password, verify, and get into their dashboard.</p>
        <input ref="linkbox" readonly :value="linkResult.url" class="linkbox" @focus="e=>e.target.select()" />
        <div v-if="linkResult.error" class="err">{{ linkResult.error }}</div>
        <div v-if="copied" class="copied">✓ Copied to clipboard</div>
        <div class="dialog-actions">
          <button class="btn-cancel" @click="linkResult=null">Close</button>
          <button class="btn-copy" @click="copyLink">{{ copylabel }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() { return { users:[], showDialog:false, deletingUser:null, deleting:false, linkResult:null, copied:false }},
  methods: {
    tok() { return 'Bearer '+localStorage.getItem('token') },
    async load() { const r=await fetch('/api/admin/users',{headers:{'Authorization':this.tok()}}); this.users=await r.json() },
    confirmDelete(u) { this.deletingUser=u; this.showDialog=true; this.deleting=false },
    async genLink(u) {
      u.linkBusy=true
      try {
        const r=await fetch('/api/admin/users/'+u.id+'/access-link',{method:'POST',headers:{'Authorization':this.tok()}})
        const d=await r.json().catch(()=>({}))
        if(!r.ok) throw new Error(d.detail||'Failed')
        this.copied=false; this.linkResult={ agent:d.agent_name, url:d.access_link }
      } catch(e) { this.linkResult={ agent:u.agent_name, url:'', error:e.message } }
      finally { u.linkBusy=false }
    },
    async copyLink() {
      if(!this.linkResult) return
      const url=this.linkResult.url||''
      let ok=false
      try { await navigator.clipboard.writeText(url); ok=true }
      catch(e) {
        const el=this.$refs.linkbox; if(el){ el.select(); ok=document.execCommand('copy') }
      }
      this.copied=ok
    },
    async doDelete() {
      this.deleting=true
      try {
        const r=await fetch('/api/admin/users/'+this.deletingUser.id,{method:'DELETE',headers:{'Authorization':this.tok()}})
        if(!r.ok) throw new Error('Delete failed')
        this.users=this.users.filter(u=>u.id!==this.deletingUser.id)
        this.showDialog=false; this.deletingUser=null
      } catch(e) { alert('Failed to delete user') }
      finally { this.deleting=false }
    }
  },
  computed: {
    copylabel() { return this.copied ? 'Copied ✓' : 'Copy' },
  },
  mounted() { this.load() }
}
</script>

<style scoped>
table { width:100%; border-collapse:collapse; background:var(--color-surface); border-radius:10px; overflow:hidden; }
th { text-align:left; padding:12px 16px; font-size:11px; text-transform:uppercase; color:var(--color-text-tertiary); background:var(--color-gray-50); border-bottom:1px solid var(--color-border); }
td { padding:12px 16px; border-bottom:1px solid var(--color-border); font-size:13px; color:var(--color-text-primary); }
.badge { font-size:11px; padding:2px 8px; border-radius:4px; background:var(--color-gray-100); color:var(--color-text-secondary); }
.green { color:var(--color-success-500); font-weight:500; }
.muted { color:var(--color-text-tertiary); }
.btn-del { padding:5px 12px; border:none; border-radius:6px; background:var(--color-error-50); color:var(--color-error-500); font-size:12px; font-weight:500; cursor:pointer; }
.btn-access { padding:5px 12px; border:none; border-radius:6px; background:var(--color-primary-100); color:var(--color-primary-500); font-size:12px; font-weight:500; cursor:pointer; margin-right:6px; }
.btn-access:hover { background:var(--color-primary-200); }
.btn-access:disabled { opacity:.6; }
.btn-del:hover { background:var(--color-error-100); }
.overlay { position:fixed; top:0; left:0; right:0; bottom:0; background:var(--modal-backdrop); display:flex; align-items:center; justify-content:center; z-index:1000; }
.dialog { background:var(--color-surface); border-radius:14px; padding:28px; max-width:420px; width:90%; }
.dialog h3 { font-size:18px; font-weight:700; margin-bottom:8px; color:var(--color-text-primary); }
.dialog p { font-size:14px; color:var(--color-text-primary); }
.dialog-actions { display:flex; gap:10px; justify-content:flex-end; margin-top:20px; }
.btn-cancel { padding:9px 20px; border:1.5px solid var(--color-border); border-radius:8px; background:var(--color-surface); color:var(--color-text-secondary); font-size:13px; font-weight:500; cursor:pointer; }
.btn-cancel:hover { border-color:var(--color-text-tertiary); }
.linkbox { width:100%; max-width:100%; padding:10px 12px; border:1.5px solid var(--color-border); border-radius:8px; font-size:12px; font-family:monospace; color:var(--color-text-primary); background:var(--color-gray-50); box-sizing:border-box; margin:6px 0 2px; }
.copied { color:var(--color-success-500); font-size:13px; font-weight:500; margin-top:4px; }
.err { color:var(--color-error-500); font-size:13px; margin-top:6px; }
.btn-copy { padding:9px 20px; border:none; border-radius:8px; background:var(--color-primary-500); color:#fff; font-size:13px; font-weight:600; cursor:pointer; }
.btn-copy:hover { background:var(--color-primary-600); }
</style>
