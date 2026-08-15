<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="modelValue"
        class="modal-backdrop"
        :style="{ zIndex: zIndex }"
        @click="handleBackdropClick"
        @keydown.escape="handleEscape"
      >
        <div
          ref="modalContent"
          :class="['modal-content', `modal-${size}`, { 'modal-fullscreen': fullscreen }]"
          role="dialog"
          :aria-modal="true"
          :aria-labelledby="titleId"
          @click.stop
        >
          <!-- Header -->
          <div v-if="$slots.header || title" class="modal-header">
            <slot name="header">
              <h2 :id="titleId" class="modal-title">{{ title }}</h2>
            </slot>
            <button
              v-if="showClose"
              type="button"
              class="modal-close"
              aria-label="Close modal"
              @click="close"
            >
              <BaseIcon name="x" :size="20" />
            </button>
          </div>

          <!-- Body -->
          <div class="modal-body" :class="{ 'no-padding': noPadding }">
            <slot />
          </div>

          <!-- Footer -->
          <div v-if="$slots.footer" class="modal-footer">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script>
import BaseIcon from './BaseIcon.vue'

let modalIdCounter = 0

export default {
  name: 'BaseModal',
  components: { BaseIcon },
  props: {
    modelValue: {
      type: Boolean,
      default: false
    },
    title: {
      type: String,
      default: ''
    },
    size: {
      type: String,
      default: 'md',
      validator: (v) => ['sm', 'md', 'lg', 'xl', 'full'].includes(v)
    },
    showClose: {
      type: Boolean,
      default: true
    },
    closeOnBackdrop: {
      type: Boolean,
      default: true
    },
    closeOnEscape: {
      type: Boolean,
      default: true
    },
    persistent: {
      type: Boolean,
      default: false
    },
    fullscreen: {
      type: Boolean,
      default: false
    },
    noPadding: {
      type: Boolean,
      default: false
    },
    zIndex: {
      type: Number,
      default: 500
    }
  },
  emits: ['update:modelValue', 'close', 'open'],
  data() {
    return {
      titleId: `modal-title-${++modalIdCounter}`,
      previousActiveElement: null
    }
  },
  watch: {
    modelValue: {
      handler(newVal) {
        if (newVal) {
          this.onOpen()
        } else {
          this.onClose()
        }
      },
      immediate: true
    }
  },
  methods: {
    close() {
      if (!this.persistent) {
        this.$emit('update:modelValue', false)
        this.$emit('close')
      }
    },
    handleBackdropClick() {
      if (this.closeOnBackdrop && !this.persistent) {
        this.close()
      } else if (this.persistent) {
        this.shake()
      }
    },
    handleEscape(e) {
      if (this.closeOnEscape && !this.persistent) {
        this.close()
      } else if (this.persistent) {
        this.shake()
      }
    },
    shake() {
      const content = this.$refs.modalContent
      if (content) {
        content.classList.add('modal-shake')
        setTimeout(() => {
          content.classList.remove('modal-shake')
        }, 300)
      }
    },
    onOpen() {
      this.previousActiveElement = document.activeElement
      document.body.style.overflow = 'hidden'
      this.$emit('open')

      this.$nextTick(() => {
        const focusable = this.$refs.modalContent?.querySelector(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        )
        focusable?.focus()
      })
    },
    onClose() {
      document.body.style.overflow = ''
      this.previousActiveElement?.focus()
    }
  },
  beforeUnmount() {
    if (this.modelValue) {
      document.body.style.overflow = ''
    }
  }
}
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-4);
  background: var(--modal-backdrop);
  backdrop-filter: blur(4px);
  z-index: var(--z-modal-backdrop);
}

.modal-content {
  display: flex;
  flex-direction: column;
  max-height: calc(100vh - var(--spacing-8));
  background: var(--color-surface);
  border-radius: var(--modal-radius);
  box-shadow: var(--modal-shadow);
  overflow: hidden;
}

/* Sizes */
.modal-sm {
  width: 100%;
  max-width: 400px;
}

.modal-md {
  width: 100%;
  max-width: 500px;
}

.modal-lg {
  width: 100%;
  max-width: 700px;
}

.modal-xl {
  width: 100%;
  max-width: 900px;
}

.modal-full {
  width: 100%;
  max-width: calc(100vw - var(--spacing-8));
  max-height: calc(100vh - var(--spacing-8));
}

.modal-fullscreen {
  width: 100vw;
  max-width: 100vw;
  height: 100vh;
  max-height: 100vh;
  border-radius: 0;
  margin: calc(-1 * var(--spacing-4));
}

/* Header */
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-4);
  padding: var(--spacing-5) var(--modal-padding);
  border-bottom: 1px solid var(--color-border-light);
  flex-shrink: 0;
}

.modal-title {
  margin: 0;
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  line-height: var(--line-height-tight);
}

.modal-close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  padding: 0;
  background: transparent;
  border: none;
  border-radius: var(--radius-lg);
  color: var(--color-text-tertiary);
  cursor: pointer;
  transition: all var(--transition-fast);
  flex-shrink: 0;
}

.modal-close:hover {
  background: var(--color-gray-100);
  color: var(--color-text-primary);
}

.modal-close:focus-visible {
  outline: 2px solid var(--color-primary-500);
  outline-offset: 2px;
}

/* Body */
.modal-body {
  flex: 1;
  padding: var(--modal-padding);
  overflow-y: auto;
}

.modal-body.no-padding {
  padding: 0;
}

/* Footer */
.modal-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: var(--spacing-3);
  padding: var(--spacing-4) var(--modal-padding);
  border-top: 1px solid var(--color-border-light);
  flex-shrink: 0;
}

/* Animations */
.modal-enter-active {
  animation: modalIn var(--transition-base) var(--ease-smooth);
}

.modal-leave-active {
  animation: modalOut var(--transition-fast) var(--ease-smooth);
}

.modal-enter-active .modal-content {
  animation: modalContentIn var(--transition-slow) var(--ease-bounce);
}

.modal-leave-active .modal-content {
  animation: modalContentOut var(--transition-fast) var(--ease-smooth);
}

@keyframes modalIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes modalOut {
  from {
    opacity: 1;
  }
  to {
    opacity: 0;
  }
}

@keyframes modalContentIn {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(10px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

@keyframes modalContentOut {
  from {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
  to {
    opacity: 0;
    transform: scale(0.95) translateY(10px);
  }
}

/* Shake animation for persistent modal */
.modal-shake {
  animation: shake 0.3s var(--ease-bounce);
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-8px); }
  75% { transform: translateX(8px); }
}

/* Responsive */
@media (max-width: 640px) {
  .modal-backdrop {
    padding: var(--spacing-3);
    align-items: flex-end;
  }

  .modal-content {
    max-height: calc(100vh - var(--spacing-6));
    border-radius: var(--radius-xl) var(--radius-xl) 0 0;
  }

  .modal-sm,
  .modal-md,
  .modal-lg,
  .modal-xl {
    max-width: 100%;
  }
}
</style>
