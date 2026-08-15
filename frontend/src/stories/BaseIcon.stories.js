import BaseIcon from '../components/ui/BaseIcon.vue'

export default {
  title: 'UI/BaseIcon',
  component: BaseIcon,
  tags: ['autodocs'],
  argTypes: {
    name: {
      control: 'select',
      options: [
        'home', 'dashboard', 'lightbulb', 'file-text', 'calendar', 'clock',
        'folder', 'settings', 'activity', 'brain', 'search', 'plus', 'x',
        'check', 'check-circle', 'alert-circle', 'x-circle', 'info',
        'trash', 'edit', 'eye', 'eye-off', 'map-pin', 'chevron-down',
        'chevron-up', 'chevron-left', 'chevron-right', 'arrow-left',
        'arrow-right', 'user', 'users', 'log-out', 'mail', 'bell', 'tag',
        'filter', 'loader', 'refresh', 'external-link', 'copy',
        'more-horizontal', 'more-vertical', 'sun', 'moon', 'star', 'heart',
        'download', 'upload', 'file', 'image', 'link', 'share', 'bookmark',
        'archive', 'globe', 'dollar-sign', 'credit-card', 'shopping-cart',
        'briefcase', 'zap', 'shield', 'lock', 'unlock', 'key', 'send',
        'message-circle', 'phone', 'video', 'mic', 'camera', 'play',
        'pause', 'volume', 'wifi', 'cloud', 'database', 'server',
        'terminal', 'code', 'git-branch', 'target', 'award', 'trending-up',
        'trending-down', 'percent', 'hash', 'at-sign', 'paperclip',
        'layers', 'grid', 'list', 'menu', 'sidebar', 'maximize', 'minimize'
      ],
      description: 'Icon name',
    },
    size: {
      control: { type: 'range', min: 12, max: 48, step: 4 },
      description: 'Icon size in pixels',
    },
    strokeWidth: {
      control: { type: 'range', min: 1, max: 4, step: 0.5 },
      description: 'Stroke width',
    },
    spin: {
      control: 'boolean',
      description: 'Spin animation',
    },
  },
}

export const Default = {
  args: {
    name: 'home',
    size: 24,
    strokeWidth: 2,
  },
}

export const AllIcons = {
  render: () => ({
    components: { BaseIcon },
    setup() {
      const icons = [
        'home', 'dashboard', 'lightbulb', 'file-text', 'calendar', 'clock',
        'folder', 'settings', 'activity', 'brain', 'search', 'plus', 'x',
        'check', 'check-circle', 'alert-circle', 'x-circle', 'info',
        'trash', 'edit', 'eye', 'eye-off', 'map-pin', 'chevron-down',
        'chevron-up', 'chevron-left', 'chevron-right', 'arrow-left',
        'arrow-right', 'user', 'users', 'log-out', 'mail', 'bell', 'tag',
        'filter', 'loader', 'refresh', 'external-link', 'copy',
        'more-horizontal', 'more-vertical', 'sun', 'moon', 'star', 'heart',
        'download', 'upload', 'file', 'image', 'link', 'share', 'bookmark',
        'archive', 'globe', 'dollar-sign', 'credit-card', 'shopping-cart',
        'briefcase', 'zap', 'shield', 'lock', 'unlock', 'key', 'send',
        'message-circle', 'phone', 'video', 'mic', 'camera', 'play',
        'pause', 'volume', 'wifi', 'cloud', 'database', 'server',
        'terminal', 'code', 'git-branch', 'target', 'award', 'trending-up',
        'trending-down', 'percent', 'hash', 'at-sign', 'paperclip',
        'layers', 'grid', 'list', 'menu', 'sidebar', 'maximize', 'minimize'
      ]
      return { icons }
    },
    template: `
      <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(100px, 1fr)); gap: 16px;">
        <div v-for="icon in icons" :key="icon" style="display: flex; flex-direction: column; align-items: center; gap: 8px; padding: 12px; background: var(--color-surface); border-radius: 8px; border: 1px solid var(--color-border);">
          <BaseIcon :name="icon" :size="24" />
          <span style="font-size: 11px; color: var(--color-text-tertiary);">{{ icon }}</span>
        </div>
      </div>
    `,
  }),
}

export const Sizes = {
  render: () => ({
    components: { BaseIcon },
    template: `
      <div style="display: flex; gap: 24px; align-items: center;">
        <div style="text-align: center;">
          <BaseIcon name="star" :size="16" />
          <div style="font-size: 11px; color: var(--color-text-tertiary); margin-top: 4px;">16px</div>
        </div>
        <div style="text-align: center;">
          <BaseIcon name="star" :size="20" />
          <div style="font-size: 11px; color: var(--color-text-tertiary); margin-top: 4px;">20px</div>
        </div>
        <div style="text-align: center;">
          <BaseIcon name="star" :size="24" />
          <div style="font-size: 11px; color: var(--color-text-tertiary); margin-top: 4px;">24px</div>
        </div>
        <div style="text-align: center;">
          <BaseIcon name="star" :size="32" />
          <div style="font-size: 11px; color: var(--color-text-tertiary); margin-top: 4px;">32px</div>
        </div>
        <div style="text-align: center;">
          <BaseIcon name="star" :size="48" />
          <div style="font-size: 11px; color: var(--color-text-tertiary); margin-top: 4px;">48px</div>
        </div>
      </div>
    `,
  }),
}

export const Spinning = {
  args: {
    name: 'loader',
    size: 24,
    spin: true,
  },
}
