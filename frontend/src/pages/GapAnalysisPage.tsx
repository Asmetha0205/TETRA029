import React, { useState, useMemo } from 'react';
import { PageTransition } from '../components/animation/PageTransition';
import { GapTable } from '../components/gap/GapTable';
import { SearchBar } from '../components/gap/SearchBar';
import { FilterPanel } from '../components/gap/FilterPanel';
import { EvidencePanel } from '../components/gap/EvidencePanel';
import { SkillGapItem } from '../types/api';
import { useAppStore } from '../app/store';

export const GapAnalysisPage: React.FC = () => {
  const { activeAnalysis, searchQuery, setSearchQuery, selectedCategory, setSelectedCategory, selectedPriority, setSelectedPriority } = useAppStore();
  const [selectedEvidenceItem, setSelectedEvidenceItem] = useState<SkillGapItem | null>(null);

  const allSkills: SkillGapItem[] = useMemo(() => {
    if (!activeAnalysis) return [];
    return [
      ...(activeAnalysis.gap_skills || []),
      ...(activeAnalysis.partial_skills || []),
      ...(activeAnalysis.covered_skills || []),
    ];
  }, [activeAnalysis]);

  const categories = useMemo(() => {
    const set = new Set<string>();
    allSkills.forEach((s) => s.category && set.add(s.category));
    return Array.from(set);
  }, [allSkills]);

  const priorities = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];

  const filteredSkills = useMemo(() => {
    return allSkills.filter((item) => {
      const matchesSearch =
        !searchQuery ||
        item.matched_industry_skill.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.academic_skill.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.category.toLowerCase().includes(searchQuery.toLowerCase());

      const matchesCategory = selectedCategory === 'ALL' || item.category === selectedCategory;
      const matchesPriority = selectedPriority === 'ALL' || item.priority === selectedPriority;

      return matchesSearch && matchesCategory && matchesPriority;
    });
  }, [allSkills, searchQuery, selectedCategory, selectedPriority]);

  return (
    <PageTransition>
      <div className="space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl md:text-3xl font-extrabold text-foreground tracking-tight">
              Curriculum Skill Gap Matrix
            </h1>
            <p className="text-xs text-muted-foreground mt-0.5">
              Interactive similarity matching table comparing academic syllabus concepts against real job market demand.
            </p>
          </div>
          <SearchBar value={searchQuery} onChange={setSearchQuery} />
        </div>

        {/* Filter Panel */}
        <FilterPanel
          categories={categories}
          selectedCategory={selectedCategory}
          onSelectCategory={setSelectedCategory}
          priorities={priorities}
          selectedPriority={selectedPriority}
          onSelectPriority={setSelectedPriority}
        />

        {/* Gap Table */}
        <GapTable items={filteredSkills} onSelectEvidence={(item) => setSelectedEvidenceItem(item)} />

        {/* Slide-over Evidence Panel */}
        <EvidencePanel item={selectedEvidenceItem} onClose={() => setSelectedEvidenceItem(null)} />
      </div>
    </PageTransition>
  );
};
