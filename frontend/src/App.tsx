import { lazy, Suspense } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { Center, Loader } from "@mantine/core";

import { AuthProvider } from "./auth/AuthContext";
import { RequireAuth } from "./auth/RequireAuth";
import { Layout } from "./components/Layout";
import { HomePage } from "./pages/HomePage";
import { LoginPage } from "./pages/LoginPage";
import { EspecialidadesPage } from "./pages/EspecialidadesPage";
import { IntermediariosPage } from "./pages/IntermediariosPage";
import { ExternosPage } from "./pages/ExternosPage";

// Dashboard usa recharts (pesado); carrega sob procura para aliviar o bundle inicial.
const DashboardPage = lazy(() =>
  import("./pages/DashboardPage").then((m) => ({ default: m.DashboardPage })),
);

export function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route element={<RequireAuth />}>
            <Route element={<Layout />}>
              <Route path="/" element={<HomePage />} />
              <Route
                path="/dashboard"
                element={
                  <Suspense fallback={<Center mih="60vh"><Loader /></Center>}>
                    <DashboardPage />
                  </Suspense>
                }
              />
              <Route path="/especialidades" element={<EspecialidadesPage />} />
              <Route path="/intermediarios" element={<IntermediariosPage />} />
              <Route path="/externos" element={<ExternosPage />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Route>
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
