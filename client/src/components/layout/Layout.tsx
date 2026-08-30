import { useState, type ReactNode } from "react";
import { Sidebar } from "@/src/components/layout/Sidebar";
import { Header } from "@/src/components/layout/Header";

export function Layout({ children }: { children: ReactNode }) {
    const [mobileNavOpen, setMobileNavOpen] = useState(false);

    return (
        <div className="flex h-screen overflow-hidden bg-slate-50">
            {/* Desktop sidebar */}
            <div className="hidden lg:block">
                <Sidebar />
            </div>

            {/* Mobile drawer */}
            {mobileNavOpen && (
                <div className="fixed inset-0 z-40 lg:hidden">
                    <div
                        className="absolute inset-0 bg-slate-900/40"
                        onClick={() => setMobileNavOpen(false)}
                        aria-hidden="true"
                    />
                    <div className="absolute left-0 top-0 h-full">
                        <Sidebar />
                    </div>
                </div>
            )}

            <div className="flex flex-1 flex-col overflow-hidden">
                <Header onMenuClick={() => setMobileNavOpen(true)} />
                <main className="flex-1 overflow-y-auto">
                    <div className="mx-auto max-w-6xl px-4 py-6 sm:px-6 lg:px-8">
                        {children}
                    </div>
                </main>
            </div>
        </div>
    );
}
