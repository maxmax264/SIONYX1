content = open(r'.\src\supervisor\SupervisorProtectedRoute.jsx', encoding='utf-8').read()

new = """import { useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';
import { Spin } from 'antd';
import { getAuth, onAuthStateChanged } from 'firebase/auth';
import { ref, get } from 'firebase/database';
import { database } from '../config/firebase';

const SupervisorProtectedRoute = ({ children }) => {
  const [status, setStatus] = useState('loading');

  useEffect(() => {
    const auth = getAuth();
    const unsub = onAuthStateChanged(auth, async (user) => {
      if (!user) { setStatus('unauth'); return; }
      const snap = await get(ref(database, `supervisors/${user.uid}`));
      setStatus(snap.exists() ? 'auth' : 'unauth');
    });
    return () => unsub();
  }, []);

  if (status === 'loading') return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
      <Spin size='large' />
    </div>
  );
  if (status === 'unauth') return <Navigate to='/supervisor/login' replace />;
  return children;
};
export default SupervisorProtectedRoute;
"""

open(r'.\src\supervisor\SupervisorProtectedRoute.jsx', 'w', encoding='utf-8').write(new)
print("OK - file written")
