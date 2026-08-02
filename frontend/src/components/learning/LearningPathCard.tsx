import React from 'react';
import { Calendar, CheckCircle, ArrowRight, BookOpen, Layers } from 'lucide-react';
import { LearningPathModule } from '../../types/api';

interface LearningPathCardProps {
  module: LearningPathModule;
  stepIndex: number;
}

export const LearningPathCard: React.FC<LearningPathCardProps> = ({ module, stepIndex }) => {
  return (
    <div className="relative pl-8 pb-10 last:pb-0 group">
      {/* Vertical Timeline Bar */}
      <div className="absolute left-3 top-3 -bottom-3 w-0.5 bg-border/60 group-last:hidden" />

      {/* Step Circle Indicator */}
      <div className="absolute left-0 top-0 flex h-7 w-7 items-center justify-center rounded-full bg-primary text-primary-foreground font-extrabold text-xs shadow-md shadow-primary/20 ring-4 ring-background">
        {stepIndex + 1}
      </div>

      <div className="rounded-3xl border border-border/60 bg-card p-6 shadow-md transition-all hover:border-primary/40 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <span className="text-xs font-bold text-primary uppercase tracking-wider block mb-1">
              {module.semester}
            </span>
            <h3 className="text-lg font-extrabold text-foreground">{module.title}</h3>
          </div>
          <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-secondary text-muted-foreground self-start sm:self-auto">
            <Calendar className="h-3.5 w-3.5" />
            <span>{module.estimated_weeks} Weeks Duration</span>
          </div>
        </div>

        <p className="text-xs text-muted-foreground leading-relaxed">{module.description}</p>

        {/* Prerequisites */}
        {module.prerequisites && module.prerequisites.length > 0 && (
          <div className="flex items-center space-x-2 text-xs">
            <span className="font-bold text-muted-foreground uppercase text-[10px]">Prerequisites:</span>
            <div className="flex flex-wrap gap-1">
              {module.prerequisites.map((req, idx) => (
                <span key={idx} className="px-2 py-0.5 rounded-lg bg-secondary text-foreground text-[10px] font-medium">
                  {req}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Skills Acquired Tags */}
        <div>
          <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block mb-2">
            Skill Competencies Acquired:
          </span>
          <div className="flex flex-wrap gap-1.5">
            {module.skills_acquired?.map((skill, idx) => (
              <span
                key={idx}
                className="px-2.5 py-1 rounded-xl bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 text-xs font-semibold"
              >
                ✓ {skill}
              </span>
            ))}
          </div>
        </div>

        {/* Capstone Project Prompt */}
        <div className="p-3.5 rounded-2xl bg-primary/5 border border-primary/20 text-xs">
          <span className="font-bold text-primary block mb-0.5">Capstone Module Deliverable:</span>
          <p className="text-foreground font-medium">{module.capstone_project}</p>
        </div>
      </div>
    </div>
  );
};
