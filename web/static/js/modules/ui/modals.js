export function closeModal() {
  document.querySelectorAll(".modal-backdrop").forEach((modal) => {
    if (modal) {
      modal.classList.add("hidden");
      modal.innerHTML = "";
    }
  });
}

export function openSelectAutomationTypeModal() {
  const modalContainer = document.getElementById("modal-routine"); // Reuse modal container
  const modalHtml = `
    <div class="modal-backdrop fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-70" data-action="cancel-modal">
        <div class="bg-gray-800 text-gray-200 rounded-lg shadow-xl w-full max-w-lg m-4">
            <div class="p-6">
                <h3 class="text-2xl font-bold mb-6 text-center">Welche Art von Automation möchtest du erstellen?</h3>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
                    
                    <button data-action="create-automation" data-type="routine" class="p-4 bg-gray-700 border border-gray-600 rounded-lg hover:bg-blue-900 hover:border-blue-500 hover:shadow-lg transition-all">
                        <i class="fas fa-calendar-alt text-4xl text-blue-400 mb-2"></i>
                        <h4 class="font-semibold text-lg">Tages-Routine</h4>
                        <p class="text-sm text-gray-400">Klassische Steuerung für Morgen, Tag, Abend, Nacht.</p>
                    </button>
                    
                    <button data-action="create-automation" data-type="timer" class="p-4 bg-gray-700 border border-gray-600 rounded-lg hover:bg-green-900 hover:border-green-500 hover:shadow-lg transition-all">
                        <i class="fas fa-hourglass-half text-4xl text-green-400 mb-2"></i>
                        <h4 class="font-semibold text-lg">Timer</h4>
                        <p class="text-sm text-gray-400">Führt eine Aktion nach einer bestimmten Zeit aus.</p>
                    </button>
                    
                    <button data-action="create-automation" data-type="state_machine" class="p-4 bg-gray-700 border border-gray-600 rounded-lg hover:bg-purple-900 hover:border-purple-500 hover:shadow-lg transition-all">
                        <i class="fas fa-sitemap text-4xl text-purple-400 mb-2"></i>
                        <h4 class="font-semibold text-lg">Zustands-Automat</h4>
                        <p class="text-sm text-gray-400">Komplexe Logik mit Zuständen und Übergängen.</p>
                    </button>
                </div>
            </div>
            <div class="bg-gray-900 px-6 py-3 flex justify-end">
                 <button type="button" data-action="cancel-modal" class="bg-gray-600 hover:bg-gray-500 py-2 px-4 rounded-md">Abbrechen</button>
            </div>
        </div>
    </div>`;
  modalContainer.innerHTML = modalHtml;
  modalContainer.classList.remove("hidden");
}

export function openCreateRoutineModal(bridgeData) {
  const modalRoutineContainer = document.getElementById("modal-routine");
  const groupOptions = [...bridgeData.rooms, ...bridgeData.zones]
    .map((g) => `<option value="${g.id}|${g.name}">${g.name}</option>`)
    .join("");
  const sensorOptions = bridgeData.sensors
    .map((s) => `<option value="${s.id}">${s.name}</option>`)
    .join("");
  modalRoutineContainer.innerHTML = `<div class="modal-backdrop fixed inset-0 z-50 overflow-auto flex items-center justify-center bg-black bg-opacity-50">
  <div class="bg-gray-800 rounded-lg shadow-xl w-full max-w-lg m-4 text-gray-200">
  <div class="p-6">
  <h3 class="text-2xl font-bold mb-4">Neue Routine</h3>
  <form class="space-y-4">
  <label class="block text-sm font-medium text-gray-300">Name</label>
  <input type="text" id="new-automation-name" required class="mt-1 block w-full rounded-md bg-gray-700 border-gray-600 text-gray-200">
  <label class="block text-sm font-medium text-gray-300">Raum / Zone</label>
  <select id="new-routine-group" class="mt-1 block w-full rounded-md bg-gray-700 border-gray-600 text-gray-200">${groupOptions}</select>
  <label class="block text-sm font-medium text-gray-300">Sensor (Optional)</label>
  <select id="new-routine-sensor" class="mt-1 block w-full rounded-md bg-gray-700 border-gray-600 text-gray-200"><option value="">Kein Sensor</option>${sensorOptions}</select>
  </form>
  </div>
  <div class="bg-gray-900 px-6 py-3 flex justify-end space-x-3">
  <button type="button" data-action="cancel-modal" class="bg-gray-600 hover:bg-gray-500 text-white py-2 px-4 border border-gray-600 rounded-md">Abbrechen</button>
  <button type="button" data-action="save-new-automation" data-type="routine" class="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md">Erstellen</button>
  </div>
  </div>
  </div>`;
  modalRoutineContainer.classList.remove("hidden");
}

