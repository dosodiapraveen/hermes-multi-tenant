<template>
  <div class="app-layout" v-if="isLoggedIn">
    <!-- Mobile overlay -->
    <Transition name="fade">
      <div
        v-if="sidebarOpen"
        class="sidebar-overlay"
        @click="sidebarOpen = false"
      ></div>
    </Transition>

    <!-- Mobile menu button -->
    <button
      class="mobile-menu-toggle"
      :aria-expanded="sidebarOpen"
      aria-controls="sidebar"
      aria-label="Toggle sidebar menu"
      @click="sidebarOpen = !sidebarOpen"
    >
      <svg v-if="!sidebarOpen" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="3" y1="12" x2="21" y2="12"></line>
        <line x1="3" y1="6" x2="21" y2="6"></line>
        <line x1="3" y1="18" x2="21" y2="18"></line>
      </svg>
      <svg v-else width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="18" y1="6" x2="6" y2="18"></line>
        <line x1="6" y1="6" x2="18" y2="18"></line>
      </svg>
    </button>

    <aside
      id="sidebar"
      :class="['sidebar', { 'sidebar--open': sidebarOpen }]"
    >
      <div class="sidebar-header">
        <div class="logo-icon">H</div>
        <div class="logo-text">
          <span class="logo-title">Hermes</span>
          <span class="logo-sub">Admin Panel</span>
        </div>
      </div>
      <nav class="sidebar-nav">
        <router-link to="/dashboard" class="nav-item" active-class="active" @click="closeSidebarOnMobile">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
          <span>Dashboard</span>
        </router-link>
        <router-link to="/users" class="nav-item" active-class="active" @click="closeSidebarOnMobile">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
          <span>Users</span>
        </router-link>
        <router-link to="/invites" class="nav-item" active-class="active" @click="closeSidebarOnMobile">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
          <span>Invites</span>
        </router-link>
        <router-link to="/registration-requests" class="nav-item" active-class="active" @click="closeSidebarOnMobile">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 8v4l3 3"/><circle cx="12" cy="12" r="10"/></svg>
          <span>Requests</span>
        </router-link>
        <router-link to="/usage" class="nav-item" active-class="active" @click="closeSidebarOnMobile">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
          <span>Usage</span>
        </router-link>
        <router-link to="/settings" class="nav-item" active-class="active" @click="closeSidebarOnMobile">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
          <span>Settings</span>
        </router-link>
      </nav>
      <div class="sidebar-footer">
        <div class="user-info">
          <div class="user-avatar">{{ userEmail.charAt(0).toUpperCase() }}</div>
          <div class="user-details"><span class="user-email">{{ userEmail }}</span></div>
        </div>
        <button class="logout-btn" @click="logout">Logout</button>
      </div>
    </aside>
    <main class="main-content"><router-view /></main>
  </div>
  <router-view v-else />
</template>

<script>
export default {
  data() {
    return {
      userEmail: localStorage.getItem('email') || 'Admin',
      sidebarOpen: false
    }
  },
  computed: {
    isLoggedIn() { return !!localStorage.getItem('token') }
  },
  methods: {
    logout() {
      localStorage.removeItem('token')
      localStorage.removeItem('email')
      this.$router.push('/internal/admin-login')
    },
    closeSidebarOnMobile() {
      if (window.innerWidth < 600) {
        this.sidebarOpen = false
      }
    }
  },
  created() {
    this.$router.afterEach(() => {
      this.userEmail = localStorage.getItem('email') || 'Admin'
    })
  }
}
</script>

<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:var(--font-family-base); background:var(--color-background); color:var(--color-text-primary); }
.app-layout { display:flex; min-height:100vh; }

/* Mobile menu toggle */
.mobile-menu-toggle {
  display: none;
  position: fixed;
  top: 16px;
  left: 16px;
  z-index: 200;
  width: 44px;
  height: 44px;
  padding: 0;
  background: #1A1A2E;
  border: none;
  border-radius: 10px;
  color: #fff;
  cursor: pointer;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
  transition: all 0.2s;
}

.mobile-menu-toggle:hover {
  background: #252542;
}

/* Sidebar overlay */
.sidebar-overlay {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  z-index: 99;
}

/* Sidebar */
.sidebar {
  width: 240px;
  min-width: 240px;
  background: #1A1A2E;
  color: #fff;
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 100;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.sidebar-header { display:flex; align-items:center; gap:12px; padding:24px 20px 20px; border-bottom:1px solid rgba(255,255,255,0.06); }
.logo-icon { width:36px; height:36px; background:linear-gradient(135deg,#6C5CE7,#A29BFE); border-radius:10px; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:18px; color:#fff; flex-shrink:0; }
.logo-title { font-size:17px; font-weight:700; letter-spacing:-0.3px; display:block; line-height:1.2; }
.logo-sub { font-size:11px; color:rgba(255,255,255,0.35); font-weight:400; display:block; }
.sidebar-nav { flex:1; padding:16px 10px; display:flex; flex-direction:column; gap:2px; }
.nav-item { display:flex; align-items:center; gap:12px; padding:10px 14px; border-radius:8px; color:rgba(255,255,255,0.5); text-decoration:none; font-size:13.5px; font-weight:500; transition:all .15s; }
.nav-item:hover { background:rgba(255,255,255,0.06); color:rgba(255,255,255,0.85); }
.nav-item.active { background:rgba(108,92,231,0.15); color:#fff; }
.sidebar-footer { padding:14px 12px; border-top:1px solid rgba(255,255,255,0.06); }
.user-info { display:flex; align-items:center; gap:10px; margin-bottom:10px; }
.user-avatar { width:30px; height:30px; border-radius:7px; background:linear-gradient(135deg,#6C5CE7,#A29BFE); display:flex; align-items:center; justify-content:center; font-weight:700; font-size:13px; color:#fff; flex-shrink:0; }
.user-email { font-size:12.5px; color:rgba(255,255,255,0.5); overflow:hidden; text-overflow:ellipsis; white-space:nowrap; display:block; }
.logout-btn { width:100%; padding:8px 14px; border:none; background:rgba(255,255,255,0.04); border-radius:7px; color:rgba(255,255,255,0.4); font-family:'Inter',sans-serif; font-size:12.5px; font-weight:500; cursor:pointer; transition:all .15s; }
.logout-btn:hover { background:rgba(255,75,75,0.15); color:#FF6B6B; }
.main-content { flex:1; margin-left:240px; padding:32px; min-height:100vh; }

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Mobile responsive */
@media (max-width: 600px) {
  .mobile-menu-toggle {
    display: flex;
  }

  .sidebar-overlay {
    display: block;
  }

  .sidebar {
    transform: translateX(-100%);
  }

  .sidebar--open {
    transform: translateX(0);
  }

  .main-content {
    margin-left: 0;
    padding: 72px 16px 24px;
  }
}

/* Tablet adjustments */
@media (min-width: 601px) and (max-width: 1024px) {
  .sidebar {
    width: 200px;
    min-width: 200px;
  }

  .main-content {
    margin-left: 200px;
    padding: 24px;
  }

  .logo-text {
    display: none;
  }

  .sidebar-header {
    justify-content: center;
    padding: 20px;
  }

  .nav-item span {
    display: none;
  }

  .nav-item {
    justify-content: center;
  }

  .user-details {
    display: none;
  }

  .user-info {
    justify-content: center;
  }
}
</style>
