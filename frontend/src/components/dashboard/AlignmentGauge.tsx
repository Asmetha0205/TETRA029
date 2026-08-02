import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import { formatScoreColor } from '../../utils/formatters';

interface AlignmentGaugeProps {
  score: number; // 0 to 100
  title?: string;
  subtitle?: string;
}

export const AlignmentGauge: React.FC<AlignmentGaugeProps> = ({
  score = 72.8,
  title = 'Overall Curriculum Alignment',
  subtitle = 'Cosine Vector Similarity against Live Industry Knowledge Graph',
}) => {
  const data = [
    { name: 'Aligned', value: score },
    { name: 'Gap Delta', value: Math.max(0, 100 - score) },
  ];

  const colors = formatScoreColor(score);
  const gaugeColor = score >= 80 ? '#10b981' : score >= 60 ? '#f59e0b' : '#ef4444';

  return (
    <div className="flex flex-col items-center justify-center p-6 rounded-2xl border border-border/50 bg-card shadow-sm text-center">
      <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1">
        {title}
      </h4>
      <p className="text-[11px] text-muted-foreground max-w-xs mb-4">{subtitle}</p>

      <div className="relative h-44 w-full max-w-[220px] flex items-center justify-center">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={62}
              outerRadius={80}
              startAngle={180}
              endAngle={0}
              dataKey="value"
              stroke="none"
              cornerRadius={6}
            >
              <Cell key="cell-0" fill={gaugeColor} />
              <Cell key="cell-1" fill="rgba(156, 163, 175, 0.15)" />
            </Pie>
          </PieChart>
        </ResponsiveContainer>

        <div className="absolute inset-0 flex flex-col items-center justify-center pt-6">
          <span className={`text-3xl font-extrabold tracking-tight ${colors.text}`}>
            {score}%
          </span>
          <span className={`mt-1 text-[10px] font-bold px-2 py-0.5 rounded-full ${colors.badge}`}>
            {score >= 80 ? 'STRONG ALIGNMENT' : score >= 60 ? 'MODERATE GAP' : 'CRITICAL DELTA'}
          </span>
        </div>
      </div>
    </div>
  );
};
