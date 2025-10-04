import * as api from "./api.js";
import { showToast } from "./ui/shared.js";

const Blueprint3d = window.Blueprint3d;
let blueprint3d;

const texture_config = {
  wallTexture: "wallmap.png",
  floorTexture: { url: "hardwood.png", scale: 400.0 },
  ceilingTexture: { url: "light_fine_wood.jpg", scale: 400.0 },
};

export async function initBlueprintEditor() {
  const opts = {
    floorplannerElement: "bp-viewer",
    threeElement: null,
    texturepath: "/static/textures/",
  };

  blueprint3d = new Blueprint3d(opts);

  try {
    const savedFloorplan = await api.loadFloorplanConfig();
    if (savedFloorplan && Object.keys(savedFloorplan).length > 0) {
      blueprint3d.model.loadSerialized(JSON.stringify(savedFloorplan));
    }
  } catch (error) {
    console.warn("Kein gespeicherter Grundriss gefunden.", error);
  }

  blueprint3d.floorplanner.setTextures(texture_config);
  setupEventListeners();
  blueprint3d.floorplanner.setMode(Blueprint3d.Floorplanner.Mode.MOVE);
}

function setupEventListeners() {
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
    if (blueprint3d) blueprint3d.floorplanner.resizeView();
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
