import React from 'react';
import { X, Loader2, CheckCircle, Circle } from 'lucide-react';

const ProgressSidebar = ({ streamingProgress, onClose }) => {
  if (!streamingProgress || !streamingProgress.isStreaming) {
    return null;
  }

  return (
    <div className="w-80 border-l border-gray-700 bg-sidebar-bg flex flex-col h-full">
      <div className="flex items-center justify-between p-4 border-b border-gray-700">
        <div className="flex items-center gap-2">
          <Loader2 size={18} className="animate-spin text-blue-400" />
          <h3 className="font-semibold text-gray-200">
            {streamingProgress.toolName === 'blogs' ? 'Writing Blog' : 'Processing'}
          </h3>
        </div>
        <button
          onClick={onClose}
          className="p-1 hover:bg-gray-700 rounded transition-colors text-gray-400 hover:text-gray-200"
          title="Close"
        >
          <X size={18} />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        <div className="space-y-4">
          {streamingProgress.steps && streamingProgress.steps.map((step, index) => (
            <div key={index} className="flex items-start gap-3">
              <div className="flex-shrink-0 mt-0.5">
                {step.status === 'completed' ? (
                  <CheckCircle size={20} className="text-green-400" />
                ) : step.status === 'in-progress' ? (
                  <Loader2 size={20} className="animate-spin text-blue-400" />
                ) : (
                  <Circle size={20} className="text-gray-600" />
                )}
              </div>

              <div className="flex-1">
                <div className={`text-sm ${
                  step.status === 'completed' 
                    ? 'text-gray-400' 
                    : step.status === 'in-progress'
                    ? 'text-gray-200 font-medium'
                    : 'text-gray-600'
                }`}>
                  {step.label}
                </div>
                
                {step.details && (
                  <div className="mt-1 text-xs text-gray-500">
                    {step.details}
                  </div>
                )}

                {step.status === 'in-progress' && (
                  <div className="mt-2 w-full bg-gray-700 rounded-full h-1.5">
                    <div className="bg-blue-500 h-1.5 rounded-full animate-pulse" style={{ width: '60%' }}></div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="p-4 border-t border-gray-700">
        <div className="text-xs text-gray-500 text-center">
          This may take a few moments...
        </div>
      </div>
    </div>
  );
};

export default ProgressSidebar;
