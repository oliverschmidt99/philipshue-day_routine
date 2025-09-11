document.addEventListener("DOMContentLoaded", () => {
  const navLinks = document.querySelectorAll("#main-nav .nav-item a");
  const contentSections = document.querySelectorAll(".content-section");

  // Funktion zum Wechseln der Tabs
  const switchTab = (targetId) => {
    navLinks.forEach((navLink) => {
      navLink.classList.toggle("active", navLink.dataset.target === targetId);
    });

    contentSections.forEach((section) => {
      section.classList.toggle("active", section.id === `content-${targetId}`);
    });
  };

  // Event-Listener für Navigations-Links
  navLinks.forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      const target = link.dataset.target;
      if (target) {
        switchTab(target);
      }
    });
  });

  // Initialen Tab anzeigen (Routinen)
  switchTab("routines");
});
