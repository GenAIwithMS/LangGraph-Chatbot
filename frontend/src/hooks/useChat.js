import { useState, useEffect } from 'react';
import { chatService } from '../services/api';

export const useChat = (threadId) => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [streamingProgress, setStreamingProgress] = useState(null);

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

  const updateProgressStep = (stepLabel, status) => {
    setStreamingProgress(prev => {
      if (!prev) return null;
      
      const stepIndex = prev.steps.findIndex(s => s.label === stepLabel);
      if (stepIndex === -1) return prev;
      
      const newSteps = [...prev.steps];
      newSteps[stepIndex] = { ...newSteps[stepIndex], status };
      
      // Mark previous steps as completed
      for (let i = 0; i < stepIndex; i++) {
        if (newSteps[i].status !== 'completed') {
          newSteps[i] = { ...newSteps[i], status: 'completed' };
        }
      }
      
      return { ...prev, steps: newSteps };
    });
  };

  const sendMessage = async (message, tools = []) => {
    if (!threadId || !message.trim()) return;

    try {
      setLoading(true);
      
      // Add user message immediately
      const userMessage = {
        type: 'human',
        content: message,
        timestamp: new Date().toISOString(),
        tools: tools.length > 0 ? tools : undefined,
      };
      setMessages(prev => [...prev, userMessage]);

      // Initialize streaming progress if using blogs tool
      if (tools.includes('blogs')) {
        setStreamingProgress({
          isStreaming: true,
          toolName: 'blogs',
          steps: [
            { label: 'Routing...', status: 'in-progress' },
            { label: 'Researching...', status: 'pending' },
            { label: 'Planning...', status: 'pending' },
            { label: 'Writing sections...', status: 'pending' },
            { label: 'Finalizing...', status: 'pending' },
          ],
        });
        
        // Use streaming endpoint
        let aiResponse = '';
        
        const handleMessage = (data) => {
          if (data.message_type === 'progress') {
            // Update progress based on node
            if (data.node === 'router') {
              updateProgressStep('Routing...', 'completed');
              updateProgressStep('Researching...', 'in-progress');
              setStreamingProgress(prev => {
                if (!prev) return null;
                const newSteps = [...prev.steps];
                const idx = newSteps.findIndex(s => s.label === 'Routing...');
                if (idx !== -1) newSteps[idx] = { ...newSteps[idx], details: data.content };
                return { ...prev, steps: newSteps };
              });
            } else if (data.node === 'research') {
              updateProgressStep('Researching...', 'completed');
              updateProgressStep('Planning...', 'in-progress');
              setStreamingProgress(prev => {
                if (!prev) return null;
                const newSteps = [...prev.steps];
                const idx = newSteps.findIndex(s => s.label === 'Researching...');
                if (idx !== -1) newSteps[idx] = { ...newSteps[idx], details: data.content };
                return { ...prev, steps: newSteps };
              });
            } else if (data.node === 'orchestrator') {
              updateProgressStep('Planning...', 'completed');
              updateProgressStep('Writing sections...', 'in-progress');
              setStreamingProgress(prev => {
                if (!prev) return null;
                const newSteps = [...prev.steps];
                const idx = newSteps.findIndex(s => s.label === 'Planning...');
                if (idx !== -1) newSteps[idx] = { ...newSteps[idx], details: data.content };
                return { ...prev, steps: newSteps };
              });
            } else if (data.node === 'worker') {
              // Keep writing in progress, just add count
              setStreamingProgress(prev => {
                if (!prev) return null;
                const newSteps = [...prev.steps];
                const idx = newSteps.findIndex(s => s.label === 'Writing sections...');
                if (idx !== -1) {
                  const currentCount = newSteps[idx].sectionCount || 0;
                  newSteps[idx] = { ...newSteps[idx], sectionCount: currentCount + 1, details: `${currentCount + 1} sections completed` };
                }
                return { ...prev, steps: newSteps };
              });
            }
          } else if (data.message_type === 'ai') {
            aiResponse += data.content;
            updateProgressStep('Writing sections...', 'completed');
            updateProgressStep('Finalizing...', 'completed');
          }
          
          if (data.done) {
            // Add final AI message
            setMessages(prev => [...prev, {
              type: 'ai',
              content: aiResponse,
              timestamp: new Date().toISOString(),
            }]);
            setStreamingProgress(null);
            setLoading(false);
          }
        };
        
        const handleError = (error) => {
          setError('Streaming error occurred');
          setStreamingProgress(null);
          setLoading(false);
        };
        
        chatService.streamMessage(threadId, message, tools, handleMessage, handleError);
        return;
      }

      // Non-streaming path for other tools
      const response = await chatService.sendMessage(threadId, message, tools);
      
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
      setStreamingProgress(null);
    } finally {
      if (!tools.includes('blogs')) {
        setLoading(false);
      }
    }
  };

  return {
    messages,
    loading,
    error,
    sendMessage,
    loadMessages,
    streamingProgress,
  };
};
