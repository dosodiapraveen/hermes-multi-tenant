<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="isOpen" class="modal-overlay" @click="handleOverlayClick" role="dialog" aria-modal="true" :aria-labelledby="titleId">
        <div class="modal-container" @click.stop>
          <div class="modal-header">
            <div class="modal-icon" :class="`icon-${type}`">
              <span v-if="type === 'danger'">⚠️</span>
              <span v-else-if="type === 'warning'">⚡</span>
              <span v-else>ℹ️</span>
            </div>
            <h3 :id="titleId" class="modal-title">{{ title }}</h3>
          </div>

          <div class="modal-body">
            <p>{{ message }}</p>
          </div>

          <div class="modal-footer">
            <button @click="handleCancel" class="btn btn-secondary" :disabled="loading">
              {{ cancelText }}
            </button>
            <button @click="handleConfirm" :class="['btn', `btn-${type}`]" :disabled="loading">
              <LoadingSpinner v-if="loading" size="sm" />
              <span v-else>{{ confirmText }}</span>
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script>
import LoadingSpinner from './LoadingSpinner.vue'

let dialogIdCounter = 0

export default {
  name: 'ConfirmDialog',
  components: { LoadingSpinner },
  props: {
    isOpen: {
      type: Boolean,
      default: false
    },
    title: {
      type: String,
      default: 'Confirm Action'
    },
    message: {
      type: String,
      required: true
    },
    confirmText: {
      type: String,
      default: 'Confirm'
    },
    cancelText: {
      type: String,
      default: 'Cancel'
    },
    type: {
      type: String,
      default: 'info',
      validator: value => ['danger', 'warning', 'info'].includes(value)
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['confirm', 'cancel', 'update:isOpen'],
  data() {
    return {
      titleId: `confirm-dialog-${++dialogIdCounter}`
    }
  },
  methods: {
    handleConfirm() {
      if (!this.loading) {
        this.$emit('confirm')
      }
    },
    handleCancel() {
      if (!this.loading) {
        this.$emit('cancel')
        this.$emit('update:isOpen', false)
      }
    },
    handleOverlayClick() {
      if (!this.loading) {
        this.handleCancel()
      }
    }
  },
  watch: {
    isOpen(newVal) {
      if (newVal) {
        document.body.style.overflow = 'hidden'
      } else {
        document.body.style.overflow = ''
      }
    }
  },
  beforeUnmount() {
    document.body.style.overflow = ''
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 20px;
}

.modal-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  max-width: 440px;
  width: 100%;
  padding: 24px;
}

.modal-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 16px;
}

.modal-icon {
  font-size: 24px;
  line-height: 1;
  flex-shrink: 0;
}

.modal-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1A202C;
}

.modal-body {
  margin-bottom: 24px;
  padding-left: 36px;
}

.modal-body p {
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
  color: #4A5568;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn {
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 500;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  min-width: 80px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: #E2E8F0;
  color: #2D3748;
}

.btn-secondary:hover:not(:disabled) {
  background: #CBD5E0;
}

.btn-danger {
  background: #E53E3E;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #C53030;
}

.btn-warning {
  background: #DD6B20;
  color: white;
}

.btn-warning:hover:not(:disabled) {
  background: #C05621;
}

.btn-info {
  background: #6C5CE7;
  color: white;
}

.btn-info:hover:not(:disabled) {
  background: #5B4BCF;
}

/* Modal animations */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.2s ease;
}

.modal-fade-enter-active .modal-container,
.modal-fade-leave-active .modal-container {
  transition: transform 0.2s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-from .modal-container,
.modal-fade-leave-to .modal-container {
  transform: scale(0.95);
}

@media (max-width: 640px) {
  .modal-container {
    padding: 20px;
  }

  .modal-title {
    font-size: 16px;
  }

  .modal-footer {
    flex-direction: column-reverse;
  }

  .btn {
    width: 100%;
  }
}
</style>
