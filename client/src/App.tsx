import { Routes, Route, Navigate } from "react-router-dom";
import { Layout } from "@/src/components/layout/Layout";
import { Dashboard } from "@/src/pages/Dashboard";
import { Dataset } from "@/src/pages/Dataset";
import { Profiling } from "@/src/pages/Profiling";
import { Recommendation } from "@/src/pages/Recommendation";
import { Verification } from "@/src/pages/Verification";
import { Optimization } from "@/src/pages/Optimization";

export default function App() {
    return (
        <Layout>
            <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/dataset" element={<Dataset />} />
                <Route path="/profiling" element={<Profiling />} />
                <Route path="/recommendation" element={<Recommendation />} />
                <Route path="/verification" element={<Verification />} />
                <Route path="/optimization" element={<Optimization />} />
                <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
        </Layout>
    );
}
