/**
 * Unit Tests for Format Utilities
 * Testing date, number, and text formatting functions
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import {
  formatRelativeTime,
  formatShortDate,
  formatLongDate,
  formatTime,
  formatDuration,
  formatNumber,
  formatCurrency,
  formatPercentage,
  truncateText
} from '@/utils/format'

describe('Date Formatting', () => {
  beforeEach(() => {
    // Mock current date for consistent testing
    vi.setSystemTime(new Date('2026-01-13T10:00:00Z'))
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  describe('formatRelativeTime', () => {
    it('should format recent dates as relative time', () => {
      expect(formatRelativeTime('2026-01-13T09:30:00Z')).toBe('30 minutes ago')
      expect(formatRelativeTime('2026-01-13T08:00:00Z')).toBe('2 hours ago')
      expect(formatRelativeTime('2026-01-12T10:00:00Z')).toBe('a day ago')
    })

    it('should handle older dates', () => {
      expect(formatRelativeTime('2026-01-06T10:00:00Z')).toBe('7 days ago')
      expect(formatRelativeTime('2025-12-13T10:00:00Z')).toBe('a month ago')
    })

    it('should handle future dates', () => {
      expect(formatRelativeTime('2026-01-13T11:00:00Z')).toBe('in an hour')
    })
  })

  describe('formatShortDate', () => {
    it('should format date to short format', () => {
      expect(formatShortDate('2026-01-13')).toBe('Jan 13, 2026')
      expect(formatShortDate('2026-12-25')).toBe('Dec 25, 2026')
    })
  })

  describe('formatLongDate', () => {
    it('should format date to long format', () => {
      expect(formatLongDate('2026-01-13T14:30:00Z')).toMatch(/January 13, 2026/)
      expect(formatLongDate('2026-01-13T09:00:00Z')).toMatch(/9:00 AM/)
    })
  })

  describe('formatTime', () => {
    it('should format time', () => {
      expect(formatTime('2026-01-13T14:30:00Z')).toBe('2:30 PM')
      expect(formatTime('2026-01-13T09:00:00Z')).toBe('9:00 AM')
      expect(formatTime('2026-01-13T00:00:00Z')).toBe('12:00 AM')
    })
  })
})

describe('formatDuration', () => {
  it('should format seconds to readable format', () => {
    expect(formatDuration(0)).toBe('0s')
    expect(formatDuration(30)).toBe('30s')
    expect(formatDuration(90)).toBe('1m 30s')
    expect(formatDuration(3661)).toBe('1h 1m 1s')
    expect(formatDuration(7325)).toBe('2h 2m 5s')
  })

  it('should handle large durations', () => {
    expect(formatDuration(3600)).toBe('1h 0m 0s')
    expect(formatDuration(7200)).toBe('2h 0m 0s')
  })
})

describe('Number Formatting', () => {
  describe('formatNumber', () => {
    it('should format numbers with commas', () => {
      expect(formatNumber(0)).toBe('0')
      expect(formatNumber(1000)).toBe('1,000')
      expect(formatNumber(1000000)).toBe('1,000,000')
      expect(formatNumber(1234567.89)).toBe('1,234,567.89')
    })

    it('should handle negative numbers', () => {
      expect(formatNumber(-1000)).toBe('-1,000')
    })
  })

  describe('formatCurrency', () => {
    it('should format currency in USD', () => {
      expect(formatCurrency(0)).toBe('$0.00')
      expect(formatCurrency(100)).toBe('$100.00')
      expect(formatCurrency(1234.56)).toBe('$1,234.56')
    })

    it('should format currency in different currencies', () => {
      expect(formatCurrency(100, 'EUR')).toBe('€100.00')
      expect(formatCurrency(100, 'GBP')).toBe('£100.00')
      expect(formatCurrency(100, 'JPY')).toBe('¥100')
    })

    it('should handle negative amounts', () => {
      expect(formatCurrency(-50)).toBe('-$50.00')
    })
  })

  describe('formatPercentage', () => {
    it('should format percentages', () => {
      expect(formatPercentage(0)).toBe('0.0%')
      expect(formatPercentage(50)).toBe('50.0%')
      expect(formatPercentage(99.99)).toBe('100.0%')
    })

    it('should handle custom decimal places', () => {
      expect(formatPercentage(50.123, 0)).toBe('50%')
      expect(formatPercentage(50.123, 2)).toBe('50.12%')
      expect(formatPercentage(50.123, 3)).toBe('50.123%')
    })
  })
})

describe('Text Formatting', () => {
  describe('truncateText', () => {
    it('should not truncate short text', () => {
      expect(truncateText('short', 10)).toBe('short')
      expect(truncateText('exact!', 6)).toBe('exact!')
    })

    it('should truncate long text', () => {
      expect(truncateText('this is very long text', 10)).toBe('this is ve...')
      expect(truncateText('hello world', 5)).toBe('hello...')
    })

    it('should handle empty text', () => {
      expect(truncateText('', 10)).toBe('')
    })

    it('should handle text at exact length', () => {
      expect(truncateText('exact', 5)).toBe('exact')
    })
  })
})
