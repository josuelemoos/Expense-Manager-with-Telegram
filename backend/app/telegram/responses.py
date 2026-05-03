from datetime import timedelta
from decimal import Decimal

from app.models import Reserve
from app.models import Category, Transaction
from app.schemas.account import AccountBalanceSummary
from app.schemas.effect import ExpenseEffectSimulation
from app.schemas.plan import MonthlyPlanRead, PlanProgress
from app.schemas.reserve import ReserveDepositRead
from app.schemas.reset import PendingReset, ResetResult
from app.schemas.summary import MonthlySummary
from app.schemas.transaction import TransactionResult
from app.telegram.parser import ParseError
from app.utils.formatters import format_brl


def progress_bar(percentage: Decimal | int | float, width: int = 10) -> str:
    pct = Decimal(str(percentage))
    filled = int(min(max(pct, 0), 100) / Decimal("100") * width)
    return "[" + ("\u2588" * filled) + ("\u2591" * (width - filled)) + f"] {pct:.0f}%"


def format_parse_error(error: ParseError) -> str:
    lines = [error.message]
    if error.suggestion:
        lines.extend(["", f"Sugestao: {error.suggestion}"])
    lines.extend(["", "Voce tambem pode enviar /ajuda para ver exemplos."])
    return "\n".join(lines)


def format_service_error(detail: str) -> str:
    return "\n".join(
        [
            "Nao consegui concluir essa acao.",
            "",
            detail,
            "",
            "Revise os dados e tente novamente. Para exemplos, envie /ajuda.",
        ],
    )


def format_transaction_result(result: TransactionResult) -> str:
    transaction = result.transaction
    if transaction.type == "income":
        header = "\u2705 Receita registrada"
        icon = "\U0001f4b0"
    else:
        header = "\u2705 Despesa registrada"
        icon = "\U0001f4b8"

    lines = [
        header,
        "",
        f"{icon} {format_brl(transaction.amount)}",
        f"\U0001f4dd {transaction.description}",
        f"\U0001f4c5 {transaction.date.strftime('%d/%m/%Y')}",
        "",
        f"\U0001f4b0 Saldo atual: {format_brl(result.account_balance)}",
    ]

    if result.budget_progress:
        budget = result.budget_progress
        lines.extend(
            [
                "",
                f"\U0001f4ca {budget.category_name} este mes: "
                f"{format_brl(budget.spent_value)} / {format_brl(budget.limit_value)} "
                f"({budget.percentage_used:.0f}%)",
                progress_bar(budget.percentage_used),
            ],
        )
        if budget.alert_message:
            lines.extend(["", f"\u26a0\ufe0f {budget.alert_message}"])

    return "\n".join(lines)


def format_balance(summary: AccountBalanceSummary) -> str:
    lines = ["\U0001f4b0 Saldo atual", ""]
    for account in summary.accounts:
        lines.append(f"\U0001f3e6 {account.name}: {format_brl(account.current_balance)}")
    lines.extend(["\u2500" * 17, f"Total: {format_brl(summary.total)}"])
    return "\n".join(lines)


def format_monthly_summary(summary: MonthlySummary) -> str:
    lines = [
        f"\U0001f4ca Resumo - {summary.month:02d}/{summary.year}",
        "",
        f"\U0001f4b0 Receitas: {format_brl(summary.total_income)}",
        f"\U0001f4b8 Despesas: {format_brl(summary.total_expense)}",
        f"\U0001f4c8 Saldo do mes: {format_brl(summary.balance)}",
    ]
    if summary.top_expenses:
        lines.extend(["", "Top gastos:"])
        for index, category in enumerate(summary.top_expenses, start=1):
            lines.append(
                f"{index}. {category.category_name} "
                f"{format_brl(category.total)} ({category.percentage:.0f}%)",
            )
    return "\n".join(lines)


