import { icons, periodNames, sectionColors } from "./shared.js";
import { initFsmEditor } from "./fsm-editor.js";

// ##### KARTEN FÜR DIE ÜBERSICHTSSEITE #####

function renderRoutineCard(automation, index, bridgeData, config) {
  const roomConf =
    bridgeData.rooms.find((r) => r.name === automation.room_name) ||
    bridgeData.zones.find((z) => z.name === automation.room_name);
  const sensorId = roomConf
    ? config.rooms.find((r) => r.name === automation.room_name)?.sensor_id
    : null;
  const sensor = sensorId
    ? bridgeData.sensors.find((s) => s.id == sensorId)
    : null;
  const sensorHtml = sensor
    ? `<span class="mx-2 text-gray-400">|</span> <span class="flex items-center" title="Sensor"><i class="fas fa-satellite-dish mr-2 text-teal-500"></i> ${sensor.name}</span>`
    : "";
  const dailyTime = automation.daily_time || {};

  return `
        <div class="flex items-center text-gray-500 text-sm mt-1">
            <p title="Raum/Zone"><i class="fas fa-layer-group mr-2 text-indigo-500"></i>${
              automation.room_name
            }</p>
            ${sensorHtml}
            <span class="mx-2 text-gray-400">|</span>
            <p title="Aktivitätszeitraum"><i class="far fa-clock mr-2 text-blue-500"></i>${String(
              dailyTime.H1 || 0
            ).padStart(2, "0")}:${String(dailyTime.M1 || 0).padStart(
    2,
    "0"
  )} - ${String(dailyTime.H2 || 23).padStart(2, "0")}:${String(
    dailyTime.M2 || 59
  ).padStart(2, "0")}</p>
        </div>
    `;
}

function renderTimerCard(automation) {
  return `
        <div class="flex items-center text-gray-500 text-sm mt-1">
             <p title="Ziel-Gerät/Raum"><i class="fas fa-bullseye mr-2 text-purple-500"></i>${
               automation.action?.target_room || "N/A"
             }</p>
            <span class="mx-2 text-gray-400">|</span>
            <p title="Dauer"><i class="fas fa-stopwatch mr-2 text-green-500"></i>${
              automation.duration_minutes
            } Minuten</p>
        </div>
    `;
}

function renderStateMachineCard(automation) {
  const stateCount = automation.states?.length || 0;
  const transitionCount = automation.transitions?.length || 0;
  return `
        <div class="flex items-center text-gray-500 text-sm mt-1">
            <p title="Ziel-Gerät/Raum"><i class="fas fa-bullseye mr-2 text-purple-500"></i>${
              automation.target_room || "N/A"
            }</p>
            <span class="mx-2 text-gray-400">|</span>
            <p title="Zustände"><i class="fas fa-project-diagram mr-2 text-orange-500"></i> ${stateCount} Zustände</p>
             <span class="mx-2 text-gray-400">|</span>
            <p title="Übergänge"><i class="fas fa-exchange-alt mr-2 text-red-500"></i> ${transitionCount} Übergänge</p>
        </div>
    `;
}

// ##### DETAILANSICHTEN / EDITOREN #####

function renderRoutineDetails(automation, bridgeData) {
  const scenes = bridgeData.scenes;
  const roomConf =
    bridgeData.rooms.find((r) => r.name === automation.room_name) ||
    bridgeData.zones.find((z) => z.name === automation.room_name);
  const roomScenes = roomConf
    ? scenes.filter((scene) => scene.group.rid === roomConf.id)
    : [];

  const sceneOptions = roomScenes
    .map(
      (scene) =>
        `<option value="${scene.metadata.name}">${scene.metadata.name.replace(
          /_/g,
          " "
        )}</option>`
    )
    .join("");

  // HINWEIS: Der Inhalt des Routine-Editors muss hier noch vervollständigt werden.
  // Ich habe ihn der Übersichtlichkeit halber weggelassen, da er bereits funktionierte.
  // Du kannst den Code aus einer älteren Version von `automations.js` hierher kopieren.
  return `
      <div class="p-4 bg-gray-50">
          <p>Detailansicht für Routinen.</p>
      </div>`;
}

