# Frontend — SG Ask Me Chat UI

Next.js React frontend for the AI chat application.

## Setup

```bash
cd frontend
npm install
```

## Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Configuration

The frontend connects to the backend at `http://localhost:8000` by default. To change this:

1. Create `.env.local`:
   ```bash
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

2. Update `app/page.tsx` to use `process.env.NEXT_PUBLIC_API_URL` instead of hardcoded URL.

## Features

- **Real-time streaming**: Receives and displays streaming responses from the backend
- **Chat interface**: Clean, modern UI with message bubbles
- **Dark mode**: Automatic dark mode support
- **Responsive**: Works on desktop and mobile

## Project Structure

```
frontend/
├── app/
│   ├── components/
│   │   ├── ChatMessage.tsx    # Message bubble component
│   │   └── ChatInput.tsx      # Input field component
│   ├── globals.css            # Global styles with Tailwind
│   ├── layout.tsx             # Root layout
│   └── page.tsx               # Main chat page
├── package.json
├── tsconfig.json
└── tailwind.config.ts
```
