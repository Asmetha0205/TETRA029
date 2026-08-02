"""
Job Definitions & Status Models for the Refresh Scheduler.
"""

import datetime
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class RefreshStatus(str, Enum):
    """Execution status of a refresh job."""
    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class RefreshJobConfig(BaseModel):
    """Configuration settings for a refresh job run."""
    source_name: str = Field(default="scheduled_refresh", description="Identifier source tag.")
    auto_snapshot: bool = Field(default=True, description="Take automatic snapshot after refresh.")
    dry_run: bool = Field(default=False, description="Dry-run mode without mutating persistence.")
    interval_hours: float = Field(default=24.0, ge=0.1, description="Interval for recurring scheduler.")


class RefreshJobState(BaseModel):
    """Current status and history of the refresh manager."""
    status: RefreshStatus = Field(default=RefreshStatus.IDLE)
    last_run_time: Optional[str] = Field(default=None)
    next_run_time: Optional[str] = Field(default=None)
    last_run_summary: Optional[Dict[str, Any]] = Field(default=None)
    total_runs: int = Field(default=0, ge=0)
    failed_runs: int = Field(default=0, ge=0)
