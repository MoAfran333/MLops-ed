import { apiPostJson } from "./client";
import type {
    VerificationRequest,
    VerificationResponse,
} from "@/src/types/types";

export function runVerification(
    datasetId: string,
    targetColumn: string,
    model: string,
) {
    const body: VerificationRequest = {
        dataset_id: datasetId,
        target_column: targetColumn,
        model,
    };
    return apiPostJson<VerificationResponse>("/api/verify", body);
}
