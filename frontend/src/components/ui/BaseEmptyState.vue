<template>
  <div :class="['empty-state', `empty-${size}`, { 'empty-compact': compact }]">
    <div v-if="icon || $slots.icon" class="empty-icon-wrapper">
      <slot name="icon">
        <div :class="['empty-icon-bg', `icon-${variant}`]">
          <BaseIcon :name="icon" :size="iconSize" />
        </div>
      </slot>
    </div>

    <div class="empty-content">
      <h3 v-if="title" class="empty-title">{{ title }}</h3>
      <p v-if="description || $slots.description" class="empty-description">
        <slot name="description">{{ description }}</slot>
      </p>
    </div>

    <div v-if="$slots.default || actionLabel" class="empty-actions">
      <slot>
        <BaseButton
          v-if="actionLabel"
          :variant="actionVariant"
          :icon="actionIcon"
          @click="$emit('action')"
        >
          {{ actionLabel }}
        </BaseButton>
      </slot>
    </div>

    <div v-if="$slots.footer" class="empty-footer">
      <slot name="footer" />
    </div>
  </div>
</template>

<script>
import BaseIcon from './BaseIcon.vue'
import BaseButton from './BaseButton.vue'

export default {
  name: 'BaseEmptyState',
  components: { BaseIcon, BaseButton },
  props: {
    icon: {
      type: String,
      default: ''
    },
    title: {
      type: String,
      default: ''
    },
    description: {
      type: String,
      default: ''
    },
    actionLabel: {
      type: String,
      default: ''
    },
    actionIcon: {
      type: String,
      default: 'plus'
    },
    actionVariant: {
      type: String,
      default: 'primary'
    },
    variant: {
      type: String,
      default: 'default',
      validator: (v) => ['default', 'primary', 'success', 'warning', 'error', 'info'].includes(v)
    },
    size: {
      type: String,
      default: 'md',
      validator: (v) => ['sm', 'md', 'lg'].includes(v)
    },
    compact: {
      type: Boolean,
      default: false
    }
  },
  emits: ['action'],
  computed: {
    iconSize() {
      return this.size === 'sm' ? 24 : this.size === 'lg' ? 40 : 32
    }
  }
}
</script>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: var(--spacing-8);
  background: var(--color-surface);
  border-radius: var(--radius-xl);
}

/* Sizes */
.empty-sm {
  padding: var(--spacing-6);
}

.empty-sm .empty-title {
  font-size: var(--font-size-md);
}

.empty-sm .empty-description {
  font-size: var(--font-size-xs);
}

.empty-lg {
  padding: var(--spacing-12);
}

.empty-lg .empty-title {
  font-size: var(--font-size-2xl);
}

.empty-lg .empty-description {
  font-size: var(--font-size-md);
  max-width: 500px;
}

/* Compact mode */
.empty-compact {
  padding: var(--spacing-4);
  background: var(--color-gray-50);
  border-radius: var(--radius-lg);
}

.empty-compact .empty-icon-wrapper {
  margin-bottom: var(--spacing-3);
}

.empty-compact .empty-icon-bg {
  width: 48px;
  height: 48px;
}

.empty-compact .empty-title {
  font-size: var(--font-size-sm);
  margin-bottom: var(--spacing-1);
}

.empty-compact .empty-description {
  font-size: var(--font-size-xs);
  margin-bottom: var(--spacing-3);
}

/* Icon */
.empty-icon-wrapper {
  margin-bottom: var(--spacing-5);
}

.empty-icon-bg {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 72px;
  height: 72px;
  border-radius: var(--radius-full);
  transition: all var(--transition-base);
}

/* Icon variants */
.icon-default {
  background: var(--color-gray-200);
  color: var(--color-gray-600);
}

.icon-primary {
  background: var(--color-primary-200);
  color: var(--color-primary-600);
}

.icon-success {
  background: var(--color-success-200);
  color: var(--color-success-600);
}

.icon-warning {
  background: var(--color-warning-200);
  color: var(--color-warning-600);
}

.icon-error {
  background: var(--color-error-200);
  color: var(--color-error-600);
}

.icon-info {
  background: var(--color-info-200);
  color: var(--color-info-600);
}

/* Content */
.empty-content {
  margin-bottom: var(--spacing-5);
}

.empty-title {
  margin: 0 0 var(--spacing-2);
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  line-height: var(--line-height-tight);
}

.empty-description {
  margin: 0;
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
  line-height: var(--line-height-relaxed);
  max-width: 400px;
}

/* Actions */
.empty-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  flex-wrap: wrap;
  justify-content: center;
}

/* Footer */
.empty-footer {
  margin-top: var(--spacing-6);
  padding-top: var(--spacing-6);
  border-top: 1px solid var(--color-border-light);
  width: 100%;
}
</style>
