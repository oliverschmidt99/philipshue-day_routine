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
      document.getElementById("setup-wizard").classList.add("flex");
      runSetupWizard();
    } else {
      document.getElementById("setup-wizard").classList.add("hidden");
      document.getElementById("main-app").classList.remove("hidden");
      runMainApp();
    }
  } catch (error) {
    document.body.innerHTML = `<div class="m-4 p-4 text-center text-red-800 bg-red-100 rounded-lg shadow-md"><h2 class="text-xl font-bold">Verbindung zum Server fehlgeschlagen</h2><p class="mt-2">Das Backend (main.py) läuft nicht. Bitte starte es und lade die Seite neu.</p></div>`;
  }
});

function runMainApp() {
  let config = {};
  let bridgeData = {};
  let colorPicker = null;
  let statusInterval;
  let chartInstance = null;
  let clockAnimationInterval;

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
    ui.renderRoutines(config.routines);
    ui.renderScenes(config.scenes);
  };

  const setupEventListeners = () => {
    const addListener = (id, event, handler) => {
      const element = document.getElementById(id);
      if (element) {
        element.addEventListener(event, handler);
      } else {
        console.warn(
          `Element with ID '${id}' not found. Cannot attach event listener.`
        );
      }
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

    addListener("btn-update-app", "click", () => {
      api.systemAction(
        "/api/system/update_app",
        "Möchtest du die Anwendung wirklich via 'git pull' aktualisieren?"
      );
    });
    addListener("btn-restart-app", "click", () => {
      api.systemAction(
        "/api/system/restart",
        "Möchtest du die Anwendung wirklich neu starten?"
      );
    });
    addListener("btn-backup-config", "click", () => {
      api.systemAction(
        "/api/config/backup",
        "Möchtest du die aktuelle Konfiguration sichern?"
      );
    });
    addListener("btn-restore-config", "click", () => {
      api.systemAction(
        "/api/config/restore",
        "Möchtest du die Konfiguration aus dem Backup wiederherstellen? Ungespeicherte Änderungen gehen verloren."
      );
    });
    addListener("btn-add-default-scenes", "click", () => {
      api.systemAction(
        "/api/scenes/add_defaults",
        "Möchtest du die Standard-Szenen hinzufügen oder aktualisieren? Deine eigenen Szenen bleiben erhalten."
      );
    });

    document.body.addEventListener("click", (e) => {
      const button = e.target.closest("[data-action]");
      if (!button) return;
      const action = button.dataset.action;
      const routineCard = e.target.closest("[data-index]");
      const sceneCard = e.target.closest("[data-name]");
      const actions = {
        "toggle-routine": () => {
          config.routines[routineCard.dataset.index].enabled = button.checked;
          ui.showToast(
            `Routine ${
              button.checked ? "aktiviert" : "deaktiviert"
            }. Speichern nicht vergessen!`
          );
        },
        "delete-scene": () => {
          if (confirm(`Szene "${sceneCard.dataset.name}" löschen?`)) {
            delete config.scenes[sceneCard.dataset.name];
            renderAll();
          }
        },
        "delete-routine": () => {
          if (
            confirm(
              `Routine "${
                config.routines[routineCard.dataset.index].name
              }" löschen?`
            )
          ) {
            config.routines.splice(routineCard.dataset.index, 1);
            renderAll();
          }
        },
        "edit-scene": () =>
          (colorPicker = ui.openSceneModal(
            config.scenes[sceneCard.dataset.name],
            sceneCard.dataset.name
          )),
        "edit-routine": () =>
          ui.openEditRoutineModal(
            config.routines[routineCard.dataset.index],
            routineCard.dataset.index,
            Object.keys(config.scenes),
            config.rooms,
            bridgeData.sensors // Sensorliste übergeben
          ),
        "save-scene": handleSaveScene,
        "save-routine": handleSaveEditedRoutine,
        "create-routine": handleCreateNewRoutine,
        "cancel-modal": ui.closeModal,
      };
      if (actions[action]) actions[action]();
    });

    const tabs = [
      { btn: "tab-routines", content: "content-routines" },
      { btn: "tab-scenes", content: "content-scenes" },
      {
        btn: "tab-status",
        content: "content-status",
        init: startStatusUpdates,
      },
      { btn: "tab-analyse", content: "content-analyse", init: setupAnalyseTab },
      {
        btn: "tab-einstellungen",
        content: "content-einstellungen",
        init: loadSettings,
      },
      { btn: "tab-hilfe", content: "content-hilfe", init: loadHelp },
    ];
    tabs.forEach((tabInfo) => {
      const btn = document.getElementById(tabInfo.btn);
      if (btn) {
        btn.addEventListener("click", () => {
          tabs.forEach((t) => {
            document.getElementById(t.btn)?.classList.remove("tab-active");
            document.getElementById(t.content)?.classList.add("hidden");
          });
          btn.classList.add("tab-active");
          document.getElementById(tabInfo.content)?.classList.remove("hidden");
          if (statusInterval) clearInterval(statusInterval);
          if (clockAnimationInterval) clearInterval(clockAnimationInterval);
          if (tabInfo.init) tabInfo.init();
        });
      }
    });
  };

  const updateStatus = async () => {
    try {
      const { statusData, logText } = await api.updateStatus();
      console.log("Empfangene Status-Daten:", statusData);
      ui.renderSunTimes(statusData.sun_times || null);
      ui.renderStatus(statusData.routines || [], statusData.sun_times);
      ui.renderLog(logText);
      animateTimeIndicators();
    } catch (error) {
      console.error("Fehler beim Abrufen des Status:", error);
    }
  };

  const animateTimeIndicators = () => {
    const now = new Date();
    const nowMins = now.getHours() * 60 + now.getMinutes();
    document.querySelectorAll(".sun-emoji-indicator").forEach((sun) => {
      const svg = sun.closest(".timeline-svg");
      if (!svg) return;
      const sunriseMins = parseInt(sun.dataset.sunriseMins);
      const sunsetMins = parseInt(sun.dataset.sunsetMins);
      if (nowMins >= sunriseMins && nowMins <= sunsetMins) {
        sun.style.display = "block";
        const dayDuration = sunsetMins - sunriseMins;
        const timeIntoDay = nowMins - sunriseMins;
        const progress = dayDuration > 0 ? timeIntoDay / dayDuration : 0;
        const arcStartX = parseFloat(svg.dataset.arcStartX);
        const arcEndX = parseFloat(svg.dataset.arcEndX);
        const centerX = parseFloat(svg.dataset.centerX);
        const arcRadiusX = parseFloat(svg.dataset.radiusX);
        const arcRadiusY = parseFloat(svg.dataset.radiusY);
        const sunX = arcStartX + progress * (arcEndX - arcStartX);
        let term = 1 - Math.pow(sunX - centerX, 2) / Math.pow(arcRadiusX, 2);
        term = Math.max(0, term);
        const sunY = 180 - arcRadiusY * Math.sqrt(term);
        sun.setAttribute("transform", `translate(${sunX}, ${sunY})`);
      } else {
        sun.style.display = "none";
      }
    });
  };

  const startStatusUpdates = () => {
    if (statusInterval) clearInterval(statusInterval);
    if (clockAnimationInterval) clearInterval(clockAnimationInterval);
    updateStatus();
    const refreshInterval =
      (config.global_settings?.status_interval_s || 5) * 1000;
    statusInterval = setInterval(updateStatus, refreshInterval);
    animateTimeIndicators();
    clockAnimationInterval = setInterval(animateTimeIndicators, 60 * 1000);
  };

  const setupAnalyseTab = () => {
    ui.populateAnalyseSensors(bridgeData.sensors);
    const periodSelect = document.getElementById("analyse-period");
    const dayOptions = document.getElementById("day-options");
    const weekOptions = document.getElementById("week-options");
    const dayPicker = document.getElementById("analyse-day-picker");
    const weekPicker = document.getElementById("analyse-week-picker");
    dayPicker.value = new Date().toISOString().split("T")[0];
    const getWeekNumber = (d) => {
      d = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()));
      d.setUTCDate(d.getUTCDate() + 4 - (d.getUTCDay() || 7));
      const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
      const weekNo = Math.ceil(((d - yearStart) / 86400000 + 1) / 7);
      return [d.getUTCFullYear(), weekNo];
    };
    const [year, weekNo] = getWeekNumber(new Date());
    weekPicker.value = `${year}-W${String(weekNo).padStart(2, "0")}`;
    const togglePeriodView = () => {
      const isWeek = periodSelect.value === "week";
      dayOptions.classList.toggle("hidden", isWeek);
      weekOptions.classList.toggle("hidden", !isWeek);
    };
    periodSelect.addEventListener("change", togglePeriodView);
    togglePeriodView();
    document
      .getElementById("btn-fetch-data")
      .addEventListener("click", loadChartData);
    if (bridgeData.sensors && bridgeData.sensors.length > 0) {
      loadChartData();
    }
  };

  const loadChartData = async () => {
    const sensorId = document.getElementById("analyse-sensor").value;
    const period = document.getElementById("analyse-period").value;
    const avgWindow = document.getElementById("analyse-avg-window").value;
    let date;
    if (period === "week") {
      const weekPicker = document.getElementById("analyse-week-picker");
      if (weekPicker.value) {
        const [year, weekNum] = weekPicker.value.split("-W");
        const d = new Date(Date.UTC(year, 0, 1 + (weekNum - 1) * 7));
        d.setUTCDate(d.getUTCDate() - (d.getUTCDay() || 7) + 1);
        date = d.toISOString().split("T")[0];
      }
    } else {
      date = document.getElementById("analyse-day-picker").value;
    }
    if (!sensorId) {
      ui.showToast("Bitte einen Sensor auswählen.", true);
      return;
    }
    if (!date) {
      ui.showToast("Bitte ein Datum auswählen.", true);
      return;
    }
    try {
      const data = await api.loadChartData(
        sensorId,
        period,
        date,
        null,
        avgWindow
      );
      chartInstance = ui.renderChart(chartInstance, data, period);
    } catch (error) {
      ui.showToast(error.message, true);
    }
  };

  const loadHelp = async () => {
    const helpContainer = document.getElementById("help-content-container");
    try {
      const content = await api.loadHelpContent();
      helpContainer.innerHTML = content;
      helpContainer.querySelectorAll(".faq-question").forEach((btn) => {
        btn.addEventListener("click", () => {
          const answer = btn.nextElementSibling;
          const icon = btn.querySelector("i");
          const isOpening = !answer.style.maxHeight;
          answer.style.maxHeight = isOpening
            ? answer.scrollHeight + "px"
            : null;
          icon.style.transform = isOpening ? "rotate(180deg)" : "rotate(0deg)";
        });
      });
    } catch (e) {
      helpContainer.innerHTML = `<p class="text-red-500">Hilfe konnte nicht geladen werden.</p>`;
    }
  };

  const loadSettings = () => {
    const settings = config.global_settings || {};
    const location = config.location || {};
    document.getElementById("setting-bridge-ip").value = config.bridge_ip || "";
    document.getElementById("setting-latitude").value = location.latitude || "";
    document.getElementById("setting-longitude").value =
      location.longitude || "";
    document.getElementById("setting-hysteresis").value =
      settings.hysteresis_percent || 25;
    document.getElementById("setting-datalogger-interval").value =
      settings.datalogger_interval_minutes || 15;
    document.getElementById("setting-loop-interval").value =
      settings.loop_interval_s || 1;
    document.getElementById("setting-status-interval").value =
      settings.status_interval_s || 5;
    document.getElementById("setting-loglevel").value =
      settings.log_level || "INFO";
  };

  const saveFullConfig = async () => {
    const settings = config.global_settings || {};
    settings.hysteresis_percent = parseInt(
      document.getElementById("setting-hysteresis").value
    );
    settings.datalogger_interval_minutes = parseInt(
      document.getElementById("setting-datalogger-interval").value
    );
    settings.loop_interval_s = parseFloat(
      document.getElementById("setting-loop-interval").value
    );
    settings.status_interval_s = parseInt(
      document.getElementById("setting-status-interval").value
    );
    settings.log_level = document.getElementById("setting-loglevel").value;
    config.global_settings = settings;
    config.bridge_ip = document.getElementById("setting-bridge-ip").value;
    config.location = {
      latitude: parseFloat(document.getElementById("setting-latitude").value),
      longitude: parseFloat(document.getElementById("setting-longitude").value),
    };
    const btn = document.getElementById("save-button");
    btn.disabled = true;
    btn.textContent = "Speichere...";
    try {
      await api.saveFullConfig(config);
      ui.showToast("Konfiguration gespeichert & neu gestartet!");
    } catch (error) {
      ui.showToast(`Fehler: ${error.message}`, true);
    } finally {
      btn.disabled = false;
      btn.textContent = "Speichern und Alle Routinen neu starten";
    }
  };

  const handleSaveScene = () => {
    const form = document.getElementById("form-scene");
    const originalName = form.querySelector("#scene-original-name").value;
    const newName = form
      .querySelector("#scene-name")
      .value.trim()
      .replace(/\s+/g, "_")
      .toLowerCase();
    if (!newName) return ui.showToast("Name fehlt.", true);
    const newScene = {
      status: form.querySelector("#scene-status").checked,
      bri: parseInt(form.querySelector("#scene-bri").value),
    };
    if (
      form.querySelector('input[name="color-mode"]:checked').value ===
        "color" &&
      colorPicker
    ) {
      const hsv = colorPicker.color.hsv;
      newScene.hue = Math.round((hsv.h / 360) * 65535);
      newScene.sat = Math.round((hsv.s / 100) * 254);
    } else {
      newScene.ct = parseInt(form.querySelector("#scene-ct").value);
    }
    if (originalName && originalName !== newName)
      delete config.scenes[originalName];
    config.scenes[newName] = newScene;
    renderAll();
    ui.closeModal();
  };

  const handleCreateNewRoutine = () => {
    const name = document.getElementById("new-routine-name").value;
    const [groupId, groupName] = document
      .getElementById("new-routine-group")
      .value.split("|");
    const sensorId = document.getElementById("new-routine-sensor").value;
    if (!name || !groupId) return ui.showToast("Name oder Raum fehlt.", true);
    const newRoutine = {
      name,
      room_name: groupName,
      enabled: true,
      daily_time: { H1: 7, M1: 0, H2: 23, M2: 0 },
      ...Object.fromEntries(
        ["morning", "day", "evening", "night"].map((p) => [
          p,
          { scene_name: "off", x_scene_name: "off" },
        ])
      ),
    };
    if (!config.routines) config.routines = [];
    config.routines.push(newRoutine);
    if (!config.rooms) config.rooms = [];
    if (!config.rooms.some((r) => r.name === groupName)) {
      config.rooms.push({
        name: groupName,
        group_ids: [parseInt(groupId)],
        sensor_id: sensorId ? parseInt(sensorId) : undefined,
      });
    }
    renderAll();
    ui.closeModal();
    ui.openEditRoutineModal(
      newRoutine,
      config.routines.length - 1,
      Object.keys(config.scenes),
      config.rooms,
      bridgeData.sensors
    );
  };

  const handleSaveEditedRoutine = () => {
    const modal = document.getElementById("modal-routine");
    if (!modal) return;
    const index = modal.querySelector("#routine-index").value;
    const routine = config.routines[index];
    if (!routine) return;

    const newRoomName = modal.querySelector("#routine-room-select").value;
    routine.room_name = newRoomName;

    const newSensorId = modal.querySelector("#routine-sensor-select").value;
    const roomToUpdate = config.rooms.find((r) => r.name === newRoomName);
    if (roomToUpdate) {
      roomToUpdate.sensor_id = newSensorId ? parseInt(newSensorId) : undefined;
    }

    const startMinutes = parseInt(
      modal.querySelector("#time-slider-start").value
    );
    const endMinutes = parseInt(modal.querySelector("#time-slider-end").value);
    routine.daily_time = {
      H1: Math.floor(startMinutes / 60),
      M1: startMinutes % 60,
      H2: Math.floor(endMinutes / 60),
      M2: endMinutes % 60,
    };
    modal.querySelectorAll("[data-section-name]").forEach((el) => {
      const name = el.dataset.sectionName;
      routine[name] = {
        scene_name: el.querySelector(".section-scene-name").value,
        x_scene_name: el.querySelector(".section-x-scene-name").value,
        motion_check: el.querySelector(".section-motion-check").checked,
        wait_time: {
          min: parseInt(el.querySelector(".section-wait-time-min").value) || 0,
          sec: parseInt(el.querySelector(".section-wait-time-sec").value) || 0,
        },
        do_not_disturb: el.querySelector(".section-do-not-disturb").checked,
        bri_check: el.querySelector(".section-bri-check").checked,
        max_light_level: parseInt(el.querySelector(".brightness-slider").value),
        bri_ct: parseInt(el.querySelector(".section-bri-ct").value),
      };
    });
    renderAll();
    ui.closeModal();
    ui.showToast("Routine aktualisiert. Globale Speicherung nicht vergessen!");
  };

  init();
}
