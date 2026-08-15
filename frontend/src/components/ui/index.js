// Hermes Design System - UI Components
// Export all base components for easy importing

export { default as BaseIcon } from './BaseIcon.vue'
export { default as BaseButton } from './BaseButton.vue'
export { default as BaseInput } from './BaseInput.vue'
export { default as BaseSelect } from './BaseSelect.vue'
export { default as BaseModal } from './BaseModal.vue'
export { default as BaseCard } from './BaseCard.vue'
export { default as BaseBadge } from './BaseBadge.vue'
export { default as BaseToast } from './BaseToast.vue'
export { default as BaseToggle } from './BaseToggle.vue'
export { default as BaseTooltip } from './BaseTooltip.vue'
export { default as BaseDateTimePicker } from './BaseDateTimePicker.vue'
export { default as BaseEmptyState } from './BaseEmptyState.vue'
export { default as BaseSearchFilter } from './BaseSearchFilter.vue'
export { default as BaseChart } from './BaseChart.vue'
export { default as BaseThemeToggle } from './BaseThemeToggle.vue'
export { default as BaseConfirmDialog } from './BaseConfirmDialog.vue'

// Plugin for global registration
export const HermesUI = {
  install(app) {
    // Import all components
    const components = {
      BaseIcon: () => import('./BaseIcon.vue'),
      BaseButton: () => import('./BaseButton.vue'),
      BaseInput: () => import('./BaseInput.vue'),
      BaseSelect: () => import('./BaseSelect.vue'),
      BaseModal: () => import('./BaseModal.vue'),
      BaseCard: () => import('./BaseCard.vue'),
      BaseBadge: () => import('./BaseBadge.vue'),
      BaseToast: () => import('./BaseToast.vue'),
      BaseToggle: () => import('./BaseToggle.vue'),
      BaseTooltip: () => import('./BaseTooltip.vue'),
      BaseDateTimePicker: () => import('./BaseDateTimePicker.vue'),
      BaseEmptyState: () => import('./BaseEmptyState.vue'),
      BaseSearchFilter: () => import('./BaseSearchFilter.vue'),
      BaseThemeToggle: () => import('./BaseThemeToggle.vue'),
      BaseConfirmDialog: () => import('./BaseConfirmDialog.vue')
    }

    // Register components globally (async)
    Object.entries(components).forEach(([name, component]) => {
      app.component(name, () => component())
    })
  }
}

export default HermesUI
