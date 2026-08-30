import { apiPostJson } from "./client";
import type {
    RecommendationRequest,
    RecommendationResponse,
} from "@/src/types/types";

export function getRecommendation(datasetId: string, targetColumn: string) {
    const body: RecommendationRequest = {
        dataset_id: datasetId,
        target_column: targetColumn,
    };
    return apiPostJson<RecommendationResponse>("/api/recommendation", body);
}
