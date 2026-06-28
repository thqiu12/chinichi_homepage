/* 控えめなスクロールリビール。
   - 画面外の要素だけを対象(初期フラッシュ回避)
   - IntersectionObserver 非対応や prefers-reduced-motion では何もしない(全要素そのまま表示) */
(function () {
  if (!("IntersectionObserver" in window)) return;
  if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  function run() {
    var sel = ".section__head,.route,.svc,.mini,.proof,.stat,.grp__col,.rep__card,.rep__body,.tl-item,.flow__step,.philo,.timeline,.brands,.campus,.region-label,.city-chips";
    var els = [].slice.call(document.querySelectorAll(sel));
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add("is-in"); io.unobserve(e.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px" });
    var vh = window.innerHeight || document.documentElement.clientHeight;
    els.forEach(function (el) {
      // 画面外(下方)の要素だけアニメ。表示中の要素はそのまま(フラッシュ防止)
      if (el.getBoundingClientRect().top > vh * 0.85) {
        el.classList.add("reveal-on");
        io.observe(el);
      }
    });
  }

  if (document.readyState !== "loading") run();
  else document.addEventListener("DOMContentLoaded", run);
})();
