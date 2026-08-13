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
        <h1>Create your account</h1>
        <p class="subtitle">Link your email to your agent account</p>
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

      <!-- Verify Link Banner -->
      <div v-if="verifyLink" class="verify-banner">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
          <polyline points="22,6 12,13 2,6"/>
        </svg>
        <div class="verify-content">
          <strong>Email not sent?</strong>
          <a :href="verifyLink" class="verify-link">Click here to verify your email manually</a>
        </div>
      </div>

      <form @submit.prevent="register" class="auth-form">
        <!-- Agent ID Input (conditionally shown) -->
        <div v-if="!autoProfile" class="input-group">
          <label for="agent-id">Agent ID</label>
          <div class="input-wrapper" :class="{ 'has-error': agentIdError, 'focused': agentIdFocused }">
            <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>
            </svg>
            <input
              id="agent-id"
              v-model="manual_profile_id"
              type="text"
              placeholder="Your agent profile ID"
              @focus="agentIdFocused = true"
              @blur="agentIdFocused = false; validateAgentIdField()"
              @input="agentIdError = ''"
            />
          </div>
          <span v-if="agentIdError" class="input-error">{{ agentIdError }}</span>
          <span v-else class="input-hint">Your agent ID is shared by your admin via invite link</span>
        </div>

        <!-- Email Input -->
        <div class="input-group">
          <label for="email">Email address</label>
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
              @focus="emailFocused = true"
              @blur="emailFocused = false; validateEmailField()"
              @input="emailError = ''"
            />
          </div>
          <span v-if="emailError" class="input-error">{{ emailError }}</span>
        </div>

        <!-- Password Input -->
        <div class="input-group">
          <label for="password">Password</label>
          <div class="input-wrapper" :class="{ 'has-error': passwordError, 'focused': passwordFocused }">
            <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
              <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
            </svg>
            <input
              id="password"
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              placeholder="Create a strong password"
              autocomplete="new-password"
              @focus="passwordFocused = true"
              @blur="passwordFocused = false; validatePasswordField()"
              @input="onPasswordInput"
            />
            <button
              type="button"
              class="password-toggle"
              @click="showPassword = !showPassword"
              tabindex="-1"
            >
              <svg v-if="!showPassword" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                <circle cx="12" cy="12" r="3"/>
              </svg>
              <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                <line x1="1" y1="1" x2="23" y2="23"/>
              </svg>
            </button>
          </div>
          <span v-if="passwordError" class="input-error">{{ passwordError }}</span>

          <!-- Password strength indicator -->
          <div v-if="password && !passwordError" class="password-requirements">
            <div class="requirement" :class="{ met: passwordChecks.length }">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              <span>At least 12 characters</span>
            </div>
            <div class="requirement" :class="{ met: passwordChecks.uppercase }">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              <span>One uppercase letter</span>
            </div>
            <div class="requirement" :class="{ met: passwordChecks.lowercase }">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              <span>One lowercase letter</span>
            </div>
            <div class="requirement" :class="{ met: passwordChecks.number }">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              <span>One number</span>
            </div>
          </div>
        </div>

        <!-- Submit Button -->
        <button type="submit" class="btn-primary" :disabled="loading">
          <span v-if="!loading">Create account</span>
          <span v-else class="loading-spinner">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
            </svg>
            Creating account...
          </span>
        </button>

        <!-- Terms notice -->
        <p class="terms-notice">
          By creating an account, you agree to our Terms of Service and Privacy Policy
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
      password: '',
      manual_profile_id: '',
      msg: '',
      msgType: 'error',
      verifyLink: '',
      autoProfile: false,
      emailError: '',
      passwordError: '',
      agentIdError: '',
      emailFocused: false,
      passwordFocused: false,
      agentIdFocused: false,
      showPassword: false,
      loading: false,
      passwordChecks: {
        length: false,
        uppercase: false,
        lowercase: false,
        number: false
      }
    }
  },
  mounted() {
    const urlToken = new URLSearchParams(location.search).get('token')
    if (urlToken) {
      this.manual_profile_id = urlToken
      this.autoProfile = true
    }
  },
  methods: {
    validateEmail(email) {
      const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      return re.test(email)
    },
    validatePassword(password) {
      if (password.length < 12) return 'Password must be at least 12 characters'
      if (!/[A-Z]/.test(password)) return 'Password must contain at least one uppercase letter'
      if (!/[a-z]/.test(password)) return 'Password must contain at least one lowercase letter'
      if (!/[0-9]/.test(password)) return 'Password must contain at least one number'
      return null
    },
    validateEmailField() {
      if (!this.email) {
        this.emailError = 'Email is required'
        return false
      }
      if (!this.validateEmail(this.email)) {
        this.emailError = 'Please enter a valid email address'
        return false
      }
      this.emailError = ''
      return true
    },
    validatePasswordField() {
      if (!this.password) {
        this.passwordError = 'Password is required'
        return false
      }
      const error = this.validatePassword(this.password)
      if (error) {
        this.passwordError = error
        return false
      }
      this.passwordError = ''
      return true
    },
    validateAgentIdField() {
      if (!this.manual_profile_id) {
        this.agentIdError = 'Agent ID is required'
        return false
      }
      this.agentIdError = ''
      return true
    },
    onPasswordInput() {
      this.passwordError = ''
      // Update password checks
      this.passwordChecks.length = this.password.length >= 12
      this.passwordChecks.uppercase = /[A-Z]/.test(this.password)
      this.passwordChecks.lowercase = /[a-z]/.test(this.password)
      this.passwordChecks.number = /[0-9]/.test(this.password)
    },
    async register() {
      this.msg = ''
      this.msgType = 'error'
      this.verifyLink = ''

      // Validate all fields
      const agentIdValid = this.autoProfile || this.validateAgentIdField()
      const emailValid = this.validateEmailField()
      const passwordValid = this.validatePasswordField()

      if (!agentIdValid || !emailValid || !passwordValid) {
        return
      }

      this.loading = true

      try {
        const profile_id = this.manual_profile_id
        const r = await fetch('/api/auth/user/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: this.email,
            password: this.password,
            profile_id
          })
        })
        const d = await r.json()

        if (r.ok) {
          this.msgType = 'success'
          this.msg = d.message || 'Account created! Please check your email to verify.'
          if (d.verify_link) this.verifyLink = d.verify_link

          // Clear form on success
          this.password = ''
          this.passwordChecks = {
            length: false,
            uppercase: false,
            lowercase: false,
            number: false
          }
        } else {
          this.msgType = 'error'
          this.msg = d.detail || 'Registration failed. Please try again.'
        }
        this.loading = false
      } catch (e) {
        this.msgType = 'error'
        this.msg = 'Connection error. Please try again.'
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
  max-width: 480px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.auth-card-header {
  text-align: center;
  margin-bottom: 32px;
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

/* Verify Banner */
.verify-banner {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 16px;
  background: #FEF3C7;
  border: 1px solid #FDE68A;
  border-radius: 10px;
  margin-bottom: 24px;
  color: #92400E;
}

.verify-banner svg {
  flex-shrink: 0;
  margin-top: 2px;
}

.verify-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 13px;
}

.verify-content strong {
  font-weight: 600;
}

.verify-link {
  color: #92400E;
  text-decoration: underline;
  font-weight: 500;
}

.verify-link:hover {
  color: #78350F;
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

.password-toggle {
  position: absolute;
  right: 12px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  color: #9CA3AF;
  transition: color 0.2s;
}

.password-toggle:hover {
  color: #6C5CE7;
}

.input-error {
  font-size: 13px;
  color: #DC2626;
  margin-top: 4px;
}

.input-hint {
  font-size: 13px;
  color: #6B7280;
  margin-top: 4px;
}

/* Password Requirements */
.password-requirements {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-top: 8px;
  padding: 12px;
  background: #F9FAFB;
  border-radius: 8px;
}

.requirement {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #9CA3AF;
  transition: color 0.2s;
}

.requirement svg {
  opacity: 0;
  transition: opacity 0.2s;
}

.requirement.met {
  color: #16A34A;
}

.requirement.met svg {
  opacity: 1;
}

/* Terms Notice */
.terms-notice {
  font-size: 12px;
  color: #9CA3AF;
  text-align: center;
  margin-top: 4px;
  line-height: 1.5;
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
  opacity: 0.7;
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
@media (max-width: 480px) {
  .auth-card {
    padding: 32px 24px;
  }

  .auth-card-header h1 {
    font-size: 24px;
  }

  .password-requirements {
    grid-template-columns: 1fr;
  }
}
</style>