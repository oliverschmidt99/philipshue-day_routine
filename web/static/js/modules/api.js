/**
 * Holt den Setup-Status vom Server.
 * @returns {Promise<Object>} Ein Promise, das ein Objekt mit { setup_needed: boolean } zurückgibt.
 */
export async function checkSetupStatus() {
  const response = await fetch("/api/setup/status");
  return response.json();
}

/**
 * Sucht nach Hue Bridges im Netzwerk.
 * @returns {Promise<Array<string>>} Ein Promise, das eine Liste von IP-Adressen zurückgibt.
 */
export async function discoverBridges() {
  const response = await fetch("/api/setup/discover");
  return response.json();
}

/**
 * Versucht, eine Verbindung zur Bridge herzustellen und einen App-Key zu erhalten.
 * @param {string} ip - Die IP-Adresse der Bridge.
 * @returns {Promise<Object>} Ein Promise, das ein Objekt mit dem app_key zurückgibt.
 */
export async function connectToBridge(ip) {
  const response = await fetch("/api/setup/connect", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ip: ip }),
  });
  const data = await response.json();
  if (!response.ok)
    throw new Error(data.error || "Unbekannter Verbindungsfehler");
  return data;
}

/**
 * Speichert die initiale Konfiguration.
 * @param {Object} configData - Die Konfigurationsdaten.
 * @returns {Promise<Object>} Das Ergebnis vom Server.
 */
export async function saveSetupConfig(configData) {
  const response = await fetch("/api/setup/save", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(configData),
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Fehler beim Speichern");
  return data;
}

/**
 * Lädt die Hauptkonfiguration.
 * @returns {Promise<Object>} Die Konfiguration als JSON-Objekt.
 */
export async function loadConfig() {
  const response = await fetch("/api/config");
  if (!response.ok)
    throw new Error("Konfiguration konnte nicht geladen werden");
  return response.json();
}

/**
 * Lädt Bridge-Daten (Gruppen und Sensoren).
 * @returns {Promise<Object>} Ein Objekt mit `groups` und `sensors`.
 */
export async function loadBridgeData() {
  const [groupsRes, sensorsRes] = await Promise.all([
    fetch("/api/bridge/groups"),
    fetch("/api/bridge/sensors"),
  ]);
  if (!groupsRes.ok || !sensorsRes.ok)
    throw new Error("Bridge-Daten konnten nicht geladen werden");
  return {
    groups: await groupsRes.json(),
    sensors: await sensorsRes.json(),
  };
}

/**
 * Lädt alle umbenennbaren Items von der Bridge.
 * @returns {Promise<Object>} Ein Objekt mit `lights`, `sensors` und `groups`.
 */
export async function loadBridgeItems() {
  const response = await fetch("/api/bridge/all_items");
  if (!response.ok)
    throw new Error("Geräte konnten nicht von der Bridge geladen werden");
  return response.json();
}

/**
 * Sendet einen Befehl zum Umbenennen eines Geräts an den Server.
 * @param {string} itemType - Der Typ des Geräts ('light', 'sensor', 'group').
 * @param {string|number} itemId - Die ID des Geräts.
 * @param {string} newName - Der neue Name.
 * @returns {Promise<Object>} Die Antwort vom Server.
 */
export async function renameBridgeItem(itemType, itemId, newName) {
  const response = await fetch("/api/bridge/rename", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ type: itemType, id: itemId, name: newName }),
  });
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || "Fehler beim Umbenennen");
  return result;
}

/**
 * Sendet einen Befehl zum Löschen eines Geräts an den Server.
 * @param {string} itemType - Der Typ des Geräts ('light', 'sensor', 'group').
 * @param {string|number} itemId - Die ID des Geräts.
 * @returns {Promise<Object>} Die Antwort vom Server.
 */
export async function deleteBridgeItem(itemType, itemId) {
  const response = await fetch("/api/bridge/delete", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ type: itemType, id: itemId }),
  });
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || "Fehler beim Löschen");
  return result;
}

/**
 * Speichert die vollständige Konfiguration.
 * @param {Object} config - Das zu speichernde Konfigurationsobjekt.
 * @returns {Promise<Object>} Die Antwort vom Server.
 */
export async function saveFullConfig(config) {
  const response = await fetch("/api/config", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(config),
  });
  const result = await response.json();
  if (!response.ok)
    throw new Error(result.error || "Unbekannter Fehler beim Speichern");
  return result;
}

/**
 * Holt den aktuellen Status und die Log-Datei.
 * @returns {Promise<Object>} Ein Objekt mit `statusData` und `logText`.
 */
export async function updateStatus() {
  const [statusRes, logRes] = await Promise.all([
    fetch("/api/status"),
    fetch("/api/log"),
  ]);
  return {
    statusData: await statusRes.json(),
    logText: await logRes.text(),
  };
}

/**
 * Holt historische Daten für die Analyse-Diagramme.
 * @param {number} sensorId - Die ID des Sensors.
 * @param {string} period - Der Zeitraum ('day' oder 'week').
 * @param {string} date - Das Datum (für Wochenansicht).
 * @param {number} range - Der Zeitraum in Stunden (für Tagesansicht).
 * @param {number} avg - Das Fenster für den gleitenden Mittelwert.
 * @returns {Promise<Object>} Die Diagrammdaten.
 */
export async function loadChartData(sensorId, period, date, range, avg) {
  const response = await fetch(
    `/api/data/history?sensor_id=${sensorId}&period=${period}&date=${date}&range=${range}&avg=${avg}`
  );
  if (!response.ok) {
    const err = await response.json();
    throw new Error(err.error || "Daten konnten nicht geladen werden.");
  }
  const data = await response.json();
  if (data.error) throw new Error(data.error);
  return data;
}

/**
 * Holt den Inhalt der Hilfeseite.
 * @returns {Promise<string>} Der HTML-Inhalt der Hilfeseite.
 */
export async function loadHelpContent() {
  const response = await fetch("/api/help");
  if (!response.ok) throw new Error(`Server-Fehler: ${response.statusText}`);
  const data = await response.json();
  if (!data.content) throw new Error("Hilfe-Inhalt ist leer oder fehlerhaft.");
  return data.content;
}

/**
 * Führt eine Systemaktion auf dem Server aus.
 * @param {string} url - Der API-Endpunkt.
 * @param {string} confirmMsg - Die Bestätigungsnachricht für den Benutzer.
 * @returns {Promise<Object|null>} Die Server-Antwort oder null bei Abbruch.
 */
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
