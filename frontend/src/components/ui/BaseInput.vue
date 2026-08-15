<template>
  <div :class="['base-input-wrapper', { 'has-error': error, 'is-disabled': disabled, 'is-focused': focused }]">
    <label v-if="label" :for="inputId" class="input-label">
      {{ label }}
      <span v-if="required" class="required-mark">*</span>
    </label>

    <div class="input-container">
      <span v-if="$slots.prefix || prefixIcon" class="input-prefix">
        <slot name="prefix">
          <BaseIcon v-if="prefixIcon" :name="prefixIcon" :size="16" />
        </slot>
      </span>

      <input
        v-if="type !== 'textarea'"
        :id="inputId"
        ref="input"
        :type="computedType"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :readonly="readonly"
        :required="required"
        :autocomplete="autocomplete"
        :class="['base-input', { 'has-prefix': $slots.prefix || prefixIcon, 'has-suffix': $slots.suffix || suffixIcon || showPasswordToggle || clearable }]"
        @input="handleInput"
        @focus="handleFocus"
        @blur="handleBlur"
        @keydown="$emit('keydown', $event)"
        @keyup.enter="$emit('enter', $event)"
      />

      <textarea
        v-else
        :id="inputId"
        ref="input"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :readonly="readonly"
        :required="required"
        :rows="rows"
        :class="['base-input', 'base-textarea', { 'has-prefix': $slots.prefix || prefixIcon }]"
        @input="handleInput"
        @focus="handleFocus"
        @blur="handleBlur"
        @keydown="$emit('keydown', $event)"
      ></textarea>

      <span v-if="$slots.suffix || suffixIcon || showPasswordToggle || (clearable && modelValue)" class="input-suffix">
        <button
          v-if="clearable && modelValue && !disabled"
          type="button"
          class="clear-btn"
          tabindex="-1"
          @click="clearInput"
        >
          <BaseIcon name="x" :size="14" />
        </button>

        <button
          v-if="showPasswordToggle && type === 'password'"
          type="button"
          class="toggle-password-btn"
          tabindex="-1"
          @click="togglePassword"
        >
          <BaseIcon :name="passwordVisible ? 'eye-off' : 'eye'" :size="16" />
        </button>

        <slot name="suffix">
          <BaseIcon v-if="suffixIcon && !showPasswordToggle" :name="suffixIcon" :size="16" />
        </slot>
      </span>
    </div>

    <!-- Password strength indicator -->
    <div v-if="showStrength && type === 'password' && modelValue" class="password-strength">
      <div class="strength-bars">
        <div
          v-for="i in 4"
          :key="i"
          :class="['strength-bar', { active: i <= strengthLevel }]"
          :style="{ backgroundColor: i <= strengthLevel ? strengthColor : '' }"
        ></div>
      </div>
      <span class="strength-text" :style="{ color: strengthColor }">{{ strengthText }}</span>
    </div>

    <p v-if="error" class="input-error">
      <BaseIcon name="alert-circle" :size="14" />
      {{ error }}
    </p>

    <p v-else-if="hint" class="input-hint">{{ hint }}</p>

    <p v-if="showCharCount && maxlength" class="char-count" :class="{ 'near-limit': charCountPercentage > 80 }">
      {{ modelValue?.length || 0 }} / {{ maxlength }}
    </p>
  </div>
</template>

<script>
import BaseIcon from './BaseIcon.vue'

let inputIdCounter = 0

