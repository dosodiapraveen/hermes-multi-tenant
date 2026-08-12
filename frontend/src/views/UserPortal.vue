<template>
  <div class="portal">
    <div class="header">
      <h1>{{ user }}</h1>
      <div class="tabs">
        <button v-for="t in tabs" :key="t.key" :class="{active: tab===t.key}" @click="tab=t.key">{{ t.label }}</button>
      </div>
    </div>

    <!-- Notes -->
    <div v-if="tab==='notes'" class="section">
      <h2>📝 Notes</h2>
      <div v-for="n in notes" :key="n.file" class="card">
        <strong>{{ n.title }}</strong>
        <p>{{ n.preview.slice(0,150) }}</p>
      </div>
      <p v-if="!notes.length">No notes yet. Tell your agent to save one!</p>
    </div>

    <!-- Reminders -->
    <div v-if="tab==='reminders'" class="section">
      <h2>⏰ Reminders</h2>
      <div v-for="r in reminders" :key="r.id" class="card" :class="{done: r.done}">
        <span>{{ r.done ? '✅' : '⏳' }}</span>
        <span>{{ r.title }}</span>
        <small v-if="r.remind_at">{{ r.remind_at.slice(0,10) }}</small>
      </div>
      <p v-if="!reminders.length">No reminders yet.</p>
    </div>

    <!-- Projects -->
    <div v-if="tab==='projects'" class="section">
      <h2>📋 Projects</h2>
      <div v-for="p in projects" :key="p.id" class="card">
        <strong>{{ p.title }}</strong>
        <span :class="'badge badge-'+p.status">{{ p.status }}</span>
        <p>{{ p.description.slice(0,100) }}</p>
      </div>
      <p v-if="!projects.length">No projects yet.</p>
    </div>

    <!-- Activity -->
    <div v-if="tab==='activity'" class="section">
      <h2>📊 Recent Activity</h2>
      <div v-for="a in activity" :key="a.time" class="card">
        <small>{{ a.time.slice(0,10) }}</small>
        <strong>{{ a.action }}</strong>
      </div>
      <p v-if="!activity.length">No activity yet.</p>
    </div>
  </div>
</template>

<script>
export default {
  data() { return {
    token: localStorage.getItem('portal_token') || new URLSearchParams(location.search).get('token') || '',
    tab: 'notes',
    user: 'My Dashboard',
    notes: [], reminders: [], projects: [], activity: [],
    tabs: [{key:'notes',label:'📝 Notes'},{key:'reminders',label:'⏰ Reminders'},{key:'projects',label:'📋 Projects'},{key:'activity',label:'📊 Activity'}],
  }},
  methods: {
    async fetchData() {
      if (!this.token) return
      localStorage.setItem('portal_token', this.token)
      for (const ep of ['notes','reminders','projects','activity']) {
        try {
          const r = await fetch('/api/me/'+ep, {headers: {'X-Access-Token': this.token}})
          const d = await r.json()
          if (ep === 'notes') { this.notes = d.notes || []; this.user = d.user || this.user }
          if (ep === 'reminders') this.reminders = d.reminders || []
          if (ep === 'projects') this.projects = d.projects || []
          if (ep === 'activity') this.activity = d.activity || []
        } catch(e) {}
      }
    }
  },
  mounted() { this.fetchData() }
}
</script>

<style scoped>
.portal { max-width: 600px; margin: 0 auto; padding: 20px; }
.header { text-align: center; margin-bottom: 20px; }
.tabs { display: flex; gap: 8px; justify-content: center; }
.tabs button { padding: 8px 16px; border: 1px solid #ddd; background: #fff; border-radius: 8px; cursor: pointer; }
.tabs button.active { background: #6C5CE7; color: #fff; border-color: #6C5CE7; }
.section h2 { margin: 16px 0; }
.card { background: #f9f9f9; padding: 12px; border-radius: 8px; margin: 8px 0; }
.card.done { opacity: 0.6; }
.badge { font-size: 11px; padding: 2px 8px; border-radius: 10px; margin-left: 8px; }
.badge-active { background: #d4edda; }
.badge-paused { background: #fff3cd; }
.badge-done { background: #cce5ff; }
.badge-archived { background: #e2e3e5; }
.card small { display: block; color: #666; }
.card p { margin: 4px 0 0; color: #555; }
</style>