"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { MonthlyChartPoint } from "@/lib/api";
import { formatCurrency } from "@/lib/api";

export function MonthlyChart({ data }: { data: MonthlyChartPoint[] }) {
  return (
    <div className="h-80 rounded-lg border border-line bg-white p-4 shadow-panel">
      <div className="mb-4 flex items-center justify-between gap-3">
        <h2 className="text-base font-semibold text-ink">Receitas vs despesas</h2>
        <span className="text-xs font-medium text-muted">6 meses</span>
      </div>
      <ResponsiveContainer width="100%" height="85%">
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="label" tick={{ fill: "#6b7280", fontSize: 12 }} />
          <YAxis tick={{ fill: "#6b7280", fontSize: 12 }} />
          <Tooltip formatter={(value) => formatCurrency(Number(value))} />
          <Legend />
          <Bar dataKey="income" name="Receitas" fill="#10b981" radius={[4, 4, 0, 0]} />
          <Bar dataKey="expense" name="Despesas" fill="#ef4444" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
