/**
 * Unit Tests for AppButton Component
 * Testing common button component functionality
 */

import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import AppButton from '@/components/common/AppButton.vue'

describe('AppButton Component', () => {
  it('should render with default props', () => {
    const wrapper = mount(AppButton, {
      slots: {
        default: 'Click me'
      }
    })

    expect(wrapper.find('.app-button').exists()).toBe(true)
    expect(wrapper.text()).toBe('Click me')
  })

  it('should apply type class', () => {
    const wrapper = mount(AppButton, {
      props: { type: 'primary' },
      slots: {
        default: 'Primary'
      }
    })

    expect(wrapper.find('.is-primary').exists()).toBe(true)
  })

  it('should apply size class', () => {
    const wrapper = mount(AppButton, {
      props: { size: 'large' },
      slots: {
        default: 'Large'
      }
    })

    expect(wrapper.find('.is-large').exists()).toBe(true)
  })

  it('should apply block class when block is true', () => {
    const wrapper = mount(AppButton, {
      props: { block: true },
      slots: {
        default: 'Block'
      }
    })

    expect(wrapper.find('.is-block').exists()).toBe(true)
  })

  it('should be disabled when disabled prop is true', () => {
    const wrapper = mount(AppButton, {
      props: { disabled: true },
      slots: {
        default: 'Disabled'
      }
    })

    const button = wrapper.find('button')
    expect(button.attributes('disabled')).toBeDefined()
  })

  it('should be disabled when loading', () => {
    const wrapper = mount(AppButton, {
      props: { loading: true },
      slots: {
        default: 'Loading'
      }
    })

    const button = wrapper.find('button')
    expect(button.attributes('disabled')).toBeDefined()
  })

  it('should emit click event when clicked', async () => {
    const wrapper = mount(AppButton, {
      slots: {
        default: 'Click me'
      }
    })

    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted('click')).toBeTruthy()
    expect(wrapper.emitted('click')?.length).toBe(1)
  })

  it('should not emit click when disabled', async () => {
    const wrapper = mount(AppButton, {
      props: { disabled: true },
      slots: {
        default: 'Disabled'
      }
    })

    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted('click')).toBeFalsy()
  })

  it('should not emit click when loading', async () => {
    const wrapper = mount(AppButton, {
      props: { loading: true },
      slots: {
        default: 'Loading'
      }
    })

    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted('click')).toBeFalsy()
  })

  it('should render icon slot', () => {
    const wrapper = mount(AppButton, {
      slots: {
        icon: '<span class="icon">🔥</span>',
        default: 'With Icon'
      }
    })

    expect(wrapper.find('.icon').exists()).toBe(true)
    expect(wrapper.text()).toContain('With Icon')
  })

  it('should pass through all attributes', () => {
    const wrapper = mount(AppButton, {
      attrs: {
        'data-testid': 'test-button',
        'aria-label': 'Test button'
      },
      slots: {
        default: 'Attributes'
      }
    })

    const button = wrapper.find('button')
    expect(button.attributes('data-testid')).toBe('test-button')
    expect(button.attributes('aria-label')).toBe('Test button')
  })
})
