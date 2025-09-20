import * as api from "./api.js";
import * as uiShared from "./ui/shared.js";
import * as uiHome from "./ui/home.js";
import * as uiModals from "./ui/modals.js";
import * as uiAutomations from "./ui/automations.js";
import * as uiScenes from "./ui/scenes.js";

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
  const hueValue = Math.round((hsv.h / 360) * 65535);
  const satValue = Math.round((hsv.s / 100) * 254);

  const state = {
    on: { on: true },
    color: { hue: hueValue, saturation: satValue },
    dimming: { brightness: hsv.v },
  };

  await api.setGroupState(groupId, state);
}, 150);

async function handleGlobalClick(e) {
  const target = e.target;
  const button = target.closest("[data-action]");

  if (target.classList.contains("modal-backdrop")) {
    uiModals.closeModal();
    if (appState.liveColorPicker)
      appState.liveColorPicker.off("color:change", handleLiveColorChange);
    return;
  }

  if (!button) return;

  const action = button.dataset.action;

  const actions = {
    "toggle-group-power": async () => {
      e.stopPropagation();
      const groupId = button.dataset.groupId;
      const isChecked = e.target.checked;
      if (groupId) {
        button.disabled = true;
        await api.setGroupState(groupId, { on: { on: isChecked } });
        await updateHomeStatus();
        button.disabled = false;
      }
    },
    "open-room-detail": () => {
      const roomCard = target.closest(".room-card");
      const groupId = roomCard.dataset.groupId;
      const group = [
        ...appState.bridgeData.rooms,
        ...appState.bridgeData.zones,
      ].find((g) => g.id === groupId);
      if (group) {
        const detailView = uiHome.renderRoomDetail(
          group,
          appState.bridgeData.lights,
          appState.bridgeData.scenes
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
          setTimeout(updateHomeStatus, 1500);
        } catch (error) {
          uiShared.showToast(`Fehler: ${error.message}`, true);
        }
      }
    },
    "toggle-light-power": async () => {
      const lightId = button.dataset.lightId;
      const isChecked = e.target.checked;
      if (lightId) {
        button.disabled = true;
        await api.setLightState(lightId, { on: { on: isChecked } });
        setTimeout(async () => {
          appState.bridgeData = await api.loadBridgeData();
          const roomDetailContainer = document.getElementById(
            "room-detail-container"
          );
          const groupName = roomDetailContainer.querySelector("h2").textContent;
          const group = [
            ...appState.bridgeData.rooms,
            ...appState.bridgeData.zones,
          ].find((g) => g.name === groupName);
          if (group) {
            roomDetailContainer.innerHTML = uiHome.renderRoomDetail(
              group,
              appState.bridgeData.lights,
              appState.bridgeData.scenes
            );
          }
          button.disabled = false;
        }, 500);
      }
    },
    "cancel-modal": () => {
      uiModals.closeModal();
      if (appState.liveColorPicker)
        appState.liveColorPicker.off("color:change", handleLiveColorChange);
    },
  };

  if (actions[action]) {
    actions[action]();
  }
}

// Funktionen zur Statusaktualisierung
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
  document.querySelectorAll('nav button[id^="tab-"]').forEach((button) => {
    button.addEventListener("click", handleTabClick);
  });

  document.body.addEventListener("input", (e) => {
    if (e.target.id === "live-brightness-slider") {
      handleLiveBrightness(e);
    }
  });
}
