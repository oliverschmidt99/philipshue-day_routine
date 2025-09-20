// web/static/js/modules/api.js

async function fetchAPI(url, options = {}) {
  try {
    const response = await fetch(url, options);
    const data = response.headers
      .get("Content-Type")
      ?.includes("application/json")
      ? await response.json()
      : await response.text();

    if (!response.ok) {
      const errorMessage =
        typeof data === "object" && data.error
          ? data.error
          : `HTTP-Fehler: ${response.status}`;
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

// --- Bridge Data ---
export const loadBridgeData = () => fetchAPI("/api/bridge/all_items");
export const loadGroupedLights = () =>
  fetchAPI("/api/bridge/all_grouped_lights");

export const setGroupState = (groupId, state) =>
  fetchAPI(`/api/bridge/grouped_light/${groupId}/state`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(state),
  });

export const setLightState = (lightId, state) =>
  fetchAPI(`/api/bridge/light/${lightId}/state`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(state),
  });

// --- Status & Logs ---
export async function updateStatus() {
  const [statusData, logText] = await Promise.all([
    fetchAPI("/api/data/status"),
    fetchAPI("/api/data/log"),
  ]);
  return { statusData, logText };
}

// --- Analyse ---
export const loadChartData = (sensorId, date) =>
  fetchAPI(`/api/data/history?sensor_id=${sensorId}&date=${date}`);

// --- System ---
export const addDefaultScenes = () =>
  fetchAPI("/api/system/scenes/add_defaults", { method: "POST" });

export const recallScene = (groupId, sceneId) =>
  fetchAPI(`/api/bridge/group/${groupId}/scene`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ scene_id: sceneId }),
  });

// --- NEUE FUNKTIONEN FÜR SZENEN-MANAGEMENT ---
export const createScene = (sceneData) =>
  fetchAPI("/api/bridge/scenes", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(sceneData),
  });

export const deleteScene = (sceneId) =>
  fetchAPI(`/api/bridge/scenes/${sceneId}`, {
    method: "DELETE",
  });
