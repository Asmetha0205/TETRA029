import React from 'react';
import {
  AreaChart as ReAreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

const areaData = [
  { year: '2021', TraditionalCS: 85, CloudDevOps: 20, AI_RAG: 5 },
  { year: '2022', TraditionalCS: 82, CloudDevOps: 38, AI_RAG: 12 },
  { year: '2023', TraditionalCS: 78, CloudDevOps: 58, AI_RAG: 35 },
  { year: '2024', TraditionalCS: 75, CloudDevOps: 75, AI_RAG: 65 },
  { year: '2025', TraditionalCS: 70, CloudDevOps: 88, AI_RAG: 92 },
  { year: '2026', TraditionalCS: 68, CloudDevOps: 95, AI_RAG: 140 },
];

export const AreaChartWidget: React.FC = () => {
  return (
    <div className="flex flex-col p-5 rounded-2xl border border-border/50 bg-card shadow-sm">
      <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1">
        Cumulative Demand Expansion
      </h4>
      <p className="text-xs text-muted-foreground mb-4">Shift from traditional CS to Cloud-Native & AI stacks</p>

      <div className="h-60 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ReAreaChart data={areaData} margin={{ top: 10, right: 20, left: 0, bottom: 5 }}>
            <defs>
              <linearGradient id="colorAI" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="colorCloud" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" opacity={0.1} />
            <XAxis dataKey="year" tick={{ fontSize: 11 }} />
            <YAxis tick={{ fontSize: 11 }} />
            <Tooltip
              contentStyle={{
                backgroundColor: 'rgba(15, 23, 42, 0.9)',
                borderRadius: '12px',
                border: 'none',
                color: '#fff',
                fontSize: '12px',
              }}
            />
            <Area type="monotone" dataKey="AI_RAG" stroke="#8b5cf6" fillOpacity={1} fill="url(#colorAI)" />
            <Area type="monotone" dataKey="CloudDevOps" stroke="#3b82f6" fillOpacity={1} fill="url(#colorCloud)" />
          </ReAreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
