import pandas as pd
import numpy as np
import pickle
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

class MetaLearner:
    def __init__(self):
        self.clf = RandomForestClassifier(n_estimators=100, random_state=42)
        self.le_model_name = LabelEncoder()
        self.feature_cols = [
            "n_samples", "n_features", "missing_ratio", "avg_variance", 
            "avg_abs_correlation", "class_entropy", "imbalance_ratio"
        ]
        self.is_fitted = False

    def prepare_training_data(self, meta_df: pd.DataFrame, results_df: pd.DataFrame, problem_type: str = None):
        """
        Merges meta-features and baseline results to create a training set.
        Finds the 'best' model for each dataset.
        """
        # Merge on dataset name
        merged = pd.merge(meta_df, results_df, on="dataset")
        
        # Filter by problem type if specified
        if problem_type:
            # Assuming 'problem_type' column might exist in results or we infer it
            # For now, relying on the 'problem_type_x' or 'problem_type_y' if they exist, 
            # or just 'problem_type' if we successfully saved it.
            # In run_pipeline, we save 'problem_type' in meta_features.csv (let's verify)
            # Yes, meta["problem_type"] = problem_type
            if 'problem_type_x' in merged.columns:
                 merged = merged[merged['problem_type_x'] == problem_type]
            elif 'problem_type' in merged.columns:
                 merged = merged[merged['problem_type'] == problem_type]

        # Determine best model per dataset
        # Strategy: 
        # For Classification: Max Accuracy
        # For Regression: Min RMSE (or Max R2 if we had it, but we saved RMSE)
        
        best_models = []
        
        grouped = merged.groupby("dataset")
        for dataset, group in grouped:
            # Check if Classification or Regression based on the group's data
            # We can check the columns available or the problem_type column
            
            # Simple heuristic: look at score_name
            # If accuracy is available, maximize it.
            if "score_name" in group.columns and "Accuracy" in group["score_name"].values:
                 best_row = group.loc[group["mean_score"].idxmax()]
            elif "score_name" in group.columns and "RMSE" in group["score_name"].values:
                 best_row = group.loc[group["mean_score"].idxmin()] # Lower RMSE is better
            elif "mean_acc" in group.columns: # Legacy support for Classification only
                 best_row = group.loc[group["mean_acc"].idxmax()]
            else:
                 continue # Cannot determine metric
            
            best_models.append({
                "dataset": dataset,
                "best_model": best_row["model"],
                **{col: best_row[col] for col in self.feature_cols if col in best_row}
            })
            
        return pd.DataFrame(best_models)

    def train(self, training_data: pd.DataFrame):
        """
        Trains the meta-learner to predict 'best_model' from meta-features.
        """
        if training_data.empty:
            print("No training data available for MetaLearner.")
            return

        X = training_data[self.feature_cols].fillna(0) # Handle missing meta-features
        y = training_data["best_model"]
        
        y_encoded = self.le_model_name.fit_transform(y)
        self.clf.fit(X, y_encoded)
        self.is_fitted = True
        print(f"MetaLearner trained on {len(training_data)} datasets.")
        print(f"Classes: {list(self.le_model_name.classes_)}")

    def predict(self, meta_features: dict) -> str:
        """
        Predicts the best model for a single dataset.
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted yet.")
            
        # Convert dict to DataFrame
        X = pd.DataFrame([meta_features])
        
        # Ensure all columns exist
        for col in self.feature_cols:
            if col not in X.columns:
                X[col] = 0.0 # or appropriate default
                
        X = X[self.feature_cols].fillna(0)
        
        pred_idx = self.clf.predict(X)[0]
        model_name = self.le_model_name.inverse_transform([pred_idx])[0]
        return model_name

    def save(self, path: Path):
        with open(path, 'wb') as f:
            pickle.dump(self, f)
        print(f"MetaLearner saved to {path}")

    @staticmethod
    def load(path: Path) -> 'MetaLearner':
        with open(path, 'rb') as f:
            return pickle.load(f)
