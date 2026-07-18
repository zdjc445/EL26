import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { App } from "./app/App";
import { AppProviders } from "./app/AppProviders";
import "./styles/index.css";

const root = document.getElementById("root");
if (root === null) {
  throw new Error("Missing #root application mount point");
}

createRoot(root).render(
  <StrictMode>
    <AppProviders>
      <App />
    </AppProviders>
  </StrictMode>,
);
