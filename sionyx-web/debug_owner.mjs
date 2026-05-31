import { initializeApp } from "firebase/app";
import { getDatabase, ref, get } from "firebase/database";
import { getAuth, signInWithEmailAndPassword } from "firebase/auth";

const app = initializeApp({
  apiKey: "AIzaSyBcL4wpFbFDgQ4l0AXNADw3D9ht70lpJe4",
  authDomain: "pc-sion.firebaseapp.com",
  databaseURL: "https://pc-sion-default-rtdb.firebaseio.com",
  projectId: "pc-sion",
});

const auth = getAuth(app);
const db = getDatabase(app);

await signInWithEmailAndPassword(auth, "05484779100@sionyx.app", "345345");
console.log("Auth OK");

const orgs = await get(ref(db, "organizations"));
console.log("Organizations:", orgs.exists() ? Object.keys(orgs.val()) : "empty");

const sups = await get(ref(db, "supervisors"));
console.log("Supervisors:", sups.exists() ? Object.keys(sups.val()) : "empty");

process.exit(0);
