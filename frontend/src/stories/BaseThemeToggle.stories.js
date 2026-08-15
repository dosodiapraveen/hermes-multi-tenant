import { BaseThemeToggle } from '@design-system/components/ui'

export default {
  title: 'UI/BaseThemeToggle',
  component: BaseThemeToggle,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component: 'A toggle switch for switching between light and dark themes. Saves preference to localStorage and respects system preference by default.',
      },
    },
  },
}

export const Default = {
  render: () => ({
    components: { BaseThemeToggle },
    template: `
      <div style="display: flex; align-items: center; gap: 16px;">
        <BaseThemeToggle />
        <span style="color: var(--color-text-secondary); font-size: 14px;">
          Click to toggle between light and dark themes
        </span>
      </div>
    `,
  }),
}

export const WithLabel = {
  render: () => ({
    components: { BaseThemeToggle },
    template: `
      <div style="display: flex; align-items: center; gap: 12px; padding: 16px; background: var(--color-surface); border-radius: 8px; border: 1px solid var(--color-border);">
        <span style="color: var(--color-text-primary); font-size: 14px; font-weight: 500;">
          Dark Mode
        </span>
        <BaseThemeToggle />
      </div>
    `,
  }),
}

export const InHeader = {
  render: () => ({
    components: { BaseThemeToggle },
    template: `
      <div style="display: flex; align-items: center; justify-content: space-between; padding: 12px 20px; background: var(--color-surface); border-radius: 12px; border: 1px solid var(--color-border);">
        <div style="display: flex; align-items: center; gap: 12px;">
          <div style="width: 32px; height: 32px; background: linear-gradient(135deg, var(--color-primary-500), var(--color-primary-400)); border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">H</div>
          <span style="font-weight: 600; color: var(--color-text-primary);">Hermes</span>
        </div>
        <div style="display: flex; align-items: center; gap: 16px;">
          <BaseThemeToggle />
          <button style="padding: 8px 16px; background: transparent; border: 1px solid var(--color-border); border-radius: 8px; color: var(--color-text-secondary); cursor: pointer;">
            Logout
          </button>
        </div>
      </div>
    `,
  }),
}
