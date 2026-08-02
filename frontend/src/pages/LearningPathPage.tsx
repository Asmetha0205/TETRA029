import React from 'react';
import { PageTransition } from '../components/animation/PageTransition';
import { LearningPathCard } from '../components/learning/LearningPathCard';
import { MapPin, Award, Rocket } from 'lucide-react';
import { useAppStore } from '../app/store';

export const LearningPathPage: React.FC = () => {
  const { activeAnalysis } = useAppStore();
  const learningPaths = activeAnalysis?.learning_paths;

  return (
    <PageTransition>
      <div className="space-y-8">
        {/* Header Banner */}
        <div className="rounded-3xl border border-border/60 bg-card p-6 md:p-8 shadow-xl relative overflow-hidden">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-500 mb-2">
                <MapPin className="h-3.5 w-3.5" />
                <span>Curriculum Integration Roadmap</span>
              </div>
              <h1 className="text-2xl md:text-3xl font-extrabold text-foreground tracking-tight">
                Semester-by-Semester Learning Path
              </h1>
              <p className="text-xs text-muted-foreground mt-1">
                Target Role Outcome: <span className="font-extrabold text-primary">{learningPaths?.target_role || 'Cloud & AI Systems Software Engineer'}</span>
              </p>
            </div>

            <div className="flex items-center space-x-4 bg-secondary/50 p-4 rounded-2xl border border-border/40 text-center">
              <div>
                <span className="text-2xl font-extrabold text-foreground">{learningPaths?.total_semesters || 4}</span>
                <p className="text-[10px] font-bold text-muted-foreground uppercase">Semesters</p>
              </div>
              <div className="h-8 w-px bg-border/60" />
              <div>
                <span className="text-2xl font-extrabold text-emerald-500">56</span>
                <p className="text-[10px] font-bold text-muted-foreground uppercase">Total Weeks</p>
              </div>
            </div>
          </div>
        </div>

        {/* Roadmap Timeline */}
        <div className="max-w-4xl mx-auto pt-4">
          {learningPaths?.roadmap?.map((module, idx) => (
            <LearningPathCard key={idx} module={module} stepIndex={idx} />
          ))}
        </div>
      </div>
    </PageTransition>
  );
};
