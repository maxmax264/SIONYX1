import { initializeApp } from 'firebase/app';
import { getDatabase, ref, set } from 'firebase/database';

const firebaseConfig = {
  apiKey: "AIzaSyBcL4wpFbFDgQ4l0AXNADw3D9ht70lpJe4",
  authDomain: "pc-sion.firebaseapp.com",
  databaseURL: "https://pc-sion-default-rtdb.firebaseio.com",
  projectId: "pc-sion",
  storageBucket: "pc-sion.appspot.com",
  messagingSenderId: "53784185799",
  appId: "1:53784185799:web:3e6e7651a021a868de9a98"
};

const app = initializeApp(firebaseConfig);
const db = getDatabase(app);

const uid = "uYtbcpgA8TZODcRFGrwc1zGR5Lf2";
await set(ref(db, `owners/${uid}`), {
  name: "Daniel",
  phone: "05484779100",
  createdAt: "2026-01-01"
});
console.log("Owner added successfully!");
process.exit(0);
