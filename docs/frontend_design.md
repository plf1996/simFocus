# Frontend Design Document
# simFocus - AI Virtual Focus Group Platform

**Document Version**: 1.0
**Date**: 2026-01-12
**Author**: Frontend Architect
**Status**: Design Phase

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [UI Component Library Selection](#2-ui-component-library-selection)
3. [Project Structure](#3-project-structure)
4. [Component Architecture](#4-component-architecture)
5. [State Management (Pinia)](#5-state-management-pinia)
6. [Routing Design](#6-routing-design)
7. [API Integration](#7-api-integration)
8. [WebSocket Integration](#8-websocket-integration)
9. [TypeScript Types](#9-typescript-types)
10. [Styling Strategy](#10-styling-strategy)
11. [Performance Optimization](#11-performance-optimization)
12. [Testing Strategy](#12-testing-strategy)

---

## 1. Executive Summary

### 1.1 Frontend Architecture Overview

The simFocus frontend is built using **Vue 3 + TypeScript** with a component-based architecture:

- **Framework**: Vue 3 Composition API with `<script setup>`
- **State Management**: Pinia for global state
- **Routing**: Vue Router 4 with lazy loading
- **UI Library**: Element Plus (recommended, see section 2)
- **Real-time**: Socket.IO Client for WebSocket connections
- **HTTP Client**: Axios with interceptors
- **Build Tool**: Vite for fast development and optimized production builds
- **Styling**: SCSS with CSS variables for theming

### 1.2 Design Principles

| Principle | Implementation |
|-----------|----------------|
| **Component-First** | Feature-based component organization, reusable UI library |
| **Type Safety** | Strict TypeScript with shared types from `shared/` |
| **Progressive Enhancement** | Core features first, advanced features lazy-loaded |
| **Performance** | Code splitting, virtual scrolling, debounced inputs |
| **Accessibility** | WCAG 2.1 AA compliance, keyboard navigation, ARIA labels |
| **Responsive Design** | Mobile-first approach, desktop primary (1920x1080+) |

---

## 2. UI Component Library Selection

### 2.1 Comparison Matrix

| Feature | Element Plus | Naive UI | PrimeVue | Winner |
|---------|-------------|----------|----------|--------|
| **Vue 3 Support** | Native, first-party | Native | Native (Vue 3 port) | Tie |
| **TypeScript** | Excellent built-in types | Excellent | Good | Element Plus |
| **Component Count** | 60+ | 80+ | 90+ | PrimeVue |
| **Documentation** | Excellent (Chinese + English) | Good | Good | Element Plus |
| **Bundle Size** | ~600 KB gzipped | ~400 KB gzipped | ~500 KB gzipped | Naive UI |
| **Tree Shaking** | Auto import support | Auto import support | Manual import | Element Plus |
| **Theme System** | SCSS variables | CSS variables | PrimeVue themes | Element Plus |
| **Form Validation** | Built-in, powerful | Built-in, flexible | Built-in | Element Plus |
| **Table Component** | Feature-rich, virtual scroll | Feature-rich | Feature-rich | Tie |
| **Community** | Large (Chinese-focused) | Growing | Large (Vue-focused) | Element Plus |
| **Icons** | Separate package (@element-plus/icons-vue) | Built-in | Built-in | Tie |
| **Accessibility** | Good ARIA support | Good ARIA support | Good ARIA support | Tie |

### 2.2 Recommendation: **Element Plus**

#### Rationale

1. **Best Vue 3 + TypeScript Integration**
   - First-party library from Vue team members
   - Excellent TypeScript definitions out of the box
   - Seamless integration with Vue 3 Composition API

2. **Rich Component Set for Enterprise Use**
   - Complex Table component with virtual scrolling (needed for message history)
   - Advanced Form components with validation
   - Data visualization components (Charts integration)
   - Loading, Message, Notification utilities

3. **Strong Form System**
   - Built-in validation rules
   - Async validation support
   - Dynamic form fields
   - Perfect for character configuration forms

4. **Developer Experience**
   - Auto-import plugin reduces boilerplate
   - Excellent documentation with Chinese translations
   - Active community and long-term maintenance

5. **Theming Flexibility**
   - SCSS variables for easy customization
   - Dark mode support
   - Brand color customization

#### Component Usage Mapping

| simFocus Feature | Element Plus Components |
|-----------------|------------------------|
| Authentication | `ElForm`, `ElInput`, `ElButton` |
| Character Selection | `ElCard`, `ElCheckbox`, `ElTag` |
| Discussion Room | `ElScrollbar`, `ElAvatar`, `ElProgress` |
| Message List | `Virtual List` (custom with ElTable) |
| Report View | `ElDescriptions`, `ElTimeline`, `ECharts` |
| API Key Management | `ElDialog`, `ElForm`, `ElInput` (type="password") |
| Navigation | `ElMenu`, `ElBreadcrumb`, `ElPagination` |
| Feedback | `ElMessage`, `ElNotification`, `ElMessageBox` |

### 2.3 Installation Configuration

```bash
# Install dependencies
npm install element-plus @element-plus/icons-vue

# Install auto-import plugin
npm install -D unplugin-vue-components unplugin-auto-import
```

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

export default defineConfig({
  plugins: [
    vue(),
    AutoImport({
      resolvers: [ElementPlusResolver()],
    }),
    Components({
      resolvers: [ElementPlusResolver()],
    }),
  ],
})
```

### 2.4 Theme Customization

```scss
// src/assets/styles/element-variables.scss
@forward 'element-plus/theme-chalk/src/common/var.scss' with (
  $colors: (
    'primary': (
      'base': #409eff,
    ),
  ),
  $button-font-weight: 500,
);

// Custom brand colors for simFocus
:root {
  --el-color-primary: #6366f1; // Indigo 500
  --el-color-success: #10b981; // Emerald 500
  --el-color-warning: #f59e0b; // Amber 500
  --el-color-danger: #ef4444;  // Red 500
  --el-color-info: #6b7280;    // Gray 500
}
```

---

## 3. Project Structure

### 3.1 Complete Directory Layout

```
frontend/
├── src/
│   ├── assets/                      # Static Assets
│   │   ├── images/
│   │   │   ├── logo.svg
│   │   │   ├── logo-dark.svg
│   │   │   ├── default-avatar.png
│   │   │   └── character-avatars/
│   │   ├── icons/                   # Custom SVG icons
│   │   │   └── *.svg
│   │   └── styles/
│   │       ├── main.scss            # Global styles
│   │       ├── variables.scss       # CSS/SCSS variables
│   │       ├── mixins.scss          # SCSS mixins
│   │       ├── reset.scss           # Style reset
│   │       └── themes/
│   │           ├── light.scss
│   │           └── dark.scss
│   │
│   ├── components/                  # Vue Components
│   │   ├── common/                  # Reusable UI Components
│   │   │   ├── AppButton.vue        # Button wrapper
│   │   │   ├── AppInput.vue         # Input wrapper
│   │   │   ├── AppSelect.vue        # Select wrapper
│   │   │   ├── AppTextarea.vue      # Textarea wrapper
│   │   │   ├── AppModal.vue         # Modal wrapper
│   │   │   ├── AppCard.vue          # Card wrapper
│   │   │   ├── AppLoading.vue       # Loading spinner
│   │   │   ├── AppEmpty.vue         # Empty state
│   │   │   ├── AppError.vue         # Error state
│   │   │   ├── AppAvatar.vue        # Avatar with fallback
│   │   │   └── AppTooltip.vue       # Tooltip wrapper
│   │   │
│   │   ├── layout/                  # Layout Components
│   │   │   ├── AppHeader.vue        # Top navigation
│   │   │   ├── AppSidebar.vue       # Side navigation
│   │   │   ├── AppFooter.vue        # Footer
│   │   │   ├── MainLayout.vue       # Main layout wrapper
│   │   │   └── AuthLayout.vue       # Auth pages layout
│   │   │
│   │   ├── auth/                    # Authentication Components
│   │   │   ├── LoginForm.vue        # Login form
│   │   │   ├── RegisterForm.vue     # Registration form
│   │   │   ├── ForgotPassword.vue   # Password reset request
│   │   │   ├── ResetPassword.vue    # Password reset confirmation
│   │   │   └── SocialLogin.vue      # OAuth buttons (P1)
│   │   │
│   │   ├── topic/                   # Topic Management Components
│   │   │   ├── TopicForm.vue        # Create/edit topic form
│   │   │   ├── TopicList.vue        # List of user topics
│   │   │   ├── TopicCard.vue        # Topic list item
│   │   │   ├── TopicDetail.vue      # Topic detail view
│   │   │   └── TopicTemplate.vue    # Topic template selector (P1)
│   │   │
│   │   ├── character/               # Character Components
│   │   │   ├── CharacterSelector.vue    # Character selection interface
│   │   │   ├── CharacterCard.vue         # Character list item
│   │   │   ├── CharacterEditor.vue       # Character creation/editing
│   │   │   ├── CharacterPreview.vue      # Character preview modal
│   │   │   ├── CharacterLibrary.vue      # Character template library
│   │   │   ├── PersonalitySlider.vue     # Personality trait sliders
│   │   │   └── KnowledgeTag.vue         # Knowledge background tags
│   │   │
│   │   ├── discussion/              # Discussion Room Components
│   │   │   ├── DiscussionRoom.vue       # Main discussion room
│   │   │   ├── MessageList.vue          # Message container with scroll
│   │   │   ├── MessageBubble.vue        # Individual message display
│   │   │   ├── CharacterPanel.vue       # Participant list
│   │   │   ├── DiscussionControls.vue   # Pause/resume/speed controls
│   │   │   ├── ProgressBar.vue          # Discussion progress
│   │   │   ├── PhaseIndicator.vue       # Current phase badge
│   │   │   ├── InjectQuestionModal.vue  # Inject question dialog
│   │   │   └── TypingIndicator.vue      # "X is typing..." indicator
│   │   │
│   │   └── report/                  # Report Components
│   │       ├── ReportView.vue            # Main report view
│   │       ├── ReportSummary.vue         # Overview section
│   │       ├── ViewpointList.vue         # Character viewpoints
│   │       ├── ConsensusSection.vue      # Agreement highlights
│   │       ├── ControversyList.vue       # Disagreement points
│   │       ├── InsightList.vue           # Key insights
│   │       ├── RecommendationList.vue    # Action items
│   │       ├── ViewpointChart.vue        # Position distribution chart
│   │       ├── ControversyHeatmap.vue    # Discussion intensity map
│   │       ├── KeywordCloud.vue          # Word cloud visualization
│   │       └── ExportButton.vue          # Export options
│   │
│   ├── composables/                # Vue Composables (Reusable Logic)
│   │   ├── useAuth.ts               # Authentication state & actions
│   │   ├── useWebSocket.ts          # WebSocket connection management
│   │   ├── useDiscussion.ts         # Discussion state & operations
│   │   ├── useCharacter.ts          # Character operations
│   │   ├── useTopic.ts              # Topic operations
│   │   ├── useNotification.ts       # Toast/notification management
│   │   ├── useModal.ts              # Modal state management
│   │   ├── useDebounce.ts           # Debounce utility
│   │   ├── useThrottle.ts           # Throttle utility
│   │   ├── useInfiniteScroll.ts     # Infinite scroll for lists
│   │   ├── useLocalStorage.ts       # Local storage wrapper
│   │   ├── useBreakpoints.ts        # Responsive breakpoint detection
│   │   └── useVirtualList.ts        # Virtual scrolling for large lists
│   │
│   ├── stores/                      # Pinia Stores
│   │   ├── user.ts                  # User profile state
│   │   ├── auth.ts                  # Authentication state
│   │   ├── topic.ts                 # Topic state
│   │   ├── character.ts             # Character state
│   │   ├── discussion.ts            # Discussion state
│   │   ├── message.ts               # Message cache
│   │   ├── ui.ts                    # UI state (loading, modals)
│   │   └── settings.ts              # User preferences
│   │
│   ├── services/                    # API Service Layer
│   │   ├── api.ts                   # Axios instance & configuration
│   │   ├── auth.service.ts          # Auth API calls
│   │   ├── user.service.ts          # User API calls
│   │   ├── topic.service.ts         # Topic API calls
│   │   ├── character.service.ts     # Character API calls
│   │   ├── discussion.service.ts    # Discussion API calls
│   │   ├── report.service.ts        # Report API calls
│   │   └── upload.service.ts        # File upload (P1)
│   │
│   ├── types/                       # TypeScript Type Definitions
│   │   ├── index.ts                 # Export all types
│   │   ├── api.ts                   # API request/response types
│   │   ├── models.ts                # Domain model types
│   │   ├── character.ts             # Character configuration types
│   │   ├── discussion.ts            # Discussion state types
│   │   ├── report.ts                # Report data types
│   │   └── components.ts            # Component prop types
│   │
│   ├── router/                      # Vue Router Configuration
│   │   ├── index.ts                 # Router instance
│   │   ├── routes.ts                # Route definitions
│   │   └── guards.ts                # Navigation guards
│   │
│   ├── views/                       # Page-Level Components
│   │   ├── HomeView.vue             # Landing page
│   │   ├── LoginView.vue            # Login page
│   │   ├── RegisterView.vue         # Registration page
│   │   ├── ForgotPasswordView.vue   # Password reset request
│   │   ├── DashboardView.vue        # User dashboard
│   │   ├── TopicCreateView.vue      # Create new topic
│   │   ├── TopicEditView.vue        # Edit existing topic
│   │   ├── DiscussionRoomView.vue   # Active discussion room
│   │   ├── ReportView.vue           # View discussion report
│   │   ├── SettingsView.vue         # User settings
│   │   ├── ApiKeyView.vue           # API key management
│   │   └── NotFoundView.vue         # 404 page
│   │
│   ├── utils/                       # Utility Functions
│   │   ├── format.ts                # Formatters (date, currency, etc.)
│   │   ├── validators.ts            # Input validators
│   │   ├── constants.ts             # App constants
│   │   ├── helpers.ts               # Helper functions
│   │   ├── storage.ts               # Storage utilities
│   │   └── download.ts              # File download utilities
│   │
│   ├── socket/                      # Socket.IO Client
│   │   ├── client.ts                # Socket.IO configuration
│   │   ├── events.ts                # Event type definitions
│   │   └── handlers.ts              # Event handlers
│   │
│   ├── middleware/                  # Vue Middleware (Route Guards)
│   │   ├── auth.ts                  # Authentication check
│   │   └── subscription.ts          # Subscription check (future)
│   │
│   ├── App.vue                      # Root Component
│   └── main.ts                      # Application Entry Point
│
├── public/                          # Public Assets
│   ├── favicon.ico
│   ├── robots.txt
│   └── browserconfig.xml
│
├── tests/                           # Tests
│   ├── unit/                        # Unit tests (Vitest)
│   │   ├── components/
│   │   ├── composables/
│   │   └── stores/
│   ├── e2e/                         # E2E tests (Playwright)
│   │   ├── auth.spec.ts
│   │   ├── discussion.spec.ts
│   │   └── report.spec.ts
│   └── setup.ts                     # Test configuration
│
├── .env.example                    # Environment variables template
├── .env.development                # Development environment
├── .env.production                 # Production environment
├── .eslintrc.cjs                   # ESLint configuration
├── .prettierrc.json                # Prettier configuration
├── Dockerfile                      # Docker image
├── index.html                      # HTML entry point
├── package.json                    # Dependencies
├── tsconfig.json                   # TypeScript config
├── tsconfig.node.json              # TypeScript config for Node
├── vite.config.ts                  # Vite configuration
└── postcss.config.js               # PostCSS configuration
```

### 3.2 File Naming Conventions

| Type | Convention | Examples |
|------|------------|----------|
| **Components** | PascalCase | `CharacterCard.vue`, `DiscussionRoom.vue` |
| **Composables** | camelCase with `use` prefix | `useAuth.ts`, `useWebSocket.ts` |
| **Stores** | camelCase | `auth.ts`, `discussion.ts` |
| **Services** | camelCase with `.service` suffix | `auth.service.ts` |
| **Views** | PascalCase with `View` suffix | `DashboardView.vue` |
| **Utils** | camelCase | `format.ts`, `validators.ts` |
| **Types** | camelCase | `character.ts`, `discussion.ts` |
| **Styles** | kebab-case | `variables.scss`, `main.scss` |

---

## 4. Component Architecture

### 4.1 Component Hierarchy Diagram

```
App.vue
└── MainLayout.vue
    ├── AppHeader.vue
    ├── AppSidebar.vue
    ├── Router View
    │   ├── DashboardView.vue
    │   │   ├── TopicList.vue
    │   │   │   └── TopicCard.vue
    │   │   └── QuickActions.vue
    │   │
    │   ├── TopicCreateView.vue
    │   │   └── TopicForm.vue
    │   │       ├── AppInput.vue
    │   │       ├── AppTextarea.vue
    │   │       └── CharacterSelector.vue
    │   │           ├── CharacterLibrary.vue
    │   │           │   └── CharacterCard.vue
    │   │           └── SelectedCharacters.vue
    │   │
    │   ├── DiscussionRoomView.vue
    │   │   └── DiscussionRoom.vue
    │   │       ├── CharacterPanel.vue
    │   │       │   └── CharacterAvatar.vue
    │   │       ├── MessageList.vue
    │   │       │   ├── MessageBubble.vue
    │   │       │   └── TypingIndicator.vue
    │   │       ├── DiscussionControls.vue
    │   │       │   └── ProgressBar.vue
    │   │       └── PhaseIndicator.vue
    │   │
    │   └── ReportView.vue
    │       └── ReportView.vue
    │           ├── ReportSummary.vue
    │           ├── ViewpointChart.vue
    │           ├── ConsensusSection.vue
    │           ├── ControversyList.vue
    │           └── ExportButton.vue
    │
    └── AppFooter.vue

AuthLayout.vue
├── AppHeader.vue (simplified)
└── Router View
    ├── LoginView.vue
    │   └── LoginForm.vue
    ├── RegisterView.vue
    │   └── RegisterForm.vue
    └── ForgotPasswordView.vue
        └── ForgotPassword.vue
```

### 4.2 Component Design Patterns

#### 4.2.1 Smart vs Presentational Components

**Smart Components (Container Components)**
- Contain business logic
- Manage state via stores/composables
- Handle API calls
- Export minimal props

**Presentational Components (Dumb Components)**
- Receive all data via props
- Emit events for actions
- No direct API calls
- Highly reusable

**Example**:

```vue
<!-- Smart Component: CharacterSelector.vue -->
<template>
  <div class="character-selector">
    <CharacterLibrary
      :characters="availableCharacters"
      :selected-ids="selectedCharacterIds"
      @select="handleSelectCharacter"
    />
    <SelectedCharacters
      :characters="selectedCharacters"
      @remove="handleRemoveCharacter"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useCharacterStore } from '@/stores/character'
import CharacterLibrary from './CharacterLibrary.vue'
import SelectedCharacters from './SelectedCharacters.vue'

const characterStore = useCharacterStore()

const availableCharacters = computed(() => characterStore.templates)
const selectedCharacterIds = defineModel<string[]>()
const selectedCharacters = computed(() =>
  characterStore.templates.filter(c => selectedCharacterIds.value?.includes(c.id))
)

const handleSelectCharacter = (id: string) => {
  // Business logic: validate selection count
  if (selectedCharacterIds.value && selectedCharacterIds.value.length >= 7) {
    ElMessage.warning('Maximum 7 characters allowed')
    return
  }
  selectedCharacterIds.value?.push(id)
}

const handleRemoveCharacter = (id: string) => {
  selectedCharacterIds.value = selectedCharacterIds.value?.filter(i => i !== id)
}
</script>
```

```vue
<!-- Presentational Component: CharacterCard.vue -->
<template>
  <el-card
    :class="['character-card', { 'is-selected': isSelected }]"
    @click="$emit('select', character.id)"
  >
    <template #cover>
      <AppAvatar :src="character.avatar_url" :size="80" />
    </template>
    <h3>{{ character.name }}</h3>
    <p class="profession">{{ character.config.profession }}</p>
    <el-tag v-if="character.rating_avg" type="success">
      ★ {{ character.rating_avg }}
    </el-tag>
    <div class="personality-preview">
      <el-tag
        v-for="(value, key) in personalityPreview"
        :key="key"
        size="small"
      >
        {{ key }}: {{ value }}
      </el-tag>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Character } from '@/types'

interface Props {
  character: Character
  isSelected?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isSelected: false
})

defineEmits<{
  select: [id: string]
}>()

const personalityPreview = computed(() => ({
  openness: props.character.config.personality.openness,
  rigor: props.character.config.personality.rigor
}))
</script>

<style scoped lang="scss">
.character-card {
  cursor: pointer;
  transition: all 0.3s;

  &.is-selected {
    border-color: var(--el-color-primary);
    box-shadow: 0 0 0 2px var(--el-color-primary-light-7);
  }

  &:hover {
    transform: translateY(-2px);
  }
}
</style>
```

#### 4.2.2 Component Props Definition

```typescript
// types/components.ts
export interface CharacterCardProps {
  character: Character
  isSelected?: boolean
  showRating?: boolean
  size?: 'small' | 'medium' | 'large'
}

export interface MessageBubbleProps {
  message: DiscussionMessage
  isStreaming?: boolean
  highlightKeywords?: string[]
}

export interface DiscussionControlsProps {
  discussionId: string
  status: DiscussionStatus
  currentPhase: DiscussionPhase
  canInject?: boolean
}
```

```vue
<!-- Usage with defineProps -->
<script setup lang="ts">
import type { CharacterCardProps } from '@/types/components'

const props = withDefaults(defineProps<CharacterCardProps>(), {
  isSelected: false,
  showRating: true,
  size: 'medium'
})
</script>
```

#### 4.2.3 Component Events Definition

```vue
<script setup lang="ts">
// Define events with TypeScript
const emit = defineEmits<{
  select: [id: string]
  remove: [id: string]
  update: [data: CharacterConfig]
}>()

// Usage
const handleSelect = (id: string) => {
  emit('select', id)
}
</script>
```

### 4.3 Common Component Patterns

#### 4.3.1 Form Components

```vue
<!-- components/common/AppInput.vue -->
<template>
  <el-form-item
    :label="label"
    :prop="name"
    :rules="rules"
    :error="error"
  >
    <el-input
      v-model="inputValue"
      :type="type"
      :placeholder="placeholder"
      :disabled="disabled"
      :readonly="readonly"
      :clearable="clearable"
      :show-password="showPassword"
      @blur="handleBlur"
      @focus="handleFocus"
    >
      <template v-if="$slots.prepend" #prepend>
        <slot name="prepend" />
      </template>
      <template v-if="$slots.append" #append>
        <slot name="append" />
      </template>
      <template v-if="$slots.prefix" #prefix>
        <slot name="prefix" />
      </template>
      <template v-if="$slots.suffix" #suffix>
        <slot name="suffix" />
      </template>
    </el-input>
  </el-form-item>
</template>

<script setup lang="ts">
interface Props {
  modelValue: string | number
  label?: string
  name?: string
  type?: 'text' | 'textarea' | 'password' | 'number' | 'email'
  placeholder?: string
  disabled?: boolean
  readonly?: boolean
  clearable?: boolean
  showPassword?: boolean
  rules?: any[]
  error?: string
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  clearable: true
})

const emit = defineEmits<{
  'update:modelValue': [value: string | number]
  blur: [event: FocusEvent]
  focus: [event: FocusEvent]
}>()

const inputValue = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const handleBlur = (event: FocusEvent) => emit('blur', event)
const handleFocus = (event: FocusEvent) => emit('focus', event)
</script>
```

#### 4.3.2 Async Data Components

```vue
<!-- components/topic/TopicList.vue -->
<template>
  <div class="topic-list">
    <!-- Loading State -->
    <AppLoading v-if="isLoading" />

    <!-- Error State -->
    <AppError
      v-else-if="error"
      :message="error.message"
      @retry="fetchTopics"
    />

    <!-- Empty State -->
    <AppEmpty
      v-else-if="topics.length === 0"
      message="No topics yet. Create your first discussion!"
      :action="{ label: 'Create Topic', to: '/topics/create' }"
    />

    <!-- Content -->
    <TransitionGroup
      v-else
      name="list"
      tag="div"
      class="topic-grid"
    >
      <TopicCard
        v-for="topic in topics"
        :key="topic.id"
        :topic="topic"
        @edit="handleEdit"
        @delete="handleDelete"
      />
    </TransitionGroup>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { topicService } from '@/services/topic.service'
import type { Topic } from '@/types'

const router = useRouter()
const topics = ref<Topic[]>([])
const isLoading = ref(true)
const error = ref<Error | null>(null)

const fetchTopics = async () => {
  isLoading.value = true
  error.value = null
  try {
    topics.value = await topicService.list()
  } catch (e) {
    error.value = e as Error
  } finally {
    isLoading.value = false
  }
}

const handleEdit = (topic: Topic) => {
  router.push(`/topics/${topic.id}/edit`)
}

const handleDelete = async (topic: Topic) => {
  try {
    await ElMessageBox.confirm(
      `Delete topic "${topic.title}"? This cannot be undone.`,
      'Confirm Delete',
      { type: 'warning' }
    )
    await topicService.delete(topic.id)
    topics.value = topics.value.filter(t => t.id !== topic.id)
    ElMessage.success('Topic deleted')
  } catch {
    // User cancelled
  }
}

onMounted(() => {
  fetchTopics()
})
</script>

<style scoped lang="scss">
.topic-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.list-enter-active,
.list-leave-active {
  transition: all 0.3s ease;
}

.list-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.list-leave-to {
  opacity: 0;
  transform: scale(0.9);
}
</style>
```

---

## 5. State Management (Pinia)

### 5.1 Store Architecture

```
stores/
├── auth.ts           # Authentication state (user, token)
├── user.ts           # User profile, preferences
├── topic.ts          # Topic CRUD, pagination
├── character.ts      # Character templates, selections
├── discussion.ts     # Active discussion state
├── message.ts        # Message cache for real-time updates
├── ui.ts             # Global UI state (loading, notifications)
└── settings.ts       # User settings (theme, language)
```

### 5.2 Store Definitions

#### 5.2.1 Auth Store

```typescript
// stores/auth.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/services/api'
import type { LoginRequest, RegisterRequest, User } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)
  const isLoading = ref(false)

  // Computed
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isEmailVerified = computed(() => user.value?.email_verified ?? false)

  // Actions
  async function login(credentials: LoginRequest) {
    isLoading.value = true
    try {
      const response = await authApi.login(credentials)
      token.value = response.access_token
      refreshToken.value = response.refresh_token
      await fetchUser()
    } finally {
      isLoading.value = false
    }
  }

  async function register(data: RegisterRequest) {
    isLoading.value = true
    try {
      const response = await authApi.register(data)
      token.value = response.access_token
      refreshToken.value = response.refresh_token
      await fetchUser()
    } finally {
      isLoading.value = false
    }
  }

  async function fetchUser() {
    if (!token.value) return
    const response = await authApi.getCurrentUser()
    user.value = response
  }

  async function logout() {
    try {
      await authApi.logout()
    } finally {
      user.value = null
      token.value = null
      refreshToken.value = null
      // Clear persisted state
      localStorage.removeItem('auth-storage')
    }
  }

  async function refreshAccessToken() {
    if (!refreshToken.value) throw new Error('No refresh token')
    const response = await authApi.refreshToken({ refresh_token: refreshToken.value })
    token.value = response.access_token
    refreshToken.value = response.refresh_token
    return response.access_token
  }

  // Initialize from storage
  function initialize() {
    const stored = localStorage.getItem('auth-storage')
    if (stored) {
      const { token: storedToken, user: storedUser } = JSON.parse(stored)
      token.value = storedToken
      user.value = storedUser
    }
  }

  return {
    // State
    user,
    token,
    refreshToken,
    isLoading,
    // Computed
    isAuthenticated,
    isEmailVerified,
    // Actions
    login,
    register,
    fetchUser,
    logout,
    refreshAccessToken,
    initialize
  }
}, {
  persist: {
    key: 'auth-storage',
    storage: localStorage,
    paths: ['user', 'token', 'refreshToken']
  }
})
```

#### 5.2.2 Discussion Store

```typescript
// stores/discussion.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { discussionApi } from '@/services/api'
import type { Discussion, DiscussionCreate, DiscussionStatus } from '@/types'

export const useDiscussionStore = defineStore('discussion', () => {
  // State
  const activeDiscussion = ref<Discussion | null>(null)
  const discussions = ref<Discussion[]>([])
  const isLoading = ref(false)
  const error = ref<Error | null>(null)

  // Computed
  const activeDiscussionId = computed(() => activeDiscussion.value?.id ?? null)
  const isActive = computed(() =>
    activeDiscussion.value?.status === 'running'
  )
  const isPaused = computed(() =>
    activeDiscussion.value?.status === 'paused'
  )
  const progress = computed(() =>
    activeDiscussion.value
      ? (activeDiscussion.value.current_round / activeDiscussion.value.max_rounds) * 100
      : 0
  )

  // Actions
  async function createDiscussion(data: DiscussionCreate) {
    isLoading.value = true
    error.value = null
    try {
      const discussion = await discussionApi.create(data)
      discussions.value.unshift(discussion)
      return discussion
    } catch (e) {
      error.value = e as Error
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function fetchDiscussion(id: string) {
    isLoading.value = true
    error.value = null
    try {
      const discussion = await discussionApi.getById(id)
      activeDiscussion.value = discussion
      return discussion
    } catch (e) {
      error.value = e as Error
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function startDiscussion(id: string) {
    const discussion = await discussionApi.start(id)
    if (activeDiscussion.value?.id === id) {
      activeDiscussion.value = discussion
    }
    updateDiscussionInList(discussion)
    return discussion
  }

  async function pauseDiscussion(id: string) {
    const discussion = await discussionApi.pause(id)
    if (activeDiscussion.value?.id === id) {
      activeDiscussion.value = discussion
    }
    updateDiscussionInList(discussion)
    return discussion
  }

  async function resumeDiscussion(id: string) {
    const discussion = await discussionApi.resume(id)
    if (activeDiscussion.value?.id === id) {
      activeDiscussion.value = discussion
    }
    updateDiscussionInList(discussion)
    return discussion
  }

  async function stopDiscussion(id: string) {
    const discussion = await discussionApi.stop(id)
    if (activeDiscussion.value?.id === id) {
      activeDiscussion.value = discussion
    }
    updateDiscussionInList(discussion)
    return discussion
  }

  function updateActiveDiscussion(data: Partial<Discussion>) {
    if (activeDiscussion.value) {
      activeDiscussion.value = { ...activeDiscussion.value, ...data }
    }
  }

  function updateDiscussionInList(discussion: Discussion) {
    const index = discussions.value.findIndex(d => d.id === discussion.id)
    if (index !== -1) {
      discussions.value[index] = discussion
    }
  }

  function clearActiveDiscussion() {
    activeDiscussion.value = null
  }

  return {
    // State
    activeDiscussion,
    discussions,
    isLoading,
    error,
    // Computed
    activeDiscussionId,
    isActive,
    isPaused,
    progress,
    // Actions
    createDiscussion,
    fetchDiscussion,
    startDiscussion,
    pauseDiscussion,
    resumeDiscussion,
    stopDiscussion,
    updateActiveDiscussion,
    clearActiveDiscussion
  }
})
```

#### 5.2.3 Message Store (Real-time)

```typescript
// stores/message.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { DiscussionMessage, DiscussionStatus } from '@/types'

export const useMessageStore = defineStore('message', () => {
  // State
  const messages = ref<Map<string, DiscussionMessage[]>>(new Map())
  const typingCharacters = ref<Set<string>>(new Set())
  const streamingContent = ref<Map<string, string>>(new Map())

  // Computed
  const getMessages = computed(() => (discussionId: string) =>
    messages.value.get(discussionId) ?? []
  )

  const isTyping = computed(() => (characterId: string) =>
    typingCharacters.value.has(characterId)
  )

  const getStreamingMessage = computed(() => (messageId: string) =>
    streamingContent.value.get(messageId) ?? ''
  )

  // Actions
  function setMessages(discussionId: string, messageList: DiscussionMessage[]) {
    messages.value.set(discussionId, messageList)
  }

  function addMessage(discussionId: string, message: DiscussionMessage) {
    const list = messages.value.get(discussionId) ?? []
    list.push(message)
    messages.value.set(discussionId, list)
  }

  function updateStreamingMessage(messageId: string, content: string) {
    streamingContent.value.set(messageId, content)
  }

  function completeStreamingMessage(messageId: string, finalContent: string) {
    streamingContent.value.delete(messageId)
    // Update the actual message in discussion
    for (const [discussionId, messageList] of messages.value) {
      const message = messageList.find(m => m.id === messageId)
      if (message) {
        message.content = finalContent
        break
      }
    }
  }

  function setTyping(characterId: string, isTyping: boolean) {
    if (isTyping) {
      typingCharacters.value.add(characterId)
    } else {
      typingCharacters.value.delete(characterId)
    }
  }

  function clearMessages(discussionId: string) {
    messages.value.delete(discussionId)
  }

  function clearAll() {
    messages.value.clear()
    typingCharacters.value.clear()
    streamingContent.value.clear()
  }

  return {
    // State
    messages,
    typingCharacters,
    streamingContent,
    // Computed
    getMessages,
    isTyping,
    getStreamingMessage,
    // Actions
    setMessages,
    addMessage,
    updateStreamingMessage,
    completeStreamingMessage,
    setTyping,
    clearMessages,
    clearAll
  }
})
```

#### 5.2.4 UI Store

```typescript
// stores/ui.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { NotificationItem } from '@/types'

export const useUiStore = defineStore('ui', () => {
  // Loading State
  const globalLoading = ref(false)
  const loadingComponent = ref<Set<string>>(new Set())

  function setLoading(key: string, isLoading: boolean) {
    if (isLoading) {
      loadingComponent.value.add(key)
    } else {
      loadingComponent.value.delete(key)
    }
    globalLoading.value = loadingComponent.value.size > 0
  }

  // Notifications
  const notifications = ref<NotificationItem[]>([])

  function showNotification(notification: Omit<NotificationItem, 'id'>) {
    const id = Date.now().toString()
    notifications.value.push({ ...notification, id })
    setTimeout(() => {
      removeNotification(id)
    }, notification.duration ?? 5000)
  }

  function removeNotification(id: string) {
    notifications.value = notifications.value.filter(n => n.id !== id)
  }

  // Modal State
  const activeModals = ref<Set<string>>(new Set())

  function openModal(key: string) {
    activeModals.value.add(key)
  }

  function closeModal(key: string) {
    activeModals.value.delete(key)
  }

  function isModalOpen(key: string) {
    return activeModals.value.has(key)
  }

  // Sidebar State (collapsed/expanded)
  const sidebarCollapsed = ref(false)

  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  // Theme
  const theme = ref<'light' | 'dark'>('light')

  function setTheme(newTheme: 'light' | 'dark') {
    theme.value = newTheme
    document.documentElement.classList.toggle('dark', newTheme === 'dark')
    localStorage.setItem('theme', newTheme)
  }

  function initializeTheme() {
    const stored = localStorage.getItem('theme') as 'light' | 'dark' | null
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    setTheme(stored ?? (prefersDark ? 'dark' : 'light'))
  }

  return {
    // Loading
    globalLoading,
    loadingComponent,
    setLoading,
    // Notifications
    notifications,
    showNotification,
    removeNotification,
    // Modal
    activeModals,
    openModal,
    closeModal,
    isModalOpen,
    // Sidebar
    sidebarCollapsed,
    toggleSidebar,
    // Theme
    theme,
    setTheme,
    initializeTheme
  }
}, {
  persist: {
    key: 'ui-storage',
    storage: localStorage,
    paths: ['sidebarCollapsed', 'theme']
  }
})
```

### 5.3 Store Persistence

```typescript
// main.ts
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'

const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

app.use(pinia)
```

---

## 6. Routing Design

### 6.1 Route Definitions

```typescript
// router/routes.ts
import type { RouteRecordRaw } from 'vue-router'

export const routes: RouteRecordRaw[] = [
  // Public Routes
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/HomeView.vue'),
    meta: { title: 'simFocus - AI Virtual Focus Groups' }
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
    meta: {
      title: 'Login',
      requiresGuest: true,
      layout: 'auth'
    }
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('@/views/RegisterView.vue'),
    meta: {
      title: 'Create Account',
      requiresGuest: true,
      layout: 'auth'
    }
  },
  {
    path: '/forgot-password',
    name: 'forgot-password',
    component: () => import('@/views/ForgotPasswordView.vue'),
    meta: {
      title: 'Reset Password',
      requiresGuest: true,
      layout: 'auth'
    }
  },
  {
    path: '/reset-password',
    name: 'reset-password',
    component: () => import('@/views/ResetPasswordView.vue'),
    meta: {
      title: 'Set New Password',
      requiresGuest: true,
      layout: 'auth'
    }
  },

  // Protected Routes
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: {
      title: 'Dashboard',
      requiresAuth: true
    }
  },

  // Topic Management
  {
    path: '/topics',
    name: 'topics',
    component: () => import('@/views/TopicListView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/topics/create',
    name: 'topic-create',
    component: () => import('@/views/TopicCreateView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/topics/:id/edit',
    name: 'topic-edit',
    component: () => import('@/views/TopicEditView.vue'),
    meta: { requiresAuth: true }
  },

  // Discussion Routes
  {
    path: '/discussions',
    name: 'discussions',
    component: () => import('@/views/DiscussionListView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/discussions/:id',
    name: 'discussion-room',
    component: () => import('@/views/DiscussionRoomView.vue'),
    meta: {
      requiresAuth: true,
      title: 'Discussion Room'
    }
  },
  {
    path: '/discussions/:id/report',
    name: 'discussion-report',
    component: () => import('@/views/ReportView.vue'),
    meta: {
      requiresAuth: true,
      title: 'Discussion Report'
    }
  },

  // Settings
  {
    path: '/settings',
    name: 'settings',
    redirect: '/settings/profile',
    meta: { requiresAuth: true }
  },
  {
    path: '/settings/profile',
    name: 'settings-profile',
    component: () => import('@/views/SettingsView.vue'),
    meta: { requiresAuth: true, title: 'Profile Settings' }
  },
  {
    path: '/settings/api-keys',
    name: 'settings-api-keys',
    component: () => import('@/views/ApiKeyView.vue'),
    meta: { requiresAuth: true, title: 'API Key Management' }
  },

  // Shared Reports (Public)
  {
    path: '/share/:slug',
    name: 'shared-report',
    component: () => import('@/views/SharedReportView.vue'),
    meta: {
      title: 'Shared Discussion',
      public: true
    }
  },

  // 404 Not Found
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFoundView.vue'),
    meta: { title: 'Page Not Found' }
  }
]
```

### 6.2 Router Configuration

```typescript
// router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import { routes } from './routes'
import { setupRouterGuards } from './guards'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else if (to.hash) {
      return { el: to.hash, behavior: 'smooth' }
    } else {
      return { top: 0 }
    }
  }
})

// Setup navigation guards
setupRouterGuards(router)

export default router
```

### 6.3 Navigation Guards

```typescript
// router/guards.ts
import type { Router } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'

export function setupRouterGuards(router: Router) {
  // Global before guard
  router.beforeEach((to, from, next) => {
    const authStore = useAuthStore()
    const uiStore = useUiStore()

    // Set page title
    if (to.meta.title) {
      document.title = typeof to.meta.title === 'string'
        ? to.meta.title
        : `${to.meta.title(to)} | simFocus`
    }

    // Close mobile sidebar on navigation
    if (uiStore.sidebarCollapsed === false && window.innerWidth < 768) {
      uiStore.toggleSidebar()
    }

    // Check authentication
    if (to.meta.requiresAuth && !authStore.isAuthenticated) {
      // Save intended destination
      localStorage.setItem('redirect', to.fullPath)
      return next({ name: 'login', query: { redirect: to.fullPath } })
    }

    // Redirect authenticated users away from auth pages
    if (to.meta.requiresGuest && authStore.isAuthenticated) {
      return next({ name: 'dashboard' })
    }

    // Email verification check
    if (to.meta.requiresAuth && !authStore.isEmailVerified && to.name !== 'settings-profile') {
      uiStore.showNotification({
        type: 'warning',
        message: 'Please verify your email to access all features'
      })
    }

    next()
  })

  // Global after guard
  router.afterEach((to, from) => {
    // Track page view (analytics)
    if (typeof gtag !== 'undefined') {
      gtag('event', 'page_view', {
        page_path: to.path,
        page_title: to.meta.title
      })
    }
  })

  // Error handler
  router.onError((error) => {
    console.error('Router error:', error)
    const uiStore = useUiStore()
    uiStore.showNotification({
      type: 'error',
      message: 'Failed to load page. Please try again.'
    })
  })
}
```

### 6.4 Route Meta Types

```typescript
// types/router.ts
import type { RouteMeta } from 'vue-router'

declare module 'vue-router' {
  interface RouteMeta {
    title?: string | ((route: RouteLocationNormalized) => string)
    requiresAuth?: boolean
    requiresGuest?: boolean
    public?: boolean
    layout?: 'default' | 'auth' | 'minimal'
    permissions?: string[]
    roles?: string[]
  }
}
```

### 6.5 Lazy Loading with Suspense

```vue
<!-- MainLayout.vue -->
<template>
  <Suspense>
    <template #default>
      <RouterView />
    </template>
    <template #fallback>
      <AppLoading />
    </template>
  </Suspense>
</template>
```

---

## 7. API Integration

### 7.1 Axios Configuration

```typescript
// services/api.ts
import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosError } from 'axios'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import router from '@/router'

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    const uiStore = useUiStore()

    // Add auth token
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }

    // Add request ID for tracing
    config.headers['X-Request-ID'] = generateRequestId()

    // Set loading state
    if (config.showLoading !== false) {
      uiStore.setLoading(config.url ?? 'request', true)
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    const uiStore = useUiStore()
    const url = response.config.url ?? 'request'

    // Clear loading state
    uiStore.setLoading(url, false)

    return response.data
  },
  async (error: AxiosError<ApiResponseError>) => {
    const authStore = useAuthStore()
    const uiStore = useUiStore()
    const url = error.config?.url ?? 'request'

    // Clear loading state
    uiStore.setLoading(url, false)

    // Handle error
    if (error.response) {
      const { status, data } = error.response
      const errorMessage = data?.error?.message || 'An error occurred'

      switch (status) {
        case 401:
          // Unauthorized - try refresh token
          if (authStore.refreshToken && !error.config?._retry) {
            error.config._retry = true
            try {
              const newToken = await authStore.refreshAccessToken()
              error.config.headers.Authorization = `Bearer ${newToken}`
              return api.request(error.config)
            } catch {
              authStore.logout()
              router.push({ name: 'login' })
            }
          } else {
            authStore.logout()
            router.push({ name: 'login' })
          }
          break

        case 403:
          uiStore.showNotification({
            type: 'error',
            message: 'You do not have permission to perform this action'
          })
          break

        case 404:
          uiStore.showNotification({
            type: 'warning',
            message: 'Resource not found'
          })
          break

        case 429:
          uiStore.showNotification({
            type: 'warning',
            message: 'Too many requests. Please wait a moment.'
          })
          break

        case 500:
        case 502:
        case 503:
        case 504:
          uiStore.showNotification({
            type: 'error',
            message: 'Server error. Please try again later.'
          })
          break

        default:
          uiStore.showNotification({
            type: 'error',
            message: errorMessage
          })
      }
    } else if (error.request) {
      // Network error
      uiStore.showNotification({
        type: 'error',
        message: 'Network error. Please check your connection.'
      })
    }

    return Promise.reject(error)
  }
)

// Utility: Generate request ID
function generateRequestId(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
}

// API Response Types
interface ApiResponseError {
  error: {
    code: string
    message: string
    details?: Record<string, unknown>
    request_id?: string
  }
}

export { api }
export default api
```

### 7.2 Service Layer Pattern

```typescript
// services/discussion.service.ts
import api from './api'
import type {
  Discussion,
  DiscussionCreate,
  DiscussionDetail,
  MessageResponse,
  InjectQuestionRequest
} from '@/types'

export const discussionService = {
  /**
   * Get all discussions for current user
   */
  async list(): Promise<Discussion[]> {
    return api.get('/discussions')
  },

  /**
   * Get discussion by ID
   */
  async getById(id: string): Promise<DiscussionDetail> {
    return api.get(`/discussions/${id}`)
  },

  /**
   * Create new discussion
   */
  async create(data: DiscussionCreate): Promise<Discussion> {
    return api.post('/discussions', data, { showLoading: true })
  },

  /**
   * Start discussion
   */
  async start(id: string): Promise<Discussion> {
    return api.post(`/discussions/${id}/start`)
  },

  /**
   * Pause discussion
   */
  async pause(id: string): Promise<Discussion> {
    return api.post(`/discussions/${id}/pause`)
  },

  /**
   * Resume discussion
   */
  async resume(id: string): Promise<Discussion> {
    return api.post(`/discussions/${id}/resume`)
  },

  /**
   * Stop discussion
   */
  async stop(id: string): Promise<Discussion> {
    return api.post(`/discussions/${id}/stop`)
  },

  /**
   * Inject question into discussion
   */
  async injectQuestion(id: string, data: InjectQuestionRequest): Promise<void> {
    return api.post(`/discussions/${id}/inject-question`, data)
  },

  /**
   * Get discussion messages
   */
  async getMessages(id: string, round?: number): Promise<MessageResponse[]> {
    return api.get(`/discussions/${id}/messages`, {
      params: round ? { round } : undefined
    })
  },

  /**
   * Delete discussion
   */
  async delete(id: string): Promise<void> {
    return api.delete(`/discussions/${id}`, { showLoading: true })
  }
}
```

### 7.3 File Upload Service (P1)

```typescript
// services/upload.service.ts
import api from './api'

export const uploadService = {
  /**
   * Upload file
   */
  async uploadFile(file: File, onProgress?: (progress: number) => void): Promise<{ url: string }> {
    const formData = new FormData()
    formData.append('file', file)

    return api.post('/uploads', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(percentCompleted)
        }
      }
    })
  },

  /**
   * Upload multiple files
   */
  async uploadFiles(
    files: File[],
    onProgress?: (fileIndex: number, progress: number) => void
  ): Promise<{ url: string }[]> {
    const uploads = files.map((file, index) =>
      this.uploadFile(file, (progress) => onProgress?.(index, progress))
    )
    return Promise.all(uploads)
  }
}
```

---

## 8. WebSocket Integration

### 8.1 Socket.IO Client Configuration

```typescript
// socket/client.ts
import { io, Socket } from 'socket.io-client'
import { useAuthStore } from '@/stores/auth'
import type { SocketEvents } from './events'

