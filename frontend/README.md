# Frontend — SG Ask Me Chat UI

Next.js React frontend for the AI chat application.

## Setup

**Using Makefile (recommended):**
```bash
cd frontend
make install
```

**Or using npm directly:**
```bash
cd frontend
npm install
```

## Development

**Using Makefile:**
```bash
make dev
```

**Or using npm:**
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Available shortcuts (Makefile)

- `make install` - Install dependencies (`npm install`)
- `make dev` - Run development server (`npm run dev`)
- `make build` - Build for production (`npm run build`)
- `make start` - Start production server (`npm start`)
- `make lint` - Run linter (`npm run lint`)
- `make clean` - Clean build artifacts and node_modules
- `make help` - Show all available commands

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
