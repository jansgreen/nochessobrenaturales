(() => {
  "use strict";

  const nav = document.querySelector("#mainNav");
  const updateNav = () => nav?.classList.toggle("scrolled", window.scrollY > 20);
  updateNav();
  window.addEventListener("scroll", updateNav, { passive: true });

  const revealElements = document.querySelectorAll(".reveal");
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (reduceMotion || !("IntersectionObserver" in window)) {
    revealElements.forEach((element) => element.classList.add("visible"));
  } else {
    const revealObserver = new IntersectionObserver(
      (entries, observer) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;

          const delay = Number(entry.target.dataset.revealDelay || 0);
          window.setTimeout(() => entry.target.classList.add("visible"), delay);
          observer.unobserve(entry.target);
        });
      },
      { threshold: 0.12 }
    );

    revealElements.forEach((element) => revealObserver.observe(element));
  }

  const eventDay = document.querySelector("#nextEventDay");
  const eventMonth = document.querySelector("#nextEventMonth");
  const eventYear = document.querySelector("#nextEventYear");
  const eventLabel = document.querySelector("#nextEventLabel");
  const eventEyebrow = document.querySelector("#nextEventEyebrow");
  const eventTime = document.querySelector("#nextEventTime");
  const eventAdmission = document.querySelector("#nextEventAdmission");
  const eventCta = document.querySelector("#nextEventCta");
  const eventCtaText = document.querySelector("#nextEventCtaText");
  const countdownParts = {
    days: document.querySelector("#d"),
    hours: document.querySelector("#h"),
    minutes: document.querySelector("#m"),
    seconds: document.querySelector("#s"),
  };
  let selectedDate = null;

  const padNumber = (number) => String(number).padStart(2, "0");

  const updateCountdown = () => {
    if (!selectedDate) return;

    const remaining = Math.max(0, selectedDate.getTime() - Date.now());
    const totalSeconds = Math.floor(remaining / 1000);
    const days = Math.floor(totalSeconds / 86400);
    const hours = Math.floor((totalSeconds % 86400) / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;

    if (countdownParts.days) countdownParts.days.textContent = padNumber(days);
    if (countdownParts.hours) countdownParts.hours.textContent = padNumber(hours);
    if (countdownParts.minutes) countdownParts.minutes.textContent = padNumber(minutes);
    if (countdownParts.seconds) countdownParts.seconds.textContent = padNumber(seconds);
  };

  const selectEvent = (button, initialSelection = false) => {
    document.querySelectorAll(".schedule-item").forEach((item) => {
      const active = item === button;
      item.classList.toggle("active", active);
      item.setAttribute("aria-pressed", String(active));
      const status = item.querySelector(".schedule-status");
      if (status) {
        if (active) {
          status.textContent =
            initialSelection && item.dataset.next === "true"
              ? "Próxima"
              : "Seleccionada";
        } else {
          status.textContent =
            item.dataset.next === "true" ? "Próxima" : "Disponible";
        }
      }
    });

    selectedDate = new Date(button.dataset.date);
    if (eventDay) eventDay.textContent = button.dataset.day;
    if (eventMonth) eventMonth.textContent = button.dataset.month;
    if (eventYear) eventYear.textContent = button.dataset.year;
    if (eventLabel) eventLabel.textContent = button.dataset.label;
    if (eventEyebrow) eventEyebrow.textContent = button.dataset.eyebrow;
    if (eventTime) eventTime.textContent = button.dataset.time;
    if (eventAdmission) eventAdmission.textContent = button.dataset.admission;
    if (eventCta) eventCta.href = button.dataset.ctaUrl;
    if (eventCtaText) eventCtaText.textContent = button.dataset.ctaText;
    updateCountdown();
  };

  const scheduleItems = document.querySelectorAll(".schedule-item");
  scheduleItems.forEach((button) => {
    button.addEventListener("click", () => selectEvent(button));
  });

  const initialEvent =
    document.querySelector(".schedule-item.active") || scheduleItems.item(0);
  if (initialEvent) {
    selectEvent(initialEvent, true);
    window.setInterval(updateCountdown, 1000);
  }

  const topicSelect = document.querySelector("#topic");
  document.querySelectorAll("[data-topic]").forEach((link) => {
    link.addEventListener("click", () => {
      if (topicSelect) topicSelect.value = link.dataset.topic;
    });
  });

  const contactForm = document.querySelector("#contactForm");
  const feedback = document.querySelector("#formFeedback");

  contactForm?.addEventListener("submit", (event) => {
    const name = contactForm.querySelector("#name");
    const email = contactForm.querySelector("#email");
    const message = contactForm.querySelector("#message");
    const requiredFields = [name, email, message];

    requiredFields.forEach((field) => {
      const isValid = field.value.trim() && field.checkValidity();
      field.classList.toggle("is-invalid", !isValid);
    });

    const firstInvalid = requiredFields.find(
      (field) => !field.value.trim() || !field.checkValidity()
    );
    if (firstInvalid) {
      event.preventDefault();
      firstInvalid.focus();
      if (feedback) feedback.textContent = "Revisa los campos indicados.";
      return;
    }

    if (feedback) {
      feedback.textContent = "Enviando tu mensaje…";
    }
    const submitButton = contactForm.querySelector('button[type="submit"]');
    if (submitButton) submitButton.disabled = true;
  });

  contactForm?.querySelectorAll("input, textarea").forEach((field) => {
    field.addEventListener("input", () => {
      field.classList.remove("is-invalid");
      field.parentElement
        ?.querySelectorAll(".server-error")
        .forEach((error) => error.setAttribute("hidden", ""));
    });
  });

  const videoDialog = document.querySelector("#videoDialog");
  const videoFrame = document.querySelector("#videoDialogFrame");
  const videoDialogTitle = document.querySelector("#videoDialogTitle");
  const videoCloseButton = videoDialog?.querySelector("[data-video-close]");
  let activeVideoTrigger = null;

  const stopVideo = () => {
    if (videoFrame) videoFrame.removeAttribute("src");
  };

  document.querySelectorAll(".js-video-trigger").forEach((trigger) => {
    trigger.addEventListener("click", (event) => {
      if (!videoDialog?.showModal || !videoFrame) return;

      event.preventDefault();
      activeVideoTrigger = trigger;
      const videoId = trigger.dataset.youtubeVideo;
      const videoTitle = trigger.dataset.videoTitle || "Video del encuentro";
      videoFrame.src =
        `https://www.youtube-nocookie.com/embed/${encodeURIComponent(videoId)}` +
        "?autoplay=1&rel=0";
      videoFrame.title = videoTitle;
      if (videoDialogTitle) videoDialogTitle.textContent = videoTitle;
      videoDialog.showModal();
    });
  });

  videoCloseButton?.addEventListener("click", () => videoDialog.close());
  videoDialog?.addEventListener("click", (event) => {
    if (event.target === videoDialog) videoDialog.close();
  });
  videoDialog?.addEventListener("close", () => {
    stopVideo();
    activeVideoTrigger?.focus();
    activeVideoTrigger = null;
  });

  const currentYear = document.querySelector("#year");
  if (currentYear) currentYear.textContent = new Date().getFullYear();

  const navMenu = document.querySelector("#navMenu");
  navMenu?.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      if (window.bootstrap && navMenu.classList.contains("show")) {
        window.bootstrap.Collapse.getOrCreateInstance(navMenu).hide();
      }
    });
  });
})();
