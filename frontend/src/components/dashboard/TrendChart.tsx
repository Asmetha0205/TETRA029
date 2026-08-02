import React from 'react';
import {
  LineChart as ReLineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

const trendData = [
  { month: 'Jan', VectorSearch: 45, CloudNative: 65, React19: 50 },
  { month: 'Feb', VectorSearch: 58, CloudNative: 72, React19: 55 },
  { month: 'Mar', VectorSearch: 72, CloudNative: 80, React19: 68 },
  { month: 'Apr', VectorSearch: 89, CloudNative: 88, React19: 78 },
  { month: 'May', VectorSearch: 120, CloudNative: 95, React19: 85 },
  { month: 'Jun', VectorSearch: 165, CloudNative: 105, React19: 98 },
];

export const TrendChartWidget: React.FC = () => {
  return (
    <div className="flex flex-col p-5 rounded-2xl border border-border/50 bg-card shadow-sm">
      <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1">
        Industry Skill Demand Growth (YoY %)
      </h4>
      <p className="text-xs text-muted-foreground mb-4">6-month trend trajectory for emerging technologies</p>

      <div className="h-60 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ReLineChart data={trendData} margin={{ top: 10, right: 20, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" opacity={0.1} />
            <XAxis dataKey="month" tick={{ fontSize: 11 }} />
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
            <Legend verticalAlign="top" height={36} wrapperStyle={{ fontSize: '11px' }} />
            <Line type="monotone" dataKey="VectorSearch" stroke="#ec4899" strokeWidth={3} dot={{ r: 4 }} />
            <Line type="monotone" dataKey="CloudNative" stroke="#6366f1" strokeWidth={2} />
            <Line type="monotone" dataKey="React19" stroke="#10b981" strokeWidth={2} />
          </ReLineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
