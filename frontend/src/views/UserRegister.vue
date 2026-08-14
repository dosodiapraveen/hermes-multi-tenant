<template>
  <div class="auth-page">
    <!-- Header with branding -->
    <div class="auth-header">
      <div class="logo">
        <div class="logo-icon">H</div>
        <span class="logo-text">Hermes</span>
      </div>
    </div>

    <!-- Main auth card -->
    <div class="auth-card">
      <div class="auth-card-header">
        <h1>Request Access</h1>
        <p class="subtitle">Submit your request — an admin reviews and approves your account</p>
      </div>

      <!-- Error/Success Alert -->
      <div v-if="msg" class="alert" :class="msgType">
        <svg v-if="msgType === 'error'" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>
        </svg>
        <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>
        </svg>
        <span>{{ msg }}</span>
      </div>

      <form @submit.prevent="register" class="auth-form">
        <!-- Full Name -->
        <div class="input-group">
          <label for="full-name">Your name <span class="required">*</span></label>
          <div class="input-wrapper" :class="{ 'has-error': fullNameError, 'focused': fullNameFocused }">
            <input id="full-name" v-model="full_name" type="text" placeholder="e.g. Sarah Johnson"
              autocomplete="name" maxlength="120"
              @focus="fullNameFocused = true"
              @blur="fullNameFocused = false; validateFullName()"
              @input="fullNameError = ''" />
          </div>
          <span v-if="fullNameError" class="input-error">{{ fullNameError }}</span>
        </div>

        <!-- Email Input -->
        <div class="input-group">
          <label for="email">Email address <span class="required">*</span></label>
          <div class="input-wrapper" :class="{ 'has-error': emailError, 'focused': emailFocused }">
            <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
              <polyline points="22,6 12,13 2,6"/>
            </svg>
            <input
              id="email"
              v-model="email"
              type="email"
              placeholder="you@example.com"
              autocomplete="email"
              maxlength="120"
              @focus="emailFocused = true"
              @blur="emailFocused = false; validateEmail()"
              @input="emailError = ''"
            />
          </div>
          <span v-if="emailError" class="input-error">{{ emailError }}</span>
        </div>

        <!-- Use Case -->
        <div class="input-group">
          <label for="use-case">What will you use your AI agent for? <span class="required">*</span></label>
          <div class="input-wrapper" :class="{ 'has-error': useCaseError, 'focused': useCaseFocused }">
            <textarea
              id="use-case"
              v-model="use_case"
              rows="3"
              maxlength="500"
              placeholder="Describe your use case (helps us prioritize your request). Example: 'Managing research notes and client meeting reminders for my consulting practice.'"
              class="no-icon"
              @focus="useCaseFocused = true"
              @blur="useCaseFocused = false; validateUseCase()"
              @input="useCaseError = ''"></textarea>
          </div>
          <div class="input-meta">
            <span v-if="useCaseError" class="input-error">{{ useCaseError }}</span>
            <span class="char-count" :class="{ 'error': use_case.length < 20, 'good': use_case.length >= 20 }">
              {{ use_case.length }}/500 characters {{ use_case.length < 20 ? `(${20 - use_case.length} more needed)` : '✓' }}
            </span>
          </div>
        </div>

        <!-- Agent Name (Optional) -->
        <div class="input-group">
          <label for="agent-name">Preferred agent name <span class="optional">(optional)</span></label>
          <div class="input-wrapper" :class="{ 'focused': agentNameFocused }">
            <input id="agent-name" v-model="agent_name" type="text" placeholder="e.g. Research Assistant"
              maxlength="120"
              @focus="agentNameFocused = true" @blur="agentNameFocused = false" />
          </div>
          <span class="input-hint">A name for your AI assistant (admin can modify this)</span>
        </div>

        <!-- Submit Button -->
        <button type="submit" class="btn-primary" :disabled="loading || !isFormValid">
          <span v-if="!loading">Submit Request</span>
          <span v-else class="loading-spinner">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
            </svg>
            Submitting...
          </span>
        </button>

        <!-- Info notice -->
        <p class="info-notice">
          📧 <strong>Next steps:</strong> You'll receive a verification email. After verifying, an admin reviews your request (usually 1-3 business days). Once approved, you'll get an email to set your password.
        </p>
      </form>

      <!-- Divider -->
      <div class="divider">
        <span>Already have an account?</span>
      </div>

      <!-- Login Link -->
      <a href="/user/login" class="btn-secondary">
        Sign in instead
      </a>

      <!-- Check Status Link -->
      <a v-if="submittedEmail" href="/user/status" class="link-check-status">
        Check registration status →
      </a>
    </div>

    <!-- Footer -->
    <div class="auth-footer">
      <a href="/" class="link-muted">← Back to home</a>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      email: '',
      full_name: '',
      agent_name: '',
      use_case: '',
      msg: '',
      msgType: 'error',
      emailError: '',
      fullNameError: '',
      useCaseError: '',
      emailFocused: false,
      fullNameFocused: false,
      useCaseFocused: false,
      agentNameFocused: false,
      loading: false,
      submittedEmail: ''
    }
  },
  computed: {
    isFormValid() {
      return this.full_name.trim().length > 0 &&
             this.validateEmailFormat(this.email) &&
             this.use_case.trim().length >= 20
    }
  },
  methods: {
    validateEmailFormat(email) {
      const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      return re.test(email)
    },
    validateEmail() {
      if (!this.email.trim()) {
        this.emailError = 'Email is required'
        return false
      }
      if (!this.validateEmailFormat(this.email)) {
        this.emailError = 'Please enter a valid email address'
        return false
      }
      this.emailError = ''
      return true
    },
    validateFullName() {
      if (!this.full_name.trim()) {
        this.fullNameError = 'Your name is required'
        return false
      }
      if (this.full_name.trim().length < 2) {
        this.fullNameError = 'Please enter your full name'
        return false
      }
      this.fullNameError = ''
      return true
    },
    validateUseCase() {
      if (!this.use_case.trim()) {
        this.useCaseError = 'Please describe your use case'
        return false
      }
      if (this.use_case.trim().length < 20) {
        this.useCaseError = `Please provide at least 20 characters (${20 - this.use_case.trim().length} more needed)`
        return false
      }
      this.useCaseError = ''
      return true
    },
    async register() {
      this.msg = ''
      this.msgType = 'error'

      // Validate all fields
      const emailValid = this.validateEmail()
      const nameValid = this.validateFullName()
      const useCaseValid = this.validateUseCase()

      if (!emailValid || !nameValid || !useCaseValid) {
        return
      }

      this.loading = true

      try {
        const r = await fetch('/api/auth/user/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: this.email.trim().toLowerCase(),
            full_name: this.full_name.trim(),
            agent_name: this.agent_name.trim(),
            use_case: this.use_case.trim()
            // NOTE: No password field - password set after approval
          })
        })
        const d = await r.json()

        if (r.ok) {
          this.msgType = 'success'
          this.msg = d.message || 'Request submitted! Check your email to verify (check spam folder too).'
          this.submittedEmail = this.email
          // Clear form except email (for status check)
          this.full_name = ''
          this.agent_name = ''
          this.use_case = ''

          // Show helpful message
          setTimeout(() => {
            this.msg += ' You can check your registration status at any time.'
          }, 2000)
        } else {
          this.msgType = 'error'
          this.msg = d.detail || 'Registration failed. Please try again.'
        }
        this.loading = false
      } catch (e) {
        this.msgType = 'error'
        this.msg = 'Connection error. Please check your internet and try again.'
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  font-family: 'Inter', -apple-system, sans-serif;
}

