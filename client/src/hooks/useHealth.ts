import { useEffect, useState } from "react";
import { getHealth } from "@/src/api/datasets";

export type HealthStatus = "checking" | "online" | "offline";

export function useHealth(pollMs = 30000) {
    const [status, setStatus] = useState<HealthStatus>("checking");

    useEffect(() => {
        let active = true;

        const check = async () => {
            try {
                const res = await getHealth();
                if (active) {
                    setStatus(res.status === "ok" ? "online" : "offline");
                }
            } catch {
                if (active) setStatus("offline");
            }
        };

        check();
        const interval = setInterval(check, pollMs);
        return () => {
            active = false;
            clearInterval(interval);
        };
    }, [pollMs]);

    return status;
}
