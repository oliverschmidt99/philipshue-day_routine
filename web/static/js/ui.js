/**
 * Rendert die Liste der Routinen.
 * @param {object} config - Das gesamte Konfigurationsobjekt.
 * @param {object} bridgeData - Die von der Bridge geladenen Daten.
 */
export function renderRoutines(config, bridgeData) {
  const container = document.getElementById("routines-container");
  if (!container) return;

  container.innerHTML = ""; // Leere den Container
  if (!config.routines || config.routines.length === 0) {
    container.innerHTML =
      '<div class="card"><p>Keine Routinen erstellt. Zeit, eine neue anzulegen!</p></div>';
    return;
  }

  config.routines.forEach((routine, index) => {
    const roomConf = config.rooms.find((r) => r.name === routine.room_name);
    const sensor =
      roomConf && roomConf.sensor_id
        ? bridgeData.sensors.find((s) => s.id == roomConf.sensor_id)
        : null;

    const routineCard = document.createElement("div");
    routineCard.className = "card routine-card";
    routineCard.dataset.index = index;

    const dailyTime = routine.daily_time || {};
    const startTime = `${String(dailyTime.H1 || 0).padStart(2, "0")}:${String(
      dailyTime.M1 || 0
    ).padStart(2, "0")}`;
    const endTime = `${String(dailyTime.H2 || 23).padStart(2, "0")}:${String(
      dailyTime.M2 || 59
    ).padStart(2, "0")}`;

    routineCard.innerHTML = `
            <div class="card-header">
                <h3>${routine.name}</h3>
                <div class="status-indicator ${
                  routine.enabled ? "active" : ""
                }">
                    ${routine.enabled ? "Aktiviert" : "Deaktiviert"}
                </div>
            </div>
            <div class="card-content">
                <p><strong>Raum:</strong> ${routine.room_name}</p>
                <p><strong>Sensor:</strong> ${
                  sensor ? sensor.name : "Kein Sensor"
                }</p>
                <p><strong>Aktiv von:</strong> ${startTime} bis ${endTime} Uhr</p>
            </div>
            <div class="card-footer">
                <button class="button secondary">Bearbeiten</button>
                <button class="button danger">Löschen</button>
            </div>
        `;
    container.appendChild(routineCard);
  });
}
