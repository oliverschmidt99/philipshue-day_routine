// web/static/js/modules/api.js

async function fetchAPI(url, options = {}) {
  try {
    const response = await fetch(url, options);
    const contentType = response.headers.get("Content-Type") || "";

    let data;
    if (contentType.includes("application/json")) {
      data = await response.json();
    } else {
      data = await response.text();
    }

    if (!response.ok) {
      const errorMessage =
        typeof data === "object" && data.error
          ? data.error
          : `HTTP-Fehler ${response.status}: ${data}`;
      throw new Error(errorMessage);
    }
    return data;
  } catch (error) {
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
export const systemAction = async (url, confirmMessage) => {
  if (confirm(confirmMessage)) {
    try {
      const result = await fetchAPI(url, { method: "POST" });
      alert(result.message || "Aktion erfolgreich ausgeführt.");
      if (url.includes("restore") || url.includes("restart")) {
        setTimeout(() => window.location.reload(), 1000);
      }
    } catch (error) {
      alert(`Fehler: ${error.message}`);
    }
  }
};

// --- Bridge Data ---
export const loadBridgeData = () => fetchAPI("/api/bridge/all_items");
export const renameBridgeItem = (type, id, newName) =>
  fetchAPI(`/api/bridge/${type}/${id}/rename`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name: newName }),
  });
export const deleteBridgeItem = (type, id) =>
  fetchAPI(`/api/bridge/${type}/${id}/delete`, { method: "DELETE" });

// --- Status & Logs ---
export async function updateStatus() {
  const [statusData, logText] = await Promise.all([
    fetchAPI("/api/data/status"),
    fetchAPI("/api/data/log"),
  ]);
  return { statusData, logText };
}

// --- Analyse ---
export const loadChartData = (sensorId, period, date, avg) =>
  fetchAPI(
    `/api/data/history?sensor_id=${sensorId}&period=${period}&date=${date}&avg=${avg}`
  );

// --- System & Hilfe ---
export const addDefaultScenes = () =>
  fetchAPI("/api/system/scenes/add_defaults", { method: "POST" });
export const loadHelpContent = () => fetchAPI("/api/help/");