export function openCreateTimerModal(bridgeData) {
  const modalContainer = document.getElementById("modal-routine");
  const roomOptions = [...bridgeData.rooms, ...bridgeData.zones]
    .map((g) => `<option value="${g.name}">${g.name}</option>`)
    .join("");
  const sceneOptions = bridgeData.scenes
    .map(
      (s) => `<option value="${s.metadata.name}">${s.metadata.name}</option>`
    )
    .join("");

  modalContainer.innerHTML = `<div class="modal-backdrop fixed inset-0 z-50 overflow-auto flex items-center justify-center bg-black bg-opacity-50">
    <div class="bg-gray-800 rounded-lg shadow-xl w-full max-w-lg m-4 text-gray-200">
    <div class="p-6">
        <h3 class="text-2xl font-bold mb-4">Neuer Timer</h3>
        <form class="space-y-4">
            <div>
                <label for="new-automation-name" class="block text-sm font-medium text-gray-300">Name</label>
                <input type="text" id="new-automation-name" required class="mt-1 block w-full rounded-md bg-gray-700 border-gray-600 text-gray-200">
            </div>
            <div>
                <label for="timer-duration" class="block text-sm font-medium text-gray-300">Dauer (Minuten)</label>
                <input type="number" id="timer-duration" value="10" min="1" class="mt-1 block w-full rounded-md bg-gray-700 border-gray-600 text-gray-200">
            </div>
             <div>
                <label class="block text-sm font-medium text-gray-300">Aktion nach Ablauf</label>
                <div class="grid grid-cols-2 gap-2 mt-1">
                    <select id="timer-target-room" class="block w-full rounded-md bg-gray-700 border-gray-600 text-gray-200">${roomOptions}</select>
                    <select id="timer-scene-name" class="block w-full rounded-md bg-gray-700 border-gray-600 text-gray-200">${sceneOptions}</select>
                </div>
            </div>
        </form>
    </div>
    <div class="bg-gray-900 px-6 py-3 flex justify-end space-x-3">
        <button type="button" data-action="cancel-modal" class="bg-gray-600 hover:bg-gray-500 text-white py-2 px-4 border border-gray-600 rounded-md">Abbrechen</button>
        <button type="button" data-action="save-new-automation" data-type="timer" class="bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded-md">Erstellen</button>
    </div>
    </div></div>`;
  modalContainer.classList.remove("hidden");
}

export function openCreateStateMachineModal(bridgeData) {
  const modalContainer = document.getElementById("modal-routine");
  const roomOptions = [...bridgeData.rooms, ...bridgeData.zones]
    .map((g) => `<option value="${g.name}">${g.name}</option>`)
    .join("");

  modalContainer.innerHTML = `<div class="modal-backdrop fixed inset-0 z-50 overflow-auto flex items-center justify-center bg-black bg-opacity-50">
    <div class="bg-gray-800 rounded-lg shadow-xl w-full max-w-lg m-4 text-gray-200">
    <div class="p-6">
        <h3 class="text-2xl font-bold mb-4">Neuer Zustands-Automat</h3>
        <form class="space-y-4">
            <div>
                <label for="new-automation-name" class="block text-sm font-medium text-gray-300">Name</label>
                <input type="text" id="new-automation-name" required class="mt-1 block w-full rounded-md bg-gray-700 border-gray-600 text-gray-200">
            </div>
             <div>
                <label for="fsm-target-room" class="block text-sm font-medium text-gray-300">Ziel-Raum/Zone</label>
                <select id="fsm-target-room" class="mt-1 block w-full rounded-md bg-gray-700 border-gray-600 text-gray-200">${roomOptions}</select>
            </div>
        </form>
    </div>
    <div class="bg-gray-900 px-6 py-3 flex justify-end space-x-3">
        <button type="button" data-action="cancel-modal" class="bg-gray-600 hover:bg-gray-500 text-white py-2 px-4 border border-gray-600 rounded-md">Abbrechen</button>
        <button type="button" data-action="save-new-automation" data-type="state_machine" class="bg-purple-600 hover:bg-purple-700 text-white py-2 px-4 rounded-md">Erstellen & Bearbeiten</button>
    </div>
    </div></div>`;
  modalContainer.classList.remove("hidden");
}
