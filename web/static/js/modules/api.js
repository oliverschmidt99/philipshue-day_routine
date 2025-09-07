// web/static/js/modules/api.js

/**
 * Eine generische Funktion zum Abrufen von Daten vom Server.
 * Sie verarbeitet JSON- und Text-Antworten und behandelt Fehler.
 * @param {string} url - Die API-Endpunkt-URL.
 * @param {object} options - Die Optionen für den fetch-Aufruf (z.B. Methode, Body).
 * @returns {Promise<any>} - Die geparsten Daten von der API.
 */
export async function fetchJson(url, options = {}) {
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
      // Versucht, eine aussagekräftige Fehlermeldung aus der Antwort zu extrahieren.
      const errorMessage =
        typeof data === "object" && data.error
          ? data.error
          : `HTTP Error ${response.status}: ${await response.text()}`;
      throw new Error(errorMessage);
    }
    return data;
  } catch (error) {
    // Loggt den Fehler für Debugging-Zwecke und wirft ihn erneut,
    // damit die aufrufende Funktion ihn behandeln kann.
    console.error(`API Error at ${url}:`, error);
    throw error;
  }
}

// --- Setup ---
export const checkSetupStatus = () => fetchJson("/api/setup/status");
export const discoverBridges = () => fetchJson("/api/setup/discover");
export const connectToBridge = (ip) =>
  fetchJson("/api/setup/connect", {
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
export const loadConfig = () => fetchJson("/api/config/");
export const saveFullConfig = (config) =>
  fetchJson("/api/config/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(config),
  });
export const systemAction = async (url, confirmMessage) => {
  if (confirm(confirmMessage)) {
    try {
      const result = await fetchJson(url, { method: "POST" });
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
export const loadBridgeData = () => fetchJson("/api/bridge/all_items");
export const renameBridgeItem = (type, id, newName) =>
  fetchJson(`/api/bridge/${type}/${id}/rename`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name: newName }),
  });
export const deleteBridgeItem = (type, id) =>
  fetchJson(`/api/bridge/${type}/${id}/delete`, { method: "DELETE" });

// --- Status & Logs ---
export async function updateStatus() {
  const [statusData, logText] = await Promise.all([
    fetchJson("/api/data/status"),
    fetchJson("/api/data/log"),
  ]);
  return { statusData, logText };
}

// --- Analyse ---
export const loadChartData = (sensorId, period, date, avg) =>
  fetchJson(
    `/api/data/history?sensor_id=${sensorId}&period=${period}&date=${date}&avg=${avg}`
  );

// --- System & Hilfe ---
export const addDefaultScenes = () =>
  fetchJson("/api/system/scenes/add_defaults", { method: "POST" });
export const loadHelpContent = () => fetchJson("/api/system/help");
