import {
  showToast,
  closeModal,
  toggleDetails,
  icons,
  sectionColors,
  periodNames,
} from "./helpers.js";

let state;
let renderAll;
const routinesContainer = document.getElementById("routines-container");
const modalRoutineContainer = document.getElementById("modal-routine");

export function initRoutines(appState, renderCallback) {
  state = appState;
  renderAll = renderCallback;

  document
    .getElementById("btn-new-routine")
    .addEventListener("click", () => openCreateRoutineModal());
  routinesContainer.addEventListener("click", handleRoutineClick);
}

export function handleRoutineModalAction(e, appState, renderCallback) {
  state = appState;
  renderAll = renderCallback;
  const button = e.target.closest("[data-action]");
  if (!button) return;
  const action = button.dataset.action;

  if (action === "create-routine") handleCreateRoutine();
  if (action === "save-routine") handleSaveRoutine();
  if (action === "cancel-modal") closeModal();
}

// ... Rest der routines.js Datei
