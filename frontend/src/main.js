import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import Login from './views/Login.vue'
import Dashboard from './views/Dashboard.vue'
import Users from './views/Users.vue'
import Invites from './views/Invites.vue'
import Settings from './views/Settings.vue'

const routes = [
  { path: '/', redirect: '/dashboard' },
  { path: '/login', component: Login },
  { path: '/dashboard', component: Dashboard, meta: { auth: true } },
  { path: '/users', component: Users, meta: { auth: true } },
  { path: '/invites', component: Invites, meta: { auth: true } },
  { path: '/settings', component: Settings, meta: { auth: true } },
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to, from, next) => {
  if (to.meta.auth && !localStorage.getItem('token')) next('/login')
  else next()
})

createApp(App).use(router).mount('#app')
