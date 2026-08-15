<template>
  <div class="base-chart" :style="{ height: height + 'px' }">
    <svg ref="svg" :viewBox="`0 0 ${width} ${height}`" preserveAspectRatio="xMidYMid meet">
      <!-- Grid lines -->
      <g class="grid-lines" v-if="showGrid">
        <line
          v-for="(y, i) in gridLines"
          :key="'grid-' + i"
          :x1="padding.left"
          :y1="y"
          :x2="width - padding.right"
          :y2="y"
          class="grid-line"
        />
      </g>

      <!-- Y-axis labels -->
      <g class="y-axis" v-if="showYAxis">
        <text
          v-for="(label, i) in yAxisLabels"
          :key="'y-' + i"
          :x="padding.left - 10"
          :y="label.y + 4"
          class="axis-label"
          text-anchor="end"
        >
          {{ label.text }}
        </text>
      </g>

      <!-- X-axis labels -->
      <g class="x-axis" v-if="showXAxis">
        <text
          v-for="(label, i) in xAxisLabels"
          :key="'x-' + i"
          :x="label.x"
          :y="height - padding.bottom + 20"
          class="axis-label"
          text-anchor="middle"
        >
          {{ label.text }}
        </text>
      </g>

      <!-- Line chart -->
      <template v-if="type === 'line'">
        <defs>
          <linearGradient :id="'gradient-' + uid" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" :stop-color="color" stop-opacity="0.3" />
            <stop offset="100%" :stop-color="color" stop-opacity="0.05" />
          </linearGradient>
        </defs>
        <path v-if="areaPath" :d="areaPath" :fill="`url(#gradient-${uid})`" class="chart-area" />
        <path :d="linePath" :stroke="color" class="chart-line" fill="none" stroke-width="2.5" />
        <g class="data-points">
          <circle
            v-for="(point, i) in dataPoints"
            :key="i"
            :cx="point.x"
            :cy="point.y"
            r="4"
            :fill="color"
            class="data-point"
            @mouseenter="showTooltip(i, $event)"
            @mouseleave="hideTooltip"
          />
        </g>
      </template>

      <!-- Bar chart -->
      <template v-if="type === 'bar'">
        <g class="bars">
          <rect
            v-for="(bar, i) in bars"
            :key="i"
            :x="bar.x"
            :y="bar.y"
            :width="bar.width"
            :height="bar.height"
            :fill="bar.color || color"
            rx="4"
            class="chart-bar"
            @mouseenter="showTooltip(i, $event)"
            @mouseleave="hideTooltip"
          />
        </g>
      </template>
    </svg>

    <!-- Tooltip -->
    <Transition name="tooltip">
      <div
        v-if="tooltipVisible"
        class="chart-tooltip"
        :style="{ left: tooltipX + 'px', top: tooltipY + 'px' }"
      >
        <div class="tooltip-label">{{ tooltipLabel }}</div>
        <div class="tooltip-value">{{ formatValue(tooltipValue) }}</div>
      </div>
    </Transition>
  </div>
</template>

<script>
let chartUid = 0

