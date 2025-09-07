// web/static/js/modules/ui.js

export const icons = { morning: "🌅", day: "☀️", evening: "🌇", night: "🌙" };
export const periodNames = {
  morning: "Morgen",
  day: "Tag",
  evening: "Abend",
  night: "Nacht",
};

export function showToast(message, type = "info") {
  window.showToast(message, type);
}

export function closeModal() {
  const modal = document.getElementById("demo-modal");
  if (modal) modal.style.display = "none";
}

export function toggleAccordion(button) {
  button.classList.toggle("active");
  const content = button.nextElementSibling;
  if (content.style.maxHeight) {
    content.style.maxHeight = null;
  } else {
    content.style.maxHeight = content.scrollHeight + "px";
  }
  const icon = button.querySelector(".icon-chevron");
  if (icon) {
    icon.style.transform = button.classList.contains("active")
      ? "rotate(180deg)"
      : "rotate(0deg)";
  }
}

export function updateClock() {
  const clockElement = document.getElementById("clock");
  if (clockElement)
    clockElement.textContent = new Date().toLocaleTimeString("de-DE", {
      hour: "2-digit",
      minute: "2-digit",
    });
}

export function renderSunTimes(sunData) {
  const sunTimesContainer = document.getElementById("sun-times");
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
      sunTimesContainer.innerHTML = `<span>🌅 ${sunrise}</span> <span style="margin-left: 0.5rem;">🌇 ${sunset}</span>`;
    } else {
      sunTimesContainer.innerHTML = `<span>--:--</span>`;
    }
  }
}

export function renderRoutines(config, bridgeData) {
  const container = document.getElementById("routines-container");
  if (!container) return;
  container.innerHTML = "";
  if (!config.routines || config.routines.length === 0) {
    container.innerHTML = `<p>Noch keine Routinen erstellt.</p>`;
    return;
  }

  config.routines.forEach((routine, index) => {
    const routineEl = document.createElement("div");
    routineEl.className = "accordion-container routine-card";
    routineEl.dataset.index = index;

    const sectionsHtml = Object.keys(periodNames)
      .map((name) => {
        const section = routine[name];
        if (!section) return "";
        return `<p><strong>${periodNames[name]}:</strong> ${
          section.scene_name || "N/A"
        }</p>`;
      })
      .join("");

    routineEl.innerHTML = `
            <button type="button" class="accordion-button" data-action="toggle-routine-details">
                <span>${routine.name} <small>(${routine.room_name})</small></span>
                <img src="/static/assets/icons/icon_chevron_down.svg" alt="Details" class="icon-chevron">
            </button>
            <div class="accordion-content">
                <div style="padding: 1rem;">
                    ${sectionsHtml}
                    <div class="button-group" style="margin-top: 1rem;">
                        <button type="button" class="button secondary" data-action="edit-routine">Bearbeiten</button>
                        <button type="button" class="button danger" data-action="delete-routine">Löschen</button>
                    </div>
                </div>
            </div>`;
    container.appendChild(routineEl);
  });
}

export function renderScenes(scenes) {
  const container = document.getElementById("scenes-container");
  if (!container) return;
  container.innerHTML = "";
  if (!scenes || Object.keys(scenes).length === 0) {
    container.innerHTML = `<p>Noch keine Szenen erstellt.</p>`;
    return;
  }

  let sceneGrid = document.createElement("div");
  sceneGrid.className = "grid-container";

  for (const [name, scene] of Object.entries(scenes)) {
    const sceneEl = document.createElement("div");
    sceneEl.className = "card scene-card";
    sceneEl.dataset.name = name;
    sceneEl.innerHTML = `
            <h4>${name.replace(/_/g, " ")}</h4>
            <p>Status: <strong>${scene.status ? "An" : "Aus"}</strong></p>
            <p>Helligkeit: <strong>${scene.bri}</strong></p>
            <div class="button-group">
                <button type="button" class="button secondary" data-action="edit-scene">Bearbeiten</button>
                <button type="button" class="button danger" data-action="delete-scene">Löschen</button>
            </div>`;
    sceneGrid.appendChild(sceneEl);
  }
  container.appendChild(sceneGrid);
}

