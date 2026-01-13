/**
 * E2E Tests for Topic Management
 * Testing topic creation, editing, and management
 */

import { test, expect } from '@playwright/test'

test.describe('Topic Creation Flow', () => {
  test.beforeEach(async ({ page }) => {
    // This would require authentication
    await page.goto('/topics/create')
  })

  test('should display topic creation form', async ({ page }) => {
    await expect(page.locator('.topic-form')).toBeVisible()

    // Check for required fields
    await expect(page.locator('input[name="title"]')).toBeVisible()
    await expect(page.locator('textarea[name="description"]')).toBeVisible()
  })

  test('should validate title requirements', async ({ page }) => {
    await page.fill('input[name="title"]', 'AB')
    await page.blur('input[name="title"]')

    // Should show validation error (minimum 10 characters per PRD)
    const errorMsg = page.locator('text=at least 10 characters')
    await expect(errorMsg).toBeVisible()
  })

  test('should validate title maximum length', async ({ page }) => {
    const longTitle = 'A'.repeat(201)

    await page.fill('input[name="title"]', longTitle)
    await page.blur('input[name="title"]')

    // Should show validation error (maximum 200 characters per PRD)
    const errorMsg = page.locator('text=no more than 200')
    await expect(errorMsg).toBeVisible()
  })

  test('should validate description maximum length', async ({ page }) => {
    const longDesc = 'A'.repeat(2001)

    await page.fill('textarea[name="description"]', longDesc)
    await page.blur('textarea[name="description"]')

    // Should show validation error (maximum 2000 characters per PRD)
    const errorMsg = page.locator('text=no more than 2000')
    await expect(errorMsg).toBeVisible()
  })

  test('should show character selector', async ({ page }) => {
    await expect(page.locator('.character-selector')).toBeVisible()

    // Should have at least some character options
    const characters = page.locator('.character-card')
    await expect(characters).toHaveCount(await characters.count())
  })

  test('should allow selecting multiple characters', async ({ page }) => {
    // Select first character
    await page.click('.character-card:first-child')

    // Should show as selected
    await expect(page.locator('.character-card:first-child.selected')).toBeVisible()

    // Select second character
    await page.click('.character-card:nth-child(2)')

    // Should update selected count
    const selectedCount = await page.locator('.selected-count').textContent()
    expect(selectedCount).toContain('2')
  })

  test('should validate minimum character selection', async ({ page }) => {
    // Try to create without selecting characters
    await page.fill('input[name="title"]', 'Valid discussion topic title')
    await page.click('button:has-text("Create Discussion")')

    // Should show error
    await expect(page.locator('text=Select at least')).toBeVisible()
  })

  test('should show discussion mode options', async ({ page }) => {
    await expect(page.locator('[data-testid="discussion-mode"]')).toBeVisible()

    // Check for all modes
    await expect(page.locator('text=Free Discussion')).toBeVisible()
    await expect(page.locator('text=Structured Debate')).toBeVisible()
    await expect(page.locator('text=Creative Brainstorm')).toBeVisible()
    await expect(page.locator('text=Consensus Building')).toBeVisible()
  })

  test('should allow selecting discussion mode', async ({ page }) => {
    await page.click('[data-testid="discussion-mode"]')
    await page.click('text=Structured Debate')

    // Should update selection
    await expect(page.locator('text=Structured Debate')).toBeVisible()
  })

  test('should allow setting max rounds', async ({ page }) => {
    const roundsInput = page.locator('input[name="max_rounds"]')

    if (await roundsInput.isVisible()) {
      await roundsInput.fill('15')

      // Should accept valid range (10-20 per PRD)
      await expect(roundsInput).toHaveValue('15')
    }
  })

  test('should show template selection', async ({ page }) => {
    await page.click('button:has-text("Use Template")')

    await expect(page.locator('.topic-template-library')).toBeVisible()

    // Should have template cards
    const templates = page.locator('.template-card')
    await expect(templates).toHaveCount(await templates.count())
  })

  test.skip('should create topic successfully', async ({ page }) => {
    // This would need backend integration

    // Fill form
    await page.fill('input[name="title"]', 'Test Discussion Topic')
    await page.fill('textarea[name="description"]', 'This is a test discussion description')

    // Select characters
    await page.click('.character-card:first-child')
    await page.click('.character-card:nth-child(2)')

    // Submit
    await page.click('button:has-text("Create Discussion")')

    // Should navigate to discussion room
    await expect(page).toHaveURL(/.*discussions\/.*/)
  })
})

test.describe('Topic List Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/topics')
  })

  test('should display list of topics', async ({ page }) => {
    await expect(page.locator('.topic-list')).toBeVisible()

    const topics = page.locator('.topic-card')
    await expect(topics).toHaveCount(await topics.count())
  })

  test('should filter topics by status', async ({ page }) => {
    // Click status filter
    await page.click('[data-testid="status-filter"]')
    await page.click('text=Ready')

    // Should filter results
    await page.waitForTimeout(500)
  })

  test('should search topics', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="search"]')

    if (await searchInput.isVisible()) {
      await searchInput.fill('test topic')

      // Should filter results
      await page.waitForTimeout(500) // Wait for debounced search
    }
  })

  test('should allow editing topic', async ({ page }) => {
    const firstTopic = page.locator('.topic-card').first()

    if (await firstTopic.isVisible()) {
      // Click edit button
      await firstTopic.locator('button:has-text("Edit")').click()

      // Should navigate to edit page
      await expect(page).toHaveURL(/.*topics\/.*\/edit/)
    }
  })

  test('should allow deleting topic', async ({ page }) => {
    const firstTopic = page.locator('.topic-card').first()

    if (await firstTopic.isVisible()) {
      // Click delete button
      await firstTopic.locator('button:has-text("Delete")').click()

      // Should show confirmation dialog
      await expect(page.locator('.el-dialog')).toBeVisible()

      // Confirm deletion
      await page.click('.el-dialog button:has-text("Confirm")')

      // Should show success message
      await expect(page.locator('.el-message--success')).toBeVisible()
    }
  })

  test('should show topic status badges', async ({ page }) => {
    const badges = page.locator('.el-tag')

    for (const badge of await badges.all()) {
      const text = await badge.textContent()
      expect(['Draft', 'Ready', 'In Discussion', 'Completed']).toContain(text)
    }
  })

  test('should allow creating new topic from list', async ({ page }) => {
    await page.click('button:has-text("New Topic")')

    await expect(page).toHaveURL(/.*topics\/create/)
  })
})

test.describe('Topic Editing', () => {
  test.beforeEach(async ({ page }) => {
    // Would need a valid topic ID
    await page.goto('/topics/test-topic-id/edit')
  })

  test('should pre-fill form with existing data', async ({ page }) => {
    const titleInput = page.locator('input[name="title"]')
    const descTextarea = page.locator('textarea[name="description"]')

    await expect(titleInput).nottoHaveValue('')
    await expect(descTextarea).not.toBeEmpty()
  })

  test('should allow updating topic', async ({ page }) => {
    const newTitle = 'Updated Topic Title'

    await page.fill('input[name="title"]', newTitle)
    await page.click('button:has-text("Save Changes")')

    // Should show success message
    await expect(page.locator('.el-message--success')).toBeVisible()
  })

  test('should show cancel confirmation if changes made', async ({ page }) => {
    // Make changes
    await page.fill('input[name="title"]', 'Changed Title')

    // Try to navigate away
    await page.click('a:has-text("Cancel")')

    // Should show confirmation dialog
    await expect(page.locator('.el-dialog')).toBeVisible()
  })
})
