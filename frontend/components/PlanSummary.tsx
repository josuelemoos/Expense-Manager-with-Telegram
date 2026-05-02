import type { PlanProgress } from "@/lib/api";
import { formatCurrency, formatPercent } from "@/lib/api";

export function PlanSummary({ progress }: { progress: PlanProgress }) {
  const { plan } = progress;

  return (
    <section className="rounded-lg border border-line bg-white p-4 shadow-panel">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="text-base font-semibold text-ink">Planejamento mensal</h2>
          <p className="mt-1 text-sm text-muted">
            {String(plan.month).padStart(2, "0")}/{plan.year}
          </p>
        </div>
        <div className="text-right">
          <p className="text-sm text-muted">Livre</p>
          <p className="text-xl font-semibold text-ink">{formatCurrency(plan.free_amount)}</p>
        </div>
      </div>
      <div className="mt-4 grid gap-3 sm:grid-cols-3">
        <div className="rounded-md bg-slate-50 p-3">
          <p className="text-xs font-medium text-muted">Renda</p>
          <p className="mt-1 font-semibold text-ink">{formatCurrency(plan.expected_income)}</p>
        </div>
        <div className="rounded-md bg-slate-50 p-3">
          <p className="text-xs font-medium text-muted">Comprometido</p>
          <p className="mt-1 font-semibold text-ink">
            {formatCurrency(plan.committed_expenses)}
          </p>
        </div>
        <div className="rounded-md bg-slate-50 p-3">
          <p className="text-xs font-medium text-muted">Nao alocado</p>
          <p className="mt-1 font-semibold text-ink">
            {formatCurrency(progress.unallocated_amount)}
          </p>
        </div>
      </div>
      {progress.allocations.length > 0 && (
        <div className="mt-4 space-y-2">
          {progress.allocations.map((item) => (
            <div key={item.rule_id} className="flex items-center justify-between gap-3 text-sm">
              <span className="font-medium text-slate-700">{item.name}</span>
              <span className="text-slate-600">
                {formatCurrency(item.planned_amount)} ({formatPercent(item.percentage)})
              </span>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
