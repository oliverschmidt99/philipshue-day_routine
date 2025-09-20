// web/static/js/modules/ui.js
export const icons = {
  morning: "🌅",
  day: "☀️",
  evening: "🌇",
  night: "🌙",
  sun: "🌞",
  sensor: "💡",
};
export const sectionColors = {
  morning: "bg-yellow-100 border-yellow-200",
  day: "bg-sky-100 border-sky-200",
  evening: "bg-orange-100 border-orange-200",
  night: "bg-indigo-100 border-indigo-200",
};
export const periodNames = {
  morning: "Morgen",
  day: "Tag",
  evening: "Abend",
  night: "Nacht",
};

const routinesContainer = document.getElementById("routines-container");
const scenesContainer = document.getElementById("scenes-container");
const statusContainer = document.getElementById("status-container");
const logContainer = document.getElementById("log-container");
const toastElement = document.getElementById("toast");
const clockElement = document.getElementById("clock");
const sunTimesContainer = document.getElementById("sun-times");
const modalSceneContainer = document.getElementById("modal-scene");
const modalRoutineContainer = document.getElementById("modal-routine");
const homeContainer = document.getElementById("home-container");

export function showToast(message, isError = false) {
  if (!toastElement) return;
  toastElement.textContent = message;
  toastElement.className = `fixed bottom-5 right-5 text-white py-2 px-4 rounded-lg shadow-xl transition-all duration-300 transform-gpu ${
    isError ? "bg-red-600" : "bg-gray-900"
  } translate-y-20 opacity-0`;
  toastElement.classList.remove("hidden");
  void toastElement.offsetWidth;
  toastElement.classList.remove("translate-y-20", "opacity-0");
  setTimeout(() => {
    toastElement.classList.add("translate-y-20", "opacity-0");
    setTimeout(() => toastElement.classList.add("hidden"), 300);
  }, 4000);
}

export function updateClock() {
  if (clockElement)
    clockElement.textContent = new Date().toLocaleTimeString("de-DE");
}

export function closeModal() {
  [modalSceneContainer, modalRoutineContainer].forEach((modal) => {
    if (modal) {
      modal.classList.add("hidden");
      modal.innerHTML = "";
    }
  });
}

export function renderSunTimes(sunData) {
  if (sunTimesContainer) {
    if (sunData && sunData.sunrise) {
      const sunrise = new Date(sunData.sunrise).toLocaleTimeString("de-DE", {
        hour: "2-digit",
        minute: "2-digit",
      });
      const sunset = new Date(sunData.sunset).toLocaleTimeString("de-DE", {
        hour: "2-digit",
        minute: "2-digit",
      });
      sunTimesContainer.innerHTML = `<span>🌅 ${sunrise}</span> <span class="ml-2">🌇 ${sunset}</span>`;
    } else {
      sunTimesContainer.innerHTML = `<span>--:--</span>`;
    }
  }
}

export function renderHome(bridgeData, groupedLights) {
  if (!homeContainer) return;

  const groups = [...bridgeData.rooms, ...bridgeData.zones];
  homeContainer.innerHTML = ""; // Clear existing cards

  groups.forEach((group) => {
    const groupedLight = groupedLights.find((gl) => gl.owner.rid === group.id);
    if (!groupedLight) return;

    const isOn = groupedLight.on.on;
    const brightness = isOn ? groupedLight.dimming.brightness : 0;

    let colorIndicatorStyle = "background-color: #e5e7eb;"; // Default gray
    if (isOn) {
      colorIndicatorStyle = "background-color: #fef08a;"; // Yellowish for 'on'
    }

    const card = `
            <div class="room-card bg-white rounded-lg shadow-md p-4 flex flex-col justify-between" data-room-id="${
              group.id
            }">
                <div class="cursor-pointer" data-action="open-room-control">
                    <div class="flex justify-between items-start">
                        <h3 class="text-xl font-bold text-gray-800">${
                          group.name
                        }</h3>
                        <div class="w-6 h-6 rounded-full border border-gray-300" style="${colorIndicatorStyle}"></div>
                    </div>
                    <p class="text-sm text-gray-500">${
                      isOn ? `An - ${brightness.toFixed(0)}%` : "Aus"
                    }</p>
                </div>
                <div class="mt-4">
                    <div class="flex items-center space-x-4">
                        <button data-action="toggle-group-power" data-group-id="${
                          group.id
                        }" data-action-type="${
      isOn ? "off" : "on"
    }" class="text-gray-500 hover:text-blue-600 focus:outline-none">
                            <i class="fas fa-power-off fa-2x"></i>
                        </button>
                        <input type="range" min="1" max="100" value="${brightness}" ${
      !isOn ? "disabled" : ""
    } 
                               data-action="set-group-brightness" data-group-id="${
                                 group.id
                               }" 
                               class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer brightness-slider">
                    </div>
                </div>
            </div>
        `;
    homeContainer.innerHTML += card;
  });
}

