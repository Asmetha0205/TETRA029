import React, { useState } from 'react';
import PdfSyllabusAnalyzer from './components/PdfSyllabusAnalyzer';
import GraphExplorer from './components/GraphExplorer';
import SkillBaseTable from './components/SkillBaseTable';
import AliasTester from './components/AliasTester';
import RoleSkillMatrix from './components/RoleSkillMatrix';
import AuraDBStatusCard from './components/AuraDBStatusCard';

import { FileText, Network, Database, Tag, Briefcase, Server, Sparkles, CheckCircle2, ShieldAlert, Cpu } from 'lucide-react';

import skillBase from './data/industry_skill_base.json';
import aliasMap from './data/skill_aliases.json';
import roleMap from './data/role_skill_map.json';
import graphData from './data/graph_sample.json';

export default function App() {
  const [activeTab, setActiveTab] = useState('pdf');

  const tabs = [
    { id: 'pdf', label: 'PDF Syllabus & Skills UI', icon: FileText, badge: 'Light Mode' },
    { id: 'graph', label: 'Knowledge Graph', icon: Network, badge: `${graphData.nodes.length} Nodes` },
    { id: 'skills', label: 'Industry Skill Base', icon: Database, badge: `${skillBase.length} Skills` },
    { id: 'aliases', label: 'Alias Normalization', icon: Tag, badge: `${Object.keys(aliasMap).length} Map Entries` },
    { id: 'roles', label: 'Role Skill Matrix', icon: Briefcase, badge: '5 Roles' },
    { id: 'auradb', label: 'Neo4j AuraDB & CLI', icon: Server, badge: 'CLI Driver' },
  ];

  return (
    <div className="min-h-screen bg-[#030712] text-slate-100 flex flex-col selection:bg-cyan-500 selection:text-white">
      {/* Top Banner */}
      <header className="border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 rounded-xl bg-gradient-to-tr from-cyan-600 via-teal-500 to-emerald-400 text-slate-950 font-black shadow-lg shadow-cyan-500/20">
              <Cpu className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-extrabold tracking-tight text-white font-sans">
                  CurricuAlign AI
                </h1>
                <span className="px-2 py-0.5 text-[10px] font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 rounded-md">
                  MEMBER 3 — Indian Data & Knowledge Graph Lead
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Data + Knowledge Graph Layer &bull; EdTech Track &bull; Unblocking Member 1 & Member 2
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold">
              <CheckCircle2 className="w-4 h-4" />
              <span>Team Unblocked (v0 Released)</span>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Stats */}
      <section className="border-b border-slate-800/50 bg-slate-950/40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-5">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-center">
            <div className="p-3 bg-slate-900/40 rounded-xl border border-slate-800/60">
              <div className="text-2xl font-extrabold text-white">{skillBase.length}</div>
              <div className="text-xs text-slate-400 font-medium">Industry Skills (6 Domains)</div>
            </div>
            <div className="p-3 bg-slate-900/40 rounded-xl border border-slate-800/60">
              <div className="text-2xl font-extrabold text-purple-400">{Object.keys(aliasMap).length}</div>
              <div className="text-xs text-slate-400 font-medium">Syllabus Aliases Normalized</div>
            </div>
            <div className="p-3 bg-slate-900/40 rounded-xl border border-slate-800/60">
              <div className="text-2xl font-extrabold text-amber-400">5</div>
              <div className="text-xs text-slate-400 font-medium">NSQF Job Roles Mapped</div>
            </div>
            <div className="p-3 bg-slate-900/40 rounded-xl border border-slate-800/60">
              <div className="text-2xl font-extrabold text-rose-400">{graphData.nodes.length} / {graphData.edges.length}</div>
              <div className="text-xs text-slate-400 font-medium">Neo4j Nodes & Edges</div>
            </div>
          </div>
        </div>
      </section>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        {/* Navigation Tabs */}
        <nav className="flex flex-wrap gap-2 p-1.5 bg-slate-900/80 rounded-2xl border border-slate-800">
          {tabs.map(t => {
            const Icon = t.icon;
            const isActive = activeTab === t.id;
            return (
              <button
                key={t.id}
                onClick={() => setActiveTab(t.id)}
                className={`flex-1 min-w-[160px] flex items-center justify-center space-x-2 px-4 py-3 text-xs font-bold rounded-xl transition-all ${
                  isActive
                    ? 'bg-gradient-to-r from-cyan-500/20 to-blue-500/20 text-cyan-300 border border-cyan-500/40 shadow-lg shadow-cyan-500/10'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 border border-transparent'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
                <span>{t.label}</span>
                <span className={`ml-1 text-[10px] px-1.5 py-0.5 rounded-full ${
                  isActive ? 'bg-cyan-500/30 text-cyan-200' : 'bg-slate-800 text-slate-500'
                }`}>
                  {t.badge}
                </span>
              </button>
            );
          })}
        </nav>

        {/* Tab Content */}
        <div className="transition-all duration-300">
          {activeTab === 'pdf' && <PdfSyllabusAnalyzer />}
          {activeTab === 'graph' && <GraphExplorer />}
          {activeTab === 'skills' && <SkillBaseTable />}
          {activeTab === 'aliases' && <AliasTester />}
          {activeTab === 'roles' && <RoleSkillMatrix />}
          {activeTab === 'auradb' && <AuraDBStatusCard />}
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-950 py-6 text-center text-xs text-slate-500 font-mono">
        <div className="max-w-7xl mx-auto px-4 flex flex-wrap justify-between items-center gap-4">
          <div>
            CurricuAlign AI &bull; Member 3 Indian Data & Knowledge Graph Layer
          </div>
          <div className="flex gap-4">
            <a href="file:///c:/Users/malav/Downloads/Tetrathon_2026/industry_skill_base.json" className="hover:text-slate-300">FILE 1: industry_skill_base.json</a>
            <a href="file:///c:/Users/malav/Downloads/Tetrathon_2026/skill_aliases.json" className="hover:text-slate-300">FILE 2: skill_aliases.json</a>
            <a href="file:///c:/Users/malav/Downloads/Tetrathon_2026/role_skill_map.json" className="hover:text-slate-300">FILE 3: role_skill_map.json</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
