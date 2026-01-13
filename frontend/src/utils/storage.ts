/**
 * Storage Utilities
 * LocalStorage and SessionStorage wrappers with error handling
 */

const STORAGE_PREFIX = 'simfocus_'

/**
 * Safe localStorage operations
 */
export const storage = {
  /**
   * Get item from localStorage
   */
  get<T>(key: string, defaultValue?: T): T | null {
    try {
      const item = localStorage.getItem(STORAGE_PREFIX + key)
      return item ? JSON.parse(item) : (defaultValue ?? null)
    } catch (error) {
      console.error('Error reading from localStorage:', error)
      return defaultValue ?? null
    }
  },

  /**
   * Set item in localStorage
   */
  set<T>(key: string, value: T): boolean {
    try {
      localStorage.setItem(STORAGE_PREFIX + key, JSON.stringify(value))
      return true
    } catch (error) {
      console.error('Error writing to localStorage:', error)
      return false
    }
  },

  /**
   * Remove item from localStorage
   */
  remove(key: string): boolean {
    try {
      localStorage.removeItem(STORAGE_PREFIX + key)
      return true
    } catch (error) {
      console.error('Error removing from localStorage:', error)
      return false
    }
  },

  /**
   * Clear all app items from localStorage
   */
  clear(): boolean {
    try {
      const keysToRemove: string[] = []
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i)
        if (key?.startsWith(STORAGE_PREFIX)) {
          keysToRemove.push(key)
        }
      }
      keysToRemove.forEach((key) => localStorage.removeItem(key))
      return true
    } catch (error) {
      console.error('Error clearing localStorage:', error)
      return false
    }
  }
}

/**
 * Safe sessionStorage operations
 */
export const session = {
  /**
   * Get item from sessionStorage
   */
  get<T>(key: string, defaultValue?: T): T | null {
    try {
      const item = sessionStorage.getItem(STORAGE_PREFIX + key)
      return item ? JSON.parse(item) : (defaultValue ?? null)
    } catch (error) {
      console.error('Error reading from sessionStorage:', error)
      return defaultValue ?? null
    }
  },

  /**
   * Set item in sessionStorage
   */
  set<T>(key: string, value: T): boolean {
    try {
      sessionStorage.setItem(STORAGE_PREFIX + key, JSON.stringify(value))
      return true
    } catch (error) {
      console.error('Error writing to sessionStorage:', error)
      return false
    }
  },

  /**
   * Remove item from sessionStorage
   */
  remove(key: string): boolean {
    try {
      sessionStorage.removeItem(STORAGE_PREFIX + key)
      return true
    } catch (error) {
      console.error('Error removing from sessionStorage:', error)
      return false
    }
  },

  /**
   * Clear all app items from sessionStorage
   */
  clear(): boolean {
    try {
      const keysToRemove: string[] = []
      for (let i = 0; i < sessionStorage.length; i++) {
        const key = sessionStorage.key(i)
        if (key?.startsWith(STORAGE_PREFIX)) {
          keysToRemove.push(key)
        }
      }
      keysToRemove.forEach((key) => sessionStorage.removeItem(key))
      return true
    } catch (error) {
      console.error('Error clearing sessionStorage:', error)
      return false
    }
  }
}
