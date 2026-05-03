# SPEC — Sistema de Gestão Financeira Pessoal
> Arquivo de especificação para implementação por IA CLI (Claude Code, Aider, etc.)
> Leia este arquivo inteiro antes de escrever qualquer linha de código.

---

## 1. VISÃO GERAL

Sistema pessoal de controle financeiro com interface via Telegram e painel web.
O objetivo central é que o usuário possa registrar receitas, despesas e reservas
enviando mensagens em linguagem natural pelo Telegram, e acompanhar tudo num
dashboard web simples.

**Filosofia de desenvolvimento:**
- MVP primeiro. Não adicione funcionalidades fora do escopo desta spec.
- Código limpo e modular desde o início.
- Cada módulo deve ser testável de forma isolada.
- Nunca misturar lógica de negócio com rotas ou com acesso ao banco.

---

## 2. STACK TECNOLÓGICA

| Camada         | Tecnologia             | Justificativa                            |
|----------------|------------------------|------------------------------------------|
| Backend        | FastAPI (Python 3.11+) | Rápido, tipado, documentação automática  |
| Banco de dados | PostgreSQL 15+         | Confiável, robusto para dados financeiros|
| ORM            | SQLModel               | Une SQLAlchemy + Pydantic elegantemente  |
| Migrações      | Alembic                | Controle de versão do banco              |
| Bot Telegram   | python-telegram-bot    | Biblioteca madura e bem documentada      |
| Frontend       | Next.js 14 (App Router)| SSR, rápido, fácil de escalar            |
| Estilização    | Tailwind CSS           | Produtividade e consistência visual      |
| Gráficos web   | Recharts               | Simples de integrar com React            |
| Gráficos bot   | matplotlib + Pillow    | Gerar imagens PNG para enviar no Telegram|
| Testes         | pytest + httpx         | Padrão Python, suporte a async           |
| Containerização| Docker + Compose       | Facilita dev e deploy                    |
| Variáveis      | python-dotenv          | Gestão de segredos                       |

---

## 3. ESTRUTURA DE PASTAS

```
fintrack/
├── backend/
│   ├── app/
│   │   ├── main.py                  # Entrypoint FastAPI
│   │   ├── config.py                # Settings via pydantic-settings
│   │   ├── database.py              # Engine, sessão, base
│   │   ├── models/                  # Modelos SQLModel (tabelas)
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── account.py
│   │   │   ├── category.py
│   │   │   ├── transaction.py
│   │   │   ├── reserve.py
│   │   │   ├── budget.py
│   │   │   ├── monthly_plan.py      # Plano mensal (renda + comprometido)
│   │   │   └── allocation_rule.py   # Regras de distribuição do livre
│   │   ├── schemas/                 # Schemas Pydantic (request/response)
│   │   │   ├── __init__.py
│   │   │   ├── transaction.py
│   │   │   ├── reserve.py
│   │   │   ├── summary.py
│   │   │   └── plan.py              # Schemas do plano mensal
│   │   ├── routers/                 # Rotas FastAPI
│   │   │   ├── __init__.py
│   │   │   ├── transactions.py
│   │   │   ├── accounts.py
│   │   │   ├── categories.py
│   │   │   ├── reserves.py
│   │   │   ├── budgets.py
│   │   │   ├── summary.py
│   │   │   ├── plan.py              # Endpoints do plano mensal
│   │   │   └── telegram.py          # Webhook do Telegram
│   │   ├── services/                # Lógica de negócio
│   │   │   ├── __init__.py
│   │   │   ├── transaction_service.py
│   │   │   ├── reserve_service.py
│   │   │   ├── summary_service.py
│   │   │   ├── budget_service.py
│   │   │   ├── plan_service.py      # Lógica do plano mensal
│   │   │   └── chart_service.py     # Geração de gráficos PNG
│   │   ├── telegram/                # Bot Telegram
│   │   │   ├── __init__.py
│   │   │   ├── bot.py               # Setup e handlers
│   │   │   ├── commands.py          # /start /saldo /resumo etc.
│   │   │   ├── parser.py            # Interpretação de mensagens livres
│   │   │   └── responses.py         # Formatação de respostas
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── formatters.py        # Formatação de valores em BRL
│   │       └── date_helpers.py
│   ├── migrations/                  # Alembic
│   │   └── versions/
│   ├── tests/
│   │   ├── test_transactions.py
│   │   ├── test_reserves.py
│   │   ├── test_parser.py
│   │   ├── test_summary.py
│   │   ├── test_plan.py             # Testes do plano mensal
│   │   └── test_charts.py           # Testes de geração de gráficos
│   ├── alembic.ini
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx                 # Dashboard principal
│   │   ├── transactions/
│   │   │   └── page.tsx             # Extrato
│   │   ├── reserves/
│   │   │   └── page.tsx             # Reservas
│   │   ├── categories/
│   │   │   └── page.tsx             # Categorias e orçamentos
│   │   └── planning/
│   │       └── page.tsx             # Planejamento mensal
│   ├── components/
│   │   ├── SummaryCards.tsx
│   │   ├── TransactionList.tsx
│   │   ├── ReserveCard.tsx
│   │   ├── CategoryProgress.tsx
│   │   ├── MonthlyChart.tsx
│   │   ├── PlanSummary.tsx          # Card de planejamento no dashboard
│   │   └── AllocationChart.tsx      # Gráfico de pizza das alocações
│   ├── lib/
│   │   └── api.ts                   # Cliente HTTP para o backend
│   ├── package.json
│   └── .env.local.example
│
├── docker-compose.yml
├── docker-compose.dev.yml
└── README.md
```

