import * as api from "../api.js";
import { showToast, toggleDetails, icons, periodNames } from "./helpers.js";

let state;
let statusInterval;
let openStatusCards = [];
const statusContainer = document.getElementById("status-container");
const logContainer = document.getElementById("log-container");

export function initStatus(appState) {
  state = appState;
  document
    .getElementById("btn-refresh-status")
    .addEventListener("click", () => updateStatus(true));
  document.addEventListener("tabchanged_status", startStatusUpdates);
  statusContainer.addEventListener("click", (e) => {
    const button = e.target.closest('[data-action="toggle-status-details"]');
    if (button) {
      const card = button.closest(".status-card");
      const cardName = card.querySelector("h4")?.textContent;
      if (cardName) {
        openStatusCards = openStatusCards.includes(cardName)
          ? openStatusCards.filter((name) => name !== cardName)
          : [...openStatusCards, cardName];
        toggleDetails(button);
      }
    }
  });
}

async function updateStatus(showToastFlag = false) {
  try {
    const { statusData, logText } = await api.updateStatus();
    renderStatus(statusData.routines, statusData.sun_times);
    renderLog(logText);
    updateStatusTimelines();
    if (showToastFlag) showToast("Status aktualisiert!");
  } catch (error) {
    if (showToastFlag)
      showToast(`Status-Update fehlgeschlagen: ${error.message}`, true);
  }
}

function startStatusUpdates() {
  updateStatus();
  clearInterval(statusInterval);
  statusInterval = setInterval(updateStatus, 5000);
}

export function renderStatus(routines, sunTimes) {
  if (!statusContainer) return;
  statusContainer.innerHTML = "";
  if (!routines || routines.length === 0) {
    statusContainer.innerHTML = `<p class="text-gray-500 text-center mt-4">Keine Routinen aktiv oder Status wird geladen...</p>`;
    return;
  }
  routines.forEach((status) => {
    statusContainer.innerHTML += renderStatusTimeline(status, sunTimes);
  });

  document.querySelectorAll(".status-card").forEach((card) => {
    const name = card.querySelector("h4")?.textContent;
    if (name && openStatusCards.includes(name)) {
      toggleDetails(card.querySelector(".status-header"), true);
    }
  });
}

export function renderLog(logText) {
  if (!logContainer) return;
  const isScrolledToBottom =
    logContainer.scrollHeight - logContainer.clientHeight <=
    logContainer.scrollTop + 1;
  logContainer.textContent = logText || "Log-Datei wird geladen...";
  if (isScrolledToBottom) {
    logContainer.scrollTop = logContainer.scrollHeight;
  }
}
//...
