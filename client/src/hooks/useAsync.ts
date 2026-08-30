import { useCallback, useRef, useState } from "react";

export type AsyncStatus = "idle" | "loading" | "success" | "error";

export interface AsyncState<T> {
    status: AsyncStatus;
    data: T | null;
    error: string | null;
}

export function useAsync<T>() {
    const requestId = useRef(0);
    const [state, setState] = useState<AsyncState<T>>({
        status: "idle",
        data: null,
        error: null,
    });

    const run = useCallback(async (fn: () => Promise<T>) => {
        const id = ++requestId.current;
        setState({ status: "loading", data: null, error: null });
        try {
            const data = await fn();
            if (id === requestId.current) {
                setState({ status: "success", data, error: null });
            }
            return data;
        } catch (err) {
            if (id === requestId.current) {
                const message =
                    err instanceof Error ? err.message : "Unexpected error";
                setState({ status: "error", data: null, error: message });
            }
            throw err;
        }
    }, []);

    const reset = useCallback(() => {
        setState({ status: "idle", data: null, error: null });
    }, []);

    return { state, run, reset, setState };
}