---

## 4. BANCO DE DADOS — MODELOS

### 4.1 users
```sql
id              SERIAL PRIMARY KEY
name            VARCHAR(100) NOT NULL
email           VARCHAR(150) UNIQUE NOT NULL
password_hash   VARCHAR(255) NOT NULL
telegram_chat_id BIGINT UNIQUE          -- vincula usuário ao chat do Telegram
created_at      TIMESTAMP DEFAULT NOW()
is_active       BOOLEAN DEFAULT TRUE
```

### 4.2 accounts
Representa onde o dinheiro está (carteira, banco, poupança).
```sql
id              SERIAL PRIMARY KEY
user_id         INT REFERENCES users(id) ON DELETE CASCADE
name            VARCHAR(100) NOT NULL
type            VARCHAR(30) NOT NULL    -- 'wallet' | 'bank' | 'savings' | 'credit'
initial_balance DECIMAL(12,2) DEFAULT 0
current_balance DECIMAL(12,2) DEFAULT 0
created_at      TIMESTAMP DEFAULT NOW()
is_active       BOOLEAN DEFAULT TRUE
```

### 4.3 categories
```sql
id              SERIAL PRIMARY KEY
user_id         INT REFERENCES users(id) ON DELETE CASCADE
name            VARCHAR(100) NOT NULL
type            VARCHAR(10) NOT NULL    -- 'expense' | 'income'
monthly_limit   DECIMAL(12,2)          -- NULL = sem limite
color           VARCHAR(7)             -- Hex color para UI (#FF5733)
icon            VARCHAR(50)            -- Nome do ícone (opcional)
is_active       BOOLEAN DEFAULT TRUE
```

**Categorias padrão a criar no seed:**
- Despesas: Alimentação, Transporte, Moradia, Saúde, Lazer, Educação, Roupas, Contas fixas, Outros
- Receitas: Salário, Freelance, Investimentos, Outros

**Aliases para o parser (mapeamento palavra → categoria):**
```python
CATEGORY_ALIASES = {
    # Alimentação
    "mercado": "Alimentação",
    "supermercado": "Alimentação",
    "padaria": "Alimentação",
    "ifood": "Alimentação",
    "restaurante": "Alimentação",
    "lanche": "Alimentação",
    "almoço": "Alimentação",
    "jantar": "Alimentação",
    # Transporte
    "uber": "Transporte",
    "ônibus": "Transporte",
    "gasolina": "Transporte",
    "combustível": "Transporte",
    "99": "Transporte",
    "taxi": "Transporte",
    "metrô": "Transporte",
    # Saúde
    "farmácia": "Saúde",
    "remédio": "Saúde",
    "médico": "Saúde",
    "consulta": "Saúde",
    "academia": "Saúde",
    # Contas fixas
    "luz": "Contas fixas",
    "água": "Contas fixas",
    "internet": "Contas fixas",
    "aluguel": "Moradia",
    # Receitas
    "salário": "Salário",
    "freela": "Freelance",
    "freelance": "Freelance",
}
```

### 4.4 transactions
```sql
id              SERIAL PRIMARY KEY
user_id         INT REFERENCES users(id) ON DELETE CASCADE
account_id      INT REFERENCES accounts(id)
category_id     INT REFERENCES categories(id)
type            VARCHAR(15) NOT NULL    -- 'income' | 'expense' | 'transfer'
amount          DECIMAL(12,2) NOT NULL  -- Sempre positivo
description     VARCHAR(255) NOT NULL
date            DATE NOT NULL DEFAULT CURRENT_DATE
notes           TEXT
source          VARCHAR(20) DEFAULT 'manual' -- 'manual' | 'telegram' | 'import'
created_at      TIMESTAMP DEFAULT NOW()
```

### 4.5 reserves
```sql
id              SERIAL PRIMARY KEY
user_id         INT REFERENCES users(id) ON DELETE CASCADE
name            VARCHAR(100) NOT NULL
current_value   DECIMAL(12,2) DEFAULT 0
goal_value      DECIMAL(12,2)          -- NULL = sem meta
description     TEXT
created_at      TIMESTAMP DEFAULT NOW()
is_active       BOOLEAN DEFAULT TRUE
```

**Reservas padrão a criar no seed:**
- Reserva de Emergência (meta: 6x renda mensal)
- Viagem
- Outros

### 4.6 budgets
Controla o limite mensal por categoria.
```sql
id              SERIAL PRIMARY KEY
user_id         INT REFERENCES users(id) ON DELETE CASCADE
category_id     INT REFERENCES categories(id)
month           INT NOT NULL            -- 1-12
year            INT NOT NULL
limit_value     DECIMAL(12,2) NOT NULL
UNIQUE(user_id, category_id, month, year)
```

