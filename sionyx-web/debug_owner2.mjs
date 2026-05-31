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

const cred = await signInWithEmailAndPassword(auth, "05484779100@sionyx.app", "345345");
console.log("UID:", cred.user.uid);

const ownerSnap = await get(ref(db, `owners/${cred.user.uid}`));
console.log("Owner exists:", ownerSnap.exists());

const allOwners = await get(ref(db, "owners"));
console.log("All owners:", allOwners.exists() ? Object.keys(allOwners.val()) : "none");

process.exit(0);
