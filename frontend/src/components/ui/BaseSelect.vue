<template>
  <div :class="['base-select-wrapper', { 'has-error': error, 'is-disabled': disabled, 'is-open': isOpen }]">
    <label v-if="label" :for="selectId" class="select-label">
      {{ label }}
      <span v-if="required" class="required-mark">*</span>
    </label>

    <div class="select-container" ref="selectContainer">
      <button
        :id="selectId"
        type="button"
        class="select-trigger"
        :disabled="disabled"
        :aria-expanded="isOpen"
        :aria-haspopup="true"
        @click="toggleDropdown"
        @keydown.down.prevent="openDropdown"
        @keydown.up.prevent="openDropdown"
        @keydown.escape="closeDropdown"
      >
        <span v-if="prefixIcon" class="select-prefix">
          <BaseIcon :name="prefixIcon" :size="16" />
        </span>
        <span class="select-value" :class="{ placeholder: !hasSelection }">
          <template v-if="hasSelection">
            <BaseIcon v-if="selectedOption?.icon" :name="selectedOption.icon" :size="16" class="option-icon" />
            {{ selectedOption?.label || modelValue }}
          </template>
          <template v-else>{{ placeholder }}</template>
        </span>
        <span class="select-arrow">
          <BaseIcon :name="isOpen ? 'chevron-up' : 'chevron-down'" :size="16" />
        </span>
      </button>

      <Transition name="dropdown">
        <div v-if="isOpen" class="select-dropdown" role="listbox">
          <div v-if="searchable" class="select-search">
            <BaseIcon name="search" :size="16" class="search-icon" />
            <input
              ref="searchInput"
              v-model="searchQuery"
              type="text"
              class="search-input"
              placeholder="Search..."
              @keydown.down.prevent="focusNextOption"
              @keydown.up.prevent="focusPrevOption"
              @keydown.enter.prevent="selectFocusedOption"
              @keydown.escape="closeDropdown"
            />
          </div>

          <div class="select-options" ref="optionsList">
            <div v-if="filteredOptions.length === 0" class="select-empty">
              No options found
            </div>
            <button
              v-for="(option, index) in filteredOptions"
              :key="option.value"
              type="button"
              :class="['select-option', { selected: isSelected(option), focused: focusedIndex === index, disabled: option.disabled }]"
              :disabled="option.disabled"
              role="option"
              :aria-selected="isSelected(option)"
              @click="selectOption(option)"
              @mouseenter="focusedIndex = index"
            >
              <BaseIcon v-if="option.icon" :name="option.icon" :size="16" class="option-icon" />
              <span class="option-label">{{ option.label }}</span>
              <span v-if="option.description" class="option-description">{{ option.description }}</span>
              <BaseIcon v-if="isSelected(option)" name="check" :size="16" class="option-check" />
            </button>
          </div>
        </div>
      </Transition>
    </div>

    <p v-if="error" class="select-error">
      <BaseIcon name="alert-circle" :size="14" />
      {{ error }}
    </p>

    <p v-else-if="hint" class="select-hint">{{ hint }}</p>
  </div>
</template>

<script>
import BaseIcon from './BaseIcon.vue'

let selectIdCounter = 0

export default {
  name: 'BaseSelect',
  components: { BaseIcon },
  props: {
    modelValue: {
      type: [String, Number, Object],
      default: ''
    },
    options: {
      type: Array,
      required: true,
      validator: (options) => {
        return options.every(opt =>
          typeof opt === 'object' && 'value' in opt && 'label' in opt
        )
      }
    },
    label: {
      type: String,
      default: ''
    },
    placeholder: {
      type: String,
      default: 'Select an option'
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
    required: {
      type: Boolean,
      default: false
    },
    searchable: {
      type: Boolean,
      default: false
    },
    prefixIcon: {
      type: String,
      default: ''
    }
  },
  emits: ['update:modelValue', 'change'],
  data() {
    return {
      isOpen: false,
      searchQuery: '',
      focusedIndex: -1,
      selectId: `select-${++selectIdCounter}`
    }
  },
  computed: {
    hasSelection() {
      return this.modelValue !== '' && this.modelValue !== null && this.modelValue !== undefined
    },
    selectedOption() {
      return this.options.find(opt => opt.value === this.modelValue)
    },
    filteredOptions() {
      if (!this.searchQuery) return this.options
      const query = this.searchQuery.toLowerCase()
      return this.options.filter(opt =>
        opt.label.toLowerCase().includes(query) ||
        (opt.description && opt.description.toLowerCase().includes(query))
      )
    }
  },
  methods: {
    toggleDropdown() {
      if (this.disabled) return
      this.isOpen ? this.closeDropdown() : this.openDropdown()
    },
    openDropdown() {
      if (this.disabled) return
      this.isOpen = true
      this.focusedIndex = this.options.findIndex(opt => opt.value === this.modelValue)
      this.$nextTick(() => {
        if (this.searchable) {
          this.$refs.searchInput?.focus()
        }
        this.addClickOutsideListener()
      })
    },
    closeDropdown() {
      this.isOpen = false
      this.searchQuery = ''
      this.focusedIndex = -1
      this.removeClickOutsideListener()
    },
    selectOption(option) {
      if (option.disabled) return
      this.$emit('update:modelValue', option.value)
      this.$emit('change', option)
      this.closeDropdown()
    },
    isSelected(option) {
      return option.value === this.modelValue
    },
    focusNextOption() {
      if (this.focusedIndex < this.filteredOptions.length - 1) {
        this.focusedIndex++
        this.scrollToFocused()
      }
    },
    focusPrevOption() {
      if (this.focusedIndex > 0) {
        this.focusedIndex--
        this.scrollToFocused()
      }
    },
    selectFocusedOption() {
      if (this.focusedIndex >= 0 && this.focusedIndex < this.filteredOptions.length) {
        this.selectOption(this.filteredOptions[this.focusedIndex])
      }
    },
    scrollToFocused() {
      this.$nextTick(() => {
        const options = this.$refs.optionsList?.querySelectorAll('.select-option')
        options?.[this.focusedIndex]?.scrollIntoView({ block: 'nearest' })
      })
    },
    handleClickOutside(event) {
      if (this.$refs.selectContainer && !this.$refs.selectContainer.contains(event.target)) {
        this.closeDropdown()
      }
    },
    addClickOutsideListener() {
      document.addEventListener('click', this.handleClickOutside)
    },
    removeClickOutsideListener() {
      document.removeEventListener('click', this.handleClickOutside)
    }
  },
  beforeUnmount() {
    this.removeClickOutsideListener()
  }
}
</script>

<style scoped>
.base-select-wrapper {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-1);
  width: 100%;
}

