from typing import Any

from pydantic import BaseModel


class RecommendRequest(BaseModel):
    dataset_id: str
    target_column: str


class RecommendResponse(BaseModel):
    dataset_id: str
    target_column: str
    problem_type: str
    meta_features: dict[str, Any]
    recommended_model: str
