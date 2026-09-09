/* ==========================================================================
Facundo Humphreys — portfolio behaviour
No dependencies. Four jobs: theme, reveals, the pinned method section,
and a click-to-load facade in front of YouTube.

The initial theme is applied by an inline script in <head>, not here —
a deferred script would run after first paint and flash white.
========================================================================== */

(function () {
  "use strict";

  var root = document.documentElement;
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  /* Reveal styles are gated behind .js so a visitor without JavaScript never
gets stranded looking at elements stuck at opacity 0. */
  root.classList.add("js");

  /* --- Theme ------------------------------------------------------------- */

  var toggle = document.querySelector(".theme-toggle");
  var osLight = window.matchMedia("(prefers-color-scheme: light)");

  function syncToggle() {
    if (!toggle) return;
    var isLight = root.dataset.theme === "light";
    toggle.setAttribute("aria-pressed", String(isLight));
    toggle.setAttribute("aria-label", isLight ? "Switch to dark theme" : "Switch to light theme");
  }

  function stored() {
    try {
      return localStorage.getItem("theme");
    } catch (e) {
      return null;
    }
  }

  syncToggle();

  if (toggle) {
    toggle.addEventListener("click", function () {
      var next = root.dataset.theme === "light" ? "dark" : "light";
      root.dataset.theme = next;
      try {
        localStorage.setItem("theme", next);
      } catch (e) {
        /* private mode */
      }
      syncToggle();
    });
  }

  /* Track the OS only while the visitor hasn't made an explicit choice. */
  osLight.addEventListener("change", function (e) {
    if (stored()) return;
    root.dataset.theme = e.matches ? "light" : "dark";
    syncToggle();
  });

  /* --- Sticky nav -------------------------------------------------------- */

  var nav = document.querySelector(".site-nav");

  if (nav) {
    var navTicking = false;

    var updateNav = function () {
      nav.classList.toggle("is-stuck", window.scrollY > 40);
      navTicking = false;
    };

    window.addEventListener(
      "scroll",
      function () {
        if (navTicking) return;
        navTicking = true;
        requestAnimationFrame(updateNav);
      },
      { passive: true },
    );

    updateNav();
  }

  /* --- Reveal on scroll -------------------------------------------------- */

  var revealables = document.querySelectorAll("[data-reveal]");

  function revealAll() {
    for (var i = 0; i < revealables.length; i++) {
      revealables[i].classList.add("is-visible");
    }
  }

  if (reduceMotion.matches || !("IntersectionObserver" in window)) {
    revealAll();
  } else {
    var revealObserver = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          entry.target.classList.add("is-visible");
          revealObserver.unobserve(entry.target);
        });
      },
      { threshold: 0.15, rootMargin: "0px 0px -10% 0px" },
    );

    revealables.forEach(function (el) {
      revealObserver.observe(el);
    });
  }

  /* --- Proof band count-up ----------------------------------------------- */

  function countUp(el) {
    var target = parseFloat(el.dataset.count);
    var suffix = el.dataset.suffix || "";
    var start = null;
    var duration = 900;

    function frame(now) {
      if (start === null) start = now;
      var t = Math.min((now - start) / duration, 1);
      // Ease-out cubic — fast off the line, settles on the number.
      var eased = 1 - Math.pow(1 - t, 3);
      el.textContent = Math.round(target * eased) + suffix;
      if (t < 1) requestAnimationFrame(frame);
    }

    requestAnimationFrame(frame);
  }

  var counters = document.querySelectorAll("[data-count]");

  if (!reduceMotion.matches && "IntersectionObserver" in window) {
    var countObserver = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          countUp(entry.target);
          countObserver.unobserve(entry.target);
        });
      },
      { threshold: 0.6 },
    );

    counters.forEach(function (el) {
      countObserver.observe(el);
    });
  }
  /* Otherwise the markup already carries the final value — nothing to do. */

  /* --- Pinned method section --------------------------------------------- */

  var method = document.getElementById("method");
  var steps = method ? method.querySelectorAll(".method-step") : [];

  if (method && steps.length && !reduceMotion.matches) {
    var progressTicking = false;
    var inView = false;

    var updateProgress = function () {
      var rect = method.getBoundingClientRect();
      var vh = window.innerHeight;

      /* 0 as the section's top reaches the viewport top,
1 as its bottom reaches the viewport bottom. */
      var span = rect.height - vh;
      var p = span > 0 ? -rect.top / span : 0;
      p = Math.min(Math.max(p, 0), 1);

      method.style.setProperty("--p", p.toFixed(4));

      var active = Math.min(Math.floor(p * steps.length), steps.length - 1);
      for (var i = 0; i < steps.length; i++) {
        steps[i].classList.toggle("is-active", i === active);
      }

      progressTicking = false;
    };

    var onScroll = function () {
      if (progressTicking || !inView) return;
      progressTicking = true;
      requestAnimationFrame(updateProgress);
    };

    /* Only listen to scroll while the section is actually on screen. */
    new IntersectionObserver(
      function (entries) {
        inView = entries[0].isIntersecting;
        if (inView) updateProgress();
      },
      { rootMargin: "100px 0px" },
    ).observe(method);

    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener(
      "resize",
      function () {
        if (inView) updateProgress();
      },
      { passive: true },
    );

    updateProgress();
  } else if (steps.length) {
    steps[0].classList.add("is-active");
  }

  /* --- YouTube facade ----------------------------------------------------- */
  /* The thumbnail is a button; nothing is requested from youtube.com until
someone actually asks for the video. */

  var media = document.querySelector(".talk-media");

  if (media) {
    media.addEventListener(
      "click",
      function () {
        var id = media.dataset.video;
        if (!id) return;

        var frame = document.createElement("iframe");
        frame.src = "https://www.youtube-nocookie.com/embed/" + id + "?autoplay=1&rel=0";
        frame.title = "Demystifying Blockchain DAOs: a practical roadmap";
        frame.allow = "accelerometer; autoplay; encrypted-media; picture-in-picture";
        frame.allowFullscreen = true;

        var holder = document.createElement("div");
        holder.className = "talk-media is-playing";
        holder.appendChild(frame);
        media.replaceWith(holder);
      },
      { once: true },
    );
  }
})();