def format_reserves(reserves: list[Reserve]) -> str:
    if not reserves:
        return "Voce ainda nao tem reservas ativas cadastradas."
    lines = ["\U0001f3e6 Suas reservas", ""]
    total = Decimal("0.00")
    for reserve in reserves:
        total += reserve.current_value
        lines.append(f"\U0001f6e1\ufe0f {reserve.name}")
        if reserve.goal_value:
            pct = (reserve.current_value / reserve.goal_value * Decimal("100")).quantize(Decimal("0.01"))
            lines.append(f"   {format_brl(reserve.current_value)} / {format_brl(reserve.goal_value)}")
            lines.append(f"   {progress_bar(pct)}")
        else:
            lines.append(f"   {format_brl(reserve.current_value)}")
        lines.append("")
    lines.append(f"Total reservado: {format_brl(total)}")
    return "\n".join(lines)


def format_categories(categories: list[Category]) -> str:
    if not categories:
        return "Nenhuma categoria ativa encontrada."
    lines = ["Categorias ativas", ""]
    for category in categories:
        lines.append(f"- {category.name} ({category.type})")
    return "\n".join(lines)


def format_transactions(transactions: list[Transaction]) -> str:
    if not transactions:
        return "Nenhuma transacao encontrada."
    lines = ["Ultimas transacoes", ""]
    for transaction in transactions:
        sign = "+" if transaction.type == "income" else "-"
        lines.append(
            f"{transaction.date.strftime('%d/%m')} {sign}{format_brl(transaction.amount)} "
            f"{transaction.description}",
        )
    return "\n".join(lines)


def format_reserve_deposit(result: ReserveDepositRead) -> str:
    reserve = result.reserve
    lines = [
        "\u2705 Aporte registrado",
        "",
        f"\U0001f6e1\ufe0f {reserve.name}: {format_brl(reserve.current_value)}",
        f"\U0001f4b0 Saldo atual: {format_brl(result.account_balance)}",
    ]
    if result.progress_percentage is not None:
        lines.append(progress_bar(result.progress_percentage))
    return "\n".join(lines)


def format_plan(progress: PlanProgress) -> str:
    plan = progress.plan
    lines = [
        f"\U0001f4cb Plano - {plan.month:02d}/{plan.year}",
        "",
        f"\U0001f4b0 Renda esperada: {format_brl(plan.expected_income)}",
        f"\U0001f512 Comprometido: {format_brl(plan.committed_expenses)}",
        f"\u2705 Livre: {format_brl(plan.free_amount)}",
    ]
    if plan.warning:
        lines.extend(["", f"\u26a0\ufe0f {plan.warning}"])
    if progress.allocations:
        lines.extend(["", "Distribuicao do livre:"])
        for item in progress.allocations:
            prefix = item.emoji or "-"
            lines.append(
                f"{prefix} {item.name} {format_brl(item.planned_amount)} "
                f"({item.percentage:.0f}%)",
            )
        if progress.unallocated_percentage > 0:
            lines.append(
                f"- Nao alocado {format_brl(progress.unallocated_amount)} "
                f"({progress.unallocated_percentage:.0f}%)",
            )
    return "\n".join(lines)


def format_plan_update(plan: MonthlyPlanRead) -> str:
    return "\n".join(
        [
            "\u2705 Planejamento atualizado",
            "",
            f"\U0001f4b0 Renda esperada: {format_brl(plan.expected_income)}",
            f"\U0001f512 Comprometido: {format_brl(plan.committed_expenses)}",
            f"\u2705 Livre: {format_brl(plan.free_amount)}",
        ],
    )


def _date_label(value) -> str:
    from app.utils.date_helpers import now_in_timezone

    today = now_in_timezone().date()
    if value == today:
        return "Hoje"
    if value == today + timedelta(days=1):
        return "Amanha"
    return value.strftime("%d/%m/%Y")


