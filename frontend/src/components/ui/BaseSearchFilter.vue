<template>
  <div class="search-filter">
    <!-- Search input -->
    <div class="search-wrapper">
      <BaseIcon name="search" :size="18" class="search-icon" />
      <input
        v-model="searchValue"
        type="text"
        class="search-input"
        :placeholder="placeholder"
        @input="handleSearch"
        @keyup.enter="$emit('search', searchValue)"
      />
      <button
        v-if="searchValue"
        type="button"
        class="clear-btn"
        @click="clearSearch"
      >
        <BaseIcon name="x" :size="16" />
      </button>
      <BaseButton
        v-if="showSearchButton"
        variant="primary"
        size="sm"
        @click="$emit('search', searchValue)"
      >
        Search
      </BaseButton>
    </div>

    <!-- Filters row -->
    <div v-if="filters.length > 0 || $slots.filters" class="filters-row">
      <slot name="filters">
        <div
          v-for="filter in filters"
          :key="filter.key"
          class="filter-item"
        >
          <BaseSelect
            v-if="filter.type === 'select'"
            v-model="filterValues[filter.key]"
            :options="filter.options"
            :placeholder="filter.placeholder || `All ${filter.label}`"
            :prefix-icon="filter.icon"
            @change="handleFilterChange(filter.key, $event)"
          />

          <div v-else-if="filter.type === 'chips'" class="filter-chips">
            <button
              v-for="option in filter.options"
              :key="option.value"
              type="button"
              :class="['filter-chip', { active: filterValues[filter.key] === option.value }]"
              @click="toggleChip(filter.key, option.value)"
            >
              <BaseIcon v-if="option.icon" :name="option.icon" :size="14" />
              {{ option.label }}
            </button>
          </div>
        </div>
      </slot>

      <!-- Active filters summary -->
      <div v-if="hasActiveFilters && showActiveFilters" class="active-filters">
        <span class="active-label">Filters:</span>
        <div class="active-tags">
          <span
            v-for="(value, key) in activeFilters"
            :key="key"
            class="active-tag"
          >
            {{ getFilterLabel(key, value) }}
            <button type="button" @click="clearFilter(key)">
              <BaseIcon name="x" :size="12" />
            </button>
          </span>
        </div>
        <button type="button" class="clear-all" @click="clearAllFilters">
          Clear all
        </button>
      </div>
    </div>

    <!-- Sort options -->
    <div v-if="sortOptions.length > 0" class="sort-row">
      <span class="sort-label">Sort by:</span>
      <div class="sort-options">
        <button
          v-for="option in sortOptions"
          :key="option.value"
          type="button"
          :class="['sort-btn', { active: sortValue === option.value }]"
          @click="handleSort(option.value)"
        >
          {{ option.label }}
          <BaseIcon
            v-if="sortValue === option.value"
            :name="sortDirection === 'asc' ? 'chevron-up' : 'chevron-down'"
            :size="14"
          />
        </button>
      </div>
    </div>

    <!-- Results count -->
    <div v-if="showResultCount && totalResults !== null" class="results-info">
      <span class="results-count">
        {{ totalResults }} {{ totalResults === 1 ? 'result' : 'results' }}
        <span v-if="searchValue">for "{{ searchValue }}"</span>
      </span>
    </div>
  </div>
</template>

<script>
import BaseIcon from './BaseIcon.vue'
import BaseButton from './BaseButton.vue'
import BaseSelect from './BaseSelect.vue'

