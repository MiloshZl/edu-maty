from typing import Any, Literal
from pydantic import BaseModel, Field, SecretStr

class LoginRequest(BaseModel):
    username: str = Field(default="", max_length=200)
    password: SecretStr = Field(default=SecretStr(""))
    school: Literal["spszl"] = "spszl"
    mode: Literal["live", "demo"] = "live"

class Result(BaseModel):
    status: Literal["ok", "partial", "unsupported", "error", "not_verified"]
    source: Literal["live", "demo"]
    period: dict[str, Any]
    data: Any = None
    lastSuccess: str | None = None
    lastAttempt: str | None = None
    stale: bool = False
    liveVerified: bool = False
    reason: str | None = None
    limitations: list[str] = Field(default_factory=list)
