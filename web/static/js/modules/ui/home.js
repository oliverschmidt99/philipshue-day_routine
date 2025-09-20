import { xyToRgb, mirekToRgb, getContrastYIQ } from "./color-converter.js";

export function renderHome(bridgeData, groupedLights) {
  const homeContainer = document.getElementById("home-container");
  if (!homeContainer) return;

  const groups = [...bridgeData.rooms, ...bridgeData.zones];
  homeContainer.innerHTML = "";

  groups.forEach((group) => {
    const groupedLight = groupedLights.find((gl) => gl.owner.rid === group.id);
    if (!groupedLight) return;

    const isOn = groupedLight.on.on;
    const brightness = isOn ? groupedLight.dimming.brightness : 0;

    let cardStyle = "background-color: #374151; color: white;"; // Standard (Aus)
    if (isOn) {
      let rgb = { r: 253, g: 224, b: 71 }; // Standard-Gelb (An)
      const lightState = groupedLight;
      if (lightState.color?.xy) {
        rgb = xyToRgb(lightState.color.xy.x, lightState.color.xy.y);
      } else if (lightState.color_temperature?.mirek) {
        rgb = mirekToRgb(lightState.color_temperature.mirek);
      }
      const textColor = getContrastYIQ(rgb);
      cardStyle = `background-color: rgb(${rgb.r}, ${rgb.g}, ${rgb.b}); color: ${textColor};`;
    }

    const card = `
            <div class="room-card rounded-lg shadow-md p-4 flex flex-col justify-between transition-colors duration-300" 
                 style="${cardStyle}"
                 data-group-id="${group.id}"
                 data-group-name="${group.name}">

                <div class="cursor-pointer flex-grow" data-action="open-room-detail">
                    <h3 class="text-xl font-bold">${group.name}</h3>
                    <p class="text-sm opacity-80">${
                      isOn ? `An - ${brightness.toFixed(0)}%` : "Aus"
                    }</p>
                </div>

                <div class="mt-4 flex items-center justify-end">
                    <label class="relative inline-flex items-center cursor-pointer">
                      <input type="checkbox" ${
                        isOn ? "checked" : ""
                      } class="sr-only peer" data-action="toggle-group-power" data-group-id="${
      group.id
    }">
                      <div class="w-14 h-7 bg-gray-500 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-1 after:left-[4px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-500"></div>
                    </label>
                </div>
            </div>
        `;
    homeContainer.innerHTML += card;
  });
}

export function renderRoomDetail(group, allLights, allScenes, groupedLight) {
  const roomLights = allLights.filter((light) =>
    group.lights.includes(light.id)
  );
  const roomScenes = allScenes.filter((scene) => scene.group.rid === group.id);

  const isOn = groupedLight?.on?.on ?? false;
  const brightness = groupedLight?.dimming?.brightness ?? 0;
  const activeSceneId = groupedLight?.scene?.rid; // Korrekter Pfad zum aktiven Szenen-RID

  const scenesHtml = roomScenes
    .map((scene) => {
      const colors = scene.actions
        .map((action) => action.action?.color?.xy)
        .filter(Boolean)
        .map((xy) => {
          const rgb = xyToRgb(xy.x, xy.y);
          return `rgb(${rgb.r}, ${rgb.g}, ${rgb.b})`;
        });

      let backgroundStyle = "background-color: #4b5563;";
      if (colors.length === 1) {
        backgroundStyle = `background-color: ${colors[0]};`;
      } else if (colors.length > 1) {
        backgroundStyle = `background-image: linear-gradient(to right, ${colors.join(
          ", "
        )});`;
      }

      const isActive = scene.id === activeSceneId;
      const activeClass = isActive
        ? "ring-2 ring-offset-2 ring-offset-gray-800 ring-yellow-400"
        : "";

      return `
        <div class="rounded-xl text-white text-center cursor-pointer flex flex-col justify-end p-2 h-24 ${activeClass}"
             style="${backgroundStyle}"
             data-action="recall-scene"
             data-scene-id="${scene.id}"
             data-group-id="${group.id}">
            <span class="text-sm font-semibold break-words" style="text-shadow: 1px 1px 2px rgba(0,0,0,0.7);">${scene.metadata.name}</span>
        </div>
    `;
    })
    .join("");

  const lightsHtml = roomLights
    .map((light) => {
      let cardStyle = "background-color: #4b5563; color: white;";
      if (light.on.on) {
        let rgb = { r: 253, g: 224, b: 71 };
        if (light.color?.xy) {
          rgb = xyToRgb(light.color.xy.x, light.color.xy.y);
        } else if (light.color_temperature?.mirek) {
          rgb = mirekToRgb(light.color_temperature.mirek);
        }
        const textColor = getContrastYIQ(rgb);
        cardStyle = `background-color: rgb(${rgb.r}, ${rgb.g}, ${rgb.b}); color: ${textColor};`;
      }
      return `
        <div class="rounded-xl p-4 flex flex-col justify-between" style="${cardStyle}">
            <div>
                <i class="fas fa-lightbulb text-xl"></i>
                <p class="font-bold mt-2 break-words">${light.metadata.name}</p>
            </div>
            <div class="flex justify-end mt-4">
                 <label class="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" ${
                      light.on.on ? "checked" : ""
                    } class="sr-only peer" data-action="toggle-light-power" data-light-id="${
        light.id
      }">
                    <div class="w-11 h-6 bg-gray-500 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-500"></div>
                </label>
            </div>
        </div>
    `;
    })
    .join("");

  return `
        <div class="p-4 md:p-8 text-white">
            <header class="mb-6 flex justify-between items-center">
                <button type="button" data-action="back-to-home" class="text-2xl"><i class="fas fa-arrow-left"></i></button>
                <h2 class="text-3xl font-bold">${group.name}</h2>
                <label class="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" ${
                      isOn ? "checked" : ""
                    } class="sr-only peer" data-action="toggle-group-power-detail" data-group-id="${
    group.id
  }">
                    <div class="w-14 h-7 bg-gray-500 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-1 after:left-[4px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-500"></div>
                </label>
            </header>
            <div class="mb-8">
                <input type="range" min="1" max="100" value="${brightness}" ${
    !isOn ? "disabled" : ""
  }
                       data-action="set-group-brightness-detail" data-group-id="${
                         group.id
                       }"
                       class="w-full h-2 bg-gray-600 rounded-lg appearance-none cursor-pointer brightness-slider">
            </div>
            <div class="mb-8">
                <div class="flex justify-between items-center mb-3">
                    <h3 class="text-lg font-semibold uppercase text-gray-400">Meine Szenen</h3>
                    <button type="button" data-action="open-scene-modal" data-group-id="${
                      group.id
                    }" class="bg-blue-600 rounded-full w-8 h-8 flex items-center justify-center text-white text-xl">
                        <i class="fas fa-plus"></i>
                    </button>
                </div>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                    ${scenesHtml}
                </div>
            </div>
            <div>
                <h3 class="text-lg font-semibold uppercase text-gray-400 mb-3">Lampen</h3>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                    ${
                      lightsHtml ||
                      '<p class="text-gray-400 col-span-full">Keine Lampen in diesem Raum gefunden.</p>'
                    }
                </div>
            </div>
        </div>
    `;
}
