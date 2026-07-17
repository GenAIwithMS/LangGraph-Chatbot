<div align="center">

<img src="public/logo.png" alt="RaketH Logo" width="120" />

# RaketH Clone

**AI-Powered Voice Cloning & Text-to-Speech Platform**

[![Next.js](https://img.shields.io/badge/Next.js-16-black?logo=next.js)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue?logo=typescript)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-4-38bdf8?logo=tailwindcss)](https://tailwindcss.com/)
[![Prisma](https://img.shields.io/badge/Prisma-6-2D3748?logo=prisma)](https://prisma.io/)
[![License](https://img.shields.io/badge/License-All%20Rights%20Reserved-red)]()

[Features](#features) • [Screenshots](#screenshots) • [Quick Start](#quick-start) • [API Docs](#api-documentation)

</div>

---

## Overview

RaketH Clone is a production-ready **AI voice cloning and text-to-speech platform**. It features a stunning glassmorphism UI, real-time credit-based billing, multi-language translation & TTS, voice cloning capabilities, and a powerful admin dashboard — all wrapped in a seamless user experience.

This repository contains the **Next.js frontend & API** (this repo). The heavy-lifting neural TTS engine lives in a separate backend service:

**TTS Backend (GPU required)** → [`yaseerabas/tts-with-translation-api`](https://github.com/yaseerabas/tts-with-translation-api)

- Neural TTS model (GPU-accelerated)
- Voice cloning & training endpoints
- Translation + TTS streaming pipeline

**Use case:** Rent a GPU → Host the backend → Connect this frontend → Launch your own TTS SaaS with custom pricing.

---

## Features

### Core Platform
- **Voice Cloning** — Upload voice samples to create personalized AI voice clones
- **Text-to-Speech (TTS)** — Convert text to natural-sounding speech with streaming audio
- **Translate & TTS** — Translate text across 11+ languages, then synthesize speech
- **Credit-Based Billing** — One-time purchases, credits never expire
- **WhatsApp Integration** — Direct subscription management and support
- **Multi-Language Support** — English, Spanish, French, German, Chinese, Japanese, Arabic, Hindi, and more

### Admin Dashboard
- **Real-Time Analytics** — Track users, subscriptions, credits, and revenue
- **User Management** — Search, filter, and manage all platform users
- **Subscription Control** — Assign plans and monitor usage with visual progress bars
- **Direct Communication** — One-click WhatsApp links with pre-filled context

### Design & UX
- **Glassmorphism UI** — Frosted glass effects with backdrop blur and gradients
- **Smooth Animations** — Floating elements, shimmer effects, and micro-interactions
- **Fully Responsive** — Optimized for mobile, tablet, and desktop
- **Dark Mode Ready** — Built with next-themes for seamless theme switching

---

## Screenshots

<div align="center">

| Landing Page | Dashboard | Generate |
|:---:|:---:|:---:|
| <img src="public/images/hero-section.png" width="280" /> | <img src="public/images/user-dashboard.png" width="280" /> | <img src="public/images/generate-voice.png" width="280" /> |

| Voice Clones | Admin Panel | Pricing |
|:---:|:---:|:---:|
| <img src="public/images/voice-clone.png" width="280" /> | <img src="public/images/admin-dashboard.png" width="280" /> | <img src="public/images/pricing.png" width="280" /> |

</div>

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Framework** | Next.js 16 (App Router + Turbopack) |
| **Language** | TypeScript 5 |
| **Styling** | Tailwind CSS 4 + OKLCH color system |
| **UI Components** | shadcn/ui + Radix UI primitives |
| **Animations** | Framer Motion + CSS keyframes |
| **Auth** | NextAuth.js v4 (Credentials) |
| **Database** | Prisma ORM (MySQL / SQLite) |
| **State** | Zustand + TanStack Query |
| **Forms** | React Hook Form + Zod |
| **Charts** | Recharts |
| **Icons** | Lucide React |

---

## Quick Start

### Prerequisites
- Node.js 18+ or Bun
- MySQL database (or SQLite for dev)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd raketh-fullstack-app

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with your database and auth secrets

# Setup database
npx prisma generate
npx prisma db push
npx prisma db seed

# Start development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

### Default Admin
- **Email:** `admin@rakethclone.com`
- **Password:** `admin123`

> Change the admin password immediately in production!

---

## Pricing

This is a **SaaS-ready platform**. You bring your own pricing.

- Set custom subscription plans via the admin dashboard
- Sell credits as one-time purchases or recurring subscriptions
- Define your own tiers, limits, and feature gates

Perfect for launching your own **TTS-as-a-Service** or **AI Voice API** business.

> **GPU Required:** The neural TTS backend needs a GPU. Rent one on [RunPod](https://www.runpod.io/), [Vast.ai](https://vast.ai/), or any cloud GPU provider, then connect this frontend to your hosted API.

---

## API Documentation

### Authentication
All API routes (except auth) require a valid session via NextAuth.

### Public Endpoints

**Generate Speech**
```http
POST /api/generate
Content-Type: application/json

{
  "text": "Hello world",
  "voiceId": "default_male_01",
  "type": "tts",
  "language": "en"
}
```

**Get User Data**
```http
GET /api/user
```

**List Voices**
```http
GET /api/voice-clones
```

**Upload Voice Clone**
```http
POST /api/voice-clones/upload
Content-Type: multipart/form-data

user_id=custom_eva_123&name=My Voice&voice_file=@audio.wav
```

**Generation History**
```http
GET /api/generations?page=1&limit=10
```

### Admin Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/admin/stats` | Platform-wide statistics |
| `GET /api/admin/users` | List all users |
| `GET /api/admin/plans` | List subscription plans |
| `POST /api/admin/subscribe` | Assign plan to user |

See [`EXTERNAL_API_DOCUMENTATION.md`](EXTERNAL_API_DOCUMENTATION.md) for the full TTS service integration spec, or visit the backend repo: [`yaseerabas/tts-with-translation-api`](https://github.com/yaseerabas/tts-with-translation-api).

---

## Project Structure

```
raketh-fullstack-app/
├── src/
│   ├── app/              # Next.js App Router
│   │   ├── api/          # API routes
│   │   ├── (routes)/     # Page routes
│   │   └── layout.tsx    # Root layout
│   ├── components/
│   │   ├── ui/           # shadcn/ui components
│   │   └── ...           # Custom components
│   ├── lib/              # Utilities, auth, DB
│   ├── hooks/            # Custom React hooks
│   └── types/            # TypeScript definitions
├── prisma/
│   ├── schema.prisma     # Database schema
│   └── seed.ts           # Seed script
├── public/               # Static assets
└── storage/audio/        # Generated audio files
```

---

## Environment Variables

```env
# Database
DATABASE_URL="mysql://user:password@localhost:3306/raketh_clone"

# Authentication
NEXTAUTH_SECRET="your-super-secret-key"
NEXTAUTH_URL="http://localhost:3000"

# External TTS Backend (GPU required)
# Backend repo: https://github.com/yaseerabas/tts-with-translation-api
EXTERNAL_TTS_API_URL="http://localhost:8000"
```

---

## Scripts

```bash
npm run dev          # Start dev server (Turbopack)
npm run build        # Production build
npm start            # Start production server
npm run lint         # Run ESLint

# Database
npx prisma db push   # Push schema changes
npx prisma db seed   # Seed admin & plans
npx prisma studio    # Open Prisma Studio
```

---

## Deployment Checklist

- [ ] Change default admin password
- [ ] Set secure `NEXTAUTH_SECRET`
- [ ] Configure production database
- [ ] Set `NODE_ENV=production`
- [ ] Configure external TTS API URL
- [ ] Enable HTTPS/SSL
- [ ] Test WhatsApp integration
- [ ] Verify payment workflow

---

## License

**Copyright &copy; 2026 RaketH Clone. All Rights Reserved.**

This is proprietary software. Unauthorized copying, modification, distribution, or use is strictly prohibited.

---

<div align="center">

**Built with Next.js, TypeScript, and Tailwind CSS**

[Report Issue](https://github.com/yaseerabas/raketh-fullstack-app/issues) &middot; [Request Feature](https://github.com/yaseerabas/raketh-fullstack-app/issues)

</div>
