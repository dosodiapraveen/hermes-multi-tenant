<template>
  <div class="portal">
    <!-- Skip Navigation Links (Accessibility) -->
    <a href="#main-content" class="skip-link">Skip to main content</a>
    <a href="#nav-tabs" class="skip-link">Skip to navigation</a>

    <!-- Header -->
    <header class="portal-header" role="banner">
      <div class="header-content">
        <h1>
          <BaseIcon name="home" :size="20" />
          {{ user }}
        </h1>

        <!-- Mobile Menu Button -->
        <button
          class="mobile-menu-btn"
          :aria-expanded="mobileMenuOpen"
          aria-controls="nav-tabs"
          aria-label="Toggle navigation menu"
          @click="mobileMenuOpen = !mobileMenuOpen"
        >
          <BaseIcon :name="mobileMenuOpen ? 'x' : 'menu'" :size="24" />
        </button>

        <nav
          id="nav-tabs"
          :class="['nav-tabs', { 'nav-tabs--open': mobileMenuOpen }]"
          role="navigation"
          aria-label="Main navigation"
        >
          <button
            v-for="t in tabs"
            :key="t.key"
            :class="['nav-tab', { active: tab === t.key }]"
            @click="selectTab(t.key)"
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

        <div class="header-actions">
          <button
            class="keyboard-hint-btn"
            @click="showKeyboardHelp = true"
            title="Keyboard shortcuts (?)"
            aria-label="Show keyboard shortcuts"
          >
            <BaseIcon name="keyboard" :size="18" />
            <kbd class="hint-key">?</kbd>
          </button>
          <BaseThemeToggle />
          <BaseButton variant="outline" icon="log-out" @click="logout" class="logout-btn">
            <span class="logout-label">Logout</span>
          </BaseButton>
        </div>
      </div>
    </header>

    <main id="main-content" class="portal-main" role="main" aria-label="Dashboard content">
      <ErrorBoundary @error="handleError" @retry="fetchData">
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
      </ErrorBoundary>
    </main>

    <!-- Toast Notifications -->
    <BaseToast ref="toast" position="bottom-right" />

    <!-- Keyboard Shortcuts Help Modal -->
    <BaseModal v-model="showKeyboardHelp" title="Keyboard Shortcuts" size="sm">
      <div class="shortcuts-list">
        <div class="shortcut-group">
          <h4>Navigation</h4>
          <div class="shortcut-item">
            <kbd>?</kbd>
            <span>Show this help</span>
          </div>
          <div class="shortcut-item">
            <kbd>g</kbd> <kbd>h</kbd>
            <span>Go to Home</span>
          </div>
          <div class="shortcut-item">
            <kbd>g</kbd> <kbd>n</kbd>
            <span>Go to Notes</span>
          </div>
          <div class="shortcut-item">
            <kbd>g</kbd> <kbd>i</kbd>
            <span>Go to Ideas</span>
          </div>
          <div class="shortcut-item">
            <kbd>g</kbd> <kbd>p</kbd>
            <span>Go to Projects</span>
          </div>
        </div>
        <div class="shortcut-group">
          <h4>Actions</h4>
          <div class="shortcut-item">
            <kbd>n</kbd>
            <span>New item (context-aware)</span>
          </div>
          <div class="shortcut-item">
            <kbd>/</kbd>
            <span>Focus search</span>
          </div>
          <div class="shortcut-item">
            <kbd>{{ isMac ? '⌘' : 'Ctrl' }}</kbd> <kbd>S</kbd>
            <span>Save current modal</span>
          </div>
          <div class="shortcut-item">
            <kbd>Esc</kbd>
            <span>Close modal / Clear</span>
          </div>
        </div>
      </div>
    </BaseModal>

    <!-- Note Modal -->
    <BaseModal v-model="showNoteModal" :title="editingNote ? 'Edit Note' : 'New Note'" :persistent="isFormDirty('note')">
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
        <BaseButton variant="outline" @click="tryCloseModal('showNoteModal', 'note')">Cancel</BaseButton>
        <BaseButton @click="saveNote" :disabled="busy">Save</BaseButton>
      </template>
    </BaseModal>

    <!-- Idea Modal -->
    <BaseModal v-model="showIdeaModal" :title="editingIdea ? 'Edit Idea' : 'New Idea'" :persistent="isFormDirty('idea')">
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
        <BaseButton variant="outline" @click="tryCloseModal('showIdeaModal', 'idea')">Cancel</BaseButton>
        <BaseButton @click="saveIdea" :disabled="busy">Save</BaseButton>
      </template>
    </BaseModal>

    <!-- Event Modal -->
    <BaseModal v-model="showEventModal" :title="editingEvent ? 'Edit Event' : 'New Event'" size="lg" :persistent="isFormDirty('event')">
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
        <BaseButton variant="outline" @click="tryCloseModal('showEventModal', 'event')">Cancel</BaseButton>
        <BaseButton @click="saveEvent" :disabled="busy">Save</BaseButton>
      </template>
    </BaseModal>

    <!-- Reminder Modal -->
    <BaseModal v-model="showReminderModal" title="New Reminder" :persistent="isFormDirty('reminder')">
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
        <BaseButton variant="outline" @click="tryCloseModal('showReminderModal', 'reminder')">Cancel</BaseButton>
        <BaseButton @click="saveReminder" :disabled="busy">Save</BaseButton>
      </template>
    </BaseModal>

    <!-- Project Modal -->
    <BaseModal v-model="showProjectModal" :title="editingProject ? 'Edit Project' : 'New Project'" :persistent="isFormDirty('project')">
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
        <BaseButton variant="outline" @click="tryCloseModal('showProjectModal', 'project')">Cancel</BaseButton>
        <BaseButton @click="saveProject" :disabled="busy">Save</BaseButton>
      </template>
    </BaseModal>

    <!-- Research Modal -->
    <BaseModal v-model="showResearchModal" title="Add Research" :persistent="isFormDirty('research')">
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
        <BaseButton variant="outline" @click="tryCloseModal('showResearchModal', 'research')">Cancel</BaseButton>
        <BaseButton @click="saveResearch" :disabled="busy">Save</BaseButton>
      </template>
    </BaseModal>

    <!-- Job Modal -->
    <BaseModal v-model="showJobModal" :title="editingJob ? 'Edit Job' : 'New Job'" :persistent="isFormDirty('job')">
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
        <BaseButton variant="outline" @click="tryCloseModal('showJobModal', 'job')">Cancel</BaseButton>
        <BaseButton @click="saveJob" :disabled="busy">Save</BaseButton>
      </template>
    </BaseModal>

    <!-- Confirm Dialog -->
    <BaseConfirmDialog
      v-model="showConfirm"
      :title="confirmTitle"
      :message="confirmMessage"
      :variant="confirmVariant"
      :loading="confirmLoading"
      confirm-text="Delete"
      @confirm="confirmAction"
      @cancel="showConfirm = false"
    />

    <!-- Onboarding Wizard -->
    <OnboardingWizard
      v-model="showOnboarding"
      @complete="onOnboardingComplete"
      @skip="onOnboardingComplete"
      @quickAction="handleQuickAction"
    />
  </div>
