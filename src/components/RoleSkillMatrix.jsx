import React, { useState } from 'react';
import roleMap from '../data/role_skill_map.json';
import skillBase from '../data/industry_skill_base.json';
import { Briefcase, CheckCircle, Flame, Shield, Server, Code, Sparkles, Cpu } from 'lucide-react';

const ROLE_META = {
  data_scientist: { name: 'Data Scientist', icon: Cpu, color: 'from-cyan-500 to-blue-600', badge: 'NSQF Level 7' },
  ml_engineer: { name: 'ML Engineer', icon: Sparkles, color: 'from-purple-500 to-pink-600', badge: 'NSQF Level 7' },
  full_stack: { name: 'Full-Stack Developer', icon: Code, color: 'from-emerald-500 to-teal-600', badge: 'NSQF Level 6' },
  cloud_engineer: { name: 'Cloud Engineer', icon: Server, color: 'from-sky-500 to-indigo-600', badge: 'NSQF Level 6' },
  cyber_analyst: { name: 'Cyber Security Analyst', icon: Shield, color: 'from-rose-500 to-red-600', badge: 'NSQF Level 6' }
};

export default function RoleSkillMatrix() {
  const [selectedRole, setSelectedRole] = useState('data_scientist');

  const skillLookup = React.useMemo(() => {
    const map = new Map();
    skillBase.forEach(s => map.set(s.id, s));
    return map;
  }, []);

  const activeSkillIds = roleMap[selectedRole] || [];
  const activeSkills = activeSkillIds.map(id => skillLookup.get(id)).filter(Boolean);

  const avgDemand = activeSkills.length > 0
    ? (activeSkills.reduce((acc, s) => acc + s.demand_score, 0) / activeSkills.length * 100).toFixed(1)
    : 0;

  const emergingSkillsCount = activeSkills.filter(s =>
    ['skill_generative_ai', 'skill_llm', 'skill_rag', 'skill_vectordb', 'skill_prompt_eng', 'skill_ai_agents'].includes(s.id)
  ).length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="glass-panel p-5 rounded-2xl border border-slate-800 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-amber-500/10 rounded-xl border border-amber-500/20 text-amber-400">
            <Briefcase className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
              Role Skill Demand Matrix
              <span className="px-2.5 py-0.5 text-xs font-semibold bg-amber-500/20 text-amber-300 border border-amber-500/30 rounded-full">
                5 Job Roles &bull; NSQF / SSC Aligned
              </span>
            </h2>
            <p className="text-xs text-slate-400">
              `role_skill_map.json` — Drives Member 1's per-role alignment score formula (weights each skill by demand_score)
            </p>
          </div>
        </div>
      </div>

      {/* Role Selection Tabs */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
        {Object.keys(roleMap).map(roleId => {
          const meta = ROLE_META[roleId] || { name: roleId, icon: Briefcase, color: 'from-slate-600 to-slate-700' };
          const Icon = meta.icon;
          const isSelected = selectedRole === roleId;

          return (
            <button
              key={roleId}
              onClick={() => setSelectedRole(roleId)}
              className={`p-3.5 rounded-2xl border text-left transition-all ${
                isSelected
                  ? 'bg-slate-900 border-amber-500/50 shadow-xl shadow-amber-500/10'
                  : 'bg-slate-900/50 border-slate-800/80 hover:bg-slate-800/60'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <div className={`p-2 rounded-xl bg-gradient-to-br ${meta.color} text-white shadow-md`}>
                  <Icon className="w-4 h-4" />
                </div>
                <span className="text-[10px] font-mono text-slate-400">
                  {roleMap[roleId]?.length} skills
                </span>
              </div>
              <div className="font-bold text-xs text-white truncate">{meta.name}</div>
              <div className="text-[10px] text-slate-500 font-mono mt-0.5">{roleId}</div>
            </button>
          );
        })}
      </div>

      {/* Selected Role Detail Panel */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-6">
        <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-4">
          <div>
            <span className="text-xs font-semibold text-amber-400 uppercase tracking-wider">Active Role Filter</span>
            <h3 className="text-2xl font-extrabold text-white">
              {ROLE_META[selectedRole]?.name}
            </h3>
            <code className="text-xs text-slate-400 font-mono">role_id: "{selectedRole}"</code>
          </div>

          <div className="flex flex-wrap gap-4 text-xs">
            <div className="bg-slate-900 px-4 py-2 rounded-xl border border-slate-800">
              <span className="text-slate-400 block">Avg Demand Index</span>
              <span className="text-lg font-bold text-amber-300">{avgDemand}%</span>
            </div>
            <div className="bg-slate-900 px-4 py-2 rounded-xl border border-slate-800">
              <span className="text-slate-400 block">EmergingTech Skills</span>
              <span className="text-lg font-bold text-rose-400 flex items-center gap-1">
                {emergingSkillsCount} <Flame className="w-4 h-4 inline" />
              </span>
            </div>
          </div>
        </div>

        {/* Demanded Skills Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {activeSkills.map(skill => {
            const isEmerging = ['skill_generative_ai', 'skill_llm', 'skill_rag', 'skill_vectordb', 'skill_prompt_eng', 'skill_ai_agents'].includes(skill.id);

            return (
              <div
                key={skill.id}
                className={`p-4 rounded-xl border transition-all ${
                  isEmerging
                    ? 'bg-rose-950/20 border-rose-500/30'
                    : 'bg-slate-900/70 border-slate-800'
                }`}
              >
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <h4 className="font-bold text-sm text-white flex items-center gap-1.5">
                      {skill.name}
                      {isEmerging && <Flame className="w-3.5 h-3.5 text-rose-400 shrink-0" />}
                    </h4>
                    <code className="text-[11px] text-slate-400 font-mono">{skill.id}</code>
                  </div>
                  <span className="text-xs font-mono font-bold text-emerald-400 px-2 py-0.5 bg-slate-800 rounded">
                    {(skill.demand_score * 100).toFixed(0)}%
                  </span>
                </div>

                <div className="flex items-center justify-between text-xs mt-3 pt-2 border-t border-slate-800/80">
                  <span className="text-slate-400">{skill.category}</span>
                  <span className={`capitalize text-[11px] font-semibold ${
                    skill.trend === 'rising' ? 'text-rose-400' : 'text-slate-300'
                  }`}>
                    {skill.trend}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
