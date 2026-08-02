import React from 'react';
import { PageTransition } from '../components/animation/PageTransition';
import { KnowledgeGraph } from '../components/graph/KnowledgeGraph';

export const KnowledgeGraphPage: React.FC = () => {
  return (
    <PageTransition>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-foreground tracking-tight">
            Curriculum Knowledge Graph Visualizer
          </h1>
          <p className="text-xs text-muted-foreground mt-0.5">
            Interactive Neo4j graph structure mapping course nodes, prerequisite skills, target gaps, and job roles.
          </p>
        </div>

        <KnowledgeGraph />
      </div>
    </PageTransition>
  );
};