</template>

<script>
// Design System imports (shared across projects)
import { BaseIcon, BaseButton, BaseBadge, BaseModal, BaseInput, BaseSelect, BaseToast, BaseDateTimePicker, BaseThemeToggle, BaseConfirmDialog } from '@design-system/components/ui'
import { ErrorBoundary } from '@design-system/components/common'

// Project-specific components
import {
  PortalDashboard,
  PortalNotes,
  PortalIdeas,
  PortalSchedule,
  PortalReminders,
  PortalProjects,
  PortalJobs,
  PortalActivity,
  PortalPersonality,
  OnboardingWizard
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
    BaseThemeToggle,
    BaseConfirmDialog,
    ErrorBoundary,
    PortalDashboard,
    PortalNotes,
    PortalIdeas,
    PortalSchedule,
    PortalReminders,
    PortalProjects,
    PortalJobs,
    PortalActivity,
    PortalPersonality,
    OnboardingWizard
  },
  data() {
    return {
      token: localStorage.getItem('portal_token') || '',
      tab: 'dashboard',
      user: 'My Dashboard',
      loading: true,
      showWelcome: false,
      showOnboarding: false,
      mobileMenuOpen: false,

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
      showKeyboardHelp: false,

      // Keyboard shortcut state
      pendingGoto: false,

      // Editing states
      editingNote: null,
      editingIdea: null,
      editingEvent: null,
      editingProject: null,
      editingJob: null,
      showConfirm: false,
      confirmTitle: 'Confirm Delete',
      confirmMessage: '',
      confirmVariant: 'danger',
      confirmLoading: false,
      confirmFn: null,
      busy: false,

      // Forms
      noteForm: { title: '', content: '', category: 'General' },
      ideaForm: { title: '', content: '', status: 'brainstorm', tags: '' },
      eventForm: { title: '', description: '', datetime: '', location: '', is_all_day: false },
      reminderForm: { title: '', remind_at: '' },
      projectForm: { title: '', description: '' },
      researchForm: { title: '', content: '' },
      jobForm: { title: '', description: '', job_type: 'custom', cron_expression: '0 9 * * *' },

      // Initial form states for dirty checking
      initialNoteForm: null,
      initialIdeaForm: null,
      initialEventForm: null,
      initialReminderForm: null,
      initialProjectForm: null,
      initialResearchForm: null,
      initialJobForm: null,

      // Pending close confirmation
      pendingCloseModal: null,

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
      this.syncTabToUrl(v)
    }
  },
  mounted() {
    this.readTabFromUrl()
    this.fetchData()
    document.addEventListener('keydown', this.handleKeydown)
    window.addEventListener('popstate', this.handlePopState)
    window.addEventListener('beforeunload', this.handleBeforeUnload)
  },
  beforeUnmount() {
    document.removeEventListener('keydown', this.handleKeydown)
    window.removeEventListener('popstate', this.handlePopState)
    window.removeEventListener('beforeunload', this.handleBeforeUnload)
  },
  computed: {
    isMac() {
      return typeof navigator !== 'undefined' && navigator.platform.toUpperCase().indexOf('MAC') >= 0
    },
    // Check if any form has unsaved changes
    hasUnsavedChanges() {
      return this.isFormDirty('note') ||
             this.isFormDirty('idea') ||
             this.isFormDirty('event') ||
             this.isFormDirty('reminder') ||
             this.isFormDirty('project') ||
             this.isFormDirty('research') ||
             this.isFormDirty('job')
    }
  },
  methods: {
    // URL State Sync
    readTabFromUrl() {
      const params = new URLSearchParams(window.location.search)
      const urlTab = params.get('tab')
      const validTabs = this.tabs.map(t => t.key)
      if (urlTab && validTabs.includes(urlTab)) {
        this.tab = urlTab
      }
    },

    syncTabToUrl(tabKey) {
      const params = new URLSearchParams(window.location.search)
      if (tabKey && tabKey !== 'dashboard') {
        params.set('tab', tabKey)
      } else {
        params.delete('tab')
      }
      const newUrl = params.toString()
        ? `${window.location.pathname}?${params.toString()}`
        : window.location.pathname
      window.history.replaceState({}, '', newUrl)
    },

    handlePopState() {
      this.readTabFromUrl()
    },

    showToast(message, type = 'success') {
      this.$refs.toast?.[type]?.(message) || this.$refs.toast?.add?.({ message, type })
    },

    // Unsaved changes handling
    handleBeforeUnload(e) {
      if (this.hasUnsavedChanges) {
        e.preventDefault()
        e.returnValue = 'You have unsaved changes. Are you sure you want to leave?'
        return e.returnValue
      }
    },

    isFormDirty(formType) {
      const formMap = {
        note: { form: 'noteForm', initial: 'initialNoteForm', modal: 'showNoteModal' },
        idea: { form: 'ideaForm', initial: 'initialIdeaForm', modal: 'showIdeaModal' },
        event: { form: 'eventForm', initial: 'initialEventForm', modal: 'showEventModal' },
        reminder: { form: 'reminderForm', initial: 'initialReminderForm', modal: 'showReminderModal' },
        project: { form: 'projectForm', initial: 'initialProjectForm', modal: 'showProjectModal' },
        research: { form: 'researchForm', initial: 'initialResearchForm', modal: 'showResearchModal' },
        job: { form: 'jobForm', initial: 'initialJobForm', modal: 'showJobModal' }
      }

      const config = formMap[formType]
      if (!config || !this[config.modal] || !this[config.initial]) return false

      const current = this[config.form]
      const initial = this[config.initial]

      return JSON.stringify(current) !== JSON.stringify(initial)
    },

    tryCloseModal(modalName, formType) {
      if (this.isFormDirty(formType)) {
        this.pendingCloseModal = modalName
        this.askConfirm(
          'You have unsaved changes. Discard them?',
          () => {
            this[modalName] = false
            this.pendingCloseModal = null
          },
          { title: 'Unsaved Changes', variant: 'warning' }
        )
      } else {
        this[modalName] = false
      }
    },

    handleError({ error, info }) {
      // Log error for tracking (could integrate with error tracking service)
      console.error('Portal error captured:', error, info)
      // Could send to error tracking service here
    },

    handleKeydown(e) {
      // Don't trigger shortcuts when typing in inputs
      const isInput = ['INPUT', 'TEXTAREA', 'SELECT'].includes(e.target.tagName)
      const isEditable = e.target.isContentEditable
      const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0
      const modKey = isMac ? e.metaKey : e.ctrlKey

      // Cmd/Ctrl+S to save current modal (works in input fields)
      if (modKey && e.key === 's') {
        e.preventDefault()
        if (this.showNoteModal && !this.busy) this.saveNote()
        else if (this.showIdeaModal && !this.busy) this.saveIdea()
        else if (this.showEventModal && !this.busy) this.saveEvent()
        else if (this.showReminderModal && !this.busy) this.saveReminder()
        else if (this.showProjectModal && !this.busy) this.saveProject()
        else if (this.showResearchModal && !this.busy) this.saveResearch()
        else if (this.showJobModal && !this.busy) this.saveJob()
        return
      }

      if (e.key === 'Escape') {
        this.pendingGoto = false
        if (this.showKeyboardHelp) this.showKeyboardHelp = false
        else if (this.showNoteModal) this.showNoteModal = false
        else if (this.showProjectModal) this.showProjectModal = false
        else if (this.showResearchModal) this.showResearchModal = false
        else if (this.showReminderModal) this.showReminderModal = false
        else if (this.showIdeaModal) this.showIdeaModal = false
        else if (this.showEventModal) this.showEventModal = false
        else if (this.showJobModal) this.showJobModal = false
        else if (this.showWelcome) this.dismissWelcome()
        return
      }

      // Skip shortcuts when in input fields
      if (isInput || isEditable) return

      // Don't trigger when modals are open
      const modalOpen = this.showNoteModal || this.showIdeaModal || this.showEventModal ||
        this.showReminderModal || this.showProjectModal || this.showResearchModal ||
        this.showJobModal || this.showKeyboardHelp

      if (modalOpen) return

      // Show keyboard help
      if (e.key === '?') {
        e.preventDefault()
        this.showKeyboardHelp = true
        return
      }

      // Focus search with /
      if (e.key === '/') {
        e.preventDefault()
        this.tab = 'dashboard'
        this.$nextTick(() => {
          const searchInput = document.querySelector('.search-container input')
          searchInput?.focus()
        })
        return
      }

      // Go to shortcuts (g + key)
      if (this.pendingGoto) {
        this.pendingGoto = false
        const gotoMap = {
          'h': 'dashboard',
          'd': 'dashboard',
          'n': 'notes',
          'i': 'ideas',
          's': 'schedule',
          'r': 'reminders',
          'p': 'projects',
          'j': 'jobs',
          'a': 'activity'
        }
        if (gotoMap[e.key]) {
          e.preventDefault()
          this.tab = gotoMap[e.key]
        }
        return
      }

      if (e.key === 'g') {
        this.pendingGoto = true
        setTimeout(() => { this.pendingGoto = false }, 1000)
        return
      }

      // New item shortcut (n)
      if (e.key === 'n') {
        e.preventDefault()
        const tabModalMap = {
          'notes': () => this.openNoteModal(),
          'ideas': () => this.openIdeaModal(),
          'schedule': () => this.openEventModal(),
          'reminders': () => this.openReminderModal(),
          'projects': () => this.openProjectModal(),
          'jobs': () => this.openJobModal()
        }
        const openFn = tabModalMap[this.tab]
        if (openFn) openFn()
        else this.openNoteModal() // Default to note
      }
    },

    tabBadge(key) {
      if (key === 'reminders') return this.reminders.filter(r => !r.done).length || null
      if (key === 'jobs') return this.jobs.filter(j => j.last_result?.includes('fail')).length || null
      if (key === 'ideas') return this.ideas.filter(i => i.status === 'brainstorm').length || null
      return null
    },

    selectTab(key) {
      this.tab = key
      this.mobileMenuOpen = false
    },

    async api(method, url, body, options = {}) {
      const { silent = false } = options
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
          this.showToast('Session expired. Please log in again.', 'warning')
          setTimeout(() => { window.location = '/user/login' }, 1500)
          return { error: true, status: 401 }
        }
        if (!r.ok) {
          const data = await r.json().catch(() => ({}))
          const errorMsg = data.detail || data.message || `Request failed (${r.status})`
          if (!silent) this.showToast(errorMsg, 'error')
          return { error: true, status: r.status, message: errorMsg }
        }
        return await r.json()
      } catch (e) {
        if (!silent) this.showToast('Network error. Please check your connection.', 'error')
        return { error: true, message: e.message }
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

        // Show onboarding wizard for first-time users with no data
        const isFirstVisit = !localStorage.getItem('portal_onboarded')
        const hasNoData = this.notes.length === 0 && this.ideas.length === 0 && this.projects.length === 0
        if (isFirstVisit && hasNoData) this.showOnboarding = true
      } finally {
        this.loading = false
      }
    },

    dismissWelcome() {
      this.showWelcome = false
      localStorage.setItem('portal_welcomed', '1')
    },

    onOnboardingComplete() {
      this.showOnboarding = false
      localStorage.setItem('portal_onboarded', '1')
      this.showToast('Welcome to Hermes! Let\'s get started.')
    },

    handleQuickAction(action) {
      this.showOnboarding = false
      localStorage.setItem('portal_onboarded', '1')

      // Open appropriate modal based on action
      switch (action) {
        case 'note':
          this.tab = 'notes'
          this.$nextTick(() => this.openNoteModal())
          break
        case 'idea':
          this.tab = 'ideas'
          this.$nextTick(() => this.openIdeaModal())
          break
        case 'project':
          this.tab = 'projects'
          this.$nextTick(() => this.openProjectModal())
          break
        case 'reminder':
          this.tab = 'reminders'
          this.$nextTick(() => this.openReminderModal())
          break
        default:
          this.tab = 'dashboard'
      }
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
      // Save initial state for dirty checking
      this.initialNoteForm = JSON.parse(JSON.stringify(this.noteForm))
      this.showNoteModal = true
    },

    async saveNote() {
      if (this.busy) return
      if (!this.noteForm.title) return
      this.busy = true
      try {
        const result = this.editingNote
          ? await this.api('PUT', `/api/me/notes/${this.editingNote.id}`, this.noteForm)
          : await this.api('POST', '/api/me/notes', this.noteForm)
        if (result?.error) return
        this.showToast(this.editingNote ? 'Note updated successfully' : 'Note created successfully')
        this.showNoteModal = false
        this.editingNote = null
        await this.fetchData()
      } finally {
        this.busy = false
      }
    },

    deleteNote(id) {
      this.askConfirm('Delete this note?', async () => {
        const res = await this.api('DELETE', `/api/me/notes/${id}`)
        if (res && res.error) return
        this.showToast('Note deleted')
        await this.fetchData()
      })
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
      this.initialIdeaForm = JSON.parse(JSON.stringify(this.ideaForm))
      this.showIdeaModal = true
    },

    async saveIdea() {
      if (this.busy) return
      this.busy = true
      try {
            if (!this.ideaForm.title) return
            const result = this.editingIdea
              ? await this.api('PUT', `/api/me/ideas/${this.editingIdea.id}`, this.ideaForm)
              : await this.api('POST', '/api/me/ideas', this.ideaForm)
            if (result?.error) return
            this.showToast(this.editingIdea ? 'Idea updated successfully' : 'Idea created successfully')
            this.showIdeaModal = false
            this.editingIdea = null
            await this.fetchData()
      } finally {
        this.busy = false
      }
    },

    deleteIdea(id) {
      this.askConfirm('Delete this idea?', async () => {
      const res = await this.api('DELETE', `/api/me/ideas/${id}`)
      if (res && res.error) return
      this.showToast('Idea deleted')
      await this.fetchData()
      })
    },

    // Events
    openEventModal(evt) {
      this.editingEvent = evt || null
      this.eventForm = {
        title: evt?.title || '',
        description: evt?.description || '',
        datetime: this.toLocalInput(evt?.event_start),
        location: evt?.location || '',
        is_all_day: evt?.is_all_day || false
      }
      // Set default time for new events, then save initial state
      if (!evt) {
        const now = new Date()
        const min = now.getHours() * 60 + now.getMinutes()
        const nextSlot = Math.ceil(min / 15) * 15
        const h = Math.floor(nextSlot / 60)
        const m = nextSlot % 60
        const today = now.toISOString().slice(0, 10)
        this.eventForm.datetime = `${today}T${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:00`
      }
      this.initialEventForm = JSON.parse(JSON.stringify(this.eventForm))
      this.showEventModal = true
    },

    async saveEvent() {
      if (this.busy) return
      this.busy = true
      try {
            if (!this.eventForm.title || !this.eventForm.datetime) return

            const payload = {
              title: this.eventForm.title,
              description: this.eventForm.description,
              location: this.eventForm.location,
              is_all_day: this.eventForm.is_all_day,
              event_start: this.toUtc(this.eventForm.datetime),
              event_end: this.eventForm.is_all_day
                ? this.toUtc(this.eventForm.datetime.slice(0, 10) + 'T23:59:00')
                : this.addHour(this.eventForm.datetime)
            }

            const result = this.editingEvent
              ? await this.api('PUT', `/api/me/events/${this.editingEvent.id}`, payload)
              : await this.api('POST', '/api/me/events', payload)
            if (result?.error) return
            this.showToast(this.editingEvent ? 'Event updated successfully' : 'Event scheduled successfully')
            this.showEventModal = false
            this.editingEvent = null
            await this.fetchData()
      } finally {
        this.busy = false
      }
    },

    addHour(datetime) {
      const d = new Date(datetime)
      d.setHours(d.getHours() + 1)
      return d.toISOString()   // full UTC ISO (with offset) — backend stores the correct instant
    },
    toUtc(naive) {              // naive local datetime-local -> UTC instant ISO (Z)
      return naive ? new Date(naive).toISOString() : naive
    },
    toLocalInput(iso) {         // offset-aware ISO -> local datetime-local for the edit input
      if (!iso) return ''
      const d = new Date(iso)
      const p = (n) => String(n).padStart(2, '0')
      return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}T${p(d.getHours())}:${p(d.getMinutes())}`
    },

    deleteEvent(id) {
      this.askConfirm('Delete this event?', async () => {
      const res = await this.api('DELETE', `/api/me/events/${id}`)
      if (res && res.error) return
      this.showToast('Event deleted')
      await this.fetchData()
      })
    },

    // Reminders
    openReminderModal() {
      this.reminderForm = { title: '', remind_at: '' }
      this.initialReminderForm = JSON.parse(JSON.stringify(this.reminderForm))
      this.showReminderModal = true
    },

    async saveReminder() {
      if (this.busy) return
      this.busy = true
      try {
            if (!this.reminderForm.title || !this.reminderForm.remind_at) return
            const result = await this.api('POST', '/api/me/reminders', { ...this.reminderForm, remind_at: this.toUtc(this.reminderForm.remind_at) })
            if (result?.error) return
            this.showToast('Reminder set successfully')
            this.showReminderModal = false
            await this.fetchData()
      } finally {
        this.busy = false
      }
    },

    async toggleReminder(r) {
      const result = await this.api('PUT', `/api/me/reminders/${r.id}`, { done: !r.done }, { silent: true })
      if (result?.error) return
      r.done = !r.done
      this.showToast(r.done ? 'Reminder completed' : 'Reminder restored')
    },

    deleteReminder(id) {
      this.askConfirm('Delete this reminder?', async () => {
      const res = await this.api('DELETE', `/api/me/reminders/${id}`)
      if (res && res.error) return
      this.showToast('Reminder deleted')
      await this.fetchData()
      })
    },

    // Projects
    openProjectModal(proj) {
      this.editingProject = proj || null
      this.projectForm = {
        title: proj?.title || '',
        description: proj?.description || ''
      }
      this.initialProjectForm = JSON.parse(JSON.stringify(this.projectForm))
      this.showProjectModal = true
    },

    async saveProject() {
      if (this.busy) return
      this.busy = true
      try {
            if (!this.projectForm.title) return
            const result = this.editingProject
              ? await this.api('PUT', `/api/me/projects/${this.editingProject.id}`, this.projectForm)
              : await this.api('POST', '/api/me/projects', this.projectForm)
            if (result?.error) return
            this.showToast(this.editingProject ? 'Project updated successfully' : 'Project created successfully')
            this.showProjectModal = false
            this.editingProject = null
            await this.fetchData()
      } finally {
        this.busy = false
      }
    },

    async selectProject(p) {
      const d = await this.api('GET', `/api/me/projects/${p.id}`, null, { silent: true })
      if (d && !d.error) this.selectedProject = d
    },

    async updateProjectStatus(p, status) {
      await this.api('PUT', `/api/me/projects/${p.id}`, { status })
      p.status = status
    },

    deleteProject(id) {
      this.askConfirm('Delete this project and all its research?', async () => {
      const res = await this.api('DELETE', `/api/me/projects/${id}`)
      if (res && res.error) return
      this.showToast('Project deleted')
      await this.fetchData()
      this.selectedProject = null
      })
    },

    // Research
    openResearchModal() {
      this.researchForm = { title: '', content: '' }
      this.initialResearchForm = JSON.parse(JSON.stringify(this.researchForm))
      this.showResearchModal = true
    },

    async saveResearch() {
      if (this.busy) return
      this.busy = true
      try {
            if (!this.researchForm.title || !this.selectedProject) return
            const result = await this.api('POST', `/api/me/projects/${this.selectedProject.id}/research`, this.researchForm)
            if (result?.error) return
            this.showToast('Research added to project')
            this.showResearchModal = false
            this.selectedProject = await this.api('GET', `/api/me/projects/${this.selectedProject.id}`)
      } finally {
        this.busy = false
      }
    },

    deleteResearch(pid, rid) {
      this.askConfirm('Delete this research?', async () => {
      const res = await this.api('DELETE', `/api/me/projects/${pid}/research/${rid}`)
      if (res && res.error) return
      this.showToast('Research deleted')
      this.selectedProject = await this.api('GET', `/api/me/projects/${this.selectedProject.id}`)
      })
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
      this.initialJobForm = JSON.parse(JSON.stringify(this.jobForm))
      this.showJobModal = true
    },

    async saveJob() {
      if (this.busy) return
      this.busy = true
      try {
            if (!this.jobForm.title) return
            const result = this.editingJob
              ? await this.api('PUT', `/api/me/jobs/${this.editingJob.id}`, this.jobForm)
              : await this.api('POST', '/api/me/jobs', this.jobForm)
            if (result?.error) return
            this.showToast(this.editingJob ? 'Job updated successfully' : 'Job created successfully')
            this.showJobModal = false
            this.editingJob = null
            await this.fetchData()
      } finally {
        this.busy = false
      }
    },

    async toggleJob(job) {
      const result = await this.api('PUT', `/api/me/jobs/${job.id}`, { is_enabled: !job.is_enabled }, { silent: true })
      if (result?.error) return
      job.is_enabled = !job.is_enabled
      this.showToast(job.is_enabled ? 'Job enabled' : 'Job disabled')
    },

    deleteJob(id) {
      this.askConfirm('Delete this background job?', async () => {
      const res = await this.api('DELETE', `/api/me/jobs/${id}`)
      if (res && res.error) return
      this.showToast('Job deleted')
      await this.fetchData()
      })
    },

    askConfirm(message, fn, options = {}) {
      this.confirmTitle = options.title || 'Confirm Delete'
      this.confirmMessage = message
      this.confirmVariant = options.variant || 'danger'
      this.confirmFn = fn
      this.confirmLoading = false
      this.showConfirm = true
    },
    async confirmAction() {
      const fn = this.confirmFn
      this.confirmFn = null   // consume immediately: blocks a repeat confirm event from re-running the op
      if (!fn) {
        this.showConfirm = false
        return
      }
      this.confirmLoading = true
      try {
        await fn()
      } finally {
        this.confirmLoading = false
        this.showConfirm = false
      }
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

/* Skip Links (Accessibility) */
.skip-link {
  position: absolute;
  top: -100%;
  left: var(--spacing-4);
  z-index: 9999;
  padding: var(--spacing-3) var(--spacing-4);
  background: var(--color-primary-500);
  color: var(--color-text-inverse);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  text-decoration: none;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  transition: top var(--transition-fast);
}

.skip-link:focus {
  top: var(--spacing-4);
  outline: 2px solid var(--color-primary-600);
  outline-offset: 2px;
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

/* Mobile Menu Button */
.mobile-menu-btn {
  display: none;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  padding: 0;
  background: transparent;
  border: none;
  border-radius: var(--radius-lg);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.mobile-menu-btn:hover {
  background: var(--color-gray-100);
  color: var(--color-text-primary);
}

.mobile-menu-btn:focus-visible {
  outline: 2px solid var(--color-primary-500);
  outline-offset: 2px;
}

.nav-tabs {
  display: flex;
  gap: var(--spacing-1);
  flex-wrap: wrap;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  margin-left: auto;
}

.keyboard-hint-btn {
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
  padding: var(--spacing-2);
  background: transparent;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-tertiary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.keyboard-hint-btn:hover {
  background: var(--color-gray-100);
  color: var(--color-text-primary);
  border-color: var(--color-border);
}

.keyboard-hint-btn:focus-visible {
  outline: 2px solid var(--color-primary-500);
  outline-offset: 2px;
}

.hint-key {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  padding: 0 var(--spacing-1);
  font-size: var(--font-size-xs);
  font-family: var(--font-family-base);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  background: var(--color-gray-100);
  border-radius: var(--radius-sm);
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
  min-height: 44px;
}

.nav-tab:hover {
  background: var(--color-gray-100);
  color: var(--color-text-primary);
}

.nav-tab:focus-visible {
  outline: 2px solid var(--color-primary-500);
  outline-offset: 2px;
}

.nav-tab.active {
  background: var(--color-primary-500);
  color: var(--color-text-inverse);
}

.tab-label {
  display: none;
}

/* Desktop: Show labels */
@media (min-width: 768px) {
  .tab-label {
    display: inline;
  }
}

/* Mobile: Hamburger menu */
@media (max-width: 640px) {
  .header-content {
    flex-wrap: wrap;
    gap: var(--spacing-2);
  }

  .header-content h1 {
    flex: 1;
    min-width: 0;
  }

  .mobile-menu-btn {
    display: flex;
    order: 1;
  }

  .header-actions {
    order: 2;
    gap: var(--spacing-1);
  }

  .keyboard-hint-btn {
    display: none;
  }

  .logout-btn .logout-label {
    display: none;
  }

  .nav-tabs {
    display: none;
    order: 3;
    width: 100%;
    flex-direction: column;
    gap: var(--spacing-1);
    padding-top: var(--spacing-3);
    margin-top: var(--spacing-2);
    border-top: 1px solid var(--color-border-light);
  }

  .nav-tabs--open {
    display: flex;
  }

  .nav-tab {
    width: 100%;
    justify-content: flex-start;
    padding: var(--spacing-3) var(--spacing-4);
  }

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
  background: linear-gradient(
    90deg,
    var(--color-gray-100) 0%,
    var(--color-gray-100) 25%,
    var(--color-gray-200) 50%,
    var(--color-gray-100) 75%,
    var(--color-gray-100) 100%
  );
  background-size: 400% 100%;
  border-radius: var(--radius-xl);
  animation: shimmer 1.5s ease-in-out infinite;
}

.skeleton-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.skeleton-item {
  height: 60px;
  background: linear-gradient(
    90deg,
    var(--color-gray-100) 0%,
    var(--color-gray-100) 25%,
    var(--color-gray-200) 50%,
    var(--color-gray-100) 75%,
    var(--color-gray-100) 100%
  );
  background-size: 400% 100%;
  border-radius: var(--radius-lg);
  animation: shimmer 1.5s ease-in-out infinite;
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
  0% { background-position: 100% 0; }
  100% { background-position: -100% 0; }
}

/* Reduce motion for accessibility */
@media (prefers-reduced-motion: reduce) {
  .skeleton-card,
  .skeleton-item {
    animation: none;
    background: var(--color-gray-100);
  }
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

/* Keyboard Shortcuts */
.shortcuts-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-5);
}

.shortcut-group h4 {
  margin: 0 0 var(--spacing-3);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.shortcut-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  padding: var(--spacing-2) 0;
}

.shortcut-item kbd {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 24px;
  height: 24px;
  padding: 0 var(--spacing-2);
  font-family: var(--font-family-mono);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  background: var(--color-gray-100);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  box-shadow: 0 1px 0 var(--color-border);
}

.shortcut-item span {
  flex: 1;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
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

  /* Float theme + logout to a persistent corner so it never takes workspace
     and is always in reach while scrolling. */
  .header-actions {
    position: fixed;
    bottom: 16px;
    right: 16px;
    z-index: 1000;
    margin-left: 0;
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg, 12px);
    padding: 6px;
    box-shadow: 0 4px 18px rgba(0, 0, 0, 0.14);
    gap: var(--spacing-1);
  }

  .logout-label {
    display: none;
  }

  .portal-main {
    padding-bottom: 84px;
  }
}
</style>
