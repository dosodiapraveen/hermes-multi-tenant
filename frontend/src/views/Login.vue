<template>
  <div class="login-wrap">
    <div class="login-card">
      <div class="icon">⚡</div>
      <h1>Hermes Admin</h1>
      <p class="sub">Sign in to manage your platform</p>
      <form @submit.prevent="login">
        <div class="field"><label>Email</label><input type="email" v-model="email" required></div>
        <div class="field"><label>Password</label><input type="password" v-model="password" required></div>
        <p v-if="error" class="error">{{ error }}</p>
        <button type="submit" class="btn" :disabled="loading">{{ loading ? 'Signing in...' : 'Sign In' }}</button>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  data() { return { email:'admin@hermes.io', password:'', loading:false, error:'' }},
  methods: {
    async login() {
      this.loading = true; this.error = ''
      try {
        const r = await fetch('/api/auth/login', { method:'POST',
          headers:{'Content-Type':'application/json'},
          body:JSON.stringify({ email:this.email, password:this.password })
        })
        const d = await r.json()
        if (!r.ok) { this.error = d.detail || 'Login failed'; return }
        localStorage.setItem('token', d.access_token)
        localStorage.setItem('email', this.email)
        this.$router.push('/dashboard')
      } catch(e) { this.error = 'Network error' }
      finally { this.loading = false }
    }
  }
}
</script>

<style scoped>
.login-wrap { display:flex; align-items:center; justify-content:center; min-height:100vh; background:#1A1A2E; }
.login-card { text-align:center; padding:40px; background:white; border-radius:16px; width:360px; }
.icon { font-size:48px; margin-bottom:10px; }
h1 { font-size:24px; font-weight:700; margin-bottom:4px; }
.sub { margin-bottom:24px; }
form { text-align:left; }
.field { margin-bottom:14px; }
.btn { width:100%; margin-top:4px; }
.error { color:#E17055; font-size:13px; margin-bottom:8px; }
</style>
