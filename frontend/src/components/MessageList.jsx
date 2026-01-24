import React, { useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Loader2 } from 'lucide-react';

const MessageList = ({ messages, loading }) => {
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const renderMessage = (message, index) => {
    const isUser = message.type === 'human';
    
    return (
      <div
        key={index}
        className="py-4 px-4"
      >
        <div className={`max-w-3xl mx-auto flex ${isUser ? 'justify-end' : 'justify-start'}`}>
          {/* Message Bubble */}
          <div className={`
            max-w-[75%] px-4 py-3 rounded-2xl
            ${isUser 
              ? 'bg-blue-600 text-white' 
              : 'bg-gray-700 text-white'
            }
          `}>
            <div className="prose prose-invert max-w-none">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  code: ({ node, inline, className, children, ...props }) => {
                    return inline ? (
                      <code
                        className="bg-black bg-opacity-30 px-1 py-0.5 rounded text-sm"
                        {...props}
                      >
                        {children}
                      </code>
                    ) : (
                      <pre className="bg-black bg-opacity-30 p-4 rounded-lg overflow-x-auto my-2">
                        <code className={className} {...props}>
                          {children}
                        </code>
                      </pre>
                    );
                  },
                  p: ({ children }) => (
                    <p className="mb-2 last:mb-0 text-white">{children}</p>
                  ),
                  ul: ({ children }) => (
                    <ul className="list-disc list-inside mb-2 text-white">
                      {children}
                    </ul>
                  ),
                  ol: ({ children }) => (
                    <ol className="list-decimal list-inside mb-2 text-white">
                      {children}
                    </ol>
                  ),
                  a: ({ href, children }) => (
                    <a
                      href={href}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-200 hover:text-blue-100 underline"
                    >
                      {children}
                    </a>
                  ),
                }}
              >
                {message.content}
              </ReactMarkdown>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="flex-1 overflow-y-auto">
      {messages.length === 0 && !loading && (
        <div className="h-full flex items-center justify-center text-gray-400">
          <div className="text-center">
            <p className="text-xl font-medium">How can I help you today?</p>
          </div>
        </div>
      )}

      {messages.map((message, index) => renderMessage(message, index))}

      {loading && (
        <div className="py-4 px-4">
          <div className="max-w-3xl mx-auto flex justify-start">
            <div className="max-w-[75%] px-4 py-3 rounded-2xl bg-gray-700 flex items-center gap-2">
              <Loader2 className="animate-spin text-white" size={20} />
              <span className="text-white">Thinking...</span>
            </div>
          </div>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  );
};

export default MessageList;
