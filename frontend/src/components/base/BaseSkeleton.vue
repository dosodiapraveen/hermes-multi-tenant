<template>
  <div
    :class="[
      'skeleton',
      `skeleton--${variant}`,
      `skeleton--${size}`,
      { 'skeleton--animated': animated }
    ]"
    :style="customStyle"
    :aria-hidden="true"
  />
</template>

<script>
export default {
  name: 'BaseSkeleton',
  props: {
    variant: {
      type: String,
      default: 'text',
      validator: value => ['text', 'circle', 'rectangle', 'card'].includes(value)
    },
    size: {
      type: String,
      default: 'md',
      validator: value => ['sm', 'md', 'lg', 'xl'].includes(value)
    },
    width: {
      type: [String, Number],
      default: null
    },
    height: {
      type: [String, Number],
      default: null
    },
    animated: {
      type: Boolean,
      default: true
    }
  },
  computed: {
    customStyle() {
      const style = {}
      if (this.width) {
        style.width = typeof this.width === 'number' ? `${this.width}px` : this.width
      }
      if (this.height) {
        style.height = typeof this.height === 'number' ? `${this.height}px` : this.height
      }
      return style
    }
  }
}
</script>

<style scoped>
.skeleton {
  background: linear-gradient(
    90deg,
    var(--skeleton-base) 0%,
    var(--skeleton-base) 25%,
    var(--skeleton-highlight) 50%,
    var(--skeleton-base) 75%,
    var(--skeleton-base) 100%
  );
  background-size: 400% 100%;
  border-radius: var(--radius-md);

  /* Light mode colors */
  --skeleton-base: var(--color-gray-100);
  --skeleton-highlight: var(--color-gray-200);
}

/* Dark mode colors */
:root.dark .skeleton,
[data-theme="dark"] .skeleton {
  --skeleton-base: var(--color-gray-200);
  --skeleton-highlight: var(--color-border);
}

@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) .skeleton {
    --skeleton-base: var(--color-gray-200);
    --skeleton-highlight: var(--color-border);
  }
}

/* Animation */
.skeleton--animated {
  animation: shimmer 1.5s ease-in-out infinite;
}

@keyframes shimmer {
  0% {
    background-position: 100% 0;
  }
  100% {
    background-position: -100% 0;
  }
}

/* Variants */
.skeleton--text {
  height: 1em;
  width: 100%;
  border-radius: var(--radius-sm);
}

.skeleton--circle {
  border-radius: var(--radius-full);
  aspect-ratio: 1;
}

.skeleton--rectangle {
  width: 100%;
}

.skeleton--card {
  border-radius: var(--radius-xl);
  width: 100%;
}

/* Sizes */
.skeleton--sm.skeleton--text {
  height: 0.75rem;
}
.skeleton--md.skeleton--text {
  height: 1rem;
}
.skeleton--lg.skeleton--text {
  height: 1.25rem;
}
.skeleton--xl.skeleton--text {
  height: 1.5rem;
}

.skeleton--sm.skeleton--circle {
  width: 24px;
  height: 24px;
}
.skeleton--md.skeleton--circle {
  width: 40px;
  height: 40px;
}
.skeleton--lg.skeleton--circle {
  width: 56px;
  height: 56px;
}
.skeleton--xl.skeleton--circle {
  width: 80px;
  height: 80px;
}

.skeleton--sm.skeleton--rectangle,
.skeleton--sm.skeleton--card {
  height: 60px;
}
.skeleton--md.skeleton--rectangle,
.skeleton--md.skeleton--card {
  height: 100px;
}
.skeleton--lg.skeleton--rectangle,
.skeleton--lg.skeleton--card {
  height: 150px;
}
.skeleton--xl.skeleton--rectangle,
.skeleton--xl.skeleton--card {
  height: 200px;
}

/* Reduce motion for accessibility */
@media (prefers-reduced-motion: reduce) {
  .skeleton--animated {
    animation: none;
    background: var(--skeleton-base);
  }
}
</style>
