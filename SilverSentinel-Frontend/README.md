# 🌐 SilverSentinel Frontend

**Modern Next.js Web Application for AI-Driven Silver Market Trading**

> Beautiful, responsive React dashboard providing real-time market intelligence, trading signals, and computer vision analysis for silver investments.

[![Next.js](https://img.shields.io/badge/Next.js-15.1.0-000000?style=flat&logo=next.js)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-19.0.0-61DAFB?style=flat&logo=react)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-007ACC?style=flat&logo=typescript)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind%20CSS-3.4.1-38B2AC?style=flat&logo=tailwind-css)](https://tailwindcss.com/)

---

## ✨ Features

### 🏠 **Landing Page**
- Modern hero section with animated elements
- Feature showcase with interactive demos
- Integration logos and testimonials
- FAQ section and call-to-action

### 📊 **Dashboard Pages**
- **Dashboard**: Real-time trading signals and market overview
- **Narratives**: Market story discovery and lifecycle tracking  
- **Analytics**: Historical performance and trend analysis
- **Scanner**: Computer vision for physical silver analysis
- **Signals**: Trading recommendations with confidence scores
- **Settings**: User preferences and API configuration

### 🔐 **Authentication**
- JWT-based user authentication
- Sign up / Sign in pages
- Protected routes and contexts
- Persistent login sessions

### 🎨 **UI/UX Features**
- **Responsive Design**: Mobile-first approach
- **Smooth Animations**: Framer Motion + GSAP
- **Dark/Light Themes**: Automatic theme switching
- **Real-time Updates**: WebSocket integration
- **Error Boundaries**: Graceful error handling
- **Toast Notifications**: User feedback system

---

## 🚀 Quick Start

### Prerequisites
- **Node.js 18+**
- **npm/yarn/pnpm/bun**
- **SilverSentinel Backend** running on port 8000

### Installation & Development

```bash
# Navigate to frontend directory
cd SilverSentinel-Frontend

# Install dependencies
npm install
# or
yarn install

# Start development server
npm run dev
# or
yarn dev

# Open browser
# http://localhost:3000
```

### Production Build

```bash
# Build for production
npm run build

# Start production server
npm run start

# Lint code
npm run lint
```

---

## 🏗️ Architecture

### Tech Stack
- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript for type safety
- **Styling**: Tailwind CSS + Custom components
- **Animations**: Framer Motion + GSAP
- **State Management**: React Context + Hooks
- **Authentication**: JWT tokens + Context API
- **API Integration**: Fetch API with proxy configuration

### Project Structure

```
src/
├─ 📄 app/                     # App Router Pages
│  ├─ layout.tsx              # Root layout
│  ├─ page.tsx                # Landing page
│  ├─ dashboard/              # Trading dashboard
│  ├─ narratives/             # Market narratives
│  ├─ analytics/              # Performance analytics
│  ├─ scanner/                # Computer vision
│  ├─ signals/                # Trading signals
│  ├─ settings/               # User settings
│  ├─ signin/                 # Authentication
│  └─ signup/                 # User registration
│
├─ 🎨 components/              # Reusable Components
│  ├─ AppNavbar.tsx           # Navigation bar
│  ├─ Button.tsx              # Custom buttons
│  ├─ ErrorBoundary.tsx       # Error handling
│  ├─ Toast.tsx               # Notifications
│  └─ MagicBento.tsx          # Feature showcase
│
├─ 📑 sections/                # Landing Page Sections
│  ├─ Hero.tsx                # Hero section
│  ├─ Features.tsx            # Feature showcase
│  ├─ Dashboard.tsx           # Demo dashboard
│  ├─ Integrations.tsx        # Partner logos
│  └─ Footer.tsx              # Site footer
│
├─ 🔐 context/                 # React Contexts
│  └─ AuthContext.tsx         # Authentication
│
└─ 🎨 assets/                  # Static Assets
   ├─ images/                 # Images and icons
   └─ fonts/                  # Custom fonts
```

---

## 🔧 Configuration

### Environment Variables

```bash
# .env.local (create this file)
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

### API Proxy Configuration

The frontend automatically proxies API calls to the backend via `next.config.mjs`:

```javascript
async rewrites() {
  return [
    {
      source: '/api/:path*',
      destination: 'http://127.0.0.1:8000/api/:path*',
    },
  ]
}
```

### Tailwind Configuration

Custom theme configuration in `tailwind.config.ts` includes:
- Brand colors and gradients
- Custom animations and transitions
- Responsive breakpoints
- Component utilities

---

## 🎯 Key Components

### Authentication Context
```typescript
// Usage in components
const { user, login, logout, loading } = useAuth();
```

### WebSocket Integration
```typescript
// Real-time price updates
useEffect(() => {
  const ws = new WebSocket('ws://localhost:8000/ws/live');
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    // Update UI with live data
  };
}, []);
```

### Error Boundaries
```typescript
// Graceful error handling
<ErrorBoundary fallback={<ErrorFallback />}>
  <YourComponent />
</ErrorBoundary>
```

---

## 🎨 Styling Guide

### Design System
- **Primary Colors**: Blue gradients (#3B82F6 to #1D4ED8)
- **Accent Colors**: Purple/pink gradients for highlights
- **Typography**: Inter font family with weight variants
- **Spacing**: Consistent 4px grid system
- **Shadows**: Subtle depth with multiple shadow layers

### Animation Principles
- **Micro-interactions**: Hover states and button animations
- **Page Transitions**: Smooth enter/exit animations
- **Loading States**: Skeleton screens and spinners
- **Real-time Updates**: Subtle pulse effects for live data

---

## 📱 Responsive Design

### Breakpoints
- **Mobile**: 320px - 768px
- **Tablet**: 768px - 1024px  
- **Desktop**: 1024px+
- **Large Screens**: 1440px+

### Mobile Optimizations
- Touch-friendly button sizes (44px minimum)
- Simplified navigation with hamburger menu
- Optimized images with next/image
- Reduced motion for accessibility

---

## 🧪 Testing & Quality

### Development Tools
```bash
# Type checking
npx tsc --noEmit

# Linting
npm run lint

# Format code
npx prettier --write .

# Bundle analysis
npx @next/bundle-analyzer
```

### Performance Optimizations
- **Image Optimization**: next/image with WebP support
- **Code Splitting**: Automatic route-based splitting
- **Tree Shaking**: Unused code elimination
- **Caching**: Static generation and ISR where applicable

---

## 🚀 Deployment

### Vercel (Recommended)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy to Vercel
vercel

# Set environment variables in Vercel dashboard
NEXT_PUBLIC_API_URL=https://your-backend-url.com
```

### Docker Deployment
```dockerfile
# Dockerfile included for containerized deployment
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

---

## 📊 Performance Metrics

- **🚀 Lighthouse Score**: 90+ (Performance, Accessibility, SEO)
- **📱 First Contentful Paint**: <2s
- **🎨 Largest Contentful Paint**: <3s
- **⚡ Time to Interactive**: <3s
- **📦 Bundle Size**: <500KB gzipped

---

## 🔗 Integration with Backend

### API Endpoints Used
- `GET /api/narratives` - Fetch market narratives
- `GET /api/trading-signal` - Get current trading signal
- `POST /api/auth/login` - User authentication  
- `POST /api/scan` - Computer vision analysis
- `WebSocket /ws/live` - Real-time updates

### Data Flow
1. **Authentication**: JWT tokens stored in httpOnly cookies
2. **API Calls**: Automatic token inclusion in requests
3. **Real-time Data**: WebSocket connection for live updates
4. **Error Handling**: Graceful fallbacks and user notifications

---

## 📚 Learn More

### Next.js Resources
- [Next.js Documentation](https://nextjs.org/docs) - Framework features and API
- [Learn Next.js](https://nextjs.org/learn) - Interactive tutorial
- [Next.js Examples](https://github.com/vercel/next.js/tree/canary/examples)

### Component Libraries Used
- [Framer Motion](https://www.framer.com/motion/) - Animations
- [Recharts](https://recharts.org/) - Chart components
- [Tailwind UI](https://tailwindui.com/) - Design inspiration

---

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Code Standards
- **TypeScript**: Strict mode enabled
- **ESLint**: Airbnb configuration
- **Prettier**: Automatic code formatting
- **Husky**: Pre-commit hooks for quality

---

**🏆 Built for NMIMS Echelon 2.0 Hackathon**

*Modern React application showcasing the future of financial AI interfaces*