### 4.7 monthly_plans
Define a renda esperada e o comprometido de cada mês.
```sql
id                  SERIAL PRIMARY KEY
user_id             INT REFERENCES users(id) ON DELETE CASCADE
month               INT NOT NULL            -- 1-12
year                INT NOT NULL
expected_income     DECIMAL(12,2) NOT NULL  -- Renda esperada do mês
committed_expenses  DECIMAL(12,2) NOT NULL  -- Gastos fixos obrigatórios
notes               TEXT
created_at          TIMESTAMP DEFAULT NOW()
updated_at          TIMESTAMP DEFAULT NOW()
UNIQUE(user_id, month, year)
```

Campo calculado (não armazenado, computado na query):
```
free_amount = expected_income - committed_expenses
```

### 4.8 allocation_rules
Define como distribuir o valor livre entre objetivos.
```sql
id              SERIAL PRIMARY KEY
user_id         INT REFERENCES users(id) ON DELETE CASCADE
name            VARCHAR(100) NOT NULL   -- ex: "Investimentos", "Lazer", "Reserva"
percentage      DECIMAL(5,2) NOT NULL   -- ex: 40.00 (representa 40%)
category_id     INT REFERENCES categories(id)  -- NULL = sem categoria vinculada
emoji           VARCHAR(10)             -- ex: "📈", "🎉", "🛡️"
sort_order      INT DEFAULT 0           -- Ordem de exibição
is_active       BOOLEAN DEFAULT TRUE
```

Regra: a soma de todos os `percentage` ativos de um usuário deve ser <= 100.
Se < 100, o restante é exibido como "Não alocado".

**Alocações padrão a criar no seed:**
```
Investimentos  40%  📈
Lazer          20%  🎉
Reserva        20%  🛡️
Outros         20%  📦
```

---

## 5. REGRAS DE NEGÓCIO

### RN-01: Registrar despesa
1. Salvar transação com `type = 'expense'`
2. Subtrair `amount` do `current_balance` da conta
3. Verificar se o gasto do mês na categoria ultrapassou o `monthly_limit` do budget
4. Se ultrapassou: adicionar alerta na resposta
5. Retornar: valor gasto, categoria, saldo atual, % do orçamento usado na categoria

### RN-02: Registrar receita
1. Salvar transação com `type = 'income'`
2. Somar `amount` ao `current_balance` da conta
3. Retornar: valor recebido, categoria, novo saldo

### RN-03: Aportar em reserva
1. Verificar se o saldo da conta cobre o aporte
2. Se não cobre: retornar erro com mensagem clara
3. Subtrair `amount` do `current_balance` da conta
4. Somar `amount` ao `current_value` da reserva
5. Registrar como transação com `type = 'expense'` e categoria "Reservas"
6. Retornar: novo valor da reserva, progresso em % se houver meta

### RN-04: Consultar saldo
1. Somar `current_balance` de todas as contas ativas do usuário
2. Retornar: saldo por conta e total geral

### RN-05: Resumo mensal
1. Calcular total de receitas do mês atual
2. Calcular total de despesas do mês atual
3. Calcular saldo do mês (receitas - despesas)
4. Listar gastos por categoria
5. Identificar top 3 categorias com maior gasto

### RN-06: Alerta de orçamento
1. Ao registrar despesa, calcular: total gasto na categoria no mês / limite mensal
2. Se >= 80%: alertar que está próximo do limite
3. Se >= 100%: alertar que ultrapassou o limite

### RN-07: Conta padrão
Se o usuário não especificar a conta na mensagem, usar a conta marcada como padrão.
O sistema deve ter uma conta padrão definida para cada usuário.
Adicionar campo `is_default BOOLEAN DEFAULT FALSE` na tabela `accounts`.

### RN-08: Plano mensal
1. O usuário define `expected_income` (renda esperada) e `committed_expenses` (comprometido)
2. O sistema calcula `free_amount = expected_income - committed_expenses`
3. `free_amount` não pode ser negativo — retornar erro se `committed > expected`
4. O plano é por mês/ano. Se não existir plano para o mês atual, retornar zeros com aviso

### RN-09: Distribuição do livre
1. Para cada `allocation_rule` ativa do usuário, calcular: `valor = free_amount * (percentage / 100)`
2. Comparar com o gasto real na categoria vinculada no mês
3. Exibir progresso: quanto foi usado de cada fatia
4. Alertar se uma fatia foi ultrapassada

### RN-10: Gráfico pelo Telegram
1. O `chart_service` gera uma imagem PNG em memória (sem salvar em disco)
2. Tipos suportados:
   - `pizza`: gastos do mês atual por categoria (excluir categorias com valor zero)
   - `barras`: receita vs. despesa dos últimos 6 meses
3. A imagem é enviada via `bot.send_photo()` com `BytesIO` como buffer
4. Sempre incluir título e legenda na imagem

5. Usar paleta de cores consistente com o frontend

### RN-11: Atualizar plano pelo Telegram
1. `definir renda 3000` → atualiza `expected_income` do mês atual
2. `comprometido 1800` → atualiza `committed_expenses` do mês atual
3. Se o plano do mês não existir, criar automaticamente
4. Sempre responder com o resumo atualizado do plano