.select-label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-1);
}

.required-mark {
  color: var(--color-error-500);
  margin-left: 2px;
}

.select-container {
  position: relative;
}

.select-trigger {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  width: 100%;
  height: var(--input-height-md);
  padding: 0 var(--spacing-3);
  font-family: var(--font-family-base);
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
  background: var(--input-background);
  border: var(--border-width-medium) solid var(--input-border-color);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-fast);
  text-align: left;
}

.select-trigger:hover:not(:disabled) {
  border-color: var(--color-gray-400);
}

.select-trigger:focus {
  outline: none;
  border-color: var(--input-border-color-focus);
  box-shadow: 0 0 0 3px var(--color-primary-100);
}

.select-trigger:disabled {
  background: var(--color-gray-100);
  cursor: not-allowed;
  opacity: 0.7;
}

.is-open .select-trigger {
  border-color: var(--input-border-color-focus);
  box-shadow: 0 0 0 3px var(--color-primary-100);
}

.select-prefix {
  color: var(--color-text-tertiary);
  flex-shrink: 0;
}

.select-value {
  flex: 1;
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.select-value.placeholder {
  color: var(--input-placeholder);
}

.select-arrow {
  color: var(--color-text-tertiary);
  flex-shrink: 0;
  transition: transform var(--transition-fast);
}

.is-open .select-arrow {
  color: var(--color-primary-500);
}

/* Dropdown */
.select-dropdown {
  position: absolute;
  top: calc(100% + var(--spacing-1));
  left: 0;
  right: 0;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  z-index: var(--z-dropdown);
  overflow: hidden;
}

.select-search {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  padding: var(--spacing-3);
  border-bottom: 1px solid var(--color-border-light);
}

.search-icon {
  color: var(--color-text-tertiary);
  flex-shrink: 0;
}

.search-input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
  outline: none;
}

.search-input::placeholder {
  color: var(--input-placeholder);
}

.select-options {
  max-height: 240px;
  overflow-y: auto;
  padding: var(--spacing-1);
}

.select-empty {
  padding: var(--spacing-4);
  text-align: center;
  color: var(--color-text-tertiary);
  font-size: var(--font-size-sm);
}

.select-option {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  width: 100%;
  padding: var(--spacing-2) var(--spacing-3);
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  text-align: left;
  transition: all var(--transition-fast);
}

.select-option:hover:not(.disabled),
.select-option.focused:not(.disabled) {
  background: var(--color-gray-100);
}

.select-option.selected {
  background: var(--color-primary-50);
  color: var(--color-primary-700);
}

.select-option.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.option-icon {
  flex-shrink: 0;
  color: var(--color-text-tertiary);
}

.select-option.selected .option-icon {
  color: var(--color-primary-500);
}

.option-label {
  flex: 1;
  min-width: 0;
}

.option-description {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.option-check {
  flex-shrink: 0;
  color: var(--color-primary-500);
}

/* Error state */
.has-error .select-trigger {
  border-color: var(--color-error-500);
}

.has-error .select-trigger:focus {
  box-shadow: 0 0 0 3px var(--color-error-100);
}

.select-error {
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
  margin: var(--spacing-1) 0 0;
  font-size: var(--font-size-xs);
  color: var(--color-error-600);
}

.select-hint {
  margin: var(--spacing-1) 0 0;
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

/* Dropdown animation */
.dropdown-enter-active {
  animation: dropdownIn var(--transition-fast) var(--ease-smooth);
}

.dropdown-leave-active {
  animation: dropdownOut var(--transition-fast) var(--ease-smooth);
}

@keyframes dropdownIn {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes dropdownOut {
  from {
    opacity: 1;
    transform: translateY(0);
  }
  to {
    opacity: 0;
    transform: translateY(-8px);
  }
}
</style>
