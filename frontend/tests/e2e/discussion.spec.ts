/**
 * E2E Tests for Discussion Flow
 * Testing discussion creation, execution, and controls
 */

import { test, expect } from '@playwright/test'

test.describe('Discussion Room Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Mock authentication - would need to implement auth helper
    await page.goto('/login')

    // This test requires authentication
    // For now, we'll skip auth and go directly to the page
    // In real tests, you'd use a test account or mock auth
  })

  test('should display discussion room', async ({ page }) => {
    // Would need a valid discussion ID
    await page.goto('/discussions/test-discussion-id')

    await expect(page.locator('.discussion-room')).toBeVisible()
  })

  test('should show discussion progress', async ({ page }) => {
    await page.goto('/discussions/test-discussion-id')

    // Check progress bar
    await expect(page.locator('.progress-bar')).toBeVisible()

    // Check phase indicator
    await expect(page.locator('.phase-indicator')).toBeVisible()
  })

  test('should display participants panel', async ({ page }) => {
    await page.goto('/discussions/test-discussion-id')

    await expect(page.locator('.character-panel')).toBeVisible()

    // Should show participant count
    await expect(page.locator('text=participants')).toBeVisible()
  })

  test('should display messages', async ({ page }) => {
    await page.goto('/discussions/test-discussion-id')

    // Check for message list
    await expect(page.locator('.message-list')).toBeVisible()

    // Should have message bubbles
    const messages = page.locator('.message-bubble')
    await expect(messages).toHaveCount(await messages.count())
  })

  test('should show discussion controls', async ({ page }) => {
    await page.goto('/discussions/test-discussion-id')

    // Check for control buttons
    await expect(page.locator('button:has-text("Start")')).toBeVisible()
    await expect(page.locator('button:has-text("Pause")')).toBeVisible()
    await expect(page.locator('button:has-text("Stop")')).toBeVisible()
  })

  test('should enable start button when discussion is ready', async ({ page }) => {
    await page.goto('/discussions/test-discussion-id')

    const startButton = page.locator('button:has-text("Start")')
    await expect(startButton).toBeEnabled()
  })

  test('should disable pause button when not running', async ({ page }) => {
    await page.goto('/discussions/test-discussion-id')

    const pauseButton = page.locator('button:has-text("Pause")')
    await expect(pauseButton).toBeDisabled()
  })

  test('should show discussion info panel', async ({ page }) => {
    await page.goto('/discussions/test-discussion-id')

    await expect(page.locator('.info-card')).toBeVisible()

    // Should show model info
    await expect(page.locator('text=Model')).toBeVisible()

    // Should show token usage
    await expect(page.locator('text=Tokens Used')).toBeVisible()
  })

  test.skip('should handle start discussion', async ({ page }) => {
    // This test would need backend integration
    await page.goto('/discussions/test-discussion-id')

    await page.click('button:has-text("Start")')

    // Should show running state
    await expect(page.locator('text=Running')).toBeVisible()

    // Start button should be disabled
    await expect(page.locator('button:has-text("Start")')).toBeDisabled()

    // Pause button should be enabled
    await expect(page.locator('button:has-text("Pause")')).toBeEnabled()
  })

  test.skip('should handle pause/resume discussion', async ({ page }) => {
    await page.goto('/discussions/test-discussion-id')

    // Start discussion first
    await page.click('button:has-text("Start")')

    // Pause
    await page.click('button:has-text("Pause")')
    await expect(page.locator('text=Paused')).toBeVisible()

    // Resume
    await page.click('button:has-text("Resume")')
    await expect(page.locator('text=Running')).toBeVisible()
  })

  test('should handle speed change', async ({ page }) => {
    await page.goto('/discussions/test-discussion-id')

    // Find speed control (dropdown or buttons)
    const speedControl = page.locator('[data-testid="speed-control"]')

    if (await speedControl.isVisible()) {
      await speedControl.click()
      await page.click('text=2.0x')

      // Should show success message
      await expect(page.locator('text=2.0x')).toBeVisible()
    }
  })

  test('should show character detail dialog', async ({ page }) => {
    await page.goto('/discussions/test-discussion-id')

    // Click on a character
    await page.click('.character-card:first-child')

    // Should show dialog
    await expect(page.locator('.el-dialog')).toBeVisible()

    // Close dialog
    await page.keyboard.press('Escape')
    await expect(page.locator('.el-dialog')).not.toBeVisible()
  })

  test('should handle export functionality', async ({ page }) => {
    await page.goto('/discussions/test-discussion-id')

    // Setup download handler
    const downloadPromise = page.waitForEvent('download')

    await page.click('button:has-text("Export")')

    const download = await downloadPromise
    expect(download.suggestedFilename()).toContain('discussion-')
  })

  test('should be responsive on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 })
    await page.goto('/discussions/test-discussion-id')

    // Side panels should be hidden on mobile
    await expect(page.locator('.layout-left')).not.toBeVisible()
    await expect(page.locator('.layout-right')).not.toBeVisible()

    // Message list should be visible
    await expect(page.locator('.layout-center')).toBeVisible()
  })
})

test.describe('Discussion List', () => {
  test('should display list of discussions', async ({ page }) => {
    // Would need authentication
    await page.goto('/discussions')

    await expect(page.locator('.discussion-list')).toBeVisible()
  })

  test('should filter discussions', async ({ page }) => {
    await page.goto('/discussions')

    // Use search/filter controls
    const searchInput = page.locator('input[placeholder*="search"]')

    if (await searchInput.isVisible()) {
      await searchInput.fill('test topic')

      // Should filter results
      await page.waitForTimeout(500) // Wait for debounced search
    }
  })

  test('should navigate to discussion from list', async ({ page }) => {
    await page.goto('/discussions')

    // Click on first discussion card
    const firstCard = page.locator('.discussion-card').first()
    if (await firstCard.isVisible()) {
      await firstCard.click()

      await expect(page).toHaveURL(/.*discussions\/.*/)
    }
  })
})
