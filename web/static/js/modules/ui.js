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
const bridgeDevicesContainer = document.getElementById(
  "bridge-devices-container"
);

export function showToast(message, isError = false) {
  if (!toastElement) return;
  toastElement.textContent = message;
  toastElement.className = `fixed bottom-5 right-5 text-white py-2 px-4 rounded-lg shadow-xl transition-opacity duration-300 ${
    isError ? "bg-red-600" : "bg-gray-900"
  }`;
  toastElement.classList.remove("hidden");
  setTimeout(() => toastElement.classList.add("hidden"), 4000);
}

export function updateClock() {
  if (clockElement)
    clockElement.textContent = new Date().toLocaleTimeString("de-DE");
}

export function closeModal() {
  modalSceneContainer.classList.add("hidden");
  modalRoutineContainer.classList.add("hidden");
  modalSceneContainer.innerHTML = "";
  modalRoutineContainer.innerHTML = "";
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

export function renderStatus(statuses, sunTimes, openStates = []) {
  if (!statusContainer) return;
  statusContainer.innerHTML = "";
  if (!statuses || statuses.length === 0) {
    statusContainer.innerHTML = `<p class="text-gray-500 text-center mt-4">Keine Routinen aktiv. Status wird geladen...</p>`;
    return;
  }
  statuses.forEach((status) => {
    statusContainer.innerHTML += renderStatusTimeline(status, sunTimes);
  });

  // Klappt die Elemente wieder auf, die vor dem Refresh offen waren
  document.querySelectorAll(".status-card").forEach((card) => {
    const name = card.querySelector("h4")?.textContent;
    if (name && openStates.includes(name)) {
      const details = card.querySelector(".status-details");
      const icon = card.querySelector(".status-header i");
      if (details && icon) {
        details.style.maxHeight = details.scrollHeight + "px";
        icon.style.transform = "rotate(180deg)";
      }
    }
  });
}

export function renderLog(logText) {
  if (!logContainer) return;
  logContainer.textContent = logText || "Log-Datei wird geladen...";
  logContainer.scrollTop = logContainer.scrollHeight;
}

export function renderBridgeDevices(items) {
  if (!bridgeDevicesContainer) return;

  const renderItem = (item, type) => `
        <li class="flex justify-between items-center py-2 border-b" data-id="${item.id}" data-type="${type}">
            <div class="item-view flex items-center">
                <span class="font-mono text-xs text-gray-400 mr-2 w-8 text-right">${item.id}</span>
                <span class="item-name">${item.name}</span>
            </div>
            <div class="item-edit hidden flex-grow ml-4">
                <input type="text" value="${item.name}" class="border-gray-300 rounded-md shadow-sm text-sm p-1 w-full">
            </div>
            <div class="item-actions flex items-center flex-shrink-0">
                <button data-action="save-rename" class="hidden ml-2 text-sm bg-green-500 text-white py-1 px-2 rounded hover:bg-green-600">Speichern</button>
                <button data-action="cancel-rename" class="hidden ml-1 text-sm bg-gray-500 text-white py-1 px-2 rounded hover:bg-gray-600">X</button>
                <button data-action="edit-rename" class="ml-2 text-sm bg-blue-500 text-white py-1 px-2 rounded hover:bg-blue-600">Ändern</button>
                <button data-action="delete-item" class="ml-1 text-sm bg-red-500 text-white py-1 px-2 rounded hover:bg-red-600"><i class="fas fa-trash"></i></button>
            </div>
        </li>
    `;

  const groupsHtml = items.grouped_lights
    .map((group) => {
      const lightsHtml =
        group.lights && group.lights.length > 0
          ? group.lights.map((light) => renderItem(light, "light")).join("")
          : '<li class="text-xs text-gray-500 py-2">Keine Lampen in diesem Raum.</li>';

      return `
            <div class="bg-white p-4 rounded-lg shadow-md">
                <div class="flex justify-between items-center pb-2 border-b mb-2" data-id="${group.id}" data-type="group">
                    <div class="item-view flex items-center">
                        <i class="fas fa-layer-group mr-3 text-indigo-500"></i>
                        <h3 class="text-xl font-semibold item-name">${group.name}</h3>
                    </div>
                    <div class="item-edit hidden flex-grow ml-4">
                        <input type="text" value="${group.name}" class="border-gray-300 rounded-md shadow-sm text-sm p-1 w-full">
                    </div>
                    <div class="item-actions flex items-center flex-shrink-0">
                        <button data-action="save-rename" class="hidden ml-2 text-sm bg-green-500 text-white py-1 px-2 rounded hover:bg-green-600">Speichern</button>
                        <button data-action="cancel-rename" class="hidden ml-1 text-sm bg-gray-500 text-white py-1 px-2 rounded hover:bg-gray-600">X</button>
                        <button data-action="edit-rename" class="ml-2 text-sm bg-blue-500 text-white py-1 px-2 rounded hover:bg-blue-600">Ändern</button>
                        <button data-action="delete-item" class="ml-1 text-sm bg-red-500 text-white py-1 px-2 rounded hover:bg-red-600"><i class="fas fa-trash"></i></button>
                    </div>
                </div>
                <ul class="space-y-1">${lightsHtml}</ul>
            </div>
        `;
    })
    .join("");

  let unassignedLightsHtml = "";
  if (items.unassigned_lights && items.unassigned_lights.length > 0) {
    unassignedLightsHtml = `
            <div class="bg-white p-4 rounded-lg shadow-md">
                <h3 class="text-xl font-semibold mb-2 flex items-center"><i class="fas fa-question-circle mr-3 text-gray-400"></i>Unsortierte Lampen</h3>
                <ul class="space-y-1">${items.unassigned_lights
                  .map((light) => renderItem(light, "light"))
                  .join("")}</ul>
            </div>
        `;
  }

  const sensorsHtml =
    items.sensors && items.sensors.length > 0
      ? `
        <div class="bg-white p-4 rounded-lg shadow-md">
             <h3 class="text-xl font-semibold mb-2 flex items-center"><i class="fas fa-satellite-dish mr-3 text-teal-500"></i>Sensoren</h3>
            <ul class="space-y-1">${items.sensors
              .map((sensor) => renderItem(sensor, "sensor"))
              .join("")}</ul>
        </div>
    `
      : "";

  bridgeDevicesContainer.innerHTML = `<div class="space-y-6">${groupsHtml}${unassignedLightsHtml}${sensorsHtml}</div>`;
}

export function populateAnalyseSensors(sensors) {
  const sensorSelect = document.getElementById("analyse-sensor");
  if (!sensorSelect) return;
  sensorSelect.innerHTML = "";
  sensors.forEach((sensor) => {
    const option = document.createElement("option");
    option.value = sensor.id;
    option.textContent = sensor.name;
    sensorSelect.appendChild(option);
  });
}

export function renderChart(chartInstance, data, period) {
  const ctx = document.getElementById("sensor-chart")?.getContext("2d");
  if (!ctx) return null;
  if (chartInstance) chartInstance.destroy();
  const getMinMax = (arr, forceMinZero = false) => {
    const validValues = arr.filter((v) => v !== null && isFinite(v));
    if (validValues.length === 0) return {};
    let minVal = Math.min(...validValues);
    let maxVal = Math.max(...validValues);
    if (minVal === maxVal) {
      minVal -= 5;
      maxVal += 5;
    }
    const padding = (maxVal - minVal) * 0.1;
    let finalMin = minVal - padding;
    if (forceMinZero) {
      finalMin = Math.max(0, finalMin);
    }
    return { min: finalMin, max: maxVal + padding };
  };
  const brightnessRange = getMinMax(data.brightness_avg, true);
  const temperatureRange = getMinMax(data.temperature_avg);
  const datasets = [];
  if (data.brightness_avg && data.brightness_avg.some((v) => v !== null)) {
    datasets.push({
      label: "Helligkeit",
      data: data.brightness_avg,
      borderColor: "rgba(234, 179, 8, 1)",
      yAxisID: "y",
      tension: 0.2,
      pointRadius: 0,
      borderWidth: 2.5,
      spanGaps: true,
    });
  }
  if (data.temperature_avg && data.temperature_avg.some((v) => v !== null)) {
    datasets.push({
      label: "Temperatur (°C)",
      data: data.temperature_avg,
      borderColor: "rgba(37, 99, 235, 1)",
      yAxisID: "y1",
      tension: 0.2,
      pointRadius: 0,
      borderWidth: 2.5,
      spanGaps: true,
    });
  }
  return new Chart(ctx, {
    type: "line",
    data: {
      labels: data.labels,
      datasets: datasets.map((ds) => ({
        ...ds,
        data: ds.data.map((val, i) => ({ x: data.labels[i], y: val })),
      })),
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          type: "time",
          time: {
            unit: period === "week" ? "day" : "hour",
            tooltipFormat: "dd.MM.yyyy HH:mm",
            displayFormats: { hour: "HH:mm", day: "EEE dd.MM" },
          },
          title: { display: true, text: "Zeit" },
        },
        y: {
          type: "linear",
          position: "left",
          title: {
            display: true,
            text: "Helligkeit (lightlevel)",
            color: "#b45309",
          },
          min: brightnessRange.min,
          max: brightnessRange.max,
          ticks: { color: "#b45309" },
        },
        y1: {
          type: "linear",
          position: "right",
          title: { display: true, text: "Temperatur (°C)", color: "#2563eb" },
          grid: { drawOnChartArea: false },
          min: temperatureRange.min,
          max: temperatureRange.max,
          ticks: { color: "#2563eb" },
        },
      },
      plugins: {
        tooltip: { mode: "index", intersect: false },
        legend: { display: datasets.length > 0 },
      },
      interaction: { intersect: false, mode: "index" },
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
      ? `<span class="mx-2 text-gray-400">|</span> <span class="flex items-center"><i class="fas fa-lightbulb mr-2 text-yellow-500"></i> ${sensor.name}</span>`
      : "";

    const sectionsHtml = ["morning", "day", "evening", "night"]
      .map((name) => {
        const section = routine[name];
        if (!section) return "";
        const waitTime = section.wait_time || {};
        const waitTimeString = `${waitTime.min || 0}m ${waitTime.sec || 0}s`;
        return `<div class="py-2 px-3 ${
          sectionColors[name] || "bg-gray-50"
        } rounded-md mt-2"><p class="font-semibold capitalize flex items-center">${
          icons[name] || ""
        } <span class="ml-2">${
          periodNames[name] || name
        }</span></p><div class="text-sm text-gray-700 grid grid-cols-2 gap-x-4"><span><strong class="font-medium">Normal:</strong> ${
          section.scene_name
        }</span><span><strong class="font-medium">Bewegung:</strong> ${
          section.x_scene_name
        }</span><span><strong class="font-medium">Bewegung:</strong> ${
          section.motion_check ? `Ja (${waitTimeString})` : "Nein"
        }</span><span><strong class="font-medium">Nicht stören:</strong> ${
          section.do_not_disturb ? "Ja" : "Nein"
        }</span><span><strong class="font-medium">Helligkeit:</strong> ${
          section.bri_check ? "Ja" : "Nein"
        }</span>${
          section.bri_check
            ? `<span><strong class="font-medium">Max Level:</strong> ${section.max_light_level}</span>`
            : ""
        }</div></div>`;
      })
      .join("");

    const dailyTime = routine.daily_time || {};
    const isEnabled = routine.enabled !== false;

    routineEl.innerHTML = `
            <div class="routine-header p-4 cursor-pointer hover:bg-gray-50 flex justify-between items-center" data-action="toggle-routine-details">
                <div>
                    <div class="flex items-center">
                        <h3 class="text-2xl font-semibold">${routine.name}</h3>
                        <i class="fas fa-chevron-down ml-4 text-gray-400"></i>
                    </div>
                    <div class="flex items-center text-gray-500 text-sm mt-1">
                        <p>Raum: ${routine.room_name}</p>
                        ${sensorHtml}
                        <span class="mx-2 text-gray-400">|</span>
                        <p>Aktiv: ${String(dailyTime.H1).padStart(
                          2,
                          "0"
                        )}:${String(dailyTime.M1).padStart(2, "0")} - ${String(
      dailyTime.H2
    ).padStart(2, "0")}:${String(dailyTime.M2).padStart(2, "0")}</p>
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
            <div class="routine-details px-4 pb-4">
                <div class="space-y-2 border-t pt-4 mt-2">
                    <h4 class="text-lg font-medium">Ablauf</h4>
                    ${sectionsHtml}
                </div>
            </div>`;
    routinesContainer.appendChild(routineEl);
  });
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
        colorPreviewStyle = `background-color: hsl(${hue}, ${sat}%, 50%);`;
      } else if (scene.ct !== undefined) {
        const tempPercent = Math.min(
          1,
          Math.max(0, (scene.ct - 153) / (500 - 153))
        );
        const red = 255;
        const green = 255 - tempPercent * 100;
        const blue = 255 - tempPercent * 200;
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
  modalSceneContainer.innerHTML = `<div class="bg-white rounded-lg shadow-xl w-full max-w-md m-4"><div class="p-6"><h3 class="text-2xl font-bold mb-4">${
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
  } class="h-4 w-4 rounded"><label for="scene-status" class="ml-2 block text-sm">Licht an</label></div></form></div><div class="bg-gray-50 px-6 py-3 flex justify-end space-x-3"><button type="button" data-action="cancel-modal" class="bg-white py-2 px-4 border rounded-md">Abbrechen</button><button type="button" data-action="save-scene" class="bg-blue-600 text-white py-2 px-4 rounded-md">Speichern</button></div></div>`;
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
  modalRoutineContainer.innerHTML = `<div class="bg-white rounded-lg shadow-xl w-full max-w-lg m-4"><div class="p-6"><h3 class="text-2xl font-bold mb-4">Neue Routine</h3><form class="space-y-4"><label for="new-routine-name" class="block text-sm font-medium">Name</label><input type="text" id="new-routine-name" required class="mt-1 block w-full rounded-md border-gray-300"><label for="new-routine-group" class="block text-sm font-medium">Raum / Zone</label><select id="new-routine-group" class="mt-1 block w-full rounded-md border-gray-300">${groupOptions}</select><label for="new-routine-sensor" class="block text-sm font-medium">Sensor (Optional)</label><select id="new-routine-sensor" class="mt-1 block w-full rounded-md border-gray-300"><option value="">Kein Sensor</option>${sensorOptions}</select></form></div><div class="bg-gray-50 px-6 py-3 flex justify-end space-x-3"><button type="button" data-action="cancel-modal" class="bg-white py-2 px-4 border rounded-md">Abbrechen</button><button type="button" data-action="create-routine" class="bg-blue-600 text-white py-2 px-4 rounded-md">Erstellen</button></div></div>`;
  modalRoutineContainer.classList.remove("hidden");
}

