export function renderScenes(scenes) {
  const scenesContainer = document.getElementById("scenes-container");
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
