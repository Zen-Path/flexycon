from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class OperationStyle(BaseModel):
    short_name: str
    color: str


class RcloneStats(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    bytes: int
    checks: int
    deleted_dirs: int = Field(alias="deletedDirs")
    deletes: int
    elapsed_time: float = Field(alias="elapsedTime")
    errors: int
    eta: float | None = None
    fatal_error: bool = Field(alias="fatalError")
    listed: int
    renames: int
    retry_error: bool = Field(alias="retryError")

    server_side_copies: int = Field(alias="serverSideCopies")
    server_side_copy_bytes: int = Field(alias="serverSideCopyBytes")
    server_side_move_bytes: int = Field(alias="serverSideMoveBytes")
    server_side_moves: int = Field(alias="serverSideMoves")

    speed: float = 0.0

    total_bytes: int = Field(alias="totalBytes")
    total_checks: int = Field(alias="totalChecks")
    total_transfers: int = Field(alias="totalTransfers")

    transfer_time: float = Field(alias="transferTime", default=0.0)
    transfers: int


class RcloneOperation(BaseModel):
    time: str  # "2026-05-12T19:35:05.361378+03:00"
    level: Literal["notice", "info", "error", "debug"]  # TODO: check
    message: str = Field(alias="msg")
    file_type: Literal[
        "string",
        "*local.Object",
        "*local.Directory",
        "*drive.Object",
        "*drive.Directory",
        "*drive.documentObject",
    ] = Field(alias="objectType")
    raw_type: str = Field(alias="skipped")
    raw_file: str = Field(alias="object")
    size: int = Field(default=0)
    source: str


class ProcessedOperation(BaseModel):
    """Internal model for the transformed data pipeline"""

    display_type: str
    display_file: str
    size: int
    color: str
    destination: str | None = None
