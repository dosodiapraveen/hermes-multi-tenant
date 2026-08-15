<template>
  <Teleport to="body">
    <TransitionGroup
      name="toast"
      tag="div"
      :class="['toast-container', `toast-${position}`]"
      :style="{ zIndex }"
    >
      <div
        v-for="toast in toasts"
        :key="toast.id"
        :class="['toast', `toast-${toast.type}`]"
        role="alert"
        :aria-live="toast.type === 'error' ? 'assertive' : 'polite'"
      >
        <div class="toast-icon">
          <BaseIcon :name="getIcon(toast.type)" :size="20" />
        </div>
        <div class="toast-content">
          <p v-if="toast.title" class="toast-title">{{ toast.title }}</p>
          <p class="toast-message">{{ toast.message }}</p>
        </div>
        <button
          v-if="toast.dismissible !== false"
          type="button"
          class="toast-close"
          aria-label="Dismiss"
          @click="dismiss(toast.id)"
        >
          <BaseIcon name="x" :size="16" />
        </button>
        <div
          v-if="toast.duration && toast.showProgress"
          class="toast-progress"
          :style="{ animationDuration: `${toast.duration}ms` }"
        ></div>
      </div>
    </TransitionGroup>
  </Teleport>
</template>

<script>
import BaseIcon from './BaseIcon.vue'

export default {
  name: 'BaseToast',
  components: { BaseIcon },
  props: {
    position: {
      type: String,
      default: 'bottom-right',
      validator: (v) => ['top-left', 'top-center', 'top-right', 'bottom-left', 'bottom-center', 'bottom-right'].includes(v)
    },
    zIndex: {
      type: Number,
      default: 800
    },
    maxToasts: {
      type: Number,
      default: 5
    },
    defaultDuration: {
      type: Number,
      default: 4000
    }
  },
  data() {
    return {
      toasts: [],
      idCounter: 0
    }
  },
  methods: {
    getIcon(type) {
      const icons = {
        success: 'check-circle',
        error: 'x-circle',
        warning: 'alert-circle',
        info: 'info'
      }
      return icons[type] || 'info'
    },

    add(options) {
      const id = ++this.idCounter
      const toast = {
        id,
        type: options.type || 'info',
        message: options.message || '',
        title: options.title || '',
        duration: options.duration ?? this.defaultDuration,
        dismissible: options.dismissible ?? true,
        showProgress: options.showProgress ?? false,
        ...options
      }

      // Remove oldest if at max
      if (this.toasts.length >= this.maxToasts) {
        this.toasts.shift()
      }

      this.toasts.push(toast)

      // Auto dismiss
      if (toast.duration > 0) {
        setTimeout(() => {
          this.dismiss(id)
        }, toast.duration)
      }

      return id
    },

    dismiss(id) {
      const index = this.toasts.findIndex(t => t.id === id)
      if (index > -1) {
        this.toasts.splice(index, 1)
      }
    },

    dismissAll() {
      this.toasts = []
    },

    // Convenience methods
    success(message, options = {}) {
      return this.add({ ...options, type: 'success', message })
    },

    error(message, options = {}) {
      return this.add({ ...options, type: 'error', message, duration: options.duration ?? 6000 })
    },

    warning(message, options = {}) {
      return this.add({ ...options, type: 'warning', message })
    },

    info(message, options = {}) {
      return this.add({ ...options, type: 'info', message })
    }
  }
}
</script>

<style scoped>
.toast-container {
  position: fixed;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
  max-width: 420px;
  width: calc(100% - var(--spacing-8));
  pointer-events: none;
}

/* Positions */
.toast-top-left {
  top: var(--spacing-6);
  left: var(--spacing-6);
}

.toast-top-center {
  top: var(--spacing-6);
  left: 50%;
  transform: translateX(-50%);
}

.toast-top-right {
  top: var(--spacing-6);
  right: var(--spacing-6);
}

.toast-bottom-left {
  bottom: var(--spacing-6);
  left: var(--spacing-6);
}

