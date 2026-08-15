/**
 * Composable for auto-saving form drafts to localStorage
 * Enables recovery of unsaved form data
 */
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'

const DRAFT_PREFIX = 'form_draft_'
const DRAFT_EXPIRY_MS = 24 * 60 * 60 * 1000 // 24 hours

export function useFormDraft(formKey, formData, options = {}) {
  const {
    debounceMs = 1000,
    onRestore = null,
    excludeFields = []
  } = options

  const hasDraft = ref(false)
  const draftTimestamp = ref(null)
  let debounceTimer = null

  const storageKey = DRAFT_PREFIX + formKey

  // Get draft from localStorage
  const getDraft = () => {
    try {
      const stored = localStorage.getItem(storageKey)
      if (!stored) return null

      const { data, timestamp } = JSON.parse(stored)

      // Check if draft has expired
      if (Date.now() - timestamp > DRAFT_EXPIRY_MS) {
        clearDraft()
        return null
      }

      return { data, timestamp }
    } catch {
      return null
    }
  }

  // Save draft to localStorage
  const saveDraft = () => {
    if (!formData.value) return

    const dataToSave = { ...formData.value }

    // Remove excluded fields
    excludeFields.forEach(field => {
      delete dataToSave[field]
    })

    // Don't save if form is empty
    const hasContent = Object.values(dataToSave).some(v =>
      v !== '' && v !== null && v !== undefined
    )
    if (!hasContent) return

    try {
      localStorage.setItem(storageKey, JSON.stringify({
        data: dataToSave,
        timestamp: Date.now()
      }))
      hasDraft.value = true
      draftTimestamp.value = Date.now()
    } catch {
      // localStorage might be full
    }
  }

  // Clear draft from localStorage
  const clearDraft = () => {
    localStorage.removeItem(storageKey)
    hasDraft.value = false
    draftTimestamp.value = null
  }

  // Restore draft data
  const restoreDraft = () => {
    const draft = getDraft()
    if (draft && formData.value) {
      Object.assign(formData.value, draft.data)
      if (onRestore) onRestore(draft.data)
      clearDraft()
      return true
    }
    return false
  }

  // Check for existing draft on mount
  const checkForDraft = () => {
    const draft = getDraft()
    if (draft) {
      hasDraft.value = true
      draftTimestamp.value = draft.timestamp
    }
  }

  // Debounced save
  const debouncedSave = () => {
    clearTimeout(debounceTimer)
    debounceTimer = setTimeout(saveDraft, debounceMs)
  }

  // Watch form changes
  watch(formData, debouncedSave, { deep: true })

  onMounted(() => {
    checkForDraft()
  })

  onBeforeUnmount(() => {
    clearTimeout(debounceTimer)
  })

  // Format draft timestamp for display
  const formatDraftTime = () => {
    if (!draftTimestamp.value) return ''

    const date = new Date(draftTimestamp.value)
    const now = new Date()
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMins / 60)

    if (diffMins < 1) return 'just now'
    if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`
    return date.toLocaleDateString()
  }

  return {
    hasDraft,
    draftTimestamp,
    saveDraft,
    clearDraft,
    restoreDraft,
    checkForDraft,
    formatDraftTime
  }
}

/**
 * Hook for unsaved changes warning
 */
export function useUnsavedChanges(isDirty, message = 'You have unsaved changes. Are you sure you want to leave?') {
  const handleBeforeUnload = (e) => {
    if (isDirty.value) {
      e.preventDefault()
      e.returnValue = message
      return message
    }
  }

  onMounted(() => {
    window.addEventListener('beforeunload', handleBeforeUnload)
  })

  onBeforeUnmount(() => {
    window.removeEventListener('beforeunload', handleBeforeUnload)
  })

  return {
    // Method to manually check if navigation should be blocked
    shouldBlock: () => isDirty.value
  }
}
