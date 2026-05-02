import { CategoryProgress } from "@/components/CategoryProgress";
import { MonthlyChart } from "@/components/MonthlyChart";
import { PlanSummary } from "@/components/PlanSummary";
import { SummaryCards } from "@/components/SummaryCards";
import { TransactionList } from "@/components/TransactionList";
import { api, getMonthlyChartData } from "@/lib/api";

export default async function DashboardPage() {
  const [dashboard, budgetProgress, planProgress, chartData, categories] =
    await Promise.all([
      api.getDashboard(),
      api.getBudgetProgress(),
      api.getPlanProgress(),
      getMonthlyChartData(),
      api.getCategories(),
    ]);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-normal text-ink">Dashboard</h1>
          <p className="mt-1 text-sm text-muted">
            {String(dashboard.month).padStart(2, "0")}/{dashboard.year}
          </p>
        </div>
        <div className="rounded-lg border border-line bg-white px-4 py-3 text-right shadow-panel">
          <p className="text-xs font-medium text-muted">Saldo total</p>
          <p className="text-lg font-semibold text-ink">
            {new Intl.NumberFormat("pt-BR", {
              style: "currency",
              currency: "BRL",
            }).format(Number(dashboard.total_account_balance))}
          </p>
        </div>
      </div>

      <SummaryCards summary={dashboard} />

      <div className="grid gap-6 lg:grid-cols-[minmax(0,1.25fr)_minmax(320px,0.75fr)]">
        <MonthlyChart data={chartData} />
        <PlanSummary progress={planProgress} />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <section className="space-y-3">
          <h2 className="text-lg font-semibold text-ink">Orcamentos</h2>
          <CategoryProgress items={budgetProgress} />
        </section>
        <section className="space-y-3">
          <h2 className="text-lg font-semibold text-ink">Recentes</h2>
          <TransactionList
            transactions={dashboard.recent_transactions}
            categories={categories}
            compact
          />
        </section>
      </div>
    </div>
  );
}
