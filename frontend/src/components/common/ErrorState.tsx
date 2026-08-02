import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface ErrorStateProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = 'API Execution Warning',
  message = 'Failed to connect to the unified orchestration backend server. Ensure FastAPI is running on http://localhost:8000.',
  onRetry,
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center rounded-2xl bg-destructive/10 border border-destructive/20 my-6">
      <AlertTriangle className="h-10 w-10 text-destructive mb-3 animate-bounce" />
      <h4 className="text-base font-bold text-destructive mb-1">{title}</h4>
      <p className="text-xs text-muted-foreground max-w-md mb-4">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="inline-flex items-center space-x-2 px-4 py-2 rounded-xl bg-destructive text-destructive-foreground font-medium text-xs shadow-md hover:opacity-90 transition-all"
        >
          <RefreshCw className="h-3.5 w-3.5" />
          <span>Retry Operation</span>
        </button>
      )}
    </div>
  );
};
