# Frontend Components Implementation

## Overview

This document describes the core Vue components implemented for the simFocus frontend application.

## Implementation Status

✅ **Priority 1: Common Components** - Complete
✅ **Priority 2: Layout Components** - Complete
✅ **Priority 3: Auth Components** - Complete
✅ **Priority 4: Root Components** - Complete

## Component Structure

```
components/
├── common/              # Reusable UI components
│   ├── AppButton.vue
│   ├── AppInput.vue
│   ├── AppCard.vue
│   ├── AppModal.vue
│   ├── AppLoading.vue
│   ├── AppAvatar.vue
│   ├── AppSelect.vue
│   ├── AppTextarea.vue
│   └── index.ts
├── layout/              # Application layout components
│   ├── MainLayout.vue
│   ├── AppHeader.vue
│   ├── AppSidebar.vue
│   ├── AppFooter.vue
│   └── index.ts
├── auth/                # Authentication components
│   ├── LoginForm.vue
│   ├── RegisterForm.vue
│   ├── ForgotPassword.vue
│   └── index.ts
└── index.ts            # Global exports
```

## Common Components

### AppButton.vue
Reusable button component with multiple variants and sizes.

**Props:**
- `type`: 'primary' | 'success' | 'warning' | 'danger' | 'info' | 'text' | 'default'
- `size`: 'large' | 'default' | 'small'
- `loading`: boolean
- `disabled`: boolean
- `plain`: boolean
- `round`: boolean
- `circle`: boolean
- `block`: boolean

**Events:**
- `click`: Emitted when button is clicked

**Usage:**
```vue
<AppButton type="primary" size="large" :loading="isLoading" @click="handleClick">
  Submit
</AppButton>
```

### AppInput.vue
Text input component with validation support.

**Props:**
- `modelValue`: string | number
- `type`: 'text' | 'textarea' | 'password' | 'number' | 'email' | 'tel' | 'url'
- `label`: string
- `name`: string
- `placeholder`: string
- `disabled`: boolean
- `readonly`: boolean
- `clearable`: boolean
- `showPassword`: boolean
- `maxlength`: number
- `showWordLimit`: boolean
- `required`: boolean
- `rules`: any[]

**Events:**
- `update:modelValue`
- `blur`
- `focus`
- `clear`
- `change`

### AppCard.vue
Card container component with header and footer slots.

**Props:**
- `shadow`: 'always' | 'hover' | 'never'
- `bordered`: boolean
- `hoverable`: boolean
- `bodyStyle`: CSSProperties

**Slots:**
- `header`: Card header content
- `default`: Card body content
- `footer`: Card footer content

### AppModal.vue
Modal dialog component with customization options.

**Props:**
- `modelValue`: boolean
- `title`: string
- `width`: string | number
- `fullscreen`: boolean
- `closeOnClickModal`: boolean
- `closeOnPressEscape`: boolean
- `draggable`: boolean

**Events:**
- `update:modelValue`
- `open`
- `close`
- `opened`
- `closed`

### AppLoading.vue
Loading spinner component with different styles.

**Props:**
- `text`: string
- `size`: 'small' | 'default' | 'large'
- `type`: 'default' | 'spinner' | 'dots'

**Usage:**
```vue
<AppLoading text="Loading..." size="large" type="spinner" />
```

### AppAvatar.vue
Avatar component with fallback initials.

**Props:**
- `src`: string
- `alt`: string
- `name`: string (used for initials fallback)
- `size`: number | 'large' | 'default' | 'small'
- `shape`: 'circle' | 'square'

### AppSelect.vue
Select dropdown component with support for remote search.

**Props:**
- `modelValue`: string | number | boolean | Array
- `placeholder`: string
- `disabled`: boolean
- `clearable`: boolean
- `filterable`: boolean
- `allowCreate`: boolean
- `multiple`: boolean
- `remote`: boolean
- `loading`: boolean

### AppTextarea.vue
Textarea input component.

**Props:**
- `modelValue`: string
- `placeholder`: string
- `rows`: number
- `autosize`: boolean | { minRows, maxRows }
- `maxlength`: number
- `showWordLimit`: boolean

## Layout Components

### MainLayout.vue
Main application layout wrapper with header, sidebar, and footer.

