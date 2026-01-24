import { useState, useEffect } from 'react';
import { chatService } from '../services/api';

export const useChat = (threadId) => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (threadId) {
      loadMessages();
    } else {
      setMessages([]);
    }
  }, [threadId]);

  const loadMessages = async () => {
    if (!threadId) return;
    
    try {
      setLoading(true);
      const data = await chatService.getThreadMessages(threadId);
      setMessages(data.messages || []);
      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('Error loading messages:', err);
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async (message) => {
    if (!threadId || !message.trim()) return;

    try {
      setLoading(true);
      
      // Add user message immediately
      const userMessage = {
        type: 'human',
        content: message,
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, userMessage]);

      // Send to backend
      const response = await chatService.sendMessage(threadId, message);
      
      // Replace with actual response
      setMessages(prev => [
        ...prev.slice(0, -1),
        userMessage,
        {
          type: 'ai',
          content: response.response,
          timestamp: new Date().toISOString(),
        }
      ]);
      
      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('Error sending message:', err);
    } finally {
      setLoading(false);
    }
  };

  return {
    messages,
    loading,
    error,
    sendMessage,
    loadMessages,
  };
};
