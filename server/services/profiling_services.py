from pathlib import Path

from server.config import PROFILES_DIR
from server.services.dataset_services import (
    get_dataset_path,
    load_dataset,
)
from src.profiling import generate_profile


def profile_dataset(
    dataset_id: str,
) -> dict:

    df = load_dataset(dataset_id)
    dataset_path = get_dataset_path(dataset_id)

    profile_path = generate_profile(
        df,
        dataset_path.stem,
        PROFILES_DIR,
    )

    return {
        "dataset_id": dataset_id,
        "profile_url": f"/api/profile/{profile_path.name}",
    }


def get_profile_path(filename: str) -> Path:
    safe_filename = Path(filename).name

    if safe_filename != filename:
        raise ValueError("Invalid profile filename.")

    if not safe_filename.endswith("_profile.html"):
        raise ValueError("Invalid profile file.")

    profile_path = PROFILES_DIR / safe_filename

    if not profile_path.exists():
        raise FileNotFoundError("Profile not found.")

    return profile_path