**Features:**
- Responsive sidebar that collapses on mobile
- Page transition animations
- Automatic scroll to top on navigation
- CSS custom properties for dynamic sizing

**Usage:**
```vue
<template>
  <MainLayout>
    <router-view />
  </MainLayout>
</template>
```

### AppHeader.vue
Top navigation bar with search, notifications, and user menu.

**Features:**
- Logo and branding
- Global search functionality
- Notification badge
- User dropdown menu with theme toggle
- Responsive design with mobile menu toggle

**Events:**
- `toggle-sidebar`: Emitted when sidebar toggle is clicked

### AppSidebar.vue
Side navigation menu with collapsible items.

**Features:**
- Nested menu items support
- Active route highlighting
- Collapse/expand functionality
- Hover behavior (optional)
- Custom scrollbar styling

**Props:**
- `collapsed`: boolean

**Events:**
- `toggle-collapse`: Emitted when collapse toggle is clicked

**Menu Structure:**
The sidebar uses a dynamic menu configuration that can be extended:
```typescript
const menuItems = [
  { title: 'Dashboard', path: '/dashboard', icon: House },
  { title: 'Topics', path: '/topics', icon: Document },
  // ...
]
```

### AppFooter.vue
Application footer with links and social media icons.

**Features:**
- Copyright notice with dynamic year
- Navigation links (About, Privacy, Terms, Contact)
- Social media icons
- Responsive layout

## Auth Components

### LoginForm.vue
Login form with email/password authentication and social login options.

**Features:**
- Email and password validation
- Remember me checkbox
- Forgot password link
- Social login (Google, GitHub)
- Loading state handling
- Form validation with Element Plus

**Events:**
- `success`: Emitted after successful login

**Validation Rules:**
- Email: required, valid email format
- Password: required, minimum 6 characters

### RegisterForm.vue
Registration form with comprehensive validation.

**Features:**
- Name, email, password fields
- Confirm password validation
- Password strength requirements (uppercase, lowercase, number)
- Terms of service agreement checkbox
- Social login options
- Real-time validation feedback

**Events:**
- `success`: Emitted after successful registration

**Validation Rules:**
- Name: required, minimum 2 characters
- Email: required, valid email format
- Password: required, minimum 8 characters, must contain uppercase, lowercase, and number
- Confirm Password: required, must match password
- Terms: must be agreed to

### ForgotPassword.vue
Password reset request form.

**Features:**
- Email input with validation
- Clear instructions for users
- Back to login link
- Loading state handling

**Events:**
- `success`: Emitted after reset email is sent

## Usage Examples

### Importing Components

You can import components in two ways:

**Individual imports:**
```vue
<script setup lang="ts">
import AppButton from '@/components/common/AppButton.vue'
import AppInput from '@/components/common/AppInput.vue'
</script>
```

**Category imports:**
```vue
<script setup lang="ts">
import { AppButton, AppInput } from '@/components/common'
</script>
```

**Global imports:**
```vue
<script setup lang="ts">
import { AppButton, AppInput, MainLayout } from '@/components'
</script>
```

### Complete Example: Login Page

```vue
<template>
  <div class="auth-page">
    <div class="auth-container">
      <div class="auth-header">
        <h1>Welcome Back</h1>
        <p>Sign in to your account to continue</p>
      </div>

      <LoginForm @success="handleLoginSuccess" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { LoginForm } from '@/components/auth'

const router = useRouter()

const handleLoginSuccess = () => {
  router.push('/dashboard')
}
</script>

<style scoped lang="scss">
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--el-bg-color-page);
}

.auth-container {
  max-width: 400px;
  width: 100%;
  padding: 24px;
}

.auth-header {
  text-align: center;
  margin-bottom: 32px;

  h1 {
    font-size: 28px;
    font-weight: 600;
    margin-bottom: 8px;
  }

  p {
    color: var(--el-text-color-secondary);
  }
}
</style>
```

### Complete Example: Using MainLayout

```vue
<template>
  <MainLayout>
    <template #default>
      <AppCard>
        <template #header>
          <h2>Dashboard</h2>
        </template>

        <p>Welcome to your dashboard!</p>

        <template #footer>
          <AppButton type="primary" @click="handleAction">
            Take Action
          </AppButton>
        </template>
      </AppCard>
    </template>
  </MainLayout>
</template>

<script setup lang="ts">
import { MainLayout } from '@/components/layout'
import { AppCard, AppButton } from '@/components/common'

const handleAction = () => {
  console.log('Action button clicked')
}
</script>
```