class SocketClient {
  private socket: Socket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5

  connect(discussionId: string): Socket {
    const authStore = useAuthStore()

    // Prevent duplicate connections
    if (this.socket?.connected) {
      return this.socket
    }

    const wsUrl = import.meta.env.VITE_WS_BASE_URL || window.location.origin
    const token = authStore.token

    this.socket = io(`${wsUrl}/v1/ws/discussions/${discussionId}`, {
      auth: { token },
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: this.maxReconnectAttempts,
      timeout: 10000,
      transports: ['websocket', 'polling']
    })

    this.setupEventHandlers()
    return this.socket
  }

  private setupEventHandlers() {
    if (!this.socket) return

    // Connection events
    this.socket.on('connect', () => {
      console.log('WebSocket connected')
      this.reconnectAttempts = 0
    })

    this.socket.on('disconnect', (reason) => {
      console.log('WebSocket disconnected:', reason)
      if (reason === 'io server disconnect') {
        // Server initiated disconnect, need manual reconnect
        this.socket?.connect()
      }
    })

    this.socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error)
      this.reconnectAttempts++
      if (this.reconnectAttempts >= this.maxReconnectAttempts) {
        // Show error to user
        const uiStore = useUiStore()
        uiStore.showNotification({
          type: 'error',
          message: 'Connection lost. Please refresh the page.'
        })
      }
    })

    // Ping/pong for connection health
    this.socket.on('pong', () => {
      // Update last seen timestamp
    })
  }

  disconnect() {
    this.socket?.disconnect()
    this.socket = null
  }

  emit(event: string, data?: unknown) {
    this.socket?.emit(event, data)
  }

  on(event: string, handler: (...args: unknown[]) => void) {
    this.socket?.on(event, handler)
  }

  off(event: string, handler?: (...args: unknown[]) => void) {
    this.socket?.off(event, handler)
  }

  isConnected(): boolean {
    return this.socket?.connected ?? false
  }
}

