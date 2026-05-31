import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import { getAuth, onAuthStateChanged } from "firebase/auth";
import { ref, get } from "firebase/database";
import { database } from "../config/firebase";
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
