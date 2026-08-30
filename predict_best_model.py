import sys
import warnings
from pathlib import Path

import pandas as pd

from compare_train_size import run_comparison
from src.meta_features import compute_meta_features, detect_problem_type
from src.meta_learner import MetaLearner
from src.model_tuner import ModelTuner
from src.profiling import generate_profile

warnings.filterwarnings("ignore")

sys.path.insert(0, str(Path(__file__).parent / "src"))

DATA_DIR = Path(__file__).parent / "data" / "raw"
RESULTS_DIR = Path(__file__).parent / "results"
MODELS_DIR = Path(__file__).parent / "models"
TEST_RESULTS_DIR = Path(__file__).parent / "results" / "test_results"


def main():
    print("\n" + "=" * 70)
    print("PREDICT BEST MODEL & CONFIGURATION")
    print("=" * 70)

    model_path = MODELS_DIR / "meta_learner.pkl"
    if not model_path.exists():
        print("Error: Meta-learner model not found. Run 'train_meta_model.py' first.")
        # Optional: Ask to run training?
        # For now, just return
        return

    learner = MetaLearner.load(model_path)
    print("Meta-learner loaded.")

    # --- Input Selection ---
    csv_files = sorted([f for f in DATA_DIR.glob("*.csv")])
    if not csv_files:
        print(f"No CSV files found in {DATA_DIR}")
        return

    print("\nAvailable datasets:")
    for i, f in enumerate(csv_files, 1):
        print(f"  {i}. {f.name}")

    while True:
        try:
            choice = int(input("\nSelect dataset number: ").strip())
            if 1 <= choice <= len(csv_files):
                dataset_file = csv_files[choice - 1]
                break
            else:
                print(f"Please enter a number between 1 and {len(csv_files)}")
        except ValueError:
            print("Invalid input")

    target_col = input(f"Enter target column name for {dataset_file.name}: ").strip()

    # --- Processing ---
    print(f"\nProcessing {dataset_file.name}...")
    df = pd.read_csv(dataset_file)

    # 1. Detect Type
    problem_type = detect_problem_type(df, target_col)
    print(f"Problem Type: {problem_type}")

    # 2. Compute Meta-Features
    meta = compute_meta_features(df, target_col)
    meta["problem_type"] = problem_type

    # 3. Generate Profile
    print("Generating profile...")
    generate_profile(df, dataset_file.stem, RESULTS_DIR / "profiles")

    # 4. Predict Best Model
    print("\nPredicting best model...")
    try:
        recommended_model = learner.predict(meta)
        print(f"\n>>> RECOMMENDATION: {recommended_model} <<<")
    except Exception as e:
        print(f"Prediction failed: {e}")
        recommended_model = None

    # 5. Verification
    if recommended_model:
        run_verify = (
            input(
                f"\nCompare {recommended_model} performance on 15% vs 85% split? (y/n): "
            )
            .lower()
            .strip()
        )
        if run_verify == "y":
            print(f"\nRunning 15% vs 85% split test for {recommended_model}...")
            results = run_comparison(
                df,
                dataset_file.name,
                target_col,
                problem_type,
                specific_model=recommended_model,
            )

            # Print specific result
            if results:
                row = results[0]
                print(f"\nResults for {row['model']}:")
                print(f"  Baseline (85% train): {row['baseline_score']:.4f}")
                print(f"  Test (15% train):     {row['small_train_score']:.4f}")
                print(f"  Drop:                 {row['drop_percent']:.2f}%")

    # 6. Hyperparameter Tuning & Build
    if recommended_model:
        run_tune = (
            input(
                f"\n[Optimiztion] Tune & Build optimized {recommended_model} model? (y/n): "
            )
            .lower()
            .strip()
        )
        if run_tune == "y":
            tuner = ModelTuner(MODELS_DIR)
            result = tuner.tune_and_build(
                df, target_col, problem_type, recommended_model
            )

            if result:
                print(f"\n[Build] SUCCESS! Model saved to {result['model_path']}")
                print(f"       Variant: {result['optimized_variant']}")
                print(f"       Validation Score: {result['validation_score']:.4f}")
                print(f"       Best Params: {result['best_params']}")


if __name__ == "__main__":
    main()
