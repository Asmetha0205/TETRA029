import React from 'react';
import { Loader2, Sparkles } from 'lucide-react';

interface LoadingOverlayProps {
  message?: string;
  subtext?: string;
}

export const LoadingOverlay: React.FC<LoadingOverlayProps> = ({
  message = 'Analyzing Curriculum Document...',
  subtext = 'Running vector embedding similarity and Neo4j graph alignment',
}) => {
  return (
    <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-background/80 backdrop-blur-md">
      <div className="flex flex-col items-center p-8 rounded-3xl bg-card border border-border shadow-2xl max-w-sm text-center">
        <div className="relative mb-4 flex items-center justify-center">
          <div className="h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center">
            <Sparkles className="h-8 w-8 text-primary animate-pulse" />
          </div>
          <Loader2 className="absolute h-20 w-20 text-primary animate-spin opacity-80" />
        </div>
        <h3 className="text-lg font-bold text-foreground mb-1">{message}</h3>
        <p className="text-xs text-muted-foreground">{subtext}</p>
      </div>
    </div>
  );
};
