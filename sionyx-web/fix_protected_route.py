new_content = """import { useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';
import { Spin } from 'antd';
import { getAuth, onAuthStateChanged } from 'firebase/auth';
import { ref, get } from 'firebase/database';
import { database } from '../config/firebase';
import { isAdminOrAbove } from '../utils/roles';

const ProtectedRoute = ({ children }) => {
  const [status, setStatus] = useState('loading');

  useEffect(() => {
    const auth = getAuth();
    const unsub = onAuthStateChanged(auth, async (user) => {
      if (!user) { setStatus('unauth'); return; }
      try {
        const orgId = localStorage.getItem('adminOrgId');
        if (!orgId) { setStatus('unauth'); return; }
        const snap = await get(ref(database, `organizations/${orgId}/users/${user.uid}`));
        if (snap.exists() && isAdminOrAbove(snap.val())) {
          setStatus('auth');
        } else {
          setStatus('unauth');
        }
      } catch {
        setStatus('unauth');
      }
    });
    return () => unsub();
  }, []);

  if (status === 'loading') return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
      <Spin size='large' />
    </div>
  );
  if (status === 'unauth') return <Navigate to='/login' replace />;
  return children;
};
export default ProtectedRoute;
"""
open(r'.\src\components\ProtectedRoute.jsx', 'w', encoding='utf-8').write(new_content)
print("OK")
