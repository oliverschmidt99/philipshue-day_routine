import { discoverBridges, connectToBridge, saveSetupConfig } from "./api.js";

export function runSetupWizard() {
  let selectedIp = "";
  let appKey = "";

  const step1 = document.getElementById("setup-step-1");
  const step2 = document.getElementById("setup-step-2");
  const step3 = document.getElementById("setup-step-3");
  const step4 = document.getElementById("setup-step-4");

  const discoverBtn = document.getElementById("btn-discover-bridges");
  const loader1 = document.getElementById("setup-loader-1");
  const bridgeList = document.getElementById("setup-bridge-list");
  const manualIpInput = document.getElementById("setup-manual-ip");
  const defaultIpBtn = document.getElementById("btn-default-ip");
  const connectManualBtn = document.getElementById("btn-connect-manual-ip");
  const error1 = document.getElementById("setup-error-1");

  const selectedIpSpan = document.getElementById("setup-selected-ip");
  const connectBtn = document.getElementById("btn-connect-bridge");
  const error2 = document.getElementById("setup-error-2");

  const latInput = document.getElementById("setup-latitude");
  const lonInput = document.getElementById("setup-longitude");
  const saveBtn = document.getElementById("btn-save-config");
  const error3 = document.getElementById("setup-error-3");

  const showStep = (step) => {
    [step1, step2, step3, step4].forEach((s) => (s.style.display = "none"));
    document.getElementById(`setup-step-${step}`).style.display = "block";
  };

  const findBridges = async () => {
    loader1.style.display = "block";
    error1.textContent = "";
    bridgeList.innerHTML = "";
    try {
      const ips = await discoverBridges();
      if (ips.length > 0) {
        ips.forEach((ip) => {
          const btn = document.createElement("button");
          btn.type = "button";
          btn.className =
            "w-full text-left p-3 bg-gray-100 rounded-lg hover:bg-blue-100 border-2 border-transparent focus:border-blue-500 focus:outline-none";
          btn.textContent = ip;
          btn.onclick = () => selectBridge(ip);
          bridgeList.appendChild(btn);
        });
      } else {
        bridgeList.innerHTML =
          '<p class="text-gray-500">Keine Bridges automatisch gefunden.</p>';
      }
    } catch (e) {
      error1.textContent = e.message || "Fehler bei der Bridge-Suche.";
    } finally {
      loader1.style.display = "none";
    }
  };

  const selectBridge = (ip) => {
    if (!ip) return;
    selectedIp = ip;
    selectedIpSpan.textContent = ip;
    showStep(2);
  };

  discoverBtn.addEventListener("click", findBridges);

  defaultIpBtn.addEventListener("click", () => {
    manualIpInput.value = "192.168.178.";
    manualIpInput.focus();
  });

  const connectManualIp = () => {
    const ip = manualIpInput.value.trim();
    if (ip) {
      selectBridge(ip);
    }
  };

  connectManualBtn.addEventListener("click", connectManualIp);
  manualIpInput.addEventListener("keyup", (e) => {
    if (e.key === "Enter") {
      connectManualIp();
    }
  });

  connectBtn.addEventListener("click", async () => {
    connectBtn.disabled = true;
    connectBtn.querySelector("i").classList.remove("hidden");
    error2.textContent = "";
    try {
      const data = await connectToBridge(selectedIp);
      appKey = data.app_key;
      showStep(3);
    } catch (e) {
      error2.textContent = e.message;
    } finally {
      connectBtn.disabled = false;
      connectBtn.querySelector("i").classList.add("hidden");
    }
  });

  saveBtn.addEventListener("click", async () => {
    saveBtn.disabled = true;
    saveBtn.querySelector("i").classList.remove("hidden");
    error3.textContent = "";
    try {
      const payload = {
        bridge_ip: selectedIp,
        app_key: appKey,
        latitude: latInput.value,
        longitude: lonInput.value,
      };
      await saveSetupConfig(payload);
      showStep(4);
      setTimeout(() => window.location.reload(), 5000);
    } catch (e) {
      error3.textContent = e.message;
    } finally {
      saveBtn.disabled = false;
      saveBtn.querySelector("i").classList.add("hidden");
    }
  });
}
