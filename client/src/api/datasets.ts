import { apiGet, apiPostForm } from "./client";
import type { HealthResponse, DatasetInfo } from "@/src/types/types";

export function getHealth() {
    return apiGet<HealthResponse>("/api/health");
}

export function uploadDataset(file: File) {
    const formData = new FormData();
    formData.append("file", file);
    console.log(`file received: ${file}`);
    return apiPostForm<DatasetInfo>("/api/datasets/upload", formData);
}

export function getDataset(datasetId: string) {
    return apiGet<DatasetInfo>(
        `/api/datasets/${encodeURIComponent(datasetId)}`,
    );
}
