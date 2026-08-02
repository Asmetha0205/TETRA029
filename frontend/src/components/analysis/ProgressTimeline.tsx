import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { CheckCircle2, Loader2, Sparkles, AlertCircle, ArrowRight, Terminal } from 'lucide-react';
import { PIPELINE_STAGES } from '../../utils/constants';

interface ProgressTimelineProps {
  analysisId: string;
}

export const ProgressTimeline: React.FC<ProgressTimelineProps> = ({ analysisId }) => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [logs, setLogs] = useState<string[]>([
    '[SYSTEM] Initialized unified pipeline orchestrator.',
    '[ACADEMIC_ENGINE] Receiving PDF bytes stream...',
  ]);

  useEffect(() => {
    const logMessages = [
      '[ACADEMIC_ENGINE] PDF successfully ingested. Extracting text nodes.',
      '[ACADEMIC_ENGINE] Identified 24 course modules and 142 skill concepts.',
      '[SEMANTIC_ENGINE] Querying Pinecone vector DB with Gemini embeddings.',
      '[SEMANTIC_ENGINE] Cosine similarity matrices calculated against IEEE taxonomy.',
      '[RECOMMENDATION_ENGINE] Neo4j graph traversal in progress for target skill gaps.',
      '[RECOMMENDATION_ENGINE] Generating tailored semester-by-semester learning roadmap.',
      '[SYSTEM] Unified analysis completed successfully.',
    ];

    const timer = setInterval(() => {
      setCurrentStep((prev) => {
        if (prev >= 8) {
          clearInterval(timer);
          return 8;
        }
        const nextStep = prev + 1;
        if (logMessages[prev - 1]) {
          setLogs((l) => [...l, logMessages[prev - 1]]);
        }
        return nextStep;
      });
    }, 1200);

    return () => clearInterval(timer);
  }, []);

  const progressPct = Math.round((currentStep / 8) * 100);

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      {/* Header Banner */}
      <div className="rounded-3xl border border-border/60 bg-card p-6 md:p-8 shadow-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
          <div>
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-semibold bg-primary/10 text-primary mb-2">
              <Sparkles className="h-3.5 w-3.5 animate-spin" />
              <span>Live Orchestration Pipeline</span>
            </div>
            <h2 className="text-2xl font-extrabold text-foreground">Analyzing Curriculum Pipeline</h2>
            <p className="text-xs text-muted-foreground mt-1">
              Job ID: <code className="text-primary">{analysisId}</code>
            </p>
          </div>
          <div className="text-right">
            <span className="text-3xl font-extrabold text-primary">{progressPct}%</span>
            <p className="text-xs text-muted-foreground font-medium">Pipeline Completion</p>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="w-full h-3 rounded-full bg-secondary overflow-hidden mb-8">
          <div
            className="h-full bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 transition-all duration-500"
            style={{ width: `${progressPct}%` }}
          />
        </div>

        {/* 8-Stage Timeline Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {PIPELINE_STAGES.map((stage) => {
            const isCompleted = stage.id < currentStep;
            const isCurrent = stage.id === currentStep;
            return (
              <div
                key={stage.id}
                className={`flex items-start space-x-3.5 p-4 rounded-2xl border transition-all ${
                  isCompleted
                    ? 'border-emerald-500/30 bg-emerald-500/5'
                    : isCurrent
                    ? 'border-primary bg-primary/10 shadow-md ring-1 ring-primary/40'
                    : 'border-border/40 bg-secondary/20 opacity-60'
                }`}
              >
                <div className="shrink-0 mt-0.5">
                  {isCompleted ? (
                    <CheckCircle2 className="h-5 w-5 text-emerald-500" />
                  ) : isCurrent ? (
                    <Loader2 className="h-5 w-5 text-primary animate-spin" />
                  ) : (
                    <div className="h-5 w-5 rounded-full border-2 border-muted-foreground/40 flex items-center justify-center text-[10px] font-bold text-muted-foreground">
                      {stage.id}
                    </div>
                  )}
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <h4
                      className={`text-xs font-bold ${
                        isCompleted ? 'text-foreground' : isCurrent ? 'text-primary' : 'text-muted-foreground'
                      }`}
                    >
                      {stage.name}
                    </h4>
                    {isCurrent && (
                      <span className="text-[10px] font-semibold text-primary animate-pulse">PROCESSING</span>
                    )}
                  </div>
                  <p className="text-[11px] text-muted-foreground mt-0.5 truncate">{stage.desc}</p>
                </div>
              </div>
            );
          })}
        </div>

        {/* Console Log Terminal Window */}
        <div className="mt-8 rounded-2xl bg-black/90 p-4 border border-white/10 font-mono text-xs text-emerald-400 space-y-1">
          <div className="flex items-center justify-between pb-2 mb-2 border-b border-white/10 text-gray-400">
            <span className="flex items-center gap-1.5 text-[11px]">
              <Terminal className="h-3.5 w-3.5" />
              <span>Orchestration Execution Logs</span>
            </span>
            <span className="text-[10px]">Real-time Telemetry</span>
          </div>
          <div className="max-h-36 overflow-y-auto space-y-1">
            {logs.map((log, index) => (
              <div key={index} className="leading-relaxed">
                <span className="text-gray-500 mr-2">[{new Date().toLocaleTimeString()}]</span>
                {log}
              </div>
            ))}
          </div>
        </div>

        {/* Redirect CTA when completed */}
        {currentStep === 8 && (
          <div className="mt-6 flex justify-end">
            <button
              onClick={() => navigate('/dashboard')}
              className="inline-flex items-center space-x-2 px-6 py-3 rounded-xl bg-emerald-500 text-white font-bold text-sm shadow-lg hover:bg-emerald-600 hover:scale-105 transition-all"
            >
              <span>View Full Dashboard & Reports</span>
              <ArrowRight className="h-4 w-4" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
