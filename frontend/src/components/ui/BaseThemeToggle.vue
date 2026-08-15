<template>
  <button
    class="theme-toggle"
    :class="{ 'is-dark': isDark }"
    @click="toggleTheme"
    :aria-label="isDark ? 'Switch to light mode' : 'Switch to dark mode'"
    :title="isDark ? 'Switch to light mode' : 'Switch to dark mode'"
  >
    <span class="toggle-track">
      <span class="toggle-icon sun">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="5" />
          <line x1="12" y1="1" x2="12" y2="3" />
          <line x1="12" y1="21" x2="12" y2="23" />
          <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
          <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
          <line x1="1" y1="12" x2="3" y2="12" />
          <line x1="21" y1="12" x2="23" y2="12" />
          <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
          <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
        </svg>
      </span>
      <span class="toggle-icon moon">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
        </svg>
      </span>
      <span class="toggle-thumb" />
    </span>
  </button>
</template>

<script>
export default {
  name: 'BaseThemeToggle',
  data() {
    return {
      isDark: false
    }
  },
  mounted() {
    this.initTheme()
    // Listen for system preference changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', this.handleSystemChange)
  },
  beforeUnmount() {
    window.matchMedia('(prefers-color-scheme: dark)').removeEventListener('change', this.handleSystemChange)
  },
  methods: {
    initTheme() {
      const stored = localStorage.getItem('hermes-theme')
      if (stored) {
        this.isDark = stored === 'dark'
        document.documentElement.setAttribute('data-theme', stored)
      } else {
        // Follow system preference by default
        this.isDark = window.matchMedia('(prefers-color-scheme: dark)').matches
        // Don't set data-theme to let CSS handle system preference
      }
    },
    toggleTheme() {
      this.isDark = !this.isDark
      const theme = this.isDark ? 'dark' : 'light'
      document.documentElement.setAttribute('data-theme', theme)
      localStorage.setItem('hermes-theme', theme)
      this.$emit('change', theme)
    },
    handleSystemChange(e) {
      // Only update if user hasn't manually set a preference
      if (!localStorage.getItem('hermes-theme')) {
        this.isDark = e.matches
      }
    }
  }
}
</script>

<style scoped>
.theme-toggle {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  border: none;
  background: none;
  cursor: pointer;
  outline: none;
}

.toggle-track {
  position: relative;
  width: 52px;
  height: 28px;
  background: var(--color-gray-200);
  border-radius: var(--radius-full);
  padding: 3px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  transition: background var(--transition-base);
}

.theme-toggle.is-dark .toggle-track {
  background: var(--color-primary-600);
}

.toggle-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  color: var(--color-gray-500);
  transition: color var(--transition-base), opacity var(--transition-base);
  z-index: 1;
}

.toggle-icon.sun {
  color: var(--color-warning-500);
}

.toggle-icon.moon {
  color: var(--color-gray-400);
}

.theme-toggle.is-dark .toggle-icon.sun {
  color: var(--color-gray-400);
}

.theme-toggle.is-dark .toggle-icon.moon {
  color: var(--color-warning-300);
}

.toggle-thumb {
  position: absolute;
  top: 3px;
  left: 3px;
  width: 22px;
  height: 22px;
  background: var(--color-surface);
  border-radius: var(--radius-full);
  box-shadow: var(--shadow-sm);
  transition: transform var(--transition-base);
}

.theme-toggle.is-dark .toggle-thumb {
  transform: translateX(24px);
}

/* Focus state */
.theme-toggle:focus-visible .toggle-track {
  outline: 2px solid var(--color-primary-500);
  outline-offset: 2px;
}

/* Hover effect */
.theme-toggle:hover .toggle-track {
  background: var(--color-gray-300);
}

.theme-toggle.is-dark:hover .toggle-track {
  background: var(--color-primary-500);
}
</style>