export function openRoomControlModal(room, allLights, allScenes) {
  const roomLights = allLights.filter((light) =>
    room.lights.includes(light.id)
  );
  const roomScenes = allScenes.filter((scene) => scene.group.rid === room.id);

  let lightsHtml = roomLights
    .map((light) => {
      const isOn = light.on.on;
      const brightness = light.dimming?.brightness || 0;
      return `
        <div class="flex items-center justify-between p-2 bg-gray-100 rounded-md">
            <span class="font-medium">${light.metadata.name}</span>
            <div class="flex items-center space-x-4">
                <input type="range" min="1" max="100" value="${brightness}" ${
        !isOn ? "disabled" : ""
      } 
                       data-action="set-light-brightness" data-light-id="${
                         light.id
                       }" 
                       class="w-32 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer brightness-slider">
                <button data-action="toggle-light-power" data-light-id="${
                  light.id
                }" data-action-type="${isOn ? "off" : "on"}" 
                        class="text-gray-600 hover:text-blue-600 focus:outline-none text-xl">
                    <i class="fas fa-power-off"></i>
                </button>
            </div>
        </div>
    `;
    })
    .join("");

  let scenesHtml = roomScenes
    .map(
      (scene) => `
        <button class="bg-blue-100 text-blue-800 py-2 px-4 rounded-lg hover:bg-blue-200" 
                data-action="recall-scene" 
                data-scene-id="${scene.id}"
                data-group-id="${room.id}">
            ${scene.metadata.name}
        </button>
    `
    )
    .join("");

  const modalHtml = `
    <div class="modal-backdrop fixed inset-0 z-50 overflow-auto flex items-center justify-center bg-black bg-opacity-50" data-action="cancel-modal" data-group-id="${
      room.id
    }">
        <div class="bg-white rounded-lg shadow-xl w-full max-w-lg m-4">
            <div class="p-6">
                <h3 class="text-2xl font-bold mb-4">${room.name}</h3>
                <div class="space-y-4">
                    <div>
                        <h4 class="font-semibold mb-2">Einzelne Lampen</h4>
                        <div class="space-y-2">${
                          lightsHtml.length > 0
                            ? lightsHtml
                            : '<p class="text-gray-500">Keine Lampen in dieser Gruppe.</p>'
                        }</div>
                    </div>
                    <div>
                        <h4 class="font-semibold mb-2">Szenen</h4>
                        <div class="flex flex-wrap gap-2">${scenesHtml}</div>
                    </div>
                </div>
            </div>
            <div class="bg-gray-50 px-6 py-3 flex justify-end">
                <button type="button" data-action="cancel-modal" class="bg-white py-2 px-4 border rounded-md">Schließen</button>
            </div>
        </div>
    </div>
    `;

  modalSceneContainer.innerHTML = modalHtml;
  modalSceneContainer.classList.remove("hidden");
}

export function renderStatus(statuses, sunTimes, openStates = []) {
  if (!statusContainer) return;
  statusContainer.innerHTML = "";
  if (!statuses || statuses.length === 0) {
    statusContainer.innerHTML = `<p class="text-gray-500 text-center mt-4">Keine Routinen aktiv oder Status wird geladen...</p>`;
    return;
  }
  statuses.forEach((status) => {
    statusContainer.innerHTML += renderStatusTimeline(status, sunTimes);
  });
  document.querySelectorAll(".status-card").forEach((card) => {
    const name = card.querySelector("h4")?.textContent;
    if (name && openStates.includes(name)) {
      toggleDetails(card.querySelector(".status-header"), true);
    }
  });
}

export function renderLog(logText) {
  if (!logContainer) return;
  const isScrolledToBottom =
    logContainer.scrollHeight - logContainer.clientHeight <=
    logContainer.scrollTop + 1;
  logContainer.textContent = logText || "Log-Datei wird geladen...";
  if (isScrolledToBottom) {
    logContainer.scrollTop = logContainer.scrollHeight;
  }
}