## Styling Conventions

All components follow consistent styling conventions:

1. **CSS Variables**: Use Element Plus CSS variables for theming
2. **Scoped Styles**: All component styles are scoped
3. **Responsive Design**: Mobile-first approach with breakpoints
4. **Transitions**: Consistent 0.3s ease transitions
5. **Spacing**: Use consistent spacing scale (4, 8, 12, 16, 20, 24, 32px)

### CSS Custom Properties

The layout uses CSS custom properties for dynamic sizing:

```css
:root {
  --header-height: 60px;
  --sidebar-width: 240px;
  --sidebar-collapsed-width: 64px;
  --footer-height: 50px;
}
```

## Integration with Element Plus

All components are built on top of Element Plus and follow its conventions:

- **Form Validation**: Uses Element Plus form validation system
- **Icons**: Uses `@element-plus/icons-vue` package
- **Theming**: Respects Element Plus theme variables
- **Internationalization**: Compatible with vue-i18n

## Error Handling

The application includes comprehensive error handling:

1. **Global Error Handler** (main.ts):
   - Catches Vue component errors
   - Shows user-friendly error messages
   - Logs errors in development
   - Prepared for Sentry integration

2. **Component Error Handler** (App.vue):
   - Uses `onErrorCaptured` lifecycle hook
   - Prevents error propagation
   - Shows error notifications

3. **Promise Rejection Handler** (main.ts):
   - Catches unhandled promise rejections
   - Shows error messages in production

## Performance Considerations

1. **Lazy Loading**: Components are code-split by default
2. **Tree Shaking**: Unused components are eliminated in production
3. **Transition Optimization**: Page transitions are GPU-accelerated
4. **Responsive Images**: Avatar component supports responsive sizing
5. **Virtual Scrolling**: Prepared for large lists (future implementation)

## Accessibility

All components follow WCAG 2.1 AA guidelines:

- **Keyboard Navigation**: Full keyboard support
- **ARIA Labels**: Proper ARIA attributes
- **Focus Management**: Logical focus flow
- **Screen Reader Support**: Compatible with screen readers
- **Color Contrast**: Meets contrast requirements

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Future Enhancements

Potential improvements for future iterations:

1. **Additional Common Components**:
   - AppTable (data table with sorting/filtering)
   - AppEmpty (empty state component)
   - AppError (error state component)
   - AppTooltip (enhanced tooltip)
   - AppPagination (pagination control)

2. **Enhanced Layout Components**:
   - Breadcrumb component
   - Tabs component
   - Collapse/Accordion component

3. **Advanced Auth Components**:
   - ResetPassword.vue (password reset confirmation)
   - EmailVerification.vue (email verification prompt)
   - TwoFactorAuth.vue (2FA setup)

4. **Form Enhancements**:
   - File upload component
   - Rich text editor
   - Date/time picker wrapper
   - Form validation composable

## Testing

Components are designed to be testable with Vitest and Vue Test Utils:

```typescript
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { AppButton } from '@/components/common'

describe('AppButton', () => {
  it('emits click event when clicked', async () => {
    const wrapper = mount(AppButton)
    await wrapper.trigger('click')
    expect(wrapper.emitted('click')).toBeTruthy()
  })

  it('does not emit click when disabled', async () => {
    const wrapper = mount(AppButton, { props: { disabled: true } })
    await wrapper.trigger('click')
    expect(wrapper.emitted('click')).toBeFalsy()
  })
})
```

## Maintenance

When updating components:

1. Keep prop interfaces minimal and focused
2. Use TypeScript for all props and emits
3. Document complex props with JSDoc comments
4. Maintain consistent naming conventions
5. Update this README when adding new components
6. Test responsive behavior on mobile devices
7. Verify accessibility with keyboard navigation

## Contributing

When adding new components:

1. Create component in appropriate directory
2. Add TypeScript props interface
3. Implement with Composition API
4. Add scoped styles
5. Export from index.ts
6. Document in this README
7. Add usage examples
8. Test on multiple browsers

---

**Last Updated**: 2026-01-13
**Version**: 1.0.0
