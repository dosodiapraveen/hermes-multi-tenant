import BaseButton from '../components/ui/BaseButton.vue'
import BaseIcon from '../components/ui/BaseIcon.vue'

export default {
  title: 'UI/BaseButton',
  component: BaseButton,
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['primary', 'secondary', 'outline', 'ghost', 'danger', 'loading'],
      description: 'Button style variant',
    },
    size: {
      control: 'select',
      options: ['sm', 'md', 'lg'],
      description: 'Button size',
    },
    icon: {
      control: 'text',
      description: 'Icon name to display',
    },
    disabled: {
      control: 'boolean',
      description: 'Disabled state',
    },
    loading: {
      control: 'boolean',
      description: 'Loading state',
    },
  },
}

// Primary button
export const Primary = {
  args: {
    variant: 'primary',
    default: 'Primary Button',
  },
  render: (args) => ({
    components: { BaseButton },
    setup() { return { args } },
    template: '<BaseButton v-bind="args">Primary Button</BaseButton>',
  }),
}

// Secondary button
export const Secondary = {
  args: {
    variant: 'secondary',
  },
  render: (args) => ({
    components: { BaseButton },
    setup() { return { args } },
    template: '<BaseButton v-bind="args">Secondary Button</BaseButton>',
  }),
}

// Outline button
export const Outline = {
  args: {
    variant: 'outline',
  },
  render: (args) => ({
    components: { BaseButton },
    setup() { return { args } },
    template: '<BaseButton v-bind="args">Outline Button</BaseButton>',
  }),
}

// Ghost button
export const Ghost = {
  args: {
    variant: 'ghost',
  },
  render: (args) => ({
    components: { BaseButton },
    setup() { return { args } },
    template: '<BaseButton v-bind="args">Ghost Button</BaseButton>',
  }),
}

// Danger button
export const Danger = {
  args: {
    variant: 'danger',
  },
  render: (args) => ({
    components: { BaseButton },
    setup() { return { args } },
    template: '<BaseButton v-bind="args">Danger Button</BaseButton>',
  }),
}

// With icon
export const WithIcon = {
  args: {
    variant: 'primary',
    icon: 'plus',
  },
  render: (args) => ({
    components: { BaseButton },
    setup() { return { args } },
    template: '<BaseButton v-bind="args">Add Item</BaseButton>',
  }),
}

// Loading state
export const Loading = {
  args: {
    variant: 'primary',
    loading: true,
  },
  render: (args) => ({
    components: { BaseButton },
    setup() { return { args } },
    template: '<BaseButton v-bind="args">Loading...</BaseButton>',
  }),
}

// All sizes
export const Sizes = {
  render: () => ({
    components: { BaseButton },
    template: `
      <div style="display: flex; gap: 12px; align-items: center;">
        <BaseButton size="sm">Small</BaseButton>
        <BaseButton size="md">Medium</BaseButton>
        <BaseButton size="lg">Large</BaseButton>
      </div>
    `,
  }),
}

// All variants
export const AllVariants = {
  render: () => ({
    components: { BaseButton },
    template: `
      <div style="display: flex; gap: 12px; flex-wrap: wrap;">
        <BaseButton variant="primary">Primary</BaseButton>
        <BaseButton variant="secondary">Secondary</BaseButton>
        <BaseButton variant="outline">Outline</BaseButton>
        <BaseButton variant="ghost">Ghost</BaseButton>
        <BaseButton variant="danger">Danger</BaseButton>
        <BaseButton variant="primary" loading>Loading</BaseButton>
        <BaseButton variant="primary" disabled>Disabled</BaseButton>
      </div>
    `,
  }),
}
