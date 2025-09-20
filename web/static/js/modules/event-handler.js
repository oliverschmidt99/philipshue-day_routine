import * as api from "./api.js";
import * as uiShared from "./ui/shared.js";
import * as uiHome from "./ui/home.js";
import * as uiModals from "./ui/modals.js";

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
  // Holen Sie sich die neuesten Daten von der Bridge
  const [newBridgeData, newGroupedLights] = await Promise.all([
    api.loadBridgeData(),
    api.loadGroupedLights(),
  ]);
  appState.bridgeData = newBridgeData;
  appState.groupedLights = newGroupedLights;

  // Finden Sie die spezifische Gruppe und deren Lichtstatus
  const group = [
    ...appState.bridgeData.rooms,
    ...appState.bridgeData.zones,
  ].find((g) => g.id === groupId);
  const groupedLight = appState.groupedLights.find(
    (gl) => gl.owner.rid === groupId
  );

  // Rendern Sie die Ansicht neu
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
  if (!button) return;

  const action = button.dataset.action;

  const actions = {
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
    "cancel-modal": () => {
      uiModals.closeModal();
      if (appState.liveColorPicker)
        appState.liveColorPicker.off("color:change", handleLiveColorChange);
    },
    "open-scene-modal": () => {
      const groupId = button.dataset.groupId;
      const group = [
        ...appState.bridgeData.rooms,
        ...appState.bridgeData.zones,
      ].find((g) => g.id === groupId);
      const lightsInGroup = appState.bridgeData.lights.filter((light) =>
        group.lights.includes(light.id)
      );
      uiModals.openSceneModal(group, lightsInGroup);
    },
    "save-scene": async () => {
      const name = document.getElementById("scene-name").value.trim();
      const groupId = document.getElementById("scene-group-id").value;
      if (!name) {
        uiShared.showToast("Bitte einen Namen für die Szene eingeben.", true);
        return;
      }
      const actions = [];
      document.querySelectorAll(".scene-light-config").forEach((configEl) => {
        const isIncluded = configEl.querySelector(
          'input[data-light-control="include"]'
        ).checked;
        if (isIncluded) {
          const lightId = configEl.dataset.lightId;
          const brightness = parseInt(
            configEl.querySelector('input[data-light-control="brightness"]')
              .value,
            10
          );
          actions.push({
            target: { rid: lightId, rtype: "light" },
            action: { on: { on: true }, dimming: { brightness: brightness } },
          });
        }
      });
      if (actions.length === 0) {
        uiShared.showToast(
          "Bitte mindestens eine Lampe für die Szene auswählen.",
          true
        );
        return;
      }
      try {
        await api.createScene({ name, group_id: groupId, actions });
        uiShared.showToast("Szene erfolgreich erstellt!");
        uiModals.closeModal();
        await refreshRoomDetail(groupId);
      } catch (error) {
        uiShared.showToast(
          `Fehler beim Erstellen der Szene: ${error.message}`,
          true
        );
      }
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
}
