# simFocus Frontend Testing Quick Start Guide

## Overview

This guide helps you get started with testing the simFocus frontend application. We use **Vitest** for unit/integration tests and **Playwright** for E2E tests.

---

## Prerequisites

```bash
# Ensure Node.js version is correct
node --version  # Should be >= 18.0.0

# Navigate to frontend directory
cd frontend
```

---

## Installation

### 1. Install Dependencies

```bash
npm install
```

### 2. Install Playwright Browsers (for E2E tests)

```bash
npx playwright install
```

### 3. Verify Installation

```bash
# Run Vitest
npm run test -- --run

# Run Playwright
npm run test:e2e
```

---

## Running Tests

### Unit & Integration Tests

```bash
# Run all tests in watch mode
npm run test

# Run all tests once
npm run test:unit

# Run tests with UI
npm run test:ui

# Run tests with coverage
npm run test:coverage
```

### E2E Tests

```bash
# Run all E2E tests
npm run test:e2e

# Run E2E tests with UI
npm run test:e2e:ui

# Debug E2E tests
npm run test:e2e:debug

# View HTML report
npm run test:e2e:report
```

---

## Test Structure

```
frontend/tests/
├── unit/                    # Unit and integration tests
│   ├── components/          # Component tests
│   ├── stores/              # Pinia store tests
│   ├── utils/               # Utility function tests
│   └── services/            # API service tests
├── e2e/                     # E2E tests
│   ├── auth.spec.ts         # Authentication tests
│   ├── topic.spec.ts        # Topic management tests
│   └── discussion.spec.ts   # Discussion tests
├── MANUAL_TEST_CASES.md     # Manual test cases
├── TEST_STRATEGY.md         # Testing strategy
├── TEST_REPORT_TEMPLATE.md  # Test report template
├── BUG_REPORT_TEMPLATE.md   # Bug report template
└── setup.ts                 # Test configuration
```

---

## Writing Unit Tests

### Example: Testing a Utility Function

```typescript
// tests/unit/utils/validators.test.ts
import { describe, it, expect } from 'vitest'
import { isValidEmail } from '@/utils/validators'

describe('Email Validation', () => {
  it('should validate correct emails', () => {
    expect(isValidEmail('user@example.com')).toBe(true)
  })

  it('should reject invalid emails', () => {
    expect(isValidEmail('invalid')).toBe(false)
  })
})
```

### Example: Testing a Component

```typescript
// tests/unit/components/AppButton.test.ts
import { mount } from '@vue/test-utils'
import AppButton from '@/components/common/AppButton.vue'

describe('AppButton', () => {
  it('renders with default props', () => {
    const wrapper = mount(AppButton, {
      slots: { default: 'Click me' }
    })
    expect(wrapper.text()).toBe('Click me')
  })
})
```

### Example: Testing a Pinia Store

```typescript
// tests/unit/stores/auth.test.ts
import { createPinia, setActivePinia } from 'pinia'
import { useAuthStore } from '@/stores/auth'

describe('Auth Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('should not be authenticated initially', () => {
    const store = useAuthStore()
    expect(store.isAuthenticated).toBe(false)
  })
})
```

---

## Writing E2E Tests

### Example: Authentication Flow

```typescript
// tests/e2e/auth.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Authentication', () => {
  test('should login successfully', async ({ page }) => {
    await page.goto('/login')
    await page.fill('input[type="email"]', 'test@example.com')
    await page.fill('input[type="password"]', 'password123')
    await page.click('button:has-text("Sign In")')

    await expect(page).toHaveURL('/dashboard')
  })
})
```

---

## Best Practices

### Unit Tests

1. **Test behavior, not implementation**
   ```typescript
   // ✅ Good
   it('should format date correctly', () => {
     expect(formatDate('2026-01-13')).toBe('Jan 13, 2026')
   })

   // ❌ Bad
   it('should call Date.prototype.toLocaleString', () => {
     // Tests implementation, not behavior
   })
   ```

