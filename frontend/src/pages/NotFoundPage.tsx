import React from 'react';
import { Link } from 'react-router-dom';
import { FileQuestion, Home } from 'lucide-react';
import { PageTransition } from '../components/animation/PageTransition';

export const NotFoundPage: React.FC = () => {
  return (
    <PageTransition>
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-center p-6 space-y-4">
        <div className="flex h-20 w-20 items-center justify-center rounded-3xl bg-primary/10 text-primary mb-2">
          <FileQuestion className="h-10 w-10" />
        </div>
        <h1 className="text-3xl font-extrabold text-foreground tracking-tight">404 - Page Not Found</h1>
        <p className="text-xs text-muted-foreground max-w-sm">
          The curriculum alignment page you requested does not exist or has been relocated.
        </p>
        <Link
          to="/dashboard"
          className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-primary text-primary-foreground font-bold text-xs shadow hover:opacity-90 transition-opacity"
        >
          <Home className="h-4 w-4" />
          <span>Return to Dashboard</span>
        </Link>
      </div>
    </PageTransition>
  );
};
