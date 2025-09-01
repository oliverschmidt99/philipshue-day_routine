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
// HIER IST DIE KORREKTUR: Die Funktion heißt jetzt loadBridgeData und nutzt den korrekten Endpunkt
export const loadBridgeData = () => fetchAPI("/api/bridge/all_items");

export const renameBridgeItem = (itemType, itemId, newName) =>
  fetchAPI("/api/bridge/rename", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ type: itemType, id: itemId, name: newName }),
  });

export const deleteBridgeItem = (itemType, itemId) =>
  fetchAPI("/api/bridge/delete", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ type: itemType, id: itemId }),
  });

// --- Status & Logs ---
export async function updateStatus() {
  const [statusData, logText] = await Promise.all([
    fetchAPI("/api/data/status"),
    fetchAPI("/api/data/log"), // Log ist reiner Text
  ]);
  return { statusData, logText };
}

// --- Analyse ---
export const loadChartData = (sensorId, period, date, avgWindow) =>
  fetchAPI(
    `/api/data/history?sensor_id=${sensorId}&period=${period}&date=${date}&avg=${avgWindow}`
  );

// --- Help ---
export const loadHelpContent = () => fetchAPI("/api/help");

// --- System ---
export const addDefaultScenes = () =>
  fetchAPI("/api/system/scenes/add_defaults", { method: "POST" });

export async function systemAction(url, confirmMsg) {
  if (confirm(confirmMsg)) {
    // Find toast in a more robust way
    const showToast = (message, isError = false) => {
      const toastElement = document.getElementById("toast");
      if (!toastElement) return;
      toastElement.textContent = message;
      toastElement.className = `fixed bottom-5 right-5 text-white py-2 px-4 rounded-lg shadow-xl transition-opacity duration-300 ${
        isError ? "bg-red-600" : "bg-gray-900"
      }`;
      toastElement.classList.remove("hidden");
      setTimeout(() => toastElement.classList.add("hidden"), 5000);
    };

    showToast("Aktion wird ausgeführt...", false);
    try {
      const response = await fetch(url, { method: "POST" });
      const result = await response.json();
      if (!response.ok) {
        throw new Error(
          result.error || result.message || "Unbekannter Serverfehler"
        );
      }
      alert(
        "Ergebnis:\n\n" +
          (result.message ||
            "Aktion ohne detaillierte Rückmeldung abgeschlossen.")
      );
      showToast("Aktion erfolgreich!", false);
      return result;
    } catch (e) {
      alert("Fehler:\n\n" + e.message);
      showToast("Aktion fehlgeschlagen.", true);
      return null;
    }
  }
  return null;
}
