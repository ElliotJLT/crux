(function () {
  "use strict";
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var IO = "IntersectionObserver" in window;

  /* reveal on scroll */
  var reveals = $$(".reveal");
  if (IO && !reduce) {
    var ro = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("in"); ro.unobserve(e.target); } });
    }, { threshold: 0.16, rootMargin: "0px 0px -6% 0px" });
    reveals.forEach(function (el) { ro.observe(el); });
  } else { reveals.forEach(function (el) { el.classList.add("in"); }); }

  /* draw trajectory when in view */
  $$(".vis-card").forEach(function (v) {
    if (reduce || !IO) { v.classList.add("drawn"); return; }
    var o = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("drawn"); o.unobserve(e.target); } });
    }, { threshold: 0.4 });
    o.observe(v);
  });

  /* nav background on scroll */
  var nav = $("#nav");
  function onScroll() { if (nav) nav.classList.toggle("scrolled", (window.scrollY || 0) > 8); }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* count-up */
  function fmt(v, dec) { return dec > 0 ? v.toFixed(dec) : Math.round(v).toLocaleString("en-US"); }
  function run(el) {
    var raw = parseFloat(el.getAttribute("data-count"));
    var div = parseFloat(el.getAttribute("data-divide")) || 1;
    var dec = parseInt(el.getAttribute("data-decimals") || "0", 10);
    var suf = el.getAttribute("data-suffix") || "";
    var final = raw / div;
    if (reduce || isNaN(final)) { el.textContent = fmt(final, dec) + suf; return; }
    var dur = 1200, t0 = null;
    function step(ts) {
      if (t0 === null) t0 = ts;
      var p = Math.min((ts - t0) / dur, 1);
      el.textContent = fmt(final * (1 - Math.pow(1 - p, 3)), dec) + suf;
      if (p < 1) requestAnimationFrame(step); else el.textContent = fmt(final, dec) + suf;
    }
    requestAnimationFrame(step);
  }
  var counters = $$("[data-count]");
  if (IO) {
    var co = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { run(e.target); co.unobserve(e.target); } });
    }, { threshold: 0.7 });
    counters.forEach(function (el) { co.observe(el); });
  } else { counters.forEach(run); }
})();
