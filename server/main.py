from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.routes import (
    datasets,
    models,
    optimization,
    profiling,
    recommendation,
    verification,
)

app = FastAPI(
    title="ML System API",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


app.include_router(datasets.router)
app.include_router(recommendation.router)
app.include_router(profiling.router)
app.include_router(verification.router)
app.include_router(optimization.router)
app.include_router(models.router)
