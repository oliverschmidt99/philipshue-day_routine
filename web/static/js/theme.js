(function () {
  function e(e) {
    document.documentElement.setAttribute("data-theme", e);
  }
  const t = localStorage.getItem("theme") || "light";
  e(t),
    document.addEventListener("DOMContentLoaded", () => {
      const o = document.getElementById("theme-toggle");
      o &&
        ((o.checked = "dark" === t),
        o.addEventListener("change", () => {
          const t = o.checked ? "dark" : "light";
          localStorage.setItem("theme", t), e(t);
        }));
    });
})();
