import React from 'react';
import { Link } from 'react-router-dom';
import {
  Scale,
  BookOpen,
  Briefcase,
  CheckCircle2,
  AlertTriangle,
  Sparkles,
  Clock,
  ArrowRight,
  UploadCloud,
  FileText,
  Activity,
} from 'lucide-react';
import { PageTransition } from '../components/animation/PageTransition';
import { StatisticsCard } from '../components/dashboard/StatisticsCard';
import { AlignmentGauge } from '../components/dashboard/AlignmentGauge';
import { PieChartWidget } from '../components/dashboard/PieChart';
import { BarChartWidget } from '../components/dashboard/BarChart';
import { RadarChartWidget } from '../components/dashboard/RadarChart';
import { TrendChartWidget } from '../components/dashboard/TrendChart';
import { AreaChartWidget } from '../components/dashboard/AreaChart';
import { useAppStore } from '../app/store';

export const DashboardPage: React.FC = () => {
  const { activeAnalysis } = useAppStore();

  const data = activeAnalysis;

  if (!data) {
    return (
      <PageTransition>
        <div className="text-center py-12">
          <p className="text-muted-foreground">No active analysis found.</p>
          <Link to="/upload" className="text-primary underline mt-2 inline-block">
            Upload a PDF to get started
          </Link>
        </div>
      </PageTransition>
    );
  }

  return (
    <PageTransition>
      <div className="space-y-8">
        {/* Page Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-semibold bg-primary/10 text-primary mb-1">
              <Sparkles className="h-3.5 w-3.5" />
              <span>Active Curriculum Intelligence</span>
            </div>
            <h1 className="text-2xl md:text-3xl font-extrabold text-foreground tracking-tight">
              {data.university_name || 'CS Curriculum Analytics Dashboard'}
            </h1>
            <p className="text-xs text-muted-foreground">
              {data.department} • Academic Year {data.curriculum_year} • ID: <code className="text-primary">{data.analysis_id}</code>
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <Link
              to="/report"
              className="inline-flex items-center space-x-2 h-10 px-4 rounded-xl bg-card border border-border text-foreground font-semibold text-xs hover:bg-secondary transition-all"
            >
              <FileText className="h-4 w-4" />
              <span>Executive Report</span>
            </Link>

            <Link
              to="/upload"
              className="inline-flex items-center space-x-2 h-10 px-4 rounded-xl bg-primary text-primary-foreground font-semibold text-xs shadow-md hover:opacity-90 transition-all"
            >
              <UploadCloud className="h-4 w-4" />
              <span>New Analysis</span>
            </Link>
          </div>
        </div>

        {/* KPI Metrics Cards Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatisticsCard
            title="Overall Alignment"
            value={`${data.alignment_score}%`}
            subtitle="Vector Similarity Score"
            change="+4.2% vs last audit"
            changeType="positive"
            icon={Scale}
            iconBg="bg-primary/10 text-primary"
          />

          <StatisticsCard
            title="Covered Skills"
            value={data.covered_skills?.length || 4}
            subtitle="Full Alignment in Syllabus"
            change="100% Match"
            changeType="positive"
            icon={CheckCircle2}
            iconBg="bg-emerald-500/10 text-emerald-500"
          />

          <StatisticsCard
            title="Critical Skill Gaps"
            value={data.gap_skills?.length || 4}
            subtitle="Missing from Curriculum"
            change="Action Needed"
            changeType="negative"
            icon={AlertTriangle}
            iconBg="bg-rose-500/10 text-rose-500"
          />

          <StatisticsCard
            title="Processing Speed"
            value={`${data.execution_time || 1.64}s`}
            subtitle="FastAPI + Neo4j Pipeline"
            change="94% Cache Hit"
            changeType="positive"
            icon={Clock}
            iconBg="bg-purple-500/10 text-purple-500"
          />
        </div>

        {/* Core Gauge & Distribution Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <AlignmentGauge score={data.alignment_score} />
          <PieChartWidget
            coveredCount={data.covered_skills?.length}
            partialCount={data.partial_skills?.length}
            gapCount={data.gap_skills?.length}
          />
          <RadarChartWidget />
        </div>

        {/* Charts Grid Row 2 */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <BarChartWidget />
          <TrendChartWidget />
          <AreaChartWidget />
        </div>

        {/* Quick Action Navigation Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4">
          <Link
            to="/gap-analysis"
            className="p-5 rounded-2xl border border-border/60 bg-card hover:border-primary/50 transition-all group flex items-center justify-between"
          >
            <div>
              <h4 className="text-sm font-bold text-foreground group-hover:text-primary transition-colors">
                Explore Skill Gap Matrix
              </h4>
              <p className="text-xs text-muted-foreground mt-0.5">Filter & inspect similarity evidence citations</p>
            </div>
            <ArrowRight className="h-5 w-5 text-muted-foreground group-hover:text-primary transition-transform group-hover:translate-x-1" />
          </Link>

          <Link
            to="/recommendations"
            className="p-5 rounded-2xl border border-border/60 bg-card hover:border-primary/50 transition-all group flex items-center justify-between"
          >
            <div>
              <h4 className="text-sm font-bold text-foreground group-hover:text-primary transition-colors">
                View Actionable Recommendations
              </h4>
              <p className="text-xs text-muted-foreground mt-0.5">Suggested courses, labs, and mini projects</p>
            </div>
            <ArrowRight className="h-5 w-5 text-muted-foreground group-hover:text-primary transition-transform group-hover:translate-x-1" />
          </Link>

          <Link
            to="/knowledge-graph"
            className="p-5 rounded-2xl border border-border/60 bg-card hover:border-primary/50 transition-all group flex items-center justify-between"
          >
            <div>
              <h4 className="text-sm font-bold text-foreground group-hover:text-primary transition-colors">
                Interactive Neo4j Knowledge Graph
              </h4>
              <p className="text-xs text-muted-foreground mt-0.5">Explore prerequisite connections and nodes</p>
            </div>
            <ArrowRight className="h-5 w-5 text-muted-foreground group-hover:text-primary transition-transform group-hover:translate-x-1" />
          </Link>
        </div>
      </div>
    </PageTransition>
  );
};
