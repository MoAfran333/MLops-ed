import type { ApiError } from "@/src/types/types";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000/";

export class ApiRequestError extends Error {
    status?: number;
    detail?: string;
    constructor(message: string, status?: number, detail?: string) {
        super(message);
        this.name = "ApiRequestError";
        this.status = status;
        this.detail = detail;
    }
}

function buildUrl(path: string): string {
    if (BASE_URL && !BASE_URL.endsWith("/")) {
        return `${BASE_URL}${path}`;
    }
    if (BASE_URL.endsWith("/")) {
        return `${BASE_URL.slice(0, -1)}${path}`;
    }
    return path;
}

async function parseError(res: Response): Promise<ApiError> {
    let detail: string | undefined;
    try {
        const data = await res.json();
        detail =
            typeof data.detail === "string"
                ? data.detail
                : JSON.stringify(data);
    } catch {
        detail = res.statusText;
    }
    return {
        message: detail || `Request failed with status ${res.status}`,
        status: res.status,
        detail,
    };
}

export async function apiGet<T>(path: string): Promise<T> {
    let res: Response;
    try {
        res = await fetch(buildUrl(path), {
            method: "GET",
            headers: { Accept: "application/json" },
        });
    } catch {
        throw new ApiRequestError(
            "Network error: unable to reach the API server.",
            0,
        );
    }
    if (!res.ok) {
        const err = await parseError(res);
        throw new ApiRequestError(err.message, err.status, err.detail);
    }
    return (await res.json()) as T;
}

export async function apiPostJson<T>(path: string, body: unknown): Promise<T> {
    let res: Response;
    try {
        res = await fetch(buildUrl(path), {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Accept: "application/json",
            },
            body: JSON.stringify(body),
        });
    } catch {
        throw new ApiRequestError(
            "Network error: unable to reach the API server.",
            0,
        );
    }
    if (!res.ok) {
        const err = await parseError(res);
        throw new ApiRequestError(err.message, err.status, err.detail);
    }
    return (await res.json()) as T;
}

export async function apiPostForm<T>(
    path: string,
    formData: FormData,
): Promise<T> {
    let res: Response;
    try {
        res = await fetch(buildUrl(path), {
            method: "POST",
            body: formData,
        });
    } catch {
        throw new ApiRequestError(
            "Network error: unable to reach the API server.",
            0,
        );
    }
    if (!res.ok) {
        const err = await parseError(res);
        throw new ApiRequestError(err.message, err.status, err.detail);
    }
    return (await res.json()) as T;
}

export function buildApiUrl(path: string): string {
    return buildUrl(path);
}
