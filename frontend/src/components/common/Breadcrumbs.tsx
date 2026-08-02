import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ChevronRight, Home } from 'lucide-react';

export const Breadcrumbs: React.FC = () => {
  const location = useLocation();
  const pathnames = location.pathname.split('/').filter((x) => x);

  const formatBreadcrumb = (str: string) => {
    return str
      .replace(/-/g, ' ')
      .replace(/\b\w/g, (l) => l.toUpperCase());
  };

  return (
    <nav aria-label="Breadcrumb" className="flex items-center text-sm text-muted-foreground mb-4">
      <ol className="flex items-center space-x-2">
        <li>
          <Link
            to="/dashboard"
            className="flex items-center hover:text-primary transition-colors text-muted-foreground"
          >
            <Home className="h-4 w-4" />
            <span className="sr-only">Home</span>
          </Link>
        </li>

        {pathnames.map((value, index) => {
          const to = `/${pathnames.slice(0, index + 1).join('/')}`;
          const isLast = index === pathnames.length - 1;

          return (
            <li key={to} className="flex items-center space-x-2">
              <ChevronRight className="h-3.5 w-3.5 text-muted-foreground/60" />
              {isLast ? (
                <span className="font-medium text-foreground">{formatBreadcrumb(value)}</span>
              ) : (
                <Link to={to} className="hover:text-primary transition-colors">
                  {formatBreadcrumb(value)}
                </Link>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
};
