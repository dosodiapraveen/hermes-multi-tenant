<template>
  <component
    :is="clickable ? 'button' : 'div'"
    :class="[
      'base-card',
      `card-${variant}`,
      {
        'card-clickable': clickable,
        'card-selected': selected,
        'card-loading': loading,
        'no-padding': noPadding
      }
    ]"
    :disabled="disabled"
    @click="handleClick"
  >
    <!-- Loading overlay -->
    <div v-if="loading" class="card-loading-overlay">
      <BaseIcon name="loader" :size="24" spin />
    </div>

    <!-- Header -->
    <div v-if="$slots.header || title" class="card-header">
      <slot name="header">
        <div class="card-header-content">
          <BaseIcon v-if="icon" :name="icon" :size="20" class="card-icon" />
          <div class="card-header-text">
            <h3 class="card-title">{{ title }}</h3>
            <p v-if="subtitle" class="card-subtitle">{{ subtitle }}</p>
          </div>
        </div>
        <div v-if="$slots.actions" class="card-actions">
          <slot name="actions" />
        </div>
      </slot>
    </div>

    <!-- Body -->
    <div class="card-body">
      <slot />
    </div>

    <!-- Footer -->
    <div v-if="$slots.footer" class="card-footer">
      <slot name="footer" />
    </div>

    <!-- Badge -->
    <span v-if="badge" :class="['card-badge', `badge-${badgeVariant}`]">
      {{ badge }}
    </span>
  </component>
</template>

<script>
import BaseIcon from './BaseIcon.vue'

export default {
  name: 'BaseCard',
  components: { BaseIcon },
  props: {
    title: {
      type: String,
      default: ''
    },
    subtitle: {
      type: String,
      default: ''
    },
    icon: {
      type: String,
      default: ''
    },
    variant: {
      type: String,
      default: 'default',
      validator: (v) => ['default', 'outlined', 'elevated', 'flat'].includes(v)
    },
    clickable: {
      type: Boolean,
      default: false
    },
    selected: {
      type: Boolean,
      default: false
    },
    disabled: {
      type: Boolean,
      default: false
    },
    loading: {
      type: Boolean,
      default: false
    },
    noPadding: {
      type: Boolean,
      default: false
    },
    badge: {
      type: [String, Number],
      default: ''
    },
    badgeVariant: {
      type: String,
      default: 'primary',
      validator: (v) => ['primary', 'success', 'warning', 'error', 'info'].includes(v)
    }
  },
  emits: ['click'],
  methods: {
    handleClick(e) {
      if (this.clickable && !this.disabled && !this.loading) {
        this.$emit('click', e)
      }
    }
  }
}
</script>

<style scoped>
.base-card {
  position: relative;
  display: flex;
  flex-direction: column;
  background: var(--color-surface);
  border-radius: var(--card-radius);
  overflow: hidden;
  transition: all var(--transition-fast);
  text-align: left;
  width: 100%;
  font-family: var(--font-family-base);
}

/* Variants */
.card-default {
  box-shadow: var(--card-shadow);
  border: 1px solid var(--color-border-light);
}

.card-outlined {
  box-shadow: none;
  border: var(--border-width-medium) solid var(--color-border);
}

.card-elevated {
  box-shadow: var(--shadow-md);
  border: none;
}

.card-flat {
  box-shadow: none;
  border: none;
  background: var(--color-gray-50);
}

/* Clickable state */
.card-clickable {
  cursor: pointer;
  border: none;
  -webkit-appearance: none;
  appearance: none;
}

.card-clickable:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: var(--card-shadow-hover);
}

.card-clickable:active:not(:disabled) {
  transform: translateY(0);
}

.card-clickable:focus-visible {
  outline: 2px solid var(--color-primary-500);
  outline-offset: 2px;
}

.card-clickable:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Selected state */
.card-selected {
  border-color: var(--color-primary-500);
  box-shadow: 0 0 0 2px var(--color-primary-100);
}

/* Loading state */
.card-loading {
  pointer-events: none;
}

.card-loading-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.8);
  z-index: 1;
  color: var(--color-primary-500);
}

/* Header */
.card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--spacing-3);
  padding: var(--card-padding);
  border-bottom: 1px solid var(--color-border-light);
}

.card-header-content {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-3);
  min-width: 0;
  flex: 1;
}

.card-icon {
  flex-shrink: 0;
  color: var(--color-primary-500);
  margin-top: 2px;
}

.card-header-text {
  min-width: 0;
}

.card-title {
  margin: 0;
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  line-height: var(--line-height-tight);
}

.card-subtitle {
  margin: var(--spacing-1) 0 0;
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
  line-height: var(--line-height-normal);
}

.card-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  flex-shrink: 0;
}

/* Body */
.card-body {
  flex: 1;
  padding: var(--card-padding);
}

.no-padding .card-body {
  padding: 0;
}

/* Footer */
.card-footer {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  padding: var(--spacing-4) var(--card-padding);
  border-top: 1px solid var(--color-border-light);
  background: var(--color-gray-50);
}

/* Badge */
.card-badge {
  position: absolute;
  top: var(--spacing-3);
  right: var(--spacing-3);
  padding: var(--spacing-1) var(--spacing-2);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  border-radius: var(--radius-full);
  line-height: 1;
}

.badge-primary {
  background: var(--color-primary-200);
  color: var(--color-primary-700);
}

.badge-success {
  background: var(--color-success-200);
  color: var(--color-success-700);
}

.badge-warning {
  background: var(--color-warning-200);
  color: var(--color-warning-700);
}

.badge-error {
  background: var(--color-error-200);
  color: var(--color-error-700);
}

.badge-info {
  background: var(--color-info-200);
  color: var(--color-info-700);
}
</style>
