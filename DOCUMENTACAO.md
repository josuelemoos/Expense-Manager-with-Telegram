# Documentacao do FinTrack

Este documento resume as funcoes disponiveis no FinTrack, como usar cada uma, quais comandos existem no Telegram, quais telas existem no dashboard e quais endpoints a API expoe.

## Visao geral

O FinTrack e um sistema pessoal de gestao financeira com:

- Backend FastAPI em `http://localhost:8000`
- API REST sob o prefixo `/api/v1`
- Dashboard web Next.js em `http://localhost:3000`
- PostgreSQL via Docker
- Bot Telegram via webhook
- Ngrok automatico para expor o backend ao Telegram

## Como acessar

### Dashboard web

```bash
cd frontend
npm run dev
```

Acesse:

```text
http://localhost:3000
```

### API

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

Health check:

```bash
curl http://localhost:8000/health
```

### Painel do ngrok

```text
http://localhost:4040
```

## Subir e desligar o projeto

Subir backend, banco e ngrok:

```bash
sudo docker compose up --build -d
```

Ver containers:

```bash
sudo docker compose ps
```

Desligar tudo:

```bash
sudo docker compose down
```

Reiniciar apenas o backend:

```bash
sudo docker compose restart backend
```

## Variaveis de ambiente importantes

Backend: `backend/.env`

```env
DATABASE_URL=postgresql+psycopg://fintrack:fintrack@localhost:5432/fintrack
DATABASE_ECHO=false

SECRET_KEY=sua_chave_secreta_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

TELEGRAM_BOT_TOKEN=
TELEGRAM_WEBHOOK_URL=https://seu-dominio.com/api/v1/telegram/webhook

DEFAULT_USER_ID=1
DEFAULT_USER_TELEGRAM_CHAT_ID=
DEFAULT_MONTHLY_INCOME=3000
ENABLE_TELEGRAM_RESET=false
RESET_MAX_BALANCE=1000000
TIMEZONE=America/Fortaleza
```

Frontend: `frontend/.env.local`

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

Raiz do projeto, para o ngrok automatico:

```env
NGROK_DOMAIN=obsolete-glare-reckless.ngrok-free.dev
NGROK_CONFIG=/home/josuelemoos/.config/ngrok/ngrok.yml
```

## Telegram

O bot recebe mensagens pelo endpoint:

```text
POST /api/v1/telegram/webhook
```

Para registrar o webhook:

```bash
curl -X POST http://localhost:8000/api/v1/telegram/setup
```

### Comandos do Telegram

| Comando | O que faz | Exemplo |
| --- | --- | --- |
| `/start` | Mostra boas-vindas e exemplos basicos. | `/start` |
| `/ajuda` | Mostra ajuda com comandos e exemplos. | `/ajuda` |
| `/saldo` | Mostra saldo total e por conta. | `/saldo` |
| `/resumo` | Mostra receitas, despesas, saldo do mes e top gastos. | `/resumo` |
| `/reservas` | Lista reservas e progresso das metas. | `/reservas` |
| `/categorias` | Lista categorias ativas. | `/categorias` |
| `/extrato` | Mostra as ultimas 10 transacoes. | `/extrato` |
| `/grafico` | Envia grafico de pizza dos gastos do mes. | `/grafico` |
| `/grafico barras` | Envia grafico de receitas vs despesas dos ultimos meses. | `/grafico barras` |
| `/planejamento` | Mostra plano mensal, livre e distribuicoes. | `/planejamento` |
| `/efeito` | Simula uma despesa sem registrar no banco. | `/efeito pizza de 42 reais hoje` |
| `/reset` | Solicita reset administrativo com confirmacao obrigatoria. | `/reset 5000` |
| `/confirmar_reset` | Confirma um reset solicitado anteriormente. | `/confirmar_reset 123456` |

### Registro de despesas pelo Telegram

Voce pode escrever mensagens livres. O bot tenta identificar valor, descricao e categoria.

