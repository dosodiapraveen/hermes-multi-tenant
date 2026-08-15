import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseThemeToggle from '../BaseThemeToggle.vue'

describe('BaseThemeToggle', () => {
  let localStorageMock
  let matchMediaMock

  beforeEach(() => {
    // Mock localStorage
    localStorageMock = {
      getItem: vi.fn(),
      setItem: vi.fn(),
      removeItem: vi.fn()
    }
    Object.defineProperty(window, 'localStorage', { value: localStorageMock })

    // Mock matchMedia
    matchMediaMock = vi.fn().mockImplementation(query => ({
      matches: false,
      media: query,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
    }))
    Object.defineProperty(window, 'matchMedia', { value: matchMediaMock })
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('renders toggle button', () => {
    const wrapper = mount(BaseThemeToggle)
    expect(wrapper.find('button').exists()).toBe(true)
  })

  it('has accessible aria-label', () => {
    const wrapper = mount(BaseThemeToggle)
    expect(wrapper.attributes('aria-label')).toBeTruthy()
  })

  it('toggles dark mode on click', async () => {
    const wrapper = mount(BaseThemeToggle)
    expect(wrapper.classes()).not.toContain('is-dark')

    await wrapper.trigger('click')
    expect(wrapper.classes()).toContain('is-dark')
  })

  it('toggles back to light mode on second click', async () => {
    const wrapper = mount(BaseThemeToggle)

    await wrapper.trigger('click')
    expect(wrapper.classes()).toContain('is-dark')

    await wrapper.trigger('click')
    expect(wrapper.classes()).not.toContain('is-dark')
  })

  it('saves preference to localStorage', async () => {
    const wrapper = mount(BaseThemeToggle)

    await wrapper.trigger('click')
    expect(localStorageMock.setItem).toHaveBeenCalledWith('hermes-theme', 'dark')
  })

  it('emits change event with theme value', async () => {
    const wrapper = mount(BaseThemeToggle)

    await wrapper.trigger('click')
    expect(wrapper.emitted('change')).toBeTruthy()
    expect(wrapper.emitted('change')[0]).toEqual(['dark'])
  })

  it('reads theme from localStorage on mount', () => {
    localStorageMock.getItem.mockReturnValue('dark')
    const wrapper = mount(BaseThemeToggle)

    expect(localStorageMock.getItem).toHaveBeenCalledWith('hermes-theme')
  })

  it('respects system preference when no stored preference', () => {
    matchMediaMock.mockImplementation(query => ({
      matches: true, // System prefers dark
      media: query,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
    }))

    const wrapper = mount(BaseThemeToggle)
    expect(wrapper.vm.isDark).toBe(true)
  })

  it('renders sun and moon icons', () => {
    const wrapper = mount(BaseThemeToggle)
    expect(wrapper.find('.sun').exists()).toBe(true)
    expect(wrapper.find('.moon').exists()).toBe(true)
  })

  it('renders toggle track', () => {
    const wrapper = mount(BaseThemeToggle)
    expect(wrapper.find('.toggle-track').exists()).toBe(true)
  })

  it('renders toggle thumb', () => {
    const wrapper = mount(BaseThemeToggle)
    expect(wrapper.find('.toggle-thumb').exists()).toBe(true)
  })
})
