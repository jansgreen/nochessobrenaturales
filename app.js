const nav = document.getElementById("mainNav");
const navCollapse = document.getElementById("navMenu");
const navLinks = [...document.querySelectorAll(".navbar .nav-link")];
const sections = [...document.querySelectorAll("header[id], main section[id]")];
const eventCards = [...document.querySelectorAll(".schedule-item")];
const nextEventLabel = document.getElementById("nextEventLabel");
const nextEventDay = document.getElementById("nextEventDay");
const nextEventMonth = document.getElementById("nextEventMonth");
const nextEventYear = document.getElementById("nextEventYear");
const contactForm = document.getElementById("contactForm");
const feedback = document.getElementById("formFeedback");
const topicField = document.getElementById("topic");
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

const countdownEl = {
  d: document.getElementById("d"),
  h: document.getElementById("h"),
  m: document.getElementById("m"),
  s: document.getElementById("s")
};

let activeDate = null;

function pad(value) {
  return String(value).padStart(2, "0");
}

function updateNavState() {
  nav.classList.toggle("scrolled", window.scrollY > 18);

  const scrollPosition = window.scrollY + 180;
  let currentId = "inicio";

  sections.forEach((section) => {
    if (section.offsetTop <= scrollPosition) {
      currentId = section.id;
    }
  });

  navLinks.forEach((link) => {
    link.classList.toggle("active", link.getAttribute("href") === `#${currentId}`);
  });
}

function initReveals() {
  const reveals = document.querySelectorAll(".reveal");

  if (reduceMotion || !("IntersectionObserver" in window)) {
    reveals.forEach((element) => element.classList.add("visible"));
    return;
  }

  const observer = new IntersectionObserver(
    (entries, currentObserver) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) {
          return;
        }

        const delay = Number(entry.target.dataset.revealDelay || 0);
        window.setTimeout(() => entry.target.classList.add("visible"), delay);
        currentObserver.unobserve(entry.target);
      });
    },
    { threshold: 0.12, rootMargin: "0px 0px -40px" }
  );

  reveals.forEach((element) => observer.observe(element));
}

function setActiveEvent(card) {
  eventCards.forEach((item) => {
    const isActive = item === card;
    item.classList.toggle("active", isActive);
    item.setAttribute("aria-pressed", String(isActive));
    item.querySelector(".schedule-status").textContent = isActive ? "Seleccionada" : "Disponible";
  });

  activeDate = new Date(card.dataset.date);
  nextEventLabel.textContent = card.dataset.label;
  nextEventDay.textContent = card.dataset.day;
  nextEventMonth.textContent = card.dataset.month;
  nextEventYear.textContent = card.dataset.year;
  updateCountdown();
}

function getClosestFutureEvent() {
  const now = new Date();
  const futureCards = eventCards.filter((card) => new Date(card.dataset.date) > now);

  if (!futureCards.length) {
    return eventCards[eventCards.length - 1];
  }

  return futureCards.sort((a, b) => new Date(a.dataset.date) - new Date(b.dataset.date))[0];
}

function updateCountdown() {
  if (!activeDate) {
    return;
  }

  const diff = activeDate.getTime() - Date.now();

  if (diff <= 0) {
    Object.values(countdownEl).forEach((element) => {
      element.textContent = "00";
    });
    return;
  }

  countdownEl.d.textContent = pad(Math.floor(diff / 86400000));
  countdownEl.h.textContent = pad(Math.floor((diff / 3600000) % 24));
  countdownEl.m.textContent = pad(Math.floor((diff / 60000) % 60));
  countdownEl.s.textContent = pad(Math.floor((diff / 1000) % 60));
}

function initEvents() {
  if (!eventCards.length) {
    return;
  }

  setActiveEvent(getClosestFutureEvent());
  eventCards.forEach((card) => card.addEventListener("click", () => setActiveEvent(card)));
}

function initNavigation() {
  document.querySelectorAll('#navMenu a[href^="#"]').forEach((link) => {
    link.addEventListener("click", () => {
      if (window.bootstrap && navCollapse.classList.contains("show")) {
        bootstrap.Collapse.getOrCreateInstance(navCollapse).hide();
      }
    });
  });
}

function initSupportLinks() {
  document.querySelectorAll(".support-item[data-topic]").forEach((link) => {
    link.addEventListener("click", () => {
      const matchingOption = [...topicField.options].find(
        (option) => option.value === link.dataset.topic
      );

      if (matchingOption) {
        topicField.value = matchingOption.value;
      }
    });
  });
}

function validateField(field) {
  const isValid = field.checkValidity();
  field.classList.toggle("is-invalid", !isValid);
  return isValid;
}

function initContactForm() {
  const requiredFields = [...contactForm.querySelectorAll("[required]")];

  requiredFields.forEach((field) => {
    field.addEventListener("blur", () => validateField(field));
    field.addEventListener("input", () => {
      if (field.classList.contains("is-invalid")) {
        validateField(field);
      }
    });
  });

  contactForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const isValid = requiredFields.map(validateField).every(Boolean);

    if (!isValid) {
      feedback.textContent = "Revisa los campos señalados antes de continuar.";
      contactForm.querySelector(".is-invalid").focus();
      return;
    }

    const data = new FormData(contactForm);
    const subject = encodeURIComponent(`Noches Sobrenaturales — ${data.get("topic")}`);
    const body = encodeURIComponent(
      `Nombre: ${data.get("name")}\nCorreo: ${data.get("email")}\nTema: ${data.get("topic")}\n\nMensaje:\n${data.get("message")}`
    );

    feedback.textContent = "Listo. Abriremos tu aplicación de correo para que puedas enviar el mensaje.";
    window.location.href = `mailto:info@2819church.org?subject=${subject}&body=${body}`;
  });
}

window.addEventListener("scroll", updateNavState, { passive: true });
window.addEventListener("load", () => {
  updateNavState();
  initReveals();
  initEvents();
  initNavigation();
  initSupportLinks();
  initContactForm();
  updateCountdown();
  document.getElementById("year").textContent = new Date().getFullYear();
  window.setInterval(updateCountdown, 1000);
});
