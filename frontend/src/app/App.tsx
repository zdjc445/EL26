import { Route, Routes } from "react-router";

import { SystemStatusPage } from "../features/system/SystemStatusPage";

export function App() {
  return (
    <Routes>
      <Route path="/" element={<SystemStatusPage />} />
    </Routes>
  );
}
