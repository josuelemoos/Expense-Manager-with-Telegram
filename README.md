# FinTrack

Sistema pessoal de gestao financeira com FastAPI, PostgreSQL, SQLModel e Alembic.

## Fase 1

Esta fase cria a base do projeto:

- estrutura de pastas do backend e placeholders do frontend;
- PostgreSQL via Docker Compose;
- app FastAPI minimo;
- modelos SQLModel da especificacao;
- Alembic com migration inicial;
- seed idempotente com usuario MVP, contas, categorias, reservas e regras de alocacao.

## Rodando com Docker

```bash
docker compose up --build
```

O backend aplica as migrations, executa o seed e sobe em `http://localhost:8000`.

Health check:

```bash
curl http://localhost:8000/health
```

Swagger:

```text
http://localhost:8000/docs
```

## Endpoints

Todos os endpoints da API ficam sob o prefixo `/api/v1`.

### Contas

- `GET /accounts` lista contas ativas do usuario padrao.
- `GET /accounts/balance` retorna saldo por conta e total geral.

### Categorias

- `GET /categories` lista categorias ativas.
- `GET /categories?type=expense` filtra por tipo (`expense` ou `income`).

### Transacoes

- `POST /transactions` registra receita ou despesa e atualiza o saldo da conta.
- `GET /transactions` lista transacoes.
- Filtros: `month`, `year`, `type`, `category_id`, `limit`, `offset`.

Exemplo:

```bash
curl -X POST http://localhost:8000/api/v1/transactions \
  -H "Content-Type: application/json" \
  -d '{"type":"expense","amount":45,"description":"Mercado"}'
```

### Reservas

- `GET /reserves` lista reservas ativas.
- `POST /reserves` cria uma reserva.
- `POST /reserves/{reserve_id}/deposit` aporta em uma reserva, baixa o saldo da conta e registra a transacao.

### Resumos

- `GET /summary/monthly` retorna receitas, despesas, saldo mensal e gastos por categoria.
- `GET /summary/dashboard` retorna dados consolidados para o dashboard.
- Filtros: `month` e `year`.

### Orcamentos

- `GET /budgets` lista orcamentos.
- `POST /budgets` cria ou atualiza o limite mensal de uma categoria.
- `GET /budgets/progress` retorna uso do orcamento e alertas.

### Planejamento

- `GET /plan` retorna o plano mensal.
- `POST /plan` cria ou atualiza renda esperada e gastos comprometidos.
- `GET /plan/allocations` lista regras de alocacao.
- `POST /plan/allocations` cria ou atualiza uma regra de alocacao.
- `GET /plan/progress` compara o plano com os gastos reais.

### Graficos

- `GET /charts/pie` retorna PNG de gastos por categoria.
- `GET /charts/bars` retorna PNG de receitas vs. despesas dos ultimos meses.

### Telegram

- `POST /telegram/webhook` recebe updates do Telegram.
- `POST /telegram/setup` registra `TELEGRAM_WEBHOOK_URL` no Telegram.

## Rodando comandos do backend

```bash
cd backend
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```
