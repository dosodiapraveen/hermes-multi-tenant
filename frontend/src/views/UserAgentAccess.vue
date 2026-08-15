<template>
  <div class="aa-page">
    <div class="aa-card">
      <div style="font-size:40px;text-align:center">🤖</div>
      <h1>Set up your dashboard access</h1>
      <p class="sub" v-if="agentName">This link grants access to the <b>{{ agentName }}</b> dashboard.</p>

      <!-- show form -->
      <form v-if="!done && !error" @submit.prevent="submit" class="aa-form">
        <label>Email</label>
        <input v-model="email" type="email" required placeholder="you@example.com" autocomplete="email">
        <label>Password</label>
        <input v-model="password" type="password" required minlength="12" placeholder="min 12 chars, upper+lower+digit" autocomplete="new-password">
        <p class="hint">Password must be at least 12 characters with an uppercase, lowercase and a number.</p>
        <button type="submit" :disabled="busy">{{ busy ? 'Creating account...' : 'Create my account' }}</button>
        <p v-if="msg" class="err">{{ msg }}</p>
        <p class="alt">Already have access? <a href="/user/login">Log in</a></p>
      </form>

      <!-- success -->
      <div v-else-if="done" class="ok">
        <div style="font-size:44px">📬</div>
        <h2>{{ doneMsg }}</h2>
        <p v-if="verifyLink">If you didn't get the email, click here to verify:<br><a :href="verifyLink">{{ verifyLink }}</a></p>
        <a class="btn" href="/user/login">Go to login</a>
      </div>

      <!-- error / invalid token -->
      <div v-else class="errbox">
        <div style="font-size:44px">❌</div>
        <p>{{ error }}</p>
        <a href="/user/login" class="btn">Back to login</a>
      </div>
    </div>
  </div>
</template>
<script>
export default {
  data(){ return { agentName:'', email:'', password:'', busy:false, msg:'', done:false, doneMsg:'', verifyLink:'', error:'' } },
  async mounted(){
    const token = new URLSearchParams(location.search).get('token')
    if(!token){ this.error='Invalid link (missing token). Please use the link provided by your admin.'; return }
    this.token = token
    try{
      const r = await fetch('/api/auth/user/agent/info?token='+encodeURIComponent(token))
      const d = await r.json().catch(()=>({}))
      if(r.ok){ this.agentName = d.agent_name||'' }
      else { this.error = d.detail || 'This link is invalid or has expired.' }
    }catch(e){ this.error='Unable to reach the server.' }
  },
  methods:{
    async submit(){
      this.msg=''; this.busy=true
      try{
        const r = await fetch('/api/auth/user/agent/register',{method:'POST',headers:{'Content-Type':'application/json'},
          body:JSON.stringify({token:this.token,email:this.email,password:this.password})})
        const d = await r.json().catch(()=>({}))
        if(r.ok){
          this.done=true; this.doneMsg=d.message||'Please check your email to verify your account.'
          this.verifyLink=d.verify_link||''
        } else {
          this.msg=d.detail||(r.status===409?'That email is already in use.':'Registration failed. Please try again.')
        }
      }catch(e){ this.msg='Connection error. Please try again.' }
      this.busy=false
    }
  }
}
</script>
<style scoped>
.aa-page{min-height:100vh;background:linear-gradient(135deg,#667eea,#764ba2);display:flex;align-items:center;justify-content:center;font-family:sans-serif;padding:20px}
.aa-card{background:#fff;border-radius:16px;padding:36px 32px;max-width:420px;width:100%;box-shadow:0 20px 60px rgba(0,0,0,.3)}
h1{font-size:22px;color:#1A1A2E;margin:8px 0 6px;text-align:center}
.sub{color:#636E70;font-size:13px;text-align:center;margin:0 0 18px}
.aa-form{display:flex;flex-direction:column}
label{font-size:13px;color:#444;margin:10px 0 4px;font-weight:600}
input{padding:11px 12px;border:1px solid #d0d5dd;border-radius:8px;font-size:14px}
.hint{font-size:12px;color:#8a8f98;margin:6px 0 12px}
button{margin-top:8px;padding:12px;background:#6C5CE7;color:#fff;border:0;border-radius:8px;font-size:15px;cursor:pointer}
button:disabled{opacity:.6}
.err{color:#e74c3c;font-size:13px;margin-top:10px}
.alt{font-size:13px;margin-top:14px;text-align:center}.alt a{color:#6C5CE7}
.ok,.errbox{text-align:center}
.ok h2{color:#1A1A2E;font-size:18px;margin:8px 0}.ok p{color:#636E70;font-size:13px;word-break:break-all}
.btn{display:inline-block;margin-top:14px;background:#6C5CE7;color:#fff;padding:11px 22px;border-radius:8px;text-decoration:none}
.errbox p{color:#e74c3c}
</style>