// Singleton instance
export const socketClient = new SocketClient()
```

### 8.2 Event Type Definitions

```typescript
// socket/events.ts
/**
 * Server -> Client Events
 */
export interface ServerToClientEvents {
  // Connection confirmation
  connected: (data: {
    discussion_id: string
    status: DiscussionStatus
  }) => void

  // New character message (streaming)
  message: (data: {
    message_id: string
    character_id: string
    character_name: string
    content: string
    round: number
    phase: DiscussionPhase
    timestamp: string
    is_streaming: boolean
  }) => void

  // Message complete (final)
  message_complete: (data: {
    message_id: string
    token_count: number
  }) => void

  // Discussion status update
  status: (data: {
    status: DiscussionStatus
    current_round: number
    total_rounds: number
    current_phase: DiscussionPhase
    progress_percentage: number
  }) => void

  // Character thinking indicator
  character_thinking: (data: {
    character_id: string
    character_name: string
  }) => void

  // Error notification
  error: (data: {
    code: string
    message: string
    retryable: boolean
  }) => void

  // Pong response to heartbeat
  pong: () => void
}

/**
 * Client -> Server Events
 */
export interface ClientToServerEvents {
  // Subscribe to discussion updates
  subscribe: (data: { discussion_id: string }) => void

  // Control commands
  control: (data: {
    control_type: 'pause' | 'resume' | 'speed' | 'inject'
    speed?: 1.0 | 1.5 | 2.0 | 3.0
    question?: string
  }) => void

