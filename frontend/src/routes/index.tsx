import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { MainLayout } from '../layouts/MainLayout';
import { AuthLayout } from '../layouts/AuthLayout';

import { LandingPage } from '../pages/LandingPage';
import { DashboardPage } from '../pages/DashboardPage';
import { UploadPage } from '../pages/UploadPage';
import { AnalysisProgressPage } from '../pages/AnalysisProgressPage';
import { GapAnalysisPage } from '../pages/GapAnalysisPage';
import { RecommendationPage } from '../pages/RecommendationPage';
import { LearningPathPage } from '../pages/LearningPathPage';
import { KnowledgeGraphPage } from '../pages/KnowledgeGraphPage';
import { IndustryTrendsPage } from '../pages/IndustryTrendsPage';
import { ReportPage } from '../pages/ReportPage';

import { LoginPage } from '../pages/LoginPage';
import { RegisterPage } from '../pages/RegisterPage';
import { ForgotPasswordPage } from '../pages/ForgotPasswordPage';
import { NotFoundPage } from '../pages/NotFoundPage';

export const AppRoutes: React.FC = () => {
  return (
    <Routes>
      {/* Main SaaS Platform Layout */}
      <Route path="/" element={<MainLayout />}>
        <Route index element={<LandingPage />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="upload" element={<UploadPage />} />
        <Route path="analysis/:id/progress" element={<AnalysisProgressPage />} />
        <Route path="gap-analysis" element={<GapAnalysisPage />} />
        <Route path="recommendations" element={<RecommendationPage />} />
        <Route path="learning-path" element={<LearningPathPage />} />
        <Route path="knowledge-graph" element={<KnowledgeGraphPage />} />
        <Route path="industry-trends" element={<IndustryTrendsPage />} />
        <Route path="report" element={<ReportPage />} />
      </Route>

      {/* Auth Placeholder Layout */}
      <Route element={<AuthLayout />}>
        <Route path="login" element={<LoginPage />} />
        <Route path="register" element={<RegisterPage />} />
        <Route path="forgot-password" element={<ForgotPasswordPage />} />
      </Route>

      {/* Catch-all 404 Route */}
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
};
