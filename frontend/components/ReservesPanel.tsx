"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { ReserveCard } from "@/components/ReserveCard";
import type { Reserve } from "@/lib/api";
import { apiPost } from "@/lib/api";

export function ReservesPanel({ reserves }: { reserves: Reserve[] }) {
  const router = useRouter();
  const [reserveId, setReserveId] = useState<string>(reserves[0]?.id ? String(reserves[0].id) : "");
  const [amount, setAmount] = useState("");
  const [status, setStatus] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  async function deposit() {
    if (!reserveId || !amount) {
      return;
    }
    setSaving(true);
    setStatus(null);
    try {
      await apiPost(`/reserves/${reserveId}/deposit`, {
        amount: Number(amount),
      });
      setAmount("");
      router.refresh();
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Erro ao aportar.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <h1 className="text-2xl font-semibold tracking-normal text-ink">Reservas</h1>
        <div className="flex flex-wrap gap-2 rounded-lg border border-line bg-white p-2 shadow-panel">
          <select
            className="min-w-40 rounded-md border border-line px-3 py-2 text-sm"
            value={reserveId}
            onChange={(event) => setReserveId(event.target.value)}
          >
            {reserves.map((reserve) => (
              <option key={reserve.id} value={reserve.id}>
                {reserve.name}
              </option>
            ))}
          </select>
          <input
            className="w-28 rounded-md border border-line px-3 py-2 text-sm"
            inputMode="decimal"
            placeholder="Valor"
            value={amount}
            onChange={(event) => setAmount(event.target.value)}
          />
          <button
            type="button"
            disabled={saving || !reserveId || !amount}
            className="rounded-md bg-ink px-4 py-2 text-sm font-semibold text-white hover:bg-slate-700"
            onClick={deposit}
          >
            Aportar
          </button>
        </div>
      </div>
      {status && <p className="text-sm text-rose-700">{status}</p>}
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {reserves.map((reserve) => (
          <ReserveCard key={reserve.id} reserve={reserve} />
        ))}
      </div>
    </div>
  );
}
