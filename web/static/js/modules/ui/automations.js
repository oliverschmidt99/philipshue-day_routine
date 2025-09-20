import { icons, periodNames, sectionColors } from "./shared.js";

export function renderRoutines(config, bridgeData) {
  const routinesContainer = document.getElementById("routines-container");
  if (!routinesContainer) return;
  routinesContainer.innerHTML = "";
  if (!config.routines || config.routines.length === 0) {
    routinesContainer.innerHTML = `<p class="text-gray-500 text-center mt-4">Noch keine Routinen erstellt.</p>`;
    return;
  }
  config.routines.forEach((routine, index) => {
    const routineEl = document.createElement("div");
    routineEl.className =
      "bg-white rounded-lg shadow-md border border-gray-200 overflow-hidden";
    routineEl.dataset.index = index;

    const roomConf = config.rooms.find((r) => r.name === routine.room_name);
    const sensorId = roomConf ? roomConf.sensor_id : null;
    const sensor = sensorId
      ? bridgeData.sensors.find((s) => s.id == sensorId)
      : null;
    const sensorHtml = sensor
      ? `<span class="mx-2 text-gray-400">|</span> <span class="flex items-center"><i class="fas fa-satellite-dish mr-2 text-teal-500"></i> ${sensor.name}</span>`
      : "";
    const dailyTime = routine.daily_time || {};
    const isEnabled = routine.enabled !== false;

    routineEl.innerHTML = `
        <div class="routine-header p-4 cursor-pointer hover:bg-gray-50 flex justify-between items-center" data-action="toggle-routine-details" data-index="${index}">
            <div>
                <div class="flex items-center">
                    <h3 class="text-2xl font-semibold">${routine.name}</h3>
                    <i class="fas fa-chevron-down ml-4 text-gray-400 transition-transform"></i>
                </div>
                <div class="flex items-center text-gray-500 text-sm mt-1">
                    <p><i class="fas fa-layer-group mr-2 text-indigo-500"></i>${
                      routine.room_name
                    }</p>
                    ${sensorHtml}
                    <span class="mx-2 text-gray-400">|</span>
                    <p><i class="far fa-clock mr-2 text-blue-500"></i>Aktiv: ${String(
                      dailyTime.H1 || 0
                    ).padStart(2, "0")}:${String(dailyTime.M1 || 0).padStart(
      2,
      "0"
    )} - ${String(dailyTime.H2 || 23).padStart(2, "0")}:${String(
      dailyTime.M2 || 59
    ).padStart(2, "0")}</p>
                </div>
            </div>
            <div class="flex items-center space-x-4">
                <label class="relative inline-flex items-center cursor-pointer" title="Routine an/aus" data-action="stop-propagation">
                    <input type="checkbox" data-action="toggle-routine" class="sr-only peer" ${
                      isEnabled ? "checked" : ""
                    }>
                    <div class="w-11 h-6 bg-gray-200 rounded-full peer peer-focus:ring-2 peer-checked:after:translate-x-full after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
                <button type="button" data-action="edit-routine" class="text-blue-600 hover:text-blue-800 font-medium">Bearbeiten</button>
                <button type="button" data-action="delete-routine" class="text-red-600 hover:text-red-800 font-medium">Löschen</button>
            </div>
        </div>
        <div class="routine-details px-4 pb-4 hidden" data-index="${index}">
            </div>`;
    routinesContainer.appendChild(routineEl);
  });
}

export function renderRoutineDetails(routine, scenes) {
  const sceneOptions = Object.keys(scenes)
    .map(
      (name) =>
        `<option value="${name}" ${
          name === "aus" ? "selected" : ""
        }>${name.replace(/_/g, " ")}</option>`
    )
    .join("");

  return `
    <div class="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-4 border-t pt-4 mt-2">
        <div>
            <h4 class="text-lg font-semibold mb-2 text-gray-700">Allgemeiner Zeitplan</h4>
            <div class="flex items-center space-x-2">
                <input type="time" data-period="daily_time" data-key="H1" value="${String(
                  routine.daily_time.H1 || 0
                ).padStart(2, "0")}:${String(
    routine.daily_time.M1 || 0
  ).padStart(2, "0")}" class="p-2 border rounded-md">
                <span>bis</span>
                <input type="time" data-period="daily_time" data-key="H2" value="${String(
                  routine.daily_time.H2 || 23
                ).padStart(2, "0")}:${String(
    routine.daily_time.M2 || 59
  ).padStart(2, "0")}" class="p-2 border rounded-md">
            </div>
        </div>
        <div> </div>
        ${["morning", "day", "evening", "night"]
          .map(
            (period) => `
        <div class="p-4 rounded-lg border ${sectionColors[period]}">
            <h5 class="font-bold text-xl mb-3 flex items-center">${
              icons[period]
            } ${periodNames[period]}</h5>
            <div class="space-y-3 text-sm">
                <div class="flex items-center justify-between">
                    <label>Normal-Szene:</label>
                    <select data-period="${period}" data-key="scene_name" class="p-1 border rounded-md">${sceneOptions.replace(
              `value="${routine[period].scene_name}"`,
              `value="${routine[period].scene_name}" selected`
            )}</select>
                </div>
                <div class="flex items-center justify-between">
                    <label>Bewegungs-Szene:</label>
                    <select data-period="${period}" data-key="x_scene_name" class="p-1 border rounded-md">${sceneOptions.replace(
              `value="${routine[period].x_scene_name}"`,
              `value="${routine[period].x_scene_name}" selected`
            )}</select>
                </div>
                <div class="flex items-center justify-between">
                    <label>Wartezeit (Min/Sek):</label>
                    <div class="flex items-center space-x-1">
                       <input type="number" min="0" data-period="${period}" data-key="wait_time.min" value="${
              routine[period].wait_time.min
            }" class="w-16 p-1 border rounded-md">
                       <input type="number" min="0" max="59" data-period="${period}" data-key="wait_time.sec" value="${
              routine[period].wait_time.sec
            }" class="w-16 p-1 border rounded-md">
                    </div>
                </div>
                <div class="border-t pt-3 space-y-2">
                    <label class="flex items-center"><input type="checkbox" data-period="${period}" data-key="motion_check" ${
              routine[period].motion_check ? "checked" : ""
            } class="mr-2 h-4 w-4"> Auf Bewegung reagieren</label>
                    <label class="flex items-center"><input type="checkbox" data-period="${period}" data-key="do_not_disturb" ${
              routine[period].do_not_disturb ? "checked" : ""
            } class="mr-2 h-4 w-4"> Bitte nicht stören</label>
                    <label class="flex items-center"><input type="checkbox" data-period="${period}" data-key="bri_check" ${
              routine[period].bri_check ? "checked" : ""
            } class="mr-2 h-4 w-4"> Helligkeits-Check</label>
                </div>
            </div>
        </div>
        `
          )
          .join("")}
    </div>`;
}
