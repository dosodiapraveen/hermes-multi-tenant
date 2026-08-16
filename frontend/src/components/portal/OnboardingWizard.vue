<template>
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="isOpen" class="onboarding-overlay" role="dialog" aria-modal="true" aria-labelledby="onboarding-title">
        <div class="onboarding-container">
          <!-- Progress Bar -->
          <div class="onboarding-progress">
            <div class="progress-header">
              <span class="progress-label">{{ steps[currentStep].title }}</span>
              <span class="progress-counter">Step {{ currentStep + 1 }} of {{ steps.length }}</span>
            </div>
            <div class="progress-steps">
              <div
                v-for="(step, index) in steps"
                :key="step.key"
                :class="['progress-step', { active: currentStep >= index, completed: currentStep > index }]"
              >
                <span class="step-dot" :aria-label="`Step ${index + 1}: ${step.title}`">
                  <svg v-if="currentStep > index" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" aria-hidden="true">
                    <polyline points="20 6 9 17 4 12"/>
                  </svg>
                  <span v-else aria-hidden="true">{{ index + 1 }}</span>
                </span>
              </div>
              <div class="progress-line" role="progressbar" :aria-valuenow="currentStep + 1" :aria-valuemin="1" :aria-valuemax="steps.length">
                <div class="progress-fill" :style="{ width: `${(currentStep / (steps.length - 1)) * 100}%` }"></div>
              </div>
            </div>
          </div>

          <!-- Step Content -->
          <TransitionGroup name="slide" tag="div" class="onboarding-content">
            <div v-if="currentStep === 0" key="welcome" class="step-content">
              <div class="step-icon step-icon--primary">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                  <polyline points="14 2 14 8 20 8"/>
                  <line x1="12" y1="18" x2="12" y2="12"/>
                  <line x1="9" y1="15" x2="15" y2="15"/>
                </svg>
              </div>
              <h2 id="onboarding-title">Welcome to Your AI Dashboard!</h2>
              <p>Your personal AI assistant is ready to help you stay organized. Let's take a quick tour of what you can do.</p>
            </div>

            <div v-if="currentStep === 1" key="notes" class="step-content">
              <div class="step-icon step-icon--info">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                  <polyline points="14 2 14 8 20 8"/>
                  <line x1="16" y1="13" x2="8" y2="13"/>
                  <line x1="16" y1="17" x2="8" y2="17"/>
                </svg>
              </div>
              <h2>Capture Your Thoughts</h2>
              <p>Write <strong>Notes</strong> that sync with your AI assistant. Organize them by category and find them instantly.</p>
              <div class="feature-preview">
                <div class="preview-card">
                  <span class="preview-badge">Work</span>
                  <span class="preview-title">Meeting notes for Q4</span>
                </div>
              </div>
            </div>

            <div v-if="currentStep === 2" key="ideas" class="step-content">
              <div class="step-icon step-icon--warning">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M9 21h6"/>
                  <path d="M9 18H15"/>
                  <path d="M12 2a7 7 0 0 0-5 11.9v3.1h10v-3.1A7 7 0 0 0 12 2Z"/>
                </svg>
              </div>
              <h2>Track Your Ideas</h2>
              <p>Capture brilliant <strong>Ideas</strong> and track them from brainstorm to reality. Tag and categorize for easy discovery.</p>
              <div class="feature-preview">
                <div class="preview-card preview-card--idea">
                  <span class="preview-badge preview-badge--warning">Brainstorm</span>
                  <span class="preview-title">New feature concept</span>
                </div>
              </div>
            </div>

            <div v-if="currentStep === 3" key="schedule" class="step-content">
              <div class="step-icon step-icon--success">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                  <line x1="16" y1="2" x2="16" y2="6"/>
                  <line x1="8" y1="2" x2="8" y2="6"/>
                  <line x1="3" y1="10" x2="21" y2="10"/>
                </svg>
              </div>
              <h2>Stay on Schedule</h2>
              <p>Schedule <strong>Events</strong> and set <strong>Reminders</strong>. Your AI assistant will keep you on track.</p>
              <div class="feature-preview">
                <div class="preview-card preview-card--event">
                  <div class="preview-date">
                    <span class="date-day">15</span>
                    <span class="date-month">Mar</span>
                  </div>
                  <span class="preview-title">Team meeting at 2:00 PM</span>
                </div>
              </div>
            </div>

            <div v-if="currentStep === 4" key="projects" class="step-content">
              <div class="step-icon step-icon--primary">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
                </svg>
              </div>
              <h2>Organize with Projects</h2>
              <p>Create <strong>Projects</strong> to organize related notes, research, and tasks. Perfect for complex work.</p>
              <div class="feature-preview">
                <div class="preview-card preview-card--project">
                  <span class="preview-badge preview-badge--success">Active</span>
                  <span class="preview-title">Website Redesign</span>
                </div>
              </div>
            </div>

            <div v-if="currentStep === 5" key="telegram" class="step-content">
              <div class="step-icon step-icon--info">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                </svg>
              </div>
              <h2>Chat with Your AI</h2>
              <p>Talk to your assistant via <strong>Telegram</strong>. Ask questions, create notes, schedule events — all through natural conversation.</p>
              <div class="telegram-hint">
                <span>Just message your AI anytime!</span>
              </div>
            </div>

            <div v-if="currentStep === 6" key="ready" class="step-content">
              <div class="step-icon step-icon--success step-icon--large">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                  <polyline points="22 4 12 14.01 9 11.01"/>
                </svg>
              </div>
              <h2>You're All Set!</h2>
              <p>Start exploring your dashboard. Create your first note, capture an idea, or schedule an event.</p>
              <div class="quick-actions">
                <button class="quick-action" @click="quickAction('notes')">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <line x1="12" y1="18" x2="12" y2="12"/>
                    <line x1="9" y1="15" x2="15" y2="15"/>
                  </svg>
                  <span>New Note</span>
                </button>
                <button class="quick-action" @click="quickAction('ideas')">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M9 21h6"/>
                    <path d="M12 2a7 7 0 0 0-5 11.9v3.1h10v-3.1A7 7 0 0 0 12 2Z"/>
                  </svg>
                  <span>New Idea</span>
                </button>
                <button class="quick-action" @click="quickAction('schedule')">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="3" y="4" width="18" height="18" rx="2"/>
                    <line x1="12" y1="18" x2="12" y2="12"/>
                    <line x1="9" y1="15" x2="15" y2="15"/>
                  </svg>
                  <span>New Event</span>
                </button>
              </div>
            </div>
          </TransitionGroup>

          <!-- Navigation -->
          <div class="onboarding-nav">
            <button v-if="currentStep > 0" class="nav-btn nav-btn--secondary" @click="prevStep">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="19" y1="12" x2="5" y2="12"/>
                <polyline points="12 19 5 12 12 5"/>
              </svg>
              Back
            </button>
            <button v-else class="nav-btn nav-btn--ghost" @click="skipOnboarding">
              Skip Tour
            </button>

            <button v-if="currentStep < steps.length - 1" class="nav-btn nav-btn--primary" @click="nextStep">
              Next
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="5" y1="12" x2="19" y2="12"/>
                <polyline points="12 5 19 12 12 19"/>
              </svg>
            </button>
            <button v-else class="nav-btn nav-btn--primary nav-btn--finish" @click="finishOnboarding">
              Get Started
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script>
export default {
  name: 'OnboardingWizard',
  props: {
    modelValue: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:modelValue', 'complete', 'skip', 'quickAction'],
  data() {
    return {
      currentStep: 0,
      steps: [
        { key: 'welcome', title: 'Welcome' },
        { key: 'notes', title: 'Notes' },
        { key: 'ideas', title: 'Ideas' },
        { key: 'schedule', title: 'Schedule' },
        { key: 'projects', title: 'Projects' },
        { key: 'telegram', title: 'Chat' },
        { key: 'ready', title: 'Ready' }
      ]
    }
  },
  computed: {
    isOpen() {
      return this.modelValue
    }
  },
  watch: {
    isOpen(val) {
      if (val) {
        document.body.style.overflow = 'hidden'
        this.currentStep = 0
      } else {
        document.body.style.overflow = ''
      }
    }
  },
  beforeUnmount() {
    document.body.style.overflow = ''
  },
  methods: {
    nextStep() {
      if (this.currentStep < this.steps.length - 1) {
        this.currentStep++
      }
    },
    prevStep() {
      if (this.currentStep > 0) {
        this.currentStep--
      }
    },
    skipOnboarding() {
      this.markComplete()
      this.$emit('skip')
      this.$emit('update:modelValue', false)
    },
    finishOnboarding() {
      this.markComplete()
      this.$emit('complete')
      this.$emit('update:modelValue', false)
    },
    quickAction(action) {
      this.markComplete()
      this.$emit('quickAction', action)
      this.$emit('update:modelValue', false)
    },
    markComplete() {
      localStorage.setItem('onboarding_completed', '1')
      localStorage.setItem('portal_welcomed', '1')
    }
  }
}
</script>

<style scoped>
.onboarding-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-4);
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(4px);
}

