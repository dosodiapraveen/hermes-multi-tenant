<template>
  <div class="portal">
    <!-- Header -->
    <header>
      <div class="header-content">
        <h1>🏠 {{ user }}</h1>
        <nav>
          <button v-for="t in tabs" :key="t.key" :class="{active: tab===t.key}" @click="tab=t.key">
            {{ t.label }}
            <span v-if="counts[t.key]" class="badge">{{ counts[t.key] }}</span>
          </button>
        </nav>
        <button class="btn-outline" @click="logout">Logout</button>
      </div>
    </header>

    <main>
      <!-- Dashboard Overview -->
      <section v-if="tab==='dashboard'" class="dashboard">
        <div class="grid">
          <div class="card" @click="tab='notes'">
            <h3>📝 Notes</h3>
            <p class="count">{{ notes.length }}</p>
            <p class="sub">View all notes</p>
          </div>
          <div class="card" @click="tab='reminders'">
            <h3>⏰ Reminders</h3>
            <p class="count">{{ reminders.filter(r=>!r.done).length }}</p>
            <p class="sub">{{ reminders.filter(r=>r.done).length }} completed</p>
          </div>
          <div class="card" @click="tab='projects'">
            <h3>📋 Projects</h3>
            <p class="count">{{ projects.length }}</p>
            <p class="sub">{{ projects.filter(p=>p.status==='active').length }} active</p>
          </div>
          <div class="card" @click="tab='activity'">
            <h3>📊 Activity</h3>
            <p class="count">{{ activity.length }}</p>
            <p class="sub">Recent activity</p>
          </div>
        </div>
        <div class="quick-tips">
          <p>💡 <strong>Try telling your agent:</strong> "Remind me tomorrow at 2 PM to submit the report" or "Create project Q4 Planning"</p>
        </div>
      </section>

      <!-- Notes -->
      <section v-if="tab==='notes'">
        <div class="section-header"><h2>📝 Notes</h2></div>
        <input v-model="noteSearch" placeholder="Search notes..." class="search" />
        <div v-for="n in filteredNotes" :key="n.file" class="list-item" @click="n.expand=!n.expand">
          <div class="item-title">{{ n.title }}</div>
          <div v-if="n.expand" class="item-body">{{ n.preview }}</div>
        </div>
        <p v-if="!filteredNotes.length" class="empty">No notes yet. Send a message to your agent!</p>
      </section>

      <!-- Reminders -->
      <section v-if="tab==='reminders'">
        <div class="section-header"><h2>⏰ Reminders</h2></div>
        <div v-for="r in reminders" :key="r.id" class="list-item" :class="{done: r.done}">
          <label class="checkbox">
            <input type="checkbox" :checked="r.done" @change="r.done=!r.done;toggleReminder(r)" />
            <span></span>
          </label>
          <div>
            <div class="item-title" :class="r.done?'strikethrough':''">{{ r.title }}</div>
            <div class="item-meta" v-if="r.remind_at">{{ formatDate(r.remind_at) }}</div>
          </div>
        </div>
        <p v-if="!reminders.length" class="empty">No reminders. Tell your agent: "Remind me..."</p>
      </section>

      <!-- Projects -->
      <section v-if="tab==='projects'">
        <div class="section-header"><h2>📋 Projects</h2></div>
        <div class="kanban">
          <div v-for="s in statuses" :key="s.key" class="column">
            <h3>{{ s.label }}</h3>
            <div v-for="p in projects.filter(p=>p.status===s.key)" :key="p.id" class="card project-card">
              <strong>{{ p.title }}</strong>
              <p>{{ p.description.slice(0,80) }}</p>
              <div class="actions">
                <select :value="p.status" @change="updateStatus(p,$event.target.value)">
                  <option v-for="opt in statuses" :key="opt.key" :value="opt.key">{{ opt.label }}</option>
                </select>
              </div>
            </div>
          </div>
        </div>
        <p v-if="!projects.length" class="empty">No projects yet. Tell your agent: "Create project..."</p>
      </section>

      <!-- Activity -->
      <section v-if="tab==='activity'">
        <div class="section-header"><h2>📊 Activity</h2></div>
        <div v-for="a in activity" :key="a.time" class="list-item">
          <div class="timeline-dot"></div>
          <div>
            <div class="item-meta">{{ formatDate(a.time) }}</div>
            <div class="item-title">{{ a.action }}</div>
          </div>
        </div>
        <p v-if="!activity.length" class="empty">No activity yet.</p>
      </section>
    </main>
  </div>
</template>

