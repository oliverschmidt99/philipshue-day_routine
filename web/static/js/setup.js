import * as api from "./api.js";

export function runSetupWizard() {
  let selectedIp = "";
  let appKey = "";

  const steps = [
    document.getElementById("setup-step-1"),
    document.getElementById("setup-step-2"),
    document.getElementById("setup-step-3"),
    document.getElementById("setup-step-4"),
  ];

  const showStep = (stepIndex) => {
    steps.forEach((step, index) => {
      if (step) step.classList.toggle("hidden", index !== stepIndex - 1);
    });
  };

  const findBridges = async () => {
    const loader = document.getElementById("setup-loader-1");
    const bridgeList = document.getElementById("setup-bridge-list");
    const errorEl = document.getElementById("setup-error-1");
    if (!loader || !bridgeList || !errorEl) return;

    loader.textContent = "... Suche läuft ...";
    errorEl.textContent = "";
    try {
      const ips = await api.discoverBridges();
      bridgeList.innerHTML = "";
      if (ips.length > 0) {
        ips.forEach((ip) => {
          const btn = document.createElement("button");
          btn.type = "button";
          btn.className = "bridge-button";
          btn.textContent = ip;
          btn.onclick = () => selectBridge(ip);
          bridgeList.appendChild(btn);
        });
      } else {
        bridgeList.innerHTML = "<p>Keine Bridges automatisch gefunden.</p>";
      }
    } catch (e) {
      errorEl.textContent = `Fehler bei der Bridge-Suche: ${e.message}`;
    } finally {
      loader.textContent = "";
    }
  };

  const selectBridge = (ip) => {
    if (!ip) return;
    selectedIp = ip;
    const selectedIpSpan = document.getElementById("setup-selected-ip");
    if (selectedIpSpan) selectedIpSpan.textContent = ip;
    showStep(2);
  };

  document.getElementById("setup-manual-ip")?.addEventListener("keyup", (e) => {
    if (e.key === "Enter") {
      selectBridge(e.target.value.trim());
    }
  });

  document
    .getElementById("btn-connect-bridge")
    ?.addEventListener("click", async (e) => {
      const button = e.target;
      button.disabled = true;
      button.textContent = "Verbinde...";
      const errorEl = document.getElementById("setup-error-2");
      if (errorEl) errorEl.textContent = "";
      try {
        const data = await api.connectToBridge(selectedIp);
        appKey = data.app_key;
        showStep(3);
      } catch (e) {
        if (errorEl) errorEl.textContent = e.message;
      } finally {
        button.disabled = false;
        button.textContent = "Ich habe den Button gedrückt";
      }
    });

  document
    .getElementById("btn-save-config")
    ?.addEventListener("click", async (e) => {
      const button = e.target;
      button.disabled = true;
      button.textContent = "Speichere...";
      const errorEl = document.getElementById("setup-error-3");
      if (errorEl) errorEl.textContent = "";

      const latInput = document.getElementById("setup-latitude");
      const lonInput = document.getElementById("setup-longitude");

      try {
        const payload = {
          bridge_ip: selectedIp,
          app_key: appKey,
          latitude: latInput.value,
          longitude: lonInput.value,
        };
        await api.saveSetupConfig(payload);
        showStep(4);
        setTimeout(() => window.location.reload(), 5000);
      } catch (e) {
        if (errorEl) errorEl.textContent = e.message;
        button.disabled = false;
        button.textContent = "Einrichtung abschließen";
      }
    });

  findBridges();
  showStep(1);
}
