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
    const cardBgColor = isOn ? "bg-yellow-200" : "bg-gray-700";
    const textColor = isOn ? "text-black" : "text-white";

    const card = `
            <div class="room-card rounded-lg shadow-md p-4 flex flex-col justify-between transition-colors duration-300 ${cardBgColor} ${textColor}" 
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

export function renderRoomDetail(group, allLights, allScenes) {
  const roomLights = allLights.filter((light) =>
    group.lights.includes(light.id)
  );
  const roomScenes = allScenes.filter((scene) => scene.group.rid === group.id);

  const scenesHtml = roomScenes
    .map(
      (scene) => `
        <div class="bg-gray-700 rounded-lg p-3 text-white text-center cursor-pointer" 
             data-action="recall-scene" 
             data-scene-id="${scene.id}" 
             data-group-id="${group.id}">
            ${scene.metadata.name}
        </div>
    `
    )
    .join("");

  const lightsHtml = roomLights
    .map(
      (light) => `
        <div class="bg-gray-700 rounded-lg p-3 text-white flex justify-between items-center">
            <span>${light.metadata.name}</span>
             <label class="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" ${
                  light.on.on ? "checked" : ""
                } class="sr-only peer" data-action="toggle-light-power" data-light-id="${
        light.id
      }">
                <div class="w-11 h-6 bg-gray-500 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-500"></div>
            </label>
        </div>
    `
    )
    .join("");

  return `
        <div class="p-4 md:p-8 text-white">
            <header class="mb-6 flex justify-between items-center">
                <button type="button" data-action="back-to-home" class="text-2xl"><i class="fas fa-arrow-left"></i></button>
                <h2 class="text-3xl font-bold">${group.name}</h2>
                <button type="button" data-action="open-color-control" data-group-id="${
                  group.id
                }" class="text-2xl"><i class="fas fa-palette"></i></button>
            </header>
            
            <div class="mb-8">
                <h3 class="text-lg font-semibold uppercase text-gray-400 mb-3">Meine Szenen</h3>
                <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                    ${
                      scenesHtml ||
                      '<p class="text-gray-400 col-span-full">Keine Szenen für diesen Raum gefunden.</p>'
                    }
                </div>
            </div>

            <div>
                <h3 class="text-lg font-semibold uppercase text-gray-400 mb-3">Lampen</h3>
                <div class="space-y-3">
                    ${
                      lightsHtml ||
                      '<p class="text-gray-400">Keine Lampen in diesem Raum gefunden.</p>'
                    }
                </div>
            </div>
        </div>
    `;
}
