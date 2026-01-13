/**
 * Encryption Utilities
 * Provides AES-256 encryption for sensitive data like API keys
 */

import CryptoJS from 'crypto-js'

// Get encryption key from environment variables
// In production, this should be a securely stored key
const ENCRYPTION_KEY = import.meta.env.VITE_ENCRYPTION_KEY || 'simFocus-default-encryption-key-change-in-production'

/**
 * Encrypt sensitive data using AES-256
 * @param data - Plain text data to encrypt
 * @returns Encrypted string (Base64 encoded)
 */
export function encrypt(data: string): string {
  try {
    const encrypted = CryptoJS.AES.encrypt(data, ENCRYPTION_KEY)
    return encrypted.toString()
  } catch (error) {
    console.error('Encryption failed:', error)
    throw new Error('Failed to encrypt data')
  }
}

/**
 * Decrypt encrypted data
 * @param encryptedData - Encrypted string (Base64 encoded)
 * @returns Decrypted plain text
 */
export function decrypt(encryptedData: string): string {
  try {
    const decrypted = CryptoJS.AES.decrypt(encryptedData, ENCRYPTION_KEY)
    return decrypted.toString(CryptoJS.enc.Utf8)
  } catch (error) {
    console.error('Decryption failed:', error)
    throw new Error('Failed to decrypt data')
  }
}

/**
 * Encrypt API key for storage
 * @param apiKey - Plain API key
 * @returns Encrypted API key
 */
export function encryptApiKey(apiKey: string): string {
  if (!apiKey) {
    throw new Error('API key is required')
  }
  return encrypt(apiKey)
}

/**
 * Decrypt API key from storage
 * @param encryptedKey - Encrypted API key
 * @returns Decrypted API key
 */
export function decryptApiKey(encryptedKey: string): string {
  if (!encryptedKey) {
    throw new Error('Encrypted key is required')
  }
  return decrypt(encryptedKey)
}

/**
 * Mask API key for display purposes
 * @param apiKey - API key to mask
 * @param visibleChars - Number of characters to show at the beginning (default: 7)
 * @returns Masked API key (e.g., "sk-test••••••••")
 */
export function maskApiKey(apiKey: string, visibleChars: number = 7): string {
  if (!apiKey) return ''
  if (apiKey.length <= visibleChars) return apiKey

  const visible = apiKey.substring(0, visibleChars)
  const masked = '•'.repeat(Math.min(8, apiKey.length - visibleChars))
  return `${visible}${masked}`
}

/**
 * Validate if a string is properly encrypted
 * @param data - Data to validate
 * @returns True if data appears to be encrypted
 */
export function isEncrypted(data: string): boolean {
  try {
    // Attempt to decrypt, if successful it's encrypted
    decrypt(data)
    return true
  } catch {
    return false
  }
}

/**
 * Hash data for verification (one-way)
 * @param data - Data to hash
 * @returns Hashed string
 */
export function hashData(data: string): string {
  return CryptoJS.SHA256(data).toString()
}
