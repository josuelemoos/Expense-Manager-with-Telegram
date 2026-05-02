import { TransactionsPanel } from "@/components/TransactionsPanel";
import { api } from "@/lib/api";

export default async function TransactionsPage() {
  const [transactions, categories, accounts] = await Promise.all([
    api.getTransactions({ limit: 200 }),
    api.getCategories(),
    api.getAccounts(),
  ]);

  return (
    <TransactionsPanel
      transactions={transactions}
      categories={categories}
      accounts={accounts}
    />
  );
}
