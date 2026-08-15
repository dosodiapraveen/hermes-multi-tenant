/**
 * Toast composable for showing notifications across the app
 *
 * Usage:
 * 1. In UserPortalNew.vue, assign the toast ref:
 *    <BaseToast ref="toastRef" position="bottom-right" />
 *    const toastRef = ref(null)
 *    provide('toast', toastRef)
 *
 * 2. In child components or API calls:
 *    import { useToast } from '@/composables/useToast'
 *    const toast = useToast()
 *    toast.success('Item saved successfully!')
 */

import { inject, ref } from 'vue'

// Global toast ref for cases where injection isn't available
let globalToastRef = null

export function setGlobalToastRef(toastRef) {
  globalToastRef = toastRef
}

export function useToast() {
  // Try to inject from parent first
  const injectedToast = inject('toast', null)

  const getToastInstance = () => {
    const toastRef = injectedToast?.value || globalToastRef?.value
    if (!toastRef) {
      console.warn('Toast component not available. Make sure BaseToast is mounted and ref is set.')
      return null
    }
    return toastRef
  }

  return {
    success(message, options = {}) {
      const toast = getToastInstance()
      if (toast) {
        return toast.success(message, options)
      }
    },

    error(message, options = {}) {
      const toast = getToastInstance()
      if (toast) {
        return toast.error(message, options)
      }
    },

    warning(message, options = {}) {
      const toast = getToastInstance()
      if (toast) {
        return toast.warning(message, options)
      }
    },

    info(message, options = {}) {
      const toast = getToastInstance()
      if (toast) {
        return toast.info(message, options)
      }
    },

    add(options) {
      const toast = getToastInstance()
      if (toast) {
        return toast.add(options)
      }
    },

    dismiss(id) {
      const toast = getToastInstance()
      if (toast) {
        toast.dismiss(id)
      }
    },

    dismissAll() {
      const toast = getToastInstance()
      if (toast) {
        toast.dismissAll()
      }
    }
  }
}

/**
 * Toast messages for common API operations
 */
export const toastMessages = {
  // Notes
  noteSaved: 'Note saved successfully',
  noteDeleted: 'Note deleted',
  noteError: 'Failed to save note',

  // Ideas
  ideaSaved: 'Idea saved successfully',
  ideaDeleted: 'Idea deleted',
  ideaError: 'Failed to save idea',

  // Events
  eventSaved: 'Event scheduled successfully',
  eventDeleted: 'Event deleted',
  eventError: 'Failed to save event',

  // Reminders
  reminderSaved: 'Reminder set successfully',
  reminderDeleted: 'Reminder deleted',
  reminderToggled: 'Reminder updated',
  reminderError: 'Failed to save reminder',

  // Projects
  projectSaved: 'Project saved successfully',
  projectDeleted: 'Project deleted',
  projectError: 'Failed to save project',
  researchAdded: 'Research added to project',
  researchDeleted: 'Research removed',

  // Jobs
  jobSaved: 'Job saved successfully',
  jobDeleted: 'Job deleted',
  jobToggled: 'Job updated',
  jobError: 'Failed to save job',

  // Personality
  personalitySaved: 'Personality settings saved',
  personalityError: 'Failed to save personality settings',

  // Generic
  saved: 'Changes saved',
  deleted: 'Item deleted',
  error: 'Something went wrong. Please try again.',
  networkError: 'Network error. Please check your connection.',
  sessionExpired: 'Your session has expired. Please log in again.'
}

export default useToast
