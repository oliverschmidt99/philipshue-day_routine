export const icons = {
  morning: "🌅",
  day: "☀️",
  evening: "🌇",
  night: "🌙",
  sun: "🌞",
  sensor: "💡",
};
export const sectionColors = {
  morning: "bg-yellow-100 border-yellow-200",
  day: "bg-sky-100 border-sky-200",
  evening: "bg-orange-100 border-orange-200",
  night: "bg-indigo-100 border-indigo-200",
};
export const periodNames = {
  morning: "Morgen",
  day: "Tag",
  evening: "Abend",
  night: "Nacht",
};

export function showToast(message, isError = false) {
  const toastElement = document.getElementById("toast");
  if (!toastElement) return;
  toastElement.textContent = message;
  toastElement.className = `fixed bottom-5 right-5 text-white py-2 px-4 rounded-lg shadow-xl transition-all duration-300 transform-gpu ${
    isError ? "bg-red-600" : "bg-gray-900"
  } translate-y-20 opacity-0`;
  toastElement.classList.remove("hidden");
  void toastElement.offsetWidth;
  toastElement.classList.remove("translate-y-20", "opacity-0");
  setTimeout(() => {
    toastElement.classList.add("translate-y-20", "opacity-0");
    setTimeout(() => toastElement.classList.add("hidden"), 300);
  }, 4000);
}

export function updateClock() {
  const clockElement = document.getElementById("clock");
  if (clockElement)
    clockElement.textContent = new Date().toLocaleTimeString("de-DE");
}

export function toggleDetails(headerElement, forceOpen = false) {
  const details = headerElement.nextElementSibling;
  const icon = headerElement.querySelector("i.fa-chevron-down");
  if (!details || !icon) return;

  if (details.classList.contains("hidden") || forceOpen) {
    details.classList.remove("hidden");
    setTimeout(() => {
      details.style.maxHeight = details.scrollHeight + "px";
      icon.style.transform = "rotate(180deg)";
    }, 10);
  } else {
    details.style.maxHeight = "0px";
    icon.style.transform = "rotate(0deg)";
    details.addEventListener(
      "transitionend",
      () => {
        details.classList.add("hidden");
      },
      { once: true }
    );
  }
}
