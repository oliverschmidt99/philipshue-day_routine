import * as api from "./api.js";
import * as uiShared from "./ui/shared.js";
import * as uiHome from "./ui/home.js";
import * as uiModals from "./ui/modals.js";
import * as uiAutomations from "./ui/automations.js";
// KORREKTUR: Der Pfad wurde angepasst.
import {
  initFsmEditor,
  setFsmAppState,
  handleFsmEditorEvent,
} from "./ui/fsm-editor.js";

let appState = {}; // Wird von main.js initialisiert

const debounce = (func, delay) => {
  let timeout;
  return function (...args) {
    const context = this;
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(context, args), delay);
  };
};

const handleLiveBrightness = debounce(async (e) => {
  const groupId = e.target.dataset.groupId;
  const brightness = parseInt(e.target.value, 10);
  if (groupId) {
    await api.setGroupState(groupId, { dimming: { brightness } });
  }
}, 150);

const handleLiveColorChange = debounce(async (color) => {
  const groupId = document.getElementById("live-brightness-slider").dataset
    .groupId;
  if (!groupId) return;
  const hsv = color.hsv;
  const state = {
    on: { on: true },
    color: {
      xy: { x: color.xy.x, y: color.xy.y },
    },
    dimming: { brightness: hsv.v },
  };
  await api.setGroupState(groupId, state);
}, 150);

// Zentrale Funktion zum Neu-Rendern der Raum-Detailansicht
const refreshRoomDetail = async (groupId) => {
  const [newBridgeData, newGroupedLights] = await Promise.all([
    api.loadBridgeData(),
    api.loadGroupedLights(),
  ]);
  appState.bridgeData = newBridgeData;
  appState.groupedLights = newGroupedLights;

  const group = [
    ...appState.bridgeData.rooms,
    ...appState.bridgeData.zones,
  ].find((g) => g.id === groupId);
  const groupedLight = appState.groupedLights.find(
    (gl) => gl.owner.rid === groupId
  );

  if (group) {
    document.getElementById("room-detail-container").innerHTML =
      uiHome.renderRoomDetail(
        group,
        appState.bridgeData.lights,
        appState.bridgeData.scenes,
        groupedLight
      );
  }
};

