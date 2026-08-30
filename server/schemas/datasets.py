from typing import Any

from pydantic import BaseModel


class DatasetUploadResponse(BaseModel):
    dataset_id: str
    filename: str
    rows: int
    columns: int
    column_names: list[str]


class DatasetInfoResponse(BaseModel):
    dataset_id: str
    filename: str
    rows: int
    columns: int
    column_names: list[str]
    preview: list[dict[str, Any]]
