// web/static/js/modules/devices.js
import { fetchJson } from "./api.js";

/**
 * Rendert eine Liste von Geräten in dem angegebenen Container.
 * @param {HTMLElement} container - Das DOM-Element, in das die Liste gerendert wird.
 * @param {Array} items - Ein Array von Geräte-Objekten (müssen .name Eigenschaft haben).
 * @param {string} title - Der Titel für diesen Abschnitt.
 */
function renderDeviceList(container, items, title) {
  const section = document.createElement("div");
  section.className = "device-section";

  let content;
  if (items && items.length > 0) {
    content = `<ul>${items
      .map((item) => `<li>${item.name} (ID: ${item.id})</li>`)
      .join("")}</ul>`;
  } else {
    content = "<p>Keine Geräte dieses Typs gefunden.</p>";
  }

  section.innerHTML = `<h3>${title}</h3>${content}`;
  container.appendChild(section);
}

/**
 * Initialisiert die "Geräte"-Seite.
 * Holt die Gerätedaten vom Server und rendert sie.
 */
export async function init() {
  const container = document.getElementById("content-bridge-devices");
  // Nur neu laden, wenn der Inhalt leer ist, um Flackern beim Tab-Wechsel zu vermeiden
  if (
    container.innerHTML.trim() !== "" &&
    !container.innerHTML.includes("wird noch implementiert")
  ) {
    return;
  }

  container.innerHTML =
    '<div class="card"><div class="card-content" id="devices-content-wrapper"><p>Lade Gerätedaten...</p></div></div>';
  const wrapper = document.getElementById("devices-content-wrapper");

  try {
    const data = await fetchJson("/api/bridge/all_items");
    wrapper.innerHTML = ""; // Lade-Text entfernen

    if (data.error) {
      throw new Error(data.error);
    }

    renderDeviceList(wrapper, data.groups, "Räume & Zonen");
    renderDeviceList(wrapper, data.sensors, "Bewegungssensoren");
  } catch (error) {
    wrapper.innerHTML = `<p class="error-message">Fehler beim Laden der Gerätedaten: ${error.message}</p>`;
  }
}
