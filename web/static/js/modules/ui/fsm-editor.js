// fsm-editor.js - Logik für den visuellen State Machine Editor

let fsmInstance = null;
let appStateRef = null;
let automationIndex = -1;
let selectedElement = null; // Kann ein Zustand ('state') oder ein Übergang ('transition') sein
let isConnecting = false;
let connectionStartNode = null;

class FsmEditor {
  constructor(canvas, sidebar, automation, bridgeData, index) {
    this.canvas = canvas;
    this.sidebar = sidebar;
    this.automation = automation;
    this.bridgeData = bridgeData;
    this.svg = this.canvas.querySelector("svg");
    automationIndex = index;
    this.render();
  }

  render() {
    // Zustände rendern
    const statesContainer = this.canvas.querySelector("#fsm-states-container");
    statesContainer.innerHTML = "";
    this.automation.states.forEach((state) => {
      const stateEl = document.createElement("div");
      stateEl.className =
        "fsm-state absolute p-2 rounded-lg border-2 cursor-pointer";
      stateEl.textContent = state.name;
      stateEl.style.left = `${state.position?.x || 50}px`;
      stateEl.style.top = `${state.position?.y || 50}px`;
      stateEl.dataset.stateName = state.name;

      if (state.name === this.automation.initial_state) {
        stateEl.classList.add("border-green-500");
      } else {
        stateEl.classList.add("border-gray-500");
      }

      statesContainer.appendChild(stateEl);
    });

    this.updateTransitions();
  }

  updateTransitions() {
    // Übergänge (Linien) rendern/aktualisieren
    this.svg.innerHTML = "";
    this.automation.transitions.forEach((trans, index) => {
      const fromState = this.automation.states.find(
        (s) => s.name === trans.from
      );
      const toState = this.automation.states.find((s) => s.name === trans.to);
      if (!fromState || !toState) return;

      const fromEl = this.canvas.querySelector(
        `[data-state-name="${trans.from}"]`
      );
      const toEl = this.canvas.querySelector(`[data-state-name="${trans.to}"]`);

      const line = document.createElementNS(
        "http://www.w3.org/2000/svg",
        "line"
      );
      const x1 = fromEl.offsetLeft + fromEl.offsetWidth / 2;
      const y1 = fromEl.offsetTop + fromEl.offsetHeight / 2;
      const x2 = toEl.offsetLeft + toEl.offsetWidth / 2;
      const y2 = toEl.offsetTop + toEl.offsetHeight / 2;

      line.setAttribute("x1", x1);
      line.setAttribute("y1", y1);
      line.setAttribute("x2", x2);
      line.setAttribute("y2", y2);
      line.setAttribute("stroke", "#6b7280");
      line.setAttribute("stroke-width", "2");
      line.setAttribute("marker-end", "url(#arrow)");
      line.dataset.transitionIndex = index;
      this.svg.appendChild(line);
    });
  }

  select(element) {
    // Alte Auswahl aufheben
    this.canvas
      .querySelectorAll(".selected")
      .forEach((el) =>
        el.classList.remove("selected", "border-blue-500", "stroke-blue-500")
      );
    this.sidebar.innerHTML = "";

    selectedElement = element;
    if (!selectedElement) return;

    selectedElement.element.classList.add("selected");
    if (selectedElement.type === "state") {
      selectedElement.element.classList.add("border-blue-500");
      this.renderStateSidebar();
    } else {
      selectedElement.element.setAttribute("stroke", "#3b82f6");
      selectedElement.element.classList.add("selected");
      this.renderTransitionSidebar();
    }
  }

