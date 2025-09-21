import { icons, periodNames, sectionColors } from "./shared.js";
import { initFsmEditor } from "./fsm-editor.js";

// ##### KARTEN FÜR DIE ÜBERSICHTSSEITE (JETZT IM GLOBALEN SCOPE) #####

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
    ? `<span class="mx-2 text-gray-500">|</span> <span class="flex items-center" title="Sensor"><i class="fas fa-satellite-dish mr-2 text-teal-400"></i> ${sensor.name}</span>`
    : "";
  const dailyTime = automation.daily_time || {};

  return `
        <div class="flex flex-wrap items-center text-gray-400 text-sm mt-1">
            <p title="Raum/Zone" class="flex items-center mr-3"><i class="fas fa-layer-group mr-2 text-indigo-400"></i>${
              automation.room_name
            }</p>
            ${sensorHtml}
            <p title="Aktivitätszeitraum" class="flex items-center mt-1 md:mt-0"><i class="far fa-clock mr-2 text-blue-400"></i>${String(
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
        <div class="flex items-center text-gray-400 text-sm mt-1">
             <p title="Ziel-Gerät/Raum" class="flex items-center"><i class="fas fa-bullseye mr-2 text-purple-400"></i>${
               automation.action?.target_room || "N/A"
             }</p>
            <span class="mx-2 text-gray-500">|</span>
            <p title="Dauer" class="flex items-center"><i class="fas fa-stopwatch mr-2 text-green-400"></i>${
              automation.duration_minutes
            } Minuten</p>
        </div>
    `;
}

