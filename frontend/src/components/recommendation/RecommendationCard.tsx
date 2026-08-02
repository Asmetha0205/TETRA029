import React from 'react';
import { Sparkles, BookOpen, Clock, Award, ChevronRight, ExternalLink, Code2, Rocket } from 'lucide-react';
import { RecommendationItem } from '../../types/api';
import { formatPriorityBadge } from '../../utils/formatters';

interface RecommendationCardProps {
  item: RecommendationItem;
}

export const RecommendationCard: React.FC<RecommendationCardProps> = ({ item }) => {
  const priorityStyle = formatPriorityBadge(item.priority);

  return (
    <div className="flex flex-col justify-between rounded-3xl border border-border/60 bg-card p-6 shadow-md transition-all hover:shadow-xl hover:border-primary/40 space-y-5">
      {/* Header Info */}
      <div>
        <div className="flex items-center justify-between gap-2 mb-3">
          <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${priorityStyle.color}`}>
            {priorityStyle.label} PRIORITY
          </span>
          <div className="flex items-center space-x-2 text-xs text-muted-foreground font-semibold">
            <Clock className="h-3.5 w-3.5 text-primary" />
            <span>{item.estimated_hours} Hours</span>
            <span>•</span>
            <Award className="h-3.5 w-3.5 text-amber-500" />
            <span>{item.difficulty}</span>
          </div>
        </div>

        <h3 className="text-xl font-extrabold text-foreground tracking-tight mb-1">{item.technology}</h3>
        <p className="text-xs text-muted-foreground font-medium">{item.category}</p>
      </div>

      {/* Rationale & Industry Evidence */}
      <div className="p-4 rounded-2xl bg-secondary/40 border border-border/40 space-y-2 text-xs">
        <span className="font-bold text-foreground flex items-center gap-1.5">
          <Sparkles className="h-3.5 w-3.5 text-primary" />
          <span>Curriculum Delta Rationale:</span>
        </span>
        <p className="text-muted-foreground leading-relaxed">{item.reason}</p>
        <p className="text-[11px] text-purple-600 dark:text-purple-400 italic pt-1 border-t border-border/30">
          Industry Evidence: "{item.industry_evidence}"
        </p>
      </div>

      {/* Suggested Course Module */}
      <div className="space-y-3">
        <div className="p-3 rounded-2xl bg-primary/5 border border-primary/20 space-y-1">
          <span className="text-[10px] font-bold uppercase tracking-wider text-primary block">Suggested Course Insertion</span>
          <h4 className="text-xs font-bold text-foreground">{item.suggested_course}</h4>
          <p className="text-xs text-muted-foreground">{item.suggested_module}</p>
        </div>

        {/* Learning Outcomes */}
        <div>
          <span className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground block mb-2">
            Target Learning Outcomes:
          </span>
          <ul className="space-y-1.5 text-xs text-foreground">
            {item.learning_outcomes?.map((outcome, idx) => (
              <li key={idx} className="flex items-start space-x-2">
                <ChevronRight className="h-3.5 w-3.5 text-primary shrink-0 mt-0.5" />
                <span>{outcome}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Hands-On Lab & Mini Project */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2">
        <div className="p-3 rounded-2xl bg-emerald-500/5 border border-emerald-500/20 text-xs">
          <span className="font-bold text-emerald-600 dark:text-emerald-400 flex items-center gap-1 mb-1">
            <Code2 className="h-3.5 w-3.5" />
            <span>Hands-on Lab</span>
          </span>
          <p className="text-muted-foreground">{item.hands_on_lab}</p>
        </div>
        <div className="p-3 rounded-2xl bg-indigo-500/5 border border-indigo-500/20 text-xs">
          <span className="font-bold text-indigo-600 dark:text-indigo-400 flex items-center gap-1 mb-1">
            <Rocket className="h-3.5 w-3.5" />
            <span>Mini Project Prompt</span>
          </span>
          <p className="text-muted-foreground">{item.mini_project}</p>
        </div>
      </div>

      {/* References Links */}
      {item.references && item.references.length > 0 && (
        <div className="pt-3 border-t border-border/40 flex items-center justify-between text-xs text-muted-foreground">
          <span className="font-semibold text-[11px]">Reference Specs:</span>
          <div className="flex items-center space-x-2">
            {item.references.map((ref, idx) => (
              <a
                key={idx}
                href={ref}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center space-x-1 text-primary hover:underline"
              >
                <span>Docs #{idx + 1}</span>
                <ExternalLink className="h-3 w-3" />
              </a>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
