<template>
  <Teleport to="body">
    <Transition name="toast-slide">
      <div v-if="isVisible" :class="['toast', `toast-${type}`]" role="alert" aria-live="polite">
        <div class="toast-icon">
          <span v-if="type === 'success'">✓</span>
          <span v-else-if="type === 'error'">✕</span>
          <span v-else-if="type === 'warning'">!</span>
          <span v-else>i</span>
        </div>
        <p class="toast-message">{{ message }}</p>
        <button v-if="dismissible" @click="close" class="toast-close" aria-label="Close">
          ✕
        </button>
      </div>
    </Transition>
  </Teleport>
</template>

<script>
export default {
  name: 'SuccessToast',
  props: {
    message: {
      type: String,
      required: true
    },
    type: {
      type: String,
      default: 'success',
      validator: value => ['success', 'error', 'warning', 'info'].includes(value)
    },
    duration: {
      type: Number,
      default: 3000
    },
    dismissible: {
      type: Boolean,
      default: true
    }
  },
  data() {
    return {
      isVisible: false,
      timer: null
    }
  },
  mounted() {
    this.show()
  },
  beforeUnmount() {
    if (this.timer) {
      clearTimeout(this.timer)
    }
  },
  methods: {
    show() {
      this.isVisible = true
      if (this.duration > 0) {
        this.timer = setTimeout(() => {
          this.close()
        }, this.duration)
      }
    },
    close() {
      this.isVisible = false
      setTimeout(() => {
        this.$emit('close')
      }, 300)
    }
  }
}
</script>

<style scoped>
.toast {
  position: fixed;
  bottom: 24px;
  right: 24px;
  min-width: 280px;
  max-width: 420px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border-radius: 10px;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  z-index: 10000;
  background: white;
}

.toast-success {
  border-left: 4px solid #48BB78;
}

.toast-error {
  border-left: 4px solid #E53E3E;
}

.toast-warning {
  border-left: 4px solid #DD6B20;
}

.toast-info {
  border-left: 4px solid #6C5CE7;
}

.toast-icon {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 14px;
  color: white;
}

.toast-success .toast-icon {
  background: #48BB78;
}

.toast-error .toast-icon {
  background: #E53E3E;
}

.toast-warning .toast-icon {
  background: #DD6B20;
}

.toast-info .toast-icon {
  background: #6C5CE7;
}

.toast-message {
  flex: 1;
  margin: 0;
  font-size: 14px;
  line-height: 1.5;
  color: #2D3748;
}

.toast-close {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  padding: 0;
  background: transparent;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  color: #718096;
  transition: all 0.2s;
}

.toast-close:hover {
  background: #EDF2F7;
  color: #2D3748;
}

/* Toast animations */
.toast-slide-enter-active,
.toast-slide-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.toast-slide-enter-from {
  transform: translateX(100%);
  opacity: 0;
}

.toast-slide-leave-to {
  transform: translateY(20px);
  opacity: 0;
}

@media (max-width: 640px) {
  .toast {
    bottom: 16px;
    right: 16px;
    left: 16px;
    min-width: auto;
  }
}
</style>
