<template>
  <div class="regreq-page">
    <header>
      <h1>🔔 Registration Requests</h1>
      <p class="sub">Review and approve or reject pending sign-ups. Only requests with a <strong>verified email</strong> can be approved.</p>
      <nav>
        <button v-for="t in tabs" :key="t.key" :class="{active: tab===t.key}" @click="tab=t.key; load()">{{ t.label }}
          <span v-if="t.key==='pending' && pendingCount" class="badge">{{ pendingCount }}</span></button>
      </nav>
    </header>

    <main>
      <div v-if="!items.length" class="empty">No {{ tab }} requests.</div>

      <div v-for="req in items" :key="req.id" class="card">
        <div class="row-top">
          <div class="id-col">
            <strong>{{ req.email }}</strong>
            <div class="meta" v-if="req.full_name">{{ req.full_name }}</div>
            <div class="meta" v-if="req.agent_name">Wants agent: <em>{{ req.agent_name }}</em></div>
            <div class="meta" v-if="req.use_case">Use case: {{ req.use_case }}</div>
            <div class="meta">Plan requested: {{ req.plan_requested }} · Submitted {{ (req.created_at||'').slice(0,10) }}</div>
          </div>
          <div class="badges">
            <span class="badge" :class="req.email_verified ? 'ok' : 'warn'">{{ req.email_verified ? '✅ Email verified' : '⚠️ Not verified' }}</span>
            <span class="badge" :class="req.status">{{ statusLabel(req.status) }}</span>
          </div>
        </div>

        <!-- Pending → approve/reject controls -->
        <div v-if="req.status==='pending'" class="actions">
          <div class="approve-box">
            <input v-model="approveForms[req.id].agent_name" placeholder="Agent name (default: their preference)" />
            <select v-model="approveForms[req.id].plan">
              <option value="trial">Trial</option><option value="basic">Basic</option>
              <option value="pro" selected>Pro</option><option value="business">Business</option><option value="vip">VIP</option>
            </select>
            <input v-model="approveForms[req.id].note" placeholder="Note to admin log" />
            <button class="btn-approve" :disabled="busy" @click="approve(req)">✔ Approve</button>
          </div>
          <div class="reject-box">
            <input v-model="rejectNote[req.id]" placeholder="Reason to user (optional)" />
            <button class="btn-reject" :disabled="busy" @click="reject(req)">✕ Reject</button>
          </div>
        </div>

        <div v-if="req.status!=='pending'" class="meta reviewed">
          Reviewed {{ (req.reviewed_at||'').slice(0,10) }}{{ req.review_note ? format(' · '+req.review_note) : '' }}
        </div>
      </div>
    </main>
  </div>
</template>

<script>
export default {
  data(){return{
    tab:'pending', items:[], pendingCount:0, busy:false,
    tabs:[{key:'pending',label:'Pending'},{key:'approved',label:'Approved'},{key:'rejected',label:'Rejected'}],
    approveForms:{}, rejectNote:{},
  }},
  methods:{
    statusLabel(s){return {pending:'Pending',approved:'Approved',rejected:'Rejected'}[s]||s},
    format(v){return v},
    async api(method,url,body){
      const token=localStorage.getItem('token')
      const r=await fetch(url,{method,headers:{'Content-Type':'application/json','Authorization':'Bearer '+token},body:body?JSON.stringify(body):undefined})
      if(r.status===401){window.location='/login';return}
      return r.json()
    },
    async load(){
      const d=await this.api('GET','/api/admin/registration-requests?status='+this.tab)
      if(d){this.items=d; this.approveForms={}; this.rejectNote={};
        d.forEach(x=>{this.approveForms[x.id]={agent_name:x.agent_name,plan:x.plan_requested||'pro',note:''};this.rejectNote[x.id]=''})}
      const p=await this.api('GET','/api/admin/registration-requests?status=pending')
      if(p)this.pendingCount=p.length
    },
    async approve(req){
      this.busy=true
      const f=this.approveForms[req.id]
      const d=await this.api('POST',`/api/admin/registration-requests/${req.id}/approve`,{agent_name:f.agent_name,plan:f.plan,review_note:f.note})
      if(d&&d.status==='approved'){alert('Approved! Agent '+d.agent_name+' created. Activation email sent: '+d.email_status);req.status='approved'}
      else alert('Error: '+(d&&d.detail||'unknown'))
      this.busy=false; this.load()
    },
    async reject(req){
      if(!confirm('Reject this registration request?'))return
      this.busy=true
      const d=await this.api('POST',`/api/admin/registration-requests/${req.id}/reject`,{review_note:this.rejectNote[req.id]})
      if(d&&d.status==='rejected'){alert('Request rejected. User notified.')}
      else alert('Error: '+(d&&d.detail||'unknown'))
      this.busy=false; this.load()
    },
  },
  mounted(){this.load()}
}
</script>