def format_expense_effect(result: ExpenseEffectSimulation) -> str:
    lines = [
        "\U0001f50e Simulacao de despesa",
        "",
        f"\U0001f4b8 {result.description}: {format_brl(result.amount)}",
        f"\U0001f4c5 {_date_label(result.date)}",
        f"\U0001f3f7\ufe0f Categoria sugerida: {result.category_name}",
        "",
        "Se voce gastar isso:",
        f"\U0001f4b0 Saldo atual: {format_brl(result.current_account_balance)} -> "
        f"{format_brl(result.projected_account_balance)}",
        f"\U0001f4c8 Saldo do mes: {format_brl(result.current_monthly_balance)} -> "
        f"{format_brl(result.projected_monthly_balance)}",
        f"\u2705 Livre no plano: {format_brl(result.current_plan_remaining)} -> "
        f"{format_brl(result.projected_plan_remaining)}",
    ]

    if result.allocation:
        allocation = result.allocation
        prefix = allocation.emoji or "-"
        lines.extend(
            [
                "",
                f"{prefix} Fatia {allocation.name}:",
                f"{format_brl(allocation.current_spent)} -> "
                f"{format_brl(allocation.projected_spent)} / "
                f"{format_brl(allocation.planned_amount)} "
                f"({allocation.projected_percentage:.0f}%)",
            ],
        )

    if result.budget:
        budget = result.budget
        lines.extend(
            [
                "",
                f"\U0001f4ca {budget.category_name} este mes:",
                f"{format_brl(budget.current_spent)} -> "
                f"{format_brl(budget.projected_spent)} / "
                f"{format_brl(budget.limit_value)} "
                f"({budget.projected_percentage:.0f}%)",
                progress_bar(budget.projected_percentage),
            ],
        )

    if result.alerts:
        lines.append("")
        for alert in result.alerts:
            lines.append(f"\u26a0\ufe0f {alert}")

    lines.extend(
        [
            "",
            f"Nada foi registrado. Para lancar de verdade, envie: "
            f"{result.description.lower()} {result.amount:.2f}",
        ],
    )
    return "\n".join(lines)


def format_reset_request(pending: PendingReset) -> str:
    return "\n".join(
        [
            "\u26a0\ufe0f Reset administrativo solicitado",
            "",
            "Isso vai apagar seus dados financeiros e recriar o estado inicial.",
            "",
            "Serao apagados:",
            "- transacoes",
            "- reservas",
            "- orcamentos",
            "- plano mensal",
            "- regras de alocacao",
            "- contas e saldos",
            "",
            f"Saldo inicial apos reset: {format_brl(pending.initial_balance)}",
            "",
            "Para confirmar, envie:",
            f"/confirmar_reset {pending.confirmation_code}",
            "",
            "Se nao quiser resetar, ignore esta mensagem.",
        ],
    )


def format_reset_success(result: ResetResult) -> str:
    return "\n".join(
        [
            "\u2705 Reset concluido",
            "",
            "O banco financeiro foi recriado para o usuario padrao.",
            f"Saldo inicial da conta padrao: {format_brl(result.initial_balance)}",
            "",
            "Voce pode comecar de novo enviando uma despesa, receita ou /saldo.",
        ],
    )


def format_reset_refused(reason: str) -> str:
    return "\n".join(
        [
            "Nao executei o reset.",
            "",
            f"Motivo: {reason}",
        ],
    )


def start_message() -> str:
    return (
        "Bem-vindo ao FinTrack.\n\n"
        "Exemplos:\n"
        "- mercado 45\n"
        "- recebi 1500\n"
        "- guardei 100 reserva\n"
        "- /efeito pizza de 42 reais hoje\n"
        "- /reset 5000\n"
        "- /saldo\n"
        "- /resumo\n"
        "- /planejamento"
    )


def help_message() -> str:
    return (
        "Comandos: /saldo, /resumo, /reservas, /categorias, /extrato, "
        "/grafico, /grafico barras, /planejamento, /efeito, /reset.\n\n"
        "Voce tambem pode escrever: mercado 45, recebi 1500, "
        "guardei 100 reserva, definir renda 3000, comprometido 1800, "
        "/efeito pizza de 42 reais hoje."
    )
