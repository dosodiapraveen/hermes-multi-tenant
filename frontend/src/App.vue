<template>
  <div class="app-layout" v-if="isLoggedIn">
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="logo-icon">H</div>
        <span class="logo-text">Hermes Admin</span>
      </div>
      <nav class="sidebar-nav">
        <router-link to="/dashboard" class="nav-item" active-class="active">
          <span class="nav-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
          </span>
          <span>Dashboard</span>
        </router-link>
        <router-link to="/users" class="nav-item" active-class="active">
          <span class="nav-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
          </span>
          <span>Users</span>
        </router-link>
        <router-link to="/invites" class="nav-item" active-class="active">
          <span class="nav-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
          </span>
          <span>Invites</span>
        </router-link>
        <router-link to="/settings" class="nav-item" active-class="active">
          <span class="nav-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
          </span>
          <span>Settings</span>
        </router-link>
      </nav>
      <div class="sidebar-footer">
        <div class="user-info">
          <div class="user-avatar">{{ userEmail.charAt(0).toUpperCase() }}</div>
          <div class="user-details">
            <span class="user-email">{{ userEmail }}</span>
          </div>
        </div>
        <button class="logout-btn" @click="logout">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
          Logout
        </button>
      </div>
    </aside>
    <main class="main-content">
      <router-view />
    </main>
  </div>
  <router-view v-else />
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      userEmail: localStorage.getItem('user_email') || 'Admin',
    }
  },
  computed: {
    isLoggedIn() {
      return !!localStorage.getItem('access_token')
    },
  },
  methods: {
    logout() {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user_email')
      this.$router.push('/login')
    },
  },
  created() {
    this.$router.afterEach(() => {
      this.userEmail = localStorage.getItem('user_email') || 'Admin'
    })
  },
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  background: #F0F2F5;
  color: #1A1A2E;
}

.app-layout {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: 260px;
  min-width: 260px;
  background: #1A1A2E;
  color: #fff;
  display: flex;
  flex-direction: column;
  padding: 0;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 100;
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 24px 20px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
}

.logo-icon {
  width: 36px;
  height: 36px;
  background: #6C5CE7;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 18px;
  color: #fff;
}

.logo-text {
  font-size: 18px;
  font-weight: 700;
  letter-spacing: -0.3px;
}

.sidebar-nav {
  flex: 1;
  padding: 16px 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 10px;
  color: rgba(255,255,255,0.6);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.15s ease;
}

.nav-item:hover {
  background: rgba(255,255,255,0.06);
  color: rgba(255,255,255,0.9);
}

.nav-item.active {
  background: rgba(108, 92, 231, 0.2);
  color: #fff;
}

.nav-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
}

.sidebar-footer {
  padding: 16px 12px;
  border-top: 1px solid rgba(255,255,255,0.08);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: #6C5CE7;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 14px;
  color: #fff;
}

.user-details {
  flex: 1;
  min-width: 0;
}

.user-email {
  font-size: 13px;
  font-weight: 500;
  color: rgba(255,255,255,0.7);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: block;
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 10px 16px;
  border: none;
  background: rgba(255,255,255,0.06);
  border-radius: 8px;
  color: rgba(255,255,255,0.5);
  font-family: 'Inter', sans-serif;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.logout-btn:hover {
  background: rgba(255,75,75,0.2);
  color: #FF6B6B;
}

.main-content {
  flex: 1;
  margin-left: 260px;
  padding: 32px;
  min-height: 100vh;
}
</style>
