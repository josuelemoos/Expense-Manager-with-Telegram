import type { BudgetProgress } from "@/lib/api";
import { formatCurrency, formatPercent, money } from "@/lib/api";

export function CategoryProgress({ items }: { items: BudgetProgress[] }) {
  if (!items.length) {
    return (
      <div className="rounded-lg border border-dashed border-line bg-white p-6 text-sm text-muted">
        Nenhum limite mensal definido.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {items.map((item) => {
        const pct = Math.min(money(item.percentage_used), 100);
        const barColor =
          item.alert_level === "exceeded"
            ? "bg-rose-600"
            : item.alert_level === "warning"
              ? "bg-amber-500"
              : "bg-indigo-500";
        return (
          <article
            key={item.category_id}
            className="rounded-lg border border-line bg-white p-4 shadow-panel"
          >
            <div className="flex flex-wrap items-center justify-between gap-2">
              <p className="font-medium text-ink">{item.category_name}</p>
              <p className="text-sm text-slate-600">
                {formatCurrency(item.spent_value)} / {formatCurrency(item.limit_value)}
              </p>
            </div>
            <div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-100">
              <div className={`h-full rounded-full ${barColor}`} style={{ width: `${pct}%` }} />
            </div>
            <div className="mt-2 flex flex-wrap items-center justify-between gap-2 text-sm">
              <span className="font-medium text-slate-700">
                {formatPercent(item.percentage_used)}
              </span>
              {item.alert_message && (
                <span className="text-amber-700">{item.alert_message}</span>
              )}
            </div>
          </article>
        );
      })}
    </div>
  );
}
