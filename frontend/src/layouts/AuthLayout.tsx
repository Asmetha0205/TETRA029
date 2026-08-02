import React from 'react';
import { Outlet, Link } from 'react-router-dom';
import { Sparkles, ShieldCheck } from 'lucide-react';
import { ThemeSwitcher } from '../components/common/ThemeSwitcher';

export const AuthLayout: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col md:flex-row bg-background text-foreground">
      {/* Left Decorative Branding Panel */}
      <div className="hidden md:flex flex-1 flex-col justify-between p-12 bg-gradient-to-br from-indigo-900 via-slate-900 to-purple-950 text-white relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-primary/20 rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl" />

        <div className="relative z-10">
          <Link to="/" className="flex items-center space-x-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-tr from-indigo-500 to-pink-500 text-white shadow-xl">
              <Sparkles className="h-6 w-6" />
            </div>
            <span className="font-extrabold text-2xl tracking-tight">CurricuAlign AI</span>
          </Link>
        </div>

        <div className="relative z-10 space-y-4 max-w-lg">
          <h1 className="text-4xl font-extrabold tracking-tight leading-tight">
            Autonomous Academic & Industry Alignment Intelligence
          </h1>
          <p className="text-sm text-indigo-200 leading-relaxed">
            Eliminating skill mismatches in higher education using Gemini 1.5 Pro multimodal LLMs, Neo4j Knowledge Graphs, and Pinecone vector search.
          </p>
          <div className="flex items-center space-x-4 pt-4 text-xs font-semibold text-indigo-300">
            <span className="flex items-center gap-1.5">
              <ShieldCheck className="h-4 w-4 text-emerald-400" /> Enterprise SLA
            </span>
            <span>•</span>
            <span>Real-time Telemetry</span>
            <span>•</span>
            <span>PDF Ingestion</span>
          </div>
        </div>

        <div className="relative z-10 text-xs text-indigo-400">
          © 2026 CurricuAlign AI. Hackathon Edition v1.0.
        </div>
      </div>

      {/* Right Form Container */}
      <div className="flex-1 flex flex-col justify-between p-6 md:p-12">
        <div className="flex justify-end">
          <ThemeSwitcher />
        </div>

        <div className="w-full max-w-md mx-auto">
          <Outlet />
        </div>

        <div className="text-center text-xs text-muted-foreground pt-6">
          <Link to="/" className="hover:text-foreground underline">
            Return to Public Landing Page
          </Link>
        </div>
      </div>
    </div>
  );
};
