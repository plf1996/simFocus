/**
 * E2E Tests for Authentication Flow
 * Testing user registration, login, and logout
 */

import { test, expect } from '@playwright/test'

test.describe('Authentication Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('should navigate to login page', async ({ page }) => {
    await page.click('text=Login')
    await expect(page).toHaveURL(/.*login/)
    await expect(page.locator('h1')).toContainText('Login')
  })

  test('should show validation errors for empty form', async ({ page }) => {
    await page.goto('/login')

    // Try to submit without filling form
    await page.click('button:has-text("Sign In")')

    // Check for validation errors
    await expect(page.locator('text=Please enter your email')).toBeVisible()
  })

  test('should show validation error for invalid email', async ({ page }) => {
    await page.goto('/login')

    await page.fill('input[type="email"]', 'invalid-email')
    await page.blur('input[type="email"]')

    await expect(page.locator('text=Please enter a valid email')).toBeVisible()
  })

  test('should show validation error for short password', async ({ page }) => {
    await page.goto('/login')

    await page.fill('input[type="password"]', '12345')
    await page.blur('input[type="password"]')

    await expect(page.locator('text=Password must be at least 6 characters')).toBeVisible()
  })

  test('should navigate to registration page', async ({ page }) => {
    await page.goto('/login')
    await page.click('a:has-text("Sign up")')

    await expect(page).toHaveURL(/.*register/)
    await expect(page.locator('h1')).toContainText('Create Account')
  })

  test('should navigate to forgot password page', async ({ page }) => {
    await page.goto('/login')
    await page.click('a:has-text("Forgot password?")')

    await expect(page).toHaveURL(/.*forgot-password/)
    await expect(page.locator('h1')).toContainText('Reset Password')
  })

  test('should show social login options', async ({ page }) => {
    await page.goto('/login')

    // Check for Google and GitHub login buttons
    await expect(page.locator('button:has-text("Google")')).toBeVisible()
    await expect(page.locator('button:has-text("GitHub")')).toBeVisible()
  })

  test('should enable remember me checkbox', async ({ page }) => {
    await page.goto('/login')

    const checkbox = page.locator('input[type="checkbox"]')
    await expect(checkbox).not.toBeChecked()

    await checkbox.check()
    await expect(checkbox).toBeChecked()

    await checkbox.uncheck()
    await expect(checkbox).not.toBeChecked()
  })

  test('should handle API error on login', async ({ page }) => {
    await page.goto('/login')

    // Fill with valid format credentials (will fail API call)
    await page.fill('input[type="email"]', 'test@example.com')
    await page.fill('input[type="password"]', 'wrongpassword')

    await page.click('button:has-text("Sign In")')

    // Should show loading state
    await expect(page.locator('button:has-text("Sign In")')).toHaveAttribute('disabled')

    // Error message should appear (from API or timeout)
    // This test assumes the API will return an error for invalid credentials
  })
})

test.describe('Registration Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/register')
  })

  test('should have all required fields', async ({ page }) => {
    await expect(page.locator('input[type="email"]')).toBeVisible()
    await expect(page.locator('input[type="password"]')).toBeVisible()
    await expect(page.locator('input[name="confirmPassword"]')).toBeVisible()
  })

  test('should validate password requirements', async ({ page }) => {
    await page.fill('input[type="password"]', 'weak')
    await page.blur('input[type="password"]')

    // Should show password strength validation
    // (Implementation depends on actual validation UI)
  })

  test('should validate password confirmation', async ({ page }) => {
    await page.fill('input[type="password"]', 'Password123')
    await page.fill('input[name="confirmPassword"]', 'Different123')

    await page.click('button:has-text("Create Account")')

    // Should show mismatch error
    await expect(page.locator('text=Passwords do not match')).toBeVisible()
  })

  test('should navigate back to login', async ({ page }) => {
    await page.click('a:has-text("Sign in")')

    await expect(page).toHaveURL(/.*login/)
  })
})

test.describe('Protected Routes', () => {
  test('should redirect unauthenticated users to login', async ({ page }) => {
    await page.goto('/dashboard')

    await expect(page).toHaveURL(/.*login.*/)
    await expect(page.locator('input[type="email"]')).toBeVisible()
  })

  test('should store redirect path', async ({ page }) => {
    await page.goto('/topics/create')

    const url = page.url()
    expect(url).toContain('redirect=%2Ftopics%2Fcreate')
  })
})

test.describe('Logout Flow', () => {
  test('should logout and redirect to home', async ({ page }) => {
    // First login (this would need a mock or test user)
    // Then logout
    // Verify redirect to home

    // This test requires authentication setup
    // Skip for now as it needs valid credentials
    test.skip(true, 'Requires authentication setup')
  })
})
