import * as api from "../api.js";
import { showToast } from "./helpers.js";

let state;
let renderAll;

export function initSettings(appState, renderCallback) {
  state = appState;
  renderAll = renderCallback;

  document
    .getElementById("btn-update-app")
    ?.addEventListener("click", handleUpdateApp);
  document
    .getElementById("btn-restart-app")
    ?.addEventListener("click", handleRestartApp);
  document
    .getElementById("btn-backup-config")
    ?.addEventListener("click", handleBackupConfig);
  document
    .getElementById("btn-restore-config")
    ?.addEventListener("click", handleRestoreConfig);
  document
    .getElementById("btn-add-default-scenes")
    ?.addEventListener("click", handleAddDefaultScenes);
}

async function handleUpdateApp() {
  if (
    confirm("Möchtest du die Anwendung wirklich via 'git pull' aktualisieren?")
  ) {
    try {
      showToast("Update wird ausgeführt...");
      const result = await api.updateApp();
      showToast(result.message, false);
      setTimeout(() => window.location.reload(), 3000);
    } catch (error) {
      showToast(error.message, true);
    }
  }
}

async function handleRestartApp() {
  if (confirm("Möchtest du die Anwendung wirklich neu starten?")) {
    try {
      await api.restartApp();
      showToast(
        "Neustart-Signal gesendet. Seite wird in 5 Sekunden neu geladen."
      );
      setTimeout(() => window.location.reload(), 5000);
    } catch (error) {
      showToast(error.message, true);
    }
  }
}

async function handleBackupConfig() {
  try {
    const result = await api.backupConfig();
    showToast(result.message);
  } catch (error) {
    showToast(error.message, true);
  }
}

async function handleRestoreConfig() {
  if (
    confirm(
      "Sicher, dass du die Konfiguration aus dem Backup wiederherstellen möchtest?"
    )
  ) {
    try {
      const result = await api.restoreConfig();
      showToast(result.message);
      setTimeout(() => window.location.reload(), 2000);
    } catch (error) {
      showToast(error.message, true);
    }
  }
}

async function handleAddDefaultScenes() {
  try {
    const result = await api.addDefaultScenes();
    showToast(result.message);
    const newConfig = await api.loadConfig();
    state.config = newConfig;
    renderAll();
  } catch (error) {
    showToast(error.message, true);
  }
}
