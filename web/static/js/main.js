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

  const renderSettings = (config) => {
    const bridgeIpEl = document.getElementById("setting-bridge-ip");
    if (bridgeIpEl) bridgeIpEl.value = config.bridge_ip || "";

    if (config.location) {
      const latEl = document.getElementById("setting-latitude");
      if (latEl) latEl.value = config.location.latitude || "";
      const lonEl = document.getElementById("setting-longitude");
      if (lonEl) lonEl.value = config.location.longitude || "";
    }

    if (config.global_settings) {
      const hysteresisEl = document.getElementById("setting-hysteresis");
      if (hysteresisEl)
        hysteresisEl.value = config.global_settings.hysteresis_percent || 25;
      const dataloggerEl = document.getElementById(
        "setting-datalogger-interval"
      );
      if (dataloggerEl)
        dataloggerEl.value =
          config.global_settings.datalogger_interval_minutes || 15;
      const loopEl = document.getElementById("setting-loop-interval");
      if (loopEl) loopEl.value = config.global_settings.loop_interval_s || 1;
      const statusEl = document.getElementById("setting-status-interval");
      if (statusEl)
        statusEl.value = config.global_settings.status_interval_s || 5;
      const logEl = document.getElementById("setting-loglevel");
      if (logEl) logEl.value = config.global_settings.log_level || "INFO";
    }
  };

  const renderAll = () => {
    ui.renderRoutines(config, bridgeData);
    ui.renderScenes(config.scenes);
    renderSettings(config);
    document.querySelectorAll(".routine-details[data-index]").forEach((el) => {
      const index = parseInt(el.dataset.index, 10);
      const routine = config.routines[index];
      if (routine) {
        el.innerHTML = ui.renderRoutineDetails(routine, config.scenes);
      }
    });
  };

  const setupEventListeners = () => {
    document.body.addEventListener("click", handleGlobalClick);
    document
      .getElementById("bridge-devices-tabs")
      ?.addEventListener("click", handleBridgeDeviceTabClick);
    document.body.addEventListener("input", handleGlobalInput);
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
  };

  const handleGlobalInput = (e) => {
    const input = e.target;
    const routineDetails = input.closest(".routine-details");
    if (!routineDetails) return;

    const index = parseInt(routineDetails.dataset.index, 10);
    const routine = config.routines[index];
    const period = input.dataset.period;
    const key = input.dataset.key;
    const value =
      input.type === "checkbox"
        ? input.checked
        : input.type.startsWith("time") ||
          input.type.startsWith("range") ||
          input.type.startsWith("number")
        ? input.valueAsNumber || 0
        : input.value;

    if (routine && period && key) {
      if (period === "daily_time") {
        routine.daily_time[key] = value;
      } else if (key.startsWith("wait_time")) {
        const subkey = key.split(".")[1];
        routine[period].wait_time[subkey] = value;
      } else {
        routine[period][key] = value;
      }
    }
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
    if (contentId === "content-hilfe") loadHelpContent();
    if (contentId === "content-bridge-devices") setupBridgeDevicesTab();
  };

  const handleBridgeDeviceTabClick = (e) => {
    const button = e.target.closest(".bridge-device-tab");
    if (!button) return;
    const tabId = button.dataset.tab;
    document.querySelectorAll(".bridge-device-tab").forEach((btn) => {
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
    document.querySelectorAll(".bridge-device-content-pane").forEach((pane) => {
      pane.classList.add("hidden");
    });
    const contentPane = document.getElementById(`bridge-content-${tabId}`);
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
        document.getElementById("tab-routines").click();
        setTimeout(() => {
          const header = document.querySelector(
            `.routine-header[data-index='${index}']`
          );
          if (header) {
            ui.toggleDetails(header, true);
            header.scrollIntoView({ behavior: "smooth", block: "center" });
          }
        }, 100);
      },
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
      "stop-propagation": (e) => e.stopPropagation(),
    };

    if (actions[action]) {
      e.preventDefault();
      actions[action](e);
    }
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

  const loadHelpContent = async () => {
    const container = document.getElementById("help-content-container");
    if (container && !container.innerHTML) {
      try {
        const response = await fetch("/hilfe");
        if (response.ok) {
          container.innerHTML = await response.text();
        } else {
          container.innerHTML = "<p>Hilfe konnte nicht geladen werden.</p>";
        }
      } catch (error) {
        container.innerHTML = "<p>Fehler beim Laden der Hilfe.</p>";
      }
    }
  };

  const setupBridgeDevicesTab = () => {
    ui.renderBridgeDevices(bridgeData);
  };

  await init();
}
