import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseButton from '@design-system/components/ui/BaseButton.vue'

describe('BaseButton', () => {
  it('renders slot content', () => {
    const wrapper = mount(BaseButton, {
      slots: {
        default: 'Click Me'
      }
    })
    expect(wrapper.text()).toContain('Click Me')
  })

  it('applies primary variant by default', () => {
    const wrapper = mount(BaseButton)
    expect(wrapper.classes()).toContain('btn-primary')
  })

  it('applies variant class', () => {
    const wrapper = mount(BaseButton, {
      props: { variant: 'danger' }
    })
    expect(wrapper.classes()).toContain('btn-danger')
  })

  it('applies size class', () => {
    const wrapper = mount(BaseButton, {
      props: { size: 'lg' }
    })
    expect(wrapper.classes()).toContain('btn-lg')
  })

  it('emits click event when clicked', async () => {
    const wrapper = mount(BaseButton)
    await wrapper.trigger('click')
    expect(wrapper.emitted('click')).toBeTruthy()
    expect(wrapper.emitted('click').length).toBeGreaterThanOrEqual(1)
  })

  it('does not emit click when disabled', async () => {
    const wrapper = mount(BaseButton, {
      props: { disabled: true }
    })
    await wrapper.trigger('click')
    expect(wrapper.emitted('click')).toBeFalsy()
  })

  it('does not emit click when loading', async () => {
    const wrapper = mount(BaseButton, {
      props: { loading: true }
    })
    await wrapper.trigger('click')
    expect(wrapper.emitted('click')).toBeFalsy()
  })

  it('is disabled when disabled prop is true', () => {
    const wrapper = mount(BaseButton, {
      props: { disabled: true }
    })
    expect(wrapper.attributes('disabled')).toBeDefined()
  })

  it('is disabled when loading prop is true', () => {
    const wrapper = mount(BaseButton, {
      props: { loading: true }
    })
    expect(wrapper.attributes('disabled')).toBeDefined()
  })

  it('shows loading spinner when loading', () => {
    const wrapper = mount(BaseButton, {
      props: { loading: true }
    })
    expect(wrapper.classes()).toContain('btn-loading')
    expect(wrapper.find('.btn-spinner').exists()).toBe(true)
  })

  it('applies block class when block prop is true', () => {
    const wrapper = mount(BaseButton, {
      props: { block: true }
    })
    expect(wrapper.classes()).toContain('btn-block')
  })

  it('renders with icon when icon prop is provided', () => {
    const wrapper = mount(BaseButton, {
      props: { icon: 'plus' }
    })
    expect(wrapper.find('.btn-icon').exists()).toBe(true)
  })

  it('positions icon on left by default', () => {
    const wrapper = mount(BaseButton, {
      props: { icon: 'plus' }
    })
    expect(wrapper.find('.btn-icon-left').exists()).toBe(true)
  })

  it('positions icon on right when iconPosition is right', () => {
    const wrapper = mount(BaseButton, {
      props: { icon: 'plus', iconPosition: 'right' }
    })
    expect(wrapper.find('.btn-icon-right').exists()).toBe(true)
  })

  it('applies icon-only class when iconOnly prop is true', () => {
    const wrapper = mount(BaseButton, {
      props: { icon: 'plus', iconOnly: true }
    })
    expect(wrapper.classes()).toContain('btn-icon-only')
  })

  it('sets correct button type', () => {
    const wrapper = mount(BaseButton, {
      props: { type: 'submit' }
    })
    expect(wrapper.attributes('type')).toBe('submit')
  })

  it('defaults to type button', () => {
    const wrapper = mount(BaseButton)
    expect(wrapper.attributes('type')).toBe('button')
  })
})
