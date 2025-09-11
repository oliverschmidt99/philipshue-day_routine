/**
 * Eine generische Fetch-Funktion für API-Aufrufe.
 * @param {string} url - Die API-Endpunkt-URL.
 * @param {object} [options={}] - Die Optionen für den fetch()-Aufruf.
 * @returns {Promise<any>} Die JSON-Antwort vom Server.
 */
async function fetchAPI(url, options = {}) {
  try {
    const response = await fetch(url, options);
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || `HTTP-Fehler ${response.status}`);
    }
    return data;
  } catch (error) {
    console.error(`API Fehler bei '${url}':`, error);
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

// --- Konfiguration ---
export const loadConfig = () => fetchAPI("/api/config/");
export const saveConfig = (config) =>
  fetchAPI("/api/config/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(config),
  });

// --- Bridge-Daten ---
export const loadBridgeData = () => fetchAPI("/api/bridge/all_items");