.onboarding-container {
  width: 100%;
  max-width: 520px;
  background: var(--color-surface);
  border-radius: var(--radius-2xl);
  box-shadow: var(--shadow-2xl);
  overflow: hidden;
}

/* Progress Bar */
.onboarding-progress {
  padding: var(--spacing-4) var(--spacing-6);
  background: var(--color-gray-50);
}

.progress-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-3);
}

.progress-label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.progress-counter {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
  font-variant-numeric: tabular-nums;
}

.progress-steps {
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
}

.progress-step {
  position: relative;
  z-index: 1;
}

.step-dot {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: var(--radius-full);
  background: var(--color-gray-200);
  color: var(--color-text-tertiary);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  transition: all var(--transition-base);
}

.step-dot svg {
  width: 14px;
  height: 14px;
}

.progress-step.active .step-dot {
  background: var(--color-primary-500);
  color: var(--color-text-inverse);
}

.progress-step.completed .step-dot {
  background: var(--color-success-500);
  color: var(--color-text-inverse);
}

.progress-line {
  position: absolute;
  left: 40px;
  right: 40px;
  top: 50%;
  height: 3px;
  background: var(--color-gray-200);
  transform: translateY(-50%);
  z-index: 0;
}

.progress-fill {
  height: 100%;
  background: var(--color-primary-500);
  transition: width var(--transition-slow);
  border-radius: 2px;
}