export function populateAnalyseSensors(sensors) {
  const sensorSelect = document.getElementById("analyse-sensor");
  if (!sensorSelect) return;
  sensorSelect.innerHTML = "";

  // Filtert nur Sensoren, die für die Analyse relevant sind (z.B. Bewegungssensoren)
  const relevantSensors = sensors.filter((s) => s.type === "ZLLPresence");

  if (!relevantSensors || relevantSensors.length === 0) {
    sensorSelect.innerHTML =
      "<option>Keine Bewegungssensoren gefunden</option>";
    return;
  }
  relevantSensors.forEach((sensor) => {
    const option = document.createElement("option");
    option.value = sensor.id;
    option.textContent = sensor.name;
    sensorSelect.appendChild(option);
  });
}

export function renderChart(chartInstance, data) {
  const ctx = document.getElementById("sensor-chart")?.getContext("2d");
  if (!ctx) return null;
  if (chartInstance) chartInstance.destroy();

  if (!data || !Array.isArray(data.labels) || data.labels.length === 0) {
    ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
    ctx.font = "16px Inter, sans-serif";
    ctx.fillStyle = "#6b7280";
    ctx.textAlign = "center";
    ctx.fillText(
      "Keine Daten für diesen Zeitraum verfügbar.",
      ctx.canvas.width / 2,
      50
    );
    return null;
  }

  const brightnessData = data.brightness || [];
  const temperatureData = data.temperature || [];

  return new Chart(ctx, {
    type: "line",
    data: {
      labels: data.labels,
      datasets: [
        {
          label: "Helligkeit",
          data: brightnessData,
          borderColor: "rgba(234, 179, 8, 1)",
          yAxisID: "y",
          tension: 0.2,
          pointRadius: 0,
        },
        {
          label: "Temperatur (°C)",
          data: temperatureData,
          borderColor: "rgba(37, 99, 235, 1)",
          yAxisID: "y1",
          tension: 0.2,
          pointRadius: 0,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          type: "time",
          time: { unit: "hour", tooltipFormat: "dd.MM.yyyy HH:mm" },
        },
        y: {
          position: "left",
          title: { display: true, text: "Helligkeit", color: "#b45309" },
        },
        y1: {
          position: "right",
          title: { display: true, text: "Temperatur (°C)", color: "#2563eb" },
          grid: { drawOnChartArea: false },
        },
      },
    },
  });
}