### RN-12: Simular efeito de despesa
1. O comando `/efeito` simula o impacto de uma despesa hipotética sem salvar transação no banco.
2. O parser deve extrair descrição, valor e data opcional da mensagem.
3. Se a data não for informada, usar a data atual no fuso `America/Fortaleza`.
4. A simulação deve calcular:
   - saldo atual após a despesa hipotética;
   - saldo mensal projetado após a despesa;
   - impacto no plano mensal (`free_amount` restante);
   - impacto na fatia de alocação relacionada à categoria sugerida;
   - impacto no orçamento da categoria, quando houver budget configurado.
5. A categoria deve ser sugerida usando os mesmos aliases do parser de despesas.
6. A resposta deve deixar claro que é uma simulação e que nada foi registrado.
7. Se o valor passar do saldo disponível, orçamento ou fatia do plano, retornar alerta amigável.
8. Exemplos de entrada:
   - `/efeito pizza de 42 reais hoje`
   - `/efeito mercado 120 amanhã`
   - `/efeito uber 35`
   - `/efeito cinema 60 dia 15`

### RN-13: Reset administrativo pelo Telegram
1. O comando `/reset` deve ser tratado como operação administrativa destrutiva.
2. O comando nunca deve executar imediatamente em uma única mensagem. O fluxo obrigatório é:
   - usuário envia `/reset` ou `/reset 5000`;
   - bot responde com resumo do que será apagado e pede confirmação;
   - usuário confirma com `/confirmar_reset <codigo>`;
   - somente então o reset é executado.
3. `/reset` limpa 100% dos dados financeiros do usuário padrão e recria o estado inicial do seed:
   - transações;
   - reservas;
   - budgets;
   - plano mensal;
   - regras de alocação;
   - contas e saldos;
   - categorias padrão.
4. `/reset 5000` faz o mesmo reset, mas define a conta padrão com `initial_balance = 5000.00` e `current_balance = 5000.00`.
5. O comando deve ser permitido somente para `DEFAULT_USER_TELEGRAM_CHAT_ID`.
6. O comando deve registrar log estruturado com `chat_id`, data/hora, modo (`full` ou `with_balance`) e valor informado, sem registrar tokens ou segredos.
7. A operação deve rodar dentro de uma transação atômica. Se qualquer etapa falhar, nenhum dado deve ficar parcialmente resetado.
8. Valores aceitos para `/reset <valor>`:
   - valor decimal positivo;
   - máximo configurável por `RESET_MAX_BALANCE`, padrão `1000000.00`;
   - zero é permitido apenas se enviado explicitamente como `/reset 0`.
9. O reset deve ser recusado em ambiente de produção, a menos que `ENABLE_TELEGRAM_RESET=true`.
10. A resposta final deve deixar claro que a ação foi executada e qual saldo inicial ficou configurado.

Observação de produto: esta feature é útil para ambiente pessoal, testes e recomeços de organização financeira, mas é perigosa. Não implementar como atalho sem confirmação. Para ajustes pontuais de saldo, preferir uma feature separada de "ajuste de saldo" que cria uma transação auditável, em vez de apagar histórico.

---

## 6. API — ENDPOINTS

Prefixo: `/api/v1`
Autenticação: Bearer JWT (implementar depois do MVP básico funcionar)

### Transações
```
POST   /transactions          — Criar transação
GET    /transactions          — Listar (query: month, year, type, category_id, limit, offset)
GET    /transactions/{id}     — Buscar por ID
DELETE /transactions/{id}     — Deletar
```

### Contas
```
GET    /accounts              — Listar contas
POST   /accounts              — Criar conta
GET    /accounts/balance       — Saldo total e por conta
```

### Categorias
```
GET    /categories            — Listar categorias (query: type)
POST   /categories            — Criar categoria
```

### Reservas
```
GET    /reserves              — Listar reservas
POST   /reserves              — Criar reserva
POST   /reserves/{id}/deposit — Aportar valor
GET    /reserves/summary       — Resumo total das reservas
```

### Orçamentos
```
GET    /budgets               — Listar (query: month, year)
POST   /budgets               — Criar/atualizar orçamento
GET    /budgets/progress       — Progresso do mês atual por categoria
```

### Plano Mensal
```
GET    /plan                  — Buscar plano do mês (query: month, year)
POST   /plan                  — Criar ou atualizar plano do mês
GET    /plan/allocations       — Listar regras de alocação
POST   /plan/allocations       — Criar/atualizar regra de alocação
GET    /plan/progress          — Plano vs. realidade do mês atual
```

### Gráficos
```
GET    /charts/pie             — PNG: pizza de gastos por categoria (query: month, year)
GET    /charts/bars            — PNG: barras receita vs. despesa (query: months=6)
```
Esses endpoints retornam `Content-Type: image/png` diretamente.
O bot Telegram chama esses endpoints e envia a imagem com `send_photo()`.

### Resumo
```
GET    /summary/monthly        — Resumo do mês (query: month, year)
GET    /summary/dashboard      — Dados para o dashboard principal
```

### Telegram
```
POST   /telegram/webhook       — Receber updates do Telegram
POST   /telegram/setup         — Registrar webhook no Telegram
```

---

## 7. PARSER DE MENSAGENS

### 7.1 Fluxo de interpretação
```
mensagem recebida
    → limpar texto (strip, lowercase)
    → identificar intenção (despesa | receita | reserva | consulta)
    → extrair valor numérico
    → extrair descrição
    → sugerir categoria via aliases
    → retornar ParsedMessage ou ParseError
```

