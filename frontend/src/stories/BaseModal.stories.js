import { ref } from 'vue'
import BaseModal from '../components/ui/BaseModal.vue'
import BaseButton from '../components/ui/BaseButton.vue'
import BaseInput from '../components/ui/BaseInput.vue'

export default {
  title: 'UI/BaseModal',
  component: BaseModal,
  tags: ['autodocs'],
  argTypes: {
    title: {
      control: 'text',
      description: 'Modal title',
    },
    size: {
      control: 'select',
      options: ['sm', 'md', 'lg'],
      description: 'Modal size',
    },
    modelValue: {
      control: 'boolean',
      description: 'Show/hide modal',
    },
  },
}

export const Default = {
  render: () => ({
    components: { BaseModal, BaseButton },
    setup() {
      const isOpen = ref(false)
      return { isOpen }
    },
    template: `
      <div>
        <BaseButton @click="isOpen = true">Open Modal</BaseButton>
        <BaseModal v-model="isOpen" title="Example Modal">
          <p style="color: var(--color-text-secondary); line-height: 1.6;">
            This is a basic modal with a title and some content. Click outside or press ESC to close.
          </p>
          <template #footer>
            <BaseButton variant="outline" @click="isOpen = false">Cancel</BaseButton>
            <BaseButton @click="isOpen = false">Confirm</BaseButton>
          </template>
        </BaseModal>
      </div>
    `,
  }),
}

export const WithForm = {
  render: () => ({
    components: { BaseModal, BaseButton, BaseInput },
    setup() {
      const isOpen = ref(false)
      return { isOpen }
    },
    template: `
      <div>
        <BaseButton @click="isOpen = true">Open Form Modal</BaseButton>
        <BaseModal v-model="isOpen" title="Create New Item">
          <div style="display: flex; flex-direction: column; gap: 16px;">
            <BaseInput label="Title" placeholder="Enter title" required />
            <BaseInput label="Description" placeholder="Enter description" type="textarea" :rows="3" />
          </div>
          <template #footer>
            <BaseButton variant="outline" @click="isOpen = false">Cancel</BaseButton>
            <BaseButton @click="isOpen = false">Save</BaseButton>
          </template>
        </BaseModal>
      </div>
    `,
  }),
}

export const SmallSize = {
  render: () => ({
    components: { BaseModal, BaseButton },
    setup() {
      const isOpen = ref(false)
      return { isOpen }
    },
    template: `
      <div>
        <BaseButton @click="isOpen = true">Open Small Modal</BaseButton>
        <BaseModal v-model="isOpen" title="Confirm Action" size="sm">
          <p style="color: var(--color-text-secondary);">Are you sure you want to proceed?</p>
          <template #footer>
            <BaseButton variant="outline" @click="isOpen = false">Cancel</BaseButton>
            <BaseButton variant="danger" @click="isOpen = false">Delete</BaseButton>
          </template>
        </BaseModal>
      </div>
    `,
  }),
}

export const LargeSize = {
  render: () => ({
    components: { BaseModal, BaseButton },
    setup() {
      const isOpen = ref(false)
      return { isOpen }
    },
    template: `
      <div>
        <BaseButton @click="isOpen = true">Open Large Modal</BaseButton>
        <BaseModal v-model="isOpen" title="Large Modal" size="lg">
          <div style="color: var(--color-text-secondary); line-height: 1.6;">
            <p>This is a large modal suitable for displaying more content.</p>
            <p style="margin-top: 16px;">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.</p>
            <p style="margin-top: 16px;">Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.</p>
          </div>
          <template #footer>
            <BaseButton variant="outline" @click="isOpen = false">Close</BaseButton>
          </template>
        </BaseModal>
      </div>
    `,
  }),
}

export const DangerConfirm = {
  render: () => ({
    components: { BaseModal, BaseButton },
    setup() {
      const isOpen = ref(false)
      return { isOpen }
    },
    template: `
      <div>
        <BaseButton variant="danger" @click="isOpen = true">Delete Item</BaseButton>
        <BaseModal v-model="isOpen" title="Delete Item">
          <p style="color: var(--color-text-secondary); line-height: 1.6;">
            Are you sure you want to delete this item? This action cannot be undone.
          </p>
          <template #footer>
            <BaseButton variant="outline" @click="isOpen = false">Cancel</BaseButton>
            <BaseButton variant="danger" @click="isOpen = false">Delete</BaseButton>
          </template>
        </BaseModal>
      </div>
    `,
  }),
}
