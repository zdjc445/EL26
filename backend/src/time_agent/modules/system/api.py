from fastapi import APIRouter, Request

from time_agent import __version__
from time_agent.modules.system.schemas import LiveStatus

router = APIRouter(prefix="/health", tags=["system"])


@router.get("/live", response_model=LiveStatus, operation_id="getLiveStatus")
def get_live_status(request: Request) -> LiveStatus:
    return LiveStatus(
        status="ok",
        service="time-api",
        version=__version__,
        build_sha=request.app.state.settings.build_sha,
    )
