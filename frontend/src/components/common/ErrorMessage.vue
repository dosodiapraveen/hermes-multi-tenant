<template>
  <div v-if="message" :class="['error-message', `error-${severity}`]" role="alert">
    <div class="error-icon">
      <span v-if="severity === 'error'">⚠️</span>
      <span v-else-if="severity === 'warning'">⚡</span>
      <span v-else>ℹ️</span>
    </div>
    <div class="error-content">
      <p class="error-text">{{ message }}</p>
      <button v-if="retryable" @click="$emit('retry')" class="retry-btn">
        Try Again
      </button>
    </div>
    <button v-if="dismissible" @click="$emit('dismiss')" class="dismiss-btn" aria-label="Dismiss">
      ✕
    </button>
  </div>
</template>

<script>
export default {
  name: 'ErrorMessage',
  props: {
    message: {
      type: String,
      default: ''
    },
    severity: {
      type: String,
      default: 'error',
      validator: value => ['error', 'warning', 'info'].includes(value)
    },
    retryable: {
      type: Boolean,
      default: false
    },
    dismissible: {
      type: Boolean,
      default: true
    }
  },
  emits: ['retry', 'dismiss']
}
</script>

<style scoped>
.error-message {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 16px;
  border-left: 4px solid;
}

.error-error {
  background: #FFF5F5;
  border-left-color: #E53E3E;
  color: #742A2A;
}

.error-warning {
  background: #FFFAF0;
  border-left-color: #DD6B20;
  color: #7C2D12;
}

.error-info {
  background: #EBF8FF;
  border-left-color: #3182CE;
  color: #2C5282;
}

.error-icon {
  font-size: 20px;
  line-height: 1;
  flex-shrink: 0;
}

.error-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.error-text {
  margin: 0;
  font-size: 14px;
  line-height: 1.5;
}

.retry-btn {
  align-self: flex-start;
  padding: 6px 12px;
  font-size: 13px;
  font-weight: 500;
  color: #6C5CE7;
  background: white;
  border: 1px solid #6C5CE7;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.retry-btn:hover {
  background: #6C5CE7;
  color: white;
}

.dismiss-btn {
  flex-shrink: 0;
  padding: 0;
  width: 24px;
  height: 24px;
  font-size: 16px;
  color: inherit;
  background: transparent;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  opacity: 0.6;
  transition: opacity 0.2s;
}

.dismiss-btn:hover {
  opacity: 1;
  background: rgba(0, 0, 0, 0.05);
}
</style>
