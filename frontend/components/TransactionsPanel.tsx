"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";

import { TransactionList } from "@/components/TransactionList";
import type { Account, Category, Transaction } from "@/lib/api";
import { apiPost } from "@/lib/api";

type FormState = {
  type: "expense" | "income";
  amount: string;
  description: string;
  category_id: string;
  account_id: string;
  date: string;
};

const initialForm: FormState = {
  type: "expense",
  amount: "",
  description: "",
  category_id: "",
  account_id: "",
  date: new Date().toISOString().slice(0, 10),
};

export function TransactionsPanel({
  transactions,
  categories,
  accounts,
}: {
  transactions: Transaction[];
  categories: Category[];
  accounts: Account[];
}) {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState<FormState>(initialForm);
  const [status, setStatus] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const filteredCategories = useMemo(
    () => categories.filter((category) => category.type === form.type),
    [categories, form.type],
  );

  async function submit() {
    setSaving(true);
    setStatus(null);
    try {
      await apiPost("/transactions", {
        type: form.type,
        amount: Number(form.amount),
        description: form.description,
        category_id: form.category_id ? Number(form.category_id) : null,
        account_id: form.account_id ? Number(form.account_id) : null,
        date: form.date || null,
        source: "manual",
      });
      setForm(initialForm);
      setOpen(false);
      router.refresh();
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Erro ao salvar.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-semibold tracking-normal text-ink">Extrato</h1>
        <button
          type="button"
          className="rounded-md bg-ink px-4 py-2 text-sm font-semibold text-white hover:bg-slate-700"
          onClick={() => setOpen(true)}
        >
          Adicionar
        </button>
      </div>

      <TransactionList transactions={transactions} categories={categories} />

      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/40 px-4">
          <div className="w-full max-w-xl rounded-lg bg-white p-5 shadow-xl">
            <div className="flex items-center justify-between gap-3">
              <h2 className="text-lg font-semibold text-ink">Nova transacao</h2>
              <button
                type="button"
                className="rounded-md px-2 py-1 text-sm text-slate-600 hover:bg-slate-100"
                onClick={() => setOpen(false)}
              >
                Fechar
              </button>
            </div>
            <div className="mt-5 grid gap-4 sm:grid-cols-2">
              <label className="space-y-1 text-sm">
                <span className="font-medium text-slate-700">Tipo</span>
                <select
                  className="w-full rounded-md border border-line px-3 py-2"
                  value={form.type}
                  onChange={(event) =>
                    setForm({ ...form, type: event.target.value as FormState["type"], category_id: "" })
                  }
                >
                  <option value="expense">Despesa</option>
                  <option value="income">Receita</option>
                </select>
              </label>
              <label className="space-y-1 text-sm">
                <span className="font-medium text-slate-700">Valor</span>
                <input
                  className="w-full rounded-md border border-line px-3 py-2"
                  inputMode="decimal"
                  value={form.amount}
                  onChange={(event) => setForm({ ...form, amount: event.target.value })}
                />
              </label>
              <label className="space-y-1 text-sm sm:col-span-2">
                <span className="font-medium text-slate-700">Descricao</span>
                <input
                  className="w-full rounded-md border border-line px-3 py-2"
                  value={form.description}
                  onChange={(event) => setForm({ ...form, description: event.target.value })}
                />
              </label>
              <label className="space-y-1 text-sm">
                <span className="font-medium text-slate-700">Categoria</span>
                <select
                  className="w-full rounded-md border border-line px-3 py-2"
                  value={form.category_id}
                  onChange={(event) => setForm({ ...form, category_id: event.target.value })}
                >
                  <option value="">Sem categoria</option>
                  {filteredCategories.map((category) => (
                    <option key={category.id} value={category.id}>
                      {category.name}
                    </option>
                  ))}
                </select>
              </label>
              <label className="space-y-1 text-sm">
                <span className="font-medium text-slate-700">Conta</span>
                <select
                  className="w-full rounded-md border border-line px-3 py-2"
                  value={form.account_id}
                  onChange={(event) => setForm({ ...form, account_id: event.target.value })}
                >
                  <option value="">Conta padrao</option>
                  {accounts.map((account) => (
                    <option key={account.id} value={account.id}>
                      {account.name}
                    </option>
                  ))}
                </select>
              </label>
              <label className="space-y-1 text-sm">
                <span className="font-medium text-slate-700">Data</span>
                <input
                  type="date"
                  className="w-full rounded-md border border-line px-3 py-2"
                  value={form.date}
                  onChange={(event) => setForm({ ...form, date: event.target.value })}
                />
              </label>
            </div>
            {status && <p className="mt-4 text-sm text-rose-700">{status}</p>}
            <div className="mt-5 flex justify-end gap-2">
              <button
                type="button"
                className="rounded-md border border-line px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
                onClick={() => setOpen(false)}
              >
                Cancelar
              </button>
              <button
                type="button"
                disabled={saving || !form.amount || !form.description}
                className="rounded-md bg-ink px-4 py-2 text-sm font-semibold text-white hover:bg-slate-700"
                onClick={submit}
              >
                Salvar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
