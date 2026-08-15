<template>
  <button
    :class="[
      'base-button',
      `btn-${variant}`,
      `btn-${size}`,
      {
        'btn-loading': loading,
        'btn-block': block,
        'btn-icon-only': iconOnly
      }
    ]"
    :disabled="disabled || loading"
    :type="type"
    @click="handleClick"
  >
    <span v-if="loading" class="btn-spinner">
      <BaseIcon name="loader" :size="spinnerSize" spin />
    </span>
    <span class="btn-content" :class="{ 'sr-only': loading && !showTextWhileLoading }">
      <BaseIcon v-if="icon && iconPosition === 'left'" :name="icon" :size="iconSize" class="btn-icon btn-icon-left" />
      <slot />
      <BaseIcon v-if="icon && iconPosition === 'right'" :name="icon" :size="iconSize" class="btn-icon btn-icon-right" />
    </span>
  </button>
</template>

<script>
import BaseIcon from './BaseIcon.vue'

export default {
  name: 'BaseButton',
  components: { BaseIcon },
  props: {
    variant: {
      type: String,
      default: 'primary',
      validator: (v) => ['primary', 'secondary', 'outline', 'ghost', 'danger', 'success', 'warning'].includes(v)
    },
    size: {
      type: String,
      default: 'md',
      validator: (v) => ['sm', 'md', 'lg'].includes(v)
    },
    type: {
      type: String,
      default: 'button'
    },
    disabled: {
      type: Boolean,
      default: false
    },
    loading: {
      type: Boolean,
      default: false
    },
    block: {
      type: Boolean,
      default: false
    },
    icon: {
      type: String,
      default: ''
    },
    iconPosition: {
      type: String,
      default: 'left',
      validator: (v) => ['left', 'right'].includes(v)
    },
    iconOnly: {
      type: Boolean,
      default: false
    },
    showTextWhileLoading: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    iconSize() {
      return this.size === 'sm' ? 14 : this.size === 'lg' ? 20 : 16
    },
    spinnerSize() {
      return this.size === 'sm' ? 14 : this.size === 'lg' ? 20 : 16
    }
  },
  methods: {
    handleClick(e) {
      if (!this.disabled && !this.loading) {
        this.$emit('click', e)
      }
    }
  }
}
</script>

<style scoped>
.base-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-2);
  font-family: var(--font-family-base);
  font-weight: var(--font-weight-medium);
  border: var(--border-width-thin) solid transparent;
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-fast);
  white-space: nowrap;
  text-decoration: none;
  position: relative;
  overflow: hidden;
}

.base-button:focus-visible {
  outline: 2px solid var(--color-primary-500);
  outline-offset: 2px;
}

.base-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: none;
}

/* Sizes */
.btn-sm {
  height: var(--button-height-sm);
  padding: 0 var(--spacing-3);
  font-size: var(--font-size-xs);
  border-radius: var(--radius-md);
}

.btn-md {
  height: var(--button-height-md);
  padding: 0 var(--spacing-4);
  font-size: var(--font-size-sm);
}

.btn-lg {
  height: var(--button-height-lg);
  padding: 0 var(--spacing-6);
  font-size: var(--font-size-base);
  border-radius: var(--radius-xl);
}

/* Icon only buttons */
.btn-icon-only.btn-sm {
  width: var(--button-height-sm);
  padding: 0;
}

.btn-icon-only.btn-md {
  width: var(--button-height-md);
  padding: 0;
}

.btn-icon-only.btn-lg {
  width: var(--button-height-lg);
  padding: 0;
}

/* Block button */
.btn-block {
  width: 100%;
}

/* Variants */
.btn-primary {
  background: var(--color-primary-500);
  color: var(--color-text-inverse);
}

.btn-primary:hover:not(:disabled) {
  background: var(--color-primary-600);
  transform: translateY(-1px);
  box-shadow: var(--shadow-primary);
}

.btn-primary:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: none;
}

.btn-secondary {
  background: var(--color-gray-100);
  color: var(--color-text-primary);
}

.btn-secondary:hover:not(:disabled) {
  background: var(--color-gray-200);
}

.btn-outline {
  background: transparent;
  border-color: var(--color-border);
  color: var(--color-text-primary);
}

.btn-outline:hover:not(:disabled) {
  background: var(--color-gray-50);
  border-color: var(--color-gray-300);
}

.btn-ghost {
  background: transparent;
  color: var(--color-text-secondary);
}

.btn-ghost:hover:not(:disabled) {
  background: var(--color-gray-100);
  color: var(--color-text-primary);
}

.btn-danger {
  background: var(--color-error-500);
  color: var(--color-text-inverse);
}

.btn-danger:hover:not(:disabled) {
  background: var(--color-error-600);
  transform: translateY(-1px);
  box-shadow: var(--shadow-error);
}

.btn-danger:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: none;
}

.btn-success {
  background: var(--color-success-500);
  color: var(--color-text-inverse);
}

.btn-success:hover:not(:disabled) {
  background: var(--color-success-600);
  transform: translateY(-1px);
  box-shadow: var(--shadow-success);
}

.btn-success:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: none;
}

.btn-warning {
  background: var(--color-warning-500);
  color: var(--color-text-primary);
}

.btn-warning:hover:not(:disabled) {
  background: var(--color-warning-600);
}

/* Loading state */
.btn-loading .btn-content {
  opacity: 0;
}

.btn-spinner {
  position: absolute;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Button content */
.btn-content {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.btn-icon-left {
  margin-right: var(--spacing-1);
}

.btn-icon-right {
  margin-left: var(--spacing-1);
}

/* Screen reader only */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
</style>
