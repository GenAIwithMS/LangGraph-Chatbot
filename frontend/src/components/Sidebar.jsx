import React, { useState, useRef, useEffect, useMemo } from 'react';
import {
  Plus,
  Edit2,
  Trash2,
  Menu,
  X,
  MoreVertical,
  Search as SearchIcon,
  PanelLeftClose,
  PanelLeftOpen,
} from 'lucide-react';

const Sidebar = ({
  threads,
  currentThreadId,
  onThreadSelect,
  onNewThread,
  onThreadRename,
  onThreadDelete,
  isSidebarOpen,
  toggleSidebar,
  isCollapsed,
  onToggleCollapse,
}) => {
  const [editingThreadId, setEditingThreadId] = useState(null);
  const [editTitle, setEditTitle] = useState('');
  const [openMenuId, setOpenMenuId] = useState(null);
  const [query, setQuery] = useState('');
  const [activeIndex, setActiveIndex] = useState(-1);
  const searchInputRef = useRef(null);

  const filteredThreads = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return threads;
    return threads.filter((t) =>
      (t.title || 'New Chat').toLowerCase().includes(q)
    );
  }, [threads, query]);

  const handleRename = (threadId, currentTitle) => {
    setEditingThreadId(threadId);
    setEditTitle(currentTitle);
    setOpenMenuId(null);
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

  const openChat = (thread) => {
    if (!thread) return;
    onThreadSelect(thread.thread_id);
    if (window.innerWidth < 1024) toggleSidebar();
  };

  const clearSearch = () => {
    setQuery('');
    setActiveIndex(-1);
    searchInputRef.current?.focus();
  };

  const handleSearchKeyDown = (e) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setActiveIndex((i) => (filteredThreads.length ? (i + 1) % filteredThreads.length : -1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setActiveIndex((i) =>
        filteredThreads.length ? (i - 1 + filteredThreads.length) % filteredThreads.length : -1
      );
    } else if (e.key === 'Enter') {
      e.preventDefault();
      const target = filteredThreads[activeIndex] || filteredThreads[0];
      if (target) openChat(target);
    } else if (e.key === 'Escape') {
      e.preventDefault();
      if (query) {
        clearSearch();
      } else {
        searchInputRef.current?.blur();
      }
    }
  };

  // Keep active index in range when the filtered list changes
  useEffect(() => {
    setActiveIndex((i) => (i >= filteredThreads.length ? filteredThreads.length - 1 : i));
  }, [filteredThreads.length]);

  // Close thread dropdown menus when clicking elsewhere
  useEffect(() => {
    if (!openMenuId) return;
    const handle = (e) => {
      if (!e.target.closest('[data-thread-menu]')) {
        setOpenMenuId(null);
      }
    };
    document.addEventListener('mousedown', handle);
    return () => document.removeEventListener('mousedown', handle);
  }, [openMenuId]);

  // Collapsed (desktop rail) view — ChatGPT-like icon-only sidebar
  if (isCollapsed) {
    return (
      <>
        <button
          onClick={toggleSidebar}
          aria-label="Open sidebar"
          className={`
            lg:hidden fixed top-4 left-4 z-50 p-2 rounded-xl bg-sidebar-bg text-white shadow-lg
            transition-opacity duration-300 ease-in-out
            ${isSidebarOpen ? 'opacity-0 pointer-events-none' : 'opacity-100'}
          `}
        >
          <Menu size={24} />
        </button>

        <div
          className={`
            fixed lg:static inset-y-0 left-0 z-40
            w-[60px] bg-sidebar-bg text-white
            transform transition-transform duration-300 ease-in-out
            ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
            flex flex-col items-center py-3
          `}
        >
          <button
            onClick={onNewThread}
            title="New chat"
            className="flex items-center justify-center w-10 h-10 rounded-xl hover:bg-gray-700 transition-colors"
          >
            <Plus size={20} />
          </button>
          <button
            onClick={() => {
              onToggleCollapse?.();
              setTimeout(() => searchInputRef.current?.focus(), 50);
            }}
            title="Expand sidebar"
            className="flex items-center justify-center w-10 h-10 mt-1 rounded-xl hover:bg-gray-700 transition-colors"
          >
            <PanelLeftOpen size={20} />
          </button>
        </div>

        <div
          className={`
            lg:hidden fixed inset-0 bg-black bg-opacity-50 z-30
            transition-opacity duration-300 ease-in-out
            ${isSidebarOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'}
          `}
          onClick={toggleSidebar}
        />
      </>
    );
  }

  return (
    <>
      {/* Mobile menu button — kept clear of the chat content, fades with the drawer */}
      <button
        onClick={toggleSidebar}
        aria-label={isSidebarOpen ? 'Close sidebar' : 'Open sidebar'}
        className={`
          lg:hidden fixed top-4 left-4 z-50 p-2 rounded-xl bg-sidebar-bg text-white shadow-lg
          transition-opacity duration-300 ease-in-out
          ${isSidebarOpen ? 'opacity-0 pointer-events-none' : 'opacity-100'}
        `}
      >
        <Menu size={24} />
      </button>

      {/* Sidebar */}
      <div
        className={`
          fixed lg:static inset-y-0 left-0 z-40
          w-64 bg-sidebar-bg text-white
          transform transition-transform duration-300 ease-in-out will-change-transform
          ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
          flex flex-col
        `}
      >
        {/* Mobile-only close button — placed inside the drawer, away from chat */}
        <button
          onClick={toggleSidebar}
          aria-label="Close sidebar"
          className="lg:hidden absolute top-3 right-3 z-50 p-2 rounded-xl text-gray-300 hover:text-white hover:bg-gray-700 transition-colors"
        >
          <X size={20} />
        </button>

        {/* Top: New chat + collapse */}
        <div className="flex items-center gap-1 px-2 pt-2">
          <button
            onClick={onNewThread}
            className="group flex items-center gap-2.5 flex-1 px-3 py-2.5 rounded-xl hover:bg-gray-700/80 transition-colors text-left"
            title="New chat"
          >
            <span className="flex items-center justify-center w-5 h-5 shrink-0">
              <Plus size={18} />
            </span>
            <span className="text-sm font-medium">New chat</span>
          </button>
          <button
            onClick={() => onToggleCollapse?.()}
            title="Close sidebar"
            className="hidden lg:flex items-center justify-center w-9 h-9 rounded-lg text-gray-400 hover:text-white hover:bg-gray-700 transition-colors"
          >
            <PanelLeftClose size={18} />
          </button>
        </div>

        {/* Search chats */}
        <div className="px-2 pt-2 pb-1">
          <div
            className={`
              flex items-center gap-2 px-3 py-2 rounded-xl
              bg-transparent border border-transparent
              focus-within:bg-gray-700/60 focus-within:border-gray-600
              transition-colors
            `}
          >
            <SearchIcon size={16} className="text-gray-400 shrink-0" />
            <input
              ref={searchInputRef}
              type="text"
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                setActiveIndex(-1);
              }}
              onKeyDown={handleSearchKeyDown}
              placeholder="Search chats"
              aria-label="Search chats"
              className="w-full bg-transparent text-sm text-gray-100 placeholder-gray-500 outline-none"
            />
            {query && (
              <button
                onClick={clearSearch}
                title="Clear search"
                className="shrink-0 p-0.5 text-gray-400 hover:text-white rounded transition-colors"
              >
                <X size={14} />
              </button>
            )}
          </div>
        </div>

        {/* Chat history */}
        <div className="flex-1 overflow-y-auto px-2 py-2 space-y-0.5 thin-scroll">
          {filteredThreads.length === 0 ? (
            <div className="px-3 py-6 text-center text-xs text-gray-500">
              {query ? 'No chats found' : 'No chats yet'}
            </div>
          ) : (
            filteredThreads.map((thread, index) => {
              const isActive = currentThreadId === thread.thread_id;
              const isEditing = editingThreadId === thread.thread_id;
              return (
                <div
                  key={thread.thread_id}
                  data-thread-menu
                  className={`
                    group relative flex items-center gap-2 px-3 py-2 rounded-xl cursor-pointer
                    transition-colors duration-100
                    ${isActive ? 'bg-gray-700/90' : 'hover:bg-gray-700/60'}
                    ${activeIndex === index && query ? 'ring-1 ring-white/30' : ''}
                  `}
                  onClick={() => {
                    if (isEditing) return;
                    openChat(thread);
                  }}
                >
                  {isEditing ? (
                    <input
                      type="text"
                      value={editTitle}
                      onChange={(e) => setEditTitle(e.target.value)}
                      onBlur={() => handleSaveRename(thread.thread_id)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') handleSaveRename(thread.thread_id);
                        if (e.key === 'Escape') {
                          setEditingThreadId(null);
                          setEditTitle('');
                        }
                      }}
                      className="w-full bg-gray-600 px-2 py-1 rounded-lg text-sm text-white outline-none focus:ring-2 focus:ring-blue-500"
                      autoFocus
                      onClick={(e) => e.stopPropagation()}
                    />
                  ) : (
                    <>
                      <span className="text-sm text-gray-100 truncate flex-1 min-w-0">
                        {thread.title || 'New Chat'}
                      </span>
                      <button
                        onClick={(e) => toggleMenu(e, thread.thread_id)}
                        aria-label="Chat options"
                        className={`
                          shrink-0 p-1 rounded-md text-gray-300 hover:bg-gray-600 opacity-0
                          group-hover:opacity-100 focus:opacity-100 transition-opacity
                          ${openMenuId === thread.thread_id ? 'opacity-100' : ''}
                        `}
                      >
                        <MoreVertical size={15} />
                      </button>

                      {openMenuId === thread.thread_id && (
                        <div
                          className="absolute right-2 top-full mt-1 w-36 bg-gray-800 rounded-xl shadow-xl shadow-black/40 z-50 py-1 border border-gray-700/70 animate-scale-in"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleRename(thread.thread_id, thread.title);
                            }}
                            className="w-full flex items-center gap-2.5 px-3 py-2 text-sm text-gray-200 hover:bg-gray-700 rounded-lg mx-1"
                          >
                            <Edit2 size={14} />
                            <span>Rename</span>
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDelete(thread.thread_id);
                            }}
                            className="w-full flex items-center gap-2.5 px-3 py-2 text-sm text-red-400 hover:bg-gray-700 rounded-lg mx-1"
                          >
                            <Trash2 size={14} />
                            <span>Delete</span>
                          </button>
                        </div>
                      )}
                    </>
                  )}
                </div>
              );
            })
          )}
        </div>

        {/* Footer */}
        <div className="px-3 py-3 border-t border-gray-700/60">
          <div className="text-xs text-gray-500 text-center">
            AI Chatbot with RAG
          </div>
        </div>
      </div>

      {/* Overlay for mobile — fades in/out with the drawer */}
      <div
        className={`
          lg:hidden fixed inset-0 bg-black bg-opacity-50 z-30
          transition-opacity duration-300 ease-in-out
          ${isSidebarOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'}
        `}
        onClick={toggleSidebar}
      />
    </>
  );
};

export default Sidebar;
