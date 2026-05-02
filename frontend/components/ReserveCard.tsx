import type { Reserve } from "@/lib/api";
import { formatCurrency, money } from "@/lib/api";

export function ReserveCard({ reserve }: { reserve: Reserve }) {
  const progress = reserve.goal_value
    ? Math.min((money(reserve.current_value) / money(reserve.goal_value)) * 100, 100)
    : 0;

  return (
    <article className="rounded-lg border border-line bg-white p-4 shadow-panel">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="font-semibold text-ink">{reserve.name}</h3>
          {reserve.description && (
            <p className="mt-1 text-sm text-muted">{reserve.description}</p>
          )}
        </div>
        <span className="rounded-md bg-slate-100 px-2 py-1 text-xs font-medium text-slate-700">
          {reserve.goal_value ? `${progress.toFixed(0)}%` : "Livre"}
        </span>
      </div>
      <p className="mt-4 text-xl font-semibold text-ink">
        {formatCurrency(reserve.current_value)}
      </p>
      {reserve.goal_value && (
        <>
          <div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-100">
            <div
              className="h-full rounded-full bg-emerald-500"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="mt-2 text-sm text-muted">
            Meta: {formatCurrency(reserve.goal_value)}
          </p>
        </>
      )}
    </article>
  );
}