/* Header */
.auth-header {
  margin-bottom: 32px;
  text-align: center;
}

.logo {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.logo-icon {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #fff, #f0f0f0);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 18px;
  color: #667eea;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  color: #fff;
  letter-spacing: -0.5px;
}

/* Auth Card */
.auth-card {
  background: #fff;
  border-radius: 16px;
  padding: 40px;
  width: 100%;
  max-width: 540px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.auth-card-header {
  text-align: center;
  margin-bottom: 28px;
}

.auth-card-header h1 {
  font-size: 28px;
  font-weight: 700;
  color: #1A1A2E;
  margin-bottom: 8px;
  letter-spacing: -0.5px;
}

.subtitle {
  font-size: 15px;
  color: #636E70;
  margin: 0;
  line-height: 1.5;
}

/* Alert */
.alert {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border-radius: 10px;
  font-size: 14px;
  margin-bottom: 24px;
  animation: slideDown 0.3s ease;
  line-height: 1.5;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.alert.error {
  background: #FEF2F2;
  color: #DC2626;
  border: 1px solid #FEE2E2;
}

.alert.success {
  background: #F0FDF4;
  color: #16A34A;
  border: 1px solid #DCFCE7;
}

.alert svg {
  flex-shrink: 0;
}

/* Form */
.auth-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.input-group label {
  font-size: 14px;
  font-weight: 500;
  color: #1A1A2E;
}

.required {
  color: #DC2626;
}

.optional {
  color: #9CA3AF;
  font-weight: 400;
  font-size: 13px;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  border: 1.5px solid #E5E7EB;
  border-radius: 10px;
  background: #fff;
  transition: all 0.2s ease;
}

.input-wrapper:hover {
  border-color: #D1D5DB;
}

.input-wrapper.focused {
  border-color: #6C5CE7;
  box-shadow: 0 0 0 3px rgba(108, 92, 231, 0.1);
}

.input-wrapper.has-error {
  border-color: #DC2626;
}

.input-icon {
  position: absolute;
  left: 14px;
  color: #9CA3AF;
  pointer-events: none;
}

.input-wrapper input {
  width: 100%;
  padding: 12px 14px 12px 44px;
  border: none;
  background: transparent;
  font-size: 15px;
  color: #1A1A2E;
  outline: none;
  font-family: 'Inter', -apple-system, sans-serif;
}

.input-wrapper input::placeholder {
  color: #9CA3AF;
}

.input-wrapper textarea {
  width: 100%;
  padding: 12px 14px;
  border: none;
  background: transparent;
  font-size: 15px;
  color: #1A1A2E;
  outline: none;
  font-family: 'Inter', -apple-system, sans-serif;
  resize: vertical;
  min-height: 80px;
}

.input-wrapper textarea::placeholder {
  color: #9CA3AF;
}

.input-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: -2px;
}

.input-error {
  font-size: 13px;
  color: #DC2626;
}

.input-hint {
  font-size: 13px;
  color: #6B7280;
}

.char-count {
  font-size: 12px;
  color: #9CA3AF;
  margin-left: auto;
}

.char-count.error {
  color: #DC2626;
  font-weight: 500;
}

.char-count.good {
  color: #16A34A;
}

.info-notice {
  font-size: 13px;
  color: #4B5563;
  background: #F9FAFB;
  padding: 12px 16px;
  border-radius: 8px;
  margin-top: 8px;
  line-height: 1.6;
  border-left: 3px solid #6C5CE7;
}

/* Buttons */
.btn-primary {
  width: 100%;
  padding: 14px;
  background: #6C5CE7;
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  font-family: 'Inter', -apple-system, sans-serif;
  transition: all 0.2s;
  margin-top: 8px;
}

.btn-primary:hover:not(:disabled) {
  background: #5A4BD1;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(108, 92, 231, 0.4);
}

.btn-primary:active:not(:disabled) {
  transform: translateY(0);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading-spinner {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.loading-spinner svg {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* Divider */
.divider {
  display: flex;
  align-items: center;
  margin: 28px 0 20px;
  text-align: center;
  color: #9CA3AF;
  font-size: 13px;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  border-bottom: 1px solid #E5E7EB;
}

.divider span {
  padding: 0 16px;
}

/* Secondary Button */
.btn-secondary {
  width: 100%;
  padding: 14px;
  background: #F9FAFB;
  color: #1A1A2E;
  border: 1.5px solid #E5E7EB;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
  display: block;
  text-align: center;
  font-family: 'Inter', -apple-system, sans-serif;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: #fff;
  border-color: #6C5CE7;
  color: #6C5CE7;
}

.link-check-status {
  display: block;
  text-align: center;
  margin-top: 16px;
  font-size: 14px;
  color: #6C5CE7;
  text-decoration: none;
  font-weight: 500;
}

.link-check-status:hover {
  text-decoration: underline;
}

/* Footer */
.auth-footer {
  margin-top: 24px;
  text-align: center;
}

.link-muted {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  transition: color 0.2s;
}

.link-muted:hover {
  color: #fff;
}

/* Responsive */
@media (max-width: 600px) {
  .auth-card {
    padding: 32px 24px;
  }

  .auth-card-header h1 {
    font-size: 24px;
  }

  .input-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
}
</style>
