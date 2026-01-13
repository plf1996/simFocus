# simFocus Frontend

AI Virtual Focus Group Platform - Frontend Application

## Tech Stack

- **Framework**: Vue 3 with Composition API and `<script setup>`
- **Language**: TypeScript 5.3+
- **Build Tool**: Vite 5
- **UI Library**: Element Plus 2.5
- **State Management**: Pinia with persistence
- **Routing**: Vue Router 4
- **HTTP Client**: Axios
- **WebSocket**: Socket.IO Client
- **Date/Time**: Day.js
- **Charts**: Apache ECharts
- **Virtual Scrolling**: vue-virtual-scroller

## Project Structure

```
frontend/
├── src/
│   ├── assets/          # Static assets (styles, images)
│   ├── components/      # Vue components
│   ├── composables/     # Reusable composables
│   ├── router/          # Vue Router configuration
│   ├── services/        # API service layer
│   ├── socket/          # WebSocket client
│   ├── stores/          # Pinia stores
│   ├── types/           # TypeScript type definitions
│   ├── utils/           # Utility functions
│   ├── views/           # Page-level components
│   ├── App.vue          # Root component
│   └── main.ts          # Application entry point
├── public/              # Public assets
├── package.json
├── vite.config.ts
├── tsconfig.json
└── .env.example         # Environment variables template
```

## Getting Started

### Prerequisites

- Node.js 18+
- npm 9+

### Installation

```bash
# Install dependencies
npm install
```

### Development

```bash
# Copy environment variables
cp .env.example .env

# Start development server
npm run dev
```

The application will be available at `http://localhost:5173`

### Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

### Testing

```bash
# Run unit tests
npm run test

# Run tests with UI
npm run test:ui

# Run E2E tests
npm run test:e2e
```

### Code Quality

```bash
# Lint code
npm run lint

# Format code
npm run format
```

## Configuration

### Environment Variables

See `.env.example` for available environment variables:

- `VITE_API_BASE_URL` - Backend API base URL
- `VITE_WS_BASE_URL` - WebSocket server URL
- `VITE_APP_TITLE` - Application title
- `VITE_ENV` - Environment (development/production)

### Vite Configuration

- Auto-imports for Vue, Vue Router, and Pinia APIs
- Auto-imports for Element Plus components
- SCSS global variables and mixins
- Code splitting for optimal bundle size
- Proxy configuration for API and WebSocket

## Type Safety

This project uses TypeScript with strict mode enabled:

- Shared types in `/shared/types/` for frontend/backend compatibility
- Component props and events fully typed
- API request/response types defined
- Full type coverage for stores and services

## State Management

Pinia stores with persistence:

- `auth` - User authentication state
- `ui` - Global UI state (loading, notifications, theme)
- `discussion` - Active discussion state
- `message` - Message cache for real-time updates

## WebSocket Integration

Socket.IO client for real-time discussion updates:

- Automatic reconnection with exponential backoff
- Event handlers for messages, status updates, typing indicators
- Control commands (pause, resume, speed, inject questions)
- Heartbeat for connection health monitoring

## Performance Optimizations

- Code splitting by vendor (Vue, UI, utils, socket, charts)
- Lazy loading for route components
- Virtual scrolling for large message lists
- Debounced inputs and throttled events
- Image optimization and lazy loading
- Tree-shaking for minimal bundle size

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## License

Proprietary - All rights reserved
