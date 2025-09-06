// web/static/js/modules/analyse.js
import * as api from "./api.js";

let chart = null;

function initializeChart(sensorId) {
  const ctx = document.getElementById("analyse-chart").getContext("2d");
  if (chart) {
    chart.destroy();
  }
  chart = new Chart(ctx, {
    type: "line",
    data: {
      labels: [],
      datasets: [
        {
          label: "Helligkeit",
          data: [],
          borderColor: "rgba(255, 206, 86, 1)",
          backgroundColor: "rgba(255, 206, 86, 0.2)",
          yAxisID: "y-brightness",
        },
        {
          label: "Temperatur",
          data: [],
          borderColor: "rgba(54, 162, 235, 1)",
          backgroundColor: "rgba(54, 162, 235, 0.2)",
          yAxisID: "y-temperature",
        },
      ],
    },
    options: {
      scales: {
        x: {
          type: "time",
          time: {
            unit: "hour",
          },
        },
        "y-brightness": {
          position: "left",
          title: {
            display: true,
            text: "Helligkeit",
          },
        },
        "y-temperature": {
          position: "right",
          title: {
            display: true,
            text: "Temperatur (°C)",
          },
          grid: {
            drawOnChartArea: false,
          },
        },
      },
    },
  });
}

async function loadChartData() {
  const sensorId = document.getElementById("sensor-select").value;
  const period = document.getElementById("period-select").value;
  const date = document.getElementById("date-select").value;
  const avg = document.getElementById("avg-select").value;

  if (!sensorId) return;

  try {
    const data = await api.loadChartData(sensorId, period, date, avg);
    chart.data.labels = data.labels;
    chart.data.datasets[0].data = data.brightness_avg;
    chart.data.datasets[1].data = data.temperature_avg;
    chart.update();
  } catch (error) {
    console.error("Fehler beim Laden der Analysedaten:", error);
  }
}

export function initAnalysePage(bridgeData) {
  const sensorSelect = document.getElementById("sensor-select");
  if (bridgeData && bridgeData.sensors) {
    bridgeData.sensors.forEach((sensor) => {
      const option = document.createElement("option");
      option.value = sensor.id;
      option.textContent = sensor.name;
      sensorSelect.appendChild(option);
    });
  }

  document
    .getElementById("sensor-select")
    .addEventListener("change", loadChartData);
  document
    .getElementById("period-select")
    .addEventListener("change", loadChartData);
  document
    .getElementById("date-select")
    .addEventListener("change", loadChartData);
  document
    .getElementById("avg-select")
    .addEventListener("change", loadChartData);
  document.getElementById("date-select").valueAsDate = new Date();

  initializeChart();
  if (bridgeData.sensors && bridgeData.sensors.length > 0) {
    loadChartData();
  }
}
