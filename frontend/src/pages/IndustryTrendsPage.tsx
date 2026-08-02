import React from 'react';
import { PageTransition } from '../components/animation/PageTransition';
import { TrendingUp, Flame, Zap, Award } from 'lucide-react';
import { TrendChartWidget } from '../components/dashboard/TrendChart';
import { AreaChartWidget } from '../components/dashboard/AreaChart';
import { BarChartWidget } from '../components/dashboard/BarChart';
import { useAppStore } from '../app/store';

export const IndustryTrendsPage: React.FC = () => {
  const { activeAnalysis } = useAppStore();
  const stats = activeAnalysis?.industry_statistics;

  return (
    <PageTransition>
      <div className="space-y-8">
        <div>
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-500 mb-1">
            <TrendingUp className="h-3.5 w-3.5" />
            <span>Real-time Market Intelligence Engine</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-foreground tracking-tight">
            Industry Tech Skill Demand & Trends
          </h1>
          <p className="text-xs text-muted-foreground mt-0.5">
            Aggregated metrics derived from 1,200+ active software engineering job listings in Q1 2026.
          </p>
        </div>

        {/* Top Growth Highlights Row */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {stats?.trending_technologies?.slice(0, 3).map((tech, idx) => (
            <div
              key={idx}
              className="p-5 rounded-2xl border border-border/60 bg-card shadow-sm space-y-2 relative overflow-hidden"
            >
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-bold text-muted-foreground uppercase">{tech.category}</span>
                <span className="inline-flex items-center gap-1 text-xs font-extrabold text-emerald-500 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
                  <Flame className="h-3.5 w-3.5 text-rose-500" />
                  +{tech.growth}% YoY
                </span>
              </div>
              <h3 className="text-lg font-extrabold text-foreground">{tech.name}</h3>
              <p className="text-xs text-muted-foreground">High market hiring growth trajectory</p>
            </div>
          ))}
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <TrendChartWidget />
          <AreaChartWidget />
        </div>

        {/* Top Demanded Skills List */}
        <div className="p-6 rounded-3xl border border-border/60 bg-card shadow-md space-y-4">
          <h3 className="text-base font-extrabold text-foreground flex items-center gap-2">
            <Zap className="h-5 w-5 text-amber-500" />
            <span>Top Demanded Technical Skills Index (2026)</span>
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
            {stats?.top_demanded_skills?.map((item, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between p-3 rounded-xl bg-secondary/40 border border-border/40 text-xs"
              >
                <span className="font-bold text-foreground">{item.name}</span>
                <span className="font-extrabold text-primary">{item.score}/100</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </PageTransition>
  );
};
