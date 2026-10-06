/* Ядро сайтов Анатолия Шабаршова (версии 1, 2, 7): меню, окна, оплата, ролики, карта, видео, появление.
   Каждый кусок проверяет, есть ли его элементы на странице, — ошибок на страницах без них нет. */
(function () {
  'use strict';
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return [].slice.call((r || document).querySelectorAll(s)); };
  var calm = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fine = matchMedia('(pointer: fine)').matches;
  document.documentElement.classList.remove('no-js');

  // меню разделов
  var mb = $('#menu'), pg = $('#pages');
  if (mb && pg) {
    var setMenu = function (o) { pg.classList.toggle('open', o); mb.setAttribute('aria-expanded', o ? 'true' : 'false'); };
    mb.addEventListener('click', function (e) { e.stopPropagation(); setMenu(!pg.classList.contains('open')); });
    document.addEventListener('click', function (e) { if (!pg.contains(e.target)) setMenu(false); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') setMenu(false); });
  }

  // окна: запись, оплата, ролик. Закрываются по фону, крестику и Esc; фокус возвращается назад
  var opened = null, back = null;
  function openBox(el) {
    back = document.activeElement; el.hidden = false; opened = el;
    requestAnimationFrame(function () { el.classList.add('show'); });
    document.documentElement.style.overflow = 'hidden';
    var f = $('[data-close]', el); if (f) f.focus();
  }
  function closeBox() {
    if (!opened) return; var el = opened; opened = null;
    el.classList.remove('show'); document.documentElement.style.overflow = '';
    var v = $('video', el); if (v) { v.pause(); v.removeAttribute('src'); v.load(); }
    setTimeout(function () { el.hidden = true; }, 250);
    if (back && back.focus) back.focus();
  }
  $$('.modal,.lb').forEach(function (m) {
    m.addEventListener('click', function (e) { if (e.target === m || e.target.closest('[data-close]')) closeBox(); });
  });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeBox(); });
  var contact = $('#contact');
  $$('[data-contact]').forEach(function (b) { b.addEventListener('click', function () { if (contact) openBox(contact); }); });

  // оплата: без галочки «Согласен с офертой» ссылки на счёт нет
  var pay = $('#pay');
  if (pay) {
    var ok = $('#pay-ok'), go = $('#pay-go');
    var sync = function () { go.setAttribute('aria-disabled', ok.checked ? 'false' : 'true'); };
    ok.addEventListener('change', sync);
    go.addEventListener('click', function (e) { if (!ok.checked) e.preventDefault(); else setTimeout(closeBox, 300); });
    $$('[data-pay]').forEach(function (b) {
      b.addEventListener('click', function () {
        $('#pay-title').textContent = b.dataset.title;
        $('#pay-price').textContent = b.dataset.price;
        go.href = b.dataset.pay; ok.checked = false; sync(); openBox(pay);
      });
    });
  }

  // ролики: по нажатию — на весь экран со звуком
  var lb = $('#lb'), lbv = $('#lbv');
  if (lb && lbv) {
    $$('[data-video]').forEach(function (r) {
      r.addEventListener('click', function () {
        lbv.src = r.dataset.video; openBox(lb);
        var p = lbv.play(); if (p && p.catch) p.catch(function () {});
      });
    });
  }

  // видео, которые играют сами: файл грузится, только когда видео на экране; размер — по ширине экрана
  var pick = function (v) {
    var w = innerWidth, s = v.dataset.src;
    if (w <= 767 && v.dataset.srcM) s = v.dataset.srcM; else if (w <= 1440 && v.dataset.srcL) s = v.dataset.srcL;
    return s;
  };
  var onScreen = [];
  var play = function (v) { if (calm || document.hidden) return; var p = v.play(); if (p && p.catch) p.catch(function () {}); };
  if ('IntersectionObserver' in window) {
    var vio = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        var v = e.target, i = onScreen.indexOf(v);
        if (e.isIntersecting) {
          if (!v.getAttribute('src')) { v.src = pick(v); }
          if (i < 0) onScreen.push(v);
          play(v);
        } else { if (i >= 0) onScreen.splice(i, 1); if (!v.paused) v.pause(); }
      });
    }, { rootMargin: '200px 0px', threshold: 0.01 });
    $$('video[data-src]').forEach(function (v) { vio.observe(v); });
    // открыли во вкладке на фоне — запускаем, когда на неё перешли
    document.addEventListener('visibilitychange', function () { if (!document.hidden) onScreen.forEach(play); });
  }

  // отзывы лентой: стрелки
  $$('[data-rev]').forEach(function (b) {
    b.addEventListener('click', function () {
      var r = document.getElementById(b.getAttribute('aria-controls')); if (!r || !r.firstElementChild) return;
      r.scrollBy({ left: (b.dataset.rev === 'next' ? 1 : -1) * (r.firstElementChild.offsetWidth + 24), behavior: calm ? 'auto' : 'smooth' });
    });
  });

  // карта сертификата: переворот по нажатию; наклон и блик — только мышью
  $$('.cardx').forEach(function (c) {
    var flip = function () { c.classList.toggle('flip'); c.setAttribute('aria-pressed', c.classList.contains('flip') ? 'true' : 'false'); };
    c.addEventListener('click', flip);
    c.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); flip(); } });
    if (!fine || calm) return;
    var raf = 0, ev = null;
    c.addEventListener('pointermove', function (e) {
      ev = e; if (raf) return;
      raf = requestAnimationFrame(function () {
        raf = 0; var r = c.getBoundingClientRect(), x = (ev.clientX - r.left) / r.width, y = (ev.clientY - r.top) / r.height;
        c.classList.add('moving');
        c.style.setProperty('--ry', ((x - .5) * 16).toFixed(2) + 'deg');
        c.style.setProperty('--rx', ((.5 - y) * 12).toFixed(2) + 'deg');
        c.style.setProperty('--gx', (x * 100).toFixed(1) + '%');
        c.style.setProperty('--gy', (y * 100).toFixed(1) + '%');
      });
    });
    c.addEventListener('pointerleave', function () {
      c.classList.remove('moving');
      ['--rx', '--ry', '--gx', '--gy'].forEach(function (k) { c.style.removeProperty(k); });
    });
  });

  // нижняя кнопка на телефоне: видна после первого экрана, прячется у блока записи и подвала
  var dock = $('#dock');
  if (dock && 'IntersectionObserver' in window) {
    var seen = {}, first = $('main > section'), ends = $$('#zapis, footer');
    var dio = new IntersectionObserver(function (es) {
      es.forEach(function (e) { seen[e.target === first ? 'top' : 'end' + ends.indexOf(e.target)] = e.isIntersecting; });
      dock.classList.toggle('on', !seen.top && !seen.end0 && !seen.end1);
    });
    if (first) dio.observe(first);
    ends.forEach(function (el) { dio.observe(el); });
  }

  // мягкое появление блоков
  var rs = $$('.rise');
  if (rs.length && 'IntersectionObserver' in window && !calm) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('up'); io.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -6% 0px' });
    rs.forEach(function (el) { io.observe(el); });
  } else rs.forEach(function (el) { el.classList.add('up'); });
})();
