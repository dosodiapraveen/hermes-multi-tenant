<template>
  <div :class="['datetime-picker', { 'has-error': error }]">
    <label v-if="label" class="picker-label">
      {{ label }}
      <span v-if="required" class="required-mark">*</span>
    </label>

    <div class="picker-container">
      <!-- Date Input -->
      <div class="picker-field">
        <span class="field-icon">
          <BaseIcon name="calendar" :size="16" />
        </span>
        <input
          type="date"
          :value="dateValue"
          :disabled="disabled"
          :min="minDate"
          :max="maxDate"
          class="picker-input"
          @input="handleDateChange"
        />
      </div>

      <!-- Time Input (if not allDay) -->
      <div v-if="!allDay && showTime" class="picker-field time-field">
        <span class="field-icon">
          <BaseIcon name="clock" :size="16" />
        </span>
        <input
          type="time"
          :value="timeValue"
          :disabled="disabled"
          class="picker-input"
          @input="handleTimeChange"
        />
      </div>
    </div>

    <!-- Quick date buttons -->
    <div v-if="showQuickDates" class="quick-dates">
      <button
        v-for="date in quickDateOptions"
        :key="date.value"
        type="button"
        :class="['quick-date-btn', { active: dateValue === date.value }]"
        @click="setQuickDate(date.value)"
      >
        {{ date.label }}
      </button>
    </div>

    <!-- All day toggle -->
    <label v-if="showAllDay" class="all-day-toggle">
      <input
        type="checkbox"
        :checked="allDay"
        @change="$emit('update:allDay', $event.target.checked)"
      />
      <span class="toggle-label">All-day event</span>
    </label>

    <p v-if="error" class="picker-error">
      <BaseIcon name="alert-circle" :size="14" />
      {{ error }}
    </p>

    <p v-else-if="hint" class="picker-hint">{{ hint }}</p>
  </div>
</template>

<script>
import BaseIcon from './BaseIcon.vue'

export default {
  name: 'BaseDateTimePicker',
  components: { BaseIcon },
  props: {
    modelValue: {
      type: String,
      default: ''
    },
    label: {
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
    required: {
      type: Boolean,
      default: false
    },
    showTime: {
      type: Boolean,
      default: true
    },
    showAllDay: {
      type: Boolean,
      default: false
    },
    allDay: {
      type: Boolean,
      default: false
    },
    showQuickDates: {
      type: Boolean,
      default: true
    },
    minDate: {
      type: String,
      default: ''
    },
    maxDate: {
      type: String,
      default: ''
    }
  },
  emits: ['update:modelValue', 'update:allDay'],
  computed: {
    dateValue() {
      if (!this.modelValue) return ''
      return this.modelValue.slice(0, 10)
    },
    timeValue() {
      if (!this.modelValue) return ''
      const timePart = this.modelValue.slice(11, 16)
      return timePart || '09:00'
    },
    todayStr() {
      return new Date().toISOString().slice(0, 10)
    },
    tomorrowStr() {
      const d = new Date()
      d.setDate(d.getDate() + 1)
      return d.toISOString().slice(0, 10)
    },
    nextWeekStr() {
      const d = new Date()
      d.setDate(d.getDate() + 7)
      return d.toISOString().slice(0, 10)
    },
    quickDateOptions() {
      return [
        { label: 'Today', value: this.todayStr },
        { label: 'Tomorrow', value: this.tomorrowStr },
        { label: 'Next week', value: this.nextWeekStr }
      ]
    }
  },
  methods: {
    handleDateChange(e) {
      const date = e.target.value
      const time = this.timeValue || '09:00'
      this.emitValue(date, time)
    },
    handleTimeChange(e) {
      const time = e.target.value
      const date = this.dateValue || this.todayStr
      this.emitValue(date, time)
    },
    setQuickDate(date) {
      const time = this.timeValue || '09:00'
      this.emitValue(date, time)
    },
    emitValue(date, time) {
      if (!date) {
        this.$emit('update:modelValue', '')
        return
      }
      if (this.allDay) {
        this.$emit('update:modelValue', `${date}T00:00:00`)
      } else {
        this.$emit('update:modelValue', `${date}T${time}:00`)
      }
    }
  }
}
</script>

<style scoped>
.datetime-picker {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.picker-label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
}

.required-mark {
  color: var(--color-error-500);
  margin-left: 2px;
}

.picker-container {
  display: flex;
  gap: var(--spacing-2);
}

.picker-field {
  position: relative;
  display: flex;
  align-items: center;
  flex: 1;
}

.time-field {
  flex: 0 0 auto;
  min-width: 140px;
}

.field-icon {
  position: absolute;
  left: var(--spacing-3);
  color: var(--color-text-tertiary);
  pointer-events: none;
  z-index: 1;
}

.picker-input {
  width: 100%;
  height: var(--input-height-md);
  padding: 0 var(--spacing-3) 0 var(--spacing-10);
  font-family: var(--font-family-base);
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
  background: var(--input-background);
  border: var(--border-width-medium) solid var(--input-border-color);
  border-radius: var(--radius-lg);
  transition: all var(--transition-fast);
}

.picker-input:hover:not(:disabled) {
  border-color: var(--color-gray-400);
}

.picker-input:focus {
  outline: none;
  border-color: var(--input-border-color-focus);
  box-shadow: 0 0 0 3px var(--color-primary-100);
}

.picker-input:disabled {
  background: var(--color-gray-100);
  cursor: not-allowed;
  opacity: 0.7;
}

/* Quick dates */
.quick-dates {
  display: flex;
  gap: var(--spacing-2);
  flex-wrap: wrap;
}

.quick-date-btn {
  padding: var(--spacing-2) var(--spacing-3);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  background: var(--color-gray-100);
  border: 1px solid transparent;
  border-radius: var(--radius-full);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.quick-date-btn:hover {
  background: var(--color-gray-200);
  color: var(--color-text-primary);
}

.quick-date-btn.active {
  background: var(--color-primary-500);
  color: var(--color-text-inverse);
}

/* All day toggle */
.all-day-toggle {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  cursor: pointer;
}

.all-day-toggle input {
  width: 16px;
  height: 16px;
  accent-color: var(--color-primary-500);
  cursor: pointer;
}

.toggle-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

/* Error state */
.has-error .picker-input {
  border-color: var(--color-error-500);
}

.has-error .picker-input:focus {
  box-shadow: 0 0 0 3px var(--color-error-100);
}

.picker-error {
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
  margin: 0;
  font-size: var(--font-size-xs);
  color: var(--color-error-600);
}

.picker-hint {
  margin: 0;
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

/* Responsive */
@media (max-width: 480px) {
  .picker-container {
    flex-direction: column;
  }

  .time-field {
    min-width: 100%;
  }
}
</style>