export function renderRoutines(config, bridgeData) {
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

export function renderScenes(scenes) {
  if (!scenesContainer) return;
  scenesContainer.innerHTML = "";
  if (!scenes || Object.keys(scenes).length === 0) {
    scenesContainer.innerHTML = `<p class="text-gray-500 text-center mt-4">Noch keine Szenen erstellt.</p>`;
    return;
  }
  for (const [name, scene] of Object.entries(scenes)) {
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

export function openSceneModal(scene, sceneName) {
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
  const groupOptions = bridgeData.groups
    .map((g) => `<option value="${g.id}|${g.name}">${g.name}</option>`)
    .join("");
  const sensorOptions = bridgeData.sensors
    .map((s) => `<option value="${s.id}">${s.name}</option>`)
    .join("");
  modalRoutineContainer.innerHTML = `<div class="modal-backdrop fixed inset-0 z-50 overflow-auto flex items-center justify-center bg-black bg-opacity-50"><div class="bg-white rounded-lg shadow-xl w-full max-w-lg m-4"><div class="p-6"><h3 class="text-2xl font-bold mb-4">Neue Routine</h3><form class="space-y-4"><label for="new-routine-name" class="block text-sm font-medium">Name</label><input type="text" id="new-routine-name" required class="mt-1 block w-full rounded-md border-gray-300"><label for="new-routine-group" class="block text-sm font-medium">Raum / Zone</label><select id="new-routine-group" class="mt-1 block w-full rounded-md border-gray-300">${groupOptions}</select><label for="new-routine-sensor" class="block text-sm font-medium">Sensor (Optional)</label><select id="new-routine-sensor" class="mt-1 block w-full rounded-md border-gray-300"><option value="">Kein Sensor</option>${sensorOptions}</select></form></div><div class="bg-gray-50 px-6 py-3 flex justify-end space-x-3"><button type="button" data-action="cancel-modal" class="bg-white py-2 px-4 border rounded-md">Abbrechen</button><button type="button" data-action="create-routine" class="bg-blue-600 text-white py-2 px-4 rounded-md">Erstellen</button></div></div></div>`;
  modalRoutineContainer.classList.remove("hidden");
}

export function toggleDetails(headerElement, forceOpen = false) {
  const details = headerElement.nextElementSibling;
  const icon = headerElement.querySelector("i.fa-chevron-down");
  if (!details || !icon) return;

  if (details.classList.contains("hidden") || forceOpen) {
    details.classList.remove("hidden");
    setTimeout(() => {
      details.style.maxHeight = details.scrollHeight + "px";
      icon.style.transform = "rotate(180deg)";
    }, 10);
  } else {
    details.style.maxHeight = "0px";
    icon.style.transform = "rotate(0deg)";
    details.addEventListener(
      "transitionend",
      () => {
        details.classList.add("hidden");
      },
      { once: true }
    );
  }
}

export function updateStatusTimelines() {
  document.querySelectorAll(".timeline-svg").forEach((svg) => {
    const sunEmoji = svg.querySelector(".sun-emoji-indicator");
    if (!sunEmoji) return;
    const sunriseMins = parseInt(sunEmoji.dataset.sunriseMins);
    const sunsetMins = parseInt(sunEmoji.dataset.sunsetMins);
    const now = new Date();
    const nowMins = now.getHours() * 60 + now.getMinutes();

    if (nowMins < sunriseMins || nowMins > sunsetMins) {
      sunEmoji.style.display = "none";
      return;
    }
    sunEmoji.style.display = "block";
    const dayDuration = sunsetMins - sunriseMins;
    const progress = (nowMins - sunriseMins) / dayDuration;
    const arcStartX = parseFloat(svg.dataset.arcStartX);
    const arcRadiusX = parseFloat(svg.dataset.radiusX);
    const arcRadiusY = parseFloat(svg.dataset.radiusY);
    const centerX = parseFloat(svg.dataset.centerX);
    const angle = Math.PI * progress;
    const x = centerX - Math.cos(angle) * arcRadiusX;
    const y = 180 - Math.sin(angle) * arcRadiusY;
    sunEmoji.setAttribute("transform", `translate(${x}, ${y})`);
  });
}

function renderStatusTimeline(status, sunTimes) {
  const timeToMinutes = (h, m) => (h || 0) * 60 + (m || 0);
  const routineStart = status.daily_time;
  const sunrise = sunTimes ? new Date(sunTimes.sunrise) : null;
  const sunset = sunTimes ? new Date(sunTimes.sunset) : null;

  const morningStartMins = timeToMinutes(routineStart.H1, routineStart.M1);
  const eveningEndMins = timeToMinutes(routineStart.H2, routineStart.M2);
  const sunriseMins = sunrise
    ? timeToMinutes(sunrise.getHours(), sunrise.getMinutes())
    : 390;
  const sunsetMins = sunset
    ? timeToMinutes(sunset.getHours(), sunset.getMinutes())
    : 1260;
  const timeToPercent = (mins) => 10 + (mins / 1439) * 80;
  const morningStartPercent = timeToPercent(morningStartMins);
  const eveningEndPercent = timeToPercent(eveningEndMins);
  const sunrisePercent = timeToPercent(sunriseMins);
  const sunsetPercent = timeToPercent(sunsetMins);
  const arcStartX = sunrisePercent * 10;
  const arcEndX = sunsetPercent * 10;
  const arcRadiusX = (arcEndX - arcStartX) / 2;
  const arcRadiusY = Math.min(150, arcRadiusX * 0.9);
  const centerX = arcStartX + arcRadiusX;
  const periodEmoji = { morning: "🌅", day: "☀️", evening: "🌇", night: "🌙" };
  const primaryEmoji = periodEmoji[status.period] || "🗓️";
  const primaryText =
    periodNames[status.period] || status.period || "Unbekannt";

  return `
    <div class="bg-white rounded-lg shadow border border-gray-200 status-card">
        <div class="status-header flex justify-between items-center cursor-pointer hover:bg-gray-50 p-2" data-action="toggle-status-details">
            <div class="flex items-center">
                <h4 class="font-bold text-lg">${status.name}</h4>
                <i class="fas fa-chevron-down ml-4 text-gray-400 transition-transform"></i>
            </div>
            <div class="flex items-center text-sm font-medium text-gray-700 bg-gray-100 px-3 py-1 rounded-full">
                <span class="mr-2">${primaryEmoji}</span>
                <span>${primaryText}</span>
            </div>
        </div>
        <div class="status-details px-4 hidden" style="max-height: 0; overflow: hidden; transition: max-height 0.4s ease-in-out;">
             <div class="w-full my-2 h-72 text-gray-700">
                <svg class="h-full w-full timeline-svg" viewBox="0 0 1000 240" font-family="Inter, sans-serif" font-size="12px" data-center-x="${centerX}" data-radius-x="${arcRadiusX}" data-radius-y="${arcRadiusY}" data-arc-start-x="${arcStartX}" data-arc-end-x="${arcEndX}">
                     <line x1="2%" y1="180" x2="98%" y2="180" stroke="#9ca3af" stroke-width="2" />
                     <path d="M 978 175 L 988 180 L 978 185 Z" fill="#9ca3af" />
                     <path d="M ${arcStartX} 180 A ${arcRadiusX} ${arcRadiusY} 0 0 1 ${arcEndX} 180" stroke="#f97316" stroke-width="2" fill="none" />
                    
                     <line x1="${morningStartPercent}%" y1="175" x2="${morningStartPercent}%" y2="185" stroke="#4b5563" stroke-width="2" />
                     <text x="${morningStartPercent}%" y="205" text-anchor="middle" font-size="12px">${String(
    routineStart.H1 || 0
  ).padStart(2, "0")}:${String(routineStart.M1 || 0).padStart(2, "0")}</text>
                     <line x1="${eveningEndPercent}%" y1="175" x2="${eveningEndPercent}%" y2="185" stroke="#4b5563" stroke-width="2" />
                     <text x="${eveningEndPercent}%" y="205" text-anchor="middle" font-size="12px">${String(
    routineStart.H2 || 23
  ).padStart(2, "0")}:${String(routineStart.M2 || 59).padStart(2, "0")}</text>

                     <g class="sun-emoji-indicator" data-sunrise-mins="${sunriseMins}" data-sunset-mins="${sunsetMins}"><text x="0" y="0" text-anchor="middle" font-size="28">${
    icons.sun
  }</text></g>
                 </svg>
             </div>
             <div class="text-sm grid grid-cols-2 md:grid-cols-4 gap-x-4 gap-y-2 border-t pt-2 pb-4">
                 <span><strong>Status:</strong> <span class="${
                   status.enabled ? "text-green-600" : "text-red-500"
                 }">${
    status.enabled ? "Aktiviert" : "Deaktiviert"
  }</span></span>
                 <span><strong>Bewegung:</strong> ${status.motion_status}</span>
                 <span><strong>Letzte Szene:</strong> ${
                   status.last_scene
                 }</span>
             </div>
        </div>
    </div>`;
}

export function renderBridgeDevices(bridgeData) {
  const roomsContainer = document.getElementById("bridge-content-rooms");
  const zonesContainer = document.getElementById("bridge-content-zones");
  const sensorsContainer = document.getElementById("bridge-content-sensors");

  if (!roomsContainer || !zonesContainer || !sensorsContainer) return;

  // --- Räume rendern ---
  roomsContainer.innerHTML = createDeviceListHTML(
    bridgeData.rooms,
    "Raum",
    "Anzahl Lichter"
  );

  // --- Zonen rendern ---
  zonesContainer.innerHTML = createDeviceListHTML(
    bridgeData.zones,
    "Zone",
    "Anzahl Lichter"
  );

  // --- Sensoren rendern ---
  let sensorsHTML = "";
  if (
    bridgeData.sensors_categorized &&
    Object.keys(bridgeData.sensors_categorized).length > 0
  ) {
    for (const [category, sensorList] of Object.entries(
      bridgeData.sensors_categorized
    )) {
      sensorsHTML += `<h3 class="text-xl font-semibold mb-3 mt-4 text-gray-700">${category}</h3>`;
      sensorsHTML += createDeviceListHTML(sensorList, "Gerätename", "Modell");
    }
  } else {
    sensorsHTML = `<p class="text-gray-500">Keine Sensoren gefunden.</p>`;
  }
  sensorsContainer.innerHTML = sensorsHTML;
}

/**
 * Helfer-Funktion, um eine HTML-Liste für Geräte zu erstellen.
 */
function createDeviceListHTML(items, nameHeader, detailHeader) {
  if (!items || items.length === 0) {
    return `<p class="text-gray-500">Keine Geräte in dieser Kategorie gefunden.</p>`;
  }

  let html = `<div class="space-y-2">`;
  items.forEach((item) => {
    let detail = "";
    if (item.lights) {
      // Für Räume/Zonen
      detail = `${item.lights.length}`;
    } else if (item.productname) {c
      // Für Sensoren
      detail = item.productname;
    }

    html += `
        <div class="bg-white p-3 rounded-lg shadow-sm border flex justify-between items-center">
          <div>
            <span class="font-medium text-gray-800">${item.name}</span>
            <span class="block text-xs text-gray-500">${detailHeader}: ${detail}</span>
          </div>
          <span class="text-sm text-gray-500 font-mono">ID: ${item.id}</span>
        </div>`;
  });
  html += `</div>`;
  return html;
}
