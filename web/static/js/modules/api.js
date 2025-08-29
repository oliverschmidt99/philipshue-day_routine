// web/static/js/modules/api.js

async function fetchAPI(url, options = {}) {
  const response = await fetch(url, options);
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || `HTTP-Fehler: ${response.status}`);
  }
  return data;
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
export const loadConfig = () => fetchAPI("/api/config");
export const saveFullConfig = (config) =>
  fetchAPI("/api/config", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(config),
  });

// --- Bridge Data ---
export async function loadBridgeData() {
  // Diese Route wird jetzt von /api/bridge/all_items abgedeckt
  const data = await fetchAPI("/api/bridge/all_items");
  return {
    groups: data.grouped_lights,
    sensors: data.sensors,
  };
}
export const loadBridgeItems = () => fetchAPI("/api/bridge/all_items");

// --- Status & Logs ---
export async function updateStatus() {
  const [statusData, logRes] = await Promise.all([
    fetchAPI("/api/data/status"),
    fetch("/api/data/log"), // Log ist reiner Text
  ]);
  return { statusData, logText: await logRes.text() };
}

// --- Analyse ---
export const loadChartData = (sensorId, date) =>
  fetchAPI(`/api/data/history?sensor_id=${sensorId}&date=${date}`);

// --- System ---
export const addDefaultScenes = () =>
  fetchAPI("/api/system/scenes/add_defaults", { method: "POST" });
