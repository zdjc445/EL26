from fastapi import FastAPI

from time_agent import __version__
from time_agent.config import Settings
from time_agent.modules.system.api import router as system_router


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or Settings()
    app = FastAPI(title="Time API", version=__version__)
    app.state.settings = resolved_settings
    app.include_router(system_router, prefix="/api/v1")
    return app
