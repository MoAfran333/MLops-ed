import { apiPostJson } from "./client";
import type { ProfileRequest, ProfileResponse } from "@/src/types/types";

export function generateProfile(datasetId: string) {
    const body: ProfileRequest = { dataset_id: datasetId };
    return apiPostJson<ProfileResponse>("/api/profile/", body);
}

export function buildProfileUrl(filename: string): string {
    return `/api/profile/${encodeURIComponent(filename)}`;
}
