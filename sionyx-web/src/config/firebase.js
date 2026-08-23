import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getDatabase } from 'firebase/database';
import { getFunctions } from 'firebase/functions';
import { getStorage } from 'firebase/storage';

// הגדרות ה-Firebase המלאות והמדויקות של פרויקט pc-sion
const firebaseConfig = {
  apiKey: "AIzaSyBcL4wpFbFDgQ4l0AXNADw3D9ht70lpJe4",
  authDomain: "pc-sion.firebaseapp.com",
  databaseURL: "https://pc-sion-default-rtdb.firebaseio.com",
  projectId: "pc-sion",
  storageBucket: "pc-sion.appspot.com",
  messagingSenderId: "53784185799",
  appId: "1:53784185799:web:3e6e7651a021a868de9a98"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize services
export const auth = getAuth(app);
export const database = getDatabase(app);
export const functions = getFunctions(app, 'us-central1');
export const storage = getStorage(app);

// Owner and supervisor logins used to share the SAME Firebase Auth instance
// as the regular org/admin login ("auth" above). Firebase Auth only keeps
// ONE signed-in user per app instance (persisted to browser storage), so
// logging in as one role silently signed the others out - open the owner
// dashboard in one tab, then log in as a supervisor in another tab, and the
// owner session would die. Each role now gets its own NAMED secondary
// Firebase app (same project/config, different persistence slot), so the
// three logins are fully independent of one another and of each other's tabs.
const ownerApp = initializeApp(firebaseConfig, 'owner');
export const ownerAuth = getAuth(ownerApp);
export const ownerDatabase = getDatabase(ownerApp);

const supervisorApp = initializeApp(firebaseConfig, 'supervisor');
export const supervisorAuth = getAuth(supervisorApp);
export const supervisorDatabase = getDatabase(supervisorApp);

export default app;