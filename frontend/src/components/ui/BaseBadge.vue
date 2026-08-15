<template>
  <span
    :class="[
      'base-badge',
      `badge-${variant}`,
      `badge-${size}`,
      { 'badge-pill': pill, 'badge-dot': dot }
    ]"
  >
    <span v-if="dot" class="badge-dot-indicator"></span>
    <BaseIcon v-if="icon && !dot" :name="icon" :size="iconSize" class="badge-icon" />
    <span v-if="!dot" class="badge-text"><slot>{{ label }}</slot></span>
    <button
      v-if="removable && !dot"
      type="button"
      class="badge-remove"
      aria-label="Remove"
      @click.stop="$emit('remove')"
    >
      <BaseIcon name="x" :size="removeIconSize" />
    </button>
  </span>
</template>

<script>
import BaseIcon from './BaseIcon.vue'

export default {
  name: 'BaseBadge',
  components: { BaseIcon },
  props: {
    label: {
      type: [String, Number],
      default: ''
    },
    variant: {
      type: String,
      default: 'default',
      validator: (v) => [
        'default', 'primary', 'secondary', 'success', 'warning', 'error', 'info',
        'brainstorm', 'developing', 'ready', 'archived', 'active', 'paused', 'done'
      ].includes(v)
    },
    size: {
      type: String,
      default: 'md',
      validator: (v) => ['sm', 'md', 'lg'].includes(v)
    },
    pill: {
      type: Boolean,
      default: false
    },
    dot: {
      type: Boolean,
      default: false
    },
    icon: {
      type: String,
      default: ''
    },
    removable: {
      type: Boolean,
      default: false
    }
  },
  emits: ['remove'],
  computed: {
    iconSize() {
      return this.size === 'sm' ? 10 : this.size === 'lg' ? 14 : 12
    },
    removeIconSize() {
      return this.size === 'sm' ? 10 : this.size === 'lg' ? 14 : 12
    }
  }
}
</script>

<style scoped>
.base-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-1);
  font-family: var(--font-family-base);
  font-weight: var(--font-weight-medium);
  line-height: 1;
  border-radius: var(--radius-md);
  white-space: nowrap;
  transition: all var(--transition-fast);
}

/* Sizes */
.badge-sm {
  padding: 2px 6px;
  font-size: 10px;
}

.badge-md {
  padding: 4px 10px;
  font-size: var(--font-size-xs);
}

.badge-lg {
  padding: 6px 12px;
  font-size: var(--font-size-sm);
}

/* Pill shape */
.badge-pill {
  border-radius: var(--radius-full);
}

/* Variants */
.badge-default {
  background: var(--color-gray-200);
  color: var(--color-gray-700);
}

.badge-primary {
  background: var(--color-primary-200);
  color: var(--color-primary-700);
}

.badge-secondary {
  background: var(--color-gray-200);
  color: var(--color-gray-800);
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

/* Status variants for ideas/projects */
.badge-brainstorm {
  background: var(--color-info-200);
  color: var(--color-info-700);
}

.badge-developing {
  background: var(--color-primary-200);
  color: var(--color-primary-700);
}

.badge-ready {
  background: var(--color-success-200);
  color: var(--color-success-700);
}

.badge-archived {
  background: var(--color-gray-200);
  color: var(--color-gray-600);
}

.badge-active {
  background: var(--color-success-200);
  color: var(--color-success-700);
}

.badge-paused {
  background: var(--color-warning-200);
  color: var(--color-warning-700);
}

.badge-done {
  background: var(--color-info-200);
  color: var(--color-info-700);
}

/* Dot badge */
.badge-dot {
  padding: 0;
  background: none !important;
  gap: var(--spacing-2);
}

.badge-dot-indicator {
  width: 8px;
  height: 8px;
  border-radius: var(--radius-full);
  background: currentColor;
  flex-shrink: 0;
}

.badge-dot.badge-default .badge-dot-indicator { background: var(--color-gray-400); }
.badge-dot.badge-primary .badge-dot-indicator { background: var(--color-primary-500); }
.badge-dot.badge-success .badge-dot-indicator { background: var(--color-success-500); }
.badge-dot.badge-warning .badge-dot-indicator { background: var(--color-warning-500); }
.badge-dot.badge-error .badge-dot-indicator { background: var(--color-error-500); }
.badge-dot.badge-info .badge-dot-indicator { background: var(--color-info-500); }

/* Icon */
.badge-icon {
  flex-shrink: 0;
}

/* Remove button */
.badge-remove {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  margin-left: 2px;
  margin-right: -4px;
  background: transparent;
  border: none;
  border-radius: var(--radius-sm);
  color: inherit;
  opacity: 0.6;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.badge-remove:hover {
  opacity: 1;
  background: rgba(0, 0, 0, 0.1);
}

.badge-text {
  display: inline-block;
}
</style>
