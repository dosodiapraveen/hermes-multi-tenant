<template>
  <BaseModal
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    :title="title"
    size="sm"
    :persistent="loading"
  >
    <div class="confirm-content">
      <div v-if="icon" :class="['confirm-icon', `confirm-icon--${variant}`]">
        <BaseIcon :name="iconName" :size="24" />
      </div>
      <p class="confirm-message">{{ message }}</p>
    </div>

    <template #footer>
      <BaseButton
        variant="outline"
        :disabled="loading"
        @click="handleCancel"
      >
        {{ cancelText }}
      </BaseButton>
      <BaseButton
        :variant="confirmVariant"
        :loading="loading"
        :icon="confirmIcon"
        @click="handleConfirm"
      >
        {{ confirmText }}
      </BaseButton>
    </template>
  </BaseModal>
</template>

<script>
import BaseModal from './BaseModal.vue'
import BaseButton from './BaseButton.vue'
import BaseIcon from './BaseIcon.vue'

export default {
  name: 'BaseConfirmDialog',
  components: { BaseModal, BaseButton, BaseIcon },
  props: {
    modelValue: {
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
    variant: {
      type: String,
      default: 'danger',
      validator: v => ['danger', 'warning', 'info', 'primary'].includes(v)
    },
    icon: {
      type: Boolean,
      default: true
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:modelValue', 'confirm', 'cancel'],
  computed: {
    iconName() {
      const icons = {
        danger: 'alert-triangle',
        warning: 'alert-circle',
        info: 'info',
        primary: 'help-circle'
      }
      return icons[this.variant] || 'alert-triangle'
    },
    confirmVariant() {
      return this.variant === 'info' ? 'primary' : this.variant
    },
    confirmIcon() {
      if (this.variant === 'danger') return 'trash'
      return null
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
        this.$emit('update:modelValue', false)
      }
    }
  }
}
</script>

<style scoped>
.confirm-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: var(--spacing-2) 0;
}

.confirm-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  border-radius: var(--radius-full);
  margin-bottom: var(--spacing-4);
}

.confirm-icon--danger {
  background: var(--color-error-100);
  color: var(--color-error-600);
}

.confirm-icon--warning {
  background: var(--color-warning-100);
  color: var(--color-warning-600);
}

.confirm-icon--info {
  background: var(--color-info-100);
  color: var(--color-info-600);
}

.confirm-icon--primary {
  background: var(--color-primary-100);
  color: var(--color-primary-600);
}

.confirm-message {
  margin: 0;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: var(--line-height-relaxed);
  max-width: 320px;
}
</style>
