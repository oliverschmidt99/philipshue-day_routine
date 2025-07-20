/**
 * Holt den Setup-Status vom Server.
 * @returns {Promise<Object>} Ein Promise, das ein Objekt mit { setup_needed: boolean } zurückgibt.
 */
export async function checkSetupStatus() {
    const response = await fetch('/api/setup/status');
    return response.json();
}

/**
 * Sucht nach Hue Bridges im Netzwerk.
 * @returns {Promise<Array<string>>} Ein Promise, das eine Liste von IP-Adressen zurückgibt.
 */
export async function discoverBridges() {
    const response = await fetch('/api/setup/discover');
    return response.json();
}

/**
 * Versucht, eine Verbindung zur Bridge herzustellen und einen App-Key zu erhalten.
 * @param {string} ip - Die IP-Adresse der Bridge.
 * @returns {Promise<Object>} Ein Promise, das ein Objekt mit dem app_key zurückgibt.
 */
export async function connectToBridge(ip) {
    const response = await fetch('/api/setup/connect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ip: ip })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Unbekannter Verbindungsfehler');
    return data;
}

/**
 * Speichert die initiale Konfiguration.
 * @param {Object} configData - Die Konfigurationsdaten.
 * @returns {Promise<Object>} Das Ergebnis vom Server.
 */
export async function saveSetupConfig(configData) {
    const response = await fetch('/api/setup/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(configData)
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Fehler beim Speichern');
    return data;
}

/**
 * Lädt die Hauptkonfiguration.
 * @returns {Promise<Object>} Die Konfiguration als JSON-Objekt.
 */
export async function loadConfig() {
    const response = await fetch('/api/config');
    if (!response.ok) throw new Error('Konfiguration konnte nicht geladen werden');
    return response.json();
}

/**
 * Lädt Bridge-Daten (Gruppen und Sensoren).
 * @returns {Promise<Object>} Ein Objekt mit `groups` und `sensors`.
 */
export async function loadBridgeData() {
    const [groupsRes, sensorsRes] = await Promise.all([
        fetch('/api/bridge/groups'),
        fetch('/api/bridge/sensors')
    ]);
    if (!groupsRes.ok || !sensorsRes.ok) throw new Error('Bridge-Daten konnten nicht geladen werden');
    return {
        groups: await groupsRes.json(),
        sensors: await sensorsRes.json()
    };
}

/**
 * Speichert die vollständige Konfiguration.
 * @param {Object} config - Das zu speichernde Konfigurationsobjekt.
 * @returns {Promise<Object>} Die Antwort vom Server.
 */
export async function saveFullConfig(config) {
    const response = await fetch('/api/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Unbekannter Fehler beim Speichern');
    return result;
}

/**
 * Holt den aktuellen Status und die Log-Datei.
 * @returns {Promise<Object>} Ein Objekt mit `statusData` und `logText`.
 */
export async function updateStatus() {
    const [statusRes, logRes] = await Promise.all([
        fetch('/api/status'),
        fetch('/api/log')
    ]);
    return {
        statusData: await statusRes.json(),
        logText: await logRes.text()
    };
}

/**
 * Holt historische Daten für die Analyse-Diagramme.
 * @param {number} sensorId - Die ID des Sensors.
 * @param {string} period - Der Zeitraum ('day' oder 'week').
 * @param {string} date - Das Datum.
 * @returns {Promise<Object>} Die Diagrammdaten.
 */
export async function loadChartData(sensorId, period, date) {
    const response = await fetch(`/api/data/history?sensor_id=${sensorId}&period=${period}&date=${date}`);
    if (!response.ok) {
        const err = await response.json();
        throw new Error(err.error || 'Daten konnten nicht geladen werden.');
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
    const response = await fetch('/api/help');
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
        const response = await fetch(url, { method: 'POST' });
        const result = await response.json();
        if (!response.ok) throw new Error(result.error || result.message);
        return result;
    }
    return null;
}
