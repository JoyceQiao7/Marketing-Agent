# Mulan Marketing Agent - Frontend Dashboard

Next.js dashboard for monitoring and managing the Mulan Marketing Agent system.

## Features

- 📊 Real-time analytics dashboard
- 📝 Browse and filter questions
- 🚀 Manual crawl triggers
- 📈 Performance metrics
- 🎨 Modern UI with Tailwind CSS

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and set NEXT_PUBLIC_API_URL to your backend API
```

### 3. Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## Production Build

```bash
npm run build
npm start
```

## Docker Deployment

```bash
docker build -t mulan-frontend .
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=https://your-api.com mulan-frontend
```

## Project Structure

```
frontend/
├── src/
│   ├── components/      # Reusable React components
│   ├── pages/           # Next.js pages (routes)
│   ├── hooks/           # Custom React hooks
│   ├── lib/             # Utilities and API client
│   └── styles/          # Global styles
├── public/              # Static assets
└── package.json
```

## Pages

- **/** - Dashboard with analytics and quick actions
- **/questions** - Browse and filter all questions

## Tech Stack

- **Framework**: Next.js 14
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **API Client**: Axios
- **Deployment**: Docker / Vercel

## Environment Variables

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000  # Backend API URL
```

