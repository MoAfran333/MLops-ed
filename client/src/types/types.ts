export type ProblemType = "classification" | "regression" | string;

export interface HealthResponse {
    status: string;
}

export interface DatasetInfo {
    dataset_id: string;
    filename: string;
    rows: number;
    columns: number;
    column_names: string[];
    preview: Record<string, string | number | null>[];
}

export interface ProfileRequest {
    dataset_id: string;
}

export interface ProfileResponse {
    filename?: string;
    profile_path?: string;
    profile_url?: string;
    [key: string]: unknown;
}

export interface MetaFeatures {
    n_samples?: number;
    n_features?: number;
    missing_ratio?: number;
    avg_variance?: number;
    avg_abs_correlation?: number;
    class_entropy?: number;
    imbalance_ratio?: number;
    [key: string]: unknown;
}

export interface RecommendationRequest {
    dataset_id: string;
    target_column: string;
}

export interface RecommendationResponse {
    dataset_id?: string;
    target_column?: string;
    problem_type?: ProblemType;
    meta_features?: MetaFeatures;
    recommended_model?: string;
    [key: string]: unknown;
}

export interface VerificationRequest {
    dataset_id: string;
    target_column: string;
    model: string;
}

export interface VerificationResponse {
    dataset?: string;
    model?: string;
    baseline_score?: number;
    small_train_score?: number;
    score_drop?: number;
    drop_percent?: number;
    [key: string]: unknown;
}

export interface OptimizationRequest {
    dataset_id: string;
    target_column: string;
    model: string;
}

export interface OptimizationResponse {
    model_type?: string;
    optimized_variant?: string;
    validation_score?: number;
    best_params?: Record<string, unknown>;
    model_path?: string;
    download_url?: string;
    [key: string]: unknown;
}

export interface ApiError {
    message: string;
    status?: number;
    detail?: string;
}
