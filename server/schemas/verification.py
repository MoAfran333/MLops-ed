from pydantic import BaseModel


class VerifyRequest(BaseModel):
    dataset_id: str
    target_column: str
    model: str


class VerifyResponse(BaseModel):
    dataset: str
    model: str
    problem_type: str
    baseline_score: float | None
    small_train_score: float | None
    score_drop: float | None
    drop_percent: float | None
    robust: bool | None
