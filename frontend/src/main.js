import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import Landing from './views/Landing.vue'
import Login from './views/Login.vue'
import AdminLogin from './views/AdminLogin.vue'
import Dashboard from './views/Dashboard.vue'
import Users from './views/Users.vue'
import Invites from './views/Invites.vue'
import Join from './views/Join.vue'
import Usage from './views/Usage.vue'
import UserPortal from './views/UserPortal.vue'
import UserRegister from './views/UserRegister.vue'
import UserAgentAccess from './views/UserAgentAccess.vue'
import UserLogin from './views/UserLogin.vue'
import UserForgot from './views/UserForgot.vue'
import UserReset from './views/UserReset.vue'
import UserVerify from './views/UserVerify.vue'
import RegistrationRequests from './views/RegistrationRequests.vue'
import Settings from './views/Settings.vue'

const routes = [
  { path: '/', name: 'Landing', component: Landing, meta: { public: true } },
  { path: '/login', redirect: '/user/login' },
  { path: '/internal/admin-login', name: 'AdminLogin', component: AdminLogin, meta: { public: true } },
  { path: '/join/:code', name: 'Join', component: Join, meta: { public: true } },
  { path: '/dashboard', name: 'Dashboard', component: Dashboard, meta: { requiresAuth: true } },
  { path: '/users', name: 'Users', component: Users, meta: { requiresAuth: true } },
  { path: '/invites', name: 'Invites', component: Invites, meta: { requiresAuth: true } },
  { path: '/usage', name: 'Usage', component: Usage, meta: { requiresAuth: true } },
  { path: '/user', redirect: '/user/dashboard' },
  { path: '/portal', redirect: '/user/dashboard' },
  { path: '/user/dashboard', name: 'UserPortal', component: UserPortal, meta: { public: true } },
  { path: '/user/register', name: 'UserRegister', component: UserRegister, meta: { public: true } },
  { path: '/user/agent-access', name: 'UserAgentAccess', component: UserAgentAccess, meta: { public: true } },
  { path: '/user/login', name: 'UserLogin', component: UserLogin, meta: { public: true } },
  { path: '/user/forgot', name: 'UserForgot', component: UserForgot, meta: { public: true } },
  { path: '/user/reset', name: 'UserReset', component: UserReset, meta: { public: true } },
  { path: '/user/verify', name: 'UserVerify', component: UserVerify, meta: { public: true } },
  { path: '/registration-requests', name: 'RegistrationRequests', component: RegistrationRequests, meta: { requiresAuth: true } },
  { path: '/settings', name: 'Settings', component: Settings, meta: { requiresAuth: true } },
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && !token) {
    next('/user/login')
  } else {
    next()
  }
})

const app = createApp(App)
app.use(router)
app.mount('#app')