### 7.2 Padrões reconhecidos

**Despesas:**
```
"mercado 45"              → expense, 45.00, Alimentação
"gastei 45 no mercado"    → expense, 45.00, Alimentação
"ifood 27.50"             → expense, 27.50, Alimentação
"uber 15"                 → expense, 15.00, Transporte
"45 farmácia"             → expense, 45.00, Saúde
```

**Receitas:**
```
"recebi 1300"             → income, 1300.00, Outros
"salário 2500"            → income, 2500.00, Salário
"freela 400"              → income, 400.00, Freelance
"recebi 500 freela"       → income, 500.00, Freelance
```

**Reservas:**
```
"guardei 100 reserva"     → reserve_deposit, 100.00
"guardei 200 na viagem"   → reserve_deposit, 200.00, reserva=Viagem
"guardei 150"             → reserve_deposit, 150.00, reserva=padrão
```

**Consultas:**
```
"/saldo"                  → query_balance
"quanto tenho?"           → query_balance
"/resumo"                 → query_monthly_summary
"como estou esse mês?"    → query_monthly_summary
"/reservas"               → query_reserves
"/grafico"                → chart_pie
"/grafico pizza"          → chart_pie
"/grafico barras"         → chart_bars
"gráfico do mês"          → chart_pie
"/planejamento"           → query_plan
"/efeito pizza de 42 reais hoje" → simulate_expense_effect, 42.00, Alimentação, description=Pizza, date=today
"/reset"                  → request_reset, mode=full
"/reset 5000"             → request_reset, mode=with_balance, amount=5000.00
"/confirmar_reset 123456" → confirm_reset, code=123456
"definir renda 3000"      → set_income, 3000.00
"comprometido 1800"       → set_committed, 1800.00
```

### 7.3 Schema da resposta do parser
```python
class ParsedMessage:
    intent: Literal["expense", "income", "reserve_deposit",
                    "query_balance", "query_summary", "query_reserves",
                    "query_plan", "chart_pie", "chart_bars",
                    "simulate_expense_effect", "request_reset",
                    "confirm_reset", "set_income", "set_committed",
                    "unknown"]
    amount: Optional[float]
    description: Optional[str]
    suggested_category: Optional[str]
    date: Optional[date]
    confirmation_code: Optional[str]
    reserve_name: Optional[str]
    raw_text: str
    confidence: float  # 0.0 a 1.0

class ParseError:
    error_type: Literal["no_amount", "no_context", "ambiguous", "unknown_intent"]
    message: str        # Mensagem amigável para o usuário
    suggestion: str     # Como corrigir o input
```

### 7.4 Tratamento de ambiguidade
```
Mensagem só com número (ex: "45"):
→ "Você quer registrar R$ 45,00 como despesa ou receita?"
→ Oferecer botões inline: [💸 Despesa] [💰 Receita]

Mensagem sem valor (ex: "comprei uma coisa"):
→ "Não consegui identificar o valor. Tente: mercado 45"

Descrição sem categoria conhecida:
→ Usar categoria "Outros" e informar na resposta
```

---

## 8. BOT TELEGRAM

### 8.1 Comandos
```
/start          — Boas-vindas + instruções de uso
/ajuda          — Exibir ajuda completa com exemplos
/saldo          — Saldo atual (total e por conta)
/resumo         — Resumo do mês atual
/reservas       — Status das reservas
/categorias     — Listar categorias ativas
/extrato        — Últimas 10 transações
/grafico        — Gráfico de pizza dos gastos do mês (envia imagem)
/grafico barras — Evolução dos últimos 6 meses (envia imagem)
/planejamento   — Plano mensal vs. realidade
/efeito         — Simula o impacto de uma despesa sem registrar transação
/reset          — Solicita reset administrativo com confirmação obrigatória
```

### 8.2 Formato das respostas

**Despesa registrada:**
```
✅ Despesa registrada

💸 R$ 42,00 · Alimentação
📝 Mercado
📅 02/05/2026

📊 Alimentação este mês: R$ 380,00 / R$ 500,00 (76%)
[████████░░] 76%

💰 Saldo atual: R$ 1.240,00
```

**Receita registrada:**
```
✅ Receita registrada

💰 R$ 2.500,00 · Salário
📝 Salário maio
📅 02/05/2026

💰 Saldo atual: R$ 3.740,00
```

**Alerta de orçamento (>= 80%):**
```
⚠️ Atenção: você já usou 95% do orçamento de Alimentação este mês.
```

**Saldo (/saldo):**
```
💰 Saldo atual

🏦 Nubank: R$ 1.240,00
👛 Carteira: R$ 80,00
─────────────────
Total: R$ 1.320,00
```

**Resumo mensal (/resumo):**
```
📊 Resumo — Maio/2026

💰 Receitas: R$ 3.200,00
💸 Despesas: R$ 1.960,00
📈 Saldo do mês: R$ 1.240,00

Top gastos:
  1. Moradia     R$ 800,00 (40%)
  2. Alimentação R$ 380,00 (19%)
  3. Transporte  R$ 210,00 (10%)
```

**Reservas (/reservas):**
```
🏦 Suas reservas

🛡️ Emergência
   R$ 3.200,00 / R$ 6.000,00
   [█████░░░░░] 53%

✈️ Viagem
   R$ 800,00 / R$ 2.000,00
   [████░░░░░░] 40%

Total reservado: R$ 4.000,00
```