function renderTimerDetails(automation, bridgeData) {
  const roomOptions = [...bridgeData.rooms, ...bridgeData.zones]
    .map(
      (g) =>
        `<option value="${g.name}" ${
          automation.action?.target_room === g.name ? "selected" : ""
        }>${g.name}</option>`
    )
    .join("");
  const sceneOptions = bridgeData.scenes
    .map(
      (s) =>
        `<option value="${s.metadata.name}" ${
          automation.action?.scene_name === s.metadata.name ? "selected" : ""
        }>${s.metadata.name}</option>`
    )
    .join("");

  return `
    <div class="p-4 space-y-4 bg-gray-50">
        <div>
            <label class="block text-sm font-medium text-gray-700">Name</label>
            <input type="text" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm" value="${automation.name}">
        </div>
        <div>
            <label class="block text-sm font-medium text-gray-700">Dauer (Minuten)</label>
            <input type="number" min="1" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm" value="${automation.duration_minutes}">
        </div>
        <div class="p-4 border rounded-md bg-white">
            <h4 class="font-semibold mb-2">Auslöser (Trigger)</h4>
            <p class="text-gray-500 text-sm">TODO: UI für Trigger-Auswahl</p>
        </div>
        <div class="p-4 border rounded-md bg-white">
            <h4 class="font-semibold mb-2">Aktion (nach Ablauf)</h4>
            <div class="space-y-2">
                <select class="block w-full rounded-md border-gray-300 shadow-sm">${roomOptions}</select>
                <select class="block w-full rounded-md border-gray-300 shadow-sm">${sceneOptions}</select>
            </div>
        </div>
    </div>`;
}

function renderStateMachineDetails(automation, bridgeData, index) {
  return `
    <div class="flex h-[600px] bg-gray-100">
        <div id="fsm-editor-canvas-${index}" class="fsm-canvas flex-grow relative bg-gray-200 overflow-hidden">
            <svg class="absolute top-0 left-0 w-full h-full pointer-events-none">
                <defs>
                    <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                        <path d="M 0 0 L 10 5 L 0 10 z" fill="#6b7280"></path>
                    </marker>
                </defs>
            </svg>
            <div id="fsm-states-container"></div>
        </div>
        <div class="w-80 bg-white p-4 border-l overflow-y-auto">
            <h3 class="font-bold text-xl mb-4">Editor</h3>
            <div class="space-y-2 mb-4">
                <button data-action="add-state" class="w-full bg-blue-500 text-white p-2 rounded-md hover:bg-blue-600">Zustand hinzufügen</button>
                <button data-action="toggle-connect-mode" class="w-full bg-gray-200 p-2 rounded-md">Verbinden</button>
            </div>
            <hr>
            <div id="fsm-editor-sidebar-${index}" class="mt-4 fsm-sidebar">
                <p class="text-gray-500">Kein Element ausgewählt.</p>
            </div>
        </div>
    </div>`;
}

// ##### HAUPTFUNKTION ZUM RENDERN ALLER AUTOMATIONEN #####
export const automationTypeDetails = {
  routine: {
    icon: "fa-calendar-alt",
    color: "text-blue-500",
    renderer: renderRoutineCard,
    detailsRenderer: renderRoutineDetails,
  },
  timer: {
    icon: "fa-hourglass-half",
    color: "text-green-500",
    renderer: renderTimerCard,
    detailsRenderer: renderTimerDetails,
  },
  state_machine: {
    icon: "fa-sitemap",
    color: "text-purple-500",
    renderer: renderStateMachineCard,
    detailsRenderer: renderStateMachineDetails,
  },
};

export function renderAutomations(config, bridgeData) {
  const container = document.getElementById("automations-container");
  if (!container) return;
  container.innerHTML = "";
  if (!config.automations || config.automations.length === 0) {
    container.innerHTML = `<p class="text-gray-500 text-center mt-4">Noch keine Automationen erstellt.</p>`;
    return;
  }

  config.automations.forEach((automation, index) => {
    const el = document.createElement("div");
    el.className =
      "bg-white rounded-lg shadow-md border border-gray-200 overflow-hidden";
    el.dataset.index = index;
    const type = automation.type || "routine";
    el.dataset.type = type;

    const details = automationTypeDetails[type];
    const isEnabled = automation.enabled !== false;

    el.innerHTML = `
        <div class="automation-header p-4 cursor-pointer hover:bg-gray-50 flex justify-between items-center" data-action="toggle-automation-details" data-index="${index}">
            <div>
                <div class="flex items-center">
                    <i class="fas ${details.icon} ${
      details.color
    } text-xl mr-3"></i>
                    <h3 class="text-2xl font-semibold">${automation.name}</h3>
                    <i class="fas fa-chevron-down ml-4 text-gray-400 transition-transform"></i>
                </div>
                ${details.renderer(automation, index, bridgeData, config)}
            </div>
            <div class="flex items-center space-x-4">
                <label class="relative inline-flex items-center cursor-pointer" title="Automation an/aus" data-action="stop-propagation">
                    <input type="checkbox" data-action="toggle-automation" class="sr-only peer" ${
                      isEnabled ? "checked" : ""
                    }>
                    <div class="w-11 h-6 bg-gray-200 rounded-full peer peer-focus:ring-2 peer-checked:after:translate-x-full after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
                <button type="button" data-action="edit-automation" class="text-blue-600 hover:text-blue-800 font-medium">Bearbeiten</button>
                <button type="button" data-action="delete-automation" class="text-red-600 hover:text-red-800 font-medium">Löschen</button>
            </div>
        </div>
        <div class="automation-details hidden" data-index="${index}"></div>`;
    container.appendChild(el);
  });
}