/* Step Content */
.onboarding-content {
  position: relative;
  min-height: 320px;
  padding: var(--spacing-6);
}

.step-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.step-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 72px;
  height: 72px;
  margin-bottom: var(--spacing-5);
  border-radius: var(--radius-full);
}

.step-icon svg {
  width: 36px;
  height: 36px;
}

.step-icon--primary {
  background: var(--color-primary-100);
  color: var(--color-primary-600);
}

.step-icon--info {
  background: var(--color-info-100);
  color: var(--color-info-600);
}

.step-icon--success {
  background: var(--color-success-100);
  color: var(--color-success-600);
}

.step-icon--warning {
  background: var(--color-warning-100);
  color: var(--color-warning-600);
}

.step-icon--large {
  width: 96px;
  height: 96px;
}

.step-icon--large svg {
  width: 48px;
  height: 48px;
}

.step-content h2 {
  margin: 0 0 var(--spacing-3);
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.step-content p {
  margin: 0 0 var(--spacing-5);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: var(--line-height-relaxed);
  max-width: 380px;
}

/* Feature Preview Cards */
.feature-preview {
  width: 100%;
  max-width: 300px;
}

.preview-card {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  padding: var(--spacing-3) var(--spacing-4);
  background: var(--color-gray-50);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border-light);
}

.preview-badge {
  padding: var(--spacing-1) var(--spacing-2);
  background: var(--color-primary-100);
  color: var(--color-primary-700);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  border-radius: var(--radius-md);
}

.preview-badge--warning {
  background: var(--color-warning-100);
  color: var(--color-warning-700);
}

.preview-badge--success {
  background: var(--color-success-100);
  color: var(--color-success-700);
}

.preview-title {
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
}

.preview-date {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--spacing-2);
  background: var(--color-info-100);
  border-radius: var(--radius-md);
  min-width: 48px;
}

.date-day {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  color: var(--color-info-600);
  line-height: 1;
}

.date-month {
  font-size: var(--font-size-xs);
  color: var(--color-info-500);
  text-transform: uppercase;
}

/* Telegram Hint */
.telegram-hint {
  padding: var(--spacing-4);
  background: linear-gradient(135deg, #0088cc 0%, #229ED9 100%);
  border-radius: var(--radius-lg);
  color: white;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
}

/* Quick Actions */
.quick-actions {
  display: flex;
  gap: var(--spacing-3);
  flex-wrap: wrap;
  justify-content: center;
}

.quick-action {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-2);
  padding: var(--spacing-4);
  min-width: 100px;
  background: var(--color-gray-50);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.quick-action:hover {
  background: var(--color-primary-50);
  border-color: var(--color-primary-200);
}

.quick-action svg {
  width: 24px;
  height: 24px;
  color: var(--color-primary-500);
}

.quick-action span {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

/* Navigation */
.onboarding-nav {
  display: flex;
  justify-content: space-between;
  padding: var(--spacing-4) var(--spacing-6);
  background: var(--color-gray-50);
  border-top: 1px solid var(--color-border-light);
}

.nav-btn {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-2);
  padding: var(--spacing-3) var(--spacing-5);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  border: none;
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.nav-btn svg {
  width: 18px;
  height: 18px;
}

.nav-btn--primary {
  background: var(--color-primary-500);
  color: var(--color-text-inverse);
}

.nav-btn--primary:hover {
  background: var(--color-primary-600);
}

.nav-btn--secondary {
  background: var(--color-gray-200);
  color: var(--color-text-primary);
}

.nav-btn--secondary:hover {
  background: var(--color-gray-300);
}

.nav-btn--ghost {
  background: transparent;
  color: var(--color-text-tertiary);
}

.nav-btn--ghost:hover {
  color: var(--color-text-secondary);
}

.nav-btn--finish {
  padding: var(--spacing-3) var(--spacing-6);
}

/* Animations */
.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--transition-base);
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-enter-active,
.slide-leave-active {
  transition: all var(--transition-base);
  position: absolute;
  width: 100%;
}

.slide-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.slide-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

/* Responsive */
@media (max-width: 640px) {
  .onboarding-container {
    max-height: 90vh;
    overflow-y: auto;
  }

  .onboarding-progress {
    padding: var(--spacing-4);
  }

  .step-dot {
    width: 24px;
    height: 24px;
    font-size: 10px;
  }

  .progress-line {
    left: 30px;
    right: 30px;
  }

  .onboarding-content {
    padding: var(--spacing-5);
    min-height: 280px;
  }

  .step-icon {
    width: 56px;
    height: 56px;
  }

  .step-icon svg {
    width: 28px;
    height: 28px;
  }

  .quick-actions {
    flex-direction: column;
  }

  .quick-action {
    flex-direction: row;
    width: 100%;
    justify-content: center;
  }
}
</style>
