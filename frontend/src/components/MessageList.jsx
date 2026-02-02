import React, { useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import { Loader2 } from 'lucide-react';

const MessageList = ({ messages, loading }) => {
  const messagesEndRef = useRef(null);
  const previousLengthRef = useRef(0);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    const lastMessage = messages[messages.length - 1];
    const isInitialLoad = previousLengthRef.current === 0 && messages.length > 0;
    const isNewUserMessage =
      messages.length > previousLengthRef.current && lastMessage?.type === 'human';

    if (isInitialLoad || isNewUserMessage) {
      scrollToBottom();
    }

    previousLengthRef.current = messages.length;
  }, [messages]);

  const renderMessage = (message, index) => {
    const isUser = message.type === 'human';
    
    return (
      <div
        key={index}
        className="py-4 px-4"
      >
        <div className={`max-w-3xl mx-auto flex ${isUser ? 'justify-end' : 'justify-start'}`}>
          {/* Message Content */}
          <div className={`
            max-w-[80%] px-4 py-3 rounded-lg
            ${isUser 
              ? 'bg-[#2a2b32] text-gray-100' 
              : 'text-gray-100'
            }
          `}>
            <div className="prose prose-invert max-w-none">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                rehypePlugins={[rehypeRaw]}
                components={{
                  code: ({ node, inline, className, children, ...props }) => {
                    return inline ? (
                      <code
                        className="bg-[#1a1b1e] px-1.5 py-0.5 rounded text-sm font-mono text-gray-200"
                        {...props}
                      >
                        {children}
                      </code>
                    ) : (
                      <pre className="bg-[#1a1b1e] p-4 rounded-lg overflow-x-auto my-3 border border-gray-700">
                        <code className={`${className} text-gray-200 text-sm font-mono`} {...props}>
                          {children}
                        </code>
                      </pre>
                    );
                  },
                  p: ({ children }) => (
                    <p className="mb-3 last:mb-0 leading-7 text-gray-100 whitespace-pre-wrap break-words">{children}</p>
                  ),
                  ul: ({ children }) => (
                    <ul className="list-disc ml-6 mb-3 space-y-1 text-gray-100">
                      {children}
                    </ul>
                  ),
                  ol: ({ children }) => (
                    <ol className="list-decimal ml-6 mb-3 space-y-1 text-gray-100">
                      {children}
                    </ol>
                  ),
                  li: ({ children }) => (
                    <li className="leading-7 text-gray-100">{children}</li>
                  ),
                  h1: ({ children }) => (
                    <h1 className="text-2xl font-bold mb-3 mt-4 text-gray-100">{children}</h1>
                  ),
                  h2: ({ children }) => (
                    <h2 className="text-xl font-bold mb-3 mt-4 text-gray-100">{children}</h2>
                  ),
                  h3: ({ children }) => (
                    <h3 className="text-lg font-bold mb-2 mt-3 text-gray-100">{children}</h3>
                  ),
                  blockquote: ({ children }) => (
                    <blockquote className="border-l-4 border-gray-600 pl-4 my-3 italic text-gray-300">
                      {children}
                    </blockquote>
                  ),
                  table: ({ children }) => (
                    <div className="overflow-x-auto my-3">
                      <table className="min-w-full border-collapse border border-gray-600">
                        {children}
                      </table>
                    </div>
                  ),
                  th: ({ children }) => (
                    <th className="border border-gray-600 px-4 py-2 bg-[#2a2b32] font-semibold text-left text-gray-100">
                      {children}
                    </th>
                  ),
                  td: ({ children }) => (
                    <td className="border border-gray-600 px-4 py-2 text-gray-100">
                      {children}
                    </td>
                  ),
                  a: ({ href, children }) => (
                    <a
                      href={href}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-400 hover:text-blue-300 underline break-words"
                    >
                      {children}
                    </a>
                  ),
                  strong: ({ children }) => (
                    <strong className="font-semibold text-gray-100">{children}</strong>
                  ),
                  br: () => <br />,
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
            <div className="flex items-center gap-2">
              <Loader2 className="animate-spin text-gray-400" size={20} />
              <span className="text-gray-400">Thinking...</span>
            </div>
          </div>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  );
};

export default MessageList;
