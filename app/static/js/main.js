// 글로벌라오 공통 스크립트
(function () {
  // 모바일 햄버거 메뉴
  var hb = document.querySelector('.hamburger');
  if (hb) hb.addEventListener('click', function () {
    var m = document.querySelector('.m-nav');
    if (m) m.classList.toggle('open');
  });

  // 스크롤 리빌
  var io = new IntersectionObserver(function (es) {
    es.forEach(function (e) {
      if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
    });
  }, { threshold: 0.1 });
  document.querySelectorAll('.rv').forEach(function (el) { io.observe(el); });

  // 숫자 카운트업 (.count[data-to])
  var co = new IntersectionObserver(function (es) {
    es.forEach(function (e) {
      if (!e.isIntersecting) return;
      var el = e.target, to = +el.dataset.to, dur = 1400, t0 = performance.now();
      var tick = function (t) {
        var p = Math.min((t - t0) / dur, 1), v = Math.floor(to * (1 - Math.pow(1 - p, 3)));
        el.textContent = v.toLocaleString();
        if (p < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
      co.unobserve(el);
    });
  }, { threshold: 0.5 });
  document.querySelectorAll('.count').forEach(function (el) { co.observe(el); });

  // 라이트박스 ([data-lightbox] 이미지 클릭 시 확대)
  var boxTargets = document.querySelectorAll('[data-lightbox]');
  if (boxTargets.length) {
    var lb = document.createElement('div');
    lb.className = 'lightbox';
    lb.innerHTML = '<img alt="확대 이미지">';
    document.body.appendChild(lb);
    var lbImg = lb.querySelector('img');
    boxTargets.forEach(function (el) {
      el.addEventListener('click', function () {
        lbImg.src = el.dataset.lightbox || el.src;
        lb.classList.add('open');
      });
    });
    lb.addEventListener('click', function () { lb.classList.remove('open'); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') lb.classList.remove('open');
    });
  }
})();
