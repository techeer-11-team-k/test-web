import { createRoot } from "react-dom/client";
import App from "./App.tsx";
import "./index.css";
import { ClerkAuthProvider } from "./lib/clerk";

createRoot(document.getElementById("root")!).render(
  <ClerkAuthProvider>
    <App />
  </ClerkAuthProvider>
);