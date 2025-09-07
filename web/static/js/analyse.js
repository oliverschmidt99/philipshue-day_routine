// web/static/js/modules/analyse.js
import { fetchJson } from "./api.js";

let chartInstance = null;

/**
 * Zerstört eine bestehende Chart.js-Instanz, falls vorhanden.
 * Notwendig, um Memory-Leaks und Rendering-Probleme zu vermeiden.
 */
function destroyChart() {
  if (chartInstance) {
    chartInstance.destroy();
    chartInstance = null;
  }
}

/**
 * Zeichnet das Analyse-Diagramm.
 * @param {object} data - Die vom Server empfangenen Daten.
 */
function renderChart(data) {
  destroyChart(); // Vor dem Neuzeichnen altes Diagramm zerstören

  const ctx = document.getElementById("analysis-chart");
  if (!ctx) return;

  chartInstance = new Chart(ctx, {
    type: "line",
    data: {
      labels: data.labels,
      datasets: [
        {
          label: "Helligkeit (lx)",
          data: data.brightness_avg,
          borderColor: "rgba(255, 206, 86, 1)",
          backgroundColor: "rgba(255, 206, 86, 0.2)",
          yAxisID: "yBrightness",
          tension: 0.4,
          pointRadius: 0,
        },
        {
          label: "Temperatur (°C)",
          data: data.temperature_avg,
          borderColor: "rgba(255, 99, 132, 1)",
          backgroundColor: "rgba(255, 99, 132, 0.2)",
          yAxisID: "yTemperature",
          tension: 0.4,
          pointRadius: 0,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          type: "time",
          time: {
            unit: "hour",
            tooltipFormat: "HH:mm",
            displayFormats: {
              hour: "HH:mm",
            },
          },
          title: {
            display: true,
            text: "Uhrzeit",
          },
        },
        yBrightness: {
          type: "linear",
          position: "left",
          title: {
            display: true,
            text: "Helligkeit (lx)",
          },
          beginAtZero: true,
        },
        yTemperature: {
          type: "linear",
          position: "right",
          title: {
            display: true,
            text: "Temperatur (°C)",
          },
          grid: {
            drawOnChartArea: false, // Nur die Haupt-Y-Achse (links) hat Grid-Linien
          },
        },
      },
      plugins: {
        tooltip: {
          mode: "index",
          intersect: false,
        },
      },
    },
  });
}

/**
 * Lädt die Daten vom Server und aktualisiert das Diagramm.
 */
async function loadChartData() {
  const sensorId = document.getElementById("sensor-select").value;
  const date = document.getElementById("analysis-date").value;
  const smoothing = document.getElementById("smoothing-input").value;

  if (!sensorId || !date) {
    showToast("Bitte Sensor und Datum auswählen.", "error");
    return;
  }

  const loadButton = document.getElementById("btn-load-analysis");
  loadButton.disabled = true;
  loadButton.textContent = "Lade...";

  try {
    const data = await fetchJson(
      `/api/data/history?sensor_id=${sensorId}&date=${date}&avg=${smoothing}`
    );
    if (data.labels && data.labels.length > 0) {
      renderChart(data);
    } else {
      destroyChart();
      showToast("Für diesen Zeitraum wurden keine Daten gefunden.", "info");
    }
  } catch (error) {
    destroyChart();
    showToast(`Fehler beim Laden der Daten: ${error.message}`, "error");
  } finally {
    loadButton.disabled = false;
    loadButton.textContent = "Daten laden";
  }
}

/**
 * Initialisiert die Analyse-Seite, rendert die Steuerelemente und richtet Event-Listener ein.
 * @param {object} bridgeData - Die von der Bridge geladenen Daten (Sensoren, etc.).
 */
export function init(bridgeData) {
  const container = document.getElementById("content-analyse");
  if (!container.querySelector("#analysis-controls")) {
    const motionSensors = bridgeData.sensors.filter(
      (s) => s.type === "ZLLPresence"
    );

    const controlsHtml = `
            <div id="analysis-controls" class="card">
                <div class="card-header">
                    <h2>Analyse</h2>
                </div>
                <div class="card-content form-grid">
                    <div class="form-group">
                        <label for="sensor-select">Sensor:</label>
                        <select id="sensor-select" class="styled-select">
                            <option value="">-- Sensor auswählen --</option>
                            ${motionSensors
                              .map(
                                (s) =>
                                  `<option value="${s.id}">${s.name}</option>`
                              )
                              .join("")}
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="analysis-date">Datum:</label>
                        <input type="date" id="analysis-date" value="${
                          new Date().toISOString().split("T")[0]
                        }">
                    </div>
                    <div class="form-group">
                        <label for="smoothing-input">Glättung (Punkte):</label>
                        <input type="number" id="smoothing-input" value="5" min="1" max="50">
                    </div>
                    <div class="form-group">
                        <button type="button" id="btn-load-analysis" class="button">Daten laden</button>
                    </div>
                </div>
            </div>
            <div class="card">
                <div class="chart-container">
                    <canvas id="analysis-chart"></canvas>
                </div>
            </div>
        `;
    container.innerHTML = controlsHtml;

    document
      .getElementById("btn-load-analysis")
      .addEventListener("click", loadChartData);
  }
}
