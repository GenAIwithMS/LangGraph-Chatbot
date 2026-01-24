import React, { useState } from 'react';
import { 
  Plus, 
  Edit2, 
  Trash2,
  Menu,
  X,
  MoreVertical
} from 'lucide-react';

const Sidebar = ({ 
  threads, 
  currentThreadId, 
  onThreadSelect, 
  onNewThread,
  onThreadRename,
  onThreadDelete,
  isSidebarOpen,
  toggleSidebar
}) => {
  const [editingThreadId, setEditingThreadId] = useState(null);
  const [editTitle, setEditTitle] = useState('');
  const [openMenuId, setOpenMenuId] = useState(null);

  const handleRename = (threadId, currentTitle) => {
    setEditingThreadId(threadId);
    setEditTitle(currentTitle);
  };

  const handleSaveRename = (threadId) => {
    if (editTitle.trim()) {
      onThreadRename(threadId, editTitle);
    }
    setEditingThreadId(null);
    setEditTitle('');
  };

  const handleDelete = (threadId) => {
    if (onThreadDelete) {
      onThreadDelete(threadId);
    }
    setOpenMenuId(null);
  };

  const toggleMenu = (e, threadId) => {
    e.stopPropagation();
    setOpenMenuId(openMenuId === threadId ? null : threadId);
  };

  return (
    <>
      {/* Mobile menu button */}
      <button
        onClick={toggleSidebar}
        className="lg:hidden fixed top-4 left-4 z-50 p-2 rounded-md bg-sidebar-bg text-white"
      >
        {isSidebarOpen ? <X size={24} /> : <Menu size={24} />}
      </button>

      {/* Sidebar */}
      <div
        className={`
          fixed lg:static inset-y-0 left-0 z-40
          w-64 bg-sidebar-bg text-white
          transform transition-transform duration-300 ease-in-out
          ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
          flex flex-col
        `}
      >
        {/* New Chat Button */}
        <div className="p-3 border-b border-gray-700">
          <button
            onClick={onNewThread}
            className="w-full flex items-center gap-3 px-3 py-3 rounded-md hover:bg-gray-700 transition-colors"
          >
            <Plus size={18} />
            <span className="text-sm font-medium">New chat</span>
          </button>
        </div>

        {/* Thread List */}
        <div className="flex-1 overflow-y-auto py-2">
          {threads.map((thread) => (
            <div
              key={thread.thread_id}
              className={`
                group relative px-3 py-2 mx-2 my-1 rounded-md cursor-pointer
                transition-colors
                ${currentThreadId === thread.thread_id 
                  ? 'bg-gray-700' 
                  : 'hover:bg-gray-700'
                }
              `}
              onClick={() => onThreadSelect(thread.thread_id)}
            >
              {editingThreadId === thread.thread_id ? (
                <input
                  type="text"
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                  onBlur={() => handleSaveRename(thread.thread_id)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      handleSaveRename(thread.thread_id);
                    }
                  }}
                  className="w-full bg-gray-600 px-2 py-1 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  autoFocus
                  onClick={(e) => e.stopPropagation()}
                />
              ) : (
                <div className="flex items-center gap-2">
                  <span className="text-sm truncate flex-1">
                    {thread.title || 'New Chat'}
                  </span>
                  <div className="relative">
                    <button
                      onClick={(e) => toggleMenu(e, thread.thread_id)}
                      className="opacity-0 group-hover:opacity-100 p-1 hover:bg-gray-600 rounded transition-opacity"
                    >
                      <MoreVertical size={14} />
                    </button>
                    
                    {/* Dropdown Menu */}
                    {openMenuId === thread.thread_id && (
                      <div 
                        className="absolute right-0 mt-1 w-32 bg-gray-800 rounded-md shadow-lg z-50 py-1"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleRename(thread.thread_id, thread.title);
                            setOpenMenuId(null);
                          }}
                          className="w-full flex items-center gap-2 px-3 py-2 text-sm hover:bg-gray-700 text-left"
                        >
                          <Edit2 size={14} />
                          <span>Edit</span>
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDelete(thread.thread_id);
                          }}
                          className="w-full flex items-center gap-2 px-3 py-2 text-sm hover:bg-gray-700 text-left text-red-400"
                        >
                          <Trash2 size={14} />
                          <span>Delete</span>
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="p-3 border-t border-gray-700">
          <div className="text-xs text-gray-400 text-center">
            AI Chatbot with RAG
          </div>
        </div>
      </div>

      {/* Overlay for mobile */}
      {isSidebarOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-30"
          onClick={toggleSidebar}
        />
      )}
    </>
  );
};

export default Sidebar;
