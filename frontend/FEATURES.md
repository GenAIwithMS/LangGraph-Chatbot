# Frontend Features Overview

## UI Components

### 1. **Sidebar** (`Sidebar.jsx`)
- **New Chat Button**: Creates a new conversation thread
- **Thread List**: Shows all conversation history
- **Thread Renaming**: Click edit icon to rename threads
- **Active Thread Highlight**: Current thread is highlighted
- **Responsive**: Collapsible on mobile with hamburger menu

### 2. **Message List** (`MessageList.jsx`)
- **User Messages**: Blue avatar, displayed on user message background
- **AI Messages**: Green avatar (bot icon), displayed on assistant background
- **Markdown Rendering**: Full markdown support including:
  - Headers, lists, links
  - Inline and block code with syntax highlighting
  - Tables (GitHub Flavored Markdown)
- **Auto-scroll**: Automatically scrolls to latest message
- **Loading Indicator**: Animated spinner while AI is responding

### 3. **Message Input** (`MessageInput.jsx`)
- **Text Area**: Auto-expanding textarea for message input
- **Send Button**: Click or press Enter to send
- **PDF Upload**: 
  - Click paperclip icon to select file
  - Drag & drop PDF files directly
  - Visual feedback on drag-over
- **Document Status**: Shows uploaded PDF info with chunk count
- **Keyboard Shortcuts**: 
  - Enter = Send message
  - Shift+Enter = New line

## User Experience Flow

### Starting a Chat
1. App loads → Creates initial thread automatically
2. Welcome screen shows "How can I help you today?"
3. Type message → Press Enter → AI responds
4. Thread title auto-generated from first message

### Using Tools
The AI automatically detects when to use tools based on your query:
- "What's the weather?" → Weather tool activated
- "Search for X" → Brave search tool activated
- "Calculate 5 * 20" → Calculator tool activated
- "TSLA stock price" → Stock tool activated

### PDF Document Q&A
1. Click paperclip icon (or drag PDF onto input)
2. Select PDF file → Upload starts
3. Success message shows chunk count
4. Green indicator appears above input
5. Ask questions about the document
6. AI retrieves relevant context from PDF to answer

### Thread Management
1. Click "+ New chat" to start fresh conversation
2. Click any thread in sidebar to switch
3. Hover over thread → Click edit icon to rename
4. All threads persist in database

## Styling Details

### Color Scheme (ChatGPT-inspired)
```
Background:           #343541 (chat-bg)
Sidebar:              #202123 (sidebar-bg)  
User Messages:        #343541 (user-msg)
Assistant Messages:   #444654 (assistant-msg)
Primary Accent:       Blue (#3B82F6)
Success:              Green (#10B981)
Text:                 White/Gray shades
```

### Responsive Breakpoints
- **Desktop** (lg: 1024px+): Sidebar always visible
- **Mobile** (< 1024px): Sidebar collapsible with menu button

### Animations
- Sidebar slide in/out transition
- Message fade-in on load
- Smooth scroll to bottom
- Loading spinner rotation
- Hover effects on buttons

## Custom Hooks

### `useThreads()`
Manages thread operations:
- `threads`: Array of all threads
- `loading`: Loading state
- `error`: Error messages
- `createNewThread()`: Create new thread
- `updateThreadTitle()`: Rename thread
- `fetchThreads()`: Refresh thread list

### `useChat(threadId)`
Manages chat operations for a thread:
- `messages`: Array of messages in thread
- `loading`: Message sending state
- `error`: Error messages
- `sendMessage(text)`: Send message to AI
- `loadMessages()`: Load thread history

## API Integration

All API calls are centralized in `services/api.js`:

```javascript
chatService.sendMessage(threadId, message)
chatService.getThreads()
chatService.createThread()
chatService.getThreadMessages(threadId)
chatService.updateThreadTitle(threadId, title)
chatService.uploadPDF(threadId, file)
chatService.queryDocument(threadId, query)
chatService.getDocumentInfo(threadId)
```

## Performance Optimizations

1. **Lazy Loading**: Messages loaded only when thread is selected
2. **Memo Components**: Prevent unnecessary re-renders
3. **Debounced Input**: Textarea auto-resize debounced
4. **Virtual Scrolling**: Could be added for very long conversations
5. **Image Optimization**: SVG icons for small bundle size

## Accessibility Features

- Semantic HTML elements
- ARIA labels on interactive elements
- Keyboard navigation support
- Focus management
- Color contrast ratios meet WCAG standards
- Screen reader friendly

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Mobile Features

- Touch-friendly button sizes (min 44x44px)
- Swipe gesture for sidebar (can be added)
- Responsive typography
- Optimized for portrait and landscape
- No horizontal scroll
