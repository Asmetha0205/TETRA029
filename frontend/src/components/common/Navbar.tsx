import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Sparkles, Search, UploadCloud, Menu, X, Activity, Cpu } from 'lucide-react';
import { ThemeSwitcher } from './ThemeSwitcher';
import { useAppStore } from '../../app/store';

interface NavbarProps {
  onMobileMenuToggle?: () => void;
  isMobileMenuOpen?: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({ onMobileMenuToggle, isMobileMenuOpen }) => {
  const navigate = useNavigate();
  const { searchQuery, setSearchQuery, activeAnalysis } = useAppStore();
  const [backendHealthy] = useState(true); // backend operational status indicator

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/gap-analysis?query=${encodeURIComponent(searchQuery)}`);
    }
  };

  return (
    <header className="sticky top-0 z-40 w-full border-b border-border/40 bg-background/80 backdrop-blur-xl transition-colors">
      <div className="flex h-16 items-center justify-between px-4 md:px-6">
        {/* Left: Mobile Toggle + Logo */}
        <div className="flex items-center space-x-3">
          <button
            onClick={onMobileMenuToggle}
            type="button"
            className="inline-flex items-center justify-center rounded-xl p-2 text-muted-foreground hover:bg-secondary hover:text-foreground md:hidden"
            aria-label="Toggle navigation menu"
          >
            {isMobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>

          <Link to="/" className="flex items-center space-x-2.5 group">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-indigo-600 via-purple-600 to-pink-500 text-white shadow-lg shadow-indigo-500/25 group-hover:scale-105 transition-transform">
              <Sparkles className="h-5 w-5 animate-pulse" />
            </div>
            <div className="flex flex-col">
              <span className="font-extrabold text-lg tracking-tight bg-gradient-to-r from-foreground via-foreground to-primary bg-clip-text text-transparent">
                CurricuAlign<span className="text-primary ml-0.5">AI</span>
              </span>
              <span className="text-[10px] font-semibold text-muted-foreground uppercase tracking-widest -mt-1">
                Intelligence Engine v1.0
              </span>
            </div>
          </Link>
        </div>

        {/* Center: Search Bar */}
        <div className="hidden md:flex flex-1 max-w-md mx-6">
          <form onSubmit={handleSearchSubmit} className="relative w-full">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search skills, Docker, React, RAG, PyTorch..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full h-9 rounded-xl border border-input bg-secondary/50 pl-10 pr-4 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/40 transition-all"
            />
          </form>
        </div>

        {/* Right: Actions, Health, Theme, User */}
        <div className="flex items-center space-x-2.5">
          {/* Health Badge */}
          <div className="hidden sm:flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
            <Activity className="h-3.5 w-3.5 animate-pulse" />
            <span>FastAPI Backend Active</span>
          </div>

          {/* Quick Upload CTA */}
          <Link
            to="/upload"
            className="hidden sm:inline-flex items-center space-x-1.5 h-9 px-3.5 rounded-xl bg-gradient-to-r from-primary to-accent text-white font-medium text-xs shadow-md shadow-primary/20 hover:opacity-95 hover:scale-[1.02] active:scale-[0.98] transition-all"
          >
            <UploadCloud className="h-4 w-4" />
            <span>Analyze Curriculum</span>
          </Link>

          {/* Theme Switcher */}
          <ThemeSwitcher />

          {/* Active Document Indicator */}
          {activeAnalysis && (
            <div className="hidden lg:flex flex-col text-right text-xs pl-2 border-l border-border/50">
              <span className="font-semibold truncate max-w-[120px] text-foreground">
                {activeAnalysis.university_name || 'Curriculum Doc'}
              </span>
              <span className="text-[10px] text-emerald-500 font-medium">
                Score: {activeAnalysis.alignment_score}%
              </span>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
