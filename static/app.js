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

  const heroEffects = document.querySelector("[data-hero-effects]");
  if (heroEffects && !reduceMotion) {
    const startSource = heroEffects.dataset.startSrc;
    const variantSources = [
      heroEffects.dataset.blueSrc,
      heroEffects.dataset.whiteSrc,
      heroEffects.dataset.goldSrc,
    ].filter(Boolean);
    const randomBetween = (minimum, maximum) =>
      Math.random() * (maximum - minimum) + minimum;
    const randomVariant = (previousIndex) => {
      if (variantSources.length < 2) return 0;

      let nextIndex;
      do {
        nextIndex = Math.floor(Math.random() * variantSources.length);
      } while (nextIndex === previousIndex);
      return nextIndex;
    };

    const startHeroEffects = () => {
      const effectCount = window.matchMedia("(max-width: 767.98px)").matches
        ? 3
        : 4;

      for (let index = 0; index < effectCount; index += 1) {
        const effect = document.createElement("img");
        let firstAppearance = true;
        let previousVariant = -1;
        effect.className = "hero-effect";
        effect.alt = "";
        effect.decoding = "async";
        effect.fetchPriority = "low";
        heroEffects.appendChild(effect);

        const playEffect = () => {
          const isMobile = window.matchMedia("(max-width: 767.98px)").matches;
          const isFirstAppearance = firstAppearance;
          const duration = randomBetween(4400, 6200);
          const size = isMobile
            ? randomBetween(430, 620)
            : randomBetween(680, 1040);

          if (firstAppearance) {
            effect.src = startSource;
            firstAppearance = false;
          } else {
            previousVariant = randomVariant(previousVariant);
            effect.src = variantSources[previousVariant];
          }

          effect.style.left = `${randomBetween(8, 92)}%`;
          effect.style.top = `${randomBetween(12, 88)}%`;
          effect.style.setProperty("--effect-size", `${size}px`);
          effect.style.setProperty("--effect-duration", `${duration}ms`);
          effect.style.setProperty(
            "--effect-rotation",
            `${randomBetween(-7, 7)}deg`
          );
          const peakOpacity = isFirstAppearance
            ? randomBetween(0.78, 0.96)
            : randomBetween(0.34, 0.55);
          effect.style.setProperty("--effect-opacity", peakOpacity.toFixed(2));
          effect.style.setProperty(
            "--effect-mid-opacity",
            (peakOpacity * 0.68).toFixed(2)
          );

          effect.classList.remove("is-active");
          void effect.offsetWidth;
          effect.classList.add("is-active");
        };

        effect.addEventListener("animationend", () => {
          effect.classList.remove("is-active");
          window.setTimeout(playEffect, randomBetween(650, 1800));
        });
        window.setTimeout(playEffect, index * 700);
      }

      const preloadVariants = () => {
        variantSources.forEach((source) => {
          const image = new Image();
          image.decoding = "async";
          image.src = source;
        });
      };
      if ("requestIdleCallback" in window) {
        window.requestIdleCallback(preloadVariants, { timeout: 2500 });
      } else {
        window.setTimeout(preloadVariants, 800);
      }
    };

    const initialEffect = new Image();
    initialEffect.src = startSource;
    if (initialEffect.complete) {
      startHeroEffects();
    } else {
      initialEffect.addEventListener("load", startHeroEffects, { once: true });
    }
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

  const galleryDialog = document.querySelector("#galleryDialog");
  const galleryDialogImage = document.querySelector("#galleryDialogImage");
  const galleryDialogTitle = document.querySelector("#galleryDialogTitle");
  const galleryDialogDescription = document.querySelector(
    "#galleryDialogDescription"
  );
  const galleryDialogDate = document.querySelector("#galleryDialogDate");
  const galleryTriggers = Array.from(
    document.querySelectorAll(".js-gallery-trigger")
  );
  const galleryCloseButton = galleryDialog?.querySelector(
    "[data-gallery-close]"
  );
  const galleryPreviousButton = galleryDialog?.querySelector(
    "[data-gallery-previous]"
  );
  const galleryNextButton = galleryDialog?.querySelector(
    "[data-gallery-next]"
  );
  let activeGalleryIndex = -1;

  const showGalleryImage = (index) => {
    if (!galleryDialogImage || !galleryTriggers.length) return;

    activeGalleryIndex =
      (index + galleryTriggers.length) % galleryTriggers.length;
    const trigger = galleryTriggers[activeGalleryIndex];
    const description = trigger.dataset.galleryDescription?.trim() || "";
    const date = trigger.dataset.galleryDate?.trim() || "";

    galleryDialogImage.src = trigger.dataset.gallerySrc;
    galleryDialogImage.alt = trigger.dataset.galleryAlt || "";
    if (galleryDialogTitle) {
      galleryDialogTitle.textContent =
        trigger.dataset.galleryTitle || "Noches Sobrenaturales";
    }
    if (galleryDialogDescription) {
      galleryDialogDescription.textContent = description;
      galleryDialogDescription.hidden = !description;
    }
    if (galleryDialogDate) {
      galleryDialogDate.textContent = date;
      galleryDialogDate.hidden = !date;
    }

    const hasMultipleImages = galleryTriggers.length > 1;
    if (galleryPreviousButton) galleryPreviousButton.hidden = !hasMultipleImages;
    if (galleryNextButton) galleryNextButton.hidden = !hasMultipleImages;
  };

  galleryTriggers.forEach((trigger, index) => {
    trigger.addEventListener("click", (event) => {
      if (!galleryDialog?.showModal || !galleryDialogImage) return;

      event.preventDefault();
      showGalleryImage(index);
      galleryDialog.showModal();
    });
  });

  galleryPreviousButton?.addEventListener("click", () => {
    showGalleryImage(activeGalleryIndex - 1);
  });
  galleryNextButton?.addEventListener("click", () => {
    showGalleryImage(activeGalleryIndex + 1);
  });
  galleryCloseButton?.addEventListener("click", () => galleryDialog.close());
  galleryDialog?.addEventListener("click", (event) => {
    if (event.target === galleryDialog) galleryDialog.close();
  });
  galleryDialog?.addEventListener("keydown", (event) => {
    if (event.key === "ArrowLeft") showGalleryImage(activeGalleryIndex - 1);
    if (event.key === "ArrowRight") showGalleryImage(activeGalleryIndex + 1);
  });
  galleryDialog?.addEventListener("close", () => {
    galleryDialogImage?.removeAttribute("src");
    galleryTriggers[activeGalleryIndex]?.focus();
    activeGalleryIndex = -1;
  });

  const aboutCounters = document.querySelectorAll("[data-about-count]");
  if (aboutCounters.length && !reduceMotion && "IntersectionObserver" in window) {
    const counterObserver = new IntersectionObserver(
      (entries, observer) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;

          const counter = entry.target;
          const target = Number(counter.dataset.aboutCount || 0);
          const duration = 1100;
          const startedAt = performance.now();
          const updateCounter = (timestamp) => {
            const progress = Math.min((timestamp - startedAt) / duration, 1);
            const easedProgress = 1 - Math.pow(1 - progress, 3);
            counter.textContent = String(Math.round(target * easedProgress));
            if (progress < 1) window.requestAnimationFrame(updateCounter);
          };

          counter.textContent = "0";
          window.requestAnimationFrame(updateCounter);
          observer.unobserve(counter);
        });
      },
      { threshold: 0.55 }
    );

    aboutCounters.forEach((counter) => counterObserver.observe(counter));
  }

  const languageSwitcher = document.querySelector(".language-switcher");
  if (languageSwitcher) {
    document.addEventListener("click", (event) => {
      if (!languageSwitcher.contains(event.target)) {
        languageSwitcher.removeAttribute("open");
      }
    });
    languageSwitcher.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        languageSwitcher.removeAttribute("open");
        languageSwitcher.querySelector("summary")?.focus();
      }
    });
  }

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
