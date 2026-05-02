export const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export type Money = string;

export type Account = {
  id: number;
  name: string;
  type: "wallet" | "bank" | "savings" | "credit";
  initial_balance: Money;
  current_balance: Money;
  is_active: boolean;
  is_default: boolean;
};

export type AccountBalanceSummary = {
  total: Money;
  accounts: Account[];
};

export type Category = {
  id: number;
  name: string;
  type: "expense" | "income";
  monthly_limit: Money | null;
  color: string | null;
  icon: string | null;
  is_active: boolean;
};

export type Transaction = {
  id: number;
  user_id: number;
  account_id: number | null;
  category_id: number | null;
  type: "income" | "expense" | "transfer";
  amount: Money;
  description: string;
  date: string;
  notes: string | null;
  source: "manual" | "telegram" | "import";
  created_at: string;
};

export type Reserve = {
  id: number;
  user_id: number;
  name: string;
  current_value: Money;
  goal_value: Money | null;
  description: string | null;
  created_at: string;
  is_active: boolean;
};

export type BudgetProgress = {
  category_id: number;
  category_name: string;
  month: number;
  year: number;
  limit_value: Money;
  spent_value: Money;
  percentage_used: Money;
  alert_level: string | null;
  alert_message: string | null;
};

export type CategorySpending = {
  category_id: number | null;
  category_name: string;
  total: Money;
  percentage: Money;
};

export type MonthlySummary = {
  month: number;
  year: number;
  total_income: Money;
  total_expense: Money;
  balance: Money;
  expenses_by_category: CategorySpending[];
  top_expenses: CategorySpending[];
};

export type DashboardSummary = {
  month: number;
  year: number;
  total_income: Money;
  total_expense: Money;
  monthly_balance: Money;
  total_reserved: Money;
  total_account_balance: Money;
  accounts: Account[];
  recent_transactions: Transaction[];
};

export type MonthlyPlan = {
  id: number | null;
  user_id: number;
  month: number;
  year: number;
  expected_income: Money;
  committed_expenses: Money;
  free_amount: Money;
  notes: string | null;
  warning: string | null;
};

export type AllocationRule = {
  id: number;
  user_id: number;
  name: string;
  percentage: Money;
  category_id: number | null;
  emoji: string | null;
  sort_order: number;
  is_active: boolean;
};

export type AllocationProgress = {
  rule_id: number;
  name: string;
  percentage: Money;
  planned_amount: Money;
  spent_amount: Money;
  used_percentage: Money;
  category_id: number | null;
  emoji: string | null;
  is_over: boolean;
  alert_message: string | null;
};

export type PlanProgress = {
  plan: MonthlyPlan;
  allocations: AllocationProgress[];
  unallocated_percentage: Money;
  unallocated_amount: Money;
};

export type MonthlyChartPoint = {
  label: string;
  income: number;
  expense: number;
};

export function money(value: Money | number | null | undefined): number {
  return Number(value ?? 0);
}

export function formatCurrency(value: Money | number | null | undefined): string {
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  }).format(money(value));
}

export function formatPercent(value: Money | number | null | undefined): string {
  return `${money(value).toFixed(0)}%`;
}

function pathWithQuery(path: string, params?: Record<string, string | number | undefined | null>) {
  if (!params) {
    return path;
  }
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      search.set(key, String(value));
    }
  });
  const query = search.toString();
  return query ? `${path}?${query}` : path;
}

async function apiGet<T>(
  path: string,
  fallback: T,
  params?: Record<string, string | number | undefined | null>,
): Promise<T> {
  try {
    const response = await fetch(`${API_URL}${pathWithQuery(path, params)}`, {
      cache: "no-store",
      signal: AbortSignal.timeout(1200),
    });
    if (!response.ok) {
      return fallback;
    }
    return (await response.json()) as T;
  } catch {
    return fallback;
  }
}

export async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    let message = "Nao foi possivel salvar.";
    try {
      const payload = (await response.json()) as { detail?: string };
      message = payload.detail ?? message;
    } catch {
      // Keep the generic message.
    }
    throw new Error(message);
  }
  return (await response.json()) as T;
}

const emptyDashboard: DashboardSummary = {
  month: new Date().getMonth() + 1,
  year: new Date().getFullYear(),
  total_income: "0.00",
  total_expense: "0.00",
  monthly_balance: "0.00",
  total_reserved: "0.00",
  total_account_balance: "0.00",
  accounts: [],
  recent_transactions: [],
};

const emptyPlan: PlanProgress = {
  plan: {
    id: null,
    user_id: 1,
    month: new Date().getMonth() + 1,
    year: new Date().getFullYear(),
    expected_income: "0.00",
    committed_expenses: "0.00",
    free_amount: "0.00",
    notes: null,
    warning: "Nao existe plano para este mes.",
  },
  allocations: [],
  unallocated_percentage: "0.00",
  unallocated_amount: "0.00",
};

const emptyPlanPath = "/plan";

export const api = {
  getDashboard: () => apiGet<DashboardSummary>("/summary/dashboard", emptyDashboard),
  getMonthlySummary: (month?: number, year?: number) =>
    apiGet<MonthlySummary>(
      "/summary/monthly",
      {
        month: month ?? new Date().getMonth() + 1,
        year: year ?? new Date().getFullYear(),
        total_income: "0.00",
        total_expense: "0.00",
        balance: "0.00",
        expenses_by_category: [],
        top_expenses: [],
      },
      { month, year },
    ),
  getAccounts: () => apiGet<Account[]>("/accounts", []),
  getCategories: (type?: "income" | "expense") =>
    apiGet<Category[]>("/categories", [], { type }),
  getTransactions: (params?: {
    month?: number;
    year?: number;
    type?: string;
    category_id?: number;
    limit?: number;
  }) => apiGet<Transaction[]>("/transactions", [], params),
  getReserves: () => apiGet<Reserve[]>("/reserves", []),
  getBudgetProgress: (month?: number, year?: number) =>
    apiGet<BudgetProgress[]>("/budgets/progress", [], { month, year }),
  getPlanProgress: (month?: number, year?: number) =>
    apiGet<PlanProgress>("/plan/progress", emptyPlan, { month, year }),
  getPlan: (month?: number, year?: number) =>
    apiGet<MonthlyPlan>(emptyPlanPath, emptyPlan.plan, { month, year }),
  getAllocations: () => apiGet<AllocationRule[]>("/plan/allocations", []),
};

export async function getMonthlyChartData(months = 6): Promise<MonthlyChartPoint[]> {
  const now = new Date();
  const requests = Array.from({ length: months }, (_, index) => {
    const date = new Date(now.getFullYear(), now.getMonth() - (months - 1 - index), 1);
    return {
      month: date.getMonth() + 1,
      year: date.getFullYear(),
      label: `${String(date.getMonth() + 1).padStart(2, "0")}/${String(date.getFullYear()).slice(-2)}`,
    };
  });

  const summaries = await Promise.all(
    requests.map((item) => api.getMonthlySummary(item.month, item.year)),
  );

  return summaries.map((summary, index) => ({
    label: requests[index].label,
    income: money(summary.total_income),
    expense: money(summary.total_expense),
  }));
}
