(function () {
  "use strict";
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };

  /* ---- reveal on scroll (with light stagger inside grids) ---- */
  var reveals = $$(".reveal");
  reveals.forEach(function (el) {
    var parent = el.parentElement;
    if (parent && /stat-grid|quote-grid|code-row|contact-grid|inline-stats/.test(parent.className)) {
      var sibs = $$(".reveal", parent);
      el.style.setProperty("--d", (sibs.indexOf(el) * 0.09) + "s");
    }
  });
  if ("IntersectionObserver" in window && !reduce) {
    var revObs = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add("in"); revObs.unobserve(e.target); }
      });
    }, { threshold: 0.18, rootMargin: "0px 0px -8% 0px" });
    reveals.forEach(function (el) { revObs.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add("in"); });
  }

  /* ---- draw SVG motifs when they enter ---- */
  $$(".motif, .mini-motif").forEach(function (m) {
    if (reduce || !("IntersectionObserver" in window)) { m.classList.add("drawn"); return; }
    var o = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("drawn"); o.unobserve(e.target); } });
    }, { threshold: 0.3 });
    o.observe(m);
  });

  /* ---- active dot via viewport-centre detection ---- */
  var sections = $$("main .panel");
  var dots = $$(".dots a");
  var byId = {};
  dots.forEach(function (d) { byId[d.getAttribute("href").slice(1)] = d; });
  if ("IntersectionObserver" in window) {
    var navObs = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          dots.forEach(function (d) { d.classList.remove("active"); });
          var d = byId[e.target.id];
          if (d) d.classList.add("active");
        }
      });
    }, { rootMargin: "-50% 0px -50% 0px", threshold: 0 });
    sections.forEach(function (s) { navObs.observe(s); });
  }

  /* ---- count-up figures ---- */
  function animateCount(el) {
    var target = parseFloat(el.getAttribute("data-count"));
    var decimals = parseInt(el.getAttribute("data-decimals") || "0", 10);
    var suffix = el.getAttribute("data-suffix") || "";
    if (reduce || isNaN(target)) { el.textContent = format(target, decimals) + suffix; return; }
    var dur = 1300, start = null;
    function fmt(v) { return format(v, decimals) + suffix; }
    function step(ts) {
      if (start === null) start = ts;
      var p = Math.min((ts - start) / dur, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = fmt(target * eased);
      if (p < 1) requestAnimationFrame(step); else el.textContent = fmt(target);
    }
    requestAnimationFrame(step);
  }
  function format(v, decimals) {
    if (decimals > 0) return v.toFixed(decimals);
    return Math.round(v).toLocaleString("en-US");
  }
  var counters = $$("[data-count]");
  if ("IntersectionObserver" in window) {
    var cObs = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { animateCount(e.target); cObs.unobserve(e.target); } });
    }, { threshold: 0.6 });
    counters.forEach(function (el) { cObs.observe(el); });
  } else {
    counters.forEach(function (el) { animateCount(el); });
  }

  /* ---- scroll-driven: progress bar, hero parallax, cue fade ---- */
  var bar = $("#progressBar");
  var motif = $(".motif svg");
  var heroMeta = $$(".hero-meta");
  var cue = $(".scrollcue");
  var ticking = false;
  function onScroll() {
    var y = window.scrollY || window.pageYOffset;
    var h = document.documentElement.scrollHeight - window.innerHeight;
    if (bar) bar.style.width = (h > 0 ? (y / h) * 100 : 0) + "%";
    if (!reduce) {
      if (motif && y < window.innerHeight) motif.style.transform = "translateY(" + (y * 0.12) + "px)";
      var fade = Math.max(0, 1 - y / (window.innerHeight * 0.5));
      heroMeta.forEach(function (m) { m.style.opacity = fade; });
      if (cue) cue.style.opacity = fade;
    }
    ticking = false;
  }
  window.addEventListener("scroll", function () {
    if (!ticking) { requestAnimationFrame(onScroll); ticking = true; }
  }, { passive: true });
  onScroll();
})();