export function openEditRoutineModal(
  routine,
  routineIndex,
  sceneNames,
  configuredRooms,
  allBridgeRooms,
  allSensors
) {
  const sceneOptions = sceneNames
    .map(
      (name) => `<option value="${name}">${name.replace(/_/g, " ")}</option>`
    )
    .join("");

  const roomOptions = allBridgeRooms
    .map(
      (room) =>
        `<option value="${room.id}|${room.name}" ${
          routine.room_name === room.name ? "selected" : ""
        }>${room.name}</option>`
    )
    .join("");

  const roomConf = configuredRooms.find((r) => r.name === routine.room_name);
  const currentSensorId = roomConf ? roomConf.sensor_id : undefined;

  const sensorOptions = allSensors
    .map(
      (sensor) =>
        `<option value="${sensor.id}" ${
          currentSensorId && parseInt(sensor.id) === parseInt(currentSensorId)
            ? "selected"
            : ""
        }>${sensor.name}</option>`
    )
    .join("");

  const sectionsHtml = ["morning", "day", "evening", "night"]
    .map((name) => {
      const section = routine[name] || {};
      const waitTime = section.wait_time || {};
      const initialBriValue =
        Math.round((section.max_light_level || 0) / 100) * 100;
      return `<div class="p-4 border-2 rounded-lg ${
        sectionColors[name]
      }" data-section-name="${name}"><h5 class="font-semibold capitalize text-base flex items-center">${
        icons[name] || ""
      } <span class="ml-2">${
        periodNames[name] || name
      }</span></h5><div class="grid grid-cols-2 gap-4 text-sm mt-2"><div><label class="block font-medium">Normal-Szene</label><select class="mt-1 w-full rounded-md border-gray-300 shadow-sm section-scene-name">${sceneOptions.replace(
        `value="${section.scene_name}"`,
        `value="${section.scene_name}" selected`
      )}</select></div><div><label class="block font-medium">Bewegungs-Szene</label><select class="mt-1 w-full rounded-md border-gray-300 shadow-sm section-x-scene-name">${sceneOptions.replace(
        `value="${section.x_scene_name}"`,
        `value="${section.x_scene_name}" selected`
      )}</select></div><div class="col-span-2 border-t mt-2 pt-2 space-y-2"><div class="flex items-center"><input type="checkbox" ${
        section.motion_check ? "checked" : ""
      } class="h-4 w-4 rounded border-gray-300 section-motion-check"><label class="ml-2 font-medium">Auf Bewegung reagieren</label></div><div class="grid grid-cols-2 gap-2"><div><label class="block">Minuten</label><input type="number" value="${
        waitTime.min || 1
      }" class="mt-1 w-full rounded-md border-gray-300 shadow-sm section-wait-time-min"></div><div><label class="block">Sekunden</label><input type="number" value="${
        waitTime.sec || 0
      }" class="mt-1 w-full rounded-md border-gray-300 shadow-sm section-wait-time-sec"></div></div><div class="flex items-center"><input type="checkbox" ${
        section.do_not_disturb ? "checked" : ""
      } class="h-4 w-4 rounded border-gray-300 section-do-not-disturb"><label class="ml-2">Bitte nicht stören</label></div></div><div class="col-span-2 border-t mt-2 pt-2 space-y-2"><div class="flex items-center"><input type="checkbox" ${
        section.bri_check ? "checked" : ""
      } class="h-4 w-4 rounded border-gray-300 section-bri-check"><label class="ml-2 font-medium">Helligkeits-Check (Adaptive Helligkeit)</label></div><div class="space-y-2 pl-6">
      
      <div class="flex items-center gap-4"><div class="flex-grow"><label class="block text-xs">Max. Helligkeit (Schwellenwert)</label><input type="range" min="0" max="35000" step="100" value="${initialBriValue}" class="w-full brightness-slider"></div><span class="font-mono text-sm text-gray-700 bg-gray-100 p-1 rounded brightness-value-display w-16 text-center"></span></div>
      <div class="flex items-center gap-4"><div class="flex-grow"><label class="block text-xs">Lichtfarbe für Regelung</label><input type="range" min="153" max="500" value="${
        section.bri_ct || 366
      }" class="w-full ct-slider section-bri-ct"></div><span class="font-mono text-sm text-gray-700 bg-gray-100 p-1 rounded ct-value-display w-16 text-center"></span></div>
      </div></div></div></div>`;
    })
    .join("");

  modalRoutineContainer.innerHTML = `<div class="bg-white rounded-lg shadow-xl w-full max-w-3xl m-4 flex flex-col" style="max-height: 90vh;">
        <div class="p-6 border-b"><h3 class="text-2xl font-bold">Routine bearbeiten</h3></div>
        <div class="p-6 overflow-y-auto">
            <form class="space-y-4">
                <input type="hidden" id="routine-index" value="${routineIndex}">
                
                <div><label for="routine-name-edit" class="block text-sm font-medium">Name der Routine</label>
                <input type="text" id="routine-name-edit" value="${routine.name}" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm"></div>

                <div><label for="routine-room-select" class="block text-sm font-medium">Raum / Zone</label>
                <select id="routine-room-select" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm">${roomOptions}</select></div>
                
                <div><label for="routine-sensor-select" class="block text-sm font-medium">Sensor</label>
                <select id="routine-sensor-select" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm"><option value="">Kein Sensor</option>${sensorOptions}</select></div>

                <div class="relative h-24"><div class="flex justify-between items-center mb-2"><div class="text-center"><label class="block font-medium">Startzeit</label><input type="time" id="time-input-start" class="text-2xl font-semibold text-blue-600 bg-transparent border-none p-0 text-center w-28 focus:ring-0"></div><div class="text-center"><label class="block font-medium">Endzeit</label><input type="time" id="time-input-end" class="text-2xl font-semibold text-blue-600 bg-transparent border-none p-0 text-center w-28 focus:ring-0"></div></div><div id="timeline-container" class="relative h-20 pt-5"><svg class="absolute inset-0 w-full h-full" viewBox="0 0 1000 80" preserveAspectRatio="none"><line x1="20" y1="40" x2="980" y2="40" stroke="#9ca3af" stroke-width="2"/><path d="M 975 35 L 985 40 L 975 45 Z" fill="#9ca3af"/><line x1="20" y1="35" x2="20" y2="45" stroke="#9ca3af" stroke-width="2"/><line x1="980" y1="35" x2="980" y2="45" stroke="#9ca3af" stroke-width="2"/><text x="20" y="65" text-anchor="middle" font-size="12px" fill="#4b5563">00:00</text><text x="980" y="65" text-anchor="end" font-size="12px" fill="#4b5563">23:59</text></svg><div id="timeline-emojis" class="absolute inset-x-0 top-0 h-8 text-xl text-center pointer-events-none"></div><input type="range" id="time-slider-start" min="0" max="1439" class="absolute w-full top-1/2 -translate-y-1/2 h-2 bg-transparent appearance-none timeline-slider"><input type="range" id="time-slider-end" min="0" max="1439" class="absolute w-full top-1/2 -translate-y-1/2 h-2 bg-transparent appearance-none timeline-slider"></div></div>
                
                <div><h4 class="text-lg font-medium mb-2 mt-4 border-t pt-4">Ablauf</h4>
                <div class="space-y-3">${sectionsHtml}</div></div>
            </form>
        </div>
        <div class="bg-gray-50 px-6 py-3 border-t flex justify-end space-x-3">
            <button type="button" data-action="cancel-modal" class="bg-white py-2 px-4 border rounded-md">Abbrechen</button>
            <button type="button" data-action="save-routine" class="bg-blue-600 text-white py-2 px-4 rounded-md">Speichern</button>
        </div>
    </div>`;
  modalRoutineContainer.classList.remove("hidden");

  const handleCheckboxLogic = (sectionDiv) => {
    const motionCheck = sectionDiv.querySelector(".section-motion-check");
    const dndCheck = sectionDiv.querySelector(".section-do-not-disturb");
    const briCheck = sectionDiv.querySelector(".section-bri-check");
    if (!motionCheck.checked) {
      if (dndCheck.checked)
        showToast(
          "'Bitte nicht stören' deaktiviert, da Bewegungserkennung aus ist.",
          false
        );
      dndCheck.disabled = true;
      dndCheck.checked = false;
    } else {
      dndCheck.disabled = briCheck.checked;
    }
    if (dndCheck.checked) briCheck.disabled = true;
    else briCheck.disabled = false;
    if (briCheck.checked) dndCheck.disabled = true;
    else if (motionCheck.checked) dndCheck.disabled = false;
  };

  modalRoutineContainer
    .querySelectorAll("[data-section-name]")
    .forEach((sectionDiv) => {
      const motion = sectionDiv.querySelector(".section-motion-check");
      const dnd = sectionDiv.querySelector(".section-do-not-disturb");
      const bri = sectionDiv.querySelector(".section-bri-check");
      [motion, dnd, bri].forEach((checkbox) =>
        checkbox.addEventListener("change", () =>
          handleCheckboxLogic(sectionDiv)
        )
      );
      handleCheckboxLogic(sectionDiv);
      const briSlider = sectionDiv.querySelector(".brightness-slider");
      const briDisplay = sectionDiv.querySelector(".brightness-value-display");
      const ctSlider = sectionDiv.querySelector(".ct-slider");
      const ctDisplay = sectionDiv.querySelector(".ct-value-display");
      const updateBriDisplay = () => (briDisplay.textContent = briSlider.value);
      const updateCtDisplay = () => (ctDisplay.textContent = ctSlider.value);
      briSlider.addEventListener("input", updateBriDisplay);
      ctSlider.addEventListener("input", updateCtDisplay);
      updateBriDisplay();
      updateCtDisplay();
    });

  const startSlider = document.getElementById("time-slider-start");
  const endSlider = document.getElementById("time-slider-end");
  const timeInputStart = document.getElementById("time-input-start");
  const timeInputEnd = document.getElementById("time-input-end");
  const emojiContainer = document.getElementById("timeline-emojis");
  const minutesToTimeStr = (m) =>
    `${String(Math.floor(m / 60)).padStart(2, "0")}:${String(m % 60).padStart(
      2,
      "0"
    )}`;
  const timeStrToMinutes = (t) => {
    const [hours, minutes] = t.split(":").map(Number);
    return hours * 60 + minutes;
  };
  const updateDisplays = () => {
    const startVal = parseInt(startSlider.value);
    const endVal = parseInt(endSlider.value);
    if (startVal >= endVal) startSlider.value = endVal - 1;
    if (endVal <= startVal) endSlider.value = startVal + 1;
    timeInputStart.value = minutesToTimeStr(startSlider.value);
    timeInputEnd.value = minutesToTimeStr(endSlider.value);
    const startPercent = (startSlider.value / 1439) * 100;
    const endPercent = (endSlider.value / 1439) * 100;
    const midPercent = startPercent + (endPercent - startPercent) / 2;
    emojiContainer.innerHTML = `<span class="absolute" style="left: 1%; top: -5px;">${icons.night}</span><span class="absolute" style="left: ${startPercent}%; transform: translateX(-50%);">${icons.morning}</span><span class="absolute" style="left: ${midPercent}%; transform: translateX(-50%);">${icons.day}</span><span class="absolute" style="left: ${endPercent}%; transform: translateX(-50%);">${icons.evening}</span><span class="absolute" style="right: 1%; top: -5px;">${icons.night}</span>`;
  };
  startSlider.addEventListener("input", updateDisplays);
  endSlider.addEventListener("input", updateDisplays);
  timeInputStart.addEventListener("change", () => {
    startSlider.value = timeStrToMinutes(timeInputStart.value);
    updateDisplays();
  });
  timeInputEnd.addEventListener("change", () => {
    endSlider.value = timeStrToMinutes(timeInputEnd.value);
    updateDisplays();
  });
  const initialStartMinutes =
    routine.daily_time.H1 * 60 + routine.daily_time.M1;
  const initialEndMinutes = routine.daily_time.H2 * 60 + routine.daily_time.M2;
  startSlider.value = initialStartMinutes;
  endSlider.value = initialEndMinutes;
  updateDisplays();
}

