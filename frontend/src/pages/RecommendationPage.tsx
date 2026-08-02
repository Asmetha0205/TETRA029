import React, { useState, useMemo } from 'react';
import { PageTransition } from '../components/animation/PageTransition';
import { RecommendationCard } from '../components/recommendation/RecommendationCard';
import { Sparkles, Filter } from 'lucide-react';
import { useAppStore } from '../app/store';

export const RecommendationPage: React.FC = () => {
  const { activeAnalysis } = useAppStore();
  const [filterPriority, setFilterPriority] = useState<string>('ALL');

  const recommendations = activeAnalysis?.recommendations || [];

  const filteredRecommendations = useMemo(() => {
    if (filterPriority === 'ALL') return recommendations;
    return recommendations.filter((r) => r.priority === filterPriority);
  }, [recommendations, filterPriority]);

  return (
    <PageTransition>
      <div className="space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-semibold bg-primary/10 text-primary mb-1">
              <Sparkles className="h-3.5 w-3.5" />
              <span>Neo4j Graph & Gemini 1.5 Recommendations</span>
            </div>
            <h1 className="text-2xl md:text-3xl font-extrabold text-foreground tracking-tight">
              Actionable Course Insertion Recommendations
            </h1>
            <p className="text-xs text-muted-foreground mt-0.5">
              Structured modules, hands-on labs, and project deliverables to close curriculum skill gaps.
            </p>
          </div>

          {/* Priority Filters */}
          <div className="flex items-center space-x-2 bg-card p-1.5 rounded-2xl border border-border/50 shadow-sm self-start md:self-auto">
            <span className="text-[11px] font-semibold text-muted-foreground px-2">Priority:</span>
            {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM'].map((pri) => (
              <button
                key={pri}
                onClick={() => setFilterPriority(pri)}
                className={`px-3 py-1 rounded-xl text-xs font-semibold transition-all ${
                  filterPriority === pri
                    ? 'bg-primary text-primary-foreground shadow-sm'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                {pri}
              </button>
            ))}
          </div>
        </div>

        {/* Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {filteredRecommendations.map((item) => (
            <RecommendationCard key={item.id} item={item} />
          ))}
        </div>
      </div>
    </PageTransition>
  );
};
