"use client";

import {
  RadarChart as RechartsRadar,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

interface RadarDataPoint {
  category: string;
  score: number;
  previousScore?: number;
  fullMark?: number;
}

interface EvaluationRadarChartProps {
  data: RadarDataPoint[];
}

export function EvaluationRadarChart({ data }: EvaluationRadarChartProps) {
  const chartData = data.map((d) => ({
    subject:
      d.category.length > 12 ? d.category.slice(0, 12) + "\u2026" : d.category,
    score: d.score,
    previous: d.previousScore,
    fullMark: 10,
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <RechartsRadar data={chartData} cx="50%" cy="50%" outerRadius="80%">
        <PolarGrid stroke="rgba(255,255,255,0.07)" />
        <PolarAngleAxis
          dataKey="subject"
          tick={{ fill: "#94949F", fontSize: 11, fontFamily: "DM Sans" }}
        />
        <PolarRadiusAxis
          angle={90}
          domain={[0, 10]}
          tick={{ fill: "#52525B", fontSize: 9 }}
        />
        {data.some((d) => d.previousScore != null) && (
          <Radar
            name="Previous"
            dataKey="previous"
            stroke="rgba(139,92,246,0.35)"
            fill="rgba(139,92,246,0.06)"
            strokeWidth={1}
            strokeDasharray="4 2"
          />
        )}
        <Radar
          name="Current"
          dataKey="score"
          stroke="#06b6d4"
          fill="rgba(6,182,212,0.15)"
          strokeWidth={2}
        />
        <Tooltip
          contentStyle={{
            background: "#18181F",
            border: "1px solid rgba(255,255,255,0.08)",
            borderRadius: 8,
            fontSize: 12,
          }}
          formatter={(value: number, name: string) => [
            `${value?.toFixed(1)}/10`,
            name === "score" ? "Current" : "Previous",
          ]}
        />
      </RechartsRadar>
    </ResponsiveContainer>
  );
}
