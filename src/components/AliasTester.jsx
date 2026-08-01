import React, { useState } from 'react';
import aliasMap from '../data/skill_aliases.json';
import skillBase from '../data/industry_skill_base.json';
import { Tag, CheckCircle2, AlertCircle, ArrowRight, Sparkles, BookOpen } from 'lucide-react';

export default function AliasTester() {
  const [inputAlias, setInputAlias] = useState('gen ai');

  const normalizedInput = inputAlias.trim().toLowerCase();
  const matchedCanonical = aliasMap[normalizedInput] || null;

  const matchedSkillRecord = matchedCanonical
    ? skillBase.find(s => s.name.toLowerCase() === matchedCanonical.toLowerCase())
    : null;

  const presets = [
    'gen ai', 'RAG', 'LLM', 'K8s', 'ML', 'DL', 'NLP', 'pyspark',
    'tableau', 'agentic ai', 'docker', 'aws', 'ts', 'reactjs'
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="glass-panel p-5 rounded-2xl border border-slate-800 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-purple-500/10 rounded-xl border border-purple-500/20 text-purple-400">
            <Tag className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
              Syllabus Alias Normalization Engine
              <span className="px-2.5 py-0.5 text-xs font-semibold bg-purple-500/20 text-purple-300 border border-purple-500/30 rounded-full">
                {Object.keys(aliasMap).length} Normalized Map Entries
              </span>
            </h2>
            <p className="text-xs text-slate-400">
              `skill_aliases.json` — Maps syllabus text abbreviations to canonical industry skill IDs for Member 1 & Member 2
            </p>
          </div>
        </div>
      </div>

      {/* Interactive Tester */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <label className="block text-xs font-bold uppercase tracking-wider text-slate-300">
            Test Syllabus Skill Term / Abbreviation
          </label>
          <div className="relative">
            <input
              type="text"
              value={inputAlias}
              onChange={e => setInputAlias(e.target.value)}
              placeholder="e.g. RAG, K8s, GenAI, ML..."
              className="w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white font-mono placeholder-slate-500 focus:outline-none focus:border-purple-500 text-lg"
            />
          </div>

          <div>
            <span className="text-xs font-semibold text-slate-400 block mb-2">Quick Presets:</span>
            <div className="flex flex-wrap gap-2">
              {presets.map(p => (
                <button
                  key={p}
                  onClick={() => setInputAlias(p)}
                  className={`px-2.5 py-1 text-xs rounded-lg font-mono transition-all border ${
                    inputAlias.toLowerCase() === p.toLowerCase()
                      ? 'bg-purple-500/20 text-purple-300 border-purple-500/40'
                      : 'bg-slate-900 text-slate-400 border-slate-800 hover:border-slate-700 hover:text-white'
                  }`}
                >
                  {p}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Live Output Box */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex flex-col justify-between">
          <div>
            <div className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3 flex items-center justify-between">
              <span>Normalization Result</span>
              {matchedCanonical ? (
                <span className="text-emerald-400 flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" /> MATCH FOUND
                </span>
              ) : (
                <span className="text-amber-400 flex items-center gap-1">
                  <AlertCircle className="w-3.5 h-3.5" /> UNMAPPED TERM
                </span>
              )}
            </div>

            {matchedCanonical ? (
              <div className="space-y-4 bg-slate-900/90 p-4 rounded-xl border border-purple-500/30">
                <div className="flex items-center space-x-3">
                  <span className="text-slate-400 font-mono text-sm px-2.5 py-1 bg-slate-800 rounded">
                    "{inputAlias}"
                  </span>
                  <ArrowRight className="w-4 h-4 text-purple-400" />
                  <span className="text-lg font-bold text-emerald-300">
                    {matchedCanonical}
                  </span>
                </div>

                {matchedSkillRecord && (
                  <div className="border-t border-slate-800 pt-3 text-xs space-y-1.5">
                    <div className="flex justify-between">
                      <span className="text-slate-400">Canonical ID:</span>
                      <code className="text-cyan-400 font-mono">{matchedSkillRecord.id}</code>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Category:</span>
                      <span className="text-slate-200 font-medium">{matchedSkillRecord.category}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Demand Score:</span>
                      <span className="text-emerald-400 font-bold">{(matchedSkillRecord.demand_score * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="p-4 bg-slate-900/60 rounded-xl border border-slate-800 text-sm text-slate-400">
                No direct alias found for <code className="text-amber-300">"{inputAlias}"</code>.
                Member 2's vector engine performs fuzzy embedding similarity matching as secondary fallback!
              </div>
            )}
          </div>

          <div className="mt-4 pt-3 border-t border-slate-800 text-[11px] text-slate-500 font-mono">
            FILE 2: skill_aliases.json (Member 1 loads this for syllabus string normalization)
          </div>
        </div>
      </div>

      {/* Map Explorer Table */}
      <div className="glass-panel p-5 rounded-2xl border border-slate-800">
        <h3 className="text-sm font-bold text-white mb-3">Alias Catalog Sample (First 20 Mappings)</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
          {Object.entries(aliasMap).slice(0, 20).map(([alias, canonical], idx) => (
            <div key={idx} className="p-2.5 bg-slate-900/80 rounded-xl border border-slate-800/80 text-xs flex justify-between items-center">
              <span className="font-mono text-slate-400 truncate max-w-[100px]">{alias}</span>
              <span className="font-semibold text-purple-300 truncate max-w-[120px]">{canonical}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