  // Heartbeat (client-side ping)
  ping: () => void
}

export type SocketEvents = ServerToClientEvents & ClientToServerEvents
```

### 8.3 Event Handlers

```typescript
// socket/handlers.ts
import { socketClient } from './client'
import type { ServerToClientEvents } from './events'
import { useMessageStore } from '@/stores/message'
import { useDiscussionStore } from '@/stores/discussion'
import { useUiStore } from '@/stores/ui'

export function setupDiscussionHandlers(discussionId: string) {
  const socket = socketClient.connect(discussionId)
  const messageStore = useMessageStore()
  const discussionStore = useDiscussionStore()
  const uiStore = useUiStore()

  // Connection established
  socket.on('connected', (data) => {
    console.log('Connected to discussion:', data.discussion_id)
    discussionStore.updateActiveDiscussion({ status: data.status })
  })

  // New message (streaming)
  socket.on('message', (data) => {
    if (data.is_streaming) {
      // Update streaming content
      messageStore.updateStreamingMessage(data.message_id, data.content)
    } else {
      // Add complete message
      messageStore.addMessage(discussionId, {
        id: data.message_id,
        participant_id: data.character_id,
        character_name: data.character_name,
        round: data.round,
        phase: data.phase,
        content: data.content,
        token_count: 0, // Will be updated in message_complete
        is_injected_question: false,
        created_at: data.timestamp
      })
    }
  })

  // Message complete
  socket.on('message_complete', (data) => {
    messageStore.completeStreamingMessage(
      data.message_id,
      messageStore.getStreamingMessage(data.message_id)
    )
  })

  // Status update
  socket.on('status', (data) => {
    discussionStore.updateActiveDiscussion({
      status: data.status,
      current_round: data.current_round,
      current_phase: data.current_phase
    })
  })

  // Character thinking indicator
  socket.on('character_thinking', (data) => {
    messageStore.setTyping(data.character_id, true)
    // Clear typing indicator after 3 seconds
    setTimeout(() => {
      messageStore.setTyping(data.character_id, false)
    }, 3000)
  })

  // Error
  socket.on('error', (data) => {
    uiStore.showNotification({
      type: 'error',
      message: data.message,
      duration: data.retryable ? 3000 : 0
    })
  })

  // Cleanup function
  return () => {
    socket.off('connected')
    socket.off('message')
    socket.off('message_complete')
    socket.off('status')
    socket.off('character_thinking')
    socket.off('error')
  }
}

