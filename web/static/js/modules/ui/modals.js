export function closeModal() {
  document.querySelectorAll(".modal-backdrop").forEach((modal) => {
    if (modal) {
      modal.classList.add("hidden");
      modal.innerHTML = "";
    }
  });
}

export function openSceneModal(scene, sceneName) {
  const modalSceneContainer = document.getElementById("modal-scene");
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

  const colorPicker = new iro.ColorPicker("#color-picker-container", {
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
  return colorPicker;
}

export function openCreateRoutineModal(bridgeData) {
  const modalRoutineContainer = document.getElementById("modal-routine");
  const groupOptions = bridgeData.groups
    .map((g) => `<option value="${g.id}|${g.name}">${g.name}</option>`)
    .join("");
  const sensorOptions = bridgeData.sensors
    .map((s) => `<option value="${s.id}">${s.name}</option>`)
    .join("");
  modalRoutineContainer.innerHTML = `<div class="modal-backdrop fixed inset-0 z-50 overflow-auto flex items-center justify-center bg-black bg-opacity-50"><div class="bg-white rounded-lg shadow-xl w-full max-w-lg m-4"><div class="p-6"><h3 class="text-2xl font-bold mb-4">Neue Routine</h3><form class="space-y-4"><label for="new-routine-name" class="block text-sm font-medium">Name</label><input type="text" id="new-routine-name" required class="mt-1 block w-full rounded-md border-gray-300"><label for="new-routine-group" class="block text-sm font-medium">Raum / Zone</label><select id="new-routine-group" class="mt-1 block w-full rounded-md border-gray-300">${groupOptions}</select><label for="new-routine-sensor" class="block text-sm font-medium">Sensor (Optional)</label><select id="new-routine-sensor" class="mt-1 block w-full rounded-md border-gray-300"><option value="">Kein Sensor</option>${sensorOptions}</select></form></div><div class="bg-gray-50 px-6 py-3 flex justify-end space-x-3"><button type="button" data-action="cancel-modal" class="bg-white py-2 px-4 border rounded-md">Abbrechen</button><button type="button" data-action="create-routine" class="bg-blue-600 text-white py-2 px-4 rounded-md">Erstellen</button></div></div></div>`;
  modalRoutineContainer.classList.remove("hidden");
}

export function openColorControlModal(groupId, groupedLight) {
  const modalSceneContainer = document.getElementById("modal-scene");
  const brightness = groupedLight?.dimming?.brightness || 50;

  const modalHtml = `
    <div class="modal-backdrop fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-70" data-action="cancel-modal">
        <div class="bg-gray-800 rounded-lg shadow-xl w-full max-w-sm m-4 p-6 text-white">
            <h3 class="text-xl font-bold mb-4 text-center">Licht anpassen</h3>
            
            <div class="flex justify-center my-4">
                <div id="live-color-picker-container"></div>
            </div>

            <div class="mt-6">
                <label class="block text-sm font-medium mb-2">Helligkeit</label>
                <input type="range" id="live-brightness-slider" min="1" max="100" value="${brightness}" 
                       data-group-id="${groupId}"
                       class="w-full h-2 bg-gray-600 rounded-lg appearance-none cursor-pointer brightness-slider">
            </div>

            <div class="mt-6 flex justify-end">
                <button type="button" data-action="cancel-modal" class="bg-blue-600 py-2 px-5 rounded-md">Fertig</button>
            </div>
        </div>
    </div>
    `;

  modalSceneContainer.innerHTML = modalHtml;
  modalSceneContainer.classList.remove("hidden");
}
