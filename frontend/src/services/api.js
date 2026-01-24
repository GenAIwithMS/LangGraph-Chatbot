import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const chatService = {
  // Send a message to the chatbot
  sendMessage: async (threadId, message) => {
    const response = await api.post('/chat', {
      thread_id: threadId,
      message: message,
    });
    return response.data;
  },

  // Stream messages (using EventSource for SSE)
  streamMessage: (threadId, message, onMessage, onError) => {
    const eventSource = new EventSource(
      `${API_BASE_URL}/chat/stream?thread_id=${threadId}&message=${encodeURIComponent(message)}`
    );

    eventSource.onmessage = (event) => {
      if (event.data === '[DONE]') {
        eventSource.close();
        return;
      }
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch (error) {
        console.error('Error parsing message:', error);
      }
    };

    eventSource.onerror = (error) => {
      console.error('EventSource error:', error);
      eventSource.close();
      if (onError) onError(error);
    };

    return eventSource;
  },

  // Get all threads
  getThreads: async () => {
    const response = await api.get('/threads');
    return response.data.threads;
  },

  // Create a new thread
  createThread: async () => {
    const response = await api.post('/threads/new');
    return response.data;
  },

  // Get messages from a specific thread
  getThreadMessages: async (threadId) => {
    const response = await api.get(`/threads/${threadId}`);
    return response.data;
  },

  // Update thread title
  updateThreadTitle: async (threadId, title) => {
    const response = await api.put(`/threads/${threadId}/title`, { title });
    return response.data;
  },

  // Upload PDF
  uploadPDF: async (threadId, file) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('thread_id', threadId);

    const response = await api.post('/upload-pdf', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Query document
  queryDocument: async (threadId, query) => {
    const response = await api.post('/query-document', {
      thread_id: threadId,
      query: query,
    });
    return response.data;
  },

  // Get document info
  getDocumentInfo: async (threadId) => {
    const response = await api.get(`/threads/${threadId}/document`);
    return response.data;
  },
};
