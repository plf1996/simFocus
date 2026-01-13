# Frontend Quick Start Guide

## Prerequisites

Ensure you have the following installed:
- Node.js 18+ ([Download](https://nodejs.org/))
- npm 9+ (comes with Node.js)

Verify versions:
```bash
node --version  # Should be v18+
npm --version   # Should be v9+
```

## Installation

1. **Navigate to frontend directory**:
   ```bash
   cd /root/projects/simFocus/frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

   This will install all production and development dependencies (about 150 packages).

## Configuration

3. **Create environment file**:
   ```bash
   cp .env.example .env
   ```

4. **Edit `.env` with your settings**:
   ```bash
   # Application
   VITE_APP_TITLE=simFocus
   VITE_APP_DESC=AI Virtual Focus Group Platform

   # API Base URL (update if backend is on different port)
   VITE_API_BASE_URL=http://localhost:8000/api/v1

   # WebSocket Base URL
   VITE_WS_BASE_URL=ws://localhost:8000

   # Environment
   VITE_ENV=development
   ```

## Development

5. **Start development server**:
   ```bash
   npm run dev
   ```

   The application will be available at:
   - **Local**: http://localhost:5173
   - **Network**: http://192.168.x.x:5173 (check terminal)

6. **Open in browser**:
   Navigate to http://localhost:5173

You should see:
- Home page with "HomeView" title
- No errors in browser console
- Vue DevTools extension shows "vue-router" and "pinia"

## Development Tools

### Code Quality

**Lint code**:
```bash
npm run lint
```

**Format code**:
```bash
npm run format
```

### Testing

**Run unit tests** (Vitest):
```bash
npm run test
```

**Run tests with UI**:
```bash
npm run test:ui
```

**Run E2E tests** (Playwright):
```bash
npm run test:e2e
```

### Build

**Build for production**:
```bash
npm run build
```

Output will be in `frontend/dist/` directory.

**Preview production build**:
```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/      # Vue components (to be implemented)
│   ├── composables/     # Reusable composition functions
│   ├── router/          # Route definitions
│   ├── services/        # API client
│   ├── socket/          # WebSocket client
│   ├── stores/          # Pinia state stores
│   ├── types/           # TypeScript types
│   ├── utils/           # Utility functions
│   ├── views/           # Page components (placeholders ready)
│   ├── App.vue          # Root component
│   └── main.ts          # Entry point
├── public/              # Static assets
└── [config files]      # Vite, TypeScript, ESLint
```

## Key Files to Know

### Configuration
- `vite.config.ts` - Vite build configuration
- `tsconfig.json` - TypeScript settings
- `.env` - Environment variables

### Entry Points
- `index.html` - HTML template
- `src/main.ts` - Application bootstrap
- `src/App.vue` - Root component

### Core Modules
- `src/router/routes.ts` - All route definitions
- `src/stores/` - State management (auth, ui, discussion, message)
- `src/services/api.ts` - Axios HTTP client
- `src/socket/client.ts` - WebSocket client

### Types
- `shared/types/` - Types shared with backend
- `src/types/` - Frontend-specific types

## What's Implemented

✅ **Foundation** (100% complete):
- Project structure with all directories
- TypeScript configuration (strict mode)
- Vite build setup with auto-imports
- Pinia stores (auth, ui, discussion, message)
- Vue Router with navigation guards
- Socket.IO client with reconnection
- Axios service with interceptors
- Utility functions (format, validate, storage, etc.)
- Global SCSS styles with variables
- 15 placeholder view components

⏳ **Components** (next phase):
- Common components (AppButton, AppInput, etc.)
- Layout components (AppHeader, AppSidebar, etc.)
- Feature components (character, discussion, report, etc.)
- View components with full functionality

## Development Workflow

1. **Create a new component**:
   ```bash
   # Component file
   touch src/components/common/MyComponent.vue

   # Or use a component generator (optional)
   ```

2. **Import auto-imported APIs**:
   ```vue
   <script setup lang="ts">
   import { ref, computed, onMounted } from 'vue'  // Auto-imported
   import { useRouter } from 'vue-router'          // Auto-imported
   import { useAuthStore } from '@/stores'         // Auto-imported

   // No import needed for Element Plus components
   </script>
   ```

3. **Use TypeScript types**:
   ```ts
   import type { User, Discussion } from '@/types'

   const user = ref<User | null>(null)
   const discussions = ref<Discussion[]>([])
   ```

4. **Use Pinia stores**:
   ```ts
   import { useAuthStore, useUiStore } from '@/stores'

   const authStore = useAuthStore()
   const uiStore = useUiStore()

   // Call actions
   await authStore.login({ email, password })
   uiStore.showNotification({ type: 'success', message: 'Logged in!' })
   ```

5. **Make API calls**:
   ```ts
   import api from '@/services/api'

   const users = await api.get('/users')
   const user = await api.post('/users', { name: 'John' })
   ```

6. **Use WebSocket**:
   ```ts
   import { setupDiscussionHandlers, sendControlCommand } from '@/socket'

   // Setup handlers
   const cleanup = setupDiscussionHandlers(discussionId)

   // Send commands
   sendControlCommand('pause')

   // Cleanup on unmount
   onUnmounted(() => cleanup())
   ```

## Hot Reload

Vite provides instant hot module replacement (HMR):
- Edit any `.vue` or `.ts` file
- Changes appear in browser instantly
- State is preserved during HMR

## Browser DevTools

Install these extensions for better development:

1. **Vue DevTools**:
   - Chrome: [Vue.js devtools](https://chrome.google.com/webstore)
   - Firefox: [Vue.js devtools](https://addons.mozilla.org/firefox/)

2. **Pinia DevTools** (built into Vue DevTools):
   - Inspect Pinia stores
   - Time-travel debugging
   - State mutations tracking

## Troubleshooting

### Port already in use
```bash
# Kill process on port 5173
npx kill-port 5173

# Or use different port
npm run dev -- --port 3000
```

### Module not found
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### TypeScript errors
```bash
# Restart TypeScript server in VS Code
# Cmd/Ctrl + Shift + P -> "TypeScript: Restart TS Server"
```

### Vite cache issues
```bash
# Clear Vite cache
rm -rf node_modules/.vite
npm run dev
```

## Next Steps

1. **Explore the codebase**:
   - Read `frontend/README.md` for detailed documentation
   - Check `docs/frontend_design.md` for architecture decisions

2. **Start implementing components**:
   - Begin with common components in `src/components/common/`
   - Follow the component design patterns in the design doc

3. **Connect to backend**:
   - Ensure backend is running on port 8000
   - Test API endpoints with the configured Axios client
   - Verify WebSocket connection for real-time features

4. **Run tests**:
   - Add unit tests for components and composables
   - Add E2E tests for critical user flows

## Resources

- [Vue 3 Documentation](https://vuejs.org/)
- [Vite Guide](https://vitejs.dev/guide/)
- [Pinia Documentation](https://pinia.vuejs.org/)
- [Element Plus Components](https://element-plus.org/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Socket.IO Client](https://socket.io/docs/v4/client-api/)

## Support

For questions or issues:
1. Check the documentation in `docs/`
2. Review the design document `docs/frontend_design.md`
3. See the project `CLAUDE.md` for context

Happy coding! 🚀
