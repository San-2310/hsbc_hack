// // src/firebase.ts
// import { initializeApp } from "firebase/app";

// const firebaseConfig = {
//   apiKey: process.env.REACT_APP_FIREBASE_API_KEY!,
//   authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN!,
//   projectId: process.env.REACT_APP_FIREBASE_PROJECT_ID!,
//   storageBucket: process.env.REACT_APP_FIREBASE_STORAGE_BUCKET!,
//   messagingSenderId: process.env.REACT_APP_FIREBASE_MESSAGING_SENDER_ID!,
//   appId: process.env.REACT_APP_FIREBASE_APP_ID!,
//   measurementId: process.env.REACT_APP_FIREBASE_MEASUREMENT_ID!,
// };

// const app = initializeApp(firebaseConfig);

// export default app;
import { initializeApp } from "firebase/app";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyD7sSQ0il_27YAYzf0F-P1W5z7TEicetQc",
  authDomain: "hsbc-api-98ff3.firebaseapp.com",
  projectId: "hsbc-api-98ff3",
  storageBucket: "hsbc-api-98ff3.firebasestorage.app",
  messagingSenderId: "44619439858",
  appId: "1:44619439858:web:b7df02bfec117dd2fdfa6b",
  measurementId: "G-585DQ143TC",
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
export default app;
