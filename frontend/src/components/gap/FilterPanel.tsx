import React from 'react';
import { Filter } from 'lucide-react';

interface FilterPanelProps {
  categories: string[];
  selectedCategory: string;
  onSelectCategory: (cat: string) => void;
  priorities: string[];
  selectedPriority: string;
  onSelectPriority: (pri: string) => void;
}

export const FilterPanel: React.FC<FilterPanelProps> = ({
  categories,
  selectedCategory,
  onSelectCategory,
  priorities,
  selectedPriority,
  onSelectPriority,
}) => {
  return (
    <div className="flex flex-wrap items-center gap-3 bg-card p-3 rounded-2xl border border-border/50 shadow-sm">
      <div className="flex items-center space-x-1.5 text-xs font-semibold text-muted-foreground mr-1">
        <Filter className="h-3.5 w-3.5" />
        <span>Filters:</span>
      </div>

      {/* Category Pills */}
      <div className="flex flex-wrap items-center gap-1.5">
        <button
          onClick={() => onSelectCategory('ALL')}
          className={`px-3 py-1 rounded-xl text-xs font-medium transition-all ${
            selectedCategory === 'ALL'
              ? 'bg-primary text-primary-foreground shadow-sm'
              : 'bg-secondary/60 text-muted-foreground hover:bg-secondary hover:text-foreground'
          }`}
        >
          All Categories
        </button>
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => onSelectCategory(cat)}
            className={`px-3 py-1 rounded-xl text-xs font-medium transition-all ${
              selectedCategory === cat
                ? 'bg-primary text-primary-foreground shadow-sm'
                : 'bg-secondary/60 text-muted-foreground hover:bg-secondary hover:text-foreground'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      <div className="h-4 w-px bg-border/60 mx-1 hidden md:block" />

      {/* Priority Select */}
      <div className="flex items-center space-x-1.5">
        <span className="text-[11px] font-medium text-muted-foreground">Priority:</span>
        <select
          value={selectedPriority}
          onChange={(e) => onSelectPriority(e.target.value)}
          className="h-8 rounded-xl border border-input bg-secondary/40 px-2.5 text-xs text-foreground focus:ring-2 focus:ring-primary/40 focus:outline-none"
        >
          <option value="ALL">All Priorities</option>
          {priorities.map((pri) => (
            <option key={pri} value={pri}>
              {pri}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
};
