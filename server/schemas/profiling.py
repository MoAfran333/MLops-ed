from pydantic import BaseModel


class ProfileRequest(BaseModel):
    dataset_id: str
    target_column: str | None = None


class ProfileResponse(BaseModel):
    dataset_id: str
    profile_url: str
