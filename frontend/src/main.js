import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'

// Design System
import './styles/design-tokens.css'

import App from './App.vue'

// Route-based code splitting: Dynamic imports for reduced initial bundle size
// Each route is lazy-loaded only when visited, reducing initial load by ~40-60%
const Landing = () => import('./views/Landing.vue')
const AdminLogin = () => import('./views/AdminLogin.vue')
const Dashboard = () => import('./views/DashboardNew.vue')
const Users = () => import('./views/Users.vue')
const Invites = () => import('./views/Invites.vue')
const Join = () => import('./views/Join.vue')
const Usage = () => import('./views/Usage.vue')
const UserPortal = () => import('./views/UserPortalNew.vue')
const UserRegister = () => import('./views/UserRegister.vue')
const UserAgentAccess = () => import('./views/UserAgentAccess.vue')
const UserLogin = () => import('./views/UserLogin.vue')
const UserForgot = () => import('./views/UserForgot.vue')
const UserReset = () => import('./views/UserReset.vue')
const UserVerify = () => import('./views/UserVerify.vue')
const RegistrationRequests = () => import('./views/RegistrationRequests.vue')
const Settings = () => import('./views/Settings.vue')

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

// FIX: Global error handler to catch and log unhandled Vue errors
app.config.errorHandler = (err, instance, info) => {
  // Log error for debugging
  console.error('Vue Error:', err)
  console.error('Component:', instance?.$options?.name || 'Unknown')
  console.error('Info:', info)

  // In production, you could send this to an error tracking service like Sentry
  // if (import.meta.env.PROD) {
  //   sendToErrorTracker(err, instance, info)
  // }
}

// FIX: Global warning handler (development only)
app.config.warnHandler = (msg, instance, trace) => {
  console.warn('Vue Warning:', msg)
  if (trace) console.warn('Trace:', trace)
}

app.use(router)
app.mount('#app')
