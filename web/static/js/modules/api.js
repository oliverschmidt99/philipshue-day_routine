// web/static/js/modules/api.js

async function fetchAPI(url, options = {}) {
  try {
    const response = await fetch(url, options);
    // Log ist reiner Text, der Rest JSON
    const data = response.headers
      .get("Content-Type")
      ?.includes("application/json")
      ? await response.json()
      : await response.text();

    if (!response.ok) {
      // Wenn der Server JSON-Fehler schickt, nutze die Nachricht
      const errorMessage =
        typeof data === "object" && data.error
          ? data.error
          : `HTTP-Fehler: ${response.status}`;
      throw new Error(errorMessage);
    }
    return data;
  } catch (error) {
    // Fängt Netzwerkfehler ab
    console.error(`API-Fehler bei ${url}:`, error);
    throw error;
  }
}

// --- Setup ---
export const checkSetupStatus = () => fetchAPI("/api/setup/status");
export const discoverBridges = () => fetchAPI("/api/setup/discover");
export const connectToBridge = (ip) =>
  fetchAPI("/api/setup/connect", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ip }),
  });
export const saveSetupConfig = (configData) =>
  fetchAPI("/api/setup/save", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(configData),
  });

// --- Config ---
export const loadConfig = () => fetchAPI("/api/config/");
export const saveFullConfig = (config) =>
  fetchAPI("/api/config/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(config),
  });

// --- Bridge Data ---
export const loadBridgeData = () => fetchAPI("/api/bridge/all_items");

// --- Status & Logs ---
export async function updateStatus() {
  const [statusData, logText] = await Promise.all([
    fetchAPI("/api/data/status"),
    fetchAPI("/api/data/log"), // Log ist reiner Text
  ]);
  return { statusData, logText };
}

// --- Analyse ---
export const loadChartData = (sensorId, date) =>
  fetchAPI(`/api/data/history?sensor_id=${sensorId}&date=${date}`);

// --- System ---
export const addDefaultScenes = () =>
  fetchAPI("/api/system/scenes/add_defaults", { method: "POST" });
