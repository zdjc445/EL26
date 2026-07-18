from typing import Literal

from pydantic import BaseModel, ConfigDict


class LiveStatus(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["ok"]
    service: Literal["time-api"]
    version: str
    build_sha: str