2. **Use descriptive test names**
   ```typescript
   // ✅ Good
   it('should return false for invalid email format', () => {})

   // ❌ Bad
   it('test email', () => {})
   ```

3. **Follow AAA pattern (Arrange, Act, Assert)**
   ```typescript
   it('should calculate discount correctly', () => {
     // Arrange
     const price = 100
     const discount = 0.2

     // Act
     const result = calculateDiscount(price, discount)

     // Assert
     expect(result).toBe(80)
   })
   ```

4. **Mock external dependencies**
   ```typescript
   vi.mock('@/services/api', () => ({
     api: {
       post: vi.fn(() => Promise.resolve({ data: {} }))
     }
   }))
   ```

### E2E Tests

1. **Use data-testid selectors**
   ```vue
   <template>
     <button data-testid="submit-button">Submit</button>
   </template>
   ```
   ```typescript
   await page.click('[data-testid="submit-button"]')
   ```

2. **Wait for elements properly**
   ```typescript
   // ✅ Good
   await expect(page.locator('.success-message')).toBeVisible()

   // ❌ Bad
   await page.waitForTimeout(1000)
   ```

3. **Use page objects for repeated actions**
   ```typescript
   class LoginPage {
     constructor(page) {
       this.page = page
       this.emailInput = page.locator('input[type="email"]')
       this.passwordInput = page.locator('input[type="password"]')
       this.submitButton = page.locator('button:has-text("Sign In")')
     }

     async login(email, password) {
       await this.emailInput.fill(email)
       await this.passwordInput.fill(password)
       await this.submitButton.click()
     }
   }
   ```

---

## Coverage Goals

| Metric | Target | Command |
|--------|--------|---------|
| Statements | 70% | `npm run test:coverage` |
| Branches | 65% | `npm run test:coverage` |
| Functions | 70% | `npm run test:coverage` |
| Lines | 70% | `npm run test:coverage` |

View coverage report at: `coverage/index.html`

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      - run: npm ci
      - run: npm run test:unit
      - run: npm run test:e2e
```

---

## Debugging Tests

### Vitest

```bash
# Run in watch mode with UI
npm run test:ui

# Run specific test file
npm run test -- tests/unit/utils/validators.test.ts

# Run tests matching pattern
npm run test -- --grep "email"
```

### Playwright

```bash
# Run with debug mode
npm run test:e2e:debug

# Run specific test file
npx playwright test auth.spec.ts

# Run with headed browser
npx playwright test --headed

# Run specific test
npx playwright test --grep "should login"
```

---

## Common Issues

### Issue: Tests fail in CI but pass locally

**Solution**: Check for timing issues, use explicit waits

```typescript
// Instead of
await page.waitForTimeout(1000)

// Use
await expect(page.locator('.element')).toBeVisible()
```

### Issue: Component tests fail with "Cannot find module"

**Solution**: Check Vite alias configuration in vitest.config.ts

```typescript
resolve: {
  alias: {
    '@': fileURLToPath(new URL('./src', import.meta.url))
  }
}
```

### Issue: E2E tests are flaky

**Solution**: Use proper selectors and waits

```typescript
// Use data-testid
await page.click('[data-testid="submit-button"]')

// Wait for navigation
await page.waitForURL('/dashboard')

// Wait for element
await expect(page.locator('.success')).toBeVisible()
```

---

## Resources

- **Vitest Docs**: https://vitest.dev/
- **Vue Test Utils**: https://test-utils.vuejs.org/
- **Playwright Docs**: https://playwright.dev/
- **Testing Best Practices**: https://github.com/goldbergyoni/javascript-testing-best-practices

---

## Getting Help

- Check `TEST_STRATEGY.md` for detailed testing approach
- Review existing tests in `tests/` directory
- Check `MANUAL_TEST_CASES.md` for manual testing scenarios
- Contact QA team for assistance

---

## Next Steps

1. ✅ Install dependencies
2. ✅ Run sample tests
3. ✅ Write your first test
4. ✅ Run tests with coverage
5. ✅ Check CI/CD integration

**Happy Testing!** 🚀
