<template>
  <div class="portal">
    <header>
      <div class="header-content">
        <h1>🏠 {{ user }}</h1>
        <nav>
          <button v-for="t in tabs" :key="t.key" :class="{active: tab===t.key}" @click="tab=t.key" @click.prevent>{{ t.label }}<span v-if="counts[t.key]" class="badge">{{ counts[t.key] }}</span></button>
        </nav>
        <button class="btn-outline" @click="logout">Logout</button>
      </div>
    </header>

    <main>
      <!-- ─────── DASHBOARD ─────── -->
      <section v-if="tab==='dashboard'">
        <div class="grid">
          <div class="card" @click="tab='ideas'"><h3>💡 Ideas</h3><p class="count">{{ ideas.length }}</p></div>
          <div class="card" @click="tab='notes'"><h3>📝 Notes</h3><p class="count">{{ notes.length }}</p></div>
          <div class="card" @click="tab='reminders'"><h3>⏰ Reminders</h3><p class="count">{{ reminders.filter(r=>!r.done).length }}</p></div>
          <div class="card" @click="tab='projects'"><h3>📋 Projects</h3><p class="count">{{ projects.length }}</p></div>
        </div>

        <h3 style="margin:20px 0 12px;font-size:16px">📅 Upcoming Events</h3>
        <div v-if="upcomingEvents.length" class="widget-list">
          <div v-for="evt in upcomingEvents" :key="evt.id" class="widget-item" @click="tab='schedule'">
            <span class="event-date">{{ formatEventDate(evt.event_start).split(' ')[0] }}</span>
            <strong>{{ evt.title }}</strong>
            <span v-if="evt.location" class="item-meta">📍 {{ evt.location }}</span>
          </div>
        </div>
        <p v-else class="empty-widget">No upcoming events</p>

        <h3 style="margin:20px 0 12px;font-size:16px">💭 Recent Ideas</h3>
        <div v-if="recentIdeas.length" class="widget-list">
          <div v-for="idea in recentIdeas" :key="idea.id" class="widget-item" @click="tab='ideas'">
            <span :class="'badge-status badge-'+idea.status">{{ statusBadge(idea.status) }}</span>
            <strong>{{ idea.title }}</strong>
          </div>
        </div>
        <p v-else class="empty-widget">No ideas yet - start brainstorming!</p>

        <div v-if="failedJobs.length" class="warning-box">
          ⚠️ <strong>{{ failedJobs.length }}</strong> background job(s) need attention - <a @click="tab='jobs'" style="color:#e74c3c;cursor:pointer;text-decoration:underline">View Jobs</a>
        </div>
      </section>

      <!-- ─────── NOTES ─────── -->
      <section v-if="tab==='notes'">
        <div class="section-header"><h2>📝 Notes</h2><button class="btn-primary" @click="openNoteModal()">+ New Note</button></div>
        
        <div class="filter-bar">
          <input v-model="noteSearch" placeholder="Search notes..." class="search" />
          <select v-model="noteCategoryFilter"><option value="">All categories</option><option v-for="c in noteCategories" :key="c" :value="c">{{ c }}</option></select>
        </div>

        <div v-for="n in filteredNotes" :key="n.id" class="list-item" :class="{expanded: expandedNote===n.id}" @click="expandedNote=expandedNote===n.id?null:n.id">
          <div class="item-top"><span class="badge-cat">{{ n.category }}</span><span class="item-title">{{ n.title }}</span><span class="item-meta">{{ n.updated_at?.slice(0,10) }}</span></div>
          <div v-if="expandedNote===n.id" class="item-body">
            <p>{{ n.content }}</p>
            <div class="item-actions">
              <button class="btn-sm" @click.stop="openNoteModal(n)">Edit</button>
              <button class="btn-sm btn-danger" @click.stop="deleteNote(n.id)">Delete</button>
            </div>
          </div>
        </div>
        <p v-if="!filteredNotes.length" class="empty">No notes yet.</p>
      </section>

      <!-- ─────── IDEAS ─────── -->
      <section v-if="tab==='ideas'">
        <div class="section-header"><h2>💡 Ideas</h2><button class="btn-primary" @click="openIdeaModal()">+ New Idea</button></div>

        <div class="idea-grid">
          <div v-for="idea in ideas" :key="idea.id" class="idea-card">
            <div class="idea-header">
              <strong>{{ idea.title }}</strong>
              <span :class="'badge-status badge-'+idea.status">{{ statusBadge(idea.status) }}</span>
            </div>
            <p class="idea-content">{{ idea.content?.slice(0,100) }}</p>
            <div class="idea-footer">
              <span v-if="idea.tags" class="idea-tags">{{ idea.tags }}</span>
              <div class="item-actions">
                <button class="btn-sm" @click="openIdeaModal(idea)">Edit</button>
                <button class="btn-sm btn-danger" @click="deleteIdea(idea.id)">Delete</button>
              </div>
            </div>
          </div>
        </div>
        <p v-if="!ideas.length" class="empty">No ideas yet. Start brainstorming!</p>
      </section>

      <!-- ─────── SCHEDULE ─────── -->
      <section v-if="tab==='schedule'">
        <div class="section-header"><h2>📅 Schedule</h2><button class="btn-primary" @click="openEventModal()">+ New Event</button></div>

        <div v-for="evt in events" :key="evt.id" class="list-item event-item">
          <div style="flex:1">
            <div class="item-top">
              <span class="event-date">{{ formatEventDate(evt.event_start) }}</span>
              <strong class="item-title">{{ evt.title }}</strong>
              <span v-if="evt.is_all_day" class="badge-cat">All Day</span>
            </div>
            <div v-if="evt.description" class="item-meta">{{ evt.description }}</div>
            <div class="item-meta" v-if="evt.location">📍 {{ evt.location }}</div>
          </div>
          <div class="item-actions">
            <button class="btn-sm" @click="openEventModal(evt)">Edit</button>
            <button class="btn-sm btn-danger" @click="deleteEvent(evt.id)">Delete</button>
          </div>
        </div>
        <p v-if="!events.length" class="empty">No events scheduled yet.</p>
      </section>

      <!-- ─────── REMINDERS ─────── -->
      <section v-if="tab==='reminders'">
        <div class="section-header"><h2>⏰ Reminders</h2><button class="btn-primary" @click="openReminderModal()">+ New Reminder</button></div>
        <div v-for="r in reminders" :key="r.id" class="list-item" :class="{done:r.done}">
          <label class="checkbox"><input type="checkbox" :checked="r.done" @change="toggleReminder(r)" /><span></span></label>
          <div style="flex:1"><div class="item-title" :class="r.done?'strikethrough':''">{{ r.title }}</div><div class="item-meta" v-if="r.remind_at">{{ r.remind_at.slice(0,16).replace('T', ' ') }}</div></div>
          <button class="btn-sm btn-danger" @click.stop="deleteReminder(r.id)">Delete</button>
        </div>
        <p v-if="!reminders.length" class="empty">No reminders yet.</p>
      </section>

      <!-- ─────── PROJECTS ─────── -->
      <section v-if="tab==='projects'">
        <div class="section-header"><h2>📋 Projects</h2><button class="btn-primary" @click="openProjectModal()">+ New Project</button></div>
        
        <div v-if="!selectedProject" class="project-grid">
          <div v-for="p in projects" :key="p.id" class="card project-card" @click="selectProject(p)">
            <div class="project-top"><strong>{{ p.title }}</strong><span :class="'badge badge-'+p.status">{{ statusLabel(p.status) }}</span></div>
            <p>{{ p.description?.slice(0,80) }}</p>
            <div class="item-meta">Updated {{ p.updated_at?.slice(0,10) }}</div>
          </div>
        </div>

        <!-- Project Detail -->
        <div v-if="selectedProject" class="project-detail">
          <button class="btn-outline" @click="selectedProject=null" style="margin-bottom:12px">← Back to projects</button>
          
          <div class="card">
            <div class="project-detail-header">
              <h2>{{ selectedProject.title }}</h2>
              <select :value="selectedProject.status" @change="updateProjectStatus(selectedProject, $event.target.value)" class="status-select">
                <option v-for="s in ['active','paused','done','archived']" :key="s" :value="s">{{ statusLabel(s) }}</option>
              </select>
            </div>
            <p>{{ selectedProject.description }}</p>
            <div class="item-meta">Created {{ selectedProject.created_at?.slice(0,10) }} · Updated {{ selectedProject.updated_at?.slice(0,10) }}</div>
            <div class="item-actions" style="margin-top:8px">
              <button class="btn-sm" @click="editProjectDetail(selectedProject)">Edit</button>
              <button class="btn-sm btn-danger" @click="deleteProject(selectedProject.id); selectedProject=null">Delete</button>
            </div>
          </div>

          <h3 style="margin:16px 0 8px">📄 Research</h3>
          <button class="btn-primary btn-sm" @click="openResearchModal()">+ Add Research</button>
          <div v-for="r in selectedProject.research||[]" :key="r.id" class="list-item">
            <div><strong>{{ r.title }}</strong><p>{{ r.content }}</p><div class="item-meta">{{ r.created_at?.slice(0,10) }}</div></div>
            <button class="btn-sm btn-danger" @click="deleteResearch(selectedProject.id, r.id)" style="flex-shrink:0">✕</button>
          </div>
          <p v-if="!(selectedProject.research||[]).length" class="empty">No research added yet.</p>
        </div>
      </section>

      <!-- ─────── JOBS ─────── -->
      <section v-if="tab==='jobs'">
        <div class="section-header"><h2>⚙️ Background Jobs</h2><button class="btn-primary" @click="openJobModal()">+ New Job</button></div>

        <div class="jobs-table">
          <div class="job-row job-header">
            <div style="flex:2">Title</div>
            <div style="flex:1">Type</div>
            <div style="flex:1.5">Schedule</div>
            <div style="flex:1">Next Run</div>
            <div style="flex:0.5">Status</div>
            <div style="flex:1">Actions</div>
          </div>
          <div v-for="job in jobs" :key="job.id" class="job-row">
            <div style="flex:2"><strong>{{ job.title }}</strong><div class="item-meta">{{ job.description }}</div></div>
            <div style="flex:1"><span class="badge-cat">{{ job.job_type }}</span></div>
            <div style="flex:1.5" class="item-meta">{{ job.cron_expression }}</div>
            <div style="flex:1" class="item-meta">{{ formatJobDate(job.next_run_at) }}</div>
            <div style="flex:0.5">
              <label class="toggle" @click.stop="toggleJob(job)">
                <input type="checkbox" :checked="job.is_enabled" />
                <span class="toggle-slider"></span>
              </label>
            </div>
            <div style="flex:1" class="item-actions">
              <button class="btn-sm" @click="openJobModal(job)">Edit</button>
              <button class="btn-sm btn-danger" @click="deleteJob(job.id)">Delete</button>
            </div>
          </div>
        </div>
        <p v-if="!jobs.length" class="empty">No background jobs configured yet.</p>
      </section>

      <!-- ─────── ACTIVITY ─────── -->
      <section v-if="tab==='activity'">
        <div class="section-header"><h2>📊 Activity</h2></div>
        <div v-for="a in activity" :key="a.time" class="list-item">
          <div class="timeline-dot"></div>
          <div><div class="item-meta">{{ a.time?.slice(0,10) }}</div><div class="item-title">{{ a.action }}</div></div>
        </div>
        <p v-if="!activity.length" class="empty">No activity yet.</p>
      </section>
    </main>

    <!-- ─────── NOTE MODAL ─────── -->
    <div v-if="showNoteModal" class="modal-overlay" @click.self="showNoteModal=false">
      <div class="modal">
        <h2>{{ editingNote ? 'Edit' : 'New' }} Note</h2>
        <input v-model="noteForm.title" placeholder="Title" />
        <textarea v-model="noteForm.content" placeholder="Content" rows="5"></textarea>
        <div class="modal-row">
          <input v-model="noteForm.category" placeholder="Category (e.g. Work, Personal)" />
          <button class="btn-primary" @click="saveNote">Save</button>
          <button class="btn-outline" @click="showNoteModal=false">Cancel</button>
        </div>
      </div>
    </div>

    <!-- ─────── PROJECT MODAL ─────── -->
    <div v-if="showProjectModal" class="modal-overlay" @click.self="showProjectModal=false">
      <div class="modal">
        <h2>{{ editingProject ? 'Edit' : 'New' }} Project</h2>
        <input v-model="projectForm.title" placeholder="Project title" />
        <textarea v-model="projectForm.description" placeholder="Description" rows="3"></textarea>
        <div class="modal-row">
          <button class="btn-primary" @click="saveProject">Save</button>
          <button class="btn-outline" @click="showProjectModal=false">Cancel</button>
        </div>
      </div>
    </div>

    <!-- ─────── RESEARCH MODAL ─────── -->
    <div v-if="showResearchModal" class="modal-overlay" @click.self="showResearchModal=false">
      <div class="modal">
        <h2>Add Research</h2>
        <input v-model="researchForm.title" placeholder="Title" />
        <textarea v-model="researchForm.content" placeholder="Content" rows="4"></textarea>
        <div class="modal-row">
          <button class="btn-primary" @click="saveResearch">Save</button>
          <button class="btn-outline" @click="showResearchModal=false">Cancel</button>
        </div>
      </div>
    </div>

    <!-- ─────── REMINDER MODAL ─────── -->
    <div v-if="showReminderModal" class="modal-overlay" @click.self="showReminderModal=false">
      <div class="modal">
        <h2>New Reminder</h2>
        <input v-model="reminderForm.title" placeholder="What do you want to be reminded about?" />
        <label style="font-size:13px;color:#666;margin-top:8px;display:block">Remind me at:</label>
        <input v-model="reminderForm.remind_at" type="datetime-local" />
        <div class="modal-row">
          <button class="btn-primary" @click="saveReminder">Save</button>
          <button class="btn-outline" @click="showReminderModal=false">Cancel</button>
        </div>
      </div>
    </div>

    <!-- ─────── IDEA MODAL ─────── -->
    <div v-if="showIdeaModal" class="modal-overlay" @click.self="showIdeaModal=false">
      <div class="modal">
        <h2>{{ editingIdea ? 'Edit' : 'New' }} Idea</h2>
        <input v-model="ideaForm.title" placeholder="Idea title" />
        <textarea v-model="ideaForm.content" placeholder="Details about your idea..." rows="5"></textarea>
        <div class="modal-row">
          <select v-model="ideaForm.status" style="flex:1;padding:10px;border:1px solid #ddd;border-radius:8px">
            <option value="brainstorm">💭 Brainstorm</option>
            <option value="developing">🔨 Developing</option>
            <option value="ready">✅ Ready</option>
            <option value="archived">📦 Archived</option>
          </select>
          <input v-model="ideaForm.tags" placeholder="Tags (comma separated)" style="flex:1" />
        </div>
        <div class="modal-row">
          <button class="btn-primary" @click="saveIdea">Save</button>
          <button class="btn-outline" @click="showIdeaModal=false">Cancel</button>
        </div>
      </div>
    </div>

    <!-- ─────── EVENT MODAL ─────── -->
    <div v-if="showEventModal" class="modal-overlay" @click.self="showEventModal=false">
      <div class="modal">
        <h2>{{ editingEvent ? 'Edit' : 'New' }} Event</h2>
        <input v-model="eventForm.title" placeholder="Event title" />
        <textarea v-model="eventForm.description" placeholder="Description" rows="2"></textarea>
        <div class="modal-row">
          <div style="flex:1">
            <label style="font-size:12px;color:#666;display:block;margin-bottom:4px">Start</label>
            <input v-model="eventForm.event_start" type="datetime-local" />
          </div>
          <div style="flex:1">
            <label style="font-size:12px;color:#666;display:block;margin-bottom:4px">End</label>
            <input v-model="eventForm.event_end" type="datetime-local" />
          </div>
        </div>
        <input v-model="eventForm.location" placeholder="Location (optional)" />
        <label style="font-size:13px;display:flex;align-items:center;gap:8px;margin:8px 0">
          <input type="checkbox" v-model="eventForm.is_all_day" />
          <span>All-day event</span>
        </label>
        <div class="modal-row">
          <button class="btn-primary" @click="saveEvent">Save</button>
          <button class="btn-outline" @click="showEventModal=false">Cancel</button>
        </div>
      </div>
    </div>

    <!-- ─────── JOB MODAL ─────── -->
    <div v-if="showJobModal" class="modal-overlay" @click.self="showJobModal=false">
      <div class="modal">
        <h2>{{ editingJob ? 'Edit' : 'New' }} Background Job</h2>
        <input v-model="jobForm.title" placeholder="Job title" />
        <textarea v-model="jobForm.description" placeholder="Description" rows="2"></textarea>
        <div class="modal-row">
          <select v-model="jobForm.job_type" style="flex:1;padding:10px;border:1px solid #ddd;border-radius:8px">
            <option value="email">📧 Email</option>
            <option value="webhook">🔗 Webhook</option>
            <option value="cleanup">🧹 Cleanup</option>
            <option value="report">📊 Report</option>
            <option value="custom">⚙️ Custom</option>
          </select>
        </div>
        <label style="font-size:13px;color:#666;display:block;margin-top:8px">Schedule (cron)</label>
        <select v-model="jobForm.cron_expression" style="width:100%;padding:10px;border:1px solid #ddd;border-radius:8px;margin:4px 0">
          <option value="0 9 * * *">Daily at 9:00 AM</option>
          <option value="0 0 * * 1">Weekly (Monday midnight)</option>
          <option value="0 0 1 * *">Monthly (1st day)</option>
          <option value="*/30 * * * *">Every 30 minutes</option>
          <option value="0 */6 * * *">Every 6 hours</option>
        </select>
        <div class="modal-row">
          <button class="btn-primary" @click="saveJob">Save</button>
          <button class="btn-outline" @click="showJobModal=false">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data(){return{
    token: localStorage.getItem('portal_token')||'', tab:'dashboard',
    user:'My Dashboard', notes:[], reminders:[], projects:[], activity:[], ideas:[], events:[], jobs:[],
    noteSearch:'', noteCategoryFilter:'', expandedNote:null, selectedProject:null,
    showNoteModal:false, editingNote:null, noteForm:{title:'',content:'',category:'General'},
    showProjectModal:false, editingProject:null, projectForm:{title:'',description:''},
    showResearchModal:false, researchForm:{title:'',content:''},
    showReminderModal:false, reminderForm:{title:'',remind_at:''},
    showIdeaModal:false, editingIdea:null, ideaForm:{title:'',content:'',status:'brainstorm',tags:''},
    showEventModal:false, editingEvent:null, eventForm:{title:'',description:'',event_start:'',event_end:'',location:'',is_all_day:false},
    showJobModal:false, editingJob:null, jobForm:{title:'',description:'',job_type:'custom',cron_expression:'0 9 * * *'},
    tabs:[{key:'dashboard',label:'🏠'},{key:'ideas',label:'Ideas'},{key:'notes',label:'Notes'},{key:'schedule',label:'Schedule'},{key:'reminders',label:'Reminders'},{key:'projects',label:'Projects'},{key:'jobs',label:'Jobs'},{key:'activity',label:'Activity'}],
  }},
  computed:{
    counts(){
      return{
        ideas:this.ideas.filter(i=>i.status==='brainstorm').length,
        notes:this.notes.length,
        schedule:this.events.length,
        reminders:this.reminders.filter(r=>!r.done).length,
        projects:this.projects.filter(p=>p.status==='active').length,
        jobs:this.jobs.filter(j=>j.is_enabled).length,
        activity:this.activity.length
      }
    },
    noteCategories(){return[...new Set(this.notes.map(n=>n.category).filter(Boolean))]},
    filteredNotes(){
      let n=this.notes
      if(this.noteSearch) n=n.filter(x=>x.title.toLowerCase().includes(this.noteSearch.toLowerCase()))
      if(this.noteCategoryFilter) n=n.filter(x=>x.category===this.noteCategoryFilter)
      return n
    },
    upcomingEvents(){return this.events.slice(0,3)},
    recentIdeas(){return this.ideas.filter(i=>i.status==='brainstorm').slice(0,3)},
    failedJobs(){return this.jobs.filter(j=>j.last_result&&j.last_result.includes('fail'))}
  },
  methods:{
    statusLabel(s){return{active:'🟢 Active',paused:'🟡 Paused',done:'✅ Done',archived:'📦 Archived'}[s]||s},
    async api(method,url,body){
      try{
        const r=await fetch(url,{method,headers:{'Content-Type':'application/json','Authorization':'Bearer '+this.token},body:body?JSON.stringify(body):undefined})
        if(r.status===401){localStorage.removeItem('portal_token');window.location='/user/login';return null}
        return await r.json()
      }catch(e){return null}
    },
    async fetchData(){
      if(!this.token){window.location='/user/login';return}
      for(const ep of['notes','ideas','reminders','events','projects','jobs','activity']){
        const d=await this.api('GET','/api/me/'+ep)
        if(ep==='notes'&&d){this.notes=d.notes||[];this.user=d.user||this.user}
        if(ep==='ideas'&&d)this.ideas=d.ideas||[]
        if(ep==='reminders'&&d)this.reminders=d.reminders||[]
        if(ep==='events'&&d)this.events=d.events||[]
        if(ep==='projects'&&d)this.projects=d.projects||[]
        if(ep==='jobs'&&d)this.jobs=d.jobs||[]
        if(ep==='activity'&&d)this.activity=d.activity||[]
      }
    },
    logout(){localStorage.removeItem('portal_token');localStorage.removeItem('profile_id');window.location='/user/login'},

    // Notes
    openNoteModal(note){
      this.editingNote=note||null
      this.noteForm={title:note?.title||'',content:note?.content||'',category:note?.category||'General'}
      this.showNoteModal=true
    },
    async saveNote(){
      if(!this.noteForm.title)return
      if(this.editingNote){
        await this.api('PUT',`/api/me/notes/${this.editingNote.id}`,this.noteForm)
      }else{
        await this.api('POST','/api/me/notes',this.noteForm)
      }
      this.showNoteModal=false;this.editingNote=null;await this.fetchData()
    },
    async deleteNote(id){
      if(!confirm('Delete this note?'))return
      await this.api('DELETE',`/api/me/notes/${id}`)
      await this.fetchData()
    },

    // Projects
    openProjectModal(proj){
      this.editingProject=proj||null
      this.projectForm={title:proj?.title||'',description:proj?.description||''}
      this.showProjectModal=true
    },
    async saveProject(){
      if(!this.projectForm.title)return
      if(this.editingProject){
        await this.api('PUT',`/api/me/projects/${this.editingProject.id}`,this.projectForm)
      }else{
        await this.api('POST','/api/me/projects',this.projectForm)
      }
      this.showProjectModal=false;this.editingProject=null;await this.fetchData()
    },
    async selectProject(p){
      const d=await this.api('GET',`/api/me/projects/${p.id}`)
      if(d)this.selectedProject=d
    },
    async updateProjectStatus(p,status){
      await this.api('PUT',`/api/me/projects/${p.id}`,{status})
      p.status=status
    },
    async deleteProject(id){
      if(!confirm('Delete this project and all its research?'))return
      await this.api('DELETE',`/api/me/projects/${id}`)
      await this.fetchData();this.selectedProject=null
    },
    editProjectDetail(p){this.openProjectModal(p)},

    // Research
    openResearchModal(){this.researchForm={title:'',content:''};this.showResearchModal=true},
    async saveResearch(){
      if(!this.researchForm.title||!this.selectedProject)return
      await this.api('POST',`/api/me/projects/${this.selectedProject.id}/research`,this.researchForm)
      this.showResearchModal=false;this.selectedProject=await this.api('GET',`/api/me/projects/${this.selectedProject.id}`)
    },
    async deleteResearch(pid,rid){
      if(!confirm('Delete this research?'))return
      await this.api('DELETE',`/api/me/projects/${pid}/research/${rid}`)
      this.selectedProject=await this.api('GET',`/api/me/projects/${this.selectedProject.id}`)
    },

    // Reminders
    openReminderModal(){this.reminderForm={title:'',remind_at:''};this.showReminderModal=true},
    async saveReminder(){
      if(!this.reminderForm.title||!this.reminderForm.remind_at)return
      await this.api('POST','/api/me/reminders',this.reminderForm)
      this.showReminderModal=false;await this.fetchData()
    },
    async toggleReminder(r){
      await this.api('PUT',`/api/me/reminders/${r.id}`,{done:!r.done})
      r.done=!r.done
    },
    async deleteReminder(id){
      if(!confirm('Delete this reminder?'))return
      await this.api('DELETE',`/api/me/reminders/${id}`)
      await this.fetchData()
    },

    // Ideas
    statusBadge(s){return{brainstorm:'💭 Brainstorm',developing:'🔨 Developing',ready:'✅ Ready',archived:'📦 Archived'}[s]||s},
    openIdeaModal(idea){
      this.editingIdea=idea||null
      this.ideaForm={title:idea?.title||'',content:idea?.content||'',status:idea?.status||'brainstorm',tags:idea?.tags||''}
      this.showIdeaModal=true
    },
    async saveIdea(){
      if(!this.ideaForm.title)return
      if(this.editingIdea){
        await this.api('PUT',`/api/me/ideas/${this.editingIdea.id}`,this.ideaForm)
      }else{
        await this.api('POST','/api/me/ideas',this.ideaForm)
      }
      this.showIdeaModal=false;this.editingIdea=null;await this.fetchData()
    },
    async deleteIdea(id){
      if(!confirm('Delete this idea?'))return
      await this.api('DELETE',`/api/me/ideas/${id}`)
      await this.fetchData()
    },

    // Schedule/Events
    formatEventDate(dt){if(!dt)return'';const d=new Date(dt);return d.toLocaleDateString()+' '+d.toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'})},
    openEventModal(evt){
      this.editingEvent=evt||null
      this.eventForm={
        title:evt?.title||'',
        description:evt?.description||'',
        event_start:evt?.event_start||'',
        event_end:evt?.event_end||'',
        location:evt?.location||'',
        is_all_day:evt?.is_all_day||false
      }
      this.showEventModal=true
    },
    async saveEvent(){
      if(!this.eventForm.title||!this.eventForm.event_start||!this.eventForm.event_end)return
      if(this.editingEvent){
        await this.api('PUT',`/api/me/events/${this.editingEvent.id}`,this.eventForm)
      }else{
        await this.api('POST','/api/me/events',this.eventForm)
      }
      this.showEventModal=false;this.editingEvent=null;await this.fetchData()
    },
    async deleteEvent(id){
      if(!confirm('Delete this event?'))return
      await this.api('DELETE',`/api/me/events/${id}`)
      await this.fetchData()
    },

    // Background Jobs
    formatJobDate(dt){if(!dt)return'N/A';const d=new Date(dt);return d.toLocaleDateString()+' '+d.toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'})},
    openJobModal(job){
      this.editingJob=job||null
      this.jobForm={
        title:job?.title||'',
        description:job?.description||'',
        job_type:job?.job_type||'custom',
        cron_expression:job?.cron_expression||'0 9 * * *'
      }
      this.showJobModal=true
    },
    async saveJob(){
      if(!this.jobForm.title)return
      if(this.editingJob){
        await this.api('PUT',`/api/me/jobs/${this.editingJob.id}`,this.jobForm)
      }else{
        await this.api('POST','/api/me/jobs',this.jobForm)
      }
      this.showJobModal=false;this.editingJob=null;await this.fetchData()
    },
    async toggleJob(job){
      await this.api('PUT',`/api/me/jobs/${job.id}`,{is_enabled:!job.is_enabled})
      job.is_enabled=!job.is_enabled
    },
    async deleteJob(id){
      if(!confirm('Delete this background job?'))return
      await this.api('DELETE',`/api/me/jobs/${id}`)
      await this.fetchData()
    },
  },
  mounted(){this.fetchData()}
}
</script>

<style scoped>
*{box-sizing:border-box}
.portal{min-height:100vh;background:#f5f5f7;font-family:-apple-system,BlinkMacSystemFont,sans-serif;color:#333}
header{background:#fff;border-bottom:1px solid #e5e5ea;position:sticky;top:0;z-index:10}
.header-content{max-width:960px;margin:0 auto;padding:12px 20px;display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.header-content h1{font-size:18px;margin:0;flex:1;min-width:120px}
nav{display:flex;gap:4px;flex-wrap:wrap}
nav button{padding:6px 14px;border:1px solid transparent;border-radius:6px;background:transparent;cursor:pointer;font-size:14px;position:relative;white-space:nowrap}
nav button.active{background:#6C5CE7;color:#fff}
nav button .badge{position:absolute;top:-4px;right:-4px;background:#ff4757;color:#fff;font-size:10px;padding:1px 5px;border-radius:8px}
.btn-outline{padding:6px 14px;border:1px solid #ddd;border-radius:6px;background:#fff;cursor:pointer;font-size:14px}
.btn-primary{background:#6C5CE7;color:#fff;border:none;border-radius:6px;padding:8px 16px;cursor:pointer;font-size:14px}
.btn-sm{padding:4px 10px;font-size:12px;border-radius:4px;border:1px solid #ddd;background:#fff;cursor:pointer}
.btn-danger{color:#e74c3c;border-color:#e74c3c}

main{max-width:960px;margin:0 auto;padding:20px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin-bottom:20px}
.grid .card{background:#fff;padding:20px;border-radius:12px;cursor:pointer;transition:transform .15s}
.grid .card:hover{transform:translateY(-2px);box-shadow:0 4px 12px rgba(0,0,0,.08)}
.grid .card h3{margin:0 0 8px;font-size:18px}
.grid .card .count{font-size:32px;font-weight:700;margin:0;color:#6C5CE7}
.quick-tips{background:#eef1ff;padding:12px 16px;border-radius:10px;font-size:14px}
.quick-tips p{margin:0}

.section-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px}
.section-header h2{margin:0;font-size:20px}
.filter-bar{display:flex;gap:8px;margin-bottom:12px}
.search{flex:1;padding:10px 14px;border:1px solid #ddd;border-radius:10px;font-size:14px}
.filter-bar select{padding:10px;border:1px solid #ddd;border-radius:10px;font-size:14px;background:#fff}

.list-item{background:#fff;padding:12px 16px;border-radius:10px;margin:6px 0;cursor:pointer;transition:box-shadow .1s}
.list-item:hover{box-shadow:0 2px 8px rgba(0,0,0,.04)}
.list-item.done{opacity:.5}
.list-item.expanded{box-shadow:0 2px 12px rgba(108,92,231,.12)}
.item-top{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.badge-cat{font-size:11px;padding:2px 8px;border-radius:10px;background:#eef1ff;color:#6C5CE7}
.item-title{font-weight:500;flex:1}
.strikethrough{text-decoration:line-through}
.item-meta{font-size:12px;color:#888}
.item-body{margin-top:10px;border-top:1px solid #eee;padding-top:10px}
.item-body p{white-space:pre-wrap;font-size:14px;color:#555;margin:0 0 8px}
.item-actions{display:flex;gap:6px}
.empty{color:#888;text-align:center;padding:40px 0}

.checkbox{display:flex;align-items:center;cursor:pointer;padding-top:2px}
.checkbox input{display:none}
.checkbox span{width:18px;height:18px;border:2px solid #ddd;border-radius:4px;display:inline-block;flex-shrink:0}
.checkbox input:checked+span{background:#6C5CE7;border-color:#6C5CE7}
.checkbox input:checked+span:after{content:'✓';color:#fff;position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:12px}

.project-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:12px}
.project-card{padding:16px;cursor:pointer;margin:0}
.project-card p{margin:6px 0;font-size:13px;color:#555}
.project-top{display:flex;justify-content:space-between;align-items:center;margin-bottom:4px}
.badge{font-size:11px;padding:2px 8px;border-radius:10px;white-space:nowrap}
.badge-active{background:#d4edda;color:#155724}
.badge-paused{background:#fff3cd;color:#856404}
.badge-done{background:#cce5ff;color:#004085}
.badge-archived{background:#e2e3e5;color:#383d41}

.project-detail-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}
.project-detail-header h2{margin:0;font-size:20px}
.status-select{padding:6px;border:1px solid #ddd;border-radius:6px;font-size:13px;background:#fff}

.timeline-dot{width:8px;height:8px;background:#6C5CE7;border-radius:50%;margin-top:6px;flex-shrink:0}

/* Modal */
.modal-overlay{position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.3);display:flex;align-items:center;justify-content:center;z-index:100}
.modal{background:#fff;border-radius:12px;padding:24px;width:90%;max-width:480px;max-height:80vh;overflow-y:auto}
.modal h2{margin:0 0 16px}
.modal input,.modal textarea{width:100%;padding:10px;margin:8px 0;border:1px solid #ddd;border-radius:8px;font-size:14px;font-family:inherit;box-sizing:border-box}
.modal textarea{resize:vertical}
.modal-row{display:flex;gap:8px;margin-top:12px;justify-content:flex-end}

/* Ideas */
.idea-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px}
.idea-card{background:#fff;border-radius:10px;padding:16px;cursor:pointer;transition:box-shadow .15s}
.idea-card:hover{box-shadow:0 2px 12px rgba(0,0,0,.08)}
.idea-header{display:flex;justify-content:space-between;align-items:start;margin-bottom:8px}
.idea-header strong{font-size:15px;flex:1}
.badge-status{font-size:11px;padding:3px 8px;border-radius:10px;white-space:nowrap;flex-shrink:0}
.badge-brainstorm{background:#e3f2fd;color:#1976d2}
.badge-developing{background:#f3e5f5;color:#7b1fa2}
.badge-ready{background:#e8f5e9;color:#388e3c}
.badge-archived{background:#e0e0e0;color:#616161}
.idea-content{font-size:13px;color:#666;margin:8px 0;line-height:1.4;min-height:40px}
.idea-footer{display:flex;justify-content:space-between;align-items:center;margin-top:12px;padding-top:8px;border-top:1px solid #f0f0f0}
.idea-tags{font-size:11px;color:#999;font-style:italic}

/* Events */
.event-item{display:flex;align-items:center;gap:12px}
.event-date{font-size:12px;font-weight:600;color:#6C5CE7;white-space:nowrap}

/* Jobs */
.jobs-table{background:#fff;border-radius:10px;overflow:hidden}
.job-row{display:flex;align-items:center;gap:12px;padding:12px 16px;border-bottom:1px solid #f0f0f0}
.job-row:last-child{border-bottom:none}
.job-header{background:#f8f9fa;font-weight:600;font-size:13px;color:#666}
.toggle{position:relative;display:inline-block;width:40px;height:20px;cursor:pointer}
.toggle input{display:none}
.toggle-slider{position:absolute;top:0;left:0;right:0;bottom:0;background:#ccc;border-radius:20px;transition:.3s}
.toggle-slider:before{content:'';position:absolute;height:14px;width:14px;left:3px;bottom:3px;background:#fff;border-radius:50%;transition:.3s}
.toggle input:checked+.toggle-slider{background:#6C5CE7}
.toggle input:checked+.toggle-slider:before{transform:translateX(20px)}

/* Dashboard Widgets */
.widget-list{background:#fff;border-radius:10px;overflow:hidden}
.widget-item{padding:12px 16px;border-bottom:1px solid #f5f5f7;display:flex;align-items:center;gap:12px;cursor:pointer;transition:background .15s}
.widget-item:hover{background:#f8f9fa}
.widget-item:last-child{border-bottom:none}
.empty-widget{color:#999;font-size:14px;text-align:center;padding:20px;background:#fff;border-radius:10px}
.warning-box{background:#fff3cd;color:#856404;padding:12px 16px;border-radius:10px;margin-top:16px;border-left:4px solid #ffc107}
</style>