export function renderStatus(statuses) {
  const statusContainer = document.getElementById("status-container");
  if (!statusContainer) return;
  statusContainer.innerHTML = "";
  if (!statuses || statuses.length === 0) {
    statusContainer.innerHTML = `<p>Keine Routinen aktiv.</p>`;
    return;
  }
  statuses.forEach((status) => {
    const statusEl = document.createElement("div");
    statusEl.className = "card status-card";
    statusEl.innerHTML = `
            <h4>${status.name}</h4>
            <p><strong>Aktueller Zeitraum:</strong> ${
              icons[status.period] || "❓"
            } ${periodNames[status.period] || status.period}</p>
            <p><strong>Status:</strong> ${
              status.enabled ? "Aktiviert" : "Deaktiviert"
            }</p>
            <p><strong>Letzte Szene:</strong> ${status.last_scene}</p>
            <p><strong>Bewegung:</strong> ${status.motion_status}</p>
        `;
    statusContainer.appendChild(statusEl);
  });
}

export function renderLog(logText) {
  const logContainer = document.getElementById("log-container");
  if (!logContainer) return;
  const isScrolledToBottom =
    logContainer.scrollHeight - logContainer.clientHeight <=
    logContainer.scrollTop + 1;
  logContainer.textContent = logText || "Log-Datei wird geladen...";
  if (isScrolledToBottom) {
    logContainer.scrollTop = logContainer.scrollHeight;
  }
}

export function openSceneModal(scene, sceneName, config) {
  const isEditing = sceneName !== null;
  const title = isEditing ? "Szene bearbeiten" : "Neue Szene";
  const content = `
        <form id="form-scene" style="display: flex; flex-direction: column; gap: 1rem;">
            <input type="hidden" id="scene-original-name" value="${ sceneName || "" }">
            <div>
                <label for="scene-name">Name</label>
                <input type="text" id="scene-name" value="${ isEditing ? sceneName.replace(/_/g, " ") : "" }" required style="width: 100%; padding: 0.5rem; border: 1px solid var(--border-color); border-radius: 4px;">
            </div>
            <div>
                <label for="scene-bri">Helligkeit: <span id="bri-value">${ scene.bri || 0 }</span></label>
                <input type="range" id="scene-bri" min="0" max="254" value="${ scene.bri || 0 }">
            </div>
             <div>
                <label for="scene-ct">Farbtemperatur: <span id="ct-value">${ scene.ct || 366 }</span></label>
                <input type="range" id="scene-ct" min="153" max="500" value="${ scene.ct || 366 }">
            </div>
             <div>
                <label><input type="checkbox" id="scene-status" ${ scene.status ? "checked" : "" }> Licht an</label>
            </div>
        </form>`;

  const actions = `<button type="button" class="button secondary" data-action="cancel-modal">Abbrechen</button>
                     <button type="button" class="button" data-action="save-scene">Speichern</button>`;

  window.showModal(title, content, actions);

  // Event-Listener programmatisch hinzufügen
  const briSlider = document.getElementById('scene-bri');
  const ctSlider = document.getElementById('scene-ct');
  const briValue = document.getElementById('bri-value');
  const ctValue = document.getElementById('ct-value');

  if (briSlider && briValue) {
    briSlider.addEventListener('input', (e) => {
      briValue.textContent = e.target.value;
    });
  }
  if (ctSlider && ctValue) {
    ctSlider.addEventListener('input', (e) => {
      ctValue.textContent = e.target.value;
    });
  }
}

export function openCreateRoutineModal(bridgeData, config) {
  const title = "Neue Routine erstellen";
  const groupOptions = bridgeData.groups
    .map((g) => `<option value="${g.id}|${g.name}">${g.name}</option>`)
    .join("");
  const content = `
        <form id="form-create-routine" style="display: flex; flex-direction: column; gap: 1rem;">
            <div>
                <label for="new-routine-name">Name</label>
                <input type="text" id="new-routine-name" required style="width: 100%; padding: 0.5rem; border: 1px solid var(--border-color); border-radius: 4px;">
            </div>
            <div>
                <label for="new-routine-group">Raum / Zone</label>
                <select id="new-routine-group" style="width: 100%; padding: 0.5rem; border: 1px solid var(--border-color); border-radius: 4px;">${groupOptions}</select>
            </div>
        </form>`;
  const actions = `<button type="button" class="button secondary" data-action="cancel-modal">Abbrechen</button>
                     <button type="button" class="button" data-action="create-routine">Erstellen</button>`;
  window.showModal(title, content, actions);
}
