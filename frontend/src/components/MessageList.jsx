import React, { useEffect, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import { Loader2, Copy, Check, ThumbsUp, ThumbsDown, RotateCcw } from 'lucide-react';
import { CodeBlock, CodeBlockCode, CodeBlockGroup, CopyButton } from './ui/code-block';

function nodeToString(node) {
  if (typeof node === 'string') return node;
  if (Array.isArray(node)) return node.map(nodeToString).join('');
  if (node && node.props && node.props.children) return nodeToString(node.props.children);
  return '';
}

function MessageActions({ content, onRegenerate }) {
  const [copied, setCopied] = useState(false);
  const [feedback, setFeedback] = useState(null); // 'like' | 'dislike'

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (e) {
      // clipboard may be unavailable; ignore
    }
  };

  const btn =
    'inline-flex items-center justify-center p-1.5 rounded-md text-gray-400 transition-colors hover:bg-white/5 hover:text-gray-200';

  return (
    <div className="mt-2 flex items-center gap-1 justify-end">
      <button
        type="button"
        onClick={handleCopy}
        title="Copy"
        aria-label="Copy"
        className={`${btn} ${copied ? 'text-green-400' : ''}`}
      >
        {copied ? <Check size={15} /> : <Copy size={15} />}
        {copied && <span className="text-xs ml-1">Copied</span>}
      </button>
      <button
        type="button"
        title="Helpful"
        aria-label="Helpful"
        onClick={() => setFeedback(feedback === 'like' ? null : 'like')}
        className={`${btn} ${feedback === 'like' ? 'text-green-400' : ''}`}
      >
        <ThumbsUp size={15} />
      </button>
      <button
        type="button"
        title="Not helpful"
        aria-label="Not helpful"
        onClick={() => setFeedback(feedback === 'dislike' ? null : 'dislike')}
        className={`${btn} ${feedback === 'dislike' ? 'text-red-400' : ''}`}
      >
        <ThumbsDown size={15} />
      </button>
      <button
        type="button"
        title="Regenerate"
        aria-label="Regenerate"
        onClick={() => onRegenerate()}
        className={btn}
      >
        <RotateCcw size={15} />
      </button>
    </div>
  );
}

const markdownComponents = {
  pre: ({ children }) => <>{children}</>,
  code: ({ node, className, children, ...props }) => {
    const match = /language-(\w+)/.exec(className || '');
    const text = nodeToString(children).replace(/\n$/, '');
    const isBlock = !!match || text.includes('\n');

    if (!isBlock) {
      return (
        <code
          className="bg-[#1a1b1e] px-1.5 py-0.5 rounded text-sm font-mono text-gray-200"
          {...props}
        >
          {children}
        </code>
      );
    }

    const lang = match ? match[1] : 'text';
    return (
      <CodeBlock>
        <CodeBlockGroup>
          <span className="text-xs text-gray-400">{lang}</span>
        </CodeBlockGroup>
        <CopyButton value={text} />
        <CodeBlockCode code={text} language={lang} theme="github-dark" />
      </CodeBlock>
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
};

const MessageList = ({ messages, loading, streaming, streamingProgress, onRegenerate }) => {
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
              {message.streaming && streamingProgress?.isStreaming && (
                <div className="mb-3 rounded-md border border-gray-700 bg-[#1a1b1e]/60 p-3">
                  <div className="flex items-center gap-2 text-sm text-gray-300">
                    <Loader2 size={15} className="animate-spin text-blue-400 shrink-0" />
                    <span className="font-medium">
                      {streamingProgress.current || 'Thinking...'}
                    </span>
                  </div>

                  {streamingProgress.thoughts?.length > 0 && (
                    <div className="mt-1.5 space-y-0.5 text-xs text-gray-500">
                      {streamingProgress.thoughts.map((t, i) => (
                        <div key={i} className="truncate">• {t}</div>
                      ))}
                    </div>
                  )}

                  {streamingProgress.steps?.length > 0 && (
                    <div className="mt-1.5 space-y-1">
                      {streamingProgress.steps.map((s, i) => (
                        <div key={i} className="flex items-center gap-2 text-xs">
                          <span
                            className={
                              s.status === 'completed'
                                ? 'text-green-400'
                                : s.status === 'in-progress'
                                ? 'text-gray-200'
                                : 'text-gray-600'
                            }
                          >
                            •
                          </span>
                          <span
                            className={
                              s.status === 'in-progress'
                                ? 'text-gray-200'
                                : s.status === 'completed'
                                ? 'text-gray-400'
                                : 'text-gray-600'
                            }
                          >
                            {s.label}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                rehypePlugins={[rehypeRaw]}
                components={markdownComponents}
              >
                {message.content}
              </ReactMarkdown>
              {message.streaming && (
                <span className="inline-block w-1.5 h-4 ml-0.5 align-middle bg-gray-400 animate-pulse" />
              )}
            </div>
            {!isUser && (
              <MessageActions content={message.content} onRegenerate={onRegenerate} />
            )}
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

      {loading && !streaming && (
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