<script>
export default {
  data() { return {
    token: localStorage.getItem('portal_token') || '',
    tab: 'dashboard',
    user: 'My Dashboard',
    notes: [], reminders: [], projects: [], activity: [],
    noteSearch: '',
    statuses: [
      {key:'active',label:'🟢 Active'},
      {key:'paused',label:'🟡 Paused'},
      {key:'done',label:'✅ Done'},
      {key:'archived',label:'📦 Archived'},
    ],
    tabs: [
      {key:'dashboard',label:'🏠'},
      {key:'notes',label:'Notes'},
      {key:'reminders',label:'Reminders'},
      {key:'projects',label:'Projects'},
      {key:'activity',label:'Activity'},
    ],
  }},
  computed: {
    counts() {
      return {
        notes: this.notes.length,
        reminders: this.reminders.filter(r=>!r.done).length,
        projects: this.projects.filter(p=>p.status==='active').length,
        activity: this.activity.length,
      }
    },
    filteredNotes() {
      if (!this.noteSearch) return this.notes
      return this.notes.filter(n => n.title.toLowerCase().includes(this.noteSearch.toLowerCase()))
    }
  },
  methods: {
    formatDate(d) {
      try { return new Date(d).toLocaleDateString('en-US',{month:'short',day:'numeric',hour:'2-digit',minute:'2-digit'}) }
      catch(e) { return d.slice(0,10) }
    },
    async fetchData() {
      if (!this.token) { window.location='/portal-login'; return }
      for (const ep of ['notes','reminders','projects','activity']) {
        try {
          const r=await fetch('/api/me/'+ep,{headers:{'Authorization':'Bearer '+this.token}})
          if (r.status===401) { localStorage.removeItem('portal_token'); window.location='/portal-login'; return }
          const d=await r.json()
          if (ep==='notes') { this.notes=d.notes||[]; this.user=d.user||this.user }
          if (ep==='reminders') this.reminders=d.reminders||[]
          if (ep==='projects') this.projects=d.projects||[]
          if (ep==='activity') this.activity=d.activity||[]
        }catch(e){}
      }
    },
    logout() { localStorage.removeItem('portal_token'); localStorage.removeItem('profile_id'); window.location='/portal-login' },
    toggleReminder(r) {},
    updateStatus(p,v) { p.status=v },
  },
  mounted() { this.fetchData() }
}
</script>

<style scoped>
.portal { min-height:100vh; background:#f5f5f7; font-family:-apple-system,BlinkMacSystemFont,sans-serif }
header { background:#fff; border-bottom:1px solid #e5e5ea; position:sticky; top:0; z-index:10; }
.header-content { max-width:900px; margin:0 auto; padding:12px 20px; display:flex; align-items:center; gap:16px; flex-wrap:wrap; }
.header-content h1 { font-size:18px; margin:0; flex:1; min-width:120px; }
nav { display:flex; gap:4px; }
nav button { padding:6px 14px; border:1px solid transparent; border-radius:6px; background:transparent; cursor:pointer; font-size:14px; position:relative; white-space:nowrap; }
nav button.active { background:#6C5CE7; color:#fff; }
nav button .badge { position:absolute; top:-4px; right:-4px; background:#ff4757; color:#fff; font-size:10px; padding:1px 5px; border-radius:8px; }
.btn-outline { padding:6px 14px; border:1px solid #ddd; border-radius:6px; background:#fff; cursor:pointer; font-size:14px; white-space:nowrap; }

main { max-width:900px; margin:0 auto; padding:20px; }

.grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:12px; margin-bottom:20px; }
.grid .card { background:#fff; padding:20px; border-radius:12px; cursor:pointer; transition:transform .15s,box-shadow .15s; }
.grid .card:hover { transform:translateY(-2px); box-shadow:0 4px 12px rgba(0,0,0,.08); }
.grid .card h3 { margin:0 0 8px; font-size:18px; }
.grid .card .count { font-size:32px; font-weight:700; margin:0; color:#6C5CE7; }
.grid .card .sub { font-size:12px; color:#888; margin:4px 0 0; }

.quick-tips { background:#eef1ff; padding:12px 16px; border-radius:10px; font-size:14px; color:#444; }
.quick-tips p { margin:0; }

.section-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; }
.section-header h2 { margin:0; font-size:20px; }

.search { width:100%; padding:10px 14px; border:1px solid #ddd; border-radius:10px; font-size:14px; margin-bottom:12px; box-sizing:border-box; }

.list-item { background:#fff; padding:12px 16px; border-radius:10px; margin:6px 0; display:flex; align-items:flex-start; gap:10px; cursor:pointer; }
.list-item.done { opacity:.5; }
.item-title { font-weight:500; margin-bottom:2px; }
.item-title.strikethrough { text-decoration:line-through; }
.item-meta { font-size:12px; color:#888; }
.item-body { font-size:13px; color:#555; margin-top:6px; white-space:pre-wrap; }
.empty { color:#888; text-align:center; padding:40px 0; }

.checkbox { display:flex; align-items:center; cursor:pointer; padding-top:2px; }
.checkbox input { display:none; }
.checkbox span { width:18px; height:18px; border:2px solid #ddd; border-radius:4px; display:inline-block; position:relative; flex-shrink:0; }
.checkbox input:checked+span { background:#6C5CE7; border-color:#6C5CE7; }
.checkbox input:checked+span:after { content:'✓'; color:#fff; position:absolute; top:-1px; left:3px; font-size:13px; }

.kanban { display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:10px; }
.column { background:#f0f0f2; border-radius:10px; padding:10px; min-height:100px; }
.column h3 { margin:0 0 8px; font-size:14px; }
.project-card { padding:10px; margin:6px 0; font-size:13px; }
.project-card p { margin:4px 0; color:#666; }
.actions select { font-size:11px; padding:2px 6px; border:1px solid #ddd; border-radius:4px; margin-top:4px; }

.timeline-dot { width:8px; height:8px; background:#6C5CE7; border-radius:50%; margin-top:6px; flex-shrink:0; }

@media(max-width:600px){ .kanban{grid-template-columns:1fr} .grid{grid-template-columns:1fr 1fr} }
</style>