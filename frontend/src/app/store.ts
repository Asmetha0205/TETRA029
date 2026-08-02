import { create } from 'zustand';
import { UnifiedAnalysisResult } from '../types/api';
import { MOCK_ANALYSIS_RESULT } from '../services/mockData';

interface AppState {
  // Active Analysis
  activeAnalysis: UnifiedAnalysisResult | null;
  setActiveAnalysis: (analysis: UnifiedAnalysisResult) => void;

  // Analysis History
  analysisHistory: UnifiedAnalysisResult[];
  addAnalysisToHistory: (analysis: UnifiedAnalysisResult) => void;

  // Sidebar
  sidebarCollapsed: boolean;
  toggleSidebar: () => void;

  // Search & Filters
  searchQuery: string;
  setSearchQuery: (query: string) => void;

  selectedCategory: string;
  setSelectedCategory: (category: string) => void;

  selectedPriority: string;
  setSelectedPriority: (priority: string) => void;

  // Upload state tracking
  uploadProgress: number;
  setUploadProgress: (progress: number) => void;
  isUploading: boolean;
  setIsUploading: (uploading: boolean) => void;
}

export const useAppStore = create<AppState>((set) => ({
  activeAnalysis: MOCK_ANALYSIS_RESULT,
  setActiveAnalysis: (analysis) => set({ activeAnalysis: analysis }),

  analysisHistory: [MOCK_ANALYSIS_RESULT],
  addAnalysisToHistory: (analysis) =>
    set((state) => ({
      analysisHistory: [analysis, ...state.analysisHistory.filter((a) => a.analysis_id !== analysis.analysis_id)],
    })),

  sidebarCollapsed: false,
  toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),

  searchQuery: '',
  setSearchQuery: (query) => set({ searchQuery: query }),

  selectedCategory: 'ALL',
  setSelectedCategory: (category) => set({ selectedCategory: category }),

  selectedPriority: 'ALL',
  setSelectedPriority: (priority) => set({ selectedPriority: priority }),

  uploadProgress: 0,
  setUploadProgress: (progress) => set({ uploadProgress: progress }),
  isUploading: false,
  setIsUploading: (uploading) => set({ isUploading: uploading }),
}));
