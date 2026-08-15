<template>
  <div class="portal">
    <!-- Header -->
    <header class="portal-header">
      <div class="header-content">
        <h1>
          <BaseIcon name="home" :size="20" />
          {{ user }}
        </h1>
        <nav class="nav-tabs">
          <button
            v-for="t in tabs"
            :key="t.key"
            :class="['nav-tab', { active: tab === t.key }]"
            @click="tab = t.key"
          >
            <BaseIcon :name="t.icon" :size="16" />
            <span class="tab-label">{{ t.label }}</span>
            <BaseBadge
              v-if="tabBadge(t.key)"
              :label="tabBadge(t.key)"
              variant="error"
              size="sm"
              pill
            />
          </button>
        </nav>
        <BaseButton variant="outline" icon="log-out" @click="logout">
          Logout
        </BaseButton>
      </div>
    </header>

    <main class="portal-main">
      <!-- Loading State -->
      <div v-if="loading" class="loading-container">
        <div class="skeleton-grid">
          <div v-for="i in 4" :key="i" class="skeleton-card"></div>
        </div>
        <div class="skeleton-list">
          <div v-for="i in 3" :key="i" class="skeleton-item"></div>
        </div>
        <p class="loading-text">
          <BaseIcon name="loader" :size="16" spin />
          Loading your dashboard...
        </p>
      </div>

      <!-- Welcome Banner -->
      <Transition name="fade">
        <div v-if="showWelcome && !loading" class="welcome-banner">
          <button class="welcome-close" @click="dismissWelcome">
            <BaseIcon name="x" :size="18" />
          </button>
          <div class="welcome-content">
            <h2>Welcome to your Personal Dashboard!</h2>
            <p>This is your AI-powered workspace. Here's how to get started:</p>
            <div class="welcome-tips">
              <div class="tip">
                <BaseIcon name="lightbulb" :size="20" />
                <span>Capture <strong>Ideas</strong> as they come to you</span>
              </div>
              <div class="tip">
                <BaseIcon name="file-text" :size="20" />
                <span>Take <strong>Notes</strong> that sync with your AI assistant</span>
              </div>
              <div class="tip">
                <BaseIcon name="calendar" :size="20" />
                <span>Schedule <strong>Events</strong> and never miss a date</span>
              </div>
              <div class="tip">
                <BaseIcon name="folder" :size="20" />
                <span>Organize work with <strong>Projects</strong></span>
              </div>
            </div>
            <BaseButton variant="secondary" @click="dismissWelcome">
              Get Started
            </BaseButton>
          </div>
        </div>
      </Transition>

      <!-- Dashboard -->
      <PortalDashboard
        v-if="tab === 'dashboard' && !loading"
        :ideas="ideas"
        :notes="notes"
        :reminders="reminders"
        :projects="projects"
        :events="events"
        :jobs="jobs"
        @change-tab="tab = $event"
        @goto-result="gotoResult"
      />

      <!-- Notes -->
      <PortalNotes
        v-if="tab === 'notes' && !loading"
        :notes="notes"
        :search="noteSearch"
        :category="noteCategoryFilter"
        @open-modal="openNoteModal"
        @delete="deleteNote"
        @update:search="noteSearch = $event"
        @update:category="noteCategoryFilter = $event"
      />

      <!-- Ideas -->
      <PortalIdeas
        v-if="tab === 'ideas' && !loading"
        :ideas="ideas"
        @open-modal="openIdeaModal"
        @delete="deleteIdea"
      />

      <!-- Schedule -->
      <PortalSchedule
        v-if="tab === 'schedule' && !loading"
        :events="events"
        @open-modal="openEventModal"
        @delete="deleteEvent"
      />

      <!-- Reminders -->
      <PortalReminders
        v-if="tab === 'reminders' && !loading"
        :reminders="reminders"
        @open-modal="openReminderModal"
        @delete="deleteReminder"
        @toggle="toggleReminder"
      />

      <!-- Projects -->
      <PortalProjects
        v-if="tab === 'projects' && !loading"
        :projects="projects"
        :selected-project="selectedProject"
        @open-modal="openProjectModal"
        @open-research="openResearchModal"
        @select="selectProject"
        @deselect="selectedProject = null"
        @delete="deleteProject"
        @delete-research="deleteResearch"
        @update-status="updateProjectStatus"
      />

      <!-- Jobs -->
      <PortalJobs
        v-if="tab === 'jobs' && !loading"
        :jobs="jobs"
        @open-modal="openJobModal"
        @delete="deleteJob"
        @toggle="toggleJob"
      />

      <!-- Activity -->
      <PortalActivity
        v-if="tab === 'activity' && !loading"
        :activity="activity"
      />

      <!-- Personality -->
      <PortalPersonality
        v-if="tab === 'personality' && !loading"
        :personality="personality"
        :agent-name="personaAgentName"
        @save="personality = $event"
      />
    </main>

    <!-- Toast Notifications -->
    <BaseToast ref="toast" position="bottom-right" />

    <!-- Note Modal -->
    <BaseModal v-model="showNoteModal" :title="editingNote ? 'Edit Note' : 'New Note'">
      <div class="modal-form">
        <BaseInput v-model="noteForm.title" label="Title" placeholder="Note title" required />
        <BaseInput
          v-model="noteForm.content"
          type="textarea"
          label="Content"
          placeholder="Write your note..."
          :rows="5"
        />
        <BaseInput
          v-model="noteForm.category"
          label="Category"
          placeholder="e.g. Work, Personal, Ideas"
        />
      </div>
      <template #footer>
        <BaseButton variant="outline" @click="showNoteModal = false">Cancel</BaseButton>
        <BaseButton @click="saveNote">Save</BaseButton>
      </template>
    </BaseModal>

    <!-- Idea Modal -->
    <BaseModal v-model="showIdeaModal" :title="editingIdea ? 'Edit Idea' : 'New Idea'">
      <div class="modal-form">
        <BaseInput v-model="ideaForm.title" label="Title" placeholder="Idea title" required />
        <BaseInput
          v-model="ideaForm.content"
          type="textarea"
          label="Details"
          placeholder="Describe your idea..."
          :rows="5"
        />
        <BaseSelect
          v-model="ideaForm.status"
          label="Status"
          :options="ideaStatusOptions"
        />
        <BaseInput
          v-model="ideaForm.tags"
          label="Tags"
          placeholder="Comma separated tags"
        />
      </div>
      <template #footer>
        <BaseButton variant="outline" @click="showIdeaModal = false">Cancel</BaseButton>
        <BaseButton @click="saveIdea">Save</BaseButton>
      </template>
    </BaseModal>

    <!-- Event Modal -->
    <BaseModal v-model="showEventModal" :title="editingEvent ? 'Edit Event' : 'New Event'" size="lg">
      <div class="modal-form">
        <BaseInput v-model="eventForm.title" label="Title" placeholder="Event title" required />
        <BaseInput
          v-model="eventForm.description"
          type="textarea"
          label="Description"
          placeholder="Event description..."
          :rows="2"
        />
        <BaseDateTimePicker
          v-model="eventForm.datetime"
          label="Date & Time"
          :show-all-day="true"
          :all-day="eventForm.is_all_day"
          @update:all-day="eventForm.is_all_day = $event"
        />
        <BaseInput
          v-model="eventForm.location"
          label="Location"
          placeholder="Optional location"
          prefix-icon="map-pin"
        />
      </div>
      <template #footer>
        <BaseButton variant="outline" @click="showEventModal = false">Cancel</BaseButton>
        <BaseButton @click="saveEvent">Save</BaseButton>
      </template>
    </BaseModal>

    <!-- Reminder Modal -->
    <BaseModal v-model="showReminderModal" title="New Reminder">
      <div class="modal-form">
        <BaseInput
          v-model="reminderForm.title"
          label="What do you want to be reminded about?"
          placeholder="Enter reminder..."
          required
        />
        <BaseDateTimePicker
          v-model="reminderForm.remind_at"
          label="Remind me at"
        />
      </div>
      <template #footer>
        <BaseButton variant="outline" @click="showReminderModal = false">Cancel</BaseButton>
        <BaseButton @click="saveReminder">Save</BaseButton>
      </template>
    </BaseModal>

    <!-- Project Modal -->
    <BaseModal v-model="showProjectModal" :title="editingProject ? 'Edit Project' : 'New Project'">
      <div class="modal-form">
        <BaseInput v-model="projectForm.title" label="Title" placeholder="Project title" required />
        <BaseInput
          v-model="projectForm.description"
          type="textarea"
          label="Description"
          placeholder="Describe your project..."
          :rows="3"
        />
      </div>
      <template #footer>
        <BaseButton variant="outline" @click="showProjectModal = false">Cancel</BaseButton>
        <BaseButton @click="saveProject">Save</BaseButton>
      </template>
    </BaseModal>

    <!-- Research Modal -->
    <BaseModal v-model="showResearchModal" title="Add Research">
      <div class="modal-form">
        <BaseInput v-model="researchForm.title" label="Title" placeholder="Research title" required />
        <BaseInput
          v-model="researchForm.content"
          type="textarea"
          label="Content"
          placeholder="Research findings..."
          :rows="4"
        />
      </div>
      <template #footer>
        <BaseButton variant="outline" @click="showResearchModal = false">Cancel</BaseButton>
        <BaseButton @click="saveResearch">Save</BaseButton>
      </template>
    </BaseModal>

    <!-- Job Modal -->
    <BaseModal v-model="showJobModal" :title="editingJob ? 'Edit Job' : 'New Job'">
      <div class="modal-form">
        <BaseInput v-model="jobForm.title" label="Title" placeholder="Job title" required />
        <BaseInput
          v-model="jobForm.description"
          type="textarea"
          label="Description"
          placeholder="Job description..."
          :rows="2"
        />
        <BaseSelect v-model="jobForm.job_type" label="Type" :options="jobTypeOptions" />
        <BaseSelect v-model="jobForm.cron_expression" label="Schedule" :options="cronOptions" />
      </div>
      <template #footer>
        <BaseButton variant="outline" @click="showJobModal = false">Cancel</BaseButton>
        <BaseButton @click="saveJob">Save</BaseButton>
      </template>
    </BaseModal>

    <!-- Confirm delete -->
    <BaseModal v-model="showConfirm" title="Confirm">
      <p style="margin:0 0 20px;line-height:1.6;color:#333;font-size:14px">{{ confirmMessage }}</p>
      <div style="display:flex;justify-content:flex-end;gap:10px">
        <BaseButton variant="outline" @click="showConfirm = false">Cancel</BaseButton>
        <BaseButton variant="danger" @click="confirmAction">Delete</BaseButton>
      </div>
    </BaseModal>
  </div>
