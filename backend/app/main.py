from fastapi import FastAPI

from app.routers import accounts, categories, reserves, summary, telegram, transactions


app = FastAPI(
    title="FinTrack API",
    version="0.1.0",
    description="Sistema de gestao financeira pessoal.",
)

API_PREFIX = "/api/v1"

app.include_router(accounts.router, prefix=API_PREFIX)
app.include_router(categories.router, prefix=API_PREFIX)
app.include_router(transactions.router, prefix=API_PREFIX)
app.include_router(reserves.router, prefix=API_PREFIX)
app.include_router(summary.router, prefix=API_PREFIX)
app.include_router(telegram.router, prefix=API_PREFIX)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
