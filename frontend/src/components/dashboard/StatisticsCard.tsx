import React from 'react';
import { LucideIcon } from 'lucide-react';

interface StatisticsCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  change?: string;
  changeType?: 'positive' | 'negative' | 'neutral';
  icon: LucideIcon;
  iconBg?: string;
}

export const StatisticsCard: React.FC<StatisticsCardProps> = ({
  title,
  value,
  subtitle,
  change,
  changeType = 'positive',
  icon: Icon,
  iconBg = 'bg-primary/10 text-primary',
}) => {
  return (
    <div className="relative overflow-hidden rounded-2xl border border-border/50 bg-card p-5 shadow-sm transition-all hover:shadow-md hover:border-border">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          {title}
        </span>
        <div className={`flex h-10 w-10 items-center justify-center rounded-xl ${iconBg}`}>
          <Icon className="h-5 w-5" />
        </div>
      </div>

      <div className="flex items-baseline space-x-2">
        <h3 className="text-2xl font-extrabold tracking-tight text-foreground">{value}</h3>
        {change && (
          <span
            className={`text-xs font-medium ${
              changeType === 'positive'
                ? 'text-emerald-500'
                : changeType === 'negative'
                ? 'text-rose-500'
                : 'text-muted-foreground'
            }`}
          >
            {change}
          </span>
        )}
      </div>

      {subtitle && <p className="text-xs text-muted-foreground mt-1">{subtitle}</p>}
    </div>
  );
};
