from typing import Any

from pydantic import BaseModel


class OptimizeRequest(BaseModel):
    dataset_id: str
    target_column: str
    model: str


class OptimizeResponse(BaseModel):
    status: str
    dataset_id: str
    target_column: str
    model_type: str
    optimized_variant: str
    validation_score: float
    best_params: dict[str, Any]
    model_path: str
    download_url: str
