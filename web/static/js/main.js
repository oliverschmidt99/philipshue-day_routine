import * as api from "./api.js";
import {
  showToast,
  updateClock,
  renderSunTimes,
} from "./components/helpers.js";
import { initRoutines, renderRoutines } from "./components/routines.js";
import { initScenes, renderScenes } from "./components/scenes.js";
import { initStatus } from "./components/status.js";
import { initAnalyse } from "./components/analyse.js";
import { initSettings } from "./components/settings.js";
import { initDevices } from "./components/devices.js";
import { runSetupWizard } from "./setup.js";

document.addEventListener("DOMContentLoaded", async () => {
  try {
    const status = await api.checkSetupStatus();
    if (status.setup_needed) {
      document.getElementById("main-app")?.classList.add("hidden");
      document.getElementById("setup-wizard")?.classList.remove("hidden");
      runSetupWizard();
    } else {
      document.getElementById("setup-wizard")?.classList.add("hidden");
      document.getElementById("main-app")?.classList.remove("hidden");
      await runMainApp();
    }
  } catch (error) {
    document.body.innerHTML = `<div class="p-4 m-4 text-center text-red-800 bg-red-100 rounded-lg"><h2 class="text-xl font-bold">Verbindung zum Server fehlgeschlagen</h2><p>Das Backend (main.py) scheint nicht zu laufen oder ist nicht erreichbar. Bitte starte es und lade die Seite neu.</p><p class="mt-2 text-sm text-gray-600">Fehler: ${error.message}</p></div>`;
    console.error("Fehler bei der Initialisierung:", error);
  }
});

async function runMainApp() {
  let state = {
    config: {},
    bridgeData: {},
  };

  const loadData = async () => {
    try {
      const [config, bridgeData] = await Promise.all([
        api.loadConfig(),
        api.loadBridgeData(),
      ]);
      state.config = config;
      state.bridgeData = bridgeData;
    } catch (error) {
      showToast(`Daten konnten nicht geladen werden: ${error.message}`, true);
    }
  };

  const renderAll = () => {
    renderRoutines(state);
    renderScenes(state);
  };

  const handleSave = async () => {
    try {
      const saveButton = document.getElementById("save-button");
      saveButton.disabled = true;
      saveButton.textContent = "Speichern...";
      const result = await api.saveFullConfig(state.config);
      showToast(result.message);
      await loadData(); // Lade die Konfiguration neu, um synchron zu bleiben
      renderAll();
    } catch (error) {
      showToast(error.message, true);
    } finally {
      const saveButton = document.getElementById("save-button");
      saveButton.disabled = false;
      saveButton.textContent = "Speichern und Alle Routinen neu starten";
    }
  };

  await loadData();
  updateClock();
  setInterval(updateClock, 1000);
  renderSunTimes(state.config.sun_times);

  // Initialisiere alle Komponenten-Module
  initRoutines(state, renderAll);
  initScenes(state, renderAll);
  initStatus(state);
  initAnalyse(state);
  initSettings(state, renderAll);
  initDevices(state);

  document.getElementById("save-button").addEventListener("click", handleSave);

  // Tab-Navigation
  const tabs = [
    "routines",
    "scenes",
    "status",
    "analyse",
    "einstellungen",
    "devices",
    "hilfe",
  ];
  const tabButtons = tabs.map((id) => document.getElementById(`tab-${id}`));
  const contentPanes = tabs.map((id) =>
    document.getElementById(`content-${id}`)
  );

  tabButtons.forEach((button, index) => {
    button.addEventListener("click", () => {
      tabButtons.forEach((btn) => btn.classList.remove("tab-active"));
      contentPanes.forEach((pane) => pane.classList.add("hidden"));

      button.classList.add("tab-active");
      contentPanes[index].classList.remove("hidden");

      const tabId = tabs[index];
      if (tabId === "status")
        document.dispatchEvent(new Event("tabchanged_status"));
      if (tabId === "devices")
        document.dispatchEvent(new Event("tabchanged_devices"));
      if (tabId === "analyse")
        document.dispatchEvent(new Event("tabchanged_analyse"));

      if (
        tabId === "hilfe" &&
        !document.getElementById("help-content-container").innerHTML
      ) {
        // Die Hilfe.html wird über einen normalen Link geladen, nicht über die API
        fetch("/hilfe")
          .then((res) => res.text())
          .then(
            (html) =>
              (document.getElementById("help-content-container").innerHTML =
                html)
          );
      }
    });
  });

  // Start-Tab
  document.getElementById("tab-routines").click();
  renderAll();
}
