import os

# Create OwnerProtectedRoute
route_content = """import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import { getAuth, onAuthStateChanged } from "firebase/auth";
import { ref, get } from "firebase/database";
import { database } from "../../config/firebase";
import { Spin } from "antd";

const OwnerProtectedRoute = ({ children }) => {
  const [status, setStatus] = useState("loading");

  useEffect(() => {
    const auth = getAuth();
    const unsub = onAuthStateChanged(auth, async (user) => {
      if (!user) { setStatus("unauth"); return; }
      const snap = await get(ref(database, `owners/${user.uid}`));
      setStatus(snap.exists() ? "auth" : "unauth");
    });
    return () => unsub();
  }, []);

  if (status === "loading") return (
    <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100vh" }}>
      <Spin size="large" />
    </div>
  );
  if (status === "unauth") return <Navigate to="/owner/login" replace />;
  return children;
};

export default OwnerProtectedRoute;
"""

os.makedirs(r'.\src\owner', exist_ok=True)
open(r'.\src\owner\OwnerProtectedRoute.jsx', 'w', encoding='utf-8').write(route_content)
print("OwnerProtectedRoute created")

# Fix App.jsx
content = open(r'.\src\App.jsx', encoding='utf-8').read()

old = """const OwnerLoginPage = lazy(() => import('./owner/pages/OwnerLoginPage'));
const OwnerDashboardPage = lazy(() => import('./owner/pages/OwnerDashboardPage'));"""

new = """const OwnerLoginPage = lazy(() => import('./owner/pages/OwnerLoginPage'));
const OwnerDashboardPage = lazy(() => import('./owner/pages/OwnerDashboardPage'));
import OwnerProtectedRoute from './owner/OwnerProtectedRoute';"""

# Use different approach - add import at top
old2 = """import OwnerProtectedRoute from './owner/OwnerProtectedRoute';"""
if old2 in content:
    print("Import already exists")
else:
    content = content.replace(
        "const OwnerLoginPage = lazy(() => import('./owner/pages/OwnerLoginPage'));",
        "const OwnerLoginPage = lazy(() => import('./owner/pages/OwnerLoginPage'));"
    )

old3 = """              <Route path='/owner/login' element={<OwnerLoginPage />} />
              <Route path='/owner' element={<OwnerDashboardPage />} />"""

new3 = """              <Route path='/owner/login' element={<OwnerLoginPage />} />
              <Route path='/owner' element={<OwnerProtectedRoute><OwnerDashboardPage /></OwnerProtectedRoute>} />"""

count3 = content.count(old3)
print(f"Route fix: {count3} matches")
if count3 == 1:
    content = content.replace(old3, new3, 1)

# Add import after other imports
old4 = """import { useOwnerAuthStore } from './owner/store/ownerAuthStore';"""
if old4 not in content:
    old_import = """const OwnerLoginPage = lazy(() => import('./owner/pages/OwnerLoginPage'));"""
    new_import = """import OwnerProtectedRoute from './owner/OwnerProtectedRoute';
const OwnerLoginPage = lazy(() => import('./owner/pages/OwnerLoginPage'));"""
    content = content.replace(old_import, new_import, 1)
    print("Import added")

open(r'.\src\App.jsx', 'w', encoding='utf-8').write(content)
print("App.jsx updated")
