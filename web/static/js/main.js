import * as api from "./modules/api.js";
import { runSetupWizard } from "./modules/setup.js";
import { initializeEventHandlers } from "./modules/event-handler.js";
import * as uiAutomations from "./modules/ui/automations.js";
import * as uiScenes from "./modules/ui/scenes.js";
import * as uiShared from "./modules/ui/shared.js";
import * as uiHome from "./modules/ui/home.js";
import { initBlueprintEditor } from "./modules/blueprint-editor.js";

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
  const appState = { config: {}, bridgeData: {}, groupedLights: [] };

  const init = async () => {
    uiShared.updateClock();
    setInterval(uiShared.updateClock, 1000);
    try {
      [appState.config, appState.bridgeData, appState.groupedLights] =
        await Promise.all([
          api.loadConfig(),
          api.loadBridgeData(),
          api.loadGroupedLights(),
        ]);

      renderAllTabs();
      initializeEventHandlers(appState);

      document.getElementById("tab-zuhause")?.click();
    } catch (error) {
      uiShared.showToast(`Initialisierungsfehler: ${error.message}`, true);
    }
  };

  const renderAllTabs = () => {
    uiHome.renderHome(appState.bridgeData, appState.groupedLights);
    uiAutomations.renderAutomations(appState.config, appState.bridgeData);
    uiScenes.renderScenes(appState.config.scenes);
    initBlueprintEditor();
  };

  await init();
}
