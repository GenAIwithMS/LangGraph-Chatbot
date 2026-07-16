import React, { useState, useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import MessageList from './components/MessageList';
import MessageInput from './components/MessageInput';
import ConfirmationModal from './components/ConfirmationModal';
import { useThreads } from './hooks/useThreads';
import { useChat } from './hooks/useChat';
import { chatService } from './services/api';

// Derive the active thread id from the URL path:
//   /                 -> new chat
//   /chat             -> new chat
//   /chat/new         -> new chat
//   /chat/<threadId>  -> that thread
function threadIdFromPath(pathname) {
  const path = pathname.replace(/\/+$/, '');
  if (path === '' || path === '/chat' || path === '/chat/new') return null;
  const m = path.match(/^\/chat\/(.+)$/);
  return m ? decodeURIComponent(m[1]) : null;
}

function App() {
  const location = useLocation();
  const navigate = useNavigate();
  const urlThreadId = threadIdFromPath(location.pathname);
  const [currentThreadId, setCurrentThreadId] = useState(urlThreadId || null);
  // Set right before navigating to a freshly created thread so useChat skips
  // its backend reload (the messages were just streamed into the UI).
  const skipLoadRef = useRef(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [documentInfo, setDocumentInfo] = useState(null);
  const [uploadingPDF, setUploadingPDF] = useState(false);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [threadToDelete, setThreadToDelete] = useState(null);

  const {
    threads,
    loading: threadsLoading,
    error: threadsError,
    fetchThreads,
    updateThreadTitle,
  } = useThreads();

  // Keep the active thread in sync with the URL (deep links, back/forward).
  useEffect(() => {
    const id = urlThreadId || null;
    setCurrentThreadId((prev) => (prev === id ? prev : id));
  }, [urlThreadId]);

  // Called when the backend creates a brand-new thread (first message in a
  // "New Chat"). Silently updates the URL without interrupting the user.
  const handleThreadCreated = (id) => {
    skipLoadRef.current = true;
    setCurrentThreadId(id);
    navigate(`/chat/${id}`, { replace: true });
    fetchThreads();
  };

  const {
    messages,
    loading: chatLoading,
    error: chatError,
    sendMessage,
    regenerate,
    editMessage,
    loadMessages,
    streamingProgress,
    stop,
  } = useChat(currentThreadId, handleThreadCreated, skipLoadRef);

  // Load document info when thread changes
  useEffect(() => {
    if (currentThreadId) {
      loadDocumentInfo();
    } else {
      setDocumentInfo(null);
    }
  }, [currentThreadId]);

  const loadDocumentInfo = async () => {
    if (!currentThreadId) return;
    
    try {
      const info = await chatService.getDocumentInfo(currentThreadId);
      setDocumentInfo(info.has_document ? info : null);
    } catch (error) {
      console.error('Error loading document info:', error);
      setDocumentInfo(null);
    }
  };

  const handleNewThread = () => {
    // New chat stays client-side until the first message is sent; the backend
    // then creates the thread and the URL is updated silently.
    setCurrentThreadId(null);
    setIsSidebarOpen(false);
    navigate('/chat');
  };

  const handleThreadSelect = (threadId) => {
    setCurrentThreadId(threadId);
    setIsSidebarOpen(false);
    navigate(`/chat/${threadId}`);
  };

  const handleThreadDelete = (threadId) => {
    setThreadToDelete(threadId);
    setDeleteModalOpen(true);
  };

  const confirmDeleteThread = async () => {
    if (!threadToDelete) return;
    
    try {
      // Call the delete API
      await chatService.deleteThread(threadToDelete);
      
      // If deleting current thread, switch to another or go to new chat
      if (threadToDelete === currentThreadId) {
        const remainingThreads = threads.filter(t => t.thread_id !== threadToDelete);
        if (remainingThreads.length > 0) {
          const nextId = remainingThreads[0].thread_id;
          setCurrentThreadId(nextId);
          navigate(`/chat/${nextId}`);
        } else {
          setCurrentThreadId(null);
          navigate('/chat');
        }
      }
      
      // Refresh threads list
      await fetchThreads();
      
      // Close modal and reset state
      setDeleteModalOpen(false);
      setThreadToDelete(null);
    } catch (error) {
      console.error('Error deleting thread:', error);
      alert('Failed to delete chat. Please try again.');
    }
  };

  const cancelDeleteThread = () => {
    setDeleteModalOpen(false);
    setThreadToDelete(null);
  };

  const handleSendMessage = async (message, tools = []) => {
    await sendMessage(message, tools);
    // Refresh threads so a newly created chat (and updated titles) show in the sidebar
    fetchThreads();
  };

  const handleUploadPDF = async (file) => {
    if (!currentThreadId) {
      alert('Please send a message first to start a chat.');
      return;
    }

    try {
      setUploadingPDF(true);
      const response = await chatService.uploadPDF(currentThreadId, file);
      if (response.thread_id && response.thread_id !== currentThreadId) {
        setCurrentThreadId(response.thread_id);
      }
      await loadDocumentInfo();
    } catch (error) {
      console.error('Error uploading PDF:', error);
      alert('Failed to upload PDF. Please try again.');
    } finally {
      setUploadingPDF(false);
    }
  };

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const toggleSidebarCollapse = () => {
    setIsSidebarCollapsed((c) => !c);
  };

  return (
    <div className="flex h-screen bg-chat-bg text-white overflow-hidden">
      {/* Sidebar */}
      <Sidebar
        threads={threads}
        currentThreadId={currentThreadId}
        onThreadSelect={handleThreadSelect}
        onNewThread={handleNewThread}
        onThreadRename={updateThreadTitle}
        onThreadDelete={handleThreadDelete}
        isSidebarOpen={isSidebarOpen}
        toggleSidebar={toggleSidebar}
        isCollapsed={isSidebarCollapsed}
        onToggleCollapse={toggleSidebarCollapse}
      />

      {/* Main Chat Area */}
      <div className="flex-1 flex h-screen relative">
        {/* Chat Section */}
        <div className="flex-1 flex flex-col">
          {/* Header */}
          <div className="flex-shrink-0 border-b border-gray-700 px-4 py-3 bg-chat-bg">
            <div className="max-w-3xl mx-auto">
              {/* Empty header or add logo/branding here if needed */}
            </div>
          </div>

          {/* Messages */}
          <MessageList
            messages={messages}
            loading={chatLoading}
            streaming={streamingProgress?.isStreaming}
            streamingProgress={streamingProgress}
            onRegenerate={regenerate}
            onEditMessage={editMessage}
          />

          {/* Input */}
          <MessageInput
            onSendMessage={handleSendMessage}
            onUploadPDF={handleUploadPDF}
            onStop={stop}
            disabled={chatLoading || uploadingPDF}
            hasDocument={documentInfo?.has_document}
            documentInfo={documentInfo}
            uploadingPDF={uploadingPDF}
          />

          {/* Error Display */}
          {(threadsError || chatError) && (
            <div className="fixed bottom-20 right-4 bg-red-600 text-white px-4 py-2 rounded-lg shadow-lg">
              {threadsError || chatError}
            </div>
          )}
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      <ConfirmationModal
        isOpen={deleteModalOpen}
        onClose={cancelDeleteThread}
        onConfirm={confirmDeleteThread}
        title="Delete Chat"
        message="Are you sure you want to delete this chat? This action cannot be undone and will permanently remove all messages and uploaded documents."
        confirmText="Delete"
        cancelText="Cancel"
        danger={true}
      />
    </div>
  );
}

export default App;
