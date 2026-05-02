import type { DashboardSummary } from "@/lib/api";
import { formatCurrency } from "@/lib/api";

type Item = {
  label: string;
  value: string;
  accent: string;
};

export function SummaryCards({ summary }: { summary: DashboardSummary }) {
  const items: Item[] = [
    {
      label: "Receitas",
      value: formatCurrency(summary.total_income),
      accent: "border-emerald-500",
    },
    {
      label: "Despesas",
      value: formatCurrency(summary.total_expense),
      accent: "border-rose-500",
    },
    {
      label: "Saldo do mes",
      value: formatCurrency(summary.monthly_balance),
      accent: "border-indigo-500",
    },
    {
      label: "Total reservado",
      value: formatCurrency(summary.total_reserved),
      accent: "border-amber-500",
    },
  ];

  return (
    <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      {items.map((item) => (
        <article
          key={item.label}
          className={`rounded-lg border border-line border-l-4 ${item.accent} bg-panel p-4 shadow-panel`}
        >
          <p className="text-sm font-medium text-muted">{item.label}</p>
          <p className="mt-2 text-2xl font-semibold tracking-normal text-ink">
            {item.value}
          </p>
        </article>
      ))}
    </section>
  );
}
