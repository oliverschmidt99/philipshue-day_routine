let state;

export function initDevices(appState) {
  state = appState;
  document
    .getElementById("devices-tabs")
    ?.addEventListener("click", handleDeviceTabClick);
  document.addEventListener("tabchanged_devices", () =>
    renderBridgeDevices(state.bridgeData)
  );
}

function handleDeviceTabClick(e) {
  const button = e.target.closest(".device-tab");
  if (!button) return;
  const tabId = button.dataset.tab;

  document
    .querySelectorAll(".device-tab")
    .forEach((btn) => btn.classList.remove("tab-active"));
  button.classList.add("tab-active");

  document
    .querySelectorAll(".device-content-pane")
    .forEach((pane) => pane.classList.add("hidden"));
  document
    .getElementById(`devices-content-${tabId}`)
    ?.classList.remove("hidden");
}

export function renderBridgeDevices(bridgeData) {
  const containers = {
    lights_and_plugs: document.getElementById(
      "devices-content-lights_and_plugs"
    ),
    switches: document.getElementById("devices-content-switches"),
    sensors: document.getElementById("devices-content-sensors"),
    groups: document.getElementById("devices-content-groups"),
  };

  if (!containers.lights_and_plugs) return;

  containers.lights_and_plugs.innerHTML = createDeviceListHTML(
    bridgeData.devices?.lights_and_plugs,
    "Modell"
  );
  containers.switches.innerHTML = createDeviceListHTML(
    bridgeData.devices?.switches,
    "Modell"
  );
  containers.sensors.innerHTML = createDeviceListHTML(
    bridgeData.devices?.sensors,
    "Modell"
  );
  containers.groups.innerHTML = createDeviceListHTML(
    [...(bridgeData.rooms || []), ...(bridgeData.zones || [])],
    "Anzahl Lichter"
  );
}

function createDeviceListHTML(items, detailHeader) {
  if (!items || items.length === 0) {
    return `<p class="text-gray-500">Keine Geräte in dieser Kategorie gefunden.</p>`;
  }
  let html = `<div class="space-y-2">`;
  items.forEach((item) => {
    let detail = item.lights
      ? `${item.lights.length}`
      : item.product_name || "";
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
