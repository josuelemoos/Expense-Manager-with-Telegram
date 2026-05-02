"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { CategoryProgress } from "@/components/CategoryProgress";
import type { BudgetProgress, Category } from "@/lib/api";
import { apiPost, formatCurrency } from "@/lib/api";

export function CategoriesPanel({
  categories,
  progress,
}: {
  categories: Category[];
  progress: BudgetProgress[];
}) {
  const router = useRouter();
  const expenseCategories = categories.filter((category) => category.type === "expense");
  const [month] = useState(new Date().getMonth() + 1);
  const [year] = useState(new Date().getFullYear());
  const [limits, setLimits] = useState<Record<number, string>>(
    Object.fromEntries(
      expenseCategories.map((category) => [
        category.id,
        category.monthly_limit ? String(category.monthly_limit) : "",
      ]),
    ),
  );
  const [status, setStatus] = useState<string | null>(null);

  async function save(categoryId: number) {
    setStatus(null);
    try {
      await apiPost("/budgets", {
        category_id: categoryId,
        month,
        year,
        limit_value: Number(limits[categoryId] || 0),
      });
      router.refresh();
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Erro ao salvar limite.");
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold tracking-normal text-ink">Categorias</h1>
      {status && <p className="text-sm text-rose-700">{status}</p>}
      <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(320px,0.8fr)]">
        <div className="overflow-hidden rounded-lg border border-line bg-white shadow-panel">
          <table className="min-w-full divide-y divide-line text-sm">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-4 py-3 text-left font-semibold text-slate-600">Nome</th>
                <th className="px-4 py-3 text-left font-semibold text-slate-600">Tipo</th>
                <th className="px-4 py-3 text-left font-semibold text-slate-600">Limite</th>
                <th className="px-4 py-3 text-right font-semibold text-slate-600">Acao</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line">
              {categories.map((category) => (
                <tr key={category.id}>
                  <td className="px-4 py-3 font-medium text-ink">{category.name}</td>
                  <td className="px-4 py-3 text-slate-600">
                    {category.type === "income" ? "Receita" : "Despesa"}
                  </td>
                  <td className="px-4 py-3">
                    {category.type === "expense" ? (
                      <input
                        className="w-28 rounded-md border border-line px-3 py-2"
                        inputMode="decimal"
                        value={limits[category.id] ?? ""}
                        onChange={(event) =>
                          setLimits({ ...limits, [category.id]: event.target.value })
                        }
                      />
                    ) : (
                      <span className="text-muted">
                        {category.monthly_limit
                          ? formatCurrency(category.monthly_limit)
                          : "-"}
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-right">
                    {category.type === "expense" && (
                      <button
                        type="button"
                        className="rounded-md bg-ink px-3 py-2 text-sm font-semibold text-white hover:bg-slate-700"
                        onClick={() => save(category.id)}
                      >
                        Salvar
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <section className="space-y-3">
          <h2 className="text-lg font-semibold text-ink">Progresso</h2>
          <CategoryProgress items={progress} />
        </section>
      </div>
    </div>
  );
}
