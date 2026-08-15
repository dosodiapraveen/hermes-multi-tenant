/**
 * Composable for syncing component state with URL query parameters
 * Enables deep-linking and shareable URLs
 */
import { ref, watch, onMounted } from 'vue'

export function useUrlState(key, defaultValue = '') {
  const state = ref(defaultValue)

  // Read initial state from URL
  const readFromUrl = () => {
    const params = new URLSearchParams(window.location.search)
    const value = params.get(key)
    if (value !== null) {
      state.value = value
    }
  }

  // Write state to URL without triggering navigation
  const writeToUrl = (value) => {
    const params = new URLSearchParams(window.location.search)

    if (value && value !== defaultValue) {
      params.set(key, value)
    } else {
      params.delete(key)
    }

    const newUrl = params.toString()
      ? `${window.location.pathname}?${params.toString()}`
      : window.location.pathname

    window.history.replaceState({}, '', newUrl)
  }

  // Watch for state changes and sync to URL
  watch(state, (newValue) => {
    writeToUrl(newValue)
  })

  // Handle browser back/forward
  const handlePopState = () => {
    readFromUrl()
  }

  onMounted(() => {
    readFromUrl()
    window.addEventListener('popstate', handlePopState)
  })

  // Return both state and methods for manual control
  return {
    state,
    readFromUrl,
    writeToUrl
  }
}

/**
 * Helper to sync multiple URL parameters at once
 */
export function useUrlStateMultiple(config) {
  const states = {}

  for (const [key, defaultValue] of Object.entries(config)) {
    states[key] = useUrlState(key, defaultValue)
  }

  return states
}
