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

export default app;