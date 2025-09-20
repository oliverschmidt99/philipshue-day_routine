export function closeModal() {
  document.querySelectorAll(".modal-backdrop").forEach((modal) => {
    if (modal) {
      modal.classList.add("hidden");
      modal.innerHTML = "";
    }
  });
}

export function openSceneModal(group, lightsInGroup) {
  const modalSceneContainer = document.getElementById("modal-scene");

  const lightsHtml = lightsInGroup
    .map(
      (light) => `
    <div class="p-3 bg-gray-700 rounded-lg scene-light-config" data-light-id="${light.id}">
        <label class="flex items-center space-x-3 cursor-pointer">
            <input type="checkbox" class="form-checkbox h-5 w-5 bg-gray-600 border-gray-500 rounded text-blue-500 focus:ring-blue-400" data-light-control="include">
            <span class="font-medium">${light.metadata.name}</span>
        </label>
        <div class="mt-2 pl-8 space-y-2 hidden light-controls">
            <label class="text-sm text-gray-400">Helligkeit</label>
            <input type="range" min="1" max="100" value="80" class="w-full h-2 bg-gray-600 rounded-lg appearance-none cursor-pointer brightness-slider" data-light-control="brightness">
        </div>
    </div>
  `
    )
    .join("");

  const modalHtml = `
    <div class="modal-backdrop fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-70" data-action="cancel-modal">
        <div class="bg-gray-800 rounded-lg shadow-xl w-full max-w-lg m-4 text-white" onclick="event.stopPropagation()">
            <div class="p-6">
                <h3 class="text-2xl font-bold mb-4">Neue Szene für ${group.name}</h3>
                <form id="form-scene" class="space-y-4">
                    <input type="hidden" id="scene-group-id" value="${group.id}">
                    <div>
                        <label for="scene-name" class="block text-sm font-medium mb-1 text-gray-300">Szenenname</label>
                        <input type="text" id="scene-name" required class="w-full p-2 bg-gray-700 border border-gray-600 rounded-md focus:ring-blue-500 focus:border-blue-500">
                    </div>
                    <div>
                        <h4 class="text-lg font-semibold mb-2">Lampen für die Szene auswählen</h4>
                        <div class="space-y-3 max-h-60 overflow-y-auto p-2 border border-gray-700 rounded-lg">
                           ${lightsHtml}
                        </div>
                    </div>
                </form>
            </div>
            <div class="bg-gray-900 px-6 py-4 flex justify-end space-x-3">
                <button type="button" data-action="cancel-modal" class="bg-gray-600 hover:bg-gray-500 py-2 px-4 rounded-md">Abbrechen</button>
                <button type="button" data-action="save-scene" class="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md">Speichern</button>
            </div>
        </div>
    </div>`;

  modalSceneContainer.innerHTML = modalHtml;
  modalSceneContainer.classList.remove("hidden");

  // Event Listeners für die Checkboxen im Modal hinzufügen
  document
    .querySelectorAll('input[data-light-control="include"]')
    .forEach((checkbox) => {
      checkbox.addEventListener("change", (e) => {
        const controls = e.target
          .closest(".scene-light-config")
          .querySelector(".light-controls");
        controls.classList.toggle("hidden", !e.target.checked);
      });
    });
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
        <div class="bg-gray-800 rounded-lg shadow-xl w-full max-w-sm m-4 p-6 text-white" onclick="event.stopPropagation()">
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
