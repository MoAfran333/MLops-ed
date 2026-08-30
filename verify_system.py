import sys
import warnings
from pathlib import Path

import pandas as pd

from baselines import run_baselines
from compare_train_size import run_comparison
from meta_features import compute_meta_features, detect_problem_type
from meta_learner import MetaLearner
from profiling import generate_profile

warnings.filterwarnings("ignore")

sys.path.insert(0, str(Path(__file__).parent / "src"))
DATA_DIR = Path(__file__).parent / "data" / "raw"
RESULTS_DIR = Path(__file__).parent / "results"
MODELS_DIR = Path(__file__).parent / "models"


def main():
    print("\n" + "=" * 70)
    print("SYSTEM VERIFICATION")
    print("=" * 70)

    csv_files = sorted([f for f in DATA_DIR.glob("*.csv")])
    if not csv_files:
        print("No CSV files found.")
        return

    # 1. Run Pipeline on all datasets to generate data
    print("\n[Phase 1] Running Pipeline on all datasets...")

    # Define targets for known datasets (or guess/ask - hardcoding for verification)
    targets = {
        "adult.csv": "income",
        "Housing.csv": "price",
        "iot_energy_management_dataset.csv": "Optimization_Effective",
        "sensor_maintenance_data.csv": "Failure Type",
        "student_lifestyle_dataset.csv": "Stress_Level",
        "WineQT.csv": "quality",
    }

    # Clear old results for clean test
    meta_path = RESULTS_DIR / "meta_features.csv"
    baseline_path = RESULTS_DIR / "baseline_results.csv"
    if meta_path.exists():
        meta_path.unlink()
    if baseline_path.exists():
        baseline_path.unlink()

    # Create profiles dir
    (RESULTS_DIR / "profiles").mkdir(parents=True, exist_ok=True)

    for csv_file in csv_files:
        print(f"\nProcessing {csv_file.name}...")
        df = pd.read_csv(csv_file)

        # Heuristic to find target if not in dict
        if csv_file.name in targets:
            target_col = targets[csv_file.name]
        else:
            # Fallback: last column
            target_col = df.columns[-1]
            print(
                f"Warning: Target not specified for {csv_file.name}, using '{target_col}'"
            )

        if target_col not in df.columns:
            print(f"Skipping {csv_file.name}: Target '{target_col}' not found.")
            continue

        # Detect
        problem_type = detect_problem_type(df, target_col)
        print(f"  Type: {problem_type}")

        # Profile
        print("  Generating Profile...")
        generate_profile(df, csv_file.stem, RESULTS_DIR / "profiles")

        # Meta-features
        print("  Computing Meta-features...")
        meta = compute_meta_features(df, target_col)
        meta["dataset"] = csv_file.name
        meta["problem_type"] = problem_type

        # Save Meta
        meta_df = pd.DataFrame([meta])
        if meta_path.exists():
            meta_df.to_csv(meta_path, mode="a", header=False, index=False)
        else:
            meta_df.to_csv(meta_path, mode="w", header=True, index=False)

        # Baselines
        print("  Running Baselines...")
        baseline_results = run_baselines(df, csv_file.name, target_col, problem_type)

        # Save Baselines
        baseline_df = pd.DataFrame(baseline_results)
        if baseline_path.exists():
            baseline_df.to_csv(baseline_path, mode="a", header=False, index=False)
        else:
            baseline_df.to_csv(baseline_path, mode="w", header=True, index=False)

    # 2. Train Meta-Learner
    print("\n[Phase 2] Training Meta-Learner...")
    # We can call the main function of train script directly or logic
    # Calling logic is safer

    meta_df = pd.read_csv(meta_path)
    results_df = pd.read_csv(baseline_path)

    learner = MetaLearner()
    training_data = learner.prepare_training_data(meta_df, results_df)

    if not training_data.empty:
        learner.train(training_data)
        MODELS_DIR.mkdir(exist_ok=True)
        learner.save(MODELS_DIR / "meta_learner.pkl")
    else:
        print("Failed to prepare training data.")
        return

    # 3. Test Prediction & Verification
    print("\n[Phase 3] Testing Prediction & Verification on first dataset...")
    test_file = csv_files[0]
    target_col = targets.get(test_file.name, pd.read_csv(test_file).columns[-1])

    df = pd.read_csv(test_file)
    problem_type = detect_problem_type(df, target_col)
    meta = compute_meta_features(df, target_col)
    meta["problem_type"] = problem_type

    try:
        pred = learner.predict(meta)
        print(f"  Predicted Best Model: {pred}")

        print(f"  Running 15% vs 85% Verification for {pred}...")
        results = run_comparison(
            df, test_file.name, target_col, problem_type, specific_model=pred
        )
        print("  Verification successful!")
    except Exception as e:
        print(f"  Prediction/Verification failed: {e}")

    print("\nVERIFICATION COMPLETE")


if __name__ == "__main__":
    main()
