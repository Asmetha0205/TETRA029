import React from 'react';
import { FileQuestion, UploadCloud } from 'lucide-react';
import { Link } from 'react-router-dom';

interface EmptyStateProps {
  title?: string;
  description?: string;
  actionText?: string;
  actionPath?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title = 'No Analysis Data Found',
  description = 'Upload a Computer Science curriculum PDF file to generate live alignment intelligence, skill gaps, and learning roadmaps.',
  actionText = 'Upload Curriculum PDF',
  actionPath = '/upload',
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center border-2 border-dashed border-border/60 rounded-3xl bg-card/40 my-8">
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-secondary/80 text-muted-foreground mb-4">
        <FileQuestion className="h-8 w-8" />
      </div>
      <h3 className="text-lg font-bold text-foreground mb-2">{title}</h3>
      <p className="text-sm text-muted-foreground max-w-md mb-6">{description}</p>
      {actionPath && (
        <Link
          to={actionPath}
          className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-primary text-primary-foreground font-semibold text-sm shadow-md hover:opacity-95 hover:scale-105 transition-all"
        >
          <UploadCloud className="h-4 w-4" />
          <span>{actionText}</span>
        </Link>
      )}
    </div>
  );
};
