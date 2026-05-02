import { ReservesPanel } from "@/components/ReservesPanel";
import { TransactionList } from "@/components/TransactionList";
import { api } from "@/lib/api";

export default async function ReservesPage() {
  const [reserves, transactions, categories] = await Promise.all([
    api.getReserves(),
    api.getTransactions({ limit: 10 }),
    api.getCategories(),
  ]);

  return (
    <div className="space-y-8">
      <ReservesPanel reserves={reserves} />
      <section className="space-y-3">
        <h2 className="text-lg font-semibold text-ink">Historico recente</h2>
        <TransactionList transactions={transactions} categories={categories} />
      </section>
    </div>
  );
}
