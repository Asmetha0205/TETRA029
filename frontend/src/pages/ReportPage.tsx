import React from 'react';
import { PageTransition } from '../components/animation/PageTransition';
import { Download, FileCode, Printer, Sparkles, CheckCircle2, AlertTriangle, BookOpen, MapPin } from 'lucide-react';
import { useAppStore } from '../app/store';
import { exportService } from '../services/exportService';
import { toast } from 'sonner';

export const ReportPage: React.FC = () => {
  const { activeAnalysis } = useAppStore();
  const data = activeAnalysis;

  if (!data) return null;

  const handleDownloadPDF = () => {
    exportService.exportPrintableHTML(data);
    toast.success('Print / Export PDF dialog opened.');
  };

  const handleDownloadMarkdown = () => {
    exportService.exportMarkdown(data, `CurricuAlign_Report_${data.university_name?.replace(/\s+/g, '_')}.md`);
    toast.success('Markdown report downloaded!');
  };

  const handleDownloadJSON = () => {
    exportService.exportJSON(data, `CurricuAlign_Report_${data.analysis_id}.json`);
    toast.success('Raw JSON dataset downloaded!');
  };

  return (
    <PageTransition>
      <div className="space-y-8 max-w-5xl mx-auto py-4">
        {/* Top Export Bar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 rounded-2xl bg-card border border-border shadow-sm">
          <div>
            <span className="text-xs font-bold text-primary uppercase tracking-wider block">Official Executive Report</span>
            <h1 className="text-lg font-extrabold text-foreground">{data.university_name || 'CS Curriculum Alignment'}</h1>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={handleDownloadPDF}
              className="inline-flex items-center space-x-1.5 px-3.5 py-2 rounded-xl bg-primary text-primary-foreground font-semibold text-xs shadow hover:opacity-90 transition-all"
            >
              <Printer className="h-4 w-4" />
              <span>Export PDF / Print</span>
            </button>

            <button
              onClick={handleDownloadMarkdown}
              className="inline-flex items-center space-x-1.5 px-3.5 py-2 rounded-xl bg-secondary text-foreground font-semibold text-xs hover:bg-secondary/80 transition-all"
            >
              <FileCode className="h-4 w-4 text-purple-500" />
              <span>Export Markdown</span>
            </button>

            <button
              onClick={handleDownloadJSON}
              className="inline-flex items-center space-x-1.5 px-3.5 py-2 rounded-xl bg-secondary text-foreground font-semibold text-xs hover:bg-secondary/80 transition-all"
            >
              <Download className="h-4 w-4 text-emerald-500" />
              <span>Download JSON</span>
            </button>
          </div>
        </div>

        {/* Printable Report Document Body */}
        <div id="printable-report" className="p-8 md:p-12 rounded-3xl bg-card border border-border shadow-2xl space-y-8 text-foreground">
          {/* Document Header */}
          <div className="border-b border-border/60 pb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <span className="text-xs font-bold text-muted-foreground uppercase tracking-widest block mb-1">
                CurricuAlign AI Audit Report
              </span>
              <h2 className="text-3xl font-extrabold text-foreground tracking-tight">
                Executive Curriculum Alignment Summary
              </h2>
              <p className="text-xs text-muted-foreground mt-1">
                {data.university_name} • {data.department} • {data.curriculum_year}
              </p>
            </div>

            <div className="text-right">
              <span className="text-4xl font-extrabold text-primary">{data.alignment_score}%</span>
              <p className="text-xs font-bold text-muted-foreground uppercase">Alignment Score</p>
            </div>
          </div>

          {/* Section 1: Executive Summary */}
          <div className="space-y-3">
            <h3 className="text-lg font-bold text-foreground flex items-center gap-2 border-b border-border/40 pb-2">
              <Sparkles className="h-5 w-5 text-primary" />
              <span>1. Executive Summary & Diagnostic Rationale</span>
            </h3>
            <p className="text-xs text-muted-foreground leading-relaxed">
              This audit evaluated the official Computer Science curriculum against live technical job requirements in Q1 2026. The curriculum demonstrates exceptional depth in core theoretical foundations (Data Structures, Algorithms, Operating Systems, Relational Databases). However, a critical delta exists regarding modern cloud-native deployment, containerization (Docker/Kubernetes), Generative AI orchestration (RAG/Vector Databases), and automated CI/CD infrastructure.
            </p>
          </div>

          {/* Section 2: Skill Coverage & Gaps */}
          <div className="space-y-4">
            <h3 className="text-lg font-bold text-foreground flex items-center gap-2 border-b border-border/40 pb-2">
              <AlertTriangle className="h-5 w-5 text-rose-500" />
              <span>2. Identified Delta Gaps & Priority Matrix</span>
            </h3>

            <div className="space-y-3">
              {data.gap_skills?.map((gap, idx) => (
                <div key={idx} className="p-4 rounded-2xl bg-secondary/40 border border-border/40 space-y-1 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-foreground text-sm">{gap.matched_industry_skill}</span>
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-500/10 text-rose-500 border border-rose-500/20">
                      {gap.priority} PRIORITY
                    </span>
                  </div>
                  <p className="text-muted-foreground">Category: {gap.category} • Industry Demand Score: {gap.industry_demand_score}/100</p>
                  <p className="text-muted-foreground italic pt-1">
                    Industry Citation: "{gap.industry_evidence}"
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Section 3: Recommendations */}
          <div className="space-y-4">
            <h3 className="text-lg font-bold text-foreground flex items-center gap-2 border-b border-border/40 pb-2">
              <BookOpen className="h-5 w-5 text-emerald-500" />
              <span>3. Course Insertion Recommendations</span>
            </h3>

            <div className="space-y-3">
              {data.recommendations?.map((rec, idx) => (
                <div key={idx} className="p-4 rounded-2xl bg-primary/5 border border-primary/20 space-y-2 text-xs">
                  <h4 className="font-bold text-foreground text-sm">{rec.technology}</h4>
                  <p className="text-muted-foreground">Insertion Site: <span className="font-semibold text-foreground">{rec.suggested_course}</span> ({rec.suggested_module})</p>
                  <p className="text-muted-foreground">Hands-on Lab: {rec.hands_on_lab}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Document Footer */}
          <div className="pt-6 border-t border-border/40 text-center text-[10px] text-muted-foreground">
            Report Generated Automatically by CurricuAlign AI System Integration Layer • {new Date(data.generated_at).toLocaleString()}
          </div>
        </div>
      </div>
    </PageTransition>
  );
};
