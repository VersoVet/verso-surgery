"""Verso Surgery — API de gestion des chirurgies vétérinaires."""

import asyncio
import logging
from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import onyx_sdk  # type: ignore[import-untyped]
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.modules.animals.routes import router as animals_router
from src.modules.dashboard.routes import router as dashboard_router
from src.modules.prescriptions.routes import router as prescriptions_router
from src.modules.protocols.routes import router as protocols_router
from src.modules.surgeries.routes import router as surgeries_router

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Flag pour tracer l'état
_service_ready = False


async def wait_for_dependency(
    name: str,
    check: Callable[[], Awaitable[bool]],
    *,
    retries: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
) -> bool:
    """Attend qu'une dépendance soit disponible.

    Args:
        name: Nom de la dépendance
        check: Fonction async qui retourne True/False
        retries: Nombre de tentatives
        base_delay: Délai initial en secondes
        max_delay: Délai max entre tentatives

    Returns:
        True si disponible, False sinon.
    """
    for attempt in range(retries):
        try:
            if await check():
                logger.info(f"✓ {name} ready")
                return True
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1}/{retries} for {name}: {e}")
        if attempt < retries - 1:
            delay = min(base_delay * (2**attempt), max_delay)
            await asyncio.sleep(delay)
    logger.error(f"✗ {name} failed after {retries} attempts")
    return False


async def check_protocols() -> bool:
    """Vérifie que les protocoles sont chargés.

    Returns:
        True si protocoles disponibles.
    """
    from src.modules.protocols.service import ProtocolService

    protocols = ProtocolService.load_protocols()
    return len(protocols) > 0


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    """Gère le démarrage et l'arrêt de l'application.

    Args:
        app: Instance FastAPI.

    Yields:
        Contrôle pendant l'exécution.
    """
    global _service_ready

    logger.info("Starting verso-surgery service...")

    # Signaler au dashboard que le service démarre
    if client:
        try:
            await client.start()
        except Exception as e:
            logger.warning(f"OnyxClient start failed: {e}")

    # Attendre les dépendances
    if not await wait_for_dependency("protocols", check_protocols):
        logger.error("Failed to load protocols")
        _service_ready = False
    else:
        _service_ready = True
        logger.info("✓ verso-surgery service started successfully")

        # Signaler que le service est opérationnel
        if client:
            try:
                await client.set_status("WORKING")
            except Exception as e:
                logger.warning(f"OnyxClient set_status failed: {e}")

    yield

    logger.info("Shutting down verso-surgery service...")

    # Signaler au dashboard que le service s'arrête
    if client:
        try:
            await client.stop()
        except Exception as e:
            logger.warning(f"OnyxClient stop failed: {e}")

    _service_ready = False


# Créer l'app FastAPI
app = FastAPI(
    title="Verso Surgery",
    description="Gestion des chirurgies vétérinaires — calcul doses anesthésiques",
    version="0.1.9",
    lifespan=lifespan,
)

# Initialiser OnyxClient pour la visibilité sur le dashboard
client: onyx_sdk.OnyxClient | None = None

try:
    client = onyx_sdk.OnyxClient(skill_name="verso-surgery")
except Exception as e:
    logger.warning(f"OnyxClient initialization failed: {e}")
    client = None

# Inclure les routers
app.include_router(protocols_router)
app.include_router(animals_router)
app.include_router(surgeries_router)
app.include_router(prescriptions_router)
app.include_router(dashboard_router)

# Monter les fichiers statiques
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/dashboard")
async def dashboard_page() -> FileResponse:
    """Retourne la page du dashboard.

    Returns:
        Page HTML du dashboard.
    """
    dashboard_file = Path(__file__).parent.parent / "static" / "index.html"
    return FileResponse(dashboard_file)


@app.get("/health")
async def health() -> dict[str, Any]:
    """Health check endpoint.

    Returns:
        Status de santé du service.
    """
    return {
        "status": "healthy" if _service_ready else "degraded",
        "service": "verso-surgery",
        "version": "0.1.21",
    }


@app.get("/ready")
async def ready() -> dict[str, Any]:
    """Readiness check endpoint.

    Returns:
        Ready status.
    """
    return {
        "ready": _service_ready,
        "service": "verso-surgery",
    }


@app.get("/")
async def root() -> dict[str, Any]:
    """Root endpoint.

    Returns:
        Informations de base sur le service.
    """
    return {
        "service": "verso-surgery",
        "description": "Gestion des chirurgies vétérinaires",
        "endpoints": {
            "health": "/health",
            "ready": "/ready",
            "protocols": "/api/protocols",
            "animals": "/api/animals",
            "surgeries": "/api/surgeries",
            "prescriptions": "/api/prescriptions",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8112,
        reload=False,
        log_level="info",
    )
