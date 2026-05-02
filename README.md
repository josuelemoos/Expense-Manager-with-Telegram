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
