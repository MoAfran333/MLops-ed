import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / "src"))
from meta_learner import MetaLearner

RESULTS_DIR = Path(__file__).parent / "results"
MODELS_DIR = Path(__file__).parent / "models"

def main():
    print("\n" + "="*70)
    print("TRAIN META-LEARNER")
    print("="*70)
    
    meta_path = RESULTS_DIR / "meta_features.csv"
    results_path = RESULTS_DIR / "baseline_results.csv"
    
    if not meta_path.exists() or not results_path.exists():
        print("Error: Results files not found. Run 'run_pipeline.py' on some datasets first.")
        return
        
    print("Loading data...")
    meta_df = pd.read_csv(meta_path)
    results_df = pd.read_csv(results_path)
    
    learner = MetaLearner()
    
    print("Preparing training data...")
    # We train generic meta-learner (spanning both prob types if possible, or we could separate them)
    # For now, let's try to train one model that predicts the best algorithm name.
    # Algorithms like RandomForest exist in both, but are different classes. 
    # The label encoder in MetaLearner will treat "RandomForest" as one class if the string is same.
    # In baselines.py, I used "RandomForest" for both. This is actually good! 
    # The meta-learner will suggest "Use RandomForest", and the system knows which RF to use based on prob type.
    
    training_data = learner.prepare_training_data(meta_df, results_df)
    
    if training_data.empty:
        print("No valid training data could be prepared.")
        return
        
    print(f"Training on {len(training_data)} examples...")
    # The prepare_training_data returns a DataFrame with 'best_model' and meta-features
    
    # We need to extract the features and target to print/debug if needed, 
    # but learner.train takes the DataFrame directly as per my design.
    learner.train(training_data)
    
    MODELS_DIR.mkdir(exist_ok=True)
    model_path = MODELS_DIR / "meta_learner.pkl"
    learner.save(model_path)
    
    print("\nTraining complete!")

if __name__ == "__main__":
    main()
