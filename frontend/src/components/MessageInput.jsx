import React, { useState, useRef } from 'react';
import { Send, Paperclip, FileText } from 'lucide-react';

const MessageInput = ({ onSendMessage, onUploadPDF, disabled, hasDocument, documentInfo }) => {
  const [message, setMessage] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSendMessage(message);
      setMessage('');
    }
  };

  const handleFileSelect = (file) => {
    if (file && file.type === 'application/pdf') {
      onUploadPDF(file);
    } else {
      alert('Please upload a PDF file');
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = Array.from(e.dataTransfer.files);
    const pdfFile = files.find(file => file.type === 'application/pdf');
    
    if (pdfFile) {
      handleFileSelect(pdfFile);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  return (
    <div className="border-t border-gray-700 bg-chat-bg">
      {/* Document Status */}
      {hasDocument && documentInfo && (
        <div className="max-w-3xl mx-auto px-4 py-2">
          <div className="flex items-center gap-2 text-sm text-green-400 bg-green-900/20 px-3 py-2 rounded-lg">
            <FileText size={16} />
            <span>Document loaded: {documentInfo.filename}</span>
            <span className="text-gray-400">
              ({documentInfo.chunks} chunks)
            </span>
          </div>
        </div>
      )}

      {/* Input Area */}
      <div
        className={`max-w-3xl mx-auto px-4 py-3 ${
          isDragging ? 'bg-blue-900/20 border-2 border-blue-500 border-dashed rounded-lg' : ''
        }`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        <form onSubmit={handleSubmit} className="relative flex items-end gap-2">
          {/* File Upload Button */}
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="flex-shrink-0 p-2 text-gray-400 hover:text-gray-200 hover:bg-gray-700 rounded-lg transition-colors"
            title="Upload PDF"
          >
            <Paperclip size={20} />
          </button>
          
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) handleFileSelect(file);
              e.target.value = '';
            }}
            className="hidden"
          />

          {/* Text Input */}
          <div className="flex-1 relative">
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e);
                }
              }}
              placeholder={
                isDragging 
                  ? 'Drop PDF file here...' 
                  : 'Send a message...'
              }
              disabled={disabled}
              className="w-full px-4 py-3 pr-12 bg-gray-700 text-white rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              rows={1}
              style={{
                minHeight: '44px',
                maxHeight: '200px',
                height: 'auto',
              }}
              onInput={(e) => {
                e.target.style.height = 'auto';
                e.target.style.height = e.target.scrollHeight + 'px';
              }}
            />

            {/* Send Button */}
            <button
              type="submit"
              disabled={!message.trim() || disabled}
              className="absolute right-2 bottom-2 p-2 text-gray-400 hover:text-white disabled:text-gray-600 disabled:cursor-not-allowed transition-colors"
            >
              <Send size={18} />
            </button>
          </div>
        </form>

        {/* Helper Text */}
        <div className="mt-1 text-xs text-center text-gray-500">
          {isDragging ? (
            <span className="text-blue-400">Drop your PDF file here</span>
          ) : (
            <span>
              Press Enter to send, Shift+Enter for new line • Drag & drop PDF files to upload
            </span>
          )}
        </div>
      </div>
    </div>
  );
};

export default MessageInput;
