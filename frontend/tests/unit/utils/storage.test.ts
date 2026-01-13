/**
 * Unit Tests for Storage Utilities
 * Testing localStorage and sessionStorage wrapper functions
 */

import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { storage, session } from '@/utils/storage'

describe('LocalStorage Utilities', () => {
  beforeEach(() => {
    storage.clear()
  })

  it('should store and retrieve values', () => {
    storage.set('test-key', 'test-value')
    expect(storage.get('test-key')).toBe('test-value')
  })

  it('should store complex objects', () => {
    const obj = { name: 'test', count: 42, nested: { value: true } }
    storage.set('obj-key', obj)
    expect(storage.get('obj-key')).toEqual(obj)
  })

  it('should store arrays', () => {
    const arr = [1, 2, 3, 'four', { five: 5 }]
    storage.set('arr-key', arr)
    expect(storage.get('arr-key')).toEqual(arr)
  })

  it('should return null for non-existent keys', () => {
    expect(storage.get('non-existent')).toBeNull()
  })

  it('should return default value for non-existent keys', () => {
    expect(storage.get('non-existent', 'default')).toBe('default')
    expect(storage.get('non-existent', 0)).toBe(0)
  })

  it('should remove values', () => {
    storage.set('delete-key', 'value')
    expect(storage.get('delete-key')).toBe('value')
    storage.remove('delete-key')
    expect(storage.get('delete-key')).toBeNull()
  })

  it('should clear all app storage', () => {
    storage.set('key1', 'value1')
    storage.set('key2', 'value2')
    storage.clear()
    expect(storage.get('key1')).toBeNull()
    expect(storage.get('key2')).toBeNull()
  })

  it('should handle JSON parse errors gracefully', () => {
    // Simulate corrupted data
    localStorage.setItem('simfocus_corrupted', 'invalid json{')
    expect(storage.get('corrupted')).toBeNull()
  })

  it('should handle storage quota exceeded', () => {
    // Mock localStorage.setItem to throw error
    const originalSetItem = localStorage.setItem
    localStorage.setItem = vi.fn(() => {
      throw new Error('QuotaExceededError')
    })

    const result = storage.set('key', 'value')
    expect(result).toBe(false)

    localStorage.setItem = originalSetItem
  })

  it('should use prefix for keys', () => {
    storage.set('test', 'value')
    expect(localStorage.getItem('simfocus_test')).toBeTruthy()
    expect(localStorage.getItem('test')).toBeNull()
  })
})

describe('SessionStorage Utilities', () => {
  beforeEach(() => {
    session.clear()
  })

  it('should store and retrieve values', () => {
    session.set('test-key', 'test-value')
    expect(session.get('test-key')).toBe('test-value')
  })

  it('should store complex objects', () => {
    const obj = { name: 'test', count: 42 }
    session.set('obj-key', obj)
    expect(session.get('obj-key')).toEqual(obj)
  })

  it('should return null for non-existent keys', () => {
    expect(session.get('non-existent')).toBeNull()
  })

  it('should return default value for non-existent keys', () => {
    expect(session.get('non-existent', 'default')).toBe('default')
  })

  it('should remove values', () => {
    session.set('delete-key', 'value')
    expect(session.get('delete-key')).toBe('value')
    session.remove('delete-key')
    expect(session.get('delete-key')).toBeNull()
  })

  it('should clear all app session storage', () => {
    session.set('key1', 'value1')
    session.set('key2', 'value2')
    session.clear()
    expect(session.get('key1')).toBeNull()
    expect(session.get('key2')).toBeNull()
  })

  it('should handle JSON parse errors gracefully', () => {
    sessionStorage.setItem('simfocus_corrupted', 'invalid json{')
    expect(session.get('corrupted')).toBeNull()
  })

  it('should use prefix for keys', () => {
    session.set('test', 'value')
    expect(sessionStorage.getItem('simfocus_test')).toBeTruthy()
    expect(sessionStorage.getItem('test')).toBeNull()
  })
})

describe('Storage Independence', () => {
  it('should keep localStorage and sessionStorage separate', () => {
    storage.set('key', 'local-value')
    session.set('key', 'session-value')

    expect(storage.get('key')).toBe('local-value')
    expect(session.get('key')).toBe('session-value')
  })

  it('should not interfere between different keys', () => {
    storage.set('key1', { data: 'first' })
    storage.set('key2', { data: 'second' })

    expect(storage.get('key1')).toEqual({ data: 'first' })
    expect(storage.get('key2')).toEqual({ data: 'second' })
  })
})
