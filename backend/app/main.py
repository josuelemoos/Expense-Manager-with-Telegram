from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import accounts, budgets, categories, charts, plan, reserves, summary, telegram, transactions


app = FastAPI(
    title="FinTrack API",
    version="0.1.0",
    description="Sistema de gestao financeira pessoal.",
)

API_PREFIX = "/api/v1"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(accounts.router, prefix=API_PREFIX)
app.include_router(categories.router, prefix=API_PREFIX)
app.include_router(transactions.router, prefix=API_PREFIX)
app.include_router(reserves.router, prefix=API_PREFIX)
app.include_router(summary.router, prefix=API_PREFIX)
app.include_router(telegram.router, prefix=API_PREFIX)
app.include_router(budgets.router, prefix=API_PREFIX)
app.include_router(plan.router, prefix=API_PREFIX)
app.include_router(charts.router, prefix=API_PREFIX)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
