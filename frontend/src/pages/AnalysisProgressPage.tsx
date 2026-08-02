import React from 'react';
import { useParams } from 'react-router-dom';
import { PageTransition } from '../components/animation/PageTransition';
import { ProgressTimeline } from '../components/analysis/ProgressTimeline';

export const AnalysisProgressPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  return (
    <PageTransition>
      <div className="py-6">
        <ProgressTimeline analysisId={id || 'analysis_demo_2026_0802'} />
      </div>
    </PageTransition>
  );
};