**Planejamento (/planejamento):**
```
📋 Plano — Maio/2026

💰 Renda esperada:     R$ 3.000,00
🔒 Comprometido:       R$ 1.800,00
✅ Livre:              R$ 1.200,00

Distribuição do livre:
  📈 Investimentos  R$ 480,00  (40%)
  🎉 Lazer          R$ 360,00  (30%)
  🛡️ Reserva        R$ 240,00  (20%)
  📦 Outros         R$ 120,00  (10%)

Real vs. planejado este mês:
  🎉 Lazer     R$ 210,00 / R$ 360,00  ✅ 58%
  📈 Investido R$ 0,00   / R$ 480,00  ⚠️ 0%
```

**Atualizar renda:**
```
✅ Renda esperada atualizada

💰 Renda esperada:  R$ 3.000,00
🔒 Comprometido:    R$ 1.800,00
✅ Livre:           R$ 1.200,00
```

**Efeito de despesa (/efeito):**
```
🔎 Simulação de despesa

💸 Pizza: R$ 42,00
📅 Hoje
🏷️ Categoria sugerida: Alimentação

Se você gastar isso agora:
💰 Saldo atual:       R$ 1.240,00 → R$ 1.198,00
📈 Saldo do mês:      R$ 1.040,00 → R$ 998,00
✅ Livre no plano:    R$ 360,00 → R$ 318,00

📊 Alimentação este mês:
R$ 380,00 → R$ 422,00 / R$ 500,00 (84%)

⚠️ Atenção: isso deixa Alimentação acima de 80% do orçamento.

Nada foi registrado. Para lançar de verdade, envie: pizza 42
```

**Solicitar reset (/reset 5000):**
```
⚠️ Reset administrativo solicitado

Isso vai apagar seus dados financeiros e recriar o estado inicial.

Serão apagados:
- transações
- reservas
- orçamentos
- plano mensal
- regras de alocação
- contas e saldos

Saldo inicial após reset: R$ 5.000,00

Para confirmar, envie:
/confirmar_reset 123456

Se não quiser resetar, ignore esta mensagem.
```

**Reset confirmado:**
```
✅ Reset concluído

O banco financeiro foi recriado para o usuário padrão.
Saldo inicial da conta padrão: R$ 5.000,00

Você pode começar de novo enviando uma despesa, receita ou /saldo.
```

**Reset recusado por segurança:**
```
Não executei o reset.

Motivo: confirmação inválida ou reset desativado neste ambiente.
```

### 8.3 Segurança do bot
- Verificar `chat_id` em toda mensagem recebida
- Rejeitar mensagens de `chat_id` não cadastrado com resposta padrão
- Logar tentativas não autorizadas
- O `telegram_chat_id` do usuário é definido no setup inicial via `/start`

---

## 9. DASHBOARD WEB

### 9.1 Página principal (/)
Componentes:
- **SummaryCards**: 4 cards com receita, despesa, saldo do mês, total reservado
- **PlanSummary**: card com renda esperada, comprometido, livre e distribuição das fatias
- **CategoryProgress**: barras de progresso por categoria (vs. orçamento)
- **MonthlyChart**: gráfico de barras (receita vs. despesa dos últimos 6 meses)
- **RecentTransactions**: últimas 5 transações com tipo, valor e categoria

### 9.2 Página de extrato (/transactions)
- Tabela com todas as transações do mês
- Filtros: período, tipo (receita/despesa), categoria
- Botão para adicionar transação manualmente (modal)

### 9.3 Página de reservas (/reserves)
- Cards para cada reserva com barra de progresso
- Botão de aporte manual
- Histórico de aportes por reserva

### 9.4 Página de categorias (/categories)
- Lista de categorias com gasto acumulado no mês
- Editar limite mensal inline
- Indicação visual se está acima do limite

### 9.5 Página de planejamento (/planning)
- Formulário para definir renda esperada e comprometido do mês
- Lista editável de regras de alocação (nome, percentual, emoji)
- Validação: soma dos percentuais não pode ultrapassar 100%
- Gráfico de pizza com `AllocationChart` mostrando as fatias planejadas
- Tabela de progresso: planejado vs. real por fatia

---

## 10. CONFIGURAÇÃO E AMBIENTE

### 10.1 Variáveis de ambiente (.env)
```env
# Banco
DATABASE_URL=postgresql://user:password@localhost:5432/fintrack

# App
SECRET_KEY=sua_chave_secreta_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Telegram
TELEGRAM_BOT_TOKEN=seu_token_aqui
TELEGRAM_WEBHOOK_URL=https://seu-dominio.com/api/v1/telegram/webhook

# Usuário inicial (para MVP single-user)
DEFAULT_USER_ID=1
DEFAULT_USER_TELEGRAM_CHAT_ID=seu_chat_id_aqui

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### 10.2 docker-compose.yml
```yaml
version: "3.9"
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: fintrack
      POSTGRES_USER: fintrack
      POSTGRES_PASSWORD: fintrack
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - db
    env_file: ./backend/.env
    volumes:
      - ./backend:/app

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    env_file: ./frontend/.env.local

volumes:
  postgres_data:
