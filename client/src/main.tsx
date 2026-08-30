import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { Toaster } from "sonner";
import App from "./App";
import { WorkflowProvider } from "./context/WorkflowContext";
import "./styles.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
    <React.StrictMode>
        <BrowserRouter>
            <WorkflowProvider>
                <App />
                <Toaster position="top-right" richColors closeButton />
            </WorkflowProvider>
        </BrowserRouter>
    </React.StrictMode>,
);
