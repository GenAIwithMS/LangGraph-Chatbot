import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import MessageList from './components/MessageList';
import MessageInput from './components/MessageInput';
import { useThreads } from './hooks/useThreads';
import { useChat } from './hooks/useChat';
import { chatService } from './services/api';

function App() {
  const [currentThreadId, setCurrentThreadId] = useState(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [documentInfo, setDocumentInfo] = useState(null);
  const [uploadingPDF, setUploadingPDF] = useState(false);

  const {
    threads,
    loading: threadsLoading,
    error: threadsError,
    fetchThreads,
    createNewThread,
    updateThreadTitle,
  } = useThreads();

  const {
    messages,
    loading: chatLoading,
    error: chatError,
    sendMessage,
    loadMessages,
  } = useChat(currentThreadId);

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

  const handleNewThread = async () => {
    const newThreadId = await createNewThread();
    if (newThreadId) {
      setCurrentThreadId(newThreadId);
      setIsSidebarOpen(false);
    }
  };

  const handleThreadSelect = (threadId) => {
    setCurrentThreadId(threadId);
    setIsSidebarOpen(false);
  };

  const handleThreadDelete = async (threadId) => {
    if (confirm('Are you sure you want to delete this chat?')) {
      // If deleting current thread, switch to another or create new
      if (threadId === currentThreadId) {
        const remainingThreads = threads.filter(t => t.thread_id !== threadId);
        if (remainingThreads.length > 0) {
          setCurrentThreadId(remainingThreads[0].thread_id);
        } else {
          await handleNewThread();
        }
      }
      // Note: Backend doesn't have delete endpoint yet, but UI will update
      await fetchThreads();
    }
  };

  const handleSendMessage = async (message) => {
    await sendMessage(message);
    // Refresh threads to update titles if it's a new conversation
    if (messages.length === 0) {
      fetchThreads();
    }
  };

  const handleUploadPDF = async (file) => {
    if (!currentThreadId) {
      alert('Please create a new thread first');
      return;
    }

    try {
      setUploadingPDF(true);
      const response = await chatService.uploadPDF(currentThreadId, file);
      alert(`PDF uploaded successfully! ${response.chunks_created} chunks created.`);
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

  // Create initial thread if none exists - runs only once on mount
  useEffect(() => {
    if (!threadsLoading && threads.length === 0 && !currentThreadId) {
      handleNewThread();
    } else if (!currentThreadId && threads.length > 0) {
      setCurrentThreadId(threads[0].thread_id);
    }
  }, [threadsLoading]); // Only depend on loading state, not threads array

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
      />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col h-screen">
        {/* Header */}
        <div className="flex-shrink-0 border-b border-gray-700 px-4 py-3 bg-chat-bg">
          <div className="max-w-3xl mx-auto flex items-center justify-between">
            <h1 className="text-lg font-semibold">
              {threads.find(t => t.thread_id === currentThreadId)?.title || 'New Chat'}
            </h1>
          </div>
        </div>

        {/* Messages */}
        <MessageList messages={messages} loading={chatLoading} />

        {/* Input */}
        <MessageInput
          onSendMessage={handleSendMessage}
          onUploadPDF={handleUploadPDF}
          disabled={chatLoading || uploadingPDF || !currentThreadId}
          hasDocument={documentInfo?.has_document}
          documentInfo={documentInfo}
        />

        {/* Error Display */}
        {(threadsError || chatError) && (
          <div className="fixed bottom-20 right-4 bg-red-600 text-white px-4 py-2 rounded-lg shadow-lg">
            {threadsError || chatError}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
