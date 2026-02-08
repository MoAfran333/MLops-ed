import warnings
warnings.filterwarnings('ignore')

import sys
from pathlib import Path
import pandas as pd
import os

sys.path.insert(0, str(Path(__file__).parent / "src"))
from meta_features import compute_meta_features, detect_problem_type
from baselines import run_baselines
from profiling import generate_profile

DATA_DIR = Path(__file__).parent / "data" / "raw"
RESULTS_DIR = Path(__file__).parent / "results"

def main():
    print("\n" + "="*70)
    print("DATASET PIPELINE")
    print("="*70)
    
    csv_files = sorted([f for f in DATA_DIR.glob("*.csv")])
    
    if not csv_files:
        print(f"No CSV files found in {DATA_DIR}")
        return
    
    print(f"\nAvailable datasets:")
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
            print("Invalid input. Enter a number.")
    
    target_col = input(f"Enter target column name for {dataset_file.name}: ").strip()
    
    print(f"\n{'='*70}")
    print(f"Processing: {dataset_file.name} (target: {target_col})")
    print("="*70)
    
    df = pd.read_csv(dataset_file)
    print(f"Loaded: {df.shape[0]} rows, {df.shape[1]} columns")

    # Detect problem type
    problem_type = detect_problem_type(df, target_col)
    print(f"Detected Problem Type: {problem_type}")
    
    # Generate Profile
    print(f"\n[1/3] Generating Pandas Profile...")
    profile_path = generate_profile(df, dataset_file.stem, RESULTS_DIR / "profiles")
    print(f"Profile saved to: {profile_path}")

    print(f"\n[2/3] Computing meta-features...")
    meta = compute_meta_features(df, target_col=target_col)
    meta["dataset"] = dataset_file.name
    meta["problem_type"] = problem_type
    
    print(f"\nMeta-features:")
    for key, val in sorted(meta.items()):
        if key != "dataset":
            if isinstance(val, float):
                print(f"  {key:30} {val:.6f}")
            else:
                print(f"  {key:30} {val}")
    
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    meta_df = pd.DataFrame([meta])
    meta_path = RESULTS_DIR / "meta_features.csv"
    
    # Append if exists, otherwise write new
    if meta_path.exists():
        meta_df.to_csv(meta_path, mode='a', header=False, index=False)
    else:
        meta_df.to_csv(meta_path, mode='w', header=True, index=False)
        
    print(f"\nSaved to: {meta_path}")
    
    print(f"\n[3/3] Running baseline models...")
    baseline_results = run_baselines(df, dataset_file.name, target_col, problem_type)
    
    baseline_df = pd.DataFrame(baseline_results)
    baseline_path = RESULTS_DIR / "baseline_results.csv"
    
    # Append if exists, otherwise write new
    if baseline_path.exists():
        baseline_df.to_csv(baseline_path, mode='a', header=False, index=False)
    else:
        baseline_df.to_csv(baseline_path, mode='w', header=True, index=False)
    
    print(f"\nBaseline results:")
    print(baseline_df.to_string(index=False))
    print(f"\nSaved to: {baseline_path}")
    
    print(f"\n{'='*70}")
    print("✓ Pipeline complete")
    print("="*70)

if __name__ == "__main__":
    main()
