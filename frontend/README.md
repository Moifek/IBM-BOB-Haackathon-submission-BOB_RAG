# Medical Q&A Frontend

React-based frontend for the Medical Q&A Assistant MVP.

## Features

- **Single-screen chat interface** - Clean, focused user experience
- **Role selection** - Toggle between Patient and Doctor modes
- **Dark mode support** - Automatic theme detection with manual toggle
- **Source citations** - Expandable panel showing reference sources
- **Responsive design** - Works on desktop and mobile devices
- **Real-time feedback** - Loading states and error handling

## Tech Stack

- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first styling
- **Fetch API** - HTTP client for backend communication

## Development

### Prerequisites

- Node.js 18+ and npm

### Setup

```bash
# Install dependencies
npm install

# Start dev server (with API proxy)
npm run dev
```

The dev server runs on `http://localhost:5173` and proxies API requests to `http://localhost:8000`.

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally
- `npm run lint` - Run ESLint

## Production Build

### Docker

```bash
# Build image
docker build -t medical-qa-frontend .

# Run container
docker run -p 80:80 medical-qa-frontend
```

### Manual Build

```bash
# Build static files
npm run build

# Output is in dist/ directory
# Serve with any static file server
```

## Project Structure

```
frontend/
├── src/
│   ├── App.jsx              # Main application component
│   ├── main.jsx             # React entry point
│   ├── index.css            # Global styles with Tailwind
│   ├── api/
│   │   └── client.js        # API client (postQuery, checkHealth)
│   └── components/
│       ├── ChatWindow.jsx   # Main chat interface
│       ├── MessageBubble.jsx # Individual message display
│       ├── SourcePanel.jsx  # Citation display
│       ├── RoleSelector.jsx # Patient/Doctor toggle
│       └── DarkModeToggle.jsx # Theme switcher
├── public/                  # Static assets
├── index.html              # HTML entry point
├── vite.config.js          # Vite configuration
├── tailwind.config.js      # Tailwind configuration
├── postcss.config.js       # PostCSS configuration
├── nginx.conf              # Nginx config for production
├── Dockerfile              # Multi-stage Docker build
└── package.json            # Dependencies and scripts
```

## API Integration

The frontend communicates with the backend via:

- `POST /query` - Submit questions and get answers
- `GET /health` - Check backend status

See `src/api/client.js` for implementation details.

## Environment Variables

Create a `.env` file for custom configuration:

```env
VITE_API_URL=http://localhost:8000
```

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## License

See root LICENSE file.