Exemplos:

```text
mercado 45
gastei 30 uber
ifood 27.50
pizza 42
45 farmacia
```

O que acontece:

- Cria transacao do tipo `expense`
- Subtrai o valor da conta padrao
- Sugere categoria por aliases
- Verifica alerta de budget quando houver limite
- Responde com saldo atualizado

Categorias sugeridas por alguns aliases:

| Palavra | Categoria |
| --- | --- |
| mercado, supermercado, ifood, pizza, restaurante | Alimentacao |
| uber, onibus, gasolina, taxi, metro | Transporte |
| farmacia, remedio, medico, consulta | Saude |
| luz, agua, internet | Contas fixas |
| aluguel | Moradia |
| cinema | Lazer |

### Registro de receitas pelo Telegram

Exemplos:

```text
recebi 1300
salario 2500
freela 400
recebi 500 freela
```

O que acontece:

- Cria transacao do tipo `income`
- Soma o valor na conta padrao
- Sugere categoria de receita
- Responde com saldo atualizado

### Aporte em reservas pelo Telegram

Exemplos:

```text
guardei 100 reserva
guardei 200 na viagem
guardei 150
```

O que acontece:

- Subtrai o valor da conta padrao
- Soma o valor na reserva escolhida
- Registra uma despesa na categoria `Reservas`
- Mostra progresso da reserva quando houver meta

### Planejamento pelo Telegram

Definir renda esperada:

```text
definir renda 3000
```

Definir gastos comprometidos:

```text
comprometido 1800
```

Consultar plano:

```text
/planejamento
```

O plano calcula:

- Renda esperada
- Gastos comprometidos
- Valor livre
- Distribuicao do livre por regras de alocacao
- Real vs planejado do mes

### Simulacao de efeito de despesa

Comando:

```text
/efeito pizza de 42 reais hoje
```

Outros exemplos:

```text
/efeito mercado 120 amanha
/efeito uber 35
/efeito cinema 60 dia 15
```

O que a simulacao mostra:

- Saldo atual antes e depois da despesa hipotetica
- Saldo mensal antes e depois
- Valor livre restante no plano
- Impacto no budget da categoria
- Impacto na fatia de alocacao quando existir
- Alertas quando a despesa ultrapassar saldo, budget ou plano

Importante: `/efeito` nao salva transacao e nao altera saldo.

### Reset administrativo

O reset e uma funcao perigosa e fica desativada por padrao.

Para habilitar, no `backend/.env`:

```env
ENABLE_TELEGRAM_RESET=true
RESET_MAX_BALANCE=1000000
```

Depois reinicie:

```bash
sudo docker compose restart backend
```

Fluxo de uso:

```text
/reset
```

ou:

```text
/reset 5000
```

O bot responde com um codigo. Para confirmar:

```text
/confirmar_reset 123456
```

Comportamento:

- `/reset` apaga os dados financeiros e recria o seed com saldo inicial `R$ 0,00`
- `/reset 5000` apaga os dados financeiros e recria o seed com saldo inicial `R$ 5.000,00`
- Nada e apagado sem confirmacao
- A confirmacao expira
- So funciona no chat autorizado por `DEFAULT_USER_TELEGRAM_CHAT_ID`
- A operacao roda em transacao atomica

Dados apagados no reset:

- Transacoes
- Contas
- Categorias
- Reservas
- Budgets
- Plano mensal
- Regras de alocacao

Dados recriados:

- Usuario padrao
- Conta Principal
- Carteira
- Categorias padrao
- Reservas padrao
- Regras de alocacao padrao

## Dashboard web

### `/`

Pagina principal com:

- Saldo total
- Receitas do mes
- Despesas do mes
- Saldo mensal
- Grafico mensal
- Resumo do plano
- Progresso por categoria
- Ultimas transacoes

### `/transactions`

Pagina de extrato com:

- Lista de transacoes
- Filtros por periodo, tipo e categoria
- Visualizacao de entradas e saidas

### `/reserves`

Pagina de reservas com:

- Reservas ativas
- Valor atual
- Meta, quando existir
- Progresso da reserva

### `/categories`

Pagina de categorias com:

- Categorias de receita
- Categorias de despesa
- Limites mensais quando configurados
- Cor e icone da categoria

### `/planning`

Pagina de planejamento com:

- Renda esperada
- Gastos comprometidos
- Valor livre
- Regras de alocacao
- Grafico de alocacoes
- Comparacao entre planejado e realizado

## API REST

Todos os endpoints ficam sob:

```text
/api/v1
```

### Contas

| Metodo | Endpoint | Descricao |
| --- | --- | --- |
| `GET` | `/accounts` | Lista contas ativas do usuario padrao. |
| `GET` | `/accounts/balance` | Retorna saldo por conta e total geral. |

### Categorias

| Metodo | Endpoint | Descricao |
| --- | --- | --- |
| `GET` | `/categories` | Lista categorias ativas. |
| `GET` | `/categories?type=expense` | Lista apenas categorias de despesa. |
| `GET` | `/categories?type=income` | Lista apenas categorias de receita. |

### Transacoes

| Metodo | Endpoint | Descricao |
| --- | --- | --- |
| `POST` | `/transactions` | Cria receita ou despesa e atualiza saldo. |
| `GET` | `/transactions` | Lista transacoes. |

Filtros aceitos:

- `month`
- `year`
- `type`
- `category_id`
- `limit`
- `offset`

Exemplo:

```bash
curl -X POST http://localhost:8000/api/v1/transactions \
  -H "Content-Type: application/json" \
  -d '{"type":"expense","amount":45,"description":"Mercado"}'
```

### Reservas

| Metodo | Endpoint | Descricao |
| --- | --- | --- |
| `GET` | `/reserves` | Lista reservas ativas. |
| `POST` | `/reserves` | Cria uma reserva. |
| `POST` | `/reserves/{reserve_id}/deposit` | Aporta valor em uma reserva. |

### Resumos

| Metodo | Endpoint | Descricao |
| --- | --- | --- |
| `GET` | `/summary/monthly` | Retorna receitas, despesas, saldo mensal e gastos por categoria. |
| `GET` | `/summary/dashboard` | Retorna dados consolidados para o dashboard. |

Filtros aceitos:

- `month`
- `year`

### Orcamentos

| Metodo | Endpoint | Descricao |
| --- | --- | --- |
| `GET` | `/budgets` | Lista budgets. |
| `POST` | `/budgets` | Cria ou atualiza limite mensal de categoria. |
| `GET` | `/budgets/progress` | Retorna progresso e alertas de budget. |

### Planejamento

| Metodo | Endpoint | Descricao |
| --- | --- | --- |
| `GET` | `/plan` | Retorna o plano mensal. |
| `POST` | `/plan` | Cria ou atualiza renda esperada e comprometido. |
| `GET` | `/plan/allocations` | Lista regras de alocacao. |
| `POST` | `/plan/allocations` | Cria ou atualiza regra de alocacao. |
| `GET` | `/plan/progress` | Retorna plano vs realidade do mes. |

### Graficos

| Metodo | Endpoint | Descricao |
| --- | --- | --- |
| `GET` | `/charts/pie` | Retorna PNG de gastos por categoria. |
| `GET` | `/charts/bars` | Retorna PNG de receitas vs despesas. |

Os endpoints de graficos retornam `Content-Type: image/png`.

### Telegram

| Metodo | Endpoint | Descricao |
| --- | --- | --- |
| `POST` | `/telegram/webhook` | Recebe updates do Telegram. |
| `POST` | `/telegram/setup` | Registra `TELEGRAM_WEBHOOK_URL` no Telegram. |

## Funcoes internas principais

### Parser do Telegram

Arquivo:

```text
backend/app/telegram/parser.py
```

Funcao principal:

