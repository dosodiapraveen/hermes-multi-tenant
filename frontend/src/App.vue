<template>
  <div v-if="token" class="layout">
    <aside class="sidebar">
      <div class="logo"><span class="bolt">⚡</span>Hermes</div>
      <nav><router-link v-for="n in nav" :key="n.to" :to="n.to" class="nav-item">{{ n.label }}</router-link></nav>
      <div class="footer">
        <span class="email">{{ email }}</span>
        <button @click="logout" class="logout">Logout</button>
      </div>
    </aside>
    <main class="main"><router-view /></main>
  </div>
  <router-view v-else />
</template>

<script>
export default {
  data() { return {
    token: localStorage.getItem('token'),
    email: localStorage.getItem('email') || 'admin',
    nav: [
      { to:'/dashboard', label:'📊 Dashboard' },
      { to:'/users', label:'👥 Users' },
      { to:'/invites', label:'🔗 Invite Links' },
      { to:'/settings', label:'⚙️ Settings' },
    ]
  }},
  watch: { '$route'() { this.token = localStorage.getItem('token') }},
  methods: {
    logout() { localStorage.removeItem('token'); localStorage.removeItem('email'); this.token = null; this.$router.push('/login') }
  }
}
</script>

<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:'Inter',sans-serif; background:#F0F2F5; color:#1A1A2E; }
.layout { display:flex; min-height:100vh; }
.sidebar { width:220px; background:#1A1A2E; display:flex; flex-direction:column; padding:20px 16px; }
.logo { color:white; font-size:18px; font-weight:700; margin-bottom:28px; }
.bolt { margin-right:6px; }
.nav { flex:1; display:flex; flex-direction:column; gap:2px; }
.nav-item { padding:10px 12px; border-radius:8px; color:rgba(255,255,255,0.55); text-decoration:none; font-size:13px; }
.nav-item:hover { background:rgba(255,255,255,0.06); color:white; }
.nav-item.router-link-active { background:rgba(108,92,231,0.2); color:white; font-weight:500; }
.footer { padding-top:16px; border-top:1px solid rgba(255,255,255,0.06); font-size:12px; color:rgba(255,255,255,0.4); }
.email { display:block; margin-bottom:8px; }
.logout { padding:6px 12px; border:none; border-radius:6px; background:rgba(225,112,85,0.2); color:#E17055; cursor:pointer; font-size:12px; }
.main { flex:1; padding:28px; overflow-y:auto; }
h2 { font-size:22px; font-weight:700; margin-bottom:4px; }
.sub { color:#636E70; font-size:14px; margin-bottom:20px; }
.card { background:white; border:1px solid #DFE6E9; border-radius:10px; padding:20px; }
table { width:100%; border-collapse:collapse; background:white; border-radius:10px; overflow:hidden; }
th { text-align:left; padding:12px 16px; font-size:11px; text-transform:uppercase; color:#636E70; background:#F8F9FA; border-bottom:1px solid #DFE6E9; }
td { padding:12px 16px; border-bottom:1px solid #DFE6E9; font-size:13px; }
.green { color:#00B894; font-weight:500; }
.muted { color:#B2BEC3; }
.badge { font-size:11px; padding:2px 8px; border-radius:4px; background:#F0F2F5; }
select { height:36px; border:1.5px solid #DFE6E9; border-radius:8px; padding:0 10px; font-size:13px; font-family:inherit; background:white; width:100%; }
label { display:block; font-size:12px; font-weight:600; margin-bottom:4px; color:#636E70; }
input[type=text], input[type=email], input[type=password] { width:100%; height:40px; border:1.5px solid #DFE6E9; border-radius:8px; padding:0 12px; font-size:13px; font-family:inherit; }
.btn { padding:10px 20px; background:#6C5CE7; color:white; border:none; border-radius:8px; font-size:13px; font-weight:600; cursor:pointer; }
.btn:hover { background:#5A4BD1; }
.btn:disabled { opacity:0.5; }
.row { display:flex; gap:12px; margin-bottom:14px; }
.field { flex:1; }
</style>
