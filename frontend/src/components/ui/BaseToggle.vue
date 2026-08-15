<template>
  <label :class="['base-toggle', `toggle-${size}`, { disabled, checked: modelValue }]">
    <input
      type="checkbox"
      :checked="modelValue"
      :disabled="disabled"
      class="toggle-input"
      @change="handleChange"
    />
    <span class="toggle-track">
      <span class="toggle-thumb">
        <BaseIcon v-if="showIcons && modelValue" name="check" :size="iconSize" class="thumb-icon" />
        <BaseIcon v-else-if="showIcons" name="x" :size="iconSize" class="thumb-icon" />
      </span>
    </span>
    <span v-if="label || $slots.default" class="toggle-label">
      <slot>{{ label }}</slot>
    </span>
  </label>
</template>

<script>
import BaseIcon from './BaseIcon.vue'

export default {
  name: 'BaseToggle',
  components: { BaseIcon },
  props: {
    modelValue: {
      type: Boolean,
      default: false
    },
    label: {
      type: String,
      default: ''
    },
    disabled: {
      type: Boolean,
      default: false
    },
    size: {
      type: String,
      default: 'md',
      validator: (v) => ['sm', 'md', 'lg'].includes(v)
    },
    showIcons: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:modelValue', 'change'],
  computed: {
    iconSize() {
      return this.size === 'sm' ? 8 : this.size === 'lg' ? 12 : 10
    }
  },
  methods: {
    handleChange(e) {
      if (!this.disabled) {
        this.$emit('update:modelValue', e.target.checked)
        this.$emit('change', e.target.checked)
      }
    }
  }
}
</script>

<style scoped>
.base-toggle {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-3);
  cursor: pointer;
  user-select: none;
}

.base-toggle.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.toggle-input {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-track {
  position: relative;
  display: inline-flex;
  align-items: center;
  background: var(--color-gray-300);
  border-radius: var(--radius-full);
  transition: all var(--transition-fast);
  flex-shrink: 0;
}

.base-toggle.checked .toggle-track {
  background: var(--color-primary-500);
}

.toggle-thumb {
  position: absolute;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-surface);
  border-radius: var(--radius-full);
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-fast);
}

.base-toggle.checked .toggle-thumb {
  background: var(--color-surface);
}

.thumb-icon {
  color: var(--color-gray-400);
}

.base-toggle.checked .thumb-icon {
  color: var(--color-primary-500);
}

/* Sizes */
.toggle-sm .toggle-track {
  width: 32px;
  height: 18px;
}

.toggle-sm .toggle-thumb {
  width: 14px;
  height: 14px;
  left: 2px;
}

.toggle-sm.checked .toggle-thumb {
  transform: translateX(14px);
}

.toggle-md .toggle-track {
  width: 44px;
  height: 24px;
}

.toggle-md .toggle-thumb {
  width: 20px;
  height: 20px;
  left: 2px;
}

.toggle-md.checked .toggle-thumb {
  transform: translateX(20px);
}

.toggle-lg .toggle-track {
  width: 56px;
  height: 30px;
}

.toggle-lg .toggle-thumb {
  width: 26px;
  height: 26px;
  left: 2px;
}

.toggle-lg.checked .toggle-thumb {
  transform: translateX(26px);
}

/* Label */
.toggle-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
  line-height: 1.4;
}

/* Focus state */
.toggle-input:focus-visible + .toggle-track {
  box-shadow: 0 0 0 3px var(--color-primary-100);
}

/* Hover state */
.base-toggle:not(.disabled):hover .toggle-track {
  background: var(--color-gray-400);
}

.base-toggle.checked:not(.disabled):hover .toggle-track {
  background: var(--color-primary-600);
}
</style>