export function sendControlCommand(
  command: 'pause' | 'resume' | 'speed' | 'inject',
  params?: { speed?: number; question?: string }
) {
  socketClient.emit('control', {
    control_type: command,
    ...params
  })
}

// Heartbeat for connection health
let heartbeatInterval: number | null = null

export function startHeartbeat() {
  heartbeatInterval = window.setInterval(() => {
    if (socketClient.isConnected()) {
      socketClient.emit('ping')
    }
  }, 30000) // Every 30 seconds
}

export function stopHeartbeat() {
  if (heartbeatInterval) {
    clearInterval(heartbeatInterval)
    heartbeatInterval = null
  }
}
```

### 8.4 Composable Integration

```typescript
// composables/useWebSocket.ts
import { onUnmounted } from 'vue'
import { setupDiscussionHandlers, sendControlCommand, startHeartbeat, stopHeartbeat } from '@/socket/handlers'
import { socketClient } from '@/socket/client'

export function useWebSocket(discussionId: string) {
  let cleanup: (() => void) | null = null

  function connect() {
    cleanup = setupDiscussionHandlers(discussionId)
    startHeartbeat()
  }

  function disconnect() {
    stopHeartbeat()
    cleanup?.()
    socketClient.disconnect()
  }

  function pause() {
    sendControlCommand('pause')
  }

  function resume() {
    sendControlCommand('resume')
  }

  function setSpeed(speed: 1.0 | 1.5 | 2.0 | 3.0) {
    sendControlCommand('speed', { speed })
  }

  function injectQuestion(question: string) {
    sendControlCommand('inject', { question })
  }

  // Auto-cleanup on unmount
  onUnmounted(() => {
    disconnect()
  })

  return {
    connect,
    disconnect,
    pause,
    resume,
    setSpeed,
    injectQuestion,
    isConnected: () => socketClient.isConnected()
  }
}
```

---

## 9. TypeScript Types

### 9.1 Core Type Definitions

```typescript
// types/index.ts
// Export all types for easy importing
export * from './api'
export * from './models'
export * from './character'
export * from './discussion'
export * from './report'
export * from './components'
```

```typescript
// types/api.ts
/**
 * Generic API response wrapper
 */
