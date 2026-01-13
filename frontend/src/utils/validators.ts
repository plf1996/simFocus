/**
 * Validation Utilities
 * Common validation functions for forms
 */

/**
 * Email validation
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

/**
 * Password strength validation
 * Returns object with validity status and error messages
 */
export function validatePassword(password: string): {
  isValid: boolean
  errors: string[]
} {
  const errors: string[] = []

  if (password.length < 8) {
    errors.push('Password must be at least 8 characters')
  }

  if (!/[a-z]/.test(password)) {
    errors.push('Password must contain at least one lowercase letter')
  }

  if (!/[A-Z]/.test(password)) {
    errors.push('Password must contain at least one uppercase letter')
  }

  if (!/\d/.test(password)) {
    errors.push('Password must contain at least one number')
  }

  return {
    isValid: errors.length === 0,
    errors
  }
}

/**
 * URL validation
 */
export function isValidUrl(url: string): boolean {
  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}

/**
 * Required field validation
 */
export function isRequired(value: unknown): boolean {
  if (value === null || value === undefined) return false
  if (typeof value === 'string') return value.trim().length > 0
  if (Array.isArray(value)) return value.length > 0
  return true
}

/**
 * Length validation
 */
export function validateLength(
  value: string,
  min?: number,
  max?: number
): { isValid: boolean; error?: string } {
  const length = value.length

  if (min !== undefined && length < min) {
    return {
      isValid: false,
      error: `Must be at least ${min} characters`
    }
  }

  if (max !== undefined && length > max) {
    return {
      isValid: false,
      error: `Must be no more than ${max} characters`
    }
  }

  return { isValid: true }
}

/**
 * Range validation for numbers
 */
export function validateRange(
  value: number,
  min?: number,
  max?: number
): { isValid: boolean; error?: string } {
  if (min !== undefined && value < min) {
    return {
      isValid: false,
      error: `Must be at least ${min}`
    }
  }

  if (max !== undefined && value > max) {
    return {
      isValid: false,
      error: `Must be no more than ${max}`
    }
  }

  return { isValid: true }
}
