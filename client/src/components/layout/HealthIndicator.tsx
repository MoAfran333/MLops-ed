import { useHealth } from "@/src/hooks/useHealth";
import { StatusBadge } from "@/src/components/ui/StatusBadge";

export function HealthIndicator() {
    const status = useHealth();

    if (status === "checking") {
        return (
            <StatusBadge tone="neutral" dot>
                Checking API…
            </StatusBadge>
        );
    }
    if (status === "online") {
        return (
            <StatusBadge tone="success" dot>
                API Connected
            </StatusBadge>
        );
    }
    return (
        <StatusBadge tone="error" dot>
            API Offline
        </StatusBadge>
    );
}
