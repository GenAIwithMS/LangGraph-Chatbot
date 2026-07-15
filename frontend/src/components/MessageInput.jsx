import React, { useState, useRef, useEffect } from "react";
import { Send, Square, Paperclip, FileText, Loader2, Wrench, Search, FileEdit, X } from "lucide-react";
import { PromptInput, PromptInputTextarea, PromptInputActions, PromptInputAction } from "./ui/prompt-input";

const MessageInput = ({ onSendMessage, onUploadPDF, onStop, disabled, hasDocument, documentInfo, uploadingPDF }) => {
  const [message, setMessage] = useState("");
  const [isDragging, setIsDragging] = useState(false);
  const [showToolsMenu, setShowToolsMenu] = useState(false);
  const [selectedTools, setSelectedTools] = useState([]);
  const fileInputRef = useRef(null);
  const toolsMenuRef = useRef(null);

  // Keep the textarea writable while the agent is generating (submitting is
  // still blocked via `disabled`). Only lock the field while a PDF is uploading.
  const inputDisabled = uploadingPDF;

  // Close tools menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (toolsMenuRef.current && !toolsMenuRef.current.contains(event.target) &&
          !event.target.closest('button[title="Select Tools"]')) {
        setShowToolsMenu(false);
      }
    };

    if (showToolsMenu) {
      document.addEventListener("mousedown", handleClickOutside);
      return () => document.removeEventListener("mousedown", handleClickOutside);
    }
  }, [showToolsMenu]);

  const handleSubmit = () => {
    if (message.trim() && !disabled) {
      onSendMessage(message, selectedTools);
      setMessage("");
      setSelectedTools([]);
    }
  };

  const handleStop = () => {
    const prompt = onStop?.();
    if (prompt) setMessage(prompt);
  };

  // While the agent is streaming, the send button becomes a stop button.
  const showStop = disabled && !uploadingPDF;

  const handleToolSelect = (tool) => {
    if (!selectedTools.includes(tool)) {
      setSelectedTools([...selectedTools, tool]);
    }
    setShowToolsMenu(false);
  };

  const handleRemoveTool = (tool) => {
    setSelectedTools(selectedTools.filter((t) => t !== tool));
  };

  const getToolIcon = (tool) => {
    if (tool === "search") return <Search size={14} />;
    if (tool === "blogs") return <FileEdit size={14} />;
    return null;
  };

  const getToolLabel = (tool) => {
    if (tool === "search") return "Search";
    if (tool === "blogs") return "Blogs";
    return tool;
  };

  const handleFileSelect = (file) => {
    if (file && file.type === "application/pdf") {
      onUploadPDF(file);
    } else {
      alert("Please upload a PDF file");
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);

    const files = Array.from(e.dataTransfer.files);
    const pdfFile = files.find((file) => file.type === "application/pdf");

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
      <PromptInput
        value={message}
        onValueChange={setMessage}
        onSubmit={handleSubmit}
        disabled={inputDisabled}
        maxHeight={200}
        className={`max-w-3xl mx-auto ${isDragging ? "ring-2 ring-blue-500" : ""}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        {/* Attachment Chip */}
        {(uploadingPDF || (hasDocument && documentInfo)) && (
          <div className="flex items-center gap-2 bg-[#1f2026] border border-gray-600 rounded-lg px-3 py-2 text-sm mx-1 mb-1">
            {uploadingPDF ? (
              <Loader2 size={16} className="animate-spin text-blue-400" />
            ) : (
              <FileText size={16} className="text-blue-400" />
            )}
            <span className="text-gray-200 truncate">
              {uploadingPDF ? "Processing document..." : documentInfo?.filename}
            </span>
            {!uploadingPDF && <span className="text-xs text-gray-400">PDF</span>}
          </div>
        )}

        <PromptInputTextarea
          placeholder={isDragging ? "Drop PDF file here..." : "Send a message..."}
          disabled={inputDisabled}
        />

        <PromptInputActions className="flex items-center justify-between gap-2 px-1 pb-1">
          <div className="flex items-center gap-1">
            {/* File Upload */}
            <PromptInputAction tooltip="Upload PDF">
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="flex-shrink-0 p-2 text-gray-400 hover:text-gray-200 hover:bg-gray-700 rounded-lg transition-colors"
                title="Upload PDF"
              >
                <Paperclip size={20} />
              </button>
            </PromptInputAction>

            {/* Tools Menu Button */}
            <PromptInputAction tooltip="Select Tools">
              <button
                type="button"
                onClick={() => setShowToolsMenu(!showToolsMenu)}
                className="flex-shrink-0 p-1 text-gray-400 hover:text-gray-200 hover:bg-gray-600 rounded transition-colors"
                title="Select Tools"
              >
                <Wrench size={16} />
              </button>
            </PromptInputAction>

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

          {/* Send / Stop Button */}
          <PromptInputAction tooltip={showStop ? "Stop generating" : "Send message"}>
            {showStop ? (
              <button
                type="button"
                onClick={handleStop}
                className="p-2 text-red-400 hover:text-red-300 hover:bg-gray-700 rounded-lg transition-colors"
                title="Stop generating"
              >
                <Square size={18} />
              </button>
            ) : (
              <button
                type="button"
                onClick={handleSubmit}
                disabled={!message.trim() || disabled}
                className="p-2 text-gray-400 hover:text-white disabled:text-gray-600 disabled:cursor-not-allowed transition-colors"
              >
                <Send size={18} />
              </button>
            )}
          </PromptInputAction>
        </PromptInputActions>

        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) handleFileSelect(file);
            e.target.value = "";
          }}
          className="hidden"
        />

        {/* Tools Dropdown Menu */}
        {showToolsMenu && (
          <div
            ref={toolsMenuRef}
            className="absolute bottom-full left-4 mb-2 w-32 bg-gray-800 rounded-lg shadow-lg z-50 py-1 border border-gray-700"
          >
            <button
              onClick={() => handleToolSelect("search")}
              disabled={selectedTools.includes("search")}
              className="w-full flex items-center gap-2 px-3 py-1.5 text-xs hover:bg-gray-700 text-left disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Search size={14} className="text-blue-400" />
              <span className="text-gray-200">Search</span>
            </button>
            <button
              onClick={() => handleToolSelect("blogs")}
              disabled={selectedTools.includes("blogs")}
              className="w-full flex items-center gap-2 px-3 py-1.5 text-xs hover:bg-gray-700 text-left disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <FileEdit size={14} className="text-purple-400" />
              <span className="text-gray-200">Blogs</span>
            </button>
          </div>
        )}
      </PromptInput>

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
  );
};

export default MessageInput;
