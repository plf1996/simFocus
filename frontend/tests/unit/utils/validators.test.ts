/**
 * Unit Tests for Validation Utilities
 * Testing email, password, URL, and field validation functions
 */

import { describe, it, expect } from 'vitest'
import {
  isValidEmail,
  validatePassword,
  isValidUrl,
  isRequired,
  validateLength,
  validateRange
} from '@/utils/validators'

describe('Email Validation', () => {
  it('should validate correct email addresses', () => {
    expect(isValidEmail('user@example.com')).toBe(true)
    expect(isValidEmail('test.user+tag@example.co.uk')).toBe(true)
    expect(isValidEmail('user123@test-domain.com')).toBe(true)
  })

  it('should reject invalid email addresses', () => {
    expect(isValidEmail('invalid')).toBe(false)
    expect(isValidEmail('invalid@')).toBe(false)
    expect(isValidEmail('@example.com')).toBe(false)
    expect(isValidEmail('user@')).toBe(false)
    expect(isValidEmail('user example.com')).toBe(false)
    expect(isValidEmail('')).toBe(false)
  })

  it('should handle edge cases', () => {
    expect(isValidEmail('user@localhost')).toBe(true)
    expect(isValidEmail('user@127.0.0.1')).toBe(false)
  })
})

describe('Password Validation', () => {
  it('should validate strong passwords', () => {
    const result = validatePassword('SecurePass123')
    expect(result.isValid).toBe(true)
    expect(result.errors).toHaveLength(0)
  })

  it('should require minimum length of 8 characters', () => {
    const result = validatePassword('Short1')
    expect(result.isValid).toBe(false)
    expect(result.errors).toContain('Password must be at least 8 characters')
  })

  it('should require lowercase letters', () => {
    const result = validatePassword('UPPERCASE123')
    expect(result.isValid).toBe(false)
    expect(result.errors).toContain('Password must contain at least one lowercase letter')
  })

  it('should require uppercase letters', () => {
    const result = validatePassword('lowercase123')
    expect(result.isValid).toBe(false)
    expect(result.errors).toContain('Password must contain at least one uppercase letter')
  })

  it('should require numbers', () => {
    const result = validatePassword('NoNumbers')
    expect(result.isValid).toBe(false)
    expect(result.errors).toContain('Password must contain at least one number')
  })

  it('should return all errors for weak passwords', () => {
    const result = validatePassword('weak')
    expect(result.isValid).toBe(false)
    expect(result.errors.length).toBeGreaterThanOrEqual(3)
  })
})

describe('URL Validation', () => {
  it('should validate valid URLs', () => {
    expect(isValidUrl('https://example.com')).toBe(true)
    expect(isValidUrl('http://example.com')).toBe(true)
    expect(isValidUrl('https://example.com/path?query=value')).toBe(true)
    expect(isValidUrl('ftp://example.com')).toBe(true)
  })

  it('should reject invalid URLs', () => {
    expect(isValidUrl('not-a-url')).toBe(false)
    expect(isValidUrl('example.com')).toBe(false)
    expect(isValidUrl('')).toBe(false)
  })
})

describe('Required Field Validation', () => {
  it('should accept non-empty values', () => {
    expect(isRequired('text')).toBe(true)
    expect(isRequired('  text  ')).toBe(true)
    expect(isRequired(0)).toBe(true)
    expect(isRequired(false)).toBe(true)
    expect(isRequired([1, 2, 3])).toBe(true)
    expect(isRequired({ key: 'value' })).toBe(true)
  })

  it('should reject empty values', () => {
    expect(isRequired(null)).toBe(false)
    expect(isRequired(undefined)).toBe(false)
    expect(isRequired('')).toBe(false)
    expect(isRequired('   ')).toBe(false)
    expect(isRequired([])).toBe(false)
  })
})

describe('Length Validation', () => {
  it('should validate minimum length', () => {
    expect(validateLength('hello', 5).isValid).toBe(true)
    expect(validateLength('hi', 5).isValid).toBe(false)
    expect(validateLength('hi', 5).error).toBe('Must be at least 5 characters')
  })

  it('should validate maximum length', () => {
    expect(validateLength('hello', 0, 5).isValid).toBe(true)
    expect(validateLength('hello world', 0, 5).isValid).toBe(false)
    expect(validateLength('hello world', 0, 5).error).toBe('Must be no more than 5 characters')
  })

  it('should validate range', () => {
    expect(validateLength('hello', 3, 10).isValid).toBe(true)
    expect(validateLength('hi', 3, 10).isValid).toBe(false)
    expect(validateLength('this is very long text', 3, 10).isValid).toBe(false)
  })

  it('should handle no constraints', () => {
    expect(validateLength('').isValid).toBe(true)
    expect(validateLength('any length').isValid).toBe(true)
  })
})

describe('Range Validation for Numbers', () => {
  it('should validate minimum value', () => {
    expect(validateRange(5, 1, 10).isValid).toBe(true)
    expect(validateRange(0, 1, 10).isValid).toBe(false)
    expect(validateRange(0, 1, 10).error).toBe('Must be at least 1')
  })

  it('should validate maximum value', () => {
    expect(validateRange(5, 1, 10).isValid).toBe(true)
    expect(validateRange(11, 1, 10).isValid).toBe(false)
    expect(validateRange(11, 1, 10).error).toBe('Must be no more than 10')
  })

  it('should validate range', () => {
    expect(validateRange(5, 1, 10).isValid).toBe(true)
    expect(validateRange(0, 1, 10).isValid).toBe(false)
    expect(validateRange(11, 1, 10).isValid).toBe(false)
  })

  it('should handle no constraints', () => {
    expect(validateRange(-1000).isValid).toBe(true)
    expect(validateRange(1000).isValid).toBe(true)
  })
})
