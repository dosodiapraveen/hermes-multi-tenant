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
          <div class="card" @click="tab='notes'"><h3>📝 Notes</h3><p class="count">{{ notes.length }}</p></div>
          <div class="card" @click="tab='reminders'"><h3>⏰ Reminders</h3><p class="count">{{ reminders.filter(r=>!r.done).length }}</p></div>
          <div class="card" @click="tab='projects'"><h3>📋 Projects</h3><p class="count">{{ projects.length }}</p></div>
          <div class="card" @click="tab='activity'"><h3>📊 Activity</h3><p class="count">{{ activity.length }}</p></div>
        </div>
        <div class="quick-tips">
          <p>💡 Tell your agent: <em>"Save a note about Q4 planning"</em> or <em>"Create project Product Launch"</em></p>
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

      <!-- ─────── REMINDERS ─────── -->
      <section v-if="tab==='reminders'">
        <div class="section-header"><h2>⏰ Reminders</h2></div>
        <div v-for="r in reminders" :key="r.id" class="list-item" :class="{done:r.done}">
          <label class="checkbox"><input type="checkbox" :checked="r.done" @change="r.done=!r.done" /><span></span></label>
          <div><div class="item-title" :class="r.done?'strikethrough':''">{{ r.title }}</div><div class="item-meta" v-if="r.remind_at">{{ r.remind_at.slice(0,10) }}</div></div>
        </div>
        <p v-if="!reminders.length" class="empty">No reminders. Tell your agent: "Remind me..."</p>
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
  </div>
</template>

<script>
export default {
  data(){return{
    token: localStorage.getItem('portal_token')||'', tab:'dashboard',
    user:'My Dashboard', notes:[], reminders:[], projects:[], activity:[],
    noteSearch:'', noteCategoryFilter:'', expandedNote:null, selectedProject:null,
    showNoteModal:false, editingNote:null, noteForm:{title:'',content:'',category:'General'},
    showProjectModal:false, editingProject:null, projectForm:{title:'',description:''},
    showResearchModal:false, researchForm:{title:'',content:''},
    tabs:[{key:'dashboard',label:'🏠'},{key:'notes',label:'Notes'},{key:'reminders',label:'Reminders'},{key:'projects',label:'Projects'},{key:'activity',label:'Activity'}],
  }},
  computed:{
    counts(){return{notes:this.notes.length,reminders:this.reminders.filter(r=>!r.done).length,projects:this.projects.length,activity:this.activity.length}},
    noteCategories(){return[...new Set(this.notes.map(n=>n.category).filter(Boolean))]},
    filteredNotes(){
      let n=this.notes
      if(this.noteSearch) n=n.filter(x=>x.title.toLowerCase().includes(this.noteSearch.toLowerCase()))
      if(this.noteCategoryFilter) n=n.filter(x=>x.category===this.noteCategoryFilter)
      return n
    }
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
      for(const ep of['notes','reminders','projects','activity']){
        const d=await this.api('GET','/api/me/'+ep)
        if(ep==='notes'&&d){this.notes=d.notes||[];this.user=d.user||this.user}
        if(ep==='reminders'&&d)this.reminders=d.reminders||[]
        if(ep==='projects'&&d)this.projects=d.projects||[]
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
</style>