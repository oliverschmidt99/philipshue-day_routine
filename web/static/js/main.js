// web/static/js/main.js
import * as api from "./modules/api.js";
import * as ui from "./modules/ui.js";
import { runSetupWizard } from "./modules/setup.js";

document.addEventListener("DOMContentLoaded", async () => {
  try {
    const status = await api.checkSetupStatus();
    if (status.setup_needed) {
      document.getElementById("main-app").classList.add("hidden");
      document.getElementById("setup-wizard").classList.remove("hidden");
      runSetupWizard();
    } else {
      document.getElementById("setup-wizard").classList.add("hidden");
      document.getElementById("main-app").classList.remove("hidden");
      runMainApp();
    }
  } catch (error) {
    document.body.innerHTML = `<div class="p-4 m-4 text-center text-red-800 bg-red-100 rounded-lg"><h2 class="text-xl font-bold">Verbindung zum Server fehlgeschlagen</h2><p>Das Backend (main.py) scheint nicht zu laufen. Bitte starte es und lade die Seite neu.</p></div>`;
    console.error("Fehler bei der Initialisierung:", error);
  }
});

function runMainApp() {
  let config = {};
  let bridgeData = {};
  let colorPicker = null;
  let statusInterval;
  let chartInstance = null;

  const init = async () => {
    ui.updateClock();
    setInterval(ui.updateClock, 1000);
    try {
      [config, bridgeData] = await Promise.all([
        api.loadConfig(),
        api.loadBridgeData(),
      ]);
      renderAll();
      setupEventListeners();
    } catch (error) {
      ui.showToast(`Initialisierungsfehler: ${error.message}`, true);
      console.error(error);
    }
  };

  const renderAll = () => {
    ui.renderRoutines(config, bridgeData);
    ui.renderScenes(config.scenes);
  };

  const setupEventListeners = () => {
    const addListener = (id, event, handler) => {
      document.getElementById(id)?.addEventListener(event, handler);
    };

    addListener("save-button", "click", saveFullConfig);
    addListener("btn-new-routine", "click", () =>
      ui.openCreateRoutineModal(bridgeData)
    );
    addListener("btn-new-scene", "click", () => {
      colorPicker = ui.openSceneModal(
        { status: true, bri: 128, ct: 366 },
        null
      );
    });

    addListener("btn-refresh-status", "click", () => updateStatus(true));
    addListener("btn-add-default-scenes", "click", async () => {
      try {
        const result = await api.addDefaultScenes();
        ui.showToast(result.message);
        // Lade die Konfiguration neu, um die neuen Szenen anzuzeigen
        config = await api.loadConfig();
        renderAll();
      } catch (error) {
        ui.showToast(error.message, true);
      }
    });

    document.body.addEventListener("click", (e) => {
      const button = e.target.closest("[data-action]");
      if (!button) return;

      e.stopPropagation();
      const action = button.dataset.action;
      const routineCard = e.target.closest("[data-index]");
      const sceneCard = e.target.closest("[data-name]");

      const actions = {
        "toggle-routine-details": () => {
          /* ... Logik ... */
        },
        "delete-scene": () => {
          if (confirm(`Szene "${sceneCard.dataset.name}" wirklich löschen?`)) {
            delete config.scenes[sceneCard.dataset.name];
            renderAll();
            ui.showToast("Szene gelöscht. Speichern nicht vergessen.", false);
          }
        },
        "edit-scene": () =>
          (colorPicker = ui.openSceneModal(
            config.scenes[sceneCard.dataset.name],
            sceneCard.dataset.name
          )),
        "save-scene": handleSaveScene,
        "cancel-modal": ui.closeModal,
        // ... (weitere Aktionen)
      };

      if (actions[action]) actions[action]();
    });

    // Tab-Navigation
    document.querySelectorAll('nav button[id^="tab-"]').forEach((button) => {
      button.addEventListener("click", () => {
        document
          .querySelectorAll('nav button[id^="tab-"]')
          .forEach((btn) => btn.classList.remove("tab-active"));
        document
          .querySelectorAll('main div[id^="content-"]')
          .forEach((content) => content.classList.add("hidden"));

        button.classList.add("tab-active");
        const contentId = button.id.replace("tab-", "content-");
        document.getElementById(contentId)?.classList.remove("hidden");

        // Tab-spezifische Initialisierungen
        if (contentId === "content-status") startStatusUpdates();
        else clearInterval(statusInterval);

        if (contentId === "content-analyse") setupAnalyseTab();
        if (contentId === "content-bridge-devices") setupBridgeDevicesTab();
      });
    });
  };

  const saveFullConfig = async () => {
    // ... (Implementierung wie zuvor)
  };

  const handleSaveScene = () => {
    // ... (Implementierung wie zuvor)
  };

  const updateStatus = async (showToast = false) => {
    try {
      const { statusData, logText } = await api.updateStatus();
      ui.renderStatus(statusData.routines, statusData.sun_times);
      ui.renderLog(logText);
      if (showToast) ui.showToast("Status aktualisiert!");
    } catch (error) {
      if (showToast) ui.showToast(error.message, true);
    }
  };

  const startStatusUpdates = () => {
    updateStatus();
    statusInterval = setInterval(updateStatus, 5000);
  };

  const setupAnalyseTab = () => {
    ui.populateAnalyseSensors(bridgeData.sensors);
    document
      .getElementById("btn-fetch-data")
      ?.addEventListener("click", loadChartData);
  };

  const loadChartData = async () => {
    const sensorId = document.getElementById("analyse-sensor").value;
    const date = document.getElementById("analyse-day-picker").value;
    if (!sensorId || !date) return;

    try {
      const data = await api.loadChartData(sensorId, date);
      chartInstance = ui.renderChart(chartInstance, data);
    } catch (error) {
      ui.showToast(error.message, true);
    }
  };

  const setupBridgeDevicesTab = async () => {
    try {
      const items = await api.loadBridgeItems();
      ui.renderBridgeDevices(items);
    } catch (error) {
      ui.showToast(error.message, true);
    }
  };

  init();
}
