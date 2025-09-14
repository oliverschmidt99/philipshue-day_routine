import * as api from "../api.js";
import { showToast } from "./helpers.js";

let state;
let chartInstance = null;
const sensorSelect = document.getElementById("analyse-sensor");

export function initAnalyse(appState) {
  state = appState;
  document
    .getElementById("btn-fetch-data")
    .addEventListener("click", loadChartData);
  document.addEventListener("tabchanged_analyse", () => {
    populateAnalyseSensors(state.bridgeData.sensors);
    const today = new Date().toISOString().split("T")[0];
    document.getElementById("analyse-day-picker").value = today;
  });
}

function populateAnalyseSensors(sensors) {
  if (!sensorSelect) return;
  sensorSelect.innerHTML = "";
  const relevantSensors = sensors.filter((s) => s.type === "ZLLPresence");

  if (!relevantSensors || relevantSensors.length === 0) {
    sensorSelect.innerHTML =
      "<option>Keine Bewegungssensoren gefunden</option>";
    return;
  }
  relevantSensors.forEach((sensor) => {
    const option = document.createElement("option");
    option.value = sensor.id;
    option.textContent = sensor.name;
    sensorSelect.appendChild(option);
  });
}

async function loadChartData() {
  const sensorId = sensorSelect.value;
  const date = document.getElementById("analyse-day-picker").value;
  if (!sensorId || !date) {
    showToast("Bitte einen Sensor und ein Datum auswählen.", true);
    return;
  }

  const button = document.getElementById("btn-fetch-data");
  button.disabled = true;
  button.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Lade...';

  try {
    const data = await api.loadChartData(sensorId, date);
    renderChart(data);
  } catch (error) {
    showToast(error.message, true);
    renderChart(null);
  } finally {
    button.disabled = false;
    button.innerHTML = '<i class="fas fa-sync-alt mr-2"></i>Daten laden';
  }
}

function renderChart(data) {
  const ctx = document.getElementById("sensor-chart")?.getContext("2d");
  if (!ctx) return;
  if (chartInstance) chartInstance.destroy();

  if (!data || !Array.isArray(data.labels) || data.labels.length === 0) {
    ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
    ctx.font = "16px Inter, sans-serif";
    ctx.fillStyle = "#6b7280";
    ctx.textAlign = "center";
    ctx.fillText(
      "Keine Daten für diesen Zeitraum verfügbar.",
      ctx.canvas.width / 2,
      50
    );
    return;
  }

  chartInstance = new Chart(ctx, {
    /* ... Chart.js options ... */
  });
}
