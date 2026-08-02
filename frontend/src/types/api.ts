export interface ApiResponse<T = any> {
  success: boolean;
  message: string;
  data: T;
  timestamp?: string;
}

export interface SkillItem {
  id: string;
  name: string;
  category: string;
  proficiency_level?: string;
  blooms_level?: string;
  frequency?: number;
}

export interface SkillGapItem {
  id: string;
  academic_skill: string;
  matched_industry_skill: string;
  similarity: number;
  priority: 'HIGH' | 'MEDIUM' | 'LOW' | 'CRITICAL';
  status: 'COVERED' | 'PARTIAL' | 'GAP';
  category: string;
  industry_demand_score: number;
  industry_importance_score: number;
  trend: 'RISING' | 'STABLE' | 'DECLINING';
  academic_evidence: string;
  industry_evidence: string;
}

export interface RecommendationItem {
  id: string;
  technology: string;
  category: string;
  priority: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  reason: string;
  industry_evidence: string;
  suggested_course: string;
  suggested_module: string;
  learning_outcomes: string[];
  hands_on_lab: string;
  mini_project: string;
  estimated_hours: number;
  difficulty: 'Beginner' | 'Intermediate' | 'Advanced';
  references: string[];
}

export interface LearningPathModule {
  semester: string;
  title: string;
  description: string;
  prerequisites: string[];
  skills_acquired: string[];
  estimated_weeks: number;
  capstone_project: string;
}

export interface LearningPathsData {
  roadmap: LearningPathModule[];
  total_semesters: number;
  target_role: string;
}

export interface IndustryStatistics {
  top_demanded_skills: Array<{ name: string; score: number }>;
  trending_technologies: Array<{ name: string; growth: number; category: string }>;
  emerging_skills: Array<{ name: string; score: number }>;
  category_distribution: Record<string, number>;
}

export interface UnifiedAnalysisResult {
  analysis_id: string;
  document_id: string;
  university_name?: string;
  curriculum_year?: string;
  department?: string;
  alignment_score: number;
  covered_skills: SkillGapItem[];
  partial_skills: SkillGapItem[];
  gap_skills: SkillGapItem[];
  priority_summary: {
    CRITICAL?: number;
    HIGH?: number;
    MEDIUM?: number;
    LOW?: number;
    total_gaps?: number;
  };
  recommendations: RecommendationItem[];
  learning_paths: LearningPathsData;
  industry_statistics: IndustryStatistics;
  academic_statistics?: {
    total_courses: number;
    total_skills_extracted: number;
    top_categories: Record<string, number>;
  };
  processing_metrics?: {
    extraction_time_ms: number;
    semantic_match_time_ms: number;
    recommendation_time_ms: number;
  };
  execution_time: number;
  generated_at: string;
  warnings_or_errors?: string[];
}

export interface DashboardSummary {
  total_analyses_conducted: number;
  avg_alignment_score: number;
  total_skills_mapped: number;
  system_health_status: 'OPERATIONAL' | 'DEGRADED' | 'DOWN';
  cache_hit_ratio: number;
  top_industry_gaps: string[];
  active_workflows_count: number;
}

export interface StatusSummary {
  status: string;
  uptime_seconds: number;
  active_jobs_count: number;
  active_jobs: Array<{
    job_id: string;
    filename: string;
    stage: string;
    progress_percentage: number;
    started_at: string;
  }>;
}

export interface HealthCheckResult {
  status: 'HEALTHY' | 'DEGRADED' | 'UNHEALTHY';
  components: Record<string, { status: string; latency_ms: number; message: string }>;
  checked_at: string;
}

export interface TelemetryStats {
  telemetry: {
    cpu_usage_pct: number;
    memory_usage_pct: number;
    total_requests: number;
    avg_latency_ms: number;
  };
  cache_statistics: {
    hits: number;
    misses: number;
    hit_ratio: number;
  };
}

export interface GraphNode {
  id: string;
  label: string;
  type: 'course' | 'academic_skill' | 'industry_skill' | 'gap' | 'recommendation';
  category?: string;
  metrics?: Record<string, any>;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  label?: string;
  weight?: number;
}

export interface KnowledgeGraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}
