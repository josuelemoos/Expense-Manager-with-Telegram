import type { Category, Transaction } from "@/lib/api";
import { formatCurrency } from "@/lib/api";

function categoryName(categories: Category[], id: number | null) {
  return categories.find((category) => category.id === id)?.name ?? "Sem categoria";
}

export function TransactionList({
  transactions,
  categories = [],
  compact = false,
}: {
  transactions: Transaction[];
  categories?: Category[];
  compact?: boolean;
}) {
  if (!transactions.length) {
    return (
      <div className="rounded-lg border border-dashed border-line bg-white p-6 text-sm text-muted">
        Nenhuma transacao encontrada.
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-lg border border-line bg-white shadow-panel">
      <table className="min-w-full divide-y divide-line text-sm">
        <thead className="bg-slate-50">
          <tr>
            <th className="px-4 py-3 text-left font-semibold text-slate-600">Data</th>
            <th className="px-4 py-3 text-left font-semibold text-slate-600">Descricao</th>
            {!compact && (
              <th className="px-4 py-3 text-left font-semibold text-slate-600">
                Categoria
              </th>
            )}
            <th className="px-4 py-3 text-right font-semibold text-slate-600">Valor</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-line">
          {transactions.map((transaction) => {
            const income = transaction.type === "income";
            return (
              <tr key={transaction.id} className="bg-white">
                <td className="whitespace-nowrap px-4 py-3 text-slate-600">
                  {new Date(`${transaction.date}T00:00:00`).toLocaleDateString("pt-BR")}
                </td>
                <td className="px-4 py-3 font-medium text-ink">
                  {transaction.description}
                </td>
                {!compact && (
                  <td className="px-4 py-3 text-slate-600">
                    {categoryName(categories, transaction.category_id)}
                  </td>
                )}
                <td
                  className={`whitespace-nowrap px-4 py-3 text-right font-semibold ${
                    income ? "text-emerald-700" : "text-rose-700"
                  }`}
                >
                  {income ? "+" : "-"}
                  {formatCurrency(transaction.amount)}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
