// web/static/js/modules/status.js
import * as api from "./api.js";
import * as ui from "./ui.js";

let statusInterval;

async function updateStatus(showNotification = false) {
  try {
    const { statusData, logText } = await api.updateStatus();
    ui.renderSunTimes(statusData.sun_times || null);
    ui.renderStatus(statusData.routines || []);
    ui.renderLog(logText);
    if (showNotification)
      ui.showToast("Status erfolgreich aktualisiert!", "success");
  } catch (error) {
    console.error("Fehler beim Abrufen des Status:", error);
    if (showNotification)
      ui.showToast("Fehler beim Aktualisieren des Status.", "error");
  }
}

function startStatusUpdates(config) {
  if (statusInterval) clearInterval(statusInterval);
  updateStatus();
  const refreshInterval =
    (config.global_settings?.status_interval_s || 5) * 1000;
  statusInterval = setInterval(() => updateStatus(false), refreshInterval);
}

export function initStatusPage(config) {
  document
    .getElementById("btn-refresh-status")
    ?.addEventListener("click", () => updateStatus(true));
  startStatusUpdates(config);
}

export function stopStatusUpdates() {
  if (statusInterval) {
    clearInterval(statusInterval);
  }
}
