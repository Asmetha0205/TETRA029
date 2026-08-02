import React from 'react';
import { Link } from 'react-router-dom';
import {
  Sparkles,
  ArrowRight,
  UploadCloud,
  Cpu,
  Database,
  Network,
  Scale,
  CheckCircle2,
  Zap,
  ShieldCheck,
  Code2,
} from 'lucide-react';
import { PageTransition } from '../components/animation/PageTransition';

export const LandingPage: React.FC = () => {
  return (
    <PageTransition>
      <div className="space-y-24 py-6">
        {/* Hero Section */}
        <section className="relative flex flex-col items-center text-center space-y-8 py-16 overflow-hidden">
          {/* Animated Background Mesh */}
          <div className="absolute -top-24 left-1/2 -translate-x-1/2 w-[700px] h-[350px] bg-gradient-to-tr from-indigo-500/20 via-purple-500/20 to-pink-500/20 rounded-full blur-3xl -z-10 pointer-events-none animate-pulse" />

          {/* Floating Badge */}
          <div className="inline-flex items-center space-x-2 px-4 py-1.5 rounded-full text-xs font-bold bg-primary/10 text-primary border border-primary/20 shadow-sm">
            <Sparkles className="h-4 w-4 animate-spin" />
            <span>Autonomous AI SaaS Engine • Gemini 1.5 Pro & Neo4j</span>
          </div>

          {/* Main Title */}
          <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight text-foreground max-w-4xl leading-tight">
            Aligning Academic Curricula with Modern{' '}
            <span className="bg-gradient-to-r from-primary via-purple-500 to-pink-500 bg-clip-text text-transparent">
              Industry Demands
            </span>
          </h1>

          {/* Subtitle */}
          <p className="text-base md:text-xl text-muted-foreground max-w-2xl font-medium leading-relaxed">
            Eliminate curriculum skill mismatches automatically. CurricuAlign AI extracts course concepts from PDF syllabi, computes vector similarity against live tech job listings, and constructs tailored graph learning roadmaps.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center gap-4 pt-4">
            <Link
              to="/upload"
              className="inline-flex items-center space-x-2.5 h-12 px-8 rounded-2xl bg-gradient-to-r from-primary via-purple-600 to-accent text-white font-bold text-sm shadow-xl shadow-primary/25 hover:scale-105 active:scale-95 transition-all"
            >
              <UploadCloud className="h-5 w-5" />
              <span>Analyze Curriculum PDF</span>
              <ArrowRight className="h-4 w-4 ml-1" />
            </Link>

            <Link
              to="/dashboard"
              className="inline-flex items-center space-x-2 h-12 px-6 rounded-2xl bg-card border border-border/80 text-foreground font-semibold text-sm hover:bg-secondary/60 transition-all shadow-sm"
            >
              <span>Explore Live Dashboard Demo</span>
            </Link>
          </div>

          {/* Key Metrics Strip */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 pt-12 max-w-4xl w-full border-t border-border/40 text-center">
            <div>
              <span className="text-3xl font-extrabold text-foreground">96.5%</span>
              <p className="text-xs text-muted-foreground font-medium">Vector Matching Accuracy</p>
            </div>
            <div>
              <span className="text-3xl font-extrabold text-primary">&lt; 2.5s</span>
              <p className="text-xs text-muted-foreground font-medium">End-to-End Orchestration</p>
            </div>
            <div>
              <span className="text-3xl font-extrabold text-emerald-500">1,200+</span>
              <p className="text-xs text-muted-foreground font-medium">Live Tech Job Records</p>
            </div>
            <div>
              <span className="text-3xl font-extrabold text-amber-500">4 Engines</span>
              <p className="text-xs text-muted-foreground font-medium">Academic, Industry, Semantic, Graph</p>
            </div>
          </div>
        </section>

        {/* Feature Cards Grid */}
        <section className="space-y-10">
          <div className="text-center space-y-2">
            <h2 className="text-2xl md:text-3xl font-extrabold text-foreground">
              Four Intelligence Engines Working in Unison
            </h2>
            <p className="text-xs md:text-sm text-muted-foreground max-w-xl mx-auto">
              Modular microservice architecture coordinating academic extraction, market intelligence, vector search, and graph recommendations.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="p-6 rounded-3xl border border-border/60 bg-card shadow-md space-y-3 hover:border-primary/40 transition-all">
              <div className="h-12 w-12 rounded-2xl bg-blue-500/10 text-blue-500 flex items-center justify-center">
                <Cpu className="h-6 w-6" />
              </div>
              <h3 className="text-base font-bold text-foreground">Academic Engine</h3>
              <p className="text-xs text-muted-foreground leading-relaxed">
                Ingests PDF syllabi, parses multi-tier course heirarchies, topics, learning outcomes, and Bloom's taxonomy levels.
              </p>
            </div>

            <div className="p-6 rounded-3xl border border-border/60 bg-card shadow-md space-y-3 hover:border-primary/40 transition-all">
              <div className="h-12 w-12 rounded-2xl bg-purple-500/10 text-purple-500 flex items-center justify-center">
                <Database className="h-6 w-6" />
              </div>
              <h3 className="text-base font-bold text-foreground">Industry Engine</h3>
              <p className="text-xs text-muted-foreground leading-relaxed">
                Scrapes tech job descriptions, identifies high-demand skills, tools, and real market frequency weights.
              </p>
            </div>

            <div className="p-6 rounded-3xl border border-border/60 bg-card shadow-md space-y-3 hover:border-primary/40 transition-all">
              <div className="h-12 w-12 rounded-2xl bg-pink-500/10 text-pink-500 flex items-center justify-center">
                <Scale className="h-6 w-6" />
              </div>
              <h3 className="text-base font-bold text-foreground">Semantic Engine</h3>
              <p className="text-xs text-muted-foreground leading-relaxed">
                Computes high-dimensional cosine similarity embeddings in Pinecone to map academic concepts against industry skills.
              </p>
            </div>

            <div className="p-6 rounded-3xl border border-border/60 bg-card shadow-md space-y-3 hover:border-primary/40 transition-all">
              <div className="h-12 w-12 rounded-2xl bg-emerald-500/10 text-emerald-500 flex items-center justify-center">
                <Network className="h-6 w-6" />
              </div>
              <h3 className="text-base font-bold text-foreground">Recommendation Engine</h3>
              <p className="text-xs text-muted-foreground leading-relaxed">
                Queries Neo4j Knowledge Graph to construct semester-by-semester learning roadmaps and course modules.
              </p>
            </div>
          </div>
        </section>

        {/* How It Works Interactive Steps */}
        <section className="p-8 md:p-12 rounded-3xl border border-border/60 bg-card shadow-xl space-y-8">
          <div className="text-center space-y-2">
            <span className="text-xs font-extrabold uppercase tracking-wider text-primary">Simple 4-Step Workflow</span>
            <h2 className="text-2xl md:text-3xl font-extrabold text-foreground">From PDF Upload to Actionable Report</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 relative">
            <div className="space-y-3 text-center md:text-left">
              <div className="h-10 w-10 rounded-2xl bg-primary text-white font-extrabold flex items-center justify-center text-sm shadow-md">
                1
              </div>
              <h4 className="text-sm font-bold text-foreground">Upload Syllabus PDF</h4>
              <p className="text-xs text-muted-foreground">
                Drop your university's CS department curriculum PDF into our drag & drop portal.
              </p>
            </div>

            <div className="space-y-3 text-center md:text-left">
              <div className="h-10 w-10 rounded-2xl bg-primary text-white font-extrabold flex items-center justify-center text-sm shadow-md">
                2
              </div>
              <h4 className="text-sm font-bold text-foreground">AI Extraction & Vector Matching</h4>
              <p className="text-xs text-muted-foreground">
                Gemini 1.5 Pro extracts topics while Pinecone computes vector similarity against IEEE taxonomies.
              </p>
            </div>

            <div className="space-y-3 text-center md:text-left">
              <div className="h-10 w-10 rounded-2xl bg-primary text-white font-extrabold flex items-center justify-center text-sm shadow-md">
                3
              </div>
              <h4 className="text-sm font-bold text-foreground">Gap & Delta Diagnostics</h4>
              <p className="text-xs text-muted-foreground">
                Identify missing modern skills like Docker, Kubernetes, RAG, and Terraform IaC.
              </p>
            </div>

            <div className="space-y-3 text-center md:text-left">
              <div className="h-10 w-10 rounded-2xl bg-primary text-white font-extrabold flex items-center justify-center text-sm shadow-md">
                4
              </div>
              <h4 className="text-sm font-bold text-foreground">Download Executive Report</h4>
              <p className="text-xs text-muted-foreground">
                Export complete PDF, Markdown, or JSON reports with course syllabi insertion recommendations.
              </p>
            </div>
          </div>
        </section>

        {/* Upload CTA Banner */}
        <section className="p-8 md:p-12 rounded-3xl bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 text-white shadow-2xl flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="space-y-2 text-center md:text-left">
            <h2 className="text-2xl md:text-3xl font-extrabold tracking-tight">Ready to Audit Your CS Curriculum?</h2>
            <p className="text-xs md:text-sm text-indigo-100 max-w-xl">
              Get an instant alignment score, interactive gap matrix, and learning roadmaps tailored for 2026 tech standards.
            </p>
          </div>
          <Link
            to="/upload"
            className="inline-flex items-center space-x-2.5 h-12 px-8 rounded-2xl bg-white text-indigo-900 font-extrabold text-sm shadow-lg hover:scale-105 active:scale-95 transition-all shrink-0"
          >
            <UploadCloud className="h-5 w-5 text-indigo-600" />
            <span>Upload PDF Now</span>
          </Link>
        </section>
      </div>
    </PageTransition>
  );
};