export interface ApiResponse<T> {
  data: T
  message?: string
}

/**
 * Pagination parameters
 */
export interface PaginationParams {
  page?: number
  size?: number
  sort?: string
  order?: 'asc' | 'desc'
}

/**
 * Paginated response
 */
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

/**
 * API error response
 */
export interface ApiError {
  error: {
    code: string
    message: string
    details?: Record<string, unknown>
    request_id?: string
    timestamp?: string
  }
}
```

```typescript
// types/models.ts
/**
 * User model
 */
export interface User {
  id: string
  email: string
  name?: string
  avatar_url?: string
  bio?: string
  email_verified: boolean
  auth_provider: 'email' | 'google' | 'github'
  created_at: string
  last_login_at?: string
}

/**
 * Topic model
 */
export interface Topic {
  id: string
  user_id: string
  title: string
  description?: string
  context?: string
  attachments?: Attachment[]
  status: TopicStatus
  created_at: string
  updated_at: string
}

export interface Attachment {
  id: string
  name: string
  url: string
  type: string
  size: number
}

export type TopicStatus = 'draft' | 'ready' | 'in_discussion' | 'completed'

/**
 * Character model
 */
export interface Character {
  id: string
  user_id?: string
  name: string
  avatar_url?: string
  is_template: boolean
  is_public: boolean
  config: CharacterConfig
  usage_count: number
  rating_avg?: number
  rating_count: number
  created_at: string
}
```

```typescript
// types/character.ts
/**
 * Character configuration
 */
export interface CharacterConfig {
  age: number
  gender: Gender
  profession: string
  personality: PersonalityTraits
  knowledge: KnowledgeBackground
  stance: DiscussionStance
  expression_style: ExpressionStyle
  behavior_pattern: BehaviorPattern
}

export type Gender = 'male' | 'female' | 'other' | 'prefer_not_to_say'

export interface PersonalityTraits {
  openness: number      // 1-10
  rigor: number         // 1-10
  critical_thinking: number  // 1-10
  optimism: number      // 1-10
}

export interface KnowledgeBackground {
  fields: string[]
  experience_years: number
  representative_views: string[]
}

export type DiscussionStance =
  | 'support'
  | 'oppose'
  | 'neutral'
  | 'critical_exploration'

export type ExpressionStyle =
  | 'formal'
  | 'casual'
  | 'technical'
  | 'storytelling'

export type BehaviorPattern =
  | 'active'
  | 'passive'
  | 'balanced'
```

```typescript
// types/discussion.ts
/**
 * Discussion model
 */
export interface Discussion {
  id: string
  topic_id: string
  user_id: string
  discussion_mode: DiscussionMode
  max_rounds: number
  status: DiscussionStatus
  current_round: number
  current_phase: DiscussionPhase
  llm_provider: string
  llm_model: string
  total_tokens_used: number
  estimated_cost_usd?: number
  started_at?: string
  completed_at?: string
  created_at: string
}

export type DiscussionMode =
  | 'free'
  | 'structured'
  | 'creative'
  | 'consensus'