```

---

## 11. ORDEM DE IMPLEMENTAÇÃO

Siga esta ordem estritamente. Não avance para a próxima fase sem a anterior funcionar.

### FASE 1 — Setup inicial
- [ ] Criar estrutura de pastas conforme seção 3
- [ ] Configurar `docker-compose.yml` com PostgreSQL
- [ ] Criar projeto FastAPI com `main.py`, `config.py`, `database.py`
- [ ] Criar modelos SQLModel (seção 4)
- [ ] Configurar Alembic e gerar primeira migration
- [ ] Criar seed com: 1 usuário, contas padrão e categorias padrão
- [ ] Verificar que o banco sobe e tabelas são criadas corretamente

### FASE 2 — API base
- [ ] Criar schemas Pydantic para request/response
- [ ] Implementar router de `accounts` (GET balance, GET list)
- [ ] Implementar router de `categories` (GET list)
- [ ] Implementar router de `transactions` (POST create, GET list)
- [ ] Implementar router de `reserves` (GET list, POST deposit)
- [ ] Implementar router de `summary` (GET monthly, GET dashboard)
- [ ] Testar todos os endpoints via Swagger (http://localhost:8000/docs)

### FASE 3 — Lógica financeira
- [ ] `transaction_service.py`: criar despesa (RN-01), criar receita (RN-02)
- [ ] `reserve_service.py`: aportar em reserva (RN-03)
- [ ] `summary_service.py`: saldo total (RN-04), resumo mensal (RN-05)
- [ ] `budget_service.py`: verificar progresso do orçamento (RN-06)
- [ ] `plan_service.py`: criar/atualizar plano (RN-08), calcular distribuição (RN-09)
- [ ] `chart_service.py`: gerar PNG de pizza e barras com matplotlib (RN-10)
- [ ] Escrever testes em `tests/test_transactions.py`, `tests/test_summary.py`, `tests/test_plan.py`

### FASE 4 — Bot Telegram
- [ ] Criar bot no BotFather, obter token, salvar no `.env`
- [ ] Implementar `telegram/parser.py` com os padrões da seção 7
- [ ] Escrever testes em `tests/test_parser.py`
- [ ] Implementar `telegram/commands.py` (/start, /saldo, /resumo, /reservas, /planejamento)
- [ ] Implementar handlers de gráfico (/grafico, /grafico barras) enviando imagem PNG
- [ ] Implementar handler de simulação de despesa (/efeito)
- [ ] Implementar fluxo administrativo de reset (/reset, /confirmar_reset) com confirmação obrigatória
- [ ] Implementar handlers de atualização de plano (definir renda, comprometido)
- [ ] Implementar `telegram/bot.py` com handler de mensagens livres
- [ ] Implementar `telegram/responses.py` com os formatos da seção 8.2
- [ ] Criar endpoint `/telegram/webhook` e registrar no Telegram
- [ ] Testar fluxo completo: mensagem → parser → service → banco → resposta

### FASE 5 — Frontend
- [ ] Criar projeto Next.js com Tailwind CSS e Recharts
- [ ] Criar `lib/api.ts` com funções para cada endpoint
- [ ] Implementar página principal com SummaryCards, PlanSummary e MonthlyChart
- [ ] Implementar página de extrato com filtros
- [ ] Implementar página de reservas
- [ ] Implementar página de categorias
- [ ] Implementar página de planejamento com formulário e AllocationChart

### FASE 6 — Qualidade
- [ ] Revisar validações de entrada em todos os endpoints
- [ ] Adicionar tratamento de erros global no FastAPI
- [ ] Garantir que saldos nunca ficam inconsistentes (transação atômica)
- [ ] Revisar mensagens de erro do bot para serem claras ao usuário
- [ ] Documentar endpoints no README

---

## 12. DECISÕES TÉCNICAS IMPORTANTES

### Transações atômicas
Sempre que uma operação envolver múltiplas escritas no banco (ex: salvar transação E atualizar saldo), usar transação de banco de dados com rollback em caso de erro:
```python
async def create_expense(session: AsyncSession, data: TransactionCreate):
    async with session.begin():
        transaction = Transaction(**data.dict())
        session.add(transaction)
        account = await session.get(Account, data.account_id)
        account.current_balance -= data.amount
        # Se qualquer linha falhar, tudo faz rollback
```

### MVP single-user
Por enquanto, o sistema serve um único usuário. O `user_id` deve ser obtido do `.env` como `DEFAULT_USER_ID`. Não adicionar autenticação complexa agora — isso vem depois.

### Sem parcelamento no MVP
Ignorar compras parceladas por enquanto. Cada transação é um valor único e pontual.

### Saldo inicial das contas
O `current_balance` é inicializado com `initial_balance` no seed. Cada transação incrementa ou decrementa o `current_balance`. Nunca recalcular o saldo somando todas as transações — manter o saldo atualizado em tempo real é mais eficiente.

### Fuso horário
Usar `America/Fortaleza` (UTC-3, sem horário de verão) como fuso padrão do sistema. Todas as datas devem ser tratadas neste fuso.

### Geração de gráficos para o Telegram
Os gráficos são gerados em memória com `matplotlib` e entregues como `BytesIO`, sem nunca salvar arquivo em disco. Usar `plt.close()` após cada geração para liberar memória. Paleta de cores padrão:
```python
CHART_COLORS = [
    "#6366f1",  # índigo   — Alimentação
    "#f59e0b",  # âmbar    — Transporte
    "#10b981",  # esmeralda — Moradia
    "#ef4444",  # vermelho  — Saúde
    "#8b5cf6",  # violeta   — Lazer
    "#3b82f6",  # azul      — Educação
    "#f97316",  # laranja   — Outros
]
```
Usar fundo branco (`#ffffff`), fonte `DejaVu Sans`, título em negrito tamanho 13.