export default {
  name: 'BaseSearchFilter',
  components: { BaseIcon, BaseButton, BaseSelect },
  props: {
    search: {
      type: String,
      default: ''
    },
    placeholder: {
      type: String,
      default: 'Search...'
    },
    showSearchButton: {
      type: Boolean,
      default: false
    },
    filters: {
      type: Array,
      default: () => []
      // Array of { key, label, type: 'select'|'chips', options: [{value, label, icon?}], icon? }
    },
    initialFilters: {
      type: Object,
      default: () => ({})
    },
    showActiveFilters: {
      type: Boolean,
      default: true
    },
    sortOptions: {
      type: Array,
      default: () => []
      // Array of { value, label }
    },
    initialSort: {
      type: String,
      default: ''
    },
    initialSortDirection: {
      type: String,
      default: 'desc'
    },
    showResultCount: {
      type: Boolean,
      default: false
    },
    totalResults: {
      type: Number,
      default: null
    },
    debounceMs: {
      type: Number,
      default: 300
    }
  },
  emits: ['update:search', 'search', 'filter', 'sort', 'clear'],
  data() {
    return {
      searchValue: this.search,
      filterValues: { ...this.initialFilters },
      sortValue: this.initialSort,
      sortDirection: this.initialSortDirection,
      debounceTimer: null
    }
  },
  computed: {
    activeFilters() {
      const active = {}
      for (const [key, value] of Object.entries(this.filterValues)) {
        if (value !== '' && value !== null && value !== undefined) {
          active[key] = value
        }
      }
      return active
    },
    hasActiveFilters() {
      return Object.keys(this.activeFilters).length > 0
    }
  },
  watch: {
    search(val) {
      this.searchValue = val
    }
  },
  methods: {
    handleSearch() {
      this.$emit('update:search', this.searchValue)

      clearTimeout(this.debounceTimer)
      this.debounceTimer = setTimeout(() => {
        this.$emit('search', this.searchValue)
      }, this.debounceMs)
    },

    clearSearch() {
      this.searchValue = ''
      this.$emit('update:search', '')
      this.$emit('search', '')
    },

    handleFilterChange(key, option) {
      this.filterValues[key] = option?.value ?? ''
      this.emitFilterChange()
    },

    toggleChip(key, value) {
      this.filterValues[key] = this.filterValues[key] === value ? '' : value
      this.emitFilterChange()
    },

    emitFilterChange() {
      this.$emit('filter', { ...this.filterValues })
    },

    clearFilter(key) {
      this.filterValues[key] = ''
      this.emitFilterChange()
    },

    clearAllFilters() {
      for (const key of Object.keys(this.filterValues)) {
        this.filterValues[key] = ''
      }
      this.emitFilterChange()
      this.$emit('clear')
    },

    handleSort(value) {
      if (this.sortValue === value) {
        this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc'
      } else {
        this.sortValue = value
        this.sortDirection = 'desc'
      }
      this.$emit('sort', { field: this.sortValue, direction: this.sortDirection })
    },

    getFilterLabel(key, value) {
      const filter = this.filters.find(f => f.key === key)
      if (!filter) return `${key}: ${value}`

      const option = filter.options?.find(o => o.value === value)
      return option?.label || `${filter.label}: ${value}`
    }
  },
  beforeUnmount() {
    clearTimeout(this.debounceTimer)
  }
}
</script>

<style scoped>
.search-filter {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}

/* Search wrapper */
.search-wrapper {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  padding: var(--spacing-2) var(--spacing-3);
  background: var(--color-surface);
  border: var(--border-width-medium) solid var(--color-border);
  border-radius: var(--radius-lg);
  transition: all var(--transition-fast);
}

.search-wrapper:focus-within {
  border-color: var(--color-primary-500);
  box-shadow: 0 0 0 3px var(--color-primary-100);
}

.search-icon {
  color: var(--color-text-tertiary);
  flex-shrink: 0;
}

.search-input {
  flex: 1;
  min-width: 0;
  padding: var(--spacing-2) 0;
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
  background: transparent;
  border: none;
  outline: none;
}

.search-input::placeholder {
  color: var(--color-text-tertiary);
}

.clear-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  padding: 0;
  background: var(--color-gray-100);
  border: none;
  border-radius: var(--radius-md);
  color: var(--color-text-tertiary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.clear-btn:hover {
  background: var(--color-gray-200);
  color: var(--color-text-primary);
}

/* Filters row */
.filters-row {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  flex-wrap: wrap;
}

.filter-item {
  min-width: 160px;
}

/* Filter chips */
.filter-chips {
  display: flex;
  gap: var(--spacing-2);
  flex-wrap: wrap;
}

.filter-chip {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-1);
  padding: var(--spacing-2) var(--spacing-3);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  background: var(--color-gray-100);
  border: none;
  border-radius: var(--radius-full);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.filter-chip:hover {
  background: var(--color-gray-200);
  color: var(--color-text-primary);
}

.filter-chip.active {
  background: var(--color-primary-500);
  color: var(--color-text-inverse);
}

/* Active filters */
.active-filters {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  width: 100%;
  padding-top: var(--spacing-2);
}

.active-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.active-tags {
  display: flex;
  gap: var(--spacing-2);
  flex-wrap: wrap;
}

.active-tag {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-1);
  padding: var(--spacing-1) var(--spacing-2);
  font-size: var(--font-size-xs);
  color: var(--color-primary-700);
  background: var(--color-primary-100);
  border-radius: var(--radius-md);
}

.active-tag button {
  display: flex;
  padding: 2px;
  background: transparent;
  border: none;
  border-radius: var(--radius-sm);
  color: var(--color-primary-500);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.active-tag button:hover {
  background: var(--color-primary-200);
}

.clear-all {
  margin-left: auto;
  padding: var(--spacing-1) var(--spacing-2);
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.clear-all:hover {
  color: var(--color-error-500);
}

/* Sort row */
.sort-row {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.sort-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
}

.sort-options {
  display: flex;
  gap: var(--spacing-1);
}

.sort-btn {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-1);
  padding: var(--spacing-1) var(--spacing-2);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.sort-btn:hover {
  background: var(--color-gray-100);
  color: var(--color-text-primary);
}

.sort-btn.active {
  background: var(--color-primary-100);
  color: var(--color-primary-700);
}

/* Results info */
.results-info {
  padding-top: var(--spacing-2);
}

.results-count {
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
}

/* Responsive */
@media (max-width: 640px) {
  .filters-row {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-item {
    min-width: 100%;
  }

  .active-filters {
    flex-wrap: wrap;
  }

  .clear-all {
    margin-left: 0;
    width: 100%;
    text-align: center;
    margin-top: var(--spacing-2);
  }
}
</style>