function renderStateMachineCard(automation) {
  const stateCount = automation.states?.length || 0;
  const transitionCount = automation.transitions?.length || 0;
  return `
        <div class="flex items-center text-gray-400 text-sm mt-1">
            <p title="Ziel-Gerät/Raum" class="flex items-center"><i class="fas fa-bullseye mr-2 text-purple-400"></i>${
              automation.target_room || "N/A"
            }</p>
            <span class="mx-2 text-gray-500">|</span>
            <p title="Zustände" class="flex items-center"><i class="fas fa-project-diagram mr-2 text-orange-400"></i> ${stateCount} Zustände</p>
             <span class="mx-2 text-gray-500">|</span>
            <p title="Übergänge" class="flex items-center"><i class="fas fa-exchange-alt mr-2 text-red-400"></i> ${transitionCount} Übergänge</p>
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

  return `
    <div class="p-4 bg-gray-700 text-gray-200">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-4 pt-4 mt-2">
            <div>
                <h4 class="text-lg font-semibold mb-2 text-gray-200">Allgemeiner Zeitplan</h4>
                <div class="flex items-center space-x-2">
                    <input type="time" data-period="daily_time" data-key="H1" value="${String(
                      automation.daily_time.H1 || 0
                    ).padStart(2, "0")}:${String(
    automation.daily_time.M1 || 0
  ).padStart(
    2,
    "0"
  )}" class="p-2 border rounded-md bg-gray-800 border-gray-600 text-gray-200">
                    <span>bis</span>
                    <input type="time" data-period="daily_time" data-key="H2" value="${String(
                      automation.daily_time.H2 || 23
                    ).padStart(2, "0")}:${String(
    automation.daily_time.M2 || 59
  ).padStart(
    2,
    "0"
  )}" class="p-2 border rounded-md bg-gray-800 border-gray-600 text-gray-200">
                </div>
            </div>
            <div> </div>
            ${["morning", "day", "evening", "night"]
              .map(
                (period) => `
            <div class="p-4 rounded-lg border border-gray-600 bg-gray-800">
                <h5 class="font-bold text-xl mb-3 flex items-center">${
                  icons[period]
                } ${periodNames[period]}</h5>
                <div class="space-y-3 text-sm">
                    <div class="flex items-center justify-between">
                        <label>Normal-Szene:</label>
                        <select data-period="${period}" data-key="scene_name" class="p-1 border rounded-md bg-gray-900 border-gray-600 text-gray-200">${sceneOptions.replace(
                  `value="${automation[period].scene_name}"`,
                  `value="${automation[period].scene_name}" selected`
                )}</select>
                    </div>
                    <div class="flex items-center justify-between">
                        <label>Bewegungs-Szene:</label>
                        <select data-period="${period}" data-key="x_scene_name" class="p-1 border rounded-md bg-gray-900 border-gray-600 text-gray-200">${sceneOptions.replace(
                  `value="${automation[period].x_scene_name}"`,
                  `value="${automation[period].x_scene_name}" selected`
                )}</select>
                    </div>
                    <div class="flex items-center justify-between">
                        <label>Wartezeit (Min/Sek):</label>
                        <div class="flex items-center space-x-1">
                           <input type="number" min="0" data-period="${period}" data-key="wait_time.min" value="${
                  automation[period].wait_time.min
                }" class="w-16 p-1 border rounded-md bg-gray-900 border-gray-600 text-gray-200">
                           <input type="number" min="0" max="59" data-period="${period}" data-key="wait_time.sec" value="${
                  automation[period].wait_time.sec
                }" class="w-16 p-1 border rounded-md bg-gray-900 border-gray-600 text-gray-200">
                        </div>
                    </div>
                    <div class="border-t border-gray-600 pt-3 space-y-2">
                        <label class="flex items-center"><input type="checkbox" data-period="${period}" data-key="motion_check" ${
                  automation[period].motion_check ? "checked" : ""
                } class="mr-2 h-4 w-4 rounded bg-gray-600 border-gray-500 text-blue-500 focus:ring-blue-400"> Auf Bewegung reagieren</label>
                        <label class="flex items-center"><input type="checkbox" data-period="${period}" data-key="do_not_disturb" ${
                  automation[period].do_not_disturb ? "checked" : ""
                } class="mr-2 h-4 w-4 rounded bg-gray-600 border-gray-500 text-blue-500 focus:ring-blue-400"> Bitte nicht stören</label>
                        <label class="flex items-center"><input type="checkbox" data-period="${period}" data-key="bri_check" ${
                  automation[period].bri_check ? "checked" : ""
                } class="mr-2 h-4 w-4 rounded bg-gray-600 border-gray-500 text-blue-500 focus:ring-blue-400"> Helligkeits-Check</label>
                    </div>
                </div>
            </div>`
              )
              .join("")}
        </div>
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
    <div class="p-4 space-y-4 bg-gray-700 text-gray-200">
        <div>
            <label class="block text-sm font-medium text-gray-300">Name</label>
            <input type="text" class="mt-1 block w-full rounded-md bg-gray-800 border-gray-600 shadow-sm text-gray-200" value="${automation.name}">
        </div>
        <div>
            <label class="block text-sm font-medium text-gray-300">Dauer (Minuten)</label>
            <input type="number" min="1" class="mt-1 block w-full rounded-md bg-gray-800 border-gray-600 shadow-sm text-gray-200" value="${automation.duration_minutes}">
        </div>
        <div class="p-4 border rounded-md border-gray-600 bg-gray-800">
            <h4 class="font-semibold mb-2 text-gray-200">Auslöser (Trigger)</h4>
            <p class="text-gray-400 text-sm">TODO: UI für Trigger-Auswahl</p>
        </div>
        <div class="p-4 border rounded-md border-gray-600 bg-gray-800">
            <h4 class="font-semibold mb-2 text-gray-200">Aktion (nach Ablauf)</h4>
            <div class="space-y-2">
                <select class="block w-full rounded-md bg-gray-900 border-gray-600 shadow-sm text-gray-200">${roomOptions}</select>
                <select class="block w-full rounded-md bg-gray-900 border-gray-600 shadow-sm text-gray-200">${sceneOptions}</select>
            </div>
        </div>
    </div>`;
}

function renderStateMachineDetails(automation, bridgeData, index) {
  return `
    <div class="fsm-editor-container flex h-[600px] bg-gray-900">
        <div id="fsm-editor-canvas-${index}" class="fsm-canvas flex-grow relative bg-gray-700 overflow-hidden">
            <svg class="absolute top-0 left-0 w-full h-full pointer-events-none">
                <defs>
                    <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                        <path d="M 0 0 L 10 5 L 0 10 z" fill="#9ca3af"></path>
                    </marker>
                </defs>
            </svg>
            <div id="fsm-states-container"></div>
        </div>
        <div class="fsm-sidebar w-80 bg-gray-800 p-4 border-l border-gray-700 overflow-y-auto text-gray-200">
            <h3 class="font-bold text-xl mb-4">Editor</h3>
            <div class="space-y-2 mb-4">
                <button data-action="add-state" class="w-full bg-blue-600 text-white p-2 rounded-md hover:bg-blue-700">Zustand hinzufügen</button>
                <button data-action="toggle-connect-mode" class="w-full bg-gray-600 hover:bg-gray-500 p-2 rounded-md">Verbinden</button>
            </div>
            <hr class="border-gray-600">
            <div id="fsm-editor-sidebar-${index}" class="mt-4">
                <p class="text-gray-400">Kein Element ausgewählt.</p>
            </div>
        </div>
    </div>`;
}

// ##### HAUPTFUNKTION ZUM RENDERN ALLER AUTOMATIONEN #####
export const automationTypeDetails = {
  routine: {
    icon: "fa-calendar-alt",
    color: "text-blue-400",
    renderer: renderRoutineCard,
    detailsRenderer: renderRoutineDetails,
  },
  timer: {
    icon: "fa-hourglass-half",
    color: "text-green-400",
    renderer: renderTimerCard,
    detailsRenderer: renderTimerDetails,
  },
  state_machine: {
    icon: "fa-sitemap",
    color: "text-purple-400",
    renderer: renderStateMachineCard,
    detailsRenderer: renderStateMachineDetails,
  },
};

export function renderAutomations(config, bridgeData) {
  const container = document.getElementById("automations-container");
  if (!container) return;
  container.innerHTML = "";
  if (!config.automations || config.automations.length === 0) {
    container.innerHTML = `<p class="text-gray-400 text-center mt-4">Noch keine Automationen erstellt.</p>`;
    return;
  }

  config.automations.forEach((automation, index) => {
    const el = document.createElement("div");
    el.className =
      "bg-gray-800 rounded-lg shadow-md border border-gray-700 overflow-hidden text-gray-200";
    el.dataset.index = index;
    const type = automation.type || "routine";
    el.dataset.type = type;

    const details = automationTypeDetails[type];
    const isEnabled = automation.enabled !== false;

    el.innerHTML = `
        <div class="automation-header p-4 cursor-pointer hover:bg-gray-700 flex justify-between items-center" data-action="toggle-automation-details" data-index="${index}">
            <div>
                <div class="flex items-center">
                    <i class="fas ${details.icon} ${
      details.color
    } text-xl mr-3"></i>
                    <h3 class="text-2xl font-semibold text-gray-100">${
                      automation.name
                    }</h3>
                    <i class="fas fa-chevron-down ml-4 text-gray-500 transition-transform"></i>
                </div>
                ${details.renderer(automation, index, bridgeData, config)}
            </div>
            <div class="flex items-center space-x-4">
                <label class="relative inline-flex items-center cursor-pointer" title="Automation an/aus" data-action="stop-propagation">
                    <input type="checkbox" data-action="toggle-automation" class="sr-only peer" ${
                      isEnabled ? "checked" : ""
                    }>
                    <div class="w-11 h-6 bg-gray-600 rounded-full peer peer-focus:ring-2 peer-checked:after:translate-x-full after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
                <button type="button" data-action="edit-automation" class="text-blue-400 hover:text-blue-300 font-medium">Bearbeiten</button>
                <button type="button" data-action="delete-automation" class="text-red-500 hover:text-red-400 font-medium">Löschen</button>
            </div>
        </div>
        <div class="automation-details hidden" data-index="${index}"></div>`;
    container.appendChild(el);
  });
}
