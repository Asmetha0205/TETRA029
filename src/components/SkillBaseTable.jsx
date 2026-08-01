import React, { useState, useMemo } from 'react';
import skillBase from '../data/industry_skill_base.json';
import { Database, TrendingUp, TrendingDown, Minus, Search, Tag, ExternalLink, ShieldAlert, Sparkles } from 'lucide-react';

const CATEGORIES = ['ALL', 'AI/ML', 'Cloud', 'Cybersecurity', 'Data/Big Data', 'Web/Full-Stack', 'DevOps'];

export default function SkillBaseTable() {
  const [activeCategory, setActiveCategory] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [trendFilter, setTrendFilter] = useState('ALL');

  const filteredSkills = useMemo(() => {
    return skillBase.filter(skill => {
      if (activeCategory !== 'ALL' && skill.category !== activeCategory) return false;
      if (trendFilter !== 'ALL' && skill.trend !== trendFilter) return false;
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        const matchesName = skill.name.toLowerCase().includes(query);
        const matchesId = skill.id.toLowerCase().includes(query);
        const matchesAlias = skill.aliases.some(a => a.toLowerCase().includes(query));
        return matchesName || matchesId || matchesAlias;
      }
      return true;
    });
  }, [activeCategory, trendFilter, searchQuery]);

  return (
    <div className="space-y-6">
      {/* Summary Header */}
      <div className="glass-panel p-5 rounded-2xl flex flex-wrap items-center justify-between gap-4 border border-slate-800">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-emerald-500/10 rounded-xl border border-emerald-500/20 text-emerald-400">
            <Database className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
              Industry Skill Base Taxonomy
              <span className="px-2.5 py-0.5 text-xs font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 rounded-full">
                {skillBase.length} Curated Records
              </span>
            </h2>
            <p className="text-xs text-slate-400">
              Hand-curated against NASSCOM FutureSkills & NSQF Sector Skill Council definitions
            </p>
          </div>
        </div>

        {/* Filter Controls */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Filter skills or aliases..."
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              className="pl-9 pr-4 py-1.5 text-sm bg-slate-900/90 border border-slate-700/80 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 w-56"
            />
          </div>

          <select
            value={trendFilter}
            onChange={e => setTrendFilter(e.target.value)}
            className="px-3 py-1.5 text-sm bg-slate-900/90 border border-slate-700/80 rounded-xl text-white focus:outline-none focus:border-emerald-500"
          >
            <option value="ALL">All Trends</option>
            <option value="rising">Rising 🔥</option>
            <option value="stable">Stable ⚖️</option>
            <option value="declining">Declining 📉</option>
          </select>
        </div>
      </div>

      {/* Category Pills */}
      <div className="flex flex-wrap gap-2">
        {CATEGORIES.map(cat => (
          <button
            key={cat}
            onClick={() => setActiveCategory(cat)}
            className={`px-4 py-2 text-xs font-semibold rounded-xl border transition-all ${
              activeCategory === cat
                ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40 shadow-lg shadow-emerald-500/10'
                : 'bg-slate-900/60 text-slate-400 border-slate-800 hover:bg-slate-800 hover:text-slate-200'
            }`}
          >
            {cat}
            {cat !== 'ALL' && (
              <span className="ml-2 text-[10px] opacity-75">
                ({skillBase.filter(s => s.category === cat).length})
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Skills Data Table */}
      <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-900/90 text-xs uppercase tracking-wider text-slate-400 border-b border-slate-800">
              <tr>
                <th className="py-3.5 px-4 font-bold">Canonical Skill Name</th>
                <th className="py-3.5 px-4 font-bold">Category</th>
                <th className="py-3.5 px-4 font-bold">Demand Score</th>
                <th className="py-3.5 px-4 font-bold">Trend</th>
                <th className="py-3.5 px-4 font-bold">Aliases</th>
                <th className="py-3.5 px-4 font-bold">Sources</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filteredSkills.map(skill => {
                const isGenAiCluster = [
                  'skill_generative_ai', 'skill_llm', 'skill_rag',
                  'skill_vectordb', 'skill_prompt_eng', 'skill_ai_agents'
                ].includes(skill.id);

                return (
                  <tr key={skill.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3.5 px-4">
                      <div className="flex items-center space-x-2">
                        {isGenAiCluster && (
                          <Sparkles className="w-4 h-4 text-rose-400 shrink-0 animate-pulse" />
                        )}
                        <div>
                          <div className="font-bold text-white flex items-center gap-1.5">
                            {skill.name}
                            {isGenAiCluster && (
                              <span className="text-[10px] bg-rose-500/20 text-rose-300 px-1.5 py-0.5 rounded border border-rose-500/30">
                                GenAI Gap Engine
                              </span>
                            )}
                          </div>
                          <code className="text-[11px] text-slate-400 font-mono">{skill.id}</code>
                        </div>
                      </div>
                    </td>

                    <td className="py-3.5 px-4">
                      <span className="px-2.5 py-1 text-xs rounded-lg font-medium bg-slate-800 text-slate-300 border border-slate-700">
                        {skill.category}
                      </span>
                    </td>

                    <td className="py-3.5 px-4">
                      <div className="w-32">
                        <div className="flex justify-between text-xs mb-1">
                          <span className="font-mono font-bold text-slate-200">{(skill.demand_score * 100).toFixed(0)}%</span>
                          <span className="text-[10px] text-slate-400">Score: {skill.demand_score.toFixed(2)}</span>
                        </div>
                        <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full ${
                              skill.demand_score >= 0.85
                                ? 'bg-gradient-to-r from-emerald-400 to-cyan-400'
                                : skill.demand_score >= 0.70
                                ? 'bg-emerald-500'
                                : 'bg-amber-500'
                            }`}
                            style={{ width: `${skill.demand_score * 100}%` }}
                          />
                        </div>
                      </div>
                    </td>

                    <td className="py-3.5 px-4">
                      {skill.trend === 'rising' && (
                        <span className="inline-flex items-center gap-1 text-xs font-semibold text-rose-400 bg-rose-500/10 px-2.5 py-1 rounded-lg border border-rose-500/20">
                          <TrendingUp className="w-3.5 h-3.5" /> Rising
                        </span>
                      )}
                      {skill.trend === 'stable' && (
                        <span className="inline-flex items-center gap-1 text-xs font-semibold text-slate-300 bg-slate-800 px-2.5 py-1 rounded-lg border border-slate-700">
                          <Minus className="w-3.5 h-3.5" /> Stable
                        </span>
                      )}
                      {skill.trend === 'declining' && (
                        <span className="inline-flex items-center gap-1 text-xs font-semibold text-amber-400 bg-amber-500/10 px-2.5 py-1 rounded-lg border border-amber-500/20">
                          <TrendingDown className="w-3.5 h-3.5" /> Declining
                        </span>
                      )}
                    </td>

                    <td className="py-3.5 px-4 max-w-xs">
                      <div className="flex flex-wrap gap-1">
                        {skill.aliases.slice(0, 3).map((alias, i) => (
                          <span key={i} className="text-[11px] font-mono px-2 py-0.5 bg-slate-900 text-slate-400 rounded border border-slate-800">
                            {alias}
                          </span>
                        ))}
                        {skill.aliases.length > 3 && (
                          <span className="text-[10px] text-slate-500 px-1 py-0.5">
                            +{skill.aliases.length - 3} more
                          </span>
                        )}
                      </div>
                    </td>

                    <td className="py-3.5 px-4 text-xs text-slate-400">
                      <div className="space-y-1">
                        {skill.sources.map((src, i) => (
                          <div key={i} className="flex items-center gap-1 text-[11px]">
                            <ExternalLink className="w-3 h-3 text-cyan-400 shrink-0" />
                            <span>{src}</span>
                          </div>
                        ))}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