export default {
  name: 'BaseChart',
  props: {
    type: {
      type: String,
      default: 'line',
      validator: (v) => ['line', 'bar'].includes(v)
    },
    data: {
      type: Array,
      required: true
      // Array of { label: string, value: number, color?: string }
    },
    color: {
      type: String,
      default: 'var(--color-primary-500)'
    },
    height: {
      type: Number,
      default: 200
    },
    showGrid: {
      type: Boolean,
      default: true
    },
    showXAxis: {
      type: Boolean,
      default: true
    },
    showYAxis: {
      type: Boolean,
      default: true
    },
    formatValue: {
      type: Function,
      default: (v) => v.toLocaleString()
    }
  },
  data() {
    return {
      uid: ++chartUid,
      width: 400,
      padding: { top: 20, right: 20, bottom: 40, left: 50 },
      tooltipVisible: false,
      tooltipX: 0,
      tooltipY: 0,
      tooltipLabel: '',
      tooltipValue: 0
    }
  },
  computed: {
    chartWidth() {
      return this.width - this.padding.left - this.padding.right
    },
    chartHeight() {
      return this.height - this.padding.top - this.padding.bottom
    },
    maxValue() {
      const max = Math.max(...this.data.map(d => d.value))
      return max === 0 ? 100 : max * 1.1 // Add 10% padding
    },
    minValue() {
      return 0
    },
    scaleY() {
      return (value) => {
        const ratio = (value - this.minValue) / (this.maxValue - this.minValue)
        return this.padding.top + this.chartHeight * (1 - ratio)
      }
    },
    scaleX() {
      return (index) => {
        if (this.data.length === 1) return this.padding.left + this.chartWidth / 2
        const step = this.chartWidth / (this.data.length - 1)
        return this.padding.left + step * index
      }
    },
    dataPoints() {
      return this.data.map((d, i) => ({
        x: this.scaleX(i),
        y: this.scaleY(d.value),
        label: d.label,
        value: d.value
      }))
    },
    linePath() {
      if (!this.dataPoints.length) return ''
      return this.dataPoints
        .map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`)
        .join(' ')
    },
    areaPath() {
      if (!this.dataPoints.length) return ''
      const baseline = this.padding.top + this.chartHeight
      const start = `M ${this.dataPoints[0].x} ${baseline}`
      const line = this.dataPoints.map(p => `L ${p.x} ${p.y}`).join(' ')
      const end = `L ${this.dataPoints[this.dataPoints.length - 1].x} ${baseline} Z`
      return `${start} ${line} ${end}`
    },
    bars() {
      const barWidth = (this.chartWidth / this.data.length) * 0.7
      const gap = (this.chartWidth / this.data.length) * 0.3
      return this.data.map((d, i) => ({
        x: this.padding.left + (i * (barWidth + gap)) + gap / 2,
        y: this.scaleY(d.value),
        width: barWidth,
        height: this.padding.top + this.chartHeight - this.scaleY(d.value),
        color: d.color,
        label: d.label,
        value: d.value
      }))
    },
    gridLines() {
      const lines = []
      const steps = 4
      for (let i = 0; i <= steps; i++) {
        const value = this.minValue + ((this.maxValue - this.minValue) * i) / steps
        lines.push(this.scaleY(value))
      }
      return lines
    },
    yAxisLabels() {
      const labels = []
      const steps = 4
      for (let i = 0; i <= steps; i++) {
        const value = this.minValue + ((this.maxValue - this.minValue) * i) / steps
        labels.push({
          y: this.scaleY(value),
          text: this.formatValue(Math.round(value))
        })
      }
      return labels
    },
    xAxisLabels() {
      // Show fewer labels if too many data points
      const maxLabels = 7
      const step = Math.ceil(this.data.length / maxLabels)
      return this.data
        .filter((_, i) => i % step === 0)
        .map((d, i) => ({
          x: this.scaleX(i * step),
          text: d.label
        }))
    }
  },
  mounted() {
    this.updateWidth()
    window.addEventListener('resize', this.updateWidth)
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.updateWidth)
  },
  methods: {
    updateWidth() {
      if (this.$refs.svg) {
        this.width = this.$refs.svg.parentElement.clientWidth || 400
      }
    },
    showTooltip(index, event) {
      const d = this.type === 'bar' ? this.bars[index] : this.dataPoints[index]
      this.tooltipLabel = d.label
      this.tooltipValue = d.value
      this.tooltipX = event.offsetX
      this.tooltipY = event.offsetY - 60
      this.tooltipVisible = true
    },
    hideTooltip() {
      this.tooltipVisible = false
    }
  }
}
</script>

<style scoped>
.base-chart {
  position: relative;
  width: 100%;
}

.base-chart svg {
  width: 100%;
  height: 100%;
  overflow: visible;
}

.grid-line {
  stroke: var(--color-border-light);
  stroke-dasharray: 4 4;
}

.axis-label {
  font-size: 11px;
  fill: var(--color-text-tertiary);
  font-family: var(--font-family-base);
}

.chart-line {
  stroke-linecap: round;
  stroke-linejoin: round;
}

.chart-area {
  opacity: 1;
}

.data-point {
  cursor: pointer;
  transition: r var(--transition-fast);
}

.data-point:hover {
  r: 6;
}

.chart-bar {
  cursor: pointer;
  transition: opacity var(--transition-fast);
}

.chart-bar:hover {
  opacity: 0.8;
}

/* Tooltip */
.chart-tooltip {
  position: absolute;
  background: var(--color-gray-800);
  color: var(--color-text-inverse);
  padding: var(--spacing-2) var(--spacing-3);
  border-radius: var(--radius-md);
  font-size: var(--font-size-xs);
  pointer-events: none;
  transform: translateX(-50%);
  z-index: 10;
  white-space: nowrap;
  box-shadow: var(--shadow-lg);
}

.tooltip-label {
  color: var(--color-gray-400);
  margin-bottom: 2px;
}

.tooltip-value {
  font-weight: var(--font-weight-semibold);
  font-size: var(--font-size-sm);
}

.tooltip-enter-active,
.tooltip-leave-active {
  transition: opacity var(--transition-fast);
}

.tooltip-enter-from,
.tooltip-leave-to {
  opacity: 0;
}
</style>