---

## 13. TESTES — CASOS MÍNIMOS OBRIGATÓRIOS

### Parser
```python
test_parse_expense_simple()           # "mercado 45" → expense, 45.0
test_parse_expense_with_prefix()      # "gastei 30 uber" → expense, 30.0
test_parse_income_recebi()            # "recebi 1500" → income, 1500.0
test_parse_income_salario()           # "salário 2000" → income, 2000.0
test_parse_reserve_deposit()          # "guardei 100 reserva" → reserve, 100.0
test_parse_no_amount_returns_error()  # "mercado" → ParseError
test_parse_only_number_ambiguous()    # "45" → ambiguous
test_parse_query_balance()            # "quanto tenho?" → query_balance
test_parse_chart_pie()                # "/grafico" → chart_pie
test_parse_chart_bars()               # "/grafico barras" → chart_bars
test_parse_expense_effect()           # "/efeito pizza de 42 reais hoje" → simulate_expense_effect, 42.0
test_parse_reset_request()            # "/reset 5000" → request_reset, 5000.0
test_parse_reset_confirm()            # "/confirmar_reset 123456" → confirm_reset, code=123456
test_parse_set_income()               # "definir renda 3000" → set_income, 3000.0
test_parse_set_committed()            # "comprometido 1800" → set_committed, 1800.0
```

### Services
```python
test_create_expense_updates_balance()           # Saldo diminui após despesa
test_create_income_updates_balance()            # Saldo aumenta após receita
test_reserve_deposit_updates_both()             # Conta diminui, reserva aumenta
test_reserve_deposit_fails_if_no_balance()      # Erro se saldo insuficiente
test_monthly_summary_correct_totals()           # Receitas, despesas e saldo corretos
test_budget_alert_at_80_percent()               # Alerta gerado ao atingir 80%
test_plan_free_amount_calculated_correctly()    # free = expected - committed
test_plan_fails_if_committed_exceeds_income()   # Erro se comprometido > renda
test_allocation_percentages_sum_to_100()        # Validação de soma dos percentuais
test_simulate_expense_effect_does_not_persist() # /efeito não cria transação
test_simulate_expense_effect_updates_projection() # Projeção considera renda, plano e orçamento
test_reset_requires_confirmation()              # /reset sozinho não apaga dados
test_reset_recreates_seed_with_balance()        # /reset 5000 recria estado inicial com saldo 5000 após confirmação
test_reset_rolls_back_on_failure()              # Falha durante reset não deixa dados parciais
test_chart_pie_returns_png_bytes()              # chart_service retorna bytes válidos
test_chart_bars_returns_png_bytes()             # idem para barras
```

---

## 14. O QUE NÃO IMPLEMENTAR AGORA

Explicitamente fora do escopo desta versão:

- Múltiplos usuários / autenticação JWT
- Cartão de crédito com fatura e fechamento
- Compras parceladas
- Importação de extratos CSV/OFX
- Notificações agendadas pelo Telegram
- Relatórios em PDF
- Previsão de gastos futuros
- Integração com Open Finance / bancos reais
- App mobile nativo
- IA avançada no parser (usar apenas regex + aliases)

---

## 15. CHECKLIST FINAL ANTES DE CONSIDERAR O MVP PRONTO

- [ ] É possível registrar uma despesa pelo Telegram e ela aparece no dashboard
- [ ] É possível registrar uma receita pelo Telegram e o saldo é atualizado
- [ ] É possível aportar em uma reserva pelo Telegram
- [ ] O comando /saldo retorna valores corretos
- [ ] O comando /resumo retorna totais corretos do mês
- [ ] O comando /grafico envia uma imagem PNG no chat
- [ ] O comando /grafico barras envia gráfico de evolução mensal
- [ ] O comando /planejamento mostra renda, comprometido, livre e distribuição
- [ ] O comando /efeito mostra impacto simulado na renda, saldo mensal e plano sem registrar transação
- [ ] O comando /reset nunca apaga dados sem confirmação explícita
- [ ] O comando /reset 5000 recria o estado inicial com saldo padrão de R$ 5.000,00 após confirmação
- [ ] "definir renda 3000" atualiza o plano e responde com resumo
- [ ] "comprometido 1800" atualiza o comprometido e responde com resumo
- [ ] A soma dos percentuais de alocação não pode ultrapassar 100%
- [ ] O dashboard mostra saldo, receitas, despesas e o card de planejamento
- [ ] A página /planning permite editar renda, comprometido e alocações
- [ ] Mensagens inválidas retornam ajuda clara ao usuário
- [ ] Saldos são consistentes após múltiplas operações
- [ ] O sistema não aceita valores negativos
- [ ] Mensagens de chat_id não autorizado são rejeitadas
