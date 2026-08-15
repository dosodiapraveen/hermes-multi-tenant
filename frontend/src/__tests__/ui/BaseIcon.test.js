import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseIcon from '@design-system/components/ui/BaseIcon.vue'

describe('BaseIcon', () => {
  it('renders svg element', () => {
    const wrapper = mount(BaseIcon, {
      props: { name: 'home' }
    })
    expect(wrapper.find('svg').exists()).toBe(true)
  })

  it('applies correct size', () => {
    const wrapper = mount(BaseIcon, {
      props: { name: 'home', size: 32 }
    })
    expect(wrapper.attributes('width')).toBe('32')
    expect(wrapper.attributes('height')).toBe('32')
  })

  it('defaults to size 20', () => {
    const wrapper = mount(BaseIcon, {
      props: { name: 'home' }
    })
    expect(wrapper.attributes('width')).toBe('20')
    expect(wrapper.attributes('height')).toBe('20')
  })

  it('applies spin class when spin prop is true', () => {
    const wrapper = mount(BaseIcon, {
      props: { name: 'loader', spin: true }
    })
    expect(wrapper.classes()).toContain('spin')
  })

  it('applies stroke width', () => {
    const wrapper = mount(BaseIcon, {
      props: { name: 'home', strokeWidth: 3 }
    })
    expect(wrapper.attributes('stroke-width')).toBe('3')
  })

  it('sets aria-label when provided', () => {
    const wrapper = mount(BaseIcon, {
      props: { name: 'home', ariaLabel: 'Home icon' }
    })
    expect(wrapper.attributes('aria-label')).toBe('Home icon')
  })

  it('is hidden from screen readers when no aria-label', () => {
    const wrapper = mount(BaseIcon, {
      props: { name: 'home' }
    })
    expect(wrapper.attributes('aria-hidden')).toBe('true')
  })

  it('renders home icon', () => {
    const wrapper = mount(BaseIcon, {
      props: { name: 'home' }
    })
    expect(wrapper.html()).toContain('path')
  })

  it('renders search icon', () => {
    const wrapper = mount(BaseIcon, {
      props: { name: 'search' }
    })
    expect(wrapper.html()).toContain('circle')
    expect(wrapper.html()).toContain('line')
  })

  it('renders fallback for unknown icon', () => {
    const wrapper = mount(BaseIcon, {
      props: { name: 'unknown-icon' }
    })
    // Fallback is a question mark in circle
    expect(wrapper.html()).toContain('circle')
  })

  it('renders sun icon for theme toggle', () => {
    const wrapper = mount(BaseIcon, {
      props: { name: 'sun' }
    })
    expect(wrapper.html()).toContain('circle')
  })

  it('renders moon icon for theme toggle', () => {
    const wrapper = mount(BaseIcon, {
      props: { name: 'moon' }
    })
    expect(wrapper.html()).toContain('path')
  })
})
