from server.config import META_LEARNER_PATH
from server.services.dataset_services import load_dataset
from src.meta_features import (
    compute_meta_features,
    detect_problem_type,
)
from src.meta_learner import MetaLearner


def recommend_model(
    dataset_id: str,
    target_column: str,
) -> dict:

    df = load_dataset(dataset_id)

    if target_column not in df.columns:
        raise ValueError(f"Target column '{target_column}' does not exist.")

    problem_type = detect_problem_type(
        df,
        target_column,
    )

    meta_features = compute_meta_features(
        df,
        target_column,
    )

    meta_features["problem_type"] = problem_type

    if not META_LEARNER_PATH.exists():
        raise FileNotFoundError("Meta-learner model not found.")

    learner = MetaLearner.load(META_LEARNER_PATH)

    recommended_model = learner.predict(meta_features)

    return {
        "dataset_id": dataset_id,
        "target_column": target_column,
        "problem_type": problem_type,
        "meta_features": meta_features,
        "recommended_model": recommended_model,
    }