```python
parse_message(text: str)
```

Responsavel por transformar texto do Telegram em intents:

- `expense`
- `income`
- `reserve_deposit`
- `query_balance`
- `query_summary`
- `query_reserves`
- `query_plan`
- `chart_pie`
- `chart_bars`
- `simulate_expense_effect`
- `request_reset`
- `confirm_reset`
- `set_income`
- `set_committed`
- `unknown`

### Comandos do Telegram

Arquivo:

```text
backend/app/telegram/commands.py
```

Funcoes principais:

| Funcao | Descricao |
| --- | --- |
| `start_command` | Responde `/start`. |
| `help_command` | Responde `/ajuda`. |
| `balance_command` | Consulta saldo. |
| `summary_command` | Consulta resumo mensal. |
| `reserves_command` | Consulta reservas. |
| `categories_command` | Lista categorias. |
| `statement_command` | Lista ultimas transacoes. |
| `planning_command` | Consulta planejamento. |
| `effect_command` | Simula efeito de despesa. |
| `reset_command` | Solicita reset administrativo. |
| `confirm_reset_command` | Confirma reset administrativo. |
| `chart_command` | Envia graficos. |
| `text_message_handler` | Processa mensagens livres. |

### Services

| Arquivo | Responsabilidade |
| --- | --- |
| `account_service.py` | Listar contas, buscar conta padrao e calcular saldo total. |
| `category_service.py` | Listar, buscar e validar categorias. |
| `transaction_service.py` | Criar receitas/despesas e listar transacoes. |
| `reserve_service.py` | Criar reservas e aportar valores. |
| `summary_service.py` | Calcular resumo mensal e dados do dashboard. |
| `budget_service.py` | Criar budgets e calcular progresso/alertas. |
| `plan_service.py` | Criar plano mensal, regras e progresso. |
| `chart_service.py` | Gerar graficos PNG em memoria. |
| `effect_service.py` | Simular impacto de despesa sem persistir. |
| `reset_service.py` | Resetar dados financeiros com seed e transacao atomica. |
| `atomic.py` | Helper para commit/rollback seguro. |

## Regras de seguranca e consistencia

- Operacoes que alteram saldo usam transacao atomica.
- Se uma escrita falhar, o rollback deve preservar o estado anterior.
- O bot verifica `chat_id` quando `DEFAULT_USER_TELEGRAM_CHAT_ID` esta configurado.
- `/reset` fica desativado por padrao.
- `/reset` exige confirmacao por codigo.
- Tokens e senhas nao devem ser colocados em commits.
- `backend/.env` e `frontend/.env.local` devem ficar locais.

## Testes

Rodar todos os testes:

```bash
cd backend
../.venv/bin/python -m pytest
```

Testes cobrem:

- Parser do Telegram
- Transacoes
- Reservas
- Resumos
- Planejamento
- Graficos
- Validacoes
- Simulacao `/efeito`
- Reset administrativo
- Formatos de resposta do bot

## Problemas comuns

### Backend nao responde

Verifique containers:

```bash
sudo docker compose ps
```

Veja logs:

```bash
sudo docker compose logs backend --tail=100
```

### Ngrok responde erro

Verifique se o backend esta no ar:

```bash
curl http://localhost:8000/health
```

Verifique a URL publica:

```bash
curl https://obsolete-glare-reckless.ngrok-free.dev/health
```

### Telegram nao recebe mensagens

Registre o webhook novamente:

```bash
curl -X POST http://localhost:8000/api/v1/telegram/setup
```

Confira:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_WEBHOOK_URL`
- `DEFAULT_USER_TELEGRAM_CHAT_ID`
- ngrok ativo

### `/reset` nao funciona

Confira no `backend/.env`:

```env
ENABLE_TELEGRAM_RESET=true
DEFAULT_USER_TELEGRAM_CHAT_ID=seu_chat_id
```

Depois reinicie:

```bash
sudo docker compose restart backend
```
