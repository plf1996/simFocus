/**
 * Form Validation Composable
 * Provides reusable form validation logic with Element Plus
 */

import { ref, computed, type Ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'

export interface ValidationRule {
  required?: boolean
  message?: string
  trigger?: 'blur' | 'change'
  min?: number
  max?: number
  pattern?: RegExp
  validator?: (rule: any, value: any, callback: any) => void
}

export interface ValidationSchema {
  [field: string]: ValidationRule[]
}

export interface FormValidationResult {
  isValid: boolean
  errors: Record<string, string[]>
  firstError: string | null
}

export interface UseFormValidationOptions {
  // Enable/disable validation on input change
  validateOnInput?: boolean
  // Show inline error messages
  showInlineErrors?: boolean
  // Scroll to first error on validation failure
  scrollToError?: boolean
}

export function useFormValidation(
  formRef: Ref<FormInstance | undefined>,
  schema: ValidationSchema,
  options: UseFormValidationOptions = {}
) {
  const {
    validateOnInput = false,
    showInlineErrors = true,
    scrollToError = true
  } = options

  const errors = ref<Record<string, string[]>>({})
  const isValidating = ref(false)
  const isDirty = ref(false)

  // Convert schema to Element Plus FormRules format
  const formRules = computed<FormRules>(() => {
    const rules: FormRules = {}

    for (const [field, fieldRules] of Object.entries(schema)) {
      rules[field] = fieldRules.map((rule) => ({
        required: rule.required ?? false,
        message: rule.message ?? 'This field is required',
        trigger: rule.trigger ?? (validateOnInput ? 'change' : 'blur'),
        min: rule.min,
        max: rule.max,
        pattern: rule.pattern,
        validator: rule.validator
      }))
    }

    return rules
  })

  // Validate entire form
  async function validate(): Promise<FormValidationResult> {
    if (!formRef.value) {
      console.warn('Form ref is not available')
      return {
        isValid: false,
        errors: {},
        firstError: 'Form not initialized'
      }
    }

    isValidating.value = true
    isDirty.value = true

    try {
      await formRef.value.validate()

      // Clear errors on successful validation
      errors.value = {}

      return {
        isValid: true,
        errors: {},
        firstError: null
      }
    } catch (validationErrors: any) {
      // Process errors into a more usable format
      const processedErrors: Record<string, string[]> = {}
      let firstError: string | null = null

      if (validationErrors && typeof validationErrors === 'object') {
        for (const [field, fieldErrors] of Object.entries(validationErrors)) {
          const errorMessages = Array.isArray(fieldErrors)
            ? fieldErrors.map((e: any) => e.message || String(e))
            : [String(fieldErrors)]

          processedErrors[field] = errorMessages

          if (!firstError && errorMessages.length > 0) {
            firstError = errorMessages[0]
          }
        }
      }

      errors.value = processedErrors

      // Scroll to first error if enabled
      if (scrollToError && firstError) {
        scrollToFirstError()
      }

      return {
        isValid: false,
        errors: processedErrors,
        firstError
      }
    } finally {
      isValidating.value = false
    }
  }

  // Validate a single field
  async function validateField(field: string): Promise<boolean> {
    if (!formRef.value) return false

    try {
      await formRef.value.validateField(field)
      // Clear error for this field
      if (errors.value[field]) {
        delete errors.value[field]
      }
      return true
    } catch (error) {
      return false
    }
  }

  // Clear all validation errors
  function clearErrors(): void {
    errors.value = {}
    isDirty.value = false
    formRef.value?.clearValidate()
  }

  // Clear errors for a specific field
  function clearFieldError(field: string): void {
    if (errors.value[field]) {
      delete errors.value[field]
    }
    formRef.value?.clearValidate(field)
  }

  // Reset form to initial state
  function resetFields(): void {
    clearErrors()
    formRef.value?.resetFields()
  }

  // Scroll to first error field
  function scrollToFirstError(): void {
    const firstErrorField = Object.keys(errors.value)[0]
    if (!firstErrorField) return

    const element = document.querySelector(
      `[data-field="${firstErrorField}"]`
    ) as HTMLElement

    if (element) {
      element.scrollIntoView({
        behavior: 'smooth',
        block: 'center'
      })
      element.focus?.()
    }
  }

  // Get error message for a field
  function getFieldError(field: string): string | null {
    const fieldErrors = errors.value[field]
    return fieldErrors && fieldErrors.length > 0 ? fieldErrors[0] : null
  }

  // Check if field has error
  function hasFieldError(field: string): boolean {
    return !!errors.value[field]?.length
  }

  return {
    // State
    errors,
    isValidating,
    isDirty,
    formRules,
    // Computed
    hasErrors: computed(() => Object.keys(errors.value).length > 0),
    firstError: computed(() => getFieldError(Object.keys(errors.value)[0] ?? '')),
    // Methods
    validate,
    validateField,
    clearErrors,
    clearFieldError,
    resetFields,
    scrollToFirstError,
    getFieldError,
    hasFieldError
  }
}

// Preset validation rules for common use cases
export const validationRules = {
  // Email validation
  email: {
    pattern: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
    message: 'Please enter a valid email address'
  },

  // Password validation (min 8 chars, 1 uppercase, 1 lowercase, 1 number)
  password: {
    pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/,
    message: 'Password must be at least 8 characters with uppercase, lowercase, and number'
  },

  // URL validation
  url: {
    pattern: /^https?:\/\/[^\s/$.?#].[^\s]*$/,
    message: 'Please enter a valid URL (starting with http:// or https://)'
  },

  // Phone number validation (basic)
  phone: {
    pattern: /^[\d\s\-+()]+$/,
    message: 'Please enter a valid phone number'
  },

  // Number validation
  number: {
    pattern: /^\d+$/,
    message: 'Please enter a valid number'
  },

  // Positive number validation
  positiveNumber: {
    pattern: /^[1-9]\d*$/,
    message: 'Please enter a positive number'
  },

  // Minimum length factory
  minLength: (min: number) => ({
    min,
    message: `Must be at least ${min} characters`
  }),

  // Maximum length factory
  maxLength: (max: number) => ({
    max,
    message: `Must be no more than ${max} characters`
  }),

  // Range length factory
  rangeLength: (min: number, max: number) => ({
    min,
    max,
    message: `Must be between ${min} and ${max} characters`
  }),

  // Required field
  required: (message?: string) => ({
    required: true,
    message: message ?? 'This field is required'
  })
}

// Custom validators
export const customValidators = {
  // Confirm password validator
  confirmPassword: (passwordField: string) => ({
    validator: (rule: any, value: any, callback: any, source: any) => {
      if (value === '') {
        callback(new Error('Please confirm your password'))
      } else if (value !== source[passwordField]) {
        callback(new Error('Passwords do not match'))
      } else {
        callback()
      }
    }
  }),

  // Async username availability check
  checkUsernameAvailability: async (username: string) => {
    // TODO: Implement actual API check
    // const isAvailable = await api.get(`/auth/check-username/${username}`)
    // return isAvailable
    return true
  },

  // API key format validator
  apiKeyFormat: (provider: 'openai' | 'anthropic' | 'custom') => ({
    validator: (rule: any, value: any, callback: any) => {
      if (!value) {
        callback()
        return
      }

      const patterns = {
        openai: /^sk-[a-zA-Z0-9]{48}$/,
        anthropic: /^sk-ant-[a-zA-Z0-9_-]{95}$/,
        custom: /^.{20,}$/ // At least 20 chars for custom keys
      }

      if (patterns[provider] && !patterns[provider].test(value)) {
        callback(new Error(`Invalid ${provider} API key format`))
      } else {
        callback()
      }
    }
  })
}
