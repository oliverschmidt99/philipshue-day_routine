import { xyToRgb, mirekToRgb, getContrastYIQ } from "./color-converter.js";

// Hilfsfunktion, um Duplikate im Code zu vermeiden und Gruppen-Karten zu rendern
function renderGroupCards(groups, container, groupedLights) {
  if (!container) return;
  container.innerHTML = "";

  // Gruppen alphabetisch nach Namen sortieren
  groups.sort((a, b) => {
    const nameA = a.metadata?.name || "";
    const nameB = b.metadata?.name || "";
    return nameA.localeCompare(nameB);
  });

  groups.forEach((group) => {
    const groupedLight = groupedLights.find((gl) => gl.owner.rid === group.id);
    if (!groupedLight) return;

    const isOn = groupedLight.on?.on;
    const brightness = isOn ? groupedLight.dimming?.brightness : 0;
    const groupName = group.metadata?.name || "Unbenannte Gruppe";

    let cardStyle = "background-color: #374151; color: white;"; // Standard (Aus)
    if (isOn) {
      let rgb = { r: 253, g: 224, b: 71 }; // Standard-Gelb (An)
      if (groupedLight.color?.xy) {
        rgb = xyToRgb(groupedLight.color.xy.x, groupedLight.color.xy.y);
      } else if (groupedLight.color_temperature?.mirek) {
        rgb = mirekToRgb(groupedLight.color_temperature.mirek);
      }
      const textColor = getContrastYIQ(rgb);
      cardStyle = `background-color: rgb(${rgb.r}, ${rgb.g}, ${rgb.b}); color: ${textColor};`;
    }

    const card = `
            <div class="room-card rounded-lg shadow-md p-4 flex flex-col justify-between transition-colors duration-300" 
                 style="${cardStyle}"
                 data-group-id="${group.id}"
                 data-group-name="${groupName}">

                <div class="cursor-pointer flex-grow" data-action="open-room-detail">
                    <h3 class="text-xl font-bold">${groupName}</h3>
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
    container.innerHTML += card;
  });
}

export function renderHome(bridgeData, groupedLights) {
  const roomsContainer = document.getElementById("home-rooms-container");
  const zonesContainer = document.getElementById("home-zones-container");

  renderGroupCards(bridgeData.rooms, roomsContainer, groupedLights);
  renderGroupCards(bridgeData.zones, zonesContainer, groupedLights);
}

// Die renderRoomDetail Funktion bleibt unverändert...
export function renderRoomDetail(group, allLights, allScenes, groupedLight) {
  const roomLights = allLights.filter((light) =>
    group.lights.includes(light.id)
  );
  const roomScenes = allScenes.filter((scene) => scene.group.rid === group.id);

  const isOn = groupedLight?.on?.on ?? false;
  const brightness = groupedLight?.dimming?.brightness ?? 0;
  const activeSceneId = groupedLight?.scene?.rid;

  const scenesHtml = roomScenes
    .map((scene) => {
      // ... (Restlicher Szenen-Code bleibt gleich)
    })
    .join("");

  const lightsHtml = roomLights
    .map((light) => {
      // ... (Restlicher Lampen-Code bleibt gleich)
    })
    .join("");

  return `
        `;
}
