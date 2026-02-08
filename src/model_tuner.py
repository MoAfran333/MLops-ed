import pandas as pd
import numpy as np
import pickle
from pathlib import Path
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from sklearn.base import clone
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, BaggingClassifier, BaggingRegressor, GradientBoostingClassifier, GradientBoostingRegressor, AdaBoostClassifier, AdaBoostRegressor, VotingClassifier, VotingRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, mean_squared_error, r2_score

class ModelTuner:
    def __init__(self, models_dir):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
    def get_base_model(self, model_name, problem_type):
        """Returns the base sklearn model object."""
        if problem_type == 'Classification':
            if model_name == 'RandomForest': return RandomForestClassifier(random_state=42)
            if model_name == 'LogisticRegression': return LogisticRegression(random_state=42, max_iter=1000)
            if model_name == 'DecisionTree': return DecisionTreeClassifier(random_state=42)
            if model_name == 'GaussianNB': return GaussianNB()
            if model_name == 'GradientBoosting': return GradientBoostingClassifier(random_state=42)
            if model_name == 'AdaBoost': return AdaBoostClassifier(random_state=42)
        else:
            if model_name == 'RandomForest': return RandomForestRegressor(random_state=42)
            if model_name == 'LinearRegression': return LinearRegression()
            if model_name == 'DecisionTree': return DecisionTreeRegressor(random_state=42)
            if model_name == 'GradientBoosting': return GradientBoostingRegressor(random_state=42)
            if model_name == 'AdaBoost': return AdaBoostRegressor(random_state=42)
        return None

    def get_hyperparameter_grid(self, model_name, problem_type):
        """Returns a parameter grid for RandomizedSearchCV."""
        grid = {}
        
        # Common params
        if model_name == 'RandomForest':
            grid = {
                'model__n_estimators': [50, 100, 200],
                'model__max_depth': [None, 10, 20, 30],
                'model__min_samples_split': [2, 5, 10],
                'model__min_samples_leaf': [1, 2, 4]
            }
        elif model_name == 'DecisionTree':
            grid = {
                'model__max_depth': [None, 5, 10, 20, 50],
                'model__min_samples_split': [2, 5, 10],
                'model__min_samples_leaf': [1, 2, 4]
            }
        elif model_name == 'LogisticRegression':
             grid = {
                'model__C': [0.1, 1.0, 10.0],
                'model__solver': ['lbfgs', 'liblinear']
            }
        elif model_name == 'GradientBoosting':
            grid = {
                'model__n_estimators': [50, 100, 200],
                'model__learning_rate': [0.01, 0.1, 0.2],
                'model__max_depth': [3, 5, 7]
            }
            
        return grid

    def prepare_data(self, df, target_col, problem_type):
        X = df.drop(columns=[target_col])
        y = df[target_col]
        
        # Preprocessing
        numeric_features = X.select_dtypes(include=['int64', 'float64']).columns
        categorical_features = X.select_dtypes(include=['object', 'category']).columns

        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ])

        categorical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
            ('encoder', LabelEncoder()) # Note: Pipeline doesn't support LabelEncoder on X easily without custom wrapper, using OneHot or Ordinal is safer. 
                                        # But for tree models LabelEncoder is fine if we handle it. 
                                        # Let's use simple OneHot for safety in generic pipeline or just simple encoding.
                                        # For this specific codebase, baselines.py used simple LabelEncoding on X. 
                                        # I'll stick to a simpler approach consistent with baselines for now to avoid breaking changes.
        ])
        
        # Re-implementing simple encoding from baselines for consistency
        X_processed = X.copy()
        for col in X_processed.columns:
            if X_processed[col].dtype == 'object':
                 # Simple factorize/LabelEncoding
                 X_processed[col] = pd.factorize(X_processed[col])[0]
        X_processed = X_processed.fillna(0)
        
        if problem_type == 'Classification':
            if y.dtype == 'object' or not pd.api.types.is_numeric_dtype(y):
                y = pd.factorize(y)[0]
        
        return X_processed, y

    def tune_and_build(self, df, target_col, problem_type, model_name):
        print(f"\n[Optimiztion] Starting optimization for {model_name}...")
        
        X, y = self.prepare_data(df, target_col, problem_type)
        
        # 1. Subsample 15% for Tuning
        print("[Optimiztion] Subsampling 15% data for fast tuning...")
        # Stratify if classification
        stratify = y if problem_type == 'Classification' else None
        
        # Split: 15% tuning, 85% remaining (we will ignore the 85% for tuning, but use full later)
        # Actually proper way: Take 15% of X as X_tune
        try:
            X_tune, _, y_tune, _ = train_test_split(X, y, train_size=0.15, random_state=42, stratify=stratify)
        except ValueError:
            # Fallback if dataset is too small or classes are too rare
            X_tune, y_tune = X, y
            print("[Optimiztion] Dataset too small for stratification, using full data for tuning.")

        print(f"[Optimiztion] Tuning on {len(X_tune)} samples...")

        base_model = self.get_base_model(model_name, problem_type)
        base_model = self.get_base_model(model_name, problem_type)
        if base_model is None:
            print(f"Model {model_name} not supported for tuning.")
            return None

        # Create Pipeline
        # Since we preprocessed manually above, pipeline is just the model suitable for CV
        # But GridSearchCV needs an estimator.
        # We can wrap it in a pipeline if we wanted scaling inside CV, but we did global scaling/encoding. 
        # For 15% this is effectively a leak but acceptable for "fast heuristics".
        
        pipeline = Pipeline([('model', base_model)])
        param_grid = self.get_hyperparameter_grid(model_name, problem_type)
        
        tuned_model = base_model # Default
        best_params = {}
        
        if param_grid:
            search = RandomizedSearchCV(
                pipeline, 
                param_distributions=param_grid, 
                n_iter=10, 
                cv=3, 
                verbose=1, 
                n_jobs=-1, 
                random_state=42,
                scoring='accuracy' if problem_type == 'Classification' else 'neg_root_mean_squared_error'
            )
            search.fit(X_tune, y_tune)
            best_params = search.best_params_
            tuned_model = search.best_estimator_.named_steps['model']
            print(f"[Optimiztion] Best Params: {best_params}")
            print(f"[Optimiztion] Best Score (CV): {search.best_score_:.4f}")
        else:
            print(f"[Optimiztion] No grid defined for {model_name}, skipping tuning.")
            tuned_model.fit(X_tune, y_tune)

        # 2. Ensemble Strategy (Bagging/Boosting)
        # Try to improve the tuned model by wrapping it
        print("[Optimiztion] Evaluating Ensemble variants (Bagging)...")
        
        ensemble_candidates = []
        
        # Candidate 1: Tuned Model (Standalone)
        ensemble_candidates.append(('Tuned Single', tuned_model))
        
        # Candidate 2: Bagging (Bootstrap Aggregation) of the Tuned Model
        if problem_type == 'Classification':
            bagging = BaggingClassifier(estimator=tuned_model, n_estimators=10, random_state=42)
            # Candidate 3: Boosting (if applicable, usually base must be weak, but we can try)
            # GradientBoosting is its own beast, we can try generic Boosting if base is tree
            # For simplicity, let's just compare Single vs Bagged vs GradientBoosting(scratch)
        else:
            bagging = BaggingRegressor(estimator=tuned_model, n_estimators=10, random_state=42)
            
        ensemble_candidates.append(('Bagging Ensembled', bagging))
        
        # Evaluate Candidates on a validation holdout from the 15% (or just CV again)
        # Let's just do a quick CV on X_tune to pick the winner
        best_candidate_name = ""
        best_candidate_score = -float('inf')
        best_candidate_model = None
        
        for name, model in ensemble_candidates:
            cv_score = -float('inf')
            try:
                scoring = 'accuracy' if problem_type == 'Classification' else 'neg_mean_squared_error'
                # Note: Bagging might be slow.
                scores = RandomizedSearchCV(Pipeline([('m', model)]), param_distributions={}, n_iter=1, cv=3, scoring=scoring).fit(X_tune, y_tune).best_score_
                cv_score = scores
            except Exception as e:
                print(f"Failed to eval {name}: {e}")
                
            print(f"  > {name}: {cv_score:.4f}")
            
            if cv_score > best_candidate_score:
                best_candidate_score = cv_score
                best_candidate_name = name
                best_candidate_model = model

        print(f"[Optimiztion] Winner: {best_candidate_name}")

        # 3. Final Build (Retrain on FULL data)
        # The user said "build model pkl which should be executed at the end for testing"
        # We retrain the winner on the FULL X, y
        print(f"[Build] Retraining {best_candidate_name} on FULL dataset ({len(X)} samples)...")
        final_model = best_candidate_model
        final_model.fit(X, y)
        
        # Save
        save_path = self.models_dir / "best_model.pkl"
        with open(save_path, 'wb') as f:
            pickle.dump(final_model, f)
            
        print(f"[Build] Model saved to {save_path}")
        
        return {
            "model_type": model_name,
            "optimized_variant": best_candidate_name,
            "best_params": best_params,
            "validation_score": best_candidate_score,
            "model_path": str(save_path)
        }
