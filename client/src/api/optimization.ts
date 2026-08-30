import { apiPostJson, buildApiUrl } from "./client";
import type {
    OptimizationRequest,
    OptimizationResponse,
} from "@/src/types/types";

export function runOptimization(
    datasetId: string,
    targetColumn: string,
    model: string,
) {
    const body: OptimizationRequest = {
        dataset_id: datasetId,
        target_column: targetColumn,
        model,
    };
    return apiPostJson<OptimizationResponse>("/api/optimize", body);
}

export function buildDownloadUrl(downloadUrl: string): string {
    if (/^https?:\/\//i.test(downloadUrl)) return downloadUrl;
    return buildApiUrl(downloadUrl);
}
