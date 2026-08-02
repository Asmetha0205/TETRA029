import React from 'react';
import {
  BarChart as ReBarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

interface BarChartWidgetProps {
  data?: Array<{ name: string; score: number }>;
  title?: string;
  subtitle?: string;
}

const defaultData = [
  { name: 'Docker', score: 98 },
  { name: 'RAG & Vector Search', score: 97 },
  { name: 'Kubernetes', score: 95 },
  { name: 'React 19 / TS', score: 94 },
  { name: 'FastAPI / Python', score: 92 },
  { name: 'Terraform IaC', score: 91 },
];

export const BarChartWidget: React.FC<BarChartWidgetProps> = ({
  data = defaultData,
  title = 'Top Industry Demand Gaps',
  subtitle = 'Industry market frequency & priority score (0 - 100)',
}) => {
  return (
    <div className="flex flex-col p-5 rounded-2xl border border-border/50 bg-card shadow-sm">
      <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1">
        {title}
      </h4>
      <p className="text-xs text-muted-foreground mb-4">{subtitle}</p>

      <div className="h-60 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ReBarChart data={data} layout="vertical" margin={{ top: 5, right: 20, left: 40, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" opacity={0.1} />
            <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 11 }} />
            <YAxis dataKey="name" type="category" tick={{ fontSize: 11 }} width={110} />
            <Tooltip
              contentStyle={{
                backgroundColor: 'rgba(15, 23, 42, 0.9)',
                borderRadius: '12px',
                border: 'none',
                color: '#fff',
                fontSize: '12px',
              }}
            />
            <Bar dataKey="score" fill="#6366f1" radius={[0, 8, 8, 0]} />
          </ReBarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
