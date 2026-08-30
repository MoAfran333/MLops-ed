from server.config import MODELS_DIR
from server.services.dataset_services import load_dataset
from src.meta_features import detect_problem_type
from src.model_tuner import ModelTuner


def optimize_model(
    dataset_id: str,
    target_column: str,
    model: str,
) -> dict:

    df = load_dataset(dataset_id)

    if target_column not in df.columns:
        raise ValueError(f"Target column '{target_column}' does not exist.")

    problem_type = detect_problem_type(
        df,
        target_column,
    )

    tuner = ModelTuner(MODELS_DIR)

    result = tuner.tune_and_build(
        df,
        target_column,
        problem_type,
        model,
    )

    if not result:
        raise RuntimeError("Optimization returned no results.")

    return {
        "status": "completed",
        "dataset_id": dataset_id,
        "target_column": target_column,
        "problem_type": problem_type,
        **result,
    }
