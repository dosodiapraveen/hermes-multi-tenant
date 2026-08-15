<template>
  <div v-if="hasError" class="error-boundary">
    <div class="error-content">
      <div class="error-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
      </div>

      <h2 class="error-title">Something went wrong</h2>

      <p class="error-message">
        {{ userFriendlyMessage }}
      </p>

      <div v-if="showDetails && errorDetails" class="error-details">
        <button class="details-toggle" @click="detailsExpanded = !detailsExpanded">
          <span>{{ detailsExpanded ? 'Hide' : 'Show' }} technical details</span>
          <svg :class="{ rotated: detailsExpanded }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="6 9 12 15 18 9"/>
          </svg>
        </button>

        <Transition name="expand">
          <pre v-if="detailsExpanded" class="error-stack">{{ errorDetails }}</pre>
        </Transition>
      </div>

      <div class="error-actions">
        <button class="btn btn-primary" @click="handleRetry">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="23 4 23 10 17 10"/>
            <polyline points="1 20 1 14 7 14"/>
            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
          </svg>
          Try Again
        </button>

        <button class="btn btn-secondary" @click="handleGoHome">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
            <polyline points="9 22 9 12 15 12 15 22"/>
          </svg>
          Go to Dashboard
        </button>
      </div>

      <p class="error-help">
        If this problem persists, please contact support.
      </p>
    </div>
  </div>

  <slot v-else />
</template>

<script>
export default {
  name: 'ErrorBoundary',
  props: {
    showDetails: {
      type: Boolean,
      default: import.meta.env.DEV
    },
    fallbackMessage: {
      type: String,
      default: 'We encountered an unexpected error. Please try refreshing the page.'
    }
  },
  emits: ['error', 'retry'],
  data() {
    return {
      hasError: false,
      error: null,
      errorInfo: null,
      detailsExpanded: false
    }
  },
  computed: {
    userFriendlyMessage() {
      if (!this.error) return this.fallbackMessage

      // Map common error types to user-friendly messages
      const message = this.error.message?.toLowerCase() || ''

      if (message.includes('network') || message.includes('fetch')) {
        return 'Unable to connect to the server. Please check your internet connection and try again.'
      }
      if (message.includes('401') || message.includes('unauthorized')) {
        return 'Your session has expired. Please log in again.'
      }
      if (message.includes('403') || message.includes('forbidden')) {
        return 'You don\'t have permission to access this resource.'
      }
      if (message.includes('404') || message.includes('not found')) {
        return 'The requested resource could not be found.'
      }
      if (message.includes('timeout')) {
        return 'The request took too long. Please try again.'
      }

      return this.fallbackMessage
    },
    errorDetails() {
      if (!this.error) return null

      const details = []
      details.push(`Error: ${this.error.message || 'Unknown error'}`)

      if (this.error.stack) {
        details.push(`\nStack trace:\n${this.error.stack}`)
      }

      if (this.errorInfo) {
        details.push(`\nComponent trace:\n${this.errorInfo}`)
      }

      return details.join('\n')
    }
  },
  errorCaptured(error, instance, info) {
    this.hasError = true
    this.error = error
    this.errorInfo = info

    // Log error for debugging
    console.error('Error caught by ErrorBoundary:', error)
    console.error('Component:', instance)
    console.error('Info:', info)

    // Emit for parent handling (e.g., error tracking service)
    this.$emit('error', { error, instance, info })

    // Prevent error from propagating
    return false
  },
  methods: {
    handleRetry() {
      this.hasError = false
      this.error = null
      this.errorInfo = null
      this.$emit('retry')
    },
    handleGoHome() {
      this.hasError = false
      this.error = null
      this.errorInfo = null
      window.location.href = '/user/portal'
    }
  }
}
</script>

<style scoped>
.error-boundary {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-6);
  background: var(--color-background);
}

.error-content {
  max-width: 480px;
  width: 100%;
  text-align: center;
}

.error-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  margin-bottom: var(--spacing-6);
  background: var(--color-error-100);
  border-radius: var(--radius-full);
  color: var(--color-error-500);
}

.error-icon svg {
  width: 40px;
  height: 40px;
}

.error-title {
  margin: 0 0 var(--spacing-3);
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.error-message {
  margin: 0 0 var(--spacing-6);
  font-size: var(--font-size-md);
  color: var(--color-text-secondary);
  line-height: var(--line-height-relaxed);
}

.error-details {
  margin-bottom: var(--spacing-6);
  text-align: left;
}

.details-toggle {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  padding: var(--spacing-2) var(--spacing-3);
  width: 100%;
  background: var(--color-gray-100);
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.details-toggle:hover {
  background: var(--color-gray-200);
}

.details-toggle svg {
  width: 16px;
  height: 16px;
  margin-left: auto;
  transition: transform var(--transition-fast);
}

.details-toggle svg.rotated {
  transform: rotate(180deg);
}

.error-stack {
  margin: var(--spacing-3) 0 0;
  padding: var(--spacing-4);
  background: var(--color-gray-900);
  border-radius: var(--radius-md);
  font-family: var(--font-family-mono);
  font-size: var(--font-size-xs);
  color: var(--color-error-300);
  white-space: pre-wrap;
  word-break: break-all;
  overflow-x: auto;
  max-height: 200px;
}

.error-actions {
  display: flex;
  gap: var(--spacing-3);
  justify-content: center;
  flex-wrap: wrap;
  margin-bottom: var(--spacing-6);
}

.btn {
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

.btn svg {
  width: 18px;
  height: 18px;
}

.btn-primary {
  background: var(--color-primary-500);
  color: var(--color-text-inverse);
}

.btn-primary:hover {
  background: var(--color-primary-600);
}

.btn-secondary {
  background: var(--color-gray-100);
  color: var(--color-text-primary);
}

.btn-secondary:hover {
  background: var(--color-gray-200);
}

.error-help {
  margin: 0;
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
}

/* Expand animation */
.expand-enter-active,
.expand-leave-active {
  transition: all var(--transition-base);
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  max-height: 0;
}

.expand-enter-to,
.expand-leave-from {
  max-height: 300px;
}

/* Responsive */
@media (max-width: 640px) {
  .error-actions {
    flex-direction: column;
  }

  .btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
