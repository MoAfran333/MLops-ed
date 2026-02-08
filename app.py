import streamlit as st
import pandas as pd
from pathlib import Path
import sys
import shutil

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))
from meta_features import compute_meta_features, detect_problem_type
from profiling import generate_profile
from meta_learner import MetaLearner

from compare_train_size import run_comparison
from model_tuner import ModelTuner

# Directories
DATA_DIR = Path(__file__).parent / "data" / "raw"
RESULTS_DIR = Path(__file__).parent / "results"
MODELS_DIR = Path(__file__).parent / "models"
PROFILES_DIR = RESULTS_DIR / "profiles"

# Ensure dirs exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
PROFILES_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)

st.set_page_config(page_title="ML System Rebuild", layout="wide")

st.title("🤖 ML System: Auto-Analysis & Meta-Learning")

# Sidebar
st.sidebar.header("Data Input")
uploaded_file = st.sidebar.file_uploader("Upload CSV Dataset", type=["csv"])

if uploaded_file:
    # Save file
    file_path = DATA_DIR / uploaded_file.name
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.sidebar.success(f"File uploaded: {uploaded_file.name}")
    
    # Load DF
    df = pd.read_csv(file_path)
    
    st.subheader("1. Data Preview")
    st.dataframe(df.head())
    
    # Inputs
    target_col = st.sidebar.selectbox("Select Target Column", df.columns)
    
    # 4 Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Profiling", "🧠 Algorithm Prediction", "⚖️ 15% vs 85% Verification", "⚡ Optimization & Build"])
    
    # --- PROFILING ---
    with tab1:
        if st.button("Generate Profile"):
            with st.spinner("Generating Profile Report..."):
                profile_path = generate_profile(df, file_path.stem, PROFILES_DIR)
            st.success("Profile Generated!")
            
            # Display HTML
            with open(profile_path, "r", encoding="utf-8") as f:
                html_code = f.read()
            st.components.v1.html(html_code, height=800, scrolling=True)

    # --- PREDICTION ---
    with tab2:
        if st.button("Predict Best Model"):
            # 1. Detect Type
            problem_type = detect_problem_type(df, target_col)
            st.info(f"Detected Problem Type: **{problem_type}**")
            
            # 2. Compute Meta
            with st.spinner("Computing Meta-Features..."):
                meta = compute_meta_features(df, target_col)
                meta['problem_type'] = problem_type
                st.json(meta)
            
            # 3. Predict
            model_path = MODELS_DIR / "meta_learner.pkl"
            if model_path.exists():
                learner = MetaLearner.load(model_path)
                try:
                    prediction = learner.predict(meta)
                    st.success(f"### Recommended Model: {prediction}")
                    st.session_state['recommended_model'] = prediction
                except Exception as e:
                    st.error(f"Prediction failed: {e}")
            else:
                st.warning("Meta-Learner model not found. Please train it first.")

    # --- VERIFICATION ---
    with tab3:
        recommended_model = st.session_state.get('recommended_model', None)
        
        st.write("Compare performance of a model when trained on **15%** vs **85%** of the data.")
        
        model_to_test = st.selectbox("Select Model to Test", 
                                     ["LogisticRegression", "RandomForest", "LinearRegression", "DecisionTree", "GaussianNB"],
                                     index=1 if not recommended_model else ["LogisticRegression", "RandomForest", "LinearRegression", "DecisionTree", "GaussianNB"].index(recommended_model) if recommended_model in ["LogisticRegression", "RandomForest", "LinearRegression", "DecisionTree", "GaussianNB"] else 0)
        
        if st.button(f"Run Verification for {model_to_test}"):
            problem_type = detect_problem_type(df, target_col)
            with st.spinner("Running comparison..."):
                results = run_comparison(df, file_path.name, target_col, problem_type, specific_model=model_to_test)
            
            if results:
                res = results[0]
                col1, col2, col3 = st.columns(3)
                col1.metric("Baseline Score (85%)", f"{res['baseline_score']:.4f}")
                col2.metric("Small Train Score (15%)", f"{res['small_train_score']:.4f}")
                col3.metric("Performance Drop", f"{res['drop_percent']:.2f}%")
                
                if res['drop_percent'] < 5:
                    st.success("Model is **Robust** to data reduction.")
                else:
                    st.warning("Model is **Sensitive** to data reduction.")
            else:
                st.error("Verification failed.")

    # --- OPTIMIZATION ---
    with tab4:
        st.header("Hyperparameter Tuning & Ensembling")
        st.write("Optimize the model using **15% subsampling** and build the final `.pkl` for deployment.")
        
        recommended_model = st.session_state.get('recommended_model', None)
        
        if recommended_model:
            st.info(f"Recommended Model to Optimize: **{recommended_model}**")
            model_to_opt = recommended_model
        else:
            measure_models = ["RandomForest", "DecisionTree", "LogisticRegression", "LinearRegression", "GradientBoosting", "AdaBoost"]
            model_to_opt = st.selectbox("Select Model to Optimize", measure_models)
            
        if st.button(f"🚀 Optimize & Build {model_to_opt}"):
            problem_type = detect_problem_type(df, target_col)
            tuner = ModelTuner(MODELS_DIR)
            
            with st.spinner("Tuning hyperparameters (on 15% data) & evaluating ensembles..."):
                try:
                    result = tuner.tune_and_build(df, target_col, problem_type, model_to_opt)
                    
                    if result:
                        st.success("Optimization Complete!")
                        
                        st.write("### 🏆 Best Configuration")
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Optimized Variant", result['optimized_variant'])
                        c2.metric("Validation Score", f"{result['validation_score']:.4f}")
                        c3.metric("Model Type", result['model_type'])
                        
                        st.write("### ⚙️ Best Parameters")
                        st.json(result['best_params'])
                        
                        st.success(f"Final Model Saved: `{result['model_path']}`")
                        
                        with open(result['model_path'], "rb") as f:
                             st.download_button("Download Model .pkl", f, file_name="best_model.pkl")
                    else:
                        st.error("Optimization returned no results.")
                except Exception as e:
                    st.error(f"Optimization failed: {e}")


else:
    st.info("👈 Upload a CSV file to get started.")
