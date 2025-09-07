// web/static/js/main.js
import * as api from "./modules/api.js";
import * as ui from "./modules/ui.js";
import { runSetupWizard } from "./modules/setup.js";
import { init as initAnalyse } from "./modules/analyse.js";
import { init as initDevices } from "./modules/devices.js";

// Definiere die Template-Funktionen im globalen Scope, damit sie überall verfügbar sind.
function initializeTemplateFunctions() {
  window.showModal = (title, content, actions) => {
    const modalContainer = document.getElementById("demo-modal");
    if (!modalContainer) return;
    const modalHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>${title}</h3>
                    <button type="button" class="modal-close-btn" aria-label="Schließen">&times;</button>
                </div>
                <div id="modal-body">${content}</div>
                <div class="modal-actions">${actions}</div>
            </div>`;
    modalContainer.innerHTML = modalHTML;
    modalContainer.style.display = "flex";

    modalContainer
      .querySelectorAll(".modal-close-btn, [data-action='cancel-modal']")
      .forEach((btn) => {
        btn.addEventListener("click", () => ui.closeModal());
      });
    window.addEventListener("click", (event) => {
      if (event.target === modalContainer) ui.closeModal();
    });
  };

  window.showToast = (message, type = "info") => {
    const toastContainer = document.getElementById("toast-container");
    if (!toastContainer) return;
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.textContent = message;
    toastContainer.appendChild(toast);
    setTimeout(() => toast.classList.add("show"), 10);
    setTimeout(() => {
      toast.classList.remove("show");
      setTimeout(() => toast.remove(), 300);
    }, 3000);
  };
}

document.addEventListener("DOMContentLoaded", async () => {
  initializeTemplateFunctions();

  // Initial das Haupt-Panel verstecken, damit es nicht kurz aufblitzt
  const mainApp = document.getElementById("main-app");
  if (mainApp) mainApp.classList.add("hidden");

  try {
    const status = await api.checkSetupStatus();
    if (status.setup_needed) {
      document.getElementById("main-app").classList.add("hidden");
      document.getElementById("setup-wizard").classList.remove("hidden");
      runSetupWizard();
    } else {
      document.getElementById("setup-wizard").classList.add("hidden");
      mainApp.classList.remove("hidden");
      runMainApp();
    }
  } catch (error) {
    document.body.innerHTML = `<main class="container"><div class="card"><h2>Verbindung zum Server fehlgeschlagen</h2><p>Das Backend (main.py) läuft nicht oder ist nicht erreichbar. Bitte starte es und lade die Seite neu.</p><p><small>${error.message}</small></p></div></main>`;
    console.error("Initialization failed:", error);
  }
});

function runMainApp() {
  let config = {};
  let bridgeData = {};
  let colorPicker = null;
  let statusInterval;

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
      ui.showToast(`Initialisierungsfehler: ${error.message}`, "error");
      console.error(error);
    }
  };

  const renderAll = () => {
    ui.renderRoutines(config, bridgeData);
    ui.renderScenes(config.scenes);
  };

  const setupEventListeners = () => {
    const addListener = (id, event, handler) => {
      const element = document.getElementById(id);
      if (element) element.addEventListener(event, handler);
    };

    addListener("save-button", "click", saveFullConfig);
    addListener("btn-new-routine", "click", () =>
      ui.openCreateRoutineModal(bridgeData, config)
    );
    addListener("btn-new-scene", "click", () => {
      colorPicker = ui.openSceneModal(
        { status: true, bri: 128, ct: 366 },
        null,
        config
      );
    });

    addListener("btn-refresh-status", "click", () => updateStatus(true));
    addListener("btn-update-app", "click", () =>
      api.systemAction(
        "/api/system/update_app",
        "Anwendung via 'git pull' aktualisieren?"
      )
    );
    addListener("btn-restart-app", "click", () =>
      api.systemAction("/api/system/restart", "Anwendung neu starten?")
    );
    addListener("btn-backup-config", "click", () =>
      api.systemAction("/api/config/backup", "Konfiguration sichern?")
    );
    addListener("btn-restore-config", "click", () =>
      api.systemAction(
        "/api/config/restore",
        "Konfiguration aus Backup wiederherstellen?"
      )
    );
    addListener("btn-add-default-scenes", "click", () =>
      api.systemAction(
        "/api/system/scenes/add_defaults",
        "Standard-Szenen hinzufügen?"
      )
    );

    document.body.addEventListener("click", (e) => {
      const button = e.target.closest("[data-action]");
      if (!button) return;

      const action = button.dataset.action;
      const routineCard = e.target.closest(".routine-card");
      const sceneCard = e.target.closest(".scene-card");

      const actions = {
        "toggle-routine-details": () =>
          ui.toggleAccordion(button.closest(".accordion-button")),
        "delete-scene": () => {
          if (confirm(`Szene "${sceneCard.dataset.name}" löschen?`)) {
            delete config.scenes[sceneCard.dataset.name];
            renderAll();
            ui.showToast("Szene gelöscht.", "info");
          }
        },
        "delete-routine": () => {
          const index = routineCard.dataset.index;
          if (confirm(`Routine "${config.routines[index].name}" löschen?`)) {
            config.routines.splice(index, 1);
            renderAll();
            ui.showToast("Routine gelöscht.", "info");
          }
        },
        "edit-scene": () => {
          colorPicker = ui.openSceneModal(
            config.scenes[sceneCard.dataset.name],
            sceneCard.dataset.name,
            config
          );
        },
        "save-scene": () => handleSaveScene(config),
        "create-routine": () => handleCreateNewRoutine(config, bridgeData),
      };

      if (actions[action]) actions[action]();
    });

    const navLinks = document.querySelectorAll("header nav a[data-tab]");
    const contentSections = document.querySelectorAll(".content-section");
    navLinks.forEach((link) => {
      link.addEventListener("click", (e) => {
        e.preventDefault();
        const tabId = `content-${link.dataset.tab}`;

        navLinks.forEach((l) => l.classList.remove("active"));
        link.classList.add("active");

        contentSections.forEach((section) => {
          section.classList.toggle("hidden", section.id !== tabId);
        });

        if (statusInterval) clearInterval(statusInterval);

        if (link.dataset.tab === "status") {
          startStatusUpdates();
        } else if (link.dataset.tab === "analyse") {
          initAnalyse(bridgeData);
        } else if (link.dataset.tab === "bridge-devices") {
          initDevices();
        }
      });
    });
  };

  const updateStatus = async (showNotification = false) => {
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
  };

  const startStatusUpdates = () => {
    if (statusInterval) clearInterval(statusInterval);
    updateStatus();
    const refreshInterval =
      (config.global_settings?.status_interval_s || 5) * 1000;
    statusInterval = setInterval(() => updateStatus(false), refreshInterval);
  };

  const saveFullConfig = async () => {
    ui.showToast("Speichern...", "info");
    try {
      await api.saveFullConfig(config);
      ui.showToast("Konfiguration gespeichert!", "success");
    } catch (err) {
      ui.showToast(`Fehler: ${err.message}`, "error");
    }
  };

  const handleSaveScene = (config) => {
    const modal = document.getElementById("demo-modal");
    const originalName = modal.querySelector("#scene-original-name").value;
    const newName = modal
      .querySelector("#scene-name")
      .value.trim()
      .replace(/\s+/g, "_")
      .toLowerCase();
    if (!newName) return ui.showToast("Name fehlt.", "error");

    const newScene = {
      status: modal.querySelector("#scene-status").checked,
      bri: parseInt(modal.querySelector("#scene-bri").value),
      ct: parseInt(modal.querySelector("#scene-ct").value),
    };

    if (originalName && originalName !== newName)
      delete config.scenes[originalName];
    config.scenes[newName] = newScene;

    renderAll();
    ui.closeModal();
    ui.showToast("Szene gespeichert.", "success");
  };

  const handleCreateNewRoutine = (config, bridgeData) => {
    const modal = document.getElementById("demo-modal");
    const name = modal.querySelector("#new-routine-name").value;
    const [groupId, groupName] = modal
      .querySelector("#new-routine-group")
      .value.split("|");
    if (!name || !groupId)
      return ui.showToast("Name oder Raum fehlt.", "error");

    const newRoutine = {
      name,
      room_name: groupName,
      enabled: true,
      daily_time: { H1: 7, M1: 0, H2: 23, M2: 0 },
      morning: { scene_name: "aus" },
      day: { scene_name: "aus" },
      evening: { scene_name: "aus" },
      night: { scene_name: "aus" },
    };
    if (!config.routines) config.routines = [];
    config.routines.push(newRoutine);
    if (!config.rooms.some((r) => r.name === groupName)) {
      config.rooms.push({ name: groupName, group_id: parseInt(groupId) });
    }

    renderAll();
    ui.closeModal();
    ui.showToast("Routine erstellt.", "success");
  };

  init();
}
