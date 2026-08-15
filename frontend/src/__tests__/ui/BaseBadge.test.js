import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseBadge from '@design-system/components/ui/BaseBadge.vue'

describe('BaseBadge', () => {
  it('renders label text', () => {
    const wrapper = mount(BaseBadge, {
      props: { label: 'Test Badge' }
    })
    expect(wrapper.text()).toContain('Test Badge')
  })

  it('applies default variant by default', () => {
    const wrapper = mount(BaseBadge, {
      props: { label: 'Test' }
    })
    expect(wrapper.classes()).toContain('badge-default')
  })

  it('applies variant class', () => {
    const wrapper = mount(BaseBadge, {
      props: { label: 'Test', variant: 'success' }
    })
    expect(wrapper.classes()).toContain('badge-success')
  })

  it('applies error variant', () => {
    const wrapper = mount(BaseBadge, {
      props: { label: 'Error', variant: 'error' }
    })
    expect(wrapper.classes()).toContain('badge-error')
  })

  it('applies warning variant', () => {
    const wrapper = mount(BaseBadge, {
      props: { label: 'Warning', variant: 'warning' }
    })
    expect(wrapper.classes()).toContain('badge-warning')
  })

  it('applies info variant', () => {
    const wrapper = mount(BaseBadge, {
      props: { label: 'Info', variant: 'info' }
    })
    expect(wrapper.classes()).toContain('badge-info')
  })

  it('applies size class', () => {
    const wrapper = mount(BaseBadge, {
      props: { label: 'Test', size: 'sm' }
    })
    expect(wrapper.classes()).toContain('badge-sm')
  })

  it('applies pill class when pill prop is true', () => {
    const wrapper = mount(BaseBadge, {
      props: { label: 'Test', pill: true }
    })
    expect(wrapper.classes()).toContain('badge-pill')
  })

  it('renders slot content instead of label', () => {
    const wrapper = mount(BaseBadge, {
      slots: {
        default: 'Slot Content'
      }
    })
    expect(wrapper.text()).toContain('Slot Content')
  })
})
