"use client";

import { type FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { AllocationChart } from "@/components/AllocationChart";
import type { AllocationRule, Category, PlanProgress } from "@/lib/api";
import { apiPost, formatCurrency, formatPercent } from "@/lib/api";

export function PlanningPanel({
  progress,
  allocations,
  categories,
}: {
  progress: PlanProgress;
  allocations: AllocationRule[];
  categories: Category[];
}) {
  const router = useRouter();
  const [income, setIncome] = useState(String(progress.plan.expected_income));
  const [committed, setCommitted] = useState(String(progress.plan.committed_expenses));
  const [status, setStatus] = useState<string | null>(null);
  const expenseCategories = categories.filter((category) => category.type === "expense");

  async function savePlan() {
    setStatus(null);
    try {
      await apiPost("/plan", {
        month: progress.plan.month,
        year: progress.plan.year,
        expected_income: Number(income || 0),
        committed_expenses: Number(committed || 0),
        notes: progress.plan.notes,
      });
      router.refresh();
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Erro ao salvar plano.");
    }
  }

  async function saveRule(rule: AllocationRule, formData: FormData) {
    setStatus(null);
    try {
      await apiPost("/plan/allocations", {
        id: rule.id,
        name: String(formData.get("name") ?? rule.name),
        percentage: Number(formData.get("percentage") ?? rule.percentage),
        category_id: formData.get("category_id")
          ? Number(formData.get("category_id"))
          : null,
        emoji: String(formData.get("emoji") ?? ""),
        sort_order: Number(formData.get("sort_order") ?? rule.sort_order),
        is_active: true,
      });
      router.refresh();
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Erro ao salvar alocacao.");
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold tracking-normal text-ink">Planejamento</h1>
      {status && <p className="text-sm text-rose-700">{status}</p>}

      <section className="grid gap-6 lg:grid-cols-[minmax(0,0.9fr)_minmax(360px,1.1fr)]">
        <div className="rounded-lg border border-line bg-white p-4 shadow-panel">
          <h2 className="text-lg font-semibold text-ink">Plano mensal</h2>
          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            <label className="space-y-1 text-sm">
              <span className="font-medium text-slate-700">Renda esperada</span>
              <input
                className="w-full rounded-md border border-line px-3 py-2"
                inputMode="decimal"
                value={income}
                onChange={(event) => setIncome(event.target.value)}
              />
            </label>
            <label className="space-y-1 text-sm">
              <span className="font-medium text-slate-700">Comprometido</span>
              <input
                className="w-full rounded-md border border-line px-3 py-2"
                inputMode="decimal"
                value={committed}
                onChange={(event) => setCommitted(event.target.value)}
              />
            </label>
          </div>
          <div className="mt-4 grid gap-3 sm:grid-cols-3">
            <div className="rounded-md bg-slate-50 p-3">
              <p className="text-xs font-medium text-muted">Livre</p>
              <p className="mt-1 font-semibold text-ink">
                {formatCurrency(progress.plan.free_amount)}
              </p>
            </div>
            <div className="rounded-md bg-slate-50 p-3">
              <p className="text-xs font-medium text-muted">Nao alocado</p>
              <p className="mt-1 font-semibold text-ink">
                {formatCurrency(progress.unallocated_amount)}
              </p>
            </div>
            <div className="rounded-md bg-slate-50 p-3">
              <p className="text-xs font-medium text-muted">Mes</p>
              <p className="mt-1 font-semibold text-ink">
                {String(progress.plan.month).padStart(2, "0")}/{progress.plan.year}
              </p>
            </div>
          </div>
          <button
            type="button"
            className="mt-4 rounded-md bg-ink px-4 py-2 text-sm font-semibold text-white hover:bg-slate-700"
            onClick={savePlan}
          >
            Salvar plano
          </button>
        </div>
        <AllocationChart allocations={progress.allocations} />
      </section>

      <section className="space-y-3">
        <h2 className="text-lg font-semibold text-ink">Alocacoes</h2>
        <div className="grid gap-4 lg:grid-cols-2">
          {allocations.map((rule) => {
            const item = progress.allocations.find((entry) => entry.rule_id === rule.id);
            return (
              <form
                key={rule.id}
                onSubmit={(event: FormEvent<HTMLFormElement>) => {
                  event.preventDefault();
                  void saveRule(rule, new FormData(event.currentTarget));
                }}
                className="rounded-lg border border-line bg-white p-4 shadow-panel"
              >
                <div className="grid gap-3 sm:grid-cols-[80px_minmax(0,1fr)_100px]">
                  <label className="space-y-1 text-sm">
                    <span className="font-medium text-slate-700">Emoji</span>
                    <input
                      name="emoji"
                      defaultValue={rule.emoji ?? ""}
                      className="w-full rounded-md border border-line px-3 py-2"
                    />
                  </label>
                  <label className="space-y-1 text-sm">
                    <span className="font-medium text-slate-700">Nome</span>
                    <input
                      name="name"
                      defaultValue={rule.name}
                      className="w-full rounded-md border border-line px-3 py-2"
                    />
                  </label>
                  <label className="space-y-1 text-sm">
                    <span className="font-medium text-slate-700">%</span>
                    <input
                      name="percentage"
                      inputMode="decimal"
                      defaultValue={String(rule.percentage)}
                      className="w-full rounded-md border border-line px-3 py-2"
                    />
                  </label>
                </div>
                <div className="mt-3 grid gap-3 sm:grid-cols-[minmax(0,1fr)_110px]">
                  <label className="space-y-1 text-sm">
                    <span className="font-medium text-slate-700">Categoria</span>
                    <select
                      name="category_id"
                      defaultValue={rule.category_id ?? ""}
                      className="w-full rounded-md border border-line px-3 py-2"
                    >
                      <option value="">Sem categoria</option>
                      {expenseCategories.map((category) => (
                        <option key={category.id} value={category.id}>
                          {category.name}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label className="space-y-1 text-sm">
                    <span className="font-medium text-slate-700">Ordem</span>
                    <input
                      name="sort_order"
                      inputMode="numeric"
                      defaultValue={String(rule.sort_order)}
                      className="w-full rounded-md border border-line px-3 py-2"
                    />
                  </label>
                </div>
                {item && (
                  <div className="mt-4 grid gap-3 text-sm sm:grid-cols-3">
                    <span>Planejado: {formatCurrency(item.planned_amount)}</span>
                    <span>Usado: {formatCurrency(item.spent_amount)}</span>
                    <span>{formatPercent(item.used_percentage)}</span>
                  </div>
                )}
                <button
                  type="submit"
                  className="mt-4 rounded-md bg-ink px-4 py-2 text-sm font-semibold text-white hover:bg-slate-700"
                >
                  Salvar
                </button>
              </form>
            );
          })}
        </div>
      </section>
    </div>
  );
}
