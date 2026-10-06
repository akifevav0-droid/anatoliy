/* Автопроверка сайтов (запускать в браузере на странице того же сайта):
   const r = await window.CHECK(['v7/','v7/gruppy/'], [320,390,1440]);
   Для каждой страницы и ширины: сдвиг вбок, битые/растянутые/тяжёлые картинки, обрезанные кнопки,
   число размеров шрифта (без карты сертификата и логотипов), ошибки скриптов.
   Заодно собирает замеры мест под картинки (для sizes): r.measures. */
window.CHECK = async function (pages, widths, opts) {
  opts = opts || {};
  const out = { rows: [], measures: {}, errors: [] };
  const wait = (ms) => new Promise((r) => setTimeout(r, ms));
  for (const url of pages) for (const W of widths) {
    const f = document.createElement('iframe');
    f.style.cssText = `position:fixed;left:0;top:0;width:${W}px;height:${opts.h || 860}px;border:0;z-index:99999;background:#fff`;
    document.body.appendChild(f);
    const errs = [];
    await new Promise((res) => {
      f.onload = res; f.src = url + (url.includes('?') ? '&' : '?') + 'chk=' + Date.now();
      const t = setInterval(() => { try { const w = f.contentWindow; if (w && !w.__hooked) { w.__hooked = 1; w.addEventListener('error', (e) => errs.push((e.message || 'ресурс не загрузился') + ' ' + (e.filename || (e.target && (e.target.src || e.target.href)) || '')), true); w.addEventListener('unhandledrejection', (e) => errs.push('promise: ' + e.reason)); } } catch (e) {} }, 5);
      setTimeout(() => clearInterval(t), 4000);
    });
    const w = f.contentWindow, d = f.contentDocument;
    await wait(300);
    const H = d.documentElement.scrollHeight;
    for (let y = 0; y < H; y += 500) { w.scrollTo(0, y); await wait(40); }
    w.scrollTo(0, 0); await wait(opts.settle || 900);
    const row = { url, W, ov: 0, broken: [], stretched: [], heavy: [], blurry: [], clipped: [], fonts: [], errs, kb: 0 };
    if (d.documentElement.scrollWidth > w.innerWidth + 1) row.ov = d.documentElement.scrollWidth - w.innerWidth;
    // элементы, выходящие за край экрана (кроме лент с прокруткой)
    row.outside = [];
    d.querySelectorAll('main *').forEach((el) => {
      const r = el.getBoundingClientRect(); if (!r.width) return;
      if (r.right > w.innerWidth + 1 || r.left < -1) {
        let p = el.parentElement, ok = false;
        while (p && p !== d.body) { const cs = w.getComputedStyle(p); if (/(auto|scroll|hidden|clip)/.test(cs.overflowX)) { ok = true; break; } p = p.parentElement; }
        if (!ok) row.outside.push(((typeof el.className === 'string' && el.className) || el.tagName) + ' ' + Math.round(r.left) + '…' + Math.round(r.right));
      }
    });
    row.outside = row.outside.slice(0, 5);
    const dpr = Math.max(1, w.devicePixelRatio || 1);
    d.querySelectorAll('img').forEach((im) => {
      const r = im.getBoundingClientRect();
      const k = im.dataset.k, aw = +im.getAttribute('width'), ah = +im.getAttribute('height');
      if (k && r.width >= 2) {
        const fit = w.getComputedStyle(im).objectFit, ar = aw && ah ? aw / ah : r.width / r.height;
        out.measures[k] = out.measures[k] || {};
        out.measures[k][W] = Math.round(fit === 'cover' ? Math.max(r.width, r.height * ar) : r.width);
      }
      if (im.complete && im.naturalWidth === 0 && im.currentSrc) { row.broken.push(im.currentSrc.split('/').pop()); return; }
      if (r.width < 2 || !im.naturalWidth || im.closest('.logo,.wm,[data-art]')) return;
      const cs = w.getComputedStyle(im), nar = im.naturalWidth / im.naturalHeight, rar = im.offsetWidth / im.offsetHeight; // без учёта поворота
      const name = im.currentSrc.split('/').pop().split('?')[0];
      if ((cs.objectFit === 'fill' || !cs.objectFit) && Math.abs(nar / rar - 1) > 0.03) row.stretched.push(name);
      const need = cs.objectFit === 'cover' ? Math.max(r.width, r.height * nar) : r.width;
      // настоящая ширина файла: из имени нарезки (…-960.webp), иначе — naturalWidth
      const fm = /-(\d+)\.(?:webp|jpg|png)/.exec(name), fw = fm ? +fm[1] : im.naturalWidth;
      if (fw > need * dpr * 2.5 && fw > 500) row.heavy.push(name + ' ' + fw + '→' + Math.round(need));
      if (fw < need * 0.98) row.blurry.push(name + ' ' + fw + '→' + Math.round(need));
    });
    d.querySelectorAll('.btn,button,a').forEach((b) => {
      if (!b.offsetWidth) return;
      if (b.scrollWidth > b.clientWidth + 1 && w.getComputedStyle(b).overflow !== 'visible') row.clipped.push(b.textContent.trim().slice(0, 30));
      const r = b.getBoundingClientRect();
      if (r.right > w.innerWidth + 1 && !b.closest('.reels,.revs.scroll,.modal,.lb,.dock')) row.clipped.push('за краем: ' + b.textContent.trim().slice(0, 30));
    });
    const fs = new Set();
    d.querySelectorAll('body *').forEach((el) => {
      if (el.closest('.cardx,.logo,.wm,svg,[hidden],.modal,.lb,.skip,.vh')) return;
      if (![...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim())) return;
      if (!el.offsetWidth && !el.getClientRects().length) return;
      fs.add(parseFloat(w.getComputedStyle(el).fontSize));
    });
    row.fonts = [...fs].sort((a, b) => a - b);
    for (const e of w.performance.getEntriesByType('resource')) row.kb += (e.encodedBodySize || 0);
    row.kb = Math.round(row.kb / 1024);
    out.rows.push(row);
    f.remove();
  }
  out.summary = out.rows.map((r) => {
    const bad = [];
    if (r.ov) bad.push('сдвиг ' + r.ov + 'px');
    if (r.outside.length) bad.push('за краем: ' + r.outside.join('; '));
    if (r.broken.length) bad.push('битые: ' + r.broken.join(', '));
    if (r.stretched.length) bad.push('растянуты: ' + r.stretched.join(', '));
    if (r.heavy.length) bad.push('тяжёлые: ' + r.heavy.join(', '));
    if (r.blurry.length) bad.push('мыло: ' + r.blurry.join(', '));
    if (r.clipped.length) bad.push('обрезаны: ' + r.clipped.join(', '));
    if (r.fonts.length > 7) bad.push('шрифтов ' + r.fonts.length + ': ' + r.fonts.join(' '));
    if (r.errs.length) bad.push('ошибки: ' + r.errs.join(' | '));
    return `${r.url} @${r.W}: ${bad.length ? bad.join(' · ') : 'ок'} (${r.fonts.length} разм., ${r.kb} КБ)`;
  }).join('\n');
  return out;
};
