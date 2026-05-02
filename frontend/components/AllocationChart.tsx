"use client";

import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

import type { AllocationProgress } from "@/lib/api";
import { formatCurrency, money } from "@/lib/api";

const COLORS = ["#6366f1", "#10b981", "#f59e0b", "#ef4444", "#3b82f6", "#8b5cf6"];

export function AllocationChart({ allocations }: { allocations: AllocationProgress[] }) {
  const data = allocations.map((item) => ({
    name: item.name,
    value: money(item.planned_amount),
  }));

  if (!data.length) {
    return (
      <div className="flex h-72 items-center justify-center rounded-lg border border-dashed border-line bg-white text-sm text-muted">
        Nenhuma alocacao ativa.
      </div>
    );
  }

  return (
    <div className="h-72 rounded-lg border border-line bg-white p-4 shadow-panel">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie data={data} dataKey="value" nameKey="name" innerRadius={58} outerRadius={92}>
            {data.map((entry, index) => (
              <Cell key={entry.name} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip formatter={(value) => formatCurrency(Number(value))} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
