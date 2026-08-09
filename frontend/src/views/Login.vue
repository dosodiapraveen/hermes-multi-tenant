<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-header">
        <div class="logo-icon">H</div>
        <h1>Hermes Admin</h1>
        <p>Sign in to manage your platform</p>
      </div>
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="email">Email</label>
          <input id="email" v-model="email" type="email" placeholder="admin@hermes.io" required autocomplete="email" />
        </div>
        <div class="form-group">
          <label for="password">Password</label>
          <input id="password" v-model="password" type="password" placeholder="Enter password" required autocomplete="current-password" />
        </div>
        <div v-if="error" class="error-message">{{ error }}</div>
        <button type="submit" class="login-btn" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          <span v-else>Sign In</span>
        </button>
      </form>
      <div class="divider"><span>or</span></div>
      <button @click="supabaseLogin" class="google-btn" :disabled="sbLoading">
        <svg width="18" height="18" viewBox="0 0 24 24"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>
        <span>{{ sbLoading ? 'Connecting...' : 'Sign in with Google' }}</span>
      </button>
    </div>
  </div>
</template>

<script>
import { createClient } from '@supabase/supabase-js'

const SUPABASE_URL = 'https://ktbnfrncwvslrmuyggsl.supabase.co'
const SUPABASE_ANON_KEY = 'sb_publishable_nzg47kXolJCrkqPWMX5urA_eOgLboCL'
const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)

export default {
  data() { return { email:'', password:'', loading:false, error:'', sbLoading:false }},
  methods: {
    async handleLogin() {
      this.loading=true; this.error=''
      try {
        const r=await fetch('/api/auth/login',{method:'POST',
          headers:{'Content-Type':'application/json'},
          body:JSON.stringify({email:this.email,password:this.password})})
        const d=await r.json()
        if(!r.ok){this.error=d.detail||'Login failed';return}
        localStorage.setItem('token',d.access_token); localStorage.setItem('email',this.email)
        this.$router.push('/dashboard')
      }catch(e){this.error='Network error'}
      finally{this.loading=false}
    },
    async supabaseLogin() {
      this.sbLoading=true; this.error=''
      try {
        const {data,error}=await supabase.auth.signInWithOAuth({
          provider:'google',options:{redirectTo:window.location.origin+'/auth/callback'}
        })
        if(error)throw error
      }catch(e){this.error=e.message}
      finally{this.sbLoading=false}
    }
  },
  async mounted() {
    const hash=window.location.hash
    if(hash&&hash.includes('access_token')){
      const params=new URLSearchParams(hash.substring(1))
      const token=params.get('access_token')
      if(token){
        try {
          const r=await fetch('/api/auth/supabase',{method:'POST',
            headers:{'Content-Type':'application/json'},
            body:JSON.stringify({access_token:token})})
          const d=await r.json()
          if(r.ok){
            localStorage.setItem('token',d.access_token); localStorage.setItem('email',d.email)
            this.$router.push('/dashboard')
          }else{this.error=d.detail||'Auth failed'}
        }catch(e){this.error='Auth failed'}
      }
    }
  }
}
</script>

<style scoped>
.login-page { min-height:100vh; display:flex; align-items:center; justify-content:center;
  background:linear-gradient(135deg,#1A1A2E 0%,#16213E 50%,#0F3460 100%); padding:24px; }
.login-card { width:100%; max-width:420px; background:#fff; border-radius:16px; padding:40px;
  box-shadow:0 20px 60px rgba(0,0,0,0.3); }
.login-header { text-align:center; margin-bottom:28px; }
.logo-icon { width:48px; height:48px; background:#6C5CE7; border-radius:12px; display:inline-flex;
  align-items:center; justify-content:center; font-weight:800; font-size:22px; color:#fff; margin-bottom:14px; }
.login-header h1 { font-size:22px; font-weight:700; margin-bottom:4px; }
.login-header p { font-size:14px; color:#636E70; }
.login-form { display:flex; flex-direction:column; gap:18px; }
.form-group { display:flex; flex-direction:column; gap:6px; }
.form-group label { font-size:13px; font-weight:600; color:#1A1A2E; }
.form-group input { padding:12px 16px; border:1.5px solid #E2E8F0; border-radius:10px;
  font-family:'Inter',sans-serif; font-size:14px; outline:none; }
.form-group input:focus { border-color:#6C5CE7; box-shadow:0 0 0 3px rgba(108,92,231,0.1); }
.error-message { background:#FFF5F5; color:#E53E3E; padding:10px 14px; border-radius:8px; font-size:13px; }
.login-btn { padding:12px; border:none; background:#6C5CE7; color:#fff; font-family:'Inter',sans-serif;
  font-size:15px; font-weight:600; border-radius:10px; cursor:pointer; height:48px; display:flex;
  align-items:center; justify-content:center; }
.login-btn:hover:not(:disabled){background:#5A4BD1;}
.login-btn:disabled{opacity:0.6;cursor:not-allowed;}
.spinner { width:20px; height:20px; border:2px solid rgba(255,255,255,0.3); border-top-color:#fff;
  border-radius:50%; animation:spin 0.6s linear infinite; }
@keyframes spin{to{transform:rotate(360deg)}}
.divider { text-align:center; margin:20px 0; color:#B2BEC3; font-size:13px; position:relative; }
.divider::before,.divider::after{content:'';position:absolute;top:50%;width:42%;height:1px;background:#E2E8F0;}
.divider::before{left:0;}
.divider::after{right:0;}
.google-btn { width:100%; padding:10px; border:1.5px solid #E2E8F0; border-radius:10px; background:white;
  font-family:'Inter',sans-serif; font-size:14px; font-weight:500; cursor:pointer; display:flex;
  align-items:center; justify-content:center; gap:10px; }
.google-btn:hover{border-color:#6C5CE7;background:#F8F9FA;}
.google-btn:disabled{opacity:0.6;cursor:not-allowed;}
</style>
