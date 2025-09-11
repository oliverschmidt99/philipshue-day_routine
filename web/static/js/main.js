import * as api from "./api.js";
import * as ui from "./ui.js";
import { runSetupWizard } from "./setup.js";

document.addEventListener("DOMContentLoaded", async () => {
  try {
    const status = await api.checkSetupStatus();
    if (status.setup_needed) {
      document.getElementById("main-app-container")?.classList.add("hidden");
      document
        .getElementById("setup-wizard-container")
        ?.classList.remove("hidden");
      runSetupWizard();
    } else {
      document
        .getElementById("setup-wizard-container")
        ?.classList.add("hidden");
      document.getElementById("main-app-container")?.classList.remove("hidden");
      runMainApp();
    }
  } catch (error) {
    document.body.innerHTML = `<div class="container"><h1>Verbindungsfehler</h1><p>Der Server ist nicht erreichbar. Läuft main.py?</p><p><small>${error.message}</small></p></div>`;
  }
});

function runMainApp() {
  const appState = {
    config: {},
    bridgeData: {},
  };

  const init = async () => {
    try {
      [appState.config, appState.bridgeData] = await Promise.all([
        api.loadConfig(),
        api.loadBridgeData(),
      ]);

      ui.renderRoutines(appState.config, appState.bridgeData);
      setupEventListeners();
    } catch (error) {
      console.error("Fehler beim Initialisieren der App:", error);
    }
  };

  const setupEventListeners = () => {
    const navLinks = document.querySelectorAll("#main-nav .nav-item a");
    const contentSections = document.querySelectorAll(".content-section");

    navLinks.forEach((link) => {
      link.addEventListener("click", (e) => {
        e.preventDefault();

        // 1. Deaktiviere ALLE Links
        navLinks.forEach((navLink) => navLink.classList.remove("active"));

        // 2. Verstecke ALLE Inhaltsbereiche
        contentSections.forEach((section) =>
          section.classList.remove("active")
        );

        // 3. Aktiviere den geklickten Link
        link.classList.add("active");

        // 4. Zeige den zugehörigen Inhaltsbereich an
        const targetId = `content-${link.dataset.target}`;
        const targetSection = document.getElementById(targetId);
        if (targetSection) {
          targetSection.classList.add("active");
        }
      });
    });
  };

  init();
}
