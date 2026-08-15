<template>
  <div
    class="tooltip-wrapper"
    @mouseenter="showTooltip"
    @mouseleave="hideTooltip"
    @focus="showTooltip"
    @blur="hideTooltip"
  >
    <slot />
    <Teleport to="body">
      <Transition name="tooltip">
        <div
          v-if="visible && content"
          ref="tooltip"
          :class="['base-tooltip', `tooltip-${position}`]"
          :style="tooltipStyle"
          role="tooltip"
        >
          <div class="tooltip-content">
            <slot name="content">{{ content }}</slot>
          </div>
          <div class="tooltip-arrow" :style="arrowStyle"></div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script>
export default {
  name: 'BaseTooltip',
  props: {
    content: {
      type: String,
      default: ''
    },
    position: {
      type: String,
      default: 'top',
      validator: (v) => ['top', 'bottom', 'left', 'right'].includes(v)
    },
    delay: {
      type: Number,
      default: 200
    },
    offset: {
      type: Number,
      default: 8
    },
    disabled: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      visible: false,
      tooltipStyle: {},
      arrowStyle: {},
      showTimer: null,
      hideTimer: null
    }
  },
  methods: {
    showTooltip() {
      if (this.disabled || !this.content) return

      clearTimeout(this.hideTimer)
      this.showTimer = setTimeout(() => {
        this.visible = true
        this.$nextTick(() => {
          this.updatePosition()
        })
      }, this.delay)
    },

    hideTooltip() {
      clearTimeout(this.showTimer)
      this.hideTimer = setTimeout(() => {
        this.visible = false
      }, 100)
    },

    updatePosition() {
      const trigger = this.$el
      const tooltip = this.$refs.tooltip

      if (!trigger || !tooltip) return

      const triggerRect = trigger.getBoundingClientRect()
      const tooltipRect = tooltip.getBoundingClientRect()

      let top, left

      switch (this.position) {
        case 'top':
          top = triggerRect.top - tooltipRect.height - this.offset
          left = triggerRect.left + (triggerRect.width - tooltipRect.width) / 2
          break
        case 'bottom':
          top = triggerRect.bottom + this.offset
          left = triggerRect.left + (triggerRect.width - tooltipRect.width) / 2
          break
        case 'left':
          top = triggerRect.top + (triggerRect.height - tooltipRect.height) / 2
          left = triggerRect.left - tooltipRect.width - this.offset
          break
        case 'right':
          top = triggerRect.top + (triggerRect.height - tooltipRect.height) / 2
          left = triggerRect.right + this.offset
          break
      }

      // Viewport boundary checks
      const padding = 8
      if (left < padding) left = padding
      if (left + tooltipRect.width > window.innerWidth - padding) {
        left = window.innerWidth - tooltipRect.width - padding
      }
      if (top < padding) top = padding
      if (top + tooltipRect.height > window.innerHeight - padding) {
        top = window.innerHeight - tooltipRect.height - padding
      }

      this.tooltipStyle = {
        top: `${top}px`,
        left: `${left}px`
      }

      // Position arrow
      const arrowOffset = triggerRect.left + triggerRect.width / 2 - left
      if (this.position === 'top' || this.position === 'bottom') {
        this.arrowStyle = { left: `${arrowOffset}px` }
      }
    }
  },
  beforeUnmount() {
    clearTimeout(this.showTimer)
    clearTimeout(this.hideTimer)
  }
}
</script>

<style scoped>
.tooltip-wrapper {
  display: inline-flex;
}

.base-tooltip {
  position: fixed;
  z-index: var(--z-tooltip);
  max-width: 280px;
  pointer-events: none;
}

.tooltip-content {
  padding: var(--spacing-2) var(--spacing-3);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-inverse);
  background: var(--color-gray-800);
  border-radius: var(--radius-md);
  line-height: var(--line-height-normal);
  box-shadow: var(--shadow-lg);
}

.tooltip-arrow {
  position: absolute;
  width: 8px;
  height: 8px;
  background: var(--color-gray-800);
  transform: rotate(45deg);
}

.tooltip-top .tooltip-arrow {
  bottom: -4px;
  left: 50%;
  margin-left: -4px;
}

.tooltip-bottom .tooltip-arrow {
  top: -4px;
  left: 50%;
  margin-left: -4px;
}

.tooltip-left .tooltip-arrow {
  right: -4px;
  top: 50%;
  margin-top: -4px;
}

.tooltip-right .tooltip-arrow {
  left: -4px;
  top: 50%;
  margin-top: -4px;
}

/* Animation */
.tooltip-enter-active {
  animation: tooltipIn var(--transition-fast) var(--ease-smooth);
}

.tooltip-leave-active {
  animation: tooltipOut var(--transition-fast) var(--ease-smooth);
}

@keyframes tooltipIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes tooltipOut {
  from {
    opacity: 1;
    transform: scale(1);
  }
  to {
    opacity: 0;
    transform: scale(0.95);
  }
}
</style>