async function handleGlobalClick(e) {
  const target = e.target;
  const button = target.closest("[data-action]");

  if (target.classList.contains("modal-backdrop")) {
    uiModals.closeModal();
    if (appState.liveColorPicker)
      appState.liveColorPicker.off("color:change", handleLiveColorChange);
    return;
  }

  if (!button) {
    // Klick-Events für den FSM-Editor abfangen
    if (e.target.closest(".fsm-canvas") || e.target.closest(".fsm-sidebar")) {
      handleFsmEditorEvent(e);
    }
    return;
  }

  const action = button.dataset.action;
  const automationCard = target.closest("[data-index]");
  const index = automationCard?.dataset.index;

  const actions = {
    // ##### ZUHAUSE & SZENEN #####
    "toggle-group-power": async () => {
      e.stopPropagation();
      const groupId = button.dataset.groupId;
      const isChecked = e.target.checked;
      await api.setGroupState(groupId, { on: { on: isChecked } });
      await updateHomeStatus();
    },
    "toggle-group-power-detail": async () => {
      const groupId = button.dataset.groupId;
      const isChecked = e.target.checked;
      await api.setGroupState(groupId, { on: { on: isChecked } });
      await refreshRoomDetail(groupId);
    },
    "set-group-brightness-detail": debounce(async (event) => {
      const groupId = event.target.dataset.groupId;
      const brightness = parseInt(event.target.value, 10);
      await api.setGroupState(groupId, { dimming: { brightness } });
    }, 150),
    "open-room-detail": async () => {
      const roomCard = target.closest(".room-card");
      const groupId = roomCard.dataset.groupId;
      const group = [
        ...appState.bridgeData.rooms,
        ...appState.bridgeData.zones,
      ].find((g) => g.id === groupId);
      if (group) {
        const groupedLight = appState.groupedLights.find(
          (gl) => gl.owner.rid === groupId
        );
        const detailView = uiHome.renderRoomDetail(
          group,
          appState.bridgeData.lights,
          appState.bridgeData.scenes,
          groupedLight
        );
        document.getElementById("room-detail-container").innerHTML = detailView;
        document.getElementById("home-container").classList.add("hidden");
        document
          .getElementById("room-detail-container")
          .classList.remove("hidden");
        stopStatusUpdates();
      }
    },
    "back-to-home": () => {
      document.getElementById("home-container").classList.remove("hidden");
      document.getElementById("room-detail-container").classList.add("hidden");
      startStatusUpdates(updateHomeStatus);
    },
    "open-color-control": () => {
      const groupId = button.dataset.groupId;
      const groupLight = appState.groupedLights.find(
        (gl) => gl.owner.rid === groupId
      );
      uiModals.openColorControlModal(groupId, groupLight);
      appState.liveColorPicker = new iro.ColorPicker(
        "#live-color-picker-container",
        {
          width: 280,
          color: "#fff",
          borderWidth: 1,
          borderColor: "#fff",
          layout: [
            { component: iro.ui.Wheel },
            { component: iro.ui.Slider, options: { sliderType: "value" } },
          ],
        }
      );
      appState.liveColorPicker.on("color:change", handleLiveColorChange);
    },
    "recall-scene": async () => {
      const sceneId = button.dataset.sceneId;
      const groupId = button.dataset.groupId;
      if (sceneId && groupId) {
        try {
          await api.recallScene(groupId, sceneId);
          uiShared.showToast("Szene wird aktiviert!");
          setTimeout(() => refreshRoomDetail(groupId), 1000);
        } catch (error) {
          uiShared.showToast(`Fehler: ${error.message}`, true);
        }
      }
    },
    "toggle-light-power": async () => {
      const lightId = button.dataset.lightId;
      const isChecked = e.target.checked;
      const groupId = document.querySelector(
        '#room-detail-container [data-action="open-color-control"]'
      ).dataset.groupId;
      if (lightId) {
        await api.setLightState(lightId, { on: { on: isChecked } });
        setTimeout(() => refreshRoomDetail(groupId), 800);
      }
    },

    // ##### AUTOMATIONEN #####
    "toggle-automation-details": () => {
      const header = button.closest(".automation-header");
      const detailsContainer = header.nextElementSibling;
      const icon = header.querySelector("i.fa-chevron-down");
      const type = header.closest("[data-type]").dataset.type;

      if (detailsContainer.classList.contains("hidden")) {
        const automation = appState.config.automations[index];
        const renderer =
          uiAutomations.automationTypeDetails[type].detailsRenderer;
        detailsContainer.innerHTML = renderer(
          automation,
          appState.bridgeData,
          index
        );

        if (type === "state_machine") {
          const canvas = detailsContainer.querySelector(
            `#fsm-editor-canvas-${index}`
          );
          const sidebar = detailsContainer.querySelector(
            `#fsm-editor-sidebar-${index}`
          );
          setFsmAppState(appState);
          initFsmEditor(
            canvas,
            sidebar,
            automation,
            appState.bridgeData,
            index
          );
        }

        detailsContainer.classList.remove("hidden");
        setTimeout(() => {
          detailsContainer.style.maxHeight =
            detailsContainer.scrollHeight + "px";
          icon.style.transform = "rotate(180deg)";
        }, 10);
      } else {
        detailsContainer.style.maxHeight = "0px";
        icon.style.transform = "rotate(0deg)";
        detailsContainer.addEventListener(
          "transitionend",
          () => {
            detailsContainer.classList.add("hidden");
            detailsContainer.innerHTML = "";
          },
          { once: true }
        );
      }
    },
    "create-automation": () => {
      const type = button.dataset.type;
      uiModals.closeModal();
      if (type === "routine")
        uiModals.openCreateRoutineModal(appState.bridgeData);
      if (type === "timer") uiModals.openCreateTimerModal(appState.bridgeData);
      if (type === "state_machine")
        uiModals.openCreateStateMachineModal(appState.bridgeData);
    },
    "save-new-automation": () => {
      const type = button.dataset.type;
      const name = document.getElementById("new-automation-name").value;
      if (!name) {
        uiShared.showToast(
          "Bitte gib einen Namen für die Automation ein.",
          true
        );
        return;
      }
      let newAutomation = { name, enabled: true, type };

      if (type === "routine") {
        const [groupId, groupName] = document
          .getElementById("new-routine-group")
          .value.split("|");
        Object.assign(newAutomation, {
          room_name: groupName,
          daily_time: { H1: 7, M1: 0, H2: 23, M2: 0 },
          morning: {
            scene_name: "aus",
            x_scene_name: "entspannen",
            motion_check: true,
            wait_time: { min: 1, sec: 0 },
            do_not_disturb: false,
            bri_check: false,
          },
          day: {
            scene_name: "aus",
            x_scene_name: "konzentrieren",
            motion_check: true,
            wait_time: { min: 1, sec: 0 },
            do_not_disturb: false,
            bri_check: false,
          },
          evening: {
            scene_name: "aus",
            x_scene_name: "entspannen",
            motion_check: true,
            wait_time: { min: 1, sec: 0 },
            do_not_disturb: false,
            bri_check: false,
          },
          night: {
            scene_name: "aus",
            x_scene_name: "nachtlicht",
            motion_check: true,
            wait_time: { min: 1, sec: 0 },
            do_not_disturb: false,
            bri_check: false,
          },
        });
      }
      if (type === "timer") {
        Object.assign(newAutomation, {
          duration_minutes: parseInt(
            document.getElementById("timer-duration").value,
            10
          ),
          action: {
            target_room: document.getElementById("timer-target-room").value,
            scene_name: document.getElementById("timer-scene-name").value,
          },
          triggers: [],
        });
      }
      if (type === "state_machine") {
        Object.assign(newAutomation, {
          target_room: document.getElementById("fsm-target-room").value,
          initial_state: "Start",
          states: [{ name: "Start", action: {}, position: { x: 50, y: 50 } }],
          transitions: [],
        });
      }

      if (!appState.config.automations) appState.config.automations = [];
      appState.config.automations.push(newAutomation);
      uiModals.closeModal();
      uiAutomations.renderAutomations(
        appState.config,
        appState.bridgeData,
        appState
      );
      uiShared.showToast(
        "Neue Automation erstellt. Speichern nicht vergessen!"
      );
    },

    // ##### ALLGEMEIN #####
    "cancel-modal": () => {
      uiModals.closeModal();
      if (appState.liveColorPicker)
        appState.liveColorPicker.off("color:change", handleLiveColorChange);
    },
  };

  if (actions[action]) {
    await actions[action](e);
  }
}