  renderStateSidebar() {
    const stateName = selectedElement.id;
    const state = this.automation.states.find((s) => s.name === stateName);
    const sceneOptions = appStateRef.bridgeData.scenes
      .map(
        (s) =>
          `<option value="${s.metadata.name}" ${
            state.action?.scene_name === s.metadata.name ? "selected" : ""
          }>${s.metadata.name}</option>`
      )
      .join("");

    this.sidebar.innerHTML = `
            <h4 class="font-bold text-lg mb-2">Zustand: ${stateName}</h4>
            <div class="space-y-4">
                 <div>
                    <label class="block text-sm font-medium">Aktion bei Eintritt</label>
                    <select data-sidebar-prop="action.scene_name" class="mt-1 block w-full rounded-md border-gray-600 bg-gray-700 shadow-sm">
                        <option value="">Keine Szene</option>
                        ${sceneOptions}
                    </select>
                </div>
                <div class="flex items-center">
                    <input type="checkbox" id="is_initial_state" ${
                      this.automation.initial_state === stateName
                        ? "checked"
                        : ""
                    } class="h-4 w-4 rounded bg-gray-600 border-gray-500">
                    <label for="is_initial_state" class="ml-2">Ist Initialzustand</label>
                </div>
                <button data-action="delete-state" class="text-red-500 hover:text-red-400 text-sm">Zustand löschen</button>
            </div>
        `;
  }

  renderTransitionSidebar() {
    const transIndex = selectedElement.id;
    const transition = this.automation.transitions[transIndex];
    this.sidebar.innerHTML = `
            <h4 class="font-bold text-lg mb-2">Übergang</h4>
            <p class="text-sm text-gray-400 mb-2">${transition.from} → ${transition.to}</p>
            <div class="space-y-2">
                <h5 class="font-semibold">Bedingungen</h5>
                <div id="fsm-conditions-container" class="space-y-2">
                    </div>
                <button data-action="add-condition" class="text-blue-400 hover:text-blue-300 text-sm">+ Bedingung hinzufügen</button>
            </div>
            <hr class="my-4 border-gray-600">
            <button data-action="delete-transition" class="text-red-500 hover:text-red-400 text-sm">Übergang löschen</button>
        `;
  }
}

export function initFsmEditor(canvas, sidebar, automation, bridgeData, index) {
  fsmInstance = new FsmEditor(canvas, sidebar, automation, bridgeData, index);
}

export function setFsmAppState(state) {
  appStateRef = state;
}

// Event handler für den Editor selbst
export function handleFsmEditorEvent(e) {
  const target = e.target;
  const button = target.closest("[data-action]");
  const action = button?.dataset.action;

  if (action === "add-state") {
    const newStateName = `Neuer Zustand ${
      fsmInstance.automation.states.length + 1
    }`;
    fsmInstance.automation.states.push({
      name: newStateName,
      position: { x: 100, y: 100 },
      action: { scene_name: "" },
    });
    fsmInstance.render();
  }

  if (action === "toggle-connect-mode") {
    isConnecting = !isConnecting;
    button.classList.toggle("bg-blue-600", isConnecting);
    button.classList.toggle("text-white", isConnecting);
    connectionStartNode = null;
    fsmInstance.canvas.style.cursor = isConnecting ? "crosshair" : "default";
  }

  const stateEl = target.closest(".fsm-state");
  if (stateEl) {
    const stateName = stateEl.dataset.stateName;
    if (isConnecting) {
      if (!connectionStartNode) {
        connectionStartNode = stateName;
        stateEl.classList.add("border-yellow-400"); // Markiere Start
      } else if (connectionStartNode !== stateName) {
        // Verbindung erstellen
        fsmInstance.automation.transitions.push({
          from: connectionStartNode,
          to: stateName,
          conditions: [],
        });
        // Reset
        isConnecting = false;
        document
          .querySelector('[data-action="toggle-connect-mode"]')
          .classList.remove("bg-blue-600", "text-white");
        fsmInstance.canvas.style.cursor = "default";
        fsmInstance.render();
      }
    } else {
      fsmInstance.select({ type: "state", id: stateName, element: stateEl });
    }
  }

  const lineEl = target.closest("line");
  if (lineEl) {
    fsmInstance.select({
      type: "transition",
      id: lineEl.dataset.transitionIndex,
      element: lineEl,
    });
  }
}
