import BaseInput from '../components/ui/BaseInput.vue'

export default {
  title: 'UI/BaseInput',
  component: BaseInput,
  tags: ['autodocs'],
  argTypes: {
    type: {
      control: 'select',
      options: ['text', 'password', 'email', 'number', 'textarea'],
      description: 'Input type',
    },
    label: {
      control: 'text',
      description: 'Input label',
    },
    placeholder: {
      control: 'text',
      description: 'Placeholder text',
    },
    error: {
      control: 'text',
      description: 'Error message',
    },
    disabled: {
      control: 'boolean',
      description: 'Disabled state',
    },
    required: {
      control: 'boolean',
      description: 'Required field',
    },
  },
}

export const Default = {
  args: {
    label: 'Email',
    placeholder: 'Enter your email',
    type: 'text',
  },
}

export const WithValue = {
  args: {
    label: 'Username',
    modelValue: 'johndoe',
    type: 'text',
  },
}

export const Password = {
  args: {
    label: 'Password',
    placeholder: 'Enter password',
    type: 'password',
  },
}

export const WithError = {
  args: {
    label: 'Email',
    placeholder: 'Enter your email',
    type: 'email',
    modelValue: 'invalid-email',
    error: 'Please enter a valid email address',
  },
}

export const Disabled = {
  args: {
    label: 'Disabled Input',
    placeholder: 'Cannot edit',
    disabled: true,
  },
}

export const Required = {
  args: {
    label: 'Required Field',
    placeholder: 'This field is required',
    required: true,
  },
}

export const Textarea = {
  args: {
    label: 'Description',
    placeholder: 'Enter a description...',
    type: 'textarea',
    rows: 4,
  },
}

export const WithPrefixIcon = {
  args: {
    label: 'Search',
    placeholder: 'Search...',
    prefixIcon: 'search',
  },
}

export const AllTypes = {
  render: () => ({
    components: { BaseInput },
    template: `
      <div style="display: flex; flex-direction: column; gap: 20px; max-width: 400px;">
        <BaseInput label="Text" placeholder="Enter text" type="text" />
        <BaseInput label="Email" placeholder="email@example.com" type="email" />
        <BaseInput label="Password" placeholder="Enter password" type="password" />
        <BaseInput label="Number" placeholder="0" type="number" />
        <BaseInput label="Textarea" placeholder="Enter description..." type="textarea" :rows="3" />
      </div>
    `,
  }),
}
