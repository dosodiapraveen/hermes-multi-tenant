import { BaseBadge } from '@design-system/components/ui'

export default {
  title: 'UI/BaseBadge',
  component: BaseBadge,
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['primary', 'success', 'warning', 'error', 'info', 'secondary'],
      description: 'Badge color variant',
    },
    size: {
      control: 'select',
      options: ['sm', 'md', 'lg'],
      description: 'Badge size',
    },
    pill: {
      control: 'boolean',
      description: 'Pill shape (rounded)',
    },
    label: {
      control: 'text',
      description: 'Badge text',
    },
  },
}

export const Primary = {
  args: {
    variant: 'primary',
    label: 'Primary',
  },
}

export const Success = {
  args: {
    variant: 'success',
    label: 'Success',
  },
}

export const Warning = {
  args: {
    variant: 'warning',
    label: 'Warning',
  },
}

export const Error = {
  args: {
    variant: 'error',
    label: 'Error',
  },
}

export const Info = {
  args: {
    variant: 'info',
    label: 'Info',
  },
}

export const Secondary = {
  args: {
    variant: 'secondary',
    label: 'Secondary',
  },
}

export const Pill = {
  args: {
    variant: 'primary',
    label: 'Pill Badge',
    pill: true,
  },
}

export const AllVariants = {
  render: () => ({
    components: { BaseBadge },
    template: `
      <div style="display: flex; gap: 12px; flex-wrap: wrap;">
        <BaseBadge variant="primary" label="Primary" />
        <BaseBadge variant="success" label="Success" />
        <BaseBadge variant="warning" label="Warning" />
        <BaseBadge variant="error" label="Error" />
        <BaseBadge variant="info" label="Info" />
        <BaseBadge variant="secondary" label="Secondary" />
      </div>
    `,
  }),
}

export const Sizes = {
  render: () => ({
    components: { BaseBadge },
    template: `
      <div style="display: flex; gap: 12px; align-items: center;">
        <BaseBadge variant="primary" label="Small" size="sm" />
        <BaseBadge variant="primary" label="Medium" size="md" />
        <BaseBadge variant="primary" label="Large" size="lg" />
      </div>
    `,
  }),
}

export const StatusBadges = {
  render: () => ({
    components: { BaseBadge },
    template: `
      <div style="display: flex; gap: 12px; flex-wrap: wrap;">
        <BaseBadge variant="success" label="Active" pill />
        <BaseBadge variant="warning" label="Pending" pill />
        <BaseBadge variant="error" label="Failed" pill />
        <BaseBadge variant="secondary" label="Archived" pill />
        <BaseBadge variant="info" label="In Progress" pill />
      </div>
    `,
  }),
}
