"""
AccessLens backend entrypoint.

Shared/frozen file — CORS setup and router registration live here. Do not
add feature logic to this file; each module's routes belong in
app/routers/.py.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import ALLOWED_ORIGINS
from app.models.schemas import HealthResponse

app = FastAPI(title="AccessLens API")

# Permissive for local dev; ALLOWED_ORIGINS should be locked down to the
# real Vercel domain via an env var once deployed.

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")

# Routers get registered here as each module's endpoints come online.

from app.routers import scan, enrich, report

app.include_router(scan.router, prefix="/api")
app.include_router(enrich.router, prefix="/api")
app.include_router(report.router, prefix="/api")