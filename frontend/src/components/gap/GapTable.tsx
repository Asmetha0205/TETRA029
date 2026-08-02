import React, { useState } from 'react';
import { ExternalLink, TrendingUp, TrendingDown, Minus, ArrowUpDown } from 'lucide-react';
import { SkillGapItem } from '../../types/api';
import { formatPriorityBadge } from '../../utils/formatters';

interface GapTableProps {
  items: SkillGapItem[];
  onSelectEvidence: (item: SkillGapItem) => void;
}

export const GapTable: React.FC<GapTableProps> = ({ items, onSelectEvidence }) => {
  const [sortField, setSortField] = useState<'similarity' | 'industry_demand_score'>('similarity');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  const handleSort = (field: 'similarity' | 'industry_demand_score') => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('desc');
    }
  };

  const sortedItems = [...items].sort((a, b) => {
    const mult = sortOrder === 'asc' ? 1 : -1;
    return (a[sortField] - b[sortField]) * mult;
  });

  return (
    <div className="w-full overflow-hidden rounded-2xl border border-border/60 bg-card shadow-sm">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead className="border-b border-border/60 bg-secondary/50 font-bold uppercase tracking-wider text-muted-foreground">
            <tr>
              <th className="px-4 py-3.5">Matched Industry Skill</th>
              <th className="px-4 py-3.5">Academic Syllabus Concept</th>
              <th className="px-4 py-3.5 cursor-pointer hover:text-foreground" onClick={() => handleSort('similarity')}>
                <div className="flex items-center gap-1">
                  <span>Similarity</span>
                  <ArrowUpDown className="h-3 w-3" />
                </div>
              </th>
              <th className="px-4 py-3.5">Priority</th>
              <th className="px-4 py-3.5">Trend</th>
              <th className="px-4 py-3.5 cursor-pointer hover:text-foreground" onClick={() => handleSort('industry_demand_score')}>
                <div className="flex items-center gap-1">
                  <span>Demand Score</span>
                  <ArrowUpDown className="h-3 w-3" />
                </div>
              </th>
              <th className="px-4 py-3.5 text-right">Evidence Citation</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border/40 font-medium">
            {sortedItems.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-4 py-8 text-center text-muted-foreground">
                  No matching skill gaps found.
                </td>
              </tr>
            ) : (
              sortedItems.map((item) => {
                const priorityStyle = formatPriorityBadge(item.priority);
                return (
                  <tr
                    key={item.id}
                    onClick={() => onSelectEvidence(item)}
                    className="hover:bg-secondary/40 transition-colors cursor-pointer group"
                  >
                    <td className="px-4 py-3.5">
                      <div className="font-bold text-foreground group-hover:text-primary transition-colors">
                        {item.matched_industry_skill}
                      </div>
                      <span className="text-[10px] text-muted-foreground">{item.category}</span>
                    </td>
                    <td className="px-4 py-3.5 text-muted-foreground max-w-[200px] truncate">
                      {item.academic_skill}
                    </td>
                    <td className="px-4 py-3.5">
                      <div className="flex items-center space-x-2">
                        <span className="font-extrabold text-foreground">{item.similarity}%</span>
                        <div className="w-12 h-1.5 rounded-full bg-secondary overflow-hidden">
                          <div
                            className={`h-full ${
                              item.similarity >= 80
                                ? 'bg-emerald-500'
                                : item.similarity >= 60
                                ? 'bg-amber-500'
                                : 'bg-rose-500'
                            }`}
                            style={{ width: `${item.similarity}%` }}
                          />
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3.5">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold border ${priorityStyle.color}`}>
                        {priorityStyle.label}
                      </span>
                    </td>
                    <td className="px-4 py-3.5">
                      <div className="flex items-center space-x-1 font-bold text-amber-500">
                        {item.trend === 'RISING' ? (
                          <TrendingUp className="h-3.5 w-3.5 text-emerald-500" />
                        ) : item.trend === 'DECLINING' ? (
                          <TrendingDown className="h-3.5 w-3.5 text-rose-500" />
                        ) : (
                          <Minus className="h-3.5 w-3.5 text-muted-foreground" />
                        )}
                        <span className="text-[11px]">{item.trend}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3.5 font-extrabold text-foreground">
                      {item.industry_demand_score}/100
                    </td>
                    <td className="px-4 py-3.5 text-right">
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectEvidence(item);
                        }}
                        className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-lg bg-secondary text-foreground text-[11px] font-medium hover:bg-primary hover:text-white transition-all"
                      >
                        <span>View Citation</span>
                        <ExternalLink className="h-3 w-3" />
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
