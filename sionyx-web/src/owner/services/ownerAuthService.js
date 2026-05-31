import { signInWithEmailAndPassword, signOut as firebaseSignOut, onAuthStateChanged, updatePassword } from "firebase/auth";
import { ref, get } from "firebase/database";
import { auth, database } from "../../config/firebase";

const phoneToEmail = (phone) => `${phone.replace(/\D/g, "")}@sionyx.app`;

const waitForAuth = () =>
  new Promise((resolve) => {
    if (auth.currentUser) return resolve(auth.currentUser);
    const unsub = onAuthStateChanged(auth, (user) => { unsub(); resolve(user); });
  });

export const signInOwner = async (phone, password) => {
  try {
    const email = phoneToEmail(phone);
    const cred = await signInWithEmailAndPassword(auth, email, password);
    const snap = await get(ref(database, `owners/${cred.user.uid}`));
    if (!snap.exists()) {
      await firebaseSignOut(auth);
      return { success: false, error: "אין הרשאות בעל מערכת" };
    }
    return { success: true, owner: { uid: cred.user.uid, ...snap.val() } };
  } catch (e) {
    return { success: false, error: "טלפון או סיסמה שגויים" };
  }
};

export const signOutOwner = async () => {
  await firebaseSignOut(auth);
};

export const changeOwnerPassword = async (newPassword) => {
  try {
    const user = await waitForAuth();
    if (!user) return { success: false, error: "לא מחובר" };
    await updatePassword(user, newPassword);
    return { success: true };
  } catch (e) {
    return { success: false, error: e.message };
  }
};

export const onOwnerAuthChange = (callback) => onAuthStateChanged(auth, callback);
