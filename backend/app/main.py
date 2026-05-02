from fastapi import FastAPI


app = FastAPI(
    title="FinTrack API",
    version="0.1.0",
    description="Sistema de gestao financeira pessoal.",
)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
