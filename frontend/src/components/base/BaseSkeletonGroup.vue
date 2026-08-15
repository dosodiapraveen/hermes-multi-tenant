<template>
  <div :class="['skeleton-group', `skeleton-group--${variant}`]">
    <!-- Card Grid -->
    <template v-if="variant === 'card-grid'">
      <div class="skeleton-grid">
        <BaseSkeleton
          v-for="i in count"
          :key="i"
          variant="card"
          :size="size"
        />
      </div>
    </template>

    <!-- List -->
    <template v-else-if="variant === 'list'">
      <div class="skeleton-list">
        <div v-for="i in count" :key="i" class="skeleton-list-item">
          <BaseSkeleton v-if="showAvatar" variant="circle" size="md" />
          <div class="skeleton-list-content">
            <BaseSkeleton variant="text" size="md" :width="titleWidth(i)" />
            <BaseSkeleton v-if="showSubtitle" variant="text" size="sm" :width="subtitleWidth(i)" />
          </div>
        </div>
      </div>
    </template>

    <!-- Article/Content -->
    <template v-else-if="variant === 'article'">
      <div class="skeleton-article">
        <BaseSkeleton variant="text" size="xl" width="60%" />
        <div class="skeleton-article-meta">
          <BaseSkeleton variant="circle" size="sm" />
          <BaseSkeleton variant="text" size="sm" width="120px" />
          <BaseSkeleton variant="text" size="sm" width="80px" />
        </div>
        <BaseSkeleton variant="rectangle" size="xl" />
        <div class="skeleton-article-text">
          <BaseSkeleton v-for="i in 4" :key="i" variant="text" :width="textWidth(i)" />
        </div>
      </div>
    </template>

    <!-- Table -->
    <template v-else-if="variant === 'table'">
      <div class="skeleton-table">
        <div class="skeleton-table-header">
          <BaseSkeleton v-for="i in columns" :key="i" variant="text" size="sm" />
        </div>
        <div v-for="row in count" :key="row" class="skeleton-table-row">
          <BaseSkeleton v-for="col in columns" :key="col" variant="text" size="sm" :width="cellWidth(col)" />
        </div>
      </div>
    </template>

    <!-- Stats -->
    <template v-else-if="variant === 'stats'">
      <div class="skeleton-stats">
        <div v-for="i in count" :key="i" class="skeleton-stat">
          <BaseSkeleton variant="text" size="sm" width="60%" />
          <BaseSkeleton variant="text" size="xl" width="40%" />
        </div>
      </div>
    </template>

    <!-- Default: Simple text lines -->
    <template v-else>
      <div class="skeleton-text">
        <BaseSkeleton v-for="i in count" :key="i" variant="text" :width="textWidth(i)" />
      </div>
    </template>
  </div>
</template>

<script>
import BaseSkeleton from './BaseSkeleton.vue'

export default {
  name: 'BaseSkeletonGroup',
  components: {
    BaseSkeleton
  },
  props: {
    variant: {
      type: String,
      default: 'text',
      validator: value => ['text', 'card-grid', 'list', 'article', 'table', 'stats'].includes(value)
    },
    count: {
      type: Number,
      default: 3
    },
    size: {
      type: String,
      default: 'md'
    },
    columns: {
      type: Number,
      default: 4
    },
    showAvatar: {
      type: Boolean,
      default: true
    },
    showSubtitle: {
      type: Boolean,
      default: true
    }
  },
  methods: {
    titleWidth(index) {
      const widths = ['80%', '65%', '75%', '60%', '70%']
      return widths[(index - 1) % widths.length]
    },
    subtitleWidth(index) {
      const widths = ['50%', '40%', '55%', '45%', '35%']
      return widths[(index - 1) % widths.length]
    },
    textWidth(index) {
      const widths = ['100%', '95%', '85%', '90%', '70%']
      return widths[(index - 1) % widths.length]
    },
    cellWidth(col) {
      const widths = ['60%', '80%', '50%', '70%', '90%']
      return widths[(col - 1) % widths.length]
    }
  }
}
</script>

<style scoped>
.skeleton-group {
  width: 100%;
}

/* Card Grid */
.skeleton-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: var(--spacing-3);
}

/* List */
.skeleton-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}

.skeleton-list-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  padding: var(--spacing-3);
  background: var(--color-surface);
  border-radius: var(--radius-lg);
}

.skeleton-list-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

/* Article */
.skeleton-article {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

.skeleton-article-meta {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
}

.skeleton-article-text {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

/* Table */
.skeleton-table {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.skeleton-table-header,
.skeleton-table-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: var(--spacing-3);
  padding: var(--spacing-3);
}

.skeleton-table-header {
  background: var(--color-surface-hover);
  border-radius: var(--radius-md);
}

.skeleton-table-row {
  background: var(--color-surface);
  border-radius: var(--radius-md);
}

/* Stats */
.skeleton-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: var(--spacing-3);
}

.skeleton-stat {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
  padding: var(--spacing-4);
  background: var(--color-surface);
  border-radius: var(--radius-xl);
}

/* Text */
.skeleton-text {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}
</style>