function renderStatusTimeline(status, sunTimes) {
  const timeToMinutes = (h, m) => h * 60 + m;
  const routineStart = status.daily_time;
  const sunrise = sunTimes ? new Date(sunTimes.sunrise) : null;
  const sunset = sunTimes ? new Date(sunTimes.sunset) : null;
  const morningStartMins = timeToMinutes(routineStart.H1, routineStart.M1);
  const eveningEndMins = timeToMinutes(routineStart.H2, routineStart.M2);
  const sunriseMins = sunrise
    ? timeToMinutes(sunrise.getHours(), sunrise.getMinutes())
    : 330;
  const sunsetMins = sunset
    ? timeToMinutes(sunset.getHours(), sunset.getMinutes())
    : 1290;
  const timeToPercent = (mins) => 10 + (mins / 1439) * 80;
  const timeMarkers = [3, 9, 12, 15, 18, 21];
  let timeMarkersHtml = "";
  timeMarkers.forEach((h) => {
    const percent = timeToPercent(h * 60);
    timeMarkersHtml += `<line x1="${percent}%" y1="175" x2="${percent}%" y2="185" stroke="#d1d5db" stroke-width="1.5" /><text x="${percent}%" y="170" text-anchor="middle" font-size="12px" fill="#6b7280">${String(
      h
    ).padStart(2, "0")}</text>`;
  });
  const morningStartPercent = timeToPercent(morningStartMins);
  const eveningEndPercent = timeToPercent(eveningEndMins);
  const sunrisePercent = timeToPercent(sunriseMins);
  const sunsetPercent = timeToPercent(sunsetMins);
  let showMorning = sunriseMins > morningStartMins;
  let showEvening = sunsetMins <= eveningEndMins;
  const yPos = { day: 75, transition: 125, night: 155 };
  const leftNightX = 5;
  const rightNightX = 95;
  let periods = `<text x="${leftNightX}%" y="${yPos.night}" text-anchor="middle" font-size="24">${icons.night}</text>`;
  if (showMorning) {
    periods += `<text x="${(morningStartPercent + sunrisePercent) / 2}%" y="${
      yPos.transition
    }" text-anchor="middle" font-size="24">${icons.morning}</text>`;
  }
  periods += `<text x="${(sunrisePercent + sunsetPercent) / 2}%" y="${
    yPos.day
  }" text-anchor="middle" font-size="24">${icons.day}</text>`;
  if (showEvening) {
    periods += `<text x="${(sunsetPercent + eveningEndPercent) / 2}%" y="${
      yPos.transition
    }" text-anchor="middle" font-size="24">${icons.evening}</text>`;
  }
  periods += `<text x="${rightNightX}%" y="${yPos.night}" text-anchor="middle" font-size="24">${icons.night}</text>`;
  const arcStartX = sunrisePercent * 10;
  const arcEndX = sunsetPercent * 10;
  const arcRadiusX = (arcEndX - arcStartX) / 2;
  const arcRadiusY = Math.min(150, arcRadiusX * 0.9);
  const centerX = arcStartX + arcRadiusX;
  const lastMotionTime = status.last_motion_iso
    ? new Date(status.last_motion_iso).toLocaleTimeString("de-DE")
    : "nie";
  const yLabelSun = 205;
  const yLabelRoutine = 220;

  const periodEmoji = { morning: "🌅", day: "☀️", evening: "🌇", night: "🌙" };
  const primaryEmoji = periodEmoji[status.period] || "🗓️";
  const primaryText = periodNames[status.period] || status.period || "...";
  let primaryStateHtml = `
      <div class="flex items-center text-sm font-medium text-gray-700 bg-gray-100 px-3 py-1 rounded-full">
        <span class="mr-2">${primaryEmoji}</span>
        <span>${primaryText}</span>
      </div>
    `;

  let secondaryStateHtml = "";
  let secondaryEmoji = "";
  let secondaryText = "";

  if (status.enabled === false) {
    secondaryEmoji = "⏸️";
    secondaryText = "Deaktiviert";
  } else if (status.last_scene?.toLowerCase().includes("manuell")) {
    secondaryEmoji = "✋";
    secondaryText = "Manuell";
  } else if (status.motion_status?.includes("erkannt")) {
    secondaryEmoji = "🏃‍♂️";
    secondaryText = "Bewegung";
  } else if (status.last_scene?.toLowerCase().includes("geregelt")) {
    secondaryEmoji = "💡";
    secondaryText = "Geregelt";
  }

  if (secondaryText) {
    secondaryStateHtml = `
          <div class="flex items-center text-sm font-medium text-gray-700 bg-yellow-100 border border-yellow-200 px-3 py-1 rounded-full ml-2">
            <span class="mr-2">${secondaryEmoji}</span>
            <span>${secondaryText}</span>
          </div>
        `;
  }

  const statusDisplayHtml = `
        <div class="flex items-center">
            ${primaryStateHtml}
            ${secondaryStateHtml}
        </div>
    `;

  return `<div class="bg-white rounded-lg shadow border border-gray-200 status-card">
    <div class="status-header flex justify-between items-center cursor-pointer hover:bg-gray-50 p-2" data-action="toggle-status-details">
        <div class="flex items-center">
            <h4 class="font-bold text-lg">${status.name}</h4>
            <i class="fas fa-chevron-down ml-4 text-gray-400"></i>
        </div>
        ${statusDisplayHtml}
    </div>
    <div class="status-details px-4">
        <div class="w-full my-2 h-72 text-gray-700">
            <svg class="h-full w-full timeline-svg" viewBox="0 0 1000 240" font-family="Inter, sans-serif" font-size="12px" data-center-x="${centerX}" data-radius-x="${arcRadiusX}" data-radius-y="${arcRadiusY}" data-arc-start-x="${arcStartX}" data-arc-end-x="${arcEndX}">
                <line x1="2%" y1="180" x2="98%" y2="180" stroke="#9ca3af" stroke-width="2" />
                <path d="M 978 175 L 988 180 L 978 185 Z" fill="#9ca3af" />
                ${timeMarkersHtml}
                <line x1="${morningStartPercent}%" y1="175" x2="${morningStartPercent}%" y2="185" stroke="#3b82f6" stroke-width="2" />
                <text x="${morningStartPercent}%" y="${yLabelRoutine}" text-anchor="middle" fill="#3b82f6" font-weight="bold">${String(
    routineStart.H1
  ).padStart(2, "0")}:${String(routineStart.M1).padStart(2, "0")}</text>
                <line x1="${sunrisePercent}%" y1="175" x2="${sunrisePercent}%" y2="185" stroke="#f59e0b" stroke-width="2" />
                <text x="${sunrisePercent}%" y="${yLabelSun}" text-anchor="middle" fill="#f59e0b">${sunrise?.toLocaleTimeString(
    [],
    { hour: "2-digit", minute: "2-digit" }
  )}</text>
                <line x1="${sunsetPercent}%" y1="175" x2="${sunsetPercent}%" y2="185" stroke="#f97316" stroke-width="2" />
                <text x="${sunsetPercent}%" y="${yLabelSun}" text-anchor="middle" fill="#f97316">${sunset?.toLocaleTimeString(
    [],
    { hour: "2-digit", minute: "2-digit" }
  )}</text>
                <line x1="${eveningEndPercent}%" y1="175" x2="${eveningEndPercent}%" y2="185" stroke="#3b82f6" stroke-width="2" />
                <text x="${eveningEndPercent}%" y="${yLabelRoutine}" text-anchor="middle" fill="#3b82f6" font-weight="bold">${String(
    routineStart.H2
  ).padStart(2, "0")}:${String(routineStart.M2).padStart(2, "0")}</text>
                <path d="M ${arcStartX} 180 A ${arcRadiusX} ${arcRadiusY} 0 0 1 ${arcEndX} 180" stroke="#f97316" stroke-width="1.5" fill="none" />
                ${periods}
                <g class="sun-emoji-indicator" data-sunrise-mins="${sunriseMins}" data-sunset-mins="${sunsetMins}"><text x="0" y="0" text-anchor="middle" font-size="28">${
    icons.sun
  }</text></g>
            </svg>
        </div>
        <div class="text-sm grid grid-cols-2 md:grid-cols-4 gap-x-4 gap-y-2 border-t pt-2">
            <span><strong>Status:</strong> <span class="${
              status.enabled ? "text-green-600" : "text-red-500"
            }">${status.enabled ? "Aktiviert" : "Deaktiviert"}</span></span>
            <span class="${
              status.motion_status?.includes("erkannt") ? "text-green-600" : ""
            }"><strong >Bewegung:</strong> ${status.motion_status}</span>
            <span><strong>Helligkeit:</strong> ${status.brightness}</span>
            <span><strong>Temperatur:</strong> ${status.temperature}°C</span>
            <span class="md:col-span-2"><strong>Letzte Szene:</strong> ${
              status.last_scene
            }</span>
            <span class="md:col-span-2"><strong>Letzte Bewegung:</strong> ${lastMotionTime}</span>
        </div>
    </div>
  </div>`;
}
