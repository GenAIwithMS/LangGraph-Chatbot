# OpenGPT Frontend

A modern React frontend for OpenGPT with RAG capabilities, designed with a ChatGPT-like UI using Tailwind CSS.

## Features

- 💬 Real-time chat interface
- 📝 Thread/conversation management
- 📄 PDF upload and document Q&A
- 🎨 ChatGPT-inspired dark theme UI
- 📱 Responsive design (mobile & desktop)
- ⚡ Built with Vite for fast development

## Prerequisites

- Node.js 18+ or npm
- Backend API running on http://localhost:8000

## Installation

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm run dev
```

The frontend will be available at http://localhost:3000

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build

## Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── Sidebar.jsx      # Thread list sidebar
│   │   ├── MessageList.jsx  # Chat messages display
│   │   └── MessageInput.jsx # Message input with PDF upload
│   ├── hooks/               # Custom React hooks
│   │   ├── useThreads.js    # Thread management
│   │   └── useChat.js       # Chat functionality
│   ├── services/            # API services
│   │   └── api.js           # Backend API calls
│   ├── App.jsx              # Main app component
│   ├── main.jsx             # Entry point
│   └── index.css            # Global styles
├── package.json
├── vite.config.js
└── tailwind.config.js
```

## API Integration

The frontend connects to these backend endpoints:

- `POST /api/chat` - Send message
- `POST /api/chat/stream` - Stream responses (SSE)
- `GET /api/threads` - Get all threads
- `POST /api/threads/new` - Create new thread
- `GET /api/threads/{id}` - Get thread messages
- `PUT /api/threads/{id}/title` - Update thread title
- `POST /api/upload-pdf` - Upload PDF document
- `POST /api/query-document` - Query uploaded document
- `GET /api/threads/{id}/document` - Get document info

## Features

### Chat Interface
- Send and receive messages in real-time
- Markdown rendering for formatted responses
- Code syntax highlighting
- Auto-scroll to latest message

### Thread Management
- Create new conversations
- View conversation history
- Rename threads
- Switch between conversations

### PDF/RAG Support
- Drag & drop PDF upload
- Document chunk processing
- Context-aware document queries
- Document status indicator

### UI/UX
- ChatGPT-inspired dark theme
- Responsive mobile sidebar
- Smooth animations
- Loading states
- Error handling

## Customization

### Colors
Edit `tailwind.config.js` to customize the color scheme:

```javascript
theme: {
  extend: {
    colors: {
      'chat-bg': '#343541',      // Main background
      'sidebar-bg': '#202123',   // Sidebar background
      'user-msg': '#343541',     // User message background
      'assistant-msg': '#444654', // AI message background
    }
  }
}
```

### API Base URL
Edit `src/services/api.js` to change the backend URL:

```javascript
const API_BASE_URL = 'http://localhost:8000/api';
```

## Technologies Used

- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client
- **React Markdown** - Markdown rendering
- **Lucide React** - Icon library
- **Remark GFM** - GitHub Flavored Markdown

## Troubleshooting

### CORS Issues
Make sure your backend has CORS enabled for http://localhost:3000

### API Connection Errors
1. Verify backend is running on http://localhost:8000
2. Check browser console for error messages
3. Ensure all API endpoints are accessible

### Build Errors
1. Delete `node_modules` and `package-lock.json`
2. Run `npm install` again
3. Clear npm cache: `npm cache clean --force`

## License

MIT