<style scoped>
*{box-sizing:border-box}
.regreq-page{min-height:100vh;background:var(--color-background);font-family:-apple-system,BlinkMacSystemFont,sans-serif}
header{background:var(--color-surface);border-bottom:1px solid var(--color-border);padding:20px 28px}
header h1{margin:0;font-size:22px;color:var(--color-text-primary)}
header .sub{margin:6px 0 14px;color:var(--color-text-tertiary);font-size:14px}
nav{display:flex;gap:8px}
nav button{padding:8px 16px;border:1px solid var(--color-border);border-radius:8px;background:var(--color-surface);color:var(--color-text-primary);cursor:pointer;font-size:14px}
nav button.active{background:var(--color-primary-500);color:#fff;border-color:var(--color-primary-500)}
nav .badge{background:var(--color-error-500);color:#fff;border-radius:10px;padding:1px 6px;font-size:11px;width:auto}
main{max-width:860px;margin:0 auto;padding:24px}
.card{background:var(--color-surface);border-radius:12px;padding:18px 20px;margin-bottom:12px;box-shadow:0 1px 4px rgba(0,0,0,.05)}
.row-top{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap}
.id-col{flex:1;min-width:200px}
.id-col strong{font-size:16px;color:var(--color-text-primary)}
.meta{font-size:13px;color:var(--color-text-tertiary);margin-top:3px}
.badges{display:flex;flex-direction:column;gap:6px;align-items:flex-end}
.badge{font-size:12px;padding:3px 10px;border-radius:10px;white-space:nowrap}
.badge.ok{background:var(--color-success-100);color:var(--color-success-700)}
.badge.warn{background:var(--color-warning-100);color:var(--color-warning-700)}
.badge.pending{background:var(--color-info-100);color:var(--color-info-700)}
.badge.approved{background:var(--color-success-100);color:var(--color-success-700)}
.badge.rejected{background:var(--color-error-100);color:var(--color-error-700)}
.actions{margin-top:14px;border-top:1px solid var(--color-border);padding-top:14px;display:flex;flex-direction:column;gap:10px}
.approve-box,.reject-box{display:flex;gap:8px;flex-wrap:wrap}
.approve-box input,.approve-box select,.reject-box input{padding:8px 10px;border:1px solid var(--color-border);border-radius:8px;font-size:13px;flex:1;min-width:120px;background:var(--color-surface);color:var(--color-text-primary)}
.btn-approve{background:var(--color-success-600);color:#fff;border:none;padding:9px 16px;border-radius:8px;cursor:pointer;font-size:13px}
.btn-reject{background:var(--color-error-600);color:#fff;border:none;padding:9px 16px;border-radius:8px;cursor:pointer;font-size:13px}
.empty{color:var(--color-text-tertiary);text-align:center;padding:40px}
.reviewed{color:var(--color-text-tertiary);font-size:12px;margin-top:10px}
</style>
