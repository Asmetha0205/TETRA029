import React from 'react';

export const Footer: React.FC = () => {
  return (
    <footer className="w-full border-t border-border/40 bg-card/40 py-4 px-6 text-xs text-muted-foreground transition-colors">
      <div className="flex flex-col sm:flex-row items-center justify-between gap-2 max-w-7xl mx-auto">
        <div className="flex items-center space-x-2">
          <span className="font-semibold text-foreground">CurricuAlign AI</span>
          <span>© 2026 Autonomous AI SaaS. All rights reserved.</span>
        </div>
        <div className="flex items-center space-x-4">
          <span className="hover:text-foreground cursor-pointer transition-colors">Academic Engine v1.0</span>
          <span>•</span>
          <span className="hover:text-foreground cursor-pointer transition-colors">Industry Intelligence v1.0</span>
          <span>•</span>
          <span className="hover:text-foreground cursor-pointer transition-colors">Recommendation Graph</span>
        </div>
      </div>
    </footer>
  );
};
