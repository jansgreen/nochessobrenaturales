(() => {
  "use strict";

  const shell = document.querySelector("[data-dashboard-shell]");
  const sidebar = document.querySelector("[data-dashboard-sidebar]");
  const toggle = document.querySelector("[data-dashboard-menu-toggle]");
  const closeButton = document.querySelector("[data-dashboard-menu-close]");
  const overlay = document.querySelector("[data-dashboard-overlay]");

  if (shell && sidebar && toggle) {
    const setSidebar = (open) => {
      sidebar.classList.toggle("is-open", open);
      shell.classList.toggle("sidebar-is-open", open);
      document.body.classList.toggle("dashboard-menu-open", open);
      toggle.setAttribute("aria-expanded", String(open));
    };

    toggle.addEventListener("click", () => {
      setSidebar(!sidebar.classList.contains("is-open"));
    });
    closeButton?.addEventListener("click", () => setSidebar(false));
    overlay?.addEventListener("click", () => setSidebar(false));
    sidebar.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => setSidebar(false));
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") setSidebar(false);
    });
  }

  const search = document.querySelector("[data-dashboard-search]");
  const input = search?.querySelector("[data-dashboard-search-input]");
  const results = search?.querySelector("[data-dashboard-search-results]");
  const tools = Array.from(document.querySelectorAll("[data-dashboard-search-item]"));

  if (search && input && results && tools.length) {
    const normalize = (value) => value
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase();

    const renderResults = () => {
      const query = normalize(input.value.trim());
      results.replaceChildren();

      if (!query) {
        results.hidden = true;
        return;
      }

      const matches = tools
        .filter((tool) => normalize(`${tool.dataset.searchLabel || ""} ${tool.textContent}`).includes(query))
        .slice(0, 6);

      if (!matches.length) {
        const empty = document.createElement("p");
        empty.textContent = "No se encontraron herramientas";
        results.append(empty);
      } else {
        matches.forEach((tool) => {
          const link = document.createElement("a");
          link.href = tool.href;
          link.textContent = tool.querySelector("span")?.textContent?.trim() || tool.textContent.trim();
          results.append(link);
        });
      }
      results.hidden = false;
    };

    input.addEventListener("input", renderResults);
    input.addEventListener("keydown", (event) => {
      if (event.key === "Enter") {
        const first = results.querySelector("a");
        if (first) {
          event.preventDefault();
          window.location.assign(first.href);
        }
      }
    });
    document.addEventListener("click", (event) => {
      if (!search.contains(event.target)) results.hidden = true;
    });
  }
})();
