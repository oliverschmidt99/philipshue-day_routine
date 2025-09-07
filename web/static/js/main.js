// web/static/js/main.js
import * as api from "./modules/api.js";
import * as ui from "./modules/ui.js";
import { runSetupWizard } from "./modules/setup.js";
import { initAnalysePage } from "./modules/analyse.js";
import { initStatusPage, stopStatusUpdates } from "./modules/status.js";
import { initHelpPage } from "./modules/help.js";
import { initDevicesPage } from "./modules/devices.js";

function initializeTemplateFunctions() {
  window.showModal = (title, content, actions) => {
    const modalContainer = document.getElementById("demo-modal");
    if (!modalContainer) return;
    modalContainer.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>${title}</h3>
                    <button type="button" class="modal-close-btn" aria-label="Schließen">&times;</button>
                </div>
                <div id="modal-body">${content}</div>
                <div class="modal-actions">${actions}</div>
            </div>`;
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
  const mainApp = document.getElementById("main-app");
  if (mainApp) mainApp.classList.add("hidden");

  try {
    const status = await api.checkSetupStatus();
    if (status.setup_needed) {
      document.getElementById("setup-wizard").classList.remove("hidden");
      runSetupWizard();
    } else {
      mainApp.classList.remove("hidden");
      runMainApp();
    }
  } catch (error) {
    document.body.innerHTML = `<main class="container"><div class="card"><h2>Verbindung zum Server fehlgeschlagen</h2><p>Das Backend (main.py) läuft nicht. Bitte starte es und lade die Seite neu.</p><p><small>${error.message}</small></p></div></main>`;
    console.error("Initialization failed:", error);
  }
});

function runMainApp() {
  let config = {};
  let bridgeData = {};

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
    document
      .getElementById("save-button")
      ?.addEventListener("click", saveFullConfig);
    document
      .getElementById("btn-new-routine")
      ?.addEventListener("click", () =>
        ui.openCreateRoutineModal(bridgeData, config)
      );
    document.getElementById("btn-new-scene")?.addEventListener("click", () => {
      ui.openSceneModal({ status: true, bri: 128, ct: 366 }, null, config);
    });
    document
      .getElementById("btn-update-app")
      ?.addEventListener("click", () =>
        api.systemAction(
          "/api/system/update_app",
          "Anwendung via 'git pull' aktualisieren?"
        )
      );
    document
      .getElementById("btn-restart-app")
      ?.addEventListener("click", () =>
        api.systemAction("/api/system/restart", "Anwendung neu starten?")
      );
    document
      .getElementById("btn-backup-config")
      ?.addEventListener("click", () =>
        api.systemAction("/api/config/backup", "Konfiguration sichern?")
      );
    document
      .getElementById("btn-restore-config")
      ?.addEventListener("click", () =>
        api.systemAction(
          "/api/config/restore",
          "Konfiguration aus Backup wiederherstellen?"
        )
      );
    document
      .getElementById("btn-add-default-scenes")
      ?.addEventListener("click", () =>
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
        "toggle-routine-details": () => ui.toggleAccordion(button),
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
          ui.openSceneModal(
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

        stopStatusUpdates();

        switch (link.dataset.tab) {
          case "status":
            initStatusPage(config);
            break;
          case "analyse":
            initAnalysePage(bridgeData);
            break;
          case "hilfe":
            initHelpPage();
            break;
          case "bridge-devices":
            initDevicesPage(bridgeData);
            break;
        }
      });
    });
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
    if (!config.rooms || !config.rooms.some((r) => r.name === groupName)) {
      if (!config.rooms) config.rooms = [];
      config.rooms.push({ name: groupName, group_id: parseInt(groupId) });
    }

    renderAll();
    ui.closeModal();
    ui.showToast("Routine erstellt.", "success");
  };

  init();
}
