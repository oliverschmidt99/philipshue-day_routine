// web/static/js/modules/help.js
import * as api from "./api.js";

function initFaqToggle() {
  const helpContainer = document.getElementById("help-content-container");
  if (!helpContainer) return;

  helpContainer.addEventListener("click", function (event) {
    const questionButton = event.target.closest(".faq-question");
    if (!questionButton) return;

    const faqItem = questionButton.parentElement;
    const answer = faqItem.querySelector(".faq-answer");

    faqItem.classList.toggle("active");

    if (faqItem.classList.contains("active")) {
      answer.style.maxHeight = answer.scrollHeight + "px";
    } else {
      answer.style.maxHeight = "0px";
    }
  });
}

export async function initHelpPage() {
  try {
    const data = await api.loadHelpContent();
    const helpContainer = document.getElementById("help-content-container");
    if (helpContainer) {
      helpContainer.innerHTML = data.content;
      initFaqToggle(); // Initialisiert die FAQ-Logik, nachdem der Inhalt geladen wurde
    }
  } catch (error) {
    console.error("Fehler beim Laden der Hilfe:", error);
    const helpContainer = document.getElementById("help-content-container");
    if (helpContainer) {
      helpContainer.innerHTML =
        "<p>Hilfe-Inhalt konnte nicht geladen werden.</p>";
    }
  }
}
