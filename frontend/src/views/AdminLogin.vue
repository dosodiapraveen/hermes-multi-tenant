<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-header">
        <div class="logo-icon">H</div>
        <h1>Internal Admin Access</h1>
        <p>Authorized personnel only</p>
      </div>
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="email">Email</label>
          <input id="email" v-model="email" type="email" placeholder="you@example.com" required autocomplete="email" />
        </div>
        <div class="form-group">
          <label for="password">Password</label>
          <input id="password" v-model="password" type="password" placeholder="Enter your password" required autocomplete="current-password" />
        </div>
        <div v-if="error" class="error-message">{{ error }}</div>
        <button type="submit" class="login-btn" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          <span v-else>Sign In</span>
        </button>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  data() { return { email: '', password: '', loading: false, error: '' }},
  methods: {
    async handleLogin() {
      this.loading = true
      this.error = ''
      try {
        const r = await fetch('/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: this.email, password: this.password })
        })
        const d = await r.json()
        if (!r.ok) { this.error = 'Invalid credentials'; return }
        localStorage.setItem('token', d.access_token)
        localStorage.setItem('email', this.email)
        this.$router.push('/dashboard')
      } catch (e) { this.error = 'Connection error' }
      finally { this.loading = false }
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
</style>
