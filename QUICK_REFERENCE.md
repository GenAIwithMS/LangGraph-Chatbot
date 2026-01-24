# Quick Reference Card

## 🚀 Start Application

### One-Click Start
```bash
# Windows
start.bat

# Linux/Mac
./start.sh
```

### Manual Start
```bash
# Terminal 1 - Backend
python main.py

# Terminal 2 - Frontend  
cd frontend && npm run dev
```

## 🌐 Access URLs

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | React UI |
| Backend | http://localhost:8000 | FastAPI server |
| API Docs | http://localhost:8000/docs | Swagger UI |
| Redoc | http://localhost:8000/redoc | Alternative docs |

## 📋 Common Tasks

### Create New Thread
```bash
curl -X POST http://localhost:8000/api/threads/new
```

### Send Message
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"thread_id": "your-id", "message": "Hello"}'
```

### Upload PDF
```bash
curl -X POST http://localhost:8000/api/upload-pdf \
  -F "file=@document.pdf" \
  -F "thread_id=your-id"
```

### Query Document
```bash
curl -X POST http://localhost:8000/api/query-document \
  -H "Content-Type: application/json" \
  -d '{"thread_id": "your-id", "query": "What is this about?"}'
```

## 🛠️ Development Commands

### Backend
```bash
# Run with auto-reload
python main.py

# Install new package
pip install package-name
pip freeze > requirements.txt

# Database reset
del chatbot.db  # Windows
rm chatbot.db   # Linux/Mac
```

### Frontend
```bash
cd frontend

# Install dependencies
npm install

# Dev server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Install new package
npm install package-name
```

## 🎨 Customization Quick Edits

### Change Model
Edit [app/services/chatbot_service.py](app/services/chatbot_service.py#L13)
```python
model = ChatGroq(model="qwen/qwen3-32b")  # Change model name
```

### Add New Tool
Edit [app/tools/all_tools.py](app/tools/all_tools.py)
```python
@tool
def my_new_tool(query: str) -> str:
    """Tool description"""
    return result
```

### Change Colors
Edit [frontend/tailwind.config.js](frontend/tailwind.config.js#L7-L14)
```javascript
colors: {
  'chat-bg': '#343541',        // Main background
  'sidebar-bg': '#202123',     // Sidebar
  'user-msg': '#343541',       // User messages
  'assistant-msg': '#444654',  // AI messages
}
```

### Modify API URL
Edit [frontend/src/services/api.js](frontend/src/services/api.js#L3)
```javascript
const API_BASE_URL = 'http://localhost:8000/api';
```

## 🔑 Required API Keys

Add to `.env` file:
```env
GROQ_API_KEY=gsk_...                    # Required - Get from console.groq.com
BRAVE_API_KEY=BSA...                    # Optional - For search tool
OPENWEATHER_API_KEY=...                 # Optional - For weather tool
ALPHA_VANTAGE_API_KEY=...               # Optional - For stock tool
LANGSMITH_API_KEY=...                   # Optional - For tracing
```

## 🐛 Common Issues & Fixes

### Backend Won't Start
```bash
# Check Python version (need 3.8+)
python --version

# Reinstall dependencies
pip install -r requirements.txt

# Check .env file exists
dir .env  # Windows
ls .env   # Linux/Mac
```

### Frontend Won't Start
```bash
cd frontend

# Check Node version (need 18+)
node --version

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Or with npm cache clean
npm cache clean --force
npm install
```

### CORS Errors
Check [app/main.py](app/main.py) has:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Tools Not Working
1. Verify API keys in `.env`
2. Check API key format (no quotes)
3. Test API keys on provider websites
4. Check backend logs for errors

## 📦 Project Structure Quick Map

```
.
├── app/                    # Backend
│   ├── main.py            # FastAPI app
│   ├── router/chat.py     # API endpoints
│   ├── services/          # Business logic
│   │   ├── chatbot_service.py  # LangGraph
│   │   ├── chat_service.py     # Chat ops
│   │   ├── rag_service.py      # PDF/RAG
│   │   └── thread_service.py   # Threads
│   └── tools/all_tools.py # External tools
├── frontend/              # React app
│   └── src/
│       ├── components/    # UI components
│       ├── hooks/         # Custom hooks
│       └── services/      # API client
├── main.py               # Backend entry
├── start.bat             # Windows launcher
└── .env                  # API keys (create this!)
```

## 💡 Tips & Tricks

### Frontend Dev Tips
- Use React DevTools browser extension
- Check browser console (F12) for errors
- Use Network tab to debug API calls
- Lighthouse for performance audits

### Backend Dev Tips
- Use `/docs` endpoint to test APIs
- Check terminal for error traces
- Use LangSmith for conversation tracing
- SQLite Browser to inspect database

### Debugging
```bash
# Backend logs
python main.py
# Watch terminal output

# Frontend logs  
# Open browser console (F12)
# Check Console and Network tabs
```

### Performance
- Backend: Upgrade to paid Groq tier for faster responses
- Frontend: Run `npm run build` for production bundle
- Database: Regular cleanup of old threads
- RAG: Adjust chunk size/overlap in rag_service.py

## 📞 Quick Help

1. **Read Documentation**
   - [README.md](README.md) - Full guide
   - [SETUP.md](SETUP.md) - Setup steps
   - [TESTING.md](TESTING.md) - Testing guide

2. **Check Logs**
   - Backend: Terminal where `python main.py` runs
   - Frontend: Browser console (F12)

3. **Test APIs**
   - Use http://localhost:8000/docs
   - Try curl commands from terminal

4. **Verify Setup**
   - Python 3.8+ installed
   - Node.js 18+ installed
   - All dependencies installed
   - .env file configured
   - Ports 3000 & 8000 free

## 🎯 Feature Checklist

- [x] Chat with AI (Groq LLM)
- [x] Multi-thread conversations
- [x] Thread management (create, rename, switch)
- [x] Persistent storage (SQLite)
- [x] Web search (Brave API)
- [x] Weather lookup (OpenWeather)
- [x] Calculator
- [x] Stock prices (Alpha Vantage)
- [x] PDF upload
- [x] Document Q&A (RAG)
- [x] Markdown rendering
- [x] Code syntax highlighting
- [x] Responsive mobile UI
- [x] Dark theme (ChatGPT-like)
- [x] Auto-scrolling messages
- [x] Drag & drop file upload

## 🌟 What's Next?

Possible enhancements:
- [ ] User authentication
- [ ] Message streaming (SSE)
- [ ] Image generation
- [ ] Voice input/output
- [ ] Export conversations
- [ ] Share conversations
- [ ] Custom system prompts
- [ ] Model selection dropdown
- [ ] Conversation search
- [ ] Message editing
- [ ] Regenerate responses
- [ ] Dark/light theme toggle