</template>

<script>
import { BaseIcon, BaseButton, BaseBadge, BaseModal, BaseInput, BaseSelect, BaseToast, BaseDateTimePicker } from '../components/ui'
import {
  PortalDashboard,
  PortalNotes,
  PortalIdeas,
  PortalSchedule,
  PortalReminders,
  PortalProjects,
  PortalJobs,
  PortalActivity,
  PortalPersonality
} from '../components/portal'

export default {
  name: 'UserPortal',
  components: {
    BaseIcon,
    BaseButton,
    BaseBadge,
    BaseModal,
    BaseInput,
    BaseSelect,
    BaseToast,
    BaseDateTimePicker,
    PortalDashboard,
    PortalNotes,
    PortalIdeas,
    PortalSchedule,
    PortalReminders,
    PortalProjects,
    PortalJobs,
    PortalActivity,
    PortalPersonality
  },
  data() {
    return {
      token: localStorage.getItem('portal_token') || '',
      tab: 'dashboard',
      user: 'My Dashboard',
      loading: true,
      showWelcome: false,

      // Data
      notes: [],
      ideas: [],
      reminders: [],
      events: [],
      projects: [],
      jobs: [],
      activity: [],
      personality: '',
      personaAgentName: 'Agent',

      // Filters
      noteSearch: '',
      noteCategoryFilter: '',
      selectedProject: null,

      // Modals
      showNoteModal: false,
      showIdeaModal: false,
      showEventModal: false,
      showReminderModal: false,
      showProjectModal: false,
      showResearchModal: false,
      showJobModal: false,

      // Editing states
      editingNote: null,
      editingIdea: null,
      editingEvent: null,
      editingProject: null,
      editingJob: null,
      showConfirm: false, confirmMessage: '', confirmFn: null,

      // Forms
      noteForm: { title: '', content: '', category: 'General' },
      ideaForm: { title: '', content: '', status: 'brainstorm', tags: '' },
      eventForm: { title: '', description: '', datetime: '', location: '', is_all_day: false },
      reminderForm: { title: '', remind_at: '' },
      projectForm: { title: '', description: '' },
      researchForm: { title: '', content: '' },
      jobForm: { title: '', description: '', job_type: 'custom', cron_expression: '0 9 * * *' },

      // Options
      tabs: [
        { key: 'dashboard', label: 'Home', icon: 'home' },
        { key: 'ideas', label: 'Ideas', icon: 'lightbulb' },
        { key: 'notes', label: 'Notes', icon: 'file-text' },
        { key: 'schedule', label: 'Schedule', icon: 'calendar' },
        { key: 'reminders', label: 'Reminders', icon: 'clock' },
        { key: 'projects', label: 'Projects', icon: 'folder' },
        { key: 'jobs', label: 'Jobs', icon: 'settings' },
        { key: 'activity', label: 'Activity', icon: 'activity' },
        { key: 'personality', label: 'Personality', icon: 'brain' }
      ],
      ideaStatusOptions: [
        { value: 'brainstorm', label: 'Brainstorm', icon: 'lightbulb' },
        { value: 'developing', label: 'Developing', icon: 'settings' },
        { value: 'ready', label: 'Ready', icon: 'check' },
        { value: 'archived', label: 'Archived', icon: 'folder' }
      ],
      jobTypeOptions: [
        { value: 'email', label: 'Email', icon: 'mail' },
        { value: 'webhook', label: 'Webhook', icon: 'external-link' },
        { value: 'cleanup', label: 'Cleanup', icon: 'trash' },
        { value: 'report', label: 'Report', icon: 'activity' },
        { value: 'custom', label: 'Custom', icon: 'settings' }
      ],
      cronOptions: [
        { value: '0 9 * * *', label: 'Daily at 9:00 AM' },
        { value: '0 0 * * 1', label: 'Weekly (Monday midnight)' },
        { value: '0 0 1 * *', label: 'Monthly (1st day)' },
        { value: '*/30 * * * *', label: 'Every 30 minutes' },
        { value: '0 */6 * * *', label: 'Every 6 hours' }
      ]
    }
  },
  watch: {
    tab(v) {
      if (v === 'personality') this.loadPersonality()
    }
  },
  mounted() {
    this.fetchData()
    document.addEventListener('keydown', this.handleKeydown)
  },
  beforeUnmount() {
    document.removeEventListener('keydown', this.handleKeydown)
  },
  methods: {
    showToast(message, type = 'success') {
      this.$refs.toast?.[type]?.(message) || this.$refs.toast?.add?.({ message, type })
    },

    handleKeydown(e) {
      if (e.key === 'Escape') {
        if (this.showNoteModal) this.showNoteModal = false
        else if (this.showProjectModal) this.showProjectModal = false
        else if (this.showResearchModal) this.showResearchModal = false
        else if (this.showReminderModal) this.showReminderModal = false
        else if (this.showIdeaModal) this.showIdeaModal = false
        else if (this.showEventModal) this.showEventModal = false
        else if (this.showJobModal) this.showJobModal = false
        else if (this.showWelcome) this.dismissWelcome()
      }
    },

    tabBadge(key) {
      if (key === 'reminders') return this.reminders.filter(r => !r.done).length || null
      if (key === 'jobs') return this.jobs.filter(j => j.last_result?.includes('fail')).length || null
      if (key === 'ideas') return this.ideas.filter(i => i.status === 'brainstorm').length || null
      return null
    },

    async api(method, url, body) {
      try {
        const r = await fetch(url, {
          method,
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + this.token
          },
          body: body ? JSON.stringify(body) : undefined
        })
        if (r.status === 401) {
          localStorage.removeItem('portal_token')
          window.location = '/user/login'
          return null
        }
        return await r.json()
      } catch (e) {
        return null
      }
    },

    async fetchData() {
      if (!this.token) {
        window.location = '/user/login'
        return
      }
      this.loading = true
      try {
        const endpoints = ['notes', 'ideas', 'reminders', 'events', 'projects', 'jobs', 'activity']
        for (const ep of endpoints) {
          const d = await this.api('GET', '/api/me/' + ep)
          if (ep === 'notes' && d) {
            this.notes = d.notes || []
            this.user = d.user || this.user
          }
          if (ep === 'ideas' && d) this.ideas = d.ideas || []
          if (ep === 'reminders' && d) this.reminders = d.reminders || []
          if (ep === 'events' && d) this.events = d.events || []
          if (ep === 'projects' && d) this.projects = d.projects || []
          if (ep === 'jobs' && d) this.jobs = d.jobs || []
          if (ep === 'activity' && d) this.activity = d.activity || []
        }

        const isFirstVisit = !localStorage.getItem('portal_welcomed')
        const hasNoData = this.notes.length === 0 && this.ideas.length === 0 && this.projects.length === 0
        if (isFirstVisit && hasNoData) this.showWelcome = true
      } finally {
        this.loading = false
      }
    },

    dismissWelcome() {
      this.showWelcome = false
      localStorage.setItem('portal_welcomed', '1')
    },

    logout() {
      localStorage.removeItem('portal_token')
      localStorage.removeItem('profile_id')
      window.location = '/user/login'
    },

    gotoResult(r) {
      const map = { note: 'notes', project: 'projects', research: 'projects', idea: 'ideas', reminder: 'reminders' }
      this.tab = map[r.type] || 'dashboard'
    },

    async loadPersonality() {
      try {
        const r = await this.api('GET', '/api/me/personality')
        this.personality = r?.personality || ''
        this.personaAgentName = r?.agent_name || 'Agent'
      } catch (e) {}
    },

    // Notes
    openNoteModal(note) {
      this.editingNote = note || null
      this.noteForm = {
        title: note?.title || '',
        content: note?.content || '',
        category: note?.category || 'General'
      }
      this.showNoteModal = true
    },

    async saveNote() {
      if (!this.noteForm.title) return
      if (this.editingNote) {
        await this.api('PUT', `/api/me/notes/${this.editingNote.id}`, this.noteForm)
        this.showToast('Note updated successfully')
      } else {
        await this.api('POST', '/api/me/notes', this.noteForm)
        this.showToast('Note created successfully')
      }
      this.showNoteModal = false
      this.editingNote = null
      await this.fetchData()
    },

    deleteNote(id) {
      this.askConfirm('Delete this note?', async () => {
      await this.api('DELETE', `/api/me/notes/${id}`)
      this.showToast('Note deleted')
      await this.fetchData()
      }
    },

    // Ideas
    openIdeaModal(idea) {
      this.editingIdea = idea || null
      this.ideaForm = {
        title: idea?.title || '',
        content: idea?.content || '',
        status: idea?.status || 'brainstorm',
        tags: idea?.tags || ''
      }
      this.showIdeaModal = true
    },

    async saveIdea() {
      if (!this.ideaForm.title) return
      if (this.editingIdea) {
        await this.api('PUT', `/api/me/ideas/${this.editingIdea.id}`, this.ideaForm)
        this.showToast('Idea updated successfully')
      } else {
        await this.api('POST', '/api/me/ideas', this.ideaForm)
        this.showToast('Idea created successfully')
      }
      this.showIdeaModal = false
      this.editingIdea = null
      await this.fetchData()
    },

    deleteIdea(id) {
      this.askConfirm('Delete this idea?', async () => {
      await this.api('DELETE', `/api/me/ideas/${id}`)
      this.showToast('Idea deleted')
      await this.fetchData()
      }
    },

    // Events
    openEventModal(evt) {
      this.editingEvent = evt || null
      this.eventForm = {
        title: evt?.title || '',
        description: evt?.description || '',
        datetime: evt?.event_start || '',
        location: evt?.location || '',
        is_all_day: evt?.is_all_day || false
      }
      if (!evt) {
        const now = new Date()
        const min = now.getHours() * 60 + now.getMinutes()
        const nextSlot = Math.ceil(min / 15) * 15
        const h = Math.floor(nextSlot / 60)
        const m = nextSlot % 60
        const today = now.toISOString().slice(0, 10)
        this.eventForm.datetime = `${today}T${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:00`
      }
      this.showEventModal = true
    },

    async saveEvent() {
      if (!this.eventForm.title || !this.eventForm.datetime) return

      const payload = {
        title: this.eventForm.title,
        description: this.eventForm.description,
        location: this.eventForm.location,
        is_all_day: this.eventForm.is_all_day,
        event_start: this.eventForm.datetime,
        event_end: this.eventForm.is_all_day
          ? this.eventForm.datetime.slice(0, 10) + 'T23:59:00'
          : this.addHour(this.eventForm.datetime)
      }

      if (this.editingEvent) {
        await this.api('PUT', `/api/me/events/${this.editingEvent.id}`, payload)
        this.showToast('Event updated successfully')
      } else {
        await this.api('POST', '/api/me/events', payload)
        this.showToast('Event created successfully')
      }
      this.showEventModal = false
      this.editingEvent = null
      await this.fetchData()
    },

    addHour(datetime) {
      const d = new Date(datetime)
      d.setHours(d.getHours() + 1)
      return d.toISOString().slice(0, 19)
    },

    deleteEvent(id) {
      this.askConfirm('Delete this event?', async () => {
      await this.api('DELETE', `/api/me/events/${id}`)
      this.showToast('Event deleted')
      await this.fetchData()
      }
    },

    // Reminders
    openReminderModal() {
      this.reminderForm = { title: '', remind_at: '' }
      this.showReminderModal = true
    },

    async saveReminder() {
      if (!this.reminderForm.title || !this.reminderForm.remind_at) return
      await this.api('POST', '/api/me/reminders', this.reminderForm)
      this.showToast('Reminder created successfully')
      this.showReminderModal = false
      await this.fetchData()
    },

    async toggleReminder(r) {
      await this.api('PUT', `/api/me/reminders/${r.id}`, { done: !r.done })
      r.done = !r.done
    },

    deleteReminder(id) {
      this.askConfirm('Delete this reminder?', async () => {
      await this.api('DELETE', `/api/me/reminders/${id}`)
      this.showToast('Reminder deleted')
      await this.fetchData()
      }
    },

    // Projects
    openProjectModal(proj) {
      this.editingProject = proj || null
      this.projectForm = {
        title: proj?.title || '',
        description: proj?.description || ''
      }
      this.showProjectModal = true
    },

    async saveProject() {
      if (!this.projectForm.title) return
      if (this.editingProject) {
        await this.api('PUT', `/api/me/projects/${this.editingProject.id}`, this.projectForm)
        this.showToast('Project updated successfully')
      } else {
        await this.api('POST', '/api/me/projects', this.projectForm)
        this.showToast('Project created successfully')
      }
      this.showProjectModal = false
      this.editingProject = null
      await this.fetchData()
    },

    async selectProject(p) {
      const d = await this.api('GET', `/api/me/projects/${p.id}`)
      if (d) this.selectedProject = d
    },

    async updateProjectStatus(p, status) {
      await this.api('PUT', `/api/me/projects/${p.id}`, { status })
      p.status = status
    },

    deleteProject(id) {
      this.askConfirm('Delete this project and all its research?', async () => {
      await this.api('DELETE', `/api/me/projects/${id}`)
      this.showToast('Project deleted')
      await this.fetchData()
      this.selectedProject = null
      }
    },

    // Research
    openResearchModal() {
      this.researchForm = { title: '', content: '' }
      this.showResearchModal = true
    },

    async saveResearch() {
      if (!this.researchForm.title || !this.selectedProject) return
      await this.api('POST', `/api/me/projects/${this.selectedProject.id}/research`, this.researchForm)
      this.showToast('Research added successfully')
      this.showResearchModal = false
      this.selectedProject = await this.api('GET', `/api/me/projects/${this.selectedProject.id}`)
    },

    deleteResearch(pid, rid) {
      this.askConfirm('Delete this research?', async () => {
      await this.api('DELETE', `/api/me/projects/${pid}/research/${rid}`)
      this.showToast('Research deleted')
      this.selectedProject = await this.api('GET', `/api/me/projects/${this.selectedProject.id}`)
      }
    },

    // Jobs
    openJobModal(job) {
      this.editingJob = job || null
      this.jobForm = {
        title: job?.title || '',
        description: job?.description || '',
        job_type: job?.job_type || 'custom',
        cron_expression: job?.cron_expression || '0 9 * * *'
      }
      this.showJobModal = true
    },

    async saveJob() {
      if (!this.jobForm.title) return
      if (this.editingJob) {
        await this.api('PUT', `/api/me/jobs/${this.editingJob.id}`, this.jobForm)
        this.showToast('Job updated successfully')
      } else {
        await this.api('POST', '/api/me/jobs', this.jobForm)
        this.showToast('Job created successfully')
      }
      this.showJobModal = false
      this.editingJob = null
      await this.fetchData()
    },

    async toggleJob(job) {
      await this.api('PUT', `/api/me/jobs/${job.id}`, { is_enabled: !job.is_enabled })
      job.is_enabled = !job.is_enabled
    },

    deleteJob(id) {
      this.askConfirm('Delete this background job?', async () => {
        await this.api('DELETE', `/api/me/jobs/${id}`)
        this.showToast('Job deleted')
        await this.fetchData()
      })
    },

    askConfirm(message, fn) {
      this.confirmMessage = message
      this.confirmFn = fn
      this.showConfirm = true
    },
    confirmAction() {
      this.showConfirm = false
      const fn = this.confirmFn
      this.confirmFn = null
      if (fn) fn()
    }
  }
}
</script>

<style scoped>
.portal {
  min-height: 100vh;
  background: var(--color-background);
  font-family: var(--font-family-base);
  color: var(--color-text-primary);
}

/* Header */
.portal-header {
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border-light);
  position: sticky;
  top: 0;
  z-index: var(--z-sticky);
}

.header-content {
  max-width: 1000px;
  margin: 0 auto;
  padding: var(--spacing-3) var(--spacing-5);
  display: flex;
  align-items: center;
  gap: var(--spacing-4);
  flex-wrap: wrap;
}

.header-content h1 {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  margin: 0;
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  flex: 1;
  min-width: 140px;
}

.nav-tabs {
  display: flex;
  gap: var(--spacing-1);
  flex-wrap: wrap;
}

.nav-tab {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  padding: var(--spacing-2) var(--spacing-3);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  background: transparent;
  border: none;
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-fast);
  white-space: nowrap;
}

.nav-tab:hover {
  background: var(--color-gray-100);
  color: var(--color-text-primary);
}

.nav-tab.active {
  background: var(--color-primary-500);
  color: var(--color-text-inverse);
}

.tab-label {
  display: none;
}

@media (min-width: 768px) {
  .tab-label {
    display: inline;
  }
}

/* Main */
.portal-main {
  max-width: 1000px;
  margin: 0 auto;
  padding: var(--spacing-5);
}

/* Loading */
.loading-container {
  padding: var(--spacing-5) 0;
}

.skeleton-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: var(--spacing-3);
  margin-bottom: var(--spacing-6);
}

.skeleton-card {
  height: 100px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  border-radius: var(--radius-xl);
  animation: shimmer 1.5s infinite;
}

.skeleton-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.skeleton-item {
  height: 60px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  border-radius: var(--radius-lg);
  animation: shimmer 1.5s infinite;
}

.loading-text {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-2);
  color: var(--color-text-tertiary);
  font-size: var(--font-size-sm);
  margin-top: var(--spacing-5);
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* Welcome Banner */
.welcome-banner {
  background: linear-gradient(135deg, var(--color-primary-500) 0%, var(--color-primary-400) 100%);
  border-radius: var(--radius-2xl);
  padding: var(--spacing-8);
  margin-bottom: var(--spacing-6);
  color: var(--color-text-inverse);
  position: relative;
  box-shadow: var(--shadow-primary);
}

.welcome-close {
  position: absolute;
  top: var(--spacing-4);
  right: var(--spacing-4);
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: var(--radius-full);
  color: var(--color-text-inverse);
  cursor: pointer;
  transition: background var(--transition-fast);
}

.welcome-close:hover {
  background: rgba(255, 255, 255, 0.3);
}

.welcome-content h2 {
  margin: 0 0 var(--spacing-2);
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-semibold);
}

.welcome-content > p {
  margin: 0 0 var(--spacing-5);
  opacity: 0.9;
  font-size: var(--font-size-md);
}

.welcome-tips {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-3);
  margin-bottom: var(--spacing-6);
}

.tip {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  padding: var(--spacing-3) var(--spacing-4);
  background: rgba(255, 255, 255, 0.15);
  border-radius: var(--radius-lg);
  font-size: var(--font-size-sm);
}

/* Modal Form */
.modal-form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

/* Fade animation */
.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--transition-slow);
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: var(--spacing-3);
    padding: var(--spacing-3) var(--spacing-4);
  }

  .header-content h1 {
    text-align: center;
    width: 100%;
  }

  .nav-tabs {
    width: 100%;
    overflow-x: auto;
    padding-bottom: var(--spacing-1);
    scrollbar-width: none;
  }

  .nav-tabs::-webkit-scrollbar {
    display: none;
  }

  .portal-main {
    padding: var(--spacing-4);
  }

  .welcome-banner {
    padding: var(--spacing-6);
    margin: calc(-1 * var(--spacing-4));
    margin-bottom: var(--spacing-5);
    border-radius: 0;
  }

  .welcome-tips {
    grid-template-columns: 1fr;
  }
}
</style>
