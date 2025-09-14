import { showToast, closeModal } from "./helpers.js";

let state;
let renderAll;
let colorPicker = null;
const scenesContainer = document.getElementById("scenes-container");
const modalSceneContainer = document.getElementById("modal-scene");

export function initScenes(appState, renderCallback) {
  state = appState;
  renderAll = renderCallback;

  document
    .getElementById("btn-new-scene")
    .addEventListener("click", () =>
      openSceneModal({ status: true, bri: 128, ct: 366 }, null)
    );
  scenesContainer.addEventListener("click", handleSceneClick);
  modalSceneContainer.addEventListener("click", handleModalClick);
}

function handleSceneClick(e) {
  const button = e.target.closest("[data-action]");
  if (!button) return;

  const action = button.dataset.action;
  const sceneCard = e.target.closest("[data-name]");
  const sceneName = sceneCard.dataset.name;

  if (action === "edit-scene") {
    openSceneModal(state.config.scenes[sceneName], sceneName);
  }
  if (action === "delete-scene") {
    if (confirm(`Szene "${sceneName}" wirklich löschen?`)) {
      delete state.config.scenes[sceneName];
      renderAll();
      showToast("Szene gelöscht. Speichern nicht vergessen.", false);
    }
  }
}

function handleModalClick(e) {
  const button = e.target.closest("[data-action]");
  if (!button) return;
  const action = button.dataset.action;

  if (action === "save-scene") handleSaveScene();
  if (action === "cancel-modal") closeModal();
}

export function renderScenes() {
  if (!scenesContainer) return;
  scenesContainer.innerHTML = "";
  if (!state.config.scenes || Object.keys(state.config.scenes).length === 0) {
    scenesContainer.innerHTML = `<p class="text-gray-500 text-center mt-4">Noch keine Szenen erstellt.</p>`;
    return;
  }
  for (const [name, scene] of Object.entries(state.config.scenes)) {
    const sceneEl = document.createElement("div");
    sceneEl.className =
      "bg-white p-4 rounded-lg shadow-md flex flex-col justify-between border border-gray-200";
    sceneEl.dataset.name = name;
    let colorPreviewStyle = "background-color: #e5e7eb;";
    if (scene.status) {
      if (scene.hue !== undefined && scene.sat !== undefined) {
        const hue = (scene.hue / 65535) * 360;
        const sat = (scene.sat / 254) * 100;
        const bri = Math.min(100, Math.max(20, (scene.bri / 254) * 100));
        colorPreviewStyle = `background-color: hsl(${hue}, ${sat}%, ${bri}%);`;
      } else if (scene.ct !== undefined) {
        const tempPercent = Math.min(
          1,
          Math.max(0, (scene.ct - 153) / (500 - 153))
        );
        const red = 255;
        const green = 255 - tempPercent * 100;
        const blue = Math.max(0, 255 - tempPercent * 255);
        colorPreviewStyle = `background-color: rgb(${Math.round(
          red
        )}, ${Math.round(green)}, ${Math.round(blue)});`;
      }
    }
    sceneEl.innerHTML = `<div><div class="flex items-center mb-2"><div class="w-6 h-6 rounded-full mr-3 border border-gray-400" style="${colorPreviewStyle}"></div><h4 class="text-xl font-semibold capitalize">${name.replace(
      /_/g,
      " "
    )}</h4></div><div class="mt-2 text-sm text-gray-600 space-y-1"><p>Status: <span class="font-medium ${
      scene.status ? "text-green-600" : "text-red-600"
    }">${
      scene.status ? "An" : "Aus"
    }</span></p><p>Helligkeit: <span class="font-medium">${
      scene.bri
    }</span></p>${
      scene.ct !== undefined
        ? `<p>Farbtemp.: <span class="font-medium">${scene.ct}</span></p>`
        : ""
    }</div></div><div class="mt-3 flex justify-end space-x-3"><button type="button" data-action="edit-scene" class="text-blue-600 hover:text-blue-800 text-sm font-medium">Bearbeiten</button><button type="button" data-action="delete-scene" class="text-red-600 hover:text-red-800 text-sm font-medium">Löschen</button></div>`;
    scenesContainer.appendChild(sceneEl);
  }
}

function openSceneModal(scene, sceneName) {
  const isEditing = sceneName !== null;
  const isColorMode = scene.hue !== undefined;
  modalSceneContainer.innerHTML = `<div class="modal-backdrop fixed inset-0 z-50 overflow-auto flex items-center justify-center bg-black bg-opacity-50"><div class="bg-white rounded-lg shadow-xl w-full max-w-md m-4"><div class="p-6"><h3 class="text-2xl font-bold mb-4">${
    isEditing ? "Szene bearbeiten" : "Neue Szene"
  }</h3><form id="form-scene" class="space-y-4"><input type="hidden" id="scene-original-name" value="${
    sceneName || ""
  }"><label class="block text-sm font-medium">Name</label><input type="text" id="scene-name" value="${
    isEditing ? sceneName.replace(/_/g, " ") : ""
  }" required class="mt-1 w-full rounded-md border-gray-300"><div class="flex space-x-4 border-b pb-2"><label><input type="radio" name="color-mode" value="ct" ${
    !isColorMode ? "checked" : ""
  }> Weißtöne</label><label><input type="radio" name="color-mode" value="color" ${
    isColorMode ? "checked" : ""
  }> Farbe</label></div><div id="ct-controls" class="${
    isColorMode ? "hidden" : ""
  }"><label class="block text-sm font-medium">Farbtemperatur</label><input type="range" id="scene-ct" min="153" max="500" value="${
    scene.ct || 366
  }" class="w-full ct-slider"></div><div id="color-controls" class="${
    !isColorMode ? "hidden" : ""
  }"><div id="color-picker-container" class="flex justify-center my-2"></div></div><div><label class="block text-sm font-medium">Helligkeit</label><input type="range" id="scene-bri" min="0" max="254" value="${
    scene.bri || 0
  }" class="w-full brightness-slider"></div><div class="flex items-center"><input type="checkbox" id="scene-status" ${
    scene.status ? "checked" : ""
  } class="h-4 w-4 rounded"><label for="scene-status" class="ml-2 block text-sm">Licht an</label></div></form></div><div class="bg-gray-50 px-6 py-3 flex justify-end space-x-3"><button type="button" data-action="cancel-modal" class="bg-white py-2 px-4 border rounded-md">Abbrechen</button><button type="button" data-action="save-scene" class="bg-blue-600 text-white py-2 px-4 rounded-md">Speichern</button></div></div></div>`;
  modalSceneContainer.classList.remove("hidden");
  colorPicker = new iro.ColorPicker("#color-picker-container", {
    width: 250,
    color: isColorMode
      ? { h: (scene.hue / 65535) * 360, s: (scene.sat / 254) * 100, v: 100 }
      : "#ffffff",
  });
  document.querySelectorAll('input[name="color-mode"]').forEach((r) =>
    r.addEventListener("change", (e) => {
      document
        .getElementById("ct-controls")
        .classList.toggle("hidden", e.target.value !== "ct");
      document
        .getElementById("color-controls")
        .classList.toggle("hidden", e.target.value !== "color");
    })
  );
}
//...
