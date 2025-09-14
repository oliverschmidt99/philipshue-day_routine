import * as api from "./modules/api.js";
import * as ui from "./modules/ui.js";
import { runSetupWizard } from "./modules/setup.js";

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
  let config = {};
  let bridgeData = {};
  let colorPicker = null;
  let statusInterval;
  let chartInstance = null;
  let openStatusCards = [];

  const init = async () => {
    ui.updateClock();
    setInterval(ui.updateClock, 1000);
    try {
      [config, bridgeData] = await Promise.all([
        api.loadConfig(),
        api.loadBridgeData(),
      ]);
      ui.renderSunTimes(config.sun_times);
      renderAll();
      setupEventListeners();
      document.getElementById("tab-status")?.click();
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
    document.body.addEventListener("click", handleGlobalClick);
    document
      .getElementById("devices-tabs")
      ?.addEventListener("click", handleDeviceTabClick);

    document
      .getElementById("save-button")
      ?.addEventListener("click", saveFullConfig);
    document
      .getElementById("btn-new-routine")
      ?.addEventListener("click", () => ui.openCreateRoutineModal(bridgeData));
    document.getElementById("btn-new-scene")?.addEventListener("click", () => {
      colorPicker = ui.openSceneModal(
        { status: true, bri: 128, ct: 366 },
        null
      );
    });
    document
      .getElementById("btn-refresh-status")
      ?.addEventListener("click", () => updateStatus(true));
    document
      .getElementById("btn-add-default-scenes")
      ?.addEventListener("click", addDefaultScenes);
    document
      .getElementById("btn-fetch-data")
      ?.addEventListener("click", loadChartData);
    document.querySelectorAll('nav button[id^="tab-"]').forEach((button) => {
      button.addEventListener("click", handleTabClick);
    });

    // NEU: Event Listeners für System-Aktionen
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
  };

  const handleTabClick = (e) => {
    const button = e.currentTarget;
    document.querySelectorAll('nav button[id^="tab-"]').forEach((btn) => {
      btn.classList.remove("tab-active");
      btn.classList.add("text-gray-500", "border-transparent");
    });
    document
      .querySelectorAll(".content-section")
      .forEach((content) => content.classList.add("hidden"));
    button.classList.add("tab-active");
    button.classList.remove("text-gray-500", "border-transparent");
    const contentId = button.id.replace("tab-", "content-");
    const contentElement = document.getElementById(contentId);
    if (contentElement) contentElement.classList.remove("hidden");
    clearInterval(statusInterval);
    if (contentId === "content-status") startStatusUpdates();
    if (contentId === "content-analyse") setupAnalyseTab();
    if (contentId === "content-bridge-devices") setupBridgeDevicesTab();
  };

  const handleDeviceTabClick = (e) => {
    const button = e.target.closest(".device-tab");
    if (!button) return;
    const tabId = button.dataset.tab;
    document.querySelectorAll(".device-tab").forEach((btn) => {
      btn.classList.remove("text-blue-600", "border-blue-600");
      btn.classList.add(
        "text-gray-500",
        "hover:text-gray-700",
        "hover:border-gray-300",
        "border-transparent"
      );
    });
    button.classList.add("text-blue-600", "border-blue-600");
    button.classList.remove(
      "text-gray-500",
      "hover:text-gray-700",
      "hover:border-gray-300",
      "border-transparent"
    );
    document.querySelectorAll(".device-content-pane").forEach((pane) => {
      pane.classList.add("hidden");
    });
    const contentPane = document.getElementById(`devices-content-${tabId}`);
    if (contentPane) {
      contentPane.classList.remove("hidden");
    }
  };

  const handleGlobalClick = (e) => {
    const button = e.target.closest("[data-action]");
    if (!button) return;

    if (
      e.target.closest(".modal-backdrop") &&
      !e.target.closest(".modal-backdrop > div")
    ) {
      ui.closeModal();
      return;
    }

    const action = button.dataset.action;
    const routineCard = e.target.closest("[data-index]");
    const sceneCard = e.target.closest("[data-name]");
    const statusCard = e.target.closest(".status-card");

    const actions = {
      "toggle-routine-details": () =>
        ui.toggleDetails(button.closest(".routine-header")),
      "toggle-status-details": () => {
        const cardName = statusCard.querySelector("h4")?.textContent;
        if (cardName) {
          openStatusCards = openStatusCards.includes(cardName)
            ? openStatusCards.filter((name) => name !== cardName)
            : [...openStatusCards, cardName];
          ui.toggleDetails(button.closest(".status-header"));
        }
      },
      "delete-scene": () => handleDeleteScene(sceneCard),
      "edit-scene": () => {
        const sceneName = sceneCard.dataset.name;
        colorPicker = ui.openSceneModal(config.scenes[sceneName], sceneName);
      },
      "save-scene": handleSaveScene,
      "cancel-modal": ui.closeModal,
      "create-routine": handleCreateRoutine,
      "edit-routine": () => {
        const index = routineCard.dataset.index;
        ui.openEditRoutineModal(
          config.routines[index],
          index,
          Object.keys(config.scenes),
          config.rooms,
          bridgeData.groups,
          bridgeData.sensors
        );
      },
      "save-routine": () => handleSaveRoutine(routineCard),
      "delete-routine": () => {
        const index = routineCard.dataset.index;
        if (
          confirm(`Routine "${config.routines[index].name}" wirklich löschen?`)
        ) {
          config.routines.splice(index, 1);
          renderAll();
          ui.showToast("Routine gelöscht. Speichern nicht vergessen.");
        }
      },
      "toggle-routine": (e) => {
        const index = routineCard.dataset.index;
        config.routines[index].enabled = e.target.checked;
        ui.showToast(
          `Routine ${
            e.target.checked ? "aktiviert" : "deaktiviert"
          }. Speichern nicht vergessen.`
        );
      },
    };

    if (actions[action]) {
      e.preventDefault();
      actions[action](e);
    }
  };

  const handleSaveRoutine = () => {
    const form = document.getElementById("form-routine-edit");
    const index = parseInt(form.dataset.index, 10);
    const routine = config.routines[index];

    routine.name = document.getElementById("edit-routine-name").value;
    const [groupId, groupName] = document
      .getElementById("edit-routine-group")
      .value.split("|");
    routine.room_name = groupName;

    let roomConf = config.rooms.find((r) => r.name === groupName);
    if (!roomConf) {
      if (!config.rooms) config.rooms = [];
      roomConf = { name: groupName, group_id: groupId };
      config.rooms.push(roomConf);
    }
    roomConf.sensor_id = document.getElementById("edit-routine-sensor").value;

    ["morning", "day", "evening", "night"].forEach((period) => {
      form.querySelectorAll(`[data-period="${period}"]`).forEach((input) => {
        const key = input.dataset.key;
        const value =
          input.type === "checkbox"
            ? input.checked
            : input.type === "number"
            ? parseInt(input.value)
            : input.value;

        if (key.includes(".")) {
          const [mainKey, subKey] = key.split(".");
          routine[period][mainKey][subKey] = value;
        } else {
          routine[period][key] = value;
        }
      });
    });

    renderAll();
    ui.closeModal();
    ui.showToast("Routine gespeichert. Speichern nicht vergessen.");
  };

  const handleDeleteScene = (sceneCard) => {
    const sceneName = sceneCard.dataset.name;
    if (confirm(`Szene "${sceneName}" wirklich löschen?`)) {
      delete config.scenes[sceneName];
      renderAll();
      ui.showToast("Szene gelöscht. Speichern nicht vergessen.", false);
    }
  };

  const handleCreateRoutine = () => {
    const name = document.getElementById("new-routine-name").value.trim();
    const groupSelect = document.getElementById("new-routine-group");
    const sensorSelect = document.getElementById("new-routine-sensor");

    if (!name || !groupSelect.value) {
      ui.showToast("Bitte Name und Raum auswählen.", true);
      return;
    }

    const [groupId, groupName] = groupSelect.value.split("|");

    const newRoutine = {
      name,
      room_name: groupName,
      enabled: true,
      daily_time: { H1: 7, M1: 0, H2: 23, M2: 0 },
      morning: {
        scene_name: "aus",
        x_scene_name: "entspannen",
        motion_check: true,
        wait_time: { min: 1, sec: 0 },
        do_not_disturb: false,
        bri_check: false,
      },
      day: {
        scene_name: "aus",
        x_scene_name: "konzentrieren",
        motion_check: true,
        wait_time: { min: 1, sec: 0 },
        do_not_disturb: false,
        bri_check: false,
      },
      evening: {
        scene_name: "aus",
        x_scene_name: "entspannen",
        motion_check: true,
        wait_time: { min: 1, sec: 0 },
        do_not_disturb: false,
        bri_check: false,
      },
      night: {
        scene_name: "aus",
        x_scene_name: "nachtlicht",
        motion_check: true,
        wait_time: { min: 1, sec: 0 },
        do_not_disturb: false,
        bri_check: false,
      },
    };

    if (!config.routines) config.routines = [];
    config.routines.push(newRoutine);

    let roomConf = config.rooms?.find((r) => r.name === groupName);
    if (!roomConf) {
      if (!config.rooms) config.rooms = [];
      roomConf = { name: groupName, group_ids: [groupId] };
      config.rooms.push(roomConf);
    }
    if (sensorSelect.value) {
      roomConf.sensor_id = sensorSelect.value;
    }

    renderAll();
    ui.closeModal();
    ui.showToast("Neue Routine erstellt. Speichern nicht vergessen.");
  };

  const handleSaveScene = () => {
    const originalName = document.getElementById("scene-original-name").value;
    const newName = document
      .getElementById("scene-name")
      .value.trim()
      .replace(/\s+/g, "_");
    if (!newName) {
      ui.showToast("Der Name der Szene darf nicht leer sein.", true);
      return;
    }

    const sceneData = {
      status: document.getElementById("scene-status").checked,
      bri: parseInt(document.getElementById("scene-bri").value),
      transitiontime: 10,
    };

    const colorMode = document.querySelector(
      'input[name="color-mode"]:checked'
    ).value;
    if (colorMode === "color" && colorPicker) {
      const hsv = colorPicker.color.hsv;
      sceneData.hue = Math.round((hsv.h / 360) * 65535);
      sceneData.sat = Math.round((hsv.s / 100) * 254);
    } else {
      sceneData.ct = parseInt(document.getElementById("scene-ct").value);
    }

    if (originalName && originalName !== newName) {
      delete config.scenes[originalName];
    }
    config.scenes[newName] = sceneData;

    renderAll();
    ui.closeModal();
    ui.showToast("Szene gespeichert. Speichern nicht vergessen.", false);
  };

  const saveFullConfig = async () => {
    try {
      const saveButton = document.getElementById("save-button");
      saveButton.disabled = true;
      saveButton.textContent = "Speichern...";
      const result = await api.saveFullConfig(config);
      ui.showToast(result.message);
      config = await api.loadConfig();
      renderAll();
    } catch (error) {
      ui.showToast(error.message, true);
    } finally {
      const saveButton = document.getElementById("save-button");
      saveButton.disabled = false;
      saveButton.textContent = "Speichern und Alle Routinen neu starten";
    }
  };

  const addDefaultScenes = async () => {
    try {
      const result = await api.addDefaultScenes();
      ui.showToast(result.message);
      config = await api.loadConfig();
      renderAll();
    } catch (error) {
      ui.showToast(error.message, true);
    }
  };

  const updateStatus = async (showToast = false) => {
    try {
      const { statusData, logText } = await api.updateStatus();
      ui.renderStatus(
        statusData.routines,
        statusData.sun_times,
        openStatusCards
      );
      ui.renderLog(logText);
      ui.updateStatusTimelines();
      if (showToast) ui.showToast("Status aktualisiert!");
    } catch (error) {
      if (showToast)
        ui.showToast(`Status-Update fehlgeschlagen: ${error.message}`, true);
    }
  };

  // NEUE HANDLER FÜR SYSTEM-AKTIONEN
  const handleUpdateApp = async () => {
    if (
      confirm(
        "Möchtest du die Anwendung wirklich via 'git pull' aktualisieren?"
      )
    ) {
      try {
        const result = await api.updateApp();
        ui.showToast(result.message);
        setTimeout(() => window.location.reload(), 2000);
      } catch (error) {
        ui.showToast(error.message, true);
      }
    }
  };

  const handleRestartApp = async () => {
    if (confirm("Möchtest du die Anwendung wirklich neu starten?")) {
      try {
        const result = await api.restartApp();
        ui.showToast(
          result.message + " Die Seite wird in 5 Sekunden neu geladen."
        );
        setTimeout(() => window.location.reload(), 5000);
      } catch (error) {
        ui.showToast(error.message, true);
      }
    }
  };

  const handleBackupConfig = async () => {
    try {
      const result = await api.backupConfig();
      ui.showToast(result.message);
    } catch (error) {
      ui.showToast(error.message, true);
    }
  };

  const handleRestoreConfig = async () => {
    if (
      confirm(
        "Möchtest du die Konfiguration wirklich aus dem letzten Backup wiederherstellen? Nicht gespeicherte Änderungen gehen verloren."
      )
    ) {
      try {
        const result = await api.restoreConfig();
        ui.showToast(result.message + " Die Seite wird neu geladen.");
        setTimeout(() => window.location.reload(), 2000);
      } catch (error) {
        ui.showToast(error.message, true);
      }
    }
  };

  const startStatusUpdates = () => {
    updateStatus();
    const statusIntervalTime =
      (config?.global_settings?.status_interval_s || 5) * 1000;
    statusInterval = setInterval(updateStatus, statusIntervalTime);
  };

  const setupAnalyseTab = () => {
    ui.populateAnalyseSensors(bridgeData.sensors);
    const today = new Date().toISOString().split("T")[0];
    document.getElementById("analyse-day-picker").value = today;
  };

  const loadChartData = async () => {
    const sensorId = document.getElementById("analyse-sensor").value;
    const date = document.getElementById("analyse-day-picker").value;
    if (!sensorId || !date) {
      ui.showToast("Bitte einen Sensor und ein Datum auswählen.", true);
      return;
    }

    const button = document.getElementById("btn-fetch-data");
    button.disabled = true;
    button.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Lade...';

    try {
      const data = await api.loadChartData(sensorId, date);
      chartInstance = ui.renderChart(chartInstance, data);
    } catch (error) {
      ui.showToast(error.message, true);
      chartInstance = ui.renderChart(chartInstance, null);
    } finally {
      button.disabled = false;
      button.innerHTML = '<i class="fas fa-sync-alt mr-2"></i>Daten laden';
    }
  };

  const setupBridgeDevicesTab = () => {
    ui.renderBridgeDevices(bridgeData);
  };

  await init();
}