.toast-bottom-center {
  bottom: var(--spacing-6);
  left: 50%;
  transform: translateX(-50%);
}

.toast-bottom-right {
  bottom: var(--spacing-6);
  right: var(--spacing-6);
}

/* Toast item */
.toast {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-3);
  padding: var(--spacing-4);
  background: var(--color-surface);
  border-radius: var(--toast-radius);
  box-shadow: var(--toast-shadow);
  pointer-events: auto;
  position: relative;
  overflow: hidden;
}

.toast-icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.toast-content {
  flex: 1;
  min-width: 0;
}

.toast-title {
  margin: 0 0 var(--spacing-1);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.toast-message {
  margin: 0;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: var(--line-height-normal);
}

.toast-close {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  padding: 0;
  margin: -4px -4px 0 0;
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  color: var(--color-text-tertiary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.toast-close:hover {
  background: var(--color-gray-100);
  color: var(--color-text-primary);
}

/* Progress bar */
.toast-progress {
  position: absolute;
  bottom: 0;
  left: 0;
  height: 3px;
  background: currentColor;
  opacity: 0.3;
  animation: progress linear forwards;
}

@keyframes progress {
  from { width: 100%; }
  to { width: 0%; }
}

/* Toast types */
.toast-success {
  border-left: 4px solid var(--color-success-500);
}

.toast-success .toast-icon {
  color: var(--color-success-500);
}

.toast-error {
  border-left: 4px solid var(--color-error-500);
}

.toast-error .toast-icon {
  color: var(--color-error-500);
}

.toast-warning {
  border-left: 4px solid var(--color-warning-500);
}

.toast-warning .toast-icon {
  color: var(--color-warning-500);
}

.toast-info {
  border-left: 4px solid var(--color-info-500);
}

.toast-info .toast-icon {
  color: var(--color-info-500);
}

/* Animations */
.toast-enter-active {
  animation: toastIn var(--transition-slow) var(--ease-bounce);
}

.toast-leave-active {
  animation: toastOut var(--transition-fast) var(--ease-smooth);
}

.toast-move {
  transition: transform var(--transition-slow) var(--ease-smooth);
}

@keyframes toastIn {
  from {
    opacity: 0;
    transform: translateX(100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes toastOut {
  from {
    opacity: 1;
    transform: translateX(0);
  }
  to {
    opacity: 0;
    transform: translateX(100%);
  }
}

/* Top positions animate differently */
.toast-top-left .toast-enter-active,
.toast-bottom-left .toast-enter-active {
  animation-name: toastInLeft;
}

.toast-top-left .toast-leave-active,
.toast-bottom-left .toast-leave-active {
  animation-name: toastOutLeft;
}

@keyframes toastInLeft {
  from {
    opacity: 0;
    transform: translateX(-100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes toastOutLeft {
  from {
    opacity: 1;
    transform: translateX(0);
  }
  to {
    opacity: 0;
    transform: translateX(-100%);
  }
}

.toast-top-center .toast-enter-active,
.toast-bottom-center .toast-enter-active {
  animation-name: toastInCenter;
}

.toast-top-center .toast-leave-active,
.toast-bottom-center .toast-leave-active {
  animation-name: toastOutCenter;
}

@keyframes toastInCenter {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes toastOutCenter {
  from {
    opacity: 1;
    transform: translateY(0);
  }
  to {
    opacity: 0;
    transform: translateY(-20px);
  }
}

/* Responsive */
@media (max-width: 640px) {
  .toast-container {
    left: var(--spacing-4) !important;
    right: var(--spacing-4) !important;
    max-width: none;
    width: auto;
    transform: none !important;
  }

  .toast-top-left,
  .toast-top-center,
  .toast-top-right {
    top: var(--spacing-4);
  }

  .toast-bottom-left,
  .toast-bottom-center,
  .toast-bottom-right {
    bottom: var(--spacing-4);
  }
}
</style>