export type DiscussionStatus =
  | 'initialized'
  | 'running'
  | 'paused'
  | 'completed'
  | 'failed'
  | 'cancelled'

export type DiscussionPhase =
  | 'opening'
  | 'development'
  | 'debate'
  | 'closing'

/**
 * Discussion message
 */
export interface DiscussionMessage {
  id: string
  discussion_id: string
  participant_id: string
  character_name: string
  character_avatar?: string
  round: number
  phase: DiscussionPhase
  content: string
  token_count: number
  is_injected_question: boolean
  created_at: string
}

/**
 * Discussion participant
 */
export interface Participant {
  id: string
  character_id: string
  character_name: string
  character_avatar?: string
  position?: number
  stance?: 'pro' | 'con' | 'neutral'
  message_count: number
}
```

```typescript
// types/report.ts
/**
 * Report model
 */
export interface Report {
  id: string
  discussion_id: string
  overview: ReportOverview
  viewpoints_summary: ViewpointSummary[]
  consensus: Consensus
  controversies: Controversy[]
  insights: Insight[]
  recommendations: Recommendation[]
  quality_scores: QualityScores
  generation_time_ms: number
  created_at: string
}

export interface ReportOverview {
  topic: string
  participant_count: number
  duration_seconds: number
  round_count: number
  total_tokens: number
}

export interface ViewpointSummary {
  character_name: string
  character_stance: string
  main_arguments: string[]
  position_changes?: PositionChange[]
}

export interface PositionChange {
  from_phase: DiscussionPhase
  to_phase: DiscussionPhase
  old_position: string
  new_position: string
}

export interface Consensus {
  points: string[]
  supporting_arguments: Record<string, string[]>
}

export interface Controversy {
  topic: string
  disagreement_summary: string
  opposing_views: {
    character_name: string
    position: string
    arguments: string[]
  }[]
  resolution_status: 'unresolved' | 'partial' | 'resolved'
}

export interface Insight {
  category: string
  insight: string
  evidence: string[]
}

export interface Recommendation {
  priority: 'high' | 'medium' | 'low'
  recommendation: string
  rationale: string
}

export interface QualityScores {
  depth: number
  diversity: number
  constructive: number
  coherence: number
  overall: number
}
```

---

## 10. Styling Strategy

### 10.1 SCSS Architecture

```
src/assets/styles/
├── main.scss              # Entry point, import all styles
├── variables.scss         # CSS/SCSS variables
├── mixins.scss            # SCSS mixins
├── reset.scss             # Style reset
└── themes/
    ├── light.scss         # Light theme variables
    └── dark.scss          # Dark theme variables
```

```scss
// assets/styles/main.scss
// Import reset
@import './reset.scss';

// Import variables
@import './variables.scss';
@import './themes/light.scss';

// Import Element Plus
@import 'element-plus/theme-chalk/src/index.scss';

// Global styles
@import './components/*.scss';
```

```scss
// assets/styles/variables.scss
// Breakpoints
$breakpoint-xs: 480px;
$breakpoint-sm: 768px;
$breakpoint-md: 1024px;
$breakpoint-lg: 1280px;
$breakpoint-xl: 1920px;

// Spacing
$spacing-xs: 4px;
$spacing-sm: 8px;
$spacing-md: 16px;
$spacing-lg: 24px;
$spacing-xl: 32px;
$spacing-xxl: 48px;

// Border radius
$radius-sm: 4px;
$radius-md: 8px;
$radius-lg: 12px;
$radius-xl: 16px;
$radius-full: 9999px;

// Shadows
$shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
$shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
$shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
$shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);

// Transitions
$transition-fast: 150ms;
$transition-base: 250ms;
$transition-slow: 350ms;

// Z-index layers
$z-dropdown: 1000;
$z-sticky: 1020;
$z-fixed: 1030;
$z-modal-backdrop: 1040;
$z-modal: 1050;
$z-popover: 1060;
$z-tooltip: 1070;
```

```scss
// assets/styles/mixins.scss
// Responsive breakpoint mixin
@mixin respond-to($breakpoint) {
  @if $breakpoint == xs {
    @media (min-width: $breakpoint-xs) { @content; }
  }
  @else if $breakpoint == sm {
    @media (min-width: $breakpoint-sm) { @content; }
  }
  @else if $breakpoint == md {
    @media (min-width: $breakpoint-md) { @content; }
  }
  @else if $breakpoint == lg {
    @media (min-width: $breakpoint-lg) { @content; }
  }
  @else if $breakpoint == xl {
    @media (min-width: $breakpoint-xl) { @content; }
  }
}

// Flexbox centering
@mixin flex-center {
  display: flex;
  align-items: center;
  justify-content: center;
}

// Text truncation
@mixin text-truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

