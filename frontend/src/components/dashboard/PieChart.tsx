import React from 'react';
import { PieChart as RePieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';

interface SkillCoveragePieProps {
  coveredCount?: number;
  partialCount?: number;
  gapCount?: number;
}

const COLORS = ['#10b981', '#f59e0b', '#ef4444'];

export const PieChartWidget: React.FC<SkillCoveragePieProps> = ({
  coveredCount = 4,
  partialCount = 3,
  gapCount = 4,
}) => {
  const data = [
    { name: 'Covered Skills', value: coveredCount },
    { name: 'Partial Skills', value: partialCount },
    { name: 'Gap Skills', value: gapCount },
  ];

  return (
    <div className="flex flex-col p-5 rounded-2xl border border-border/50 bg-card shadow-sm">
      <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1">
        Skill Coverage Distribution
      </h4>
      <p className="text-xs text-muted-foreground mb-4">Breakdown of curriculum skill alignment statuses</p>

      <div className="h-56 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <RePieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={50}
              outerRadius={75}
              paddingAngle={4}
              dataKey="value"
            >
              {data.map((_, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: 'rgba(15, 23, 42, 0.9)',
                borderRadius: '12px',
                border: 'none',
                color: '#fff',
                fontSize: '12px',
              }}
            />
            <Legend verticalAlign="bottom" height={36} iconType="circle" wrapperStyle={{ fontSize: '12px' }} />
          </RePieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
