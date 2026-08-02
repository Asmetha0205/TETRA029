export const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export const NAVIGATION_ITEMS = [
  { path: '/dashboard', label: 'Dashboard', icon: 'LayoutDashboard' },
  { path: '/upload', label: 'Upload Curriculum', icon: 'UploadCloud' },
  { path: '/gap-analysis', label: 'Gap Analysis', icon: 'Scale' },
  { path: '/recommendations', label: 'Recommendations', icon: 'Sparkles' },
  { path: '/learning-path', label: 'Learning Path', icon: 'MapPin' },
  { path: '/knowledge-graph', label: 'Knowledge Graph', icon: 'Network' },
  { path: '/industry-trends', label: 'Industry Trends', icon: 'TrendingUp' },
  { path: '/report', label: 'Executive Report', icon: 'FileText' },
];

export const PIPELINE_STAGES = [
  { id: 1, key: 'uploading', name: 'Uploading Document', desc: 'Securely uploading PDF file to server' },
  { id: 2, key: 'parsing', name: 'Parsing & Extraction', desc: 'Extracting course structures, topics, and Bloom levels' },
  { id: 3, key: 'skill_extraction', name: 'Skill Extraction', desc: 'Mapping raw text to taxonomy concepts' },
  { id: 4, key: 'normalization', name: 'Taxonomy Normalization', desc: 'Standardizing skill nodes against IEEE/ACM guidelines' },
  { id: 5, key: 'semantic_matching', name: 'Semantic Matching', desc: 'Computing cosine similarity against industry vector db' },
  { id: 6, key: 'gap_analysis', name: 'Gap & Delta Scoring', desc: 'Calculating skill coverage, partials, and critical gaps' },
  { id: 7, key: 'recommendations', name: 'Graph Recommendations', desc: 'Generating tailored learning paths and course modules' },
  { id: 8, key: 'completed', name: 'Analysis Complete', desc: 'Unified intelligence report generated successfully' },
];
