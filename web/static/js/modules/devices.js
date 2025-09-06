// web/static/js/modules/devices.js
import * as api from "./api.js";

function renderBridgeItems(bridgeData) {
  const container = document.getElementById("bridge-devices-container");
  if (!container) return;

  container.innerHTML = "";

  const deviceTypes = {
    Sensoren: bridgeData.sensors,
    Gruppen: bridgeData.groups,
  };

  for (const [typeName, items] of Object.entries(deviceTypes)) {
    const section = document.createElement("div");
    section.className = "device-section";

    const title = document.createElement("h3");
    title.textContent = typeName;
    section.appendChild(title);

    if (items && items.length > 0) {
      items.forEach((item) => {
        const itemEl = document.createElement("div");
        itemEl.className = "device-item";
        itemEl.innerHTML = `
                    <span>${item.name} (ID: ${item.id})</span>
                    <div class="button-group">
                        <button class="button secondary" data-action="rename-device" data-type="${typeName
                          .toLowerCase()
                          .slice(0, -2)}" data-id="${
          item.id
        }">Umbenennen</button>
                        <button class="button danger" data-action="delete-device" data-type="${typeName
                          .toLowerCase()
                          .slice(0, -2)}" data-id="${item.id}">Löschen</button>
                    </div>
                `;
        section.appendChild(itemEl);
      });
    } else {
      section.innerHTML += "<p>Keine Geräte dieses Typs gefunden.</p>";
    }
    container.appendChild(section);
  }
}

async function handleRenameDevice(type, id) {
  const newName = prompt("Neuer Name:");
  if (newName) {
    try {
      await api.renameBridgeItem(type, id, newName);
      // Reload devices
      const bridgeData = await api.loadBridgeData();
      renderBridgeItems(bridgeData);
    } catch (error) {
      console.error("Fehler beim Umbenennen:", error);
    }
  }
}

async function handleDeleteDevice(type, id) {
  if (confirm("Wirklich löschen?")) {
    try {
      await api.deleteBridgeItem(type, id);
      // Reload devices
      const bridgeData = await api.loadBridgeData();
      renderBridgeItems(bridgeData);
    } catch (error) {
      console.error("Fehler beim Löschen:", error);
    }
  }
}

export function initDevicesPage(bridgeData) {
  renderBridgeItems(bridgeData);

  document
    .getElementById("bridge-devices-container")
    .addEventListener("click", (e) => {
      const button = e.target.closest("[data-action]");
      if (!button) return;

      const action = button.dataset.action;
      const type = button.dataset.type;
      const id = button.dataset.id;

      if (action === "rename-device") {
        handleRenameDevice(type, id);
      } else if (action === "delete-device") {
        handleDeleteDevice(type, id);
      }
    });
}
