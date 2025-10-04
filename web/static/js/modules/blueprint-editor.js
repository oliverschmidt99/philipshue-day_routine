import * as api from "./api.js";
import { showToast } from "./ui/shared.js";

let blueprint3d;
let isInitialized = false;

// Funktion zum Warten auf die Bibliothek
function waitForBlueprint3d(callback) {
  const interval = setInterval(() => {
    if (window.Blueprint3d) {
      clearInterval(interval);
      callback();
    }
  }, 100); // Überprüft alle 100ms
}

async function initialize() {
  const BP3D = window.Blueprint3d;

  const texture_config = {
    wallTexture: "wallmap.png",
    floorTexture: { url: "hardwood.png", scale: 400.0 },
    ceilingTexture: { url: "light_fine_wood.jpg", scale: 400.0 },
  };

  const opts = {
    floorplannerElement: "bp-viewer",
    threeElement: null,
    texturepath: "/blueprint3d/example/textures/", // Korrekter Pfad zu den Texturen
  };

  blueprint3d = new BP3D.Blueprint3d(opts);

  try {
    const savedFloorplan = await api.loadFloorplanConfig();
    if (savedFloorplan && Object.keys(savedFloorplan).length > 0) {
      blueprint3d.model.loadSerialized(JSON.stringify(savedFloorplan));
    }
  } catch (error) {
    console.warn("Kein gespeicherter Grundriss gefunden.", error);
  }

  if (blueprint3d.floorplanner) {
    blueprint3d.floorplanner.setTextures(texture_config);
    setupEventListeners();
    blueprint3d.floorplanner.setMode(BP3D.Floorplanner.Mode.MOVE);
  } else {
    console.error("Floorplanner konnte nicht initialisiert werden.");
  }
  isInitialized = true;
}

export function initBlueprintEditor() {
  if (isInitialized) return; // Nicht erneut initialisieren
  waitForBlueprint3d(initialize);
}

function setupEventListeners() {
  if (!blueprint3d || !blueprint3d.floorplanner) return;

  const modeButtons = document.querySelectorAll(".bp-mode-button");
  modeButtons.forEach((button) => {
    button.addEventListener("click", (e) => {
      const target = e.currentTarget;
      const mode = parseInt(target.dataset.mode, 10);
      blueprint3d.floorplanner.setMode(mode);

      modeButtons.forEach((btn) =>
        btn.classList.remove("bg-blue-600", "text-white")
      );
      modeButtons.forEach((btn) =>
        btn.classList.add("bg-gray-700", "hover:bg-gray-600")
      );
      target.classList.add("bg-blue-600", "text-white");
      target.classList.remove("bg-gray-700", "hover:bg-gray-600");
    });
  });

  document
    .getElementById("floorplan-save")
    .addEventListener("click", saveFloorplan);

  window.addEventListener("resize", () => {
    if (blueprint3d && blueprint3d.floorplanner) {
      blueprint3d.floorplanner.resizeView();
    }
  });
}

async function saveFloorplan() {
  try {
    const floorplanJson = blueprint3d.model.exportSerialized();
    const floorplanData = JSON.parse(floorplanJson);

    await api.saveFloorplanConfig(floorplanData);
    showToast("Grundriss erfolgreich gespeichert!");
  } catch (error) {
    showToast(`Fehler beim Speichern: ${error.message}`, true);
  }
}
