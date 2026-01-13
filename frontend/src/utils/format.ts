/**
 * Format Utilities
 * Date, number, and other formatting functions
 */

import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import duration from 'dayjs/plugin/duration'

dayjs.extend(relativeTime)
dayjs.extend(duration)

/**
 * Format date to relative time (e.g., "2 hours ago")
 */
export function formatRelativeTime(date: string | Date): string {
  return dayjs(date).fromNow()
}

/**
 * Format date to short format (e.g., "Jan 12, 2026")
 */
export function formatShortDate(date: string | Date): string {
  return dayjs(date).format('MMM D, YYYY')
}

/**
 * Format date to long format (e.g., "January 12, 2026 at 2:30 PM")
 */
export function formatLongDate(date: string | Date): string {
  return dayjs(date).format('MMMM D, YYYY [at] h:mm A')
}

/**
 * Format time (e.g., "2:30 PM")
 */
export function formatTime(date: string | Date): string {
  return dayjs(date).format('h:mm A')
}

/**
 * Format duration in seconds to readable format
 */
export function formatDuration(seconds: number): string {
  const dur = dayjs.duration(seconds, 'seconds')
  const hours = dur.hours()
  const minutes = dur.minutes()
  const secs = dur.seconds()

  if (hours > 0) {
    return `${hours}h ${minutes}m ${secs}s`
  } else if (minutes > 0) {
    return `${minutes}m ${secs}s`
  } else {
    return `${secs}s`
  }
}

/**
 * Format number with commas
 */
export function formatNumber(num: number): string {
  return num.toLocaleString('en-US')
}

/**
 * Format currency
 */
export function formatCurrency(amount: number, currency: string = 'USD'): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency
  }).format(amount)
}

/**
 * Format percentage
 */
export function formatPercentage(value: number, decimals: number = 1): string {
  return `${value.toFixed(decimals)}%`
}

/**
 * Truncate text with ellipsis
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength) + '...'
}
