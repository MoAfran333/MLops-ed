from pathlib import Path

from server.config import BEST_MODEL_PATH


def get_best_model_path() -> Path:

    if not BEST_MODEL_PATH.exists():
        raise FileNotFoundError("Best model has not been built yet.")

    return BEST_MODEL_PATH
