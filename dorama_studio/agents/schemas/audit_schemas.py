from typing import Any

from pydantic import BaseModel


class AuditInput(BaseModel):
    agents_dir: str


class AuditOutput(BaseModel):
    audit_results: dict[str, Any]
    status: str