// Multi-line truncation
@mixin text-clamp($lines: 3) {
  display: -webkit-box;
  -webkit-line-clamp: $lines;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

// Scrollbar styling
@mixin custom-scrollbar($size: 8px, $thumb-color: #cbd5e1) {
  &::-webkit-scrollbar {
    width: $size;
    height: $size;
  }

  &::-webkit-scrollbar-track {
    background: transparent;
  }

  &::-webkit-scrollbar-thumb {
    background: $thumb-color;
    border-radius: $size;

    &:hover {
      background: darken($thumb-color, 10%);
    }
  }
}
```

### 10.2 Component Scoped Styles

```vue
<!-- components/discussion/MessageBubble.vue -->
<template>
  <div class="message-bubble" :class="classes">
    <AppAvatar :src="characterAvatar" :size="40" />
    <div class="message-content">
      <div class="message-header">
        <span class="character-name">{{ characterName }}</span>
        <span class="message-meta">
          <el-tag :type="phaseTagType" size="small">{{ phase }}</el-tag>
          <span class="round-badge">R{{ round }}</span>
        </span>
      </div>
      <p class="message-text" v-html="formattedContent"></p>
      <span class="message-time">{{ formattedTime }}</span>
    </div>
  </div>
</template>

<style scoped lang="scss">
.message-bubble {
  display: flex;
  gap: $spacing-md;
  padding: $spacing-md;
  border-radius: $radius-lg;
  transition: background-color $transition-base;

  &:hover {
    background-color: rgba(0, 0, 0, 0.02);
  }

  &.is-injected {
    background-color: rgba($color-warning, 0.1);
    border-left: 3px solid $color-warning;
  }

  &.is-streaming .message-text::after {
    content: '▋';
    animation: blink 1s infinite;
  }
}

.message-content {
  flex: 1;
  min-width: 0;
}

.message-header {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  margin-bottom: $spacing-xs;
}

.character-name {
  font-weight: 600;
  color: $text-color-primary;
}

.message-meta {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
  margin-left: auto;
  color: $text-color-secondary;
  font-size: 12px;
}

.message-text {
  color: $text-color-primary;
  line-height: 1.6;
  word-wrap: break-word;
}

.message-time {
  display: block;
  margin-top: $spacing-xs;
  font-size: 12px;
  color: $text-color-tertiary;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}
</style>
```

### 10.3 Dark Mode Support

```scss
// assets/styles/themes/dark.scss
// Override variables for dark mode
:root[data-theme='dark'] {
  --el-bg-color: #1f2937;
  --el-bg-color-page: #111827;
  --el-text-color-primary: #f9fafb;
  --el-text-color-regular: #e5e7eb;
  --el-text-color-secondary: #9ca3af;
  --el-text-color-placeholder: #6b7280;
  --el-border-color: #374151;
  --el-border-color-light: #4b5563;
  --el-border-color-lighter: #6b7280;
}
```

```typescript
// composables/useTheme.ts
import { watch } from 'vue'
import { useUiStore } from '@/stores/ui'

export function useTheme() {
  const uiStore = useUiStore()

  function toggleTheme() {
    const newTheme = uiStore.theme === 'light' ? 'dark' : 'light'
    uiStore.setTheme(newTheme)
  }

  // Initialize theme on mount
  uiStore.initializeTheme()

  // Watch for system theme changes
  watch(
    () => window.matchMedia('(prefers-color-scheme: dark)').matches,
    (isDark) => {
      if (!localStorage.getItem('theme')) {
        uiStore.setTheme(isDark ? 'dark' : 'light')
      }
    }
  )

  return {
    theme: computed(() => uiStore.theme),
    toggleTheme,
    setTheme: uiStore.setTheme
  }
}
```

---

## 11. Performance Optimization

### 11.1 Code Splitting

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // Vendor chunks
          'vendor-vue': ['vue', 'vue-router', 'pinia'],
          'vendor-ui': ['element-plus', '@element-plus/icons-vue'],
          'vendor-utils': ['axios', 'dayjs', 'lodash-es'],
          'vendor-socket': ['socket.io-client']
        }
      }
    },
    chunkSizeWarningLimit: 1000
  }
})
```

### 11.2 Virtual Scrolling for Message Lists

```vue
<!-- components/discussion/MessageList.vue -->
<template>
  <div class="message-list" ref="scrollContainer">
    <RecycleScroller
      v-if="messages.length > 0"
      :items="messages"
      :item-size="120"
      key-field="id"
      v-slot="{ item }"
    >
      <MessageBubble :message="item" />
    </RecycleScroller>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { RecycleScroller } from 'vue-virtual-scroller'
import 'vue-virtual-scroller/dist/vue-virtual-scroller.css'
import MessageBubble from './MessageBubble.vue'
import { useMessageStore } from '@/stores/message'

const props = defineProps<{
  discussionId: string
}>()

const messageStore = useMessageStore()
const messages = computed(() => messageStore.getMessages(props.discussionId))
const scrollContainer = ref<HTMLElement>()

// Auto-scroll to bottom on new messages
watch(() => messages.value.length, async () => {
  await nextTick()
  if (scrollContainer.value) {
    scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight
  }
})
</script>
```

### 11.3 Image Optimization

```typescript
// utils/image.ts
/**
 * Generate responsive image URLs
 */
export function getResponsiveImageUrl(
  baseUrl: string,
  size: 'small' | 'medium' | 'large'
): string {
  const sizeMap = {
    small: '64x64',
    medium: '200x200',
    large: '400x400'
  }
  return `${baseUrl}?size=${sizeMap[size]}`
}

/**
 * Lazy load images
 */
export function lazyLoadImage(element: HTMLImageElement, src: string) {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target as HTMLImageElement
        img.src = src
        img.classList.add('loaded')
        observer.unobserve(img)
      }
    })
  })

  observer.observe(element)
}
```

### 11.4 Debounce & Throttle Utilities

```typescript
// composables/useDebounce.ts
import { ref, watch } from 'vue'

export function useDebounce<T>(value: Ref<T>, delay: number = 300): Ref<T> {
  const debouncedValue = ref(value.value) as Ref<T>
  let timeout: number | null = null

  watch(value, (newValue) => {
    if (timeout) clearTimeout(timeout)
    timeout = window.setTimeout(() => {
      debouncedValue.value = newValue
    }, delay)
  })

  return debouncedValue
}

// Usage
const searchQuery = ref('')
const debouncedQuery = useDebounce(searchQuery, 500)

watch(debouncedQuery, (newQuery) => {
  // Perform search
})
```

```typescript
// composables/useThrottle.ts
import { ref } from 'vue'

export function useThrottle<T extends (...args: any[]) => any>(
  fn: T,
  delay: number = 300
): T {
  const lastCall = ref(0)
  const timeout = ref<number | null>(null)

  return ((...args: Parameters<T>) => {
    const now = Date.now()
    const remaining = delay - (now - lastCall.value)

    if (remaining <= 0) {
      if (timeout.value) {
        clearTimeout(timeout.value)
        timeout.value = null
      }
      lastCall.value = now
      fn(...args)
    } else if (!timeout.value) {
      timeout.value = window.setTimeout(() => {
        lastCall.value = Date.now()
        timeout.value = null
        fn(...args)
      }, remaining)
    }
  }) as T
}

// Usage
const handleScroll = useThrottle(() => {
  // Handle scroll
}, 100)
```

---

## 12. Testing Strategy

### 12.1 Unit Testing with Vitest

```typescript
// tests/unit/components/MessageBubble.spec.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import MessageBubble from '@/components/discussion/MessageBubble.vue'
import type { DiscussionMessage } from '@/types'

describe('MessageBubble', () => {
  const mockMessage: DiscussionMessage = {
    id: '1',
    discussion_id: 'disc-1',
    participant_id: 'part-1',
    character_name: 'Alice',
    character_avatar: 'https://example.com/avatar.png',
    round: 1,
    phase: 'opening',
    content: 'Hello, everyone!',
    token_count: 5,
    is_injected_question: false,
    created_at: '2026-01-12T10:00:00Z'
  }

  it('renders message content', () => {
    const wrapper = mount(MessageBubble, {
      props: { message: mockMessage }
    })

    expect(wrapper.text()).toContain('Hello, everyone!')
    expect(wrapper.text()).toContain('Alice')
  })

  it('displays phase badge', () => {
    const wrapper = mount(MessageBubble, {
      props: { message: mockMessage }
    })

    expect(wrapper.find('.phase-badge').text()).toBe('opening')
  })

  it('highlights injected questions', () => {
    const injectedMessage = { ...mockMessage, is_injected_question: true }
    const wrapper = mount(MessageBubble, {
      props: { message: injectedMessage }
    })

    expect(wrapper.classes()).toContain('is-injected')
  })

  it('emits click event', async () => {
    const wrapper = mount(MessageBubble, {
      props: { message: mockMessage }
    })

    await wrapper.trigger('click')
    expect(wrapper.emitted('click')).toBeTruthy()
  })
})
```

```typescript
// tests/unit/composables/useAuth.spec.ts
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import * as authApi from '@/services/api/auth'

// Mock API
vi.mock('@/services/api/auth', () => ({
  authApi: {
    login: vi.fn(),
    register: vi.fn(),
    getCurrentUser: vi.fn()
  }
}))

describe('useAuth', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('logs in successfully', async () => {
    const mockResponse = {
      access_token: 'token123',
      refresh_token: 'refresh123',
      token_type: 'bearer',
      expires_in: 86400
    }
    vi.mocked(authApi.authApi.login).mockResolvedValue(mockResponse)

    const authStore = useAuthStore()
    await authStore.login({
      email: 'test@example.com',
      password: 'password123'
    })

    expect(authStore.token).toBe('token123')
    expect(authApi.authApi.login).toHaveBeenCalledOnce()
  })

  it('handles login error', async () => {
    vi.mocked(authApi.authApi.login).mockRejectedValue(
      new Error('Invalid credentials')
    )

    const authStore = useAuthStore()
    await expect(
      authStore.login({
        email: 'test@example.com',
        password: 'wrong'
      })
    ).rejects.toThrow('Invalid credentials')
  })
})
```

### 12.2 E2E Testing with Playwright

```typescript
// tests/e2e/discussion.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Discussion Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Login
    await page.goto('/login')
    await page.fill('input[name="email"]', 'test@example.com')
    await page.fill('input[name="password"]', 'password123')
    await page.click('button[type="submit"]')
    await page.waitForURL('/dashboard')
  })

  test('creates a new discussion', async ({ page }) => {
    // Navigate to topic creation
    await page.click('text=New Discussion')
    await page.waitForURL('/topics/create')

    // Fill topic form
    await page.fill('input[name="title"]', 'AI Ethics Discussion')
    await page.fill('textarea[name="description"]', 'Discuss ethical implications of AI')

    // Select characters
    await page.click('text=Select Characters')
    await page.click('.character-card:first-child')
    await page.click('.character-card:nth-child(2)')
    await page.click('.character-card:nth-child(3)')

    // Create discussion
    await page.click('button:has-text("Start Discussion")')

    // Verify navigation to discussion room
    await page.waitForURL(/\/discussions\/[a-f0-9-]+/)
    await expect(page.locator('.discussion-room')).toBeVisible()
  })

  test('pauses and resumes discussion', async ({ page }) => {
    // Start discussion
    await page.goto('/discussions/test-discussion-id')
    await page.waitForSelector('.discussion-room')

    // Pause
    await page.click('button:has-text("Pause")')
    await expect(page.locator('.status-badge')).toHaveText(/paused/i)

    // Resume
    await page.click('button:has-text("Resume")')
    await expect(page.locator('.status-badge')).toHaveText(/running/i)
  })
})
```

### 12.3 Test Configuration

```typescript
// tests/setup.ts
import { vi } from 'vitest'
import { config } from '@vue/test-utils'

// Global mocks
vi.mock('vue-router', () => ({
  useRoute: () => ({ params: {}, query: {}, path: '/' }),
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    go: vi.fn(),
    back: vi.fn(),
    forward: vi.fn()
  })
}))

// Element Plus mock
config.global.stubs = {
  'el-button': true,
  'el-input': true,
  'el-form': true,
  'el-form-item': true
}
```

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'tests/',
        '**/*.d.ts',
        '**/*.config.*',
        '**/mockData.ts'
      ]
    }
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})
```

---

## Appendix: Package.json Scripts

```json
{
  "name": "simfocus-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc && vite build",
    "preview": "vite preview",
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:e2e": "playwright test",
    "lint": "eslint . --ext .vue,.js,.jsx,.cjs,.mjs,.ts,.tsx,.cts,.mts --fix",
    "format": "prettier --write src/"
  },
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.2.0",
    "pinia": "^2.1.0",
    "pinia-plugin-persistedstate": "^3.2.0",
    "element-plus": "^2.5.0",
    "@element-plus/icons-vue": "^2.3.0",
    "axios": "^1.6.0",
    "socket.io-client": "^4.6.0",
    "dayjs": "^1.11.0",
    "lodash-es": "^4.17.0",
    "echarts": "^5.4.0",
    "vue-virtual-scroller": "^2.0.0-beta.8"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "@vue/test-utils": "^2.4.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0",
    "vue-tsc": "^1.8.0",
    "vitest": "^1.1.0",
    "playwright": "^1.40.0",
    "eslint": "^8.55.0",
    "prettier": "^3.1.0",
    "unplugin-auto-import": "^0.17.0",
    "unplugin-vue-components": "^0.26.0",
    "@types/lodash-es": "^4.17.0",
    "@types/node": "^20.0.0",
    "sass": "^1.69.0"
  }
}
```

---

## Summary

This frontend design document provides:

1. **UI Library Recommendation**: Element Plus with detailed justification
2. **Complete Project Structure**: Organized by feature with clear naming conventions
3. **Component Architecture**: Smart/presentational pattern with reusable components
4. **State Management**: Pinia stores for auth, discussion, messages, UI
5. **Routing**: Vue Router 4 with lazy loading and navigation guards
6. **API Integration**: Axios with interceptors, error handling, retry logic
7. **WebSocket**: Socket.IO with event handlers and reconnection strategy
8. **TypeScript Types**: Complete type definitions for all domain models
9. **Styling**: SCSS with CSS variables, dark mode support, responsive design
10. **Performance**: Code splitting, virtual scrolling, debouncing, image optimization
11. **Testing**: Vitest for unit tests, Playwright for E2E

### Implementation Priority

1. **Week 1**: Setup project, Element Plus, routing, auth flow
2. **Week 2**: Dashboard, topic management, character selection
3. **Week 3**: Discussion room, WebSocket integration, message streaming
4. **Week 4**: Report view, visualizations, export functionality
5. **Week 5**: Polish, testing, performance optimization

---

**Document Status**: Ready for Implementation
**Maintainer**: Frontend Architect
**Last Updated**: 2026-01-12
