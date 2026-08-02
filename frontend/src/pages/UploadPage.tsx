import React from 'react';
import { PageTransition } from '../components/animation/PageTransition';
import { UploadZone } from '../components/upload/UploadZone';
import { History, FileText, CheckCircle2 } from 'lucide-react';
import { useAppStore } from '../app/store';

export const UploadPage: React.FC = () => {
  const { analysisHistory } = useAppStore();

  return (
    <PageTransition>
      <div className="space-y-10 py-4">
        <div className="text-center space-y-2 max-w-xl mx-auto">
          <h1 className="text-3xl font-extrabold text-foreground tracking-tight">Upload Curriculum PDF</h1>
          <p className="text-xs text-muted-foreground">
            Our multi-engine pipeline automatically extracts course syllabi, standardizes taxonomy concepts, and calculates vector similarity against live market job descriptions.
          </p>
        </div>

        {/* Upload Zone */}
        <UploadZone />

        {/* Recent Upload History */}
        {analysisHistory && analysisHistory.length > 0 && (
          <div className="max-w-4xl mx-auto space-y-4">
            <h3 className="text-sm font-bold text-foreground flex items-center gap-2">
              <History className="h-4 w-4 text-primary" />
              <span>Recent Curriculum Ingestions</span>
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {analysisHistory.map((historyItem) => (
                <div
                  key={historyItem.analysis_id}
                  className="flex items-center justify-between p-4 rounded-2xl border border-border/60 bg-card shadow-sm hover:border-primary/40 transition-all"
                >
                  <div className="flex items-center space-x-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10 text-primary">
                      <FileText className="h-5 w-5" />
                    </div>
                    <div>
                      <h4 className="text-xs font-bold text-foreground truncate max-w-[200px]">
                        {historyItem.university_name || 'Curriculum Ingestion'}
                      </h4>
                      <p className="text-[10px] text-muted-foreground">
                        {historyItem.curriculum_year} • Score: <span className="font-bold text-emerald-500">{historyItem.alignment_score}%</span>
                      </p>
                    </div>
                  </div>

                  <span className="flex items-center gap-1 text-[10px] font-semibold text-emerald-500 bg-emerald-500/10 px-2.5 py-1 rounded-full border border-emerald-500/20">
                    <CheckCircle2 className="h-3 w-3" />
                    Analyzed
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </PageTransition>
  );
};
