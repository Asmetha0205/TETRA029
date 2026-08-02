import React from 'react';
import {
  Radar,
  RadarChart as ReRadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from 'recharts';

interface RadarChartProps {
  title?: string;
  subtitle?: string;
}

const radarData = [
  { subject: 'Core Algorithms', Academic: 95, Industry: 92 },
  { subject: 'Systems & OS', Academic: 88, Industry: 85 },
  { subject: 'Web & Cloud', Academic: 55, Industry: 94 },
  { subject: 'DevOps & IaC', Academic: 20, Industry: 91 },
  { subject: 'AI & Data Science', Academic: 60, Industry: 98 },
  { subject: 'Database Management', Academic: 90, Industry: 89 },
];

export const RadarChartWidget: React.FC<RadarChartProps> = ({
  title = 'Domain Competency Radar',
  subtitle = 'Academic syllabus depth vs Industry job expectation',
}) => {
  return (
    <div className="flex flex-col p-5 rounded-2xl border border-border/50 bg-card shadow-sm">
      <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1">
        {title}
      </h4>
      <p className="text-xs text-muted-foreground mb-2">{subtitle}</p>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ReRadarChart cx="50%" cy="50%" outerRadius="75%" data={radarData}>
            <PolarGrid strokeOpacity={0.2} />
            <PolarAngleAxis dataKey="subject" tick={{ fontSize: 10, fill: 'currentColor' }} />
            <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fontSize: 9 }} />
            <Radar name="Academic Syllabus" dataKey="Academic" stroke="#10b981" fill="#10b981" fillOpacity={0.3} />
            <Radar name="Industry Market" dataKey="Industry" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.3} />
            <Tooltip
              contentStyle={{
                backgroundColor: 'rgba(15, 23, 42, 0.9)',
                borderRadius: '12px',
                border: 'none',
                color: '#fff',
                fontSize: '12px',
              }}
            />
            <Legend verticalAlign="bottom" height={30} iconType="circle" wrapperStyle={{ fontSize: '11px' }} />
          </ReRadarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