const updateHomeStatus = async () => {
  try {
    [appState.bridgeData, appState.groupedLights] = await Promise.all([
      api.loadBridgeData(),
      api.loadGroupedLights(),
    ]);
    uiHome.renderHome(appState.bridgeData, appState.groupedLights);
  } catch (e) {
    console.error("Fehler bei updateHomeStatus:", e);
  }
};

const startStatusUpdates = (updateFunction) => {
  if (appState.statusInterval) clearInterval(appState.statusInterval);
  if (document.hidden) return;
  updateFunction();
  const intervalTime =
    (appState.config?.global_settings?.status_interval_s || 5) * 1000;
  appState.statusInterval = setInterval(updateFunction, intervalTime);
};

const stopStatusUpdates = () => {
  clearInterval(appState.statusInterval);
  appState.statusInterval = null;
};

function handleTabClick(e) {
  const button = e.currentTarget;
  document.querySelectorAll('nav button[id^="tab-"]').forEach((btn) => {
    btn.classList.remove("tab-active", "text-blue-400", "border-blue-400");
    btn.classList.add("text-gray-500", "border-transparent");
  });
  document
    .querySelectorAll(".content-section")
    .forEach((content) => content.classList.add("hidden"));
  button.classList.add("tab-active", "text-blue-400", "border-blue-400");
  button.classList.remove("text-gray-500", "border-transparent");
  const contentId = button.id.replace("tab-", "content-");
  const contentElement = document.getElementById(contentId);
  if (contentElement) contentElement.classList.remove("hidden");
  stopStatusUpdates();
  if (contentId === "content-zuhause") {
    document.getElementById("home-container").classList.remove("hidden");
    document.getElementById("room-detail-container").classList.add("hidden");
    startStatusUpdates(updateHomeStatus);
  }
}

export function initializeEventHandlers(initialState) {
  appState = initialState;
  document.body.addEventListener("click", handleGlobalClick);
  document.body.addEventListener("input", (e) => {
    const target = e.target;
    const action = target.dataset.action;
    if (action === "set-group-brightness-detail") {
      handleGlobalClick(e);
    }
  });
  document.querySelectorAll('nav button[id^="tab-"]').forEach((button) => {
    button.addEventListener("click", handleTabClick);
  });

  document
    .getElementById("btn-new-automation")
    ?.addEventListener("click", () => {
      uiModals.openSelectAutomationTypeModal();
    });
}