export default {
  name: 'BaseInput',
  components: { BaseIcon },
  props: {
    modelValue: {
      type: [String, Number],
      default: ''
    },
    type: {
      type: String,
      default: 'text'
    },
    label: {
      type: String,
      default: ''
    },
    placeholder: {
      type: String,
      default: ''
    },
    hint: {
      type: String,
      default: ''
    },
    error: {
      type: String,
      default: ''
    },
    disabled: {
      type: Boolean,
      default: false
    },
    readonly: {
      type: Boolean,
      default: false
    },
    required: {
      type: Boolean,
      default: false
    },
    autocomplete: {
      type: String,
      default: 'off'
    },
    prefixIcon: {
      type: String,
      default: ''
    },
    suffixIcon: {
      type: String,
      default: ''
    },
    clearable: {
      type: Boolean,
      default: false
    },
    showPasswordToggle: {
      type: Boolean,
      default: false
    },
    showStrength: {
      type: Boolean,
      default: false
    },
    rows: {
      type: [Number, String],
      default: 4
    },
    maxlength: {
      type: [Number, String],
      default: null
    },
    showCharCount: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:modelValue', 'focus', 'blur', 'keydown', 'enter', 'clear'],
  data() {
    return {
      focused: false,
      passwordVisible: false,
      inputId: `input-${++inputIdCounter}`
    }
  },
  computed: {
    computedType() {
      if (this.type === 'password' && this.passwordVisible) {
        return 'text'
      }
      return this.type
    },
    strengthLevel() {
      const password = String(this.modelValue || '')
      if (password.length === 0) return 0

      let score = 0
      if (password.length >= 8) score++
      if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score++
      if (/\d/.test(password)) score++
      if (/[^a-zA-Z0-9]/.test(password)) score++

      return score
    },
    strengthText() {
      const texts = ['', 'Weak', 'Fair', 'Good', 'Strong']
      return texts[this.strengthLevel]
    },
    strengthColor() {
      const colors = ['', 'var(--color-error-500)', 'var(--color-warning-500)', 'var(--color-info-500)', 'var(--color-success-500)']
      return colors[this.strengthLevel]
    },
    charCountPercentage() {
      if (!this.maxlength) return 0
      return ((this.modelValue?.length || 0) / this.maxlength) * 100
    }
  },
  methods: {
    handleInput(e) {
      this.$emit('update:modelValue', e.target.value)
    },
    handleFocus(e) {
      this.focused = true
      this.$emit('focus', e)
    },
    handleBlur(e) {
      this.focused = false
      this.$emit('blur', e)
    },
    clearInput() {
      this.$emit('update:modelValue', '')
      this.$emit('clear')
      this.$refs.input?.focus()
    },
    togglePassword() {
      this.passwordVisible = !this.passwordVisible
    },
    focus() {
      this.$refs.input?.focus()
    },
    blur() {
      this.$refs.input?.blur()
    }
  }
}
</script>

<style scoped>
.base-input-wrapper {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-1);
  width: 100%;
}

.input-label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-1);
}

.required-mark {
  color: var(--color-error-500);
  margin-left: 2px;
}

.input-container {
  position: relative;
  display: flex;
  align-items: center;
}

.base-input {
  width: 100%;
  height: var(--input-height-md);
  padding: 0 var(--spacing-3);
  font-family: var(--font-family-base);
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
  background: var(--input-background);
  border: var(--border-width-medium) solid var(--input-border-color);
  border-radius: var(--radius-lg);
  transition: all var(--transition-fast);
}

.base-input::placeholder {
  color: var(--input-placeholder);
}

.base-input:hover:not(:disabled):not(:focus) {
  border-color: var(--color-gray-400);
}

.base-input:focus {
  outline: none;
  border-color: var(--input-border-color-focus);
  box-shadow: 0 0 0 3px var(--color-primary-100);
}

.base-input:disabled {
  background: var(--color-gray-100);
  cursor: not-allowed;
  opacity: 0.7;
}

.base-input.has-prefix {
  padding-left: var(--spacing-10);
}

.base-input.has-suffix {
  padding-right: var(--spacing-10);
}

/* Textarea */
.base-textarea {
  height: auto;
  min-height: 100px;
  padding: var(--spacing-3);
  resize: vertical;
  line-height: var(--line-height-normal);
}

/* Prefix & Suffix */
.input-prefix,
.input-suffix {
  position: absolute;
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
  color: var(--color-text-tertiary);
  pointer-events: none;
}

.input-prefix {
  left: var(--spacing-3);
}

.input-suffix {
  right: var(--spacing-3);
  pointer-events: auto;
}

.clear-btn,
.toggle-password-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  padding: 0;
  background: transparent;
  border: none;
  border-radius: var(--radius-sm);
  color: var(--color-text-tertiary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.clear-btn:hover,
.toggle-password-btn:hover {
  color: var(--color-text-secondary);
  background: var(--color-gray-100);
}

/* Password Strength */
.password-strength {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  margin-top: var(--spacing-2);
}

.strength-bars {
  display: flex;
  gap: 4px;
}

.strength-bar {
  width: 32px;
  height: 4px;
  background: var(--color-gray-200);
  border-radius: var(--radius-full);
  transition: background-color var(--transition-fast);
}

.strength-bar.active {
  background: var(--color-gray-400);
}

.strength-text {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
}

/* Error state */
.has-error .base-input {
  border-color: var(--color-error-500);
}

.has-error .base-input:focus {
  box-shadow: 0 0 0 3px var(--color-error-100);
}

.input-error {
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
  margin: var(--spacing-1) 0 0;
  font-size: var(--font-size-xs);
  color: var(--color-error-600);
}

.input-hint {
  margin: var(--spacing-1) 0 0;
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

/* Character count */
.char-count {
  margin: var(--spacing-1) 0 0;
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
  text-align: right;
}

.char-count.near-limit {
  color: var(--color-warning-600);
}
</style>
