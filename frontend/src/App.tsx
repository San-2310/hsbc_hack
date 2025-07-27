import React from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout/Layout";
import LoadingSpinner from "./components/UI/LoadingSpinner";
import { useAuth } from "./context/AuthContext";
import { useTheme } from "./context/ThemeContext";
import Analytics from "./pages/Analytics";
import Dashboard from "./pages/Dashboard";
import Files from "./pages/Files";
import Login from "./pages/Login";
import Processing from "./pages/Processing";
import Profile from "./pages/Profile";
import Upload from "./pages/Upload";

function App() {
  const { user, loading } = useAuth();
  const { theme } = useTheme();

  // Set theme on document
  React.useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-base-100">
        <LoadingSpinner />
      </div>
    );
  }

  if (!user) {
    return <Login />;
  }

  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/upload" element={<Upload />} />
        <Route path="/files" element={<Files />} />
        <Route path="/processing" element={<Processing />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Layout>
  );
}

export default App;
