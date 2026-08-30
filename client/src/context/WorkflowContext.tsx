import {
    createContext,
    useContext,
    useEffect,
    useState,
    type ReactNode,
} from "react";
import type {
    DatasetInfo,
    RecommendationResponse,
    VerificationResponse,
    OptimizationResponse,
    ProfileResponse,
} from "@/src/types/types";

interface WorkflowState {
    dataset: DatasetInfo | null;
    targetColumn: string;
    problemType: string;
    metaFeatures: Record<string, unknown> | null;
    recommendedModel: string;
    recommendation: RecommendationResponse | null;
    verificationResult: VerificationResponse | null;
    optimizationResult: OptimizationResponse | null;
    profile: ProfileResponse | null;
    profileFilename: string;
}

interface WorkflowContextValue extends WorkflowState {
    setDataset: (dataset: DatasetInfo | null) => void;
    setTargetColumn: (target: string) => void;
    setProblemType: (type: string) => void;
    setMetaFeatures: (features: Record<string, unknown> | null) => void;
    setRecommendedModel: (model: string) => void;
    setRecommendation: (rec: RecommendationResponse | null) => void;
    setVerificationResult: (result: VerificationResponse | null) => void;
    setOptimizationResult: (result: OptimizationResponse | null) => void;
    setProfile: (profile: ProfileResponse | null) => void;
    setProfileFilename: (filename: string) => void;
    reset: () => void;
}

const STORAGE_KEY = "ml-system-workflow-v1";

const initialState: WorkflowState = {
    dataset: null,
    targetColumn: "",
    problemType: "",
    metaFeatures: null,
    recommendedModel: "",
    recommendation: null,
    verificationResult: null,
    optimizationResult: null,
    profile: null,
    profileFilename: "",
};

const WorkflowContext = createContext<WorkflowContextValue | undefined>(
    undefined,
);

function loadState(): WorkflowState {
    try {
        const raw = localStorage.getItem(STORAGE_KEY);
        if (!raw) return initialState;
        const parsed = JSON.parse(raw) as Partial<WorkflowState>;
        return { ...initialState, ...parsed };
    } catch {
        return initialState;
    }
}

export function WorkflowProvider({ children }: { children: ReactNode }) {
    const [state, setState] = useState<WorkflowState>(loadState);

    useEffect(() => {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
        } catch {
            // ignore quota errors
        }
    }, [state]);

    const update = (patch: Partial<WorkflowState>) =>
        setState((s) => ({ ...s, ...patch }));

    const value: WorkflowContextValue = {
        ...state,
        setDataset: (dataset) => update({ dataset }),
        setTargetColumn: (targetColumn) => update({ targetColumn }),
        setProblemType: (problemType) => update({ problemType }),
        setMetaFeatures: (metaFeatures) => update({ metaFeatures }),
        setRecommendedModel: (recommendedModel) => update({ recommendedModel }),
        setRecommendation: (recommendation) => update({ recommendation }),
        setVerificationResult: (verificationResult) =>
            update({ verificationResult }),
        setOptimizationResult: (optimizationResult) =>
            update({ optimizationResult }),
        setProfile: (profile) => update({ profile }),
        setProfileFilename: (profileFilename) => update({ profileFilename }),
        reset: () => setState(initialState),
    };

    return (
        <WorkflowContext.Provider value={value}>
            {children}
        </WorkflowContext.Provider>
    );
}

export function useWorkflow() {
    const ctx = useContext(WorkflowContext);
    if (!ctx)
        throw new Error("useWorkflow must be used within WorkflowProvider");
    return ctx;
}
