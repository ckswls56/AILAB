# Next.js 15 공식 문서 활용 가이드

## 🚀 Next.js 15 설치 및 프로젝트 생성

### 1. Node.js 버전 확인
```bash
node --version
# Node.js 18.17 이상 필요
```

### 2. Next.js 15 프로젝트 생성
```bash
# create-next-app으로 새 프로젝트 생성
npx create-next-app@latest my-nextjs15-app --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"

# 또는 기존 프로젝트에 Next.js 15 설치
npm install next@15 react@18 react-dom@18
```

### 3. package.json 설정
```json
{
  "name": "my-nextjs15-app",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "15.0.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "typescript": "^5.0.0",
    "tailwindcss": "^3.3.0",
    "eslint": "^8.0.0",
    "eslint-config-next": "15.0.0"
  }
}
```

## 📁 프로젝트 구조

```
my-nextjs15-app/
├── app/                    # App Router (Next.js 13+)
│   ├── layout.tsx         # 루트 레이아웃
│   ├── page.tsx           # 홈페이지
│   ├── globals.css        # 전역 스타일
│   └── (routes)/          # 라우트 그룹
├── components/            # 재사용 가능한 컴포넌트
├── lib/                   # 유틸리티 함수
├── public/                # 정적 파일
├── next.config.js         # Next.js 설정
├── tailwind.config.js     # Tailwind CSS 설정
├── tsconfig.json          # TypeScript 설정
└── package.json
```

## 🎯 Next.js 15 주요 기능

### 1. App Router (기본)
```typescript
// app/page.tsx
export default function HomePage() {
  return (
    <main>
      <h1>Next.js 15 홈페이지</h1>
    </main>
  )
}
```

### 2. Server Components (기본)
```typescript
// app/users/page.tsx
async function getUsers() {
  const res = await fetch('https://api.example.com/users')
  return res.json()
}

export default async function UsersPage() {
  const users = await getUsers()
  
  return (
    <div>
      {users.map(user => (
        <div key={user.id}>{user.name}</div>
      ))}
    </div>
  )
}
```

### 3. Client Components
```typescript
'use client'

import { useState } from 'react'

export default function Counter() {
  const [count, setCount] = useState(0)
  
  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>
        증가
      </button>
    </div>
  )
}
```

### 4. API Routes
```typescript
// app/api/users/route.ts
import { NextRequest, NextResponse } from 'next/server'

export async function GET() {
  return NextResponse.json({ users: [] })
}

export async function POST(request: NextRequest) {
  const body = await request.json()
  return NextResponse.json({ message: '사용자 생성됨' })
}
```

## 🎨 스타일링

### 1. Tailwind CSS (권장)
```typescript
// app/page.tsx
export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">
          Next.js 15 프로젝트
        </h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* 카드 컴포넌트들 */}
        </div>
      </div>
    </div>
  )
}
```

### 2. CSS Modules
```css
/* app/components/Card.module.css */
.card {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.title {
  font-size: 1.5rem;
  font-weight: bold;
  color: #333;
}
```

```typescript
// app/components/Card.tsx
import styles from './Card.module.css'

export default function Card({ title, children }: { title: string, children: React.ReactNode }) {
  return (
    <div className={styles.card}>
      <h2 className={styles.title}>{title}</h2>
      {children}
    </div>
  )
}
```

## 🔧 설정 파일

### 1. next.config.js
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    // 실험적 기능 활성화
  },
  images: {
    domains: ['example.com'], // 외부 이미지 도메인 허용
  },
  env: {
    // 환경 변수
    CUSTOM_KEY: process.env.CUSTOM_KEY,
  },
}

module.exports = nextConfig
```

### 2. tailwind.config.js
```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#3B82F6',
        secondary: '#10B981',
      },
    },
  },
  plugins: [],
}
```

## 🚀 배포

### 1. Vercel (권장)
```bash
# Vercel CLI 설치
npm i -g vercel

# 배포
vercel
```

### 2. Docker
```dockerfile
# Dockerfile
FROM node:18-alpine AS base

# 의존성 설치
FROM base AS deps
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci

# 빌드
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# 실행
FROM base AS runner
WORKDIR /app
ENV NODE_ENV production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["node", "server.js"]
```

## 📚 학습 리소스

### 공식 문서
- [Next.js 15 공식 문서](https://nextjs.org/docs)
- [App Router 가이드](https://nextjs.org/docs/app)
- [API Routes](https://nextjs.org/docs/app/building-your-application/routing/route-handlers)

### 실습 프로젝트 아이디어
1. **블로그 시스템**: MDX 지원, 댓글 시스템
2. **E-commerce**: 상품 카탈로그, 장바구니, 결제
3. **대시보드**: 차트, 데이터 시각화
4. **포트폴리오**: 개인 프로젝트 소개
5. **AI 챗봇**: OpenAI API 연동

## 🔍 성능 최적화

### 1. 이미지 최적화
```typescript
import Image from 'next/image'

export default function OptimizedImage() {
  return (
    <Image
      src="/hero.jpg"
      alt="Hero image"
      width={1200}
      height={600}
      priority
      className="rounded-lg"
    />
  )
}
```

### 2. 동적 임포트
```typescript
import dynamic from 'next/dynamic'

const DynamicComponent = dynamic(() => import('./HeavyComponent'), {
  loading: () => <p>로딩 중...</p>,
  ssr: false
})
```

### 3. 메타데이터
```typescript
// app/layout.tsx
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Next.js 15 앱',
  description: 'Next.js 15로 만든 웹 애플리케이션',
}
```

## 🛠️ 개발 도구

### 1. ESLint 설정
```json
// .eslintrc.json
{
  "extends": ["next/core-web-vitals"]
}
```

### 2. TypeScript 설정
```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "es6"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

이제 Next.js 15를 활용하여 현대적인 웹 애플리케이션을 개발할 수 있습니다! 