import { useEffect, useState } from "react";

import { getHealth } from "./api/client";

export default function App() {
  const [apiStatus, setApiStatus] = useState("verificando...");

  useEffect(() => {
    getHealth()
      .then((h) => setApiStatus(h.status))
      .catch(() => setApiStatus("indisponível"));
  }, []);

  return (
    <main>
      <h1>Ágon</h1>
      <p>API: {apiStatus}</p>
    </main>
  );
}
