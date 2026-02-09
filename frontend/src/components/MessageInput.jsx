import React, { useState, useRef, useEffect } from 'react';
import { Send, Paperclip, FileText, Loader2, Wrench, Search, FileEdit, X } from 'lucide-react';

const MessageInput = ({ onSendMessage, onUploadPDF, disabled, hasDocument, documentInfo, uploadingPDF }) => {
  const [message, setMessage] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const [showToolsMenu, setShowToolsMenu] = useState(false);
  const [selectedTools, setSelectedTools] = useState([]);
  const fileInputRef = useRef(null);
  const toolsMenuRef = useRef(null);

  // Close tools menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (toolsMenuRef.current && !toolsMenuRef.current.contains(event.target) && 
          !event.target.closest('button[title="Select Tools"]')) {
        setShowToolsMenu(false);
      }
    };

    if (showToolsMenu) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [showToolsMenu]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSendMessage(message, selectedTools);
      setMessage('');
      setSelectedTools([]);
    }
  };

  const handleToolSelect = (tool) => {
    if (!selectedTools.includes(tool)) {
      setSelectedTools([...selectedTools, tool]);
    }
    setShowToolsMenu(false);
  };

  const handleRemoveTool = (tool) => {
    setSelectedTools(selectedTools.filter(t => t !== tool));
  };

  const getToolIcon = (tool) => {
    switch(tool) {
      case 'search':
        return <Search size={14} />;
      case 'blogs':
        return <FileEdit size={14} />;
      default:
        return null;
    }
  };

  const getToolLabel = (tool) => {
    switch(tool) {
      case 'search':
        return 'Search';
      case 'blogs':
        return 'Blogs';
      default:
        return tool;
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
      {/* Input Area */}
      <div
        className={`max-w-3xl mx-auto px-4 py-3 ${
          isDragging ? 'bg-blue-900/20 border-2 border-blue-500 border-dashed rounded-lg' : ''
        }`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        <form onSubmit={handleSubmit} className="relative flex flex-col gap-2">
          {/* Attachment Chip */}
          {(uploadingPDF || (hasDocument && documentInfo)) && (
            <div className="flex items-center gap-2 bg-[#1f2026] border border-gray-600 rounded-lg px-3 py-2 text-sm">
              {uploadingPDF ? (
                <Loader2 size={16} className="animate-spin text-blue-400" />
              ) : (
                <FileText size={16} className="text-blue-400" />
              )}
              <span className="text-gray-200 truncate">
                {uploadingPDF ? 'Processing document...' : documentInfo?.filename}
              </span>
              {!uploadingPDF && (
                <span className="text-xs text-gray-400">PDF</span>
              )}
            </div>
          )}

          <div className="relative flex items-end gap-2">
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

            {/* Text Input with Tools Inside */}
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
                className="w-full px-4 py-3 pb-10 pr-12 bg-gray-700 text-white rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
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

              {/* Tools Section - Inside Input */}
              <div className="absolute bottom-2 left-2 flex items-center gap-1">
                {/* Tools Menu Button */}
                <div className="relative">
                  <button
                    type="button"
                    onClick={() => setShowToolsMenu(!showToolsMenu)}
                    className="flex-shrink-0 p-1 text-gray-400 hover:text-gray-200 hover:bg-gray-600 rounded transition-colors"
                    title="Select Tools"
                  >
                    <Wrench size={16} />
                  </button>

                  {/* Tools Dropdown Menu */}
                  {showToolsMenu && (
                    <div 
                      ref={toolsMenuRef}
                      className="absolute bottom-full left-0 mb-2 w-32 bg-gray-800 rounded-lg shadow-lg z-50 py-1 border border-gray-700"
                    >
                      <button
                        onClick={() => handleToolSelect('search')}
                        disabled={selectedTools.includes('search')}
                        className="w-full flex items-center gap-2 px-3 py-1.5 text-xs hover:bg-gray-700 text-left disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <Search size={14} className="text-blue-400" />
                        <span className="text-gray-200">Search</span>
                      </button>
                      <button
                        onClick={() => handleToolSelect('blogs')}
                        disabled={selectedTools.includes('blogs')}
                        className="w-full flex items-center gap-2 px-3 py-1.5 text-xs hover:bg-gray-700 text-left disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <FileEdit size={14} className="text-purple-400" />
                        <span className="text-gray-200">Blogs</span>
                      </button>
                    </div>
                  )}
                </div>

                {/* Selected Tools Chips */}
                {selectedTools.map((tool) => (
                  <div
                    key={tool}
                    className="group flex items-center gap-1 bg-gray-600 border border-gray-500 rounded px-1.5 py-0.5 text-xs"
                  >
                    {getToolIcon(tool)}
                    <span className="text-gray-200">{getToolLabel(tool)}</span>
                    <button
                      onClick={() => handleRemoveTool(tool)}
                      className="opacity-0 group-hover:opacity-100 p-0.5 hover:bg-gray-500 rounded transition-all"
                      title="Remove tool"
                    >
                      <X size={10} className="text-gray-300" />
                    </button>
                  </div>
                ))}
              </div>

              {/* Send Button */}
              <button
                type="submit"
                disabled={!message.trim() || disabled}
                className="absolute right-2 bottom-2 p-2 text-gray-400 hover:text-white disabled:text-gray-600 disabled:cursor-not-allowed transition-colors"
              >
                <Send size={18} />
              </button>
            </div>
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
