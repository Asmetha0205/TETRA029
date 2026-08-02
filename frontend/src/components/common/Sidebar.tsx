import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  UploadCloud,
  Scale,
  Sparkles,
  MapPin,
  Network,
  TrendingUp,
  FileText,
  ChevronLeft,
  ChevronRight,
  ShieldCheck,
} from 'lucide-react';
import { useAppStore } from '../../app/store';

const iconMap: Record<string, React.FC<{ className?: string }>> = {
  LayoutDashboard,
  UploadCloud,
  Scale,
  Sparkles,
  MapPin,
  Network,
  TrendingUp,
  FileText,
};

const navItems = [
  { path: '/dashboard', label: 'Dashboard', iconName: 'LayoutDashboard' },
  { path: '/upload', label: 'Upload PDF', iconName: 'UploadCloud' },
  { path: '/gap-analysis', label: 'Gap Analysis', iconName: 'Scale' },
  { path: '/recommendations', label: 'Recommendations', iconName: 'Sparkles' },
  { path: '/learning-path', label: 'Learning Path', iconName: 'MapPin' },
  { path: '/knowledge-graph', label: 'Knowledge Graph', iconName: 'Network' },
  { path: '/industry-trends', label: 'Industry Trends', iconName: 'TrendingUp' },
  { path: '/report', label: 'Executive Report', iconName: 'FileText' },
];

export const Sidebar: React.FC = () => {
  const { sidebarCollapsed, toggleSidebar } = useAppStore();

  return (
    <aside
      className={`relative z-30 flex flex-col border-r border-border/40 bg-card/60 backdrop-blur-xl transition-all duration-300 ${
        sidebarCollapsed ? 'w-16' : 'w-64'
      }`}
    >
      {/* Sidebar Top Header & Collapse Button */}
      <div className="flex h-12 items-center justify-between px-3 border-b border-border/30">
        {!sidebarCollapsed && (
          <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground px-2">
            Navigation Menu
          </span>
        )}
        <button
          onClick={toggleSidebar}
          type="button"
          className="ml-auto rounded-lg p-1.5 text-muted-foreground hover:bg-secondary hover:text-foreground transition-colors"
          title={sidebarCollapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
        >
          {sidebarCollapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        </button>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 space-y-1.5 p-2 overflow-y-auto">
        {navItems.map((item) => {
          const IconComponent = iconMap[item.iconName] || LayoutDashboard;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `group relative flex items-center rounded-xl px-3 py-2.5 text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-primary/10 text-primary font-semibold shadow-sm'
                    : 'text-muted-foreground hover:bg-secondary/80 hover:text-foreground'
                }`
              }
            >
              {({ isActive }) => (
                <>
                  {isActive && (
                    <span className="absolute left-0 top-1/2 -translate-y-1/2 h-6 w-1 rounded-r-full bg-primary" />
                  )}
                  <IconComponent
                    className={`h-5 w-5 shrink-0 transition-transform group-hover:scale-110 ${
                      sidebarCollapsed ? 'mx-auto' : 'mr-3'
                    } ${isActive ? 'text-primary' : 'text-muted-foreground group-hover:text-foreground'}`}
                  />
                  {!sidebarCollapsed && <span className="truncate">{item.label}</span>}
                </>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* Footer Info Widget */}
      {!sidebarCollapsed && (
        <div className="p-3 border-t border-border/30 bg-secondary/30">
          <div className="flex items-center space-x-2 text-xs text-muted-foreground">
            <ShieldCheck className="h-4 w-4 text-emerald-500 shrink-0" />
            <div className="truncate">
              <p className="font-semibold text-foreground">Neo4j & Gemini 1.5</p>
              <p className="text-[10px]">Taxonomy Match Active</p>
            </div>
          </div>
        </div>
      )}
    </aside>
  );
};
