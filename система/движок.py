# Общий сборщик версий 1, 2, 7 сайта Анатолия Шабаршова.
# Версия описывает себя в vN/собрать.py (страницы, тема, кнопки) и вызывает build(cfg).
# Что делает:
#   1) site.css = ядро.css + тема версии; site.js = ядро.js;
#   2) страница = основа.html + src/страница.html, подстановки %%…%%, неразрывные пробелы;
#   3) каждая картинка assets/*.jpg|png → <picture> с WebP и JPG/PNG в нескольких ширинах,
#      sizes — по замерам (система/размеры.json), width/height — чтобы страница не прыгала;
#   4) проверка: не осталось %%…%%, нет ссылок на несуществующие файлы.
import hashlib, json, os, re
from PIL import Image

SYS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SYS)                    # сайт/выкладка
ASSETS = os.path.join(ROOT, 'assets')
OUT = os.path.join(ASSETS, 'r')                # нарезанные картинки
SITE = 'https://akifevav0-droid.github.io/anatoliy/'
WIDTHS = [400, 640, 960, 1280, 1600, 1920]
SIZES_FILE = os.path.join(SYS, 'размеры.json')

rd = lambda p: open(p, encoding='utf-8').read()

X = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true"><path d="M5 5l14 14M19 5L5 19"/></svg>'
PLAY = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M7 4l13 8-13 8z"/></svg>'
ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'

PAGES_NAV = [('pers', '', 'Персональные'), ('groups', 'gruppy/', 'Группы'),
             ('comp', 'sorevnovaniya/', 'Соревнования'), ('cert', 'sertifikat/', 'Сертификат')]

# ---------- неразрывные пробелы ----------
SHORT = r'(?:[а-яёА-ЯЁ]{1,2}|без|для|над|под|при|про|что|как|или|все|всё|его|её|их)'


def typo(html):
    parts = re.split(r'(<script[\s\S]*?</script>|<style[\s\S]*?</style>|<svg[\s\S]*?</svg>|<[^>]+>)', html)
    for i in range(0, len(parts), 2):
        t = parts[i]
        if not t.strip():
            continue
        for _ in range(2):
            t = re.sub(r'(?<![\wа-яёА-ЯЁ\-])(' + SHORT + r') (?=\S)', '\\1\u00a0', t)
        t = re.sub(r' (—|–)', '\u00a0\\1', t)
        t = re.sub(r'(\d) (?=\d{3}\b)', '\\1\u00a0', t)
        t = re.sub(r'(\d) (?=(₽|м|км|лет|мин|минут|тыс|человек|раз|раза|тренировк|часов|ч|°C)\b|₽|°)', '\\1\u00a0', t)
        t = re.sub(r'(№|«Акватори[ия]) ', '\\1\u00a0', t)
        parts[i] = t
    return ''.join(parts)


# ---------- картинки ----------
_dims = {}


def dims(rel):
    if rel not in _dims:
        with Image.open(os.path.join(ROOT, rel)) as im:
            _dims[rel] = im.size
    return _dims[rel]


def variants(rel):
    """Нарезать картинку в несколько ширин (WebP + JPG/PNG). Возвращает [(ширина, webp, запасной)]."""
    src = os.path.join(ROOT, rel)
    stem, ext = os.path.splitext(rel[len('assets/'):].replace('/', '-'))
    w0, h0 = dims(rel)
    ws = [w for w in WIDTHS if w < w0 * 0.95] + [min(w0, WIDTHS[-1])]
    os.makedirs(OUT, exist_ok=True)
    res = []
    im = None
    for w in sorted(set(ws)):
        h = round(h0 * w / w0)
        fb_ext = '.png' if ext.lower() == '.png' else '.jpg'
        webp, fb = f'assets/r/{stem}-{w}.webp', f'assets/r/{stem}-{w}{fb_ext}'
        fresh = all(os.path.exists(os.path.join(ROOT, p)) and os.path.getmtime(os.path.join(ROOT, p)) >= os.path.getmtime(src)
                    for p in (webp, fb))
        if not fresh:
            if im is None:
                im = Image.open(src); im.load()
                if fb_ext == '.jpg' and im.mode != 'RGB':
                    im = im.convert('RGB')
            sm = im if w == w0 else im.resize((w, h), Image.LANCZOS)
            sm.save(os.path.join(ROOT, webp), 'WEBP', quality=78, method=6)
            if fb_ext == '.jpg':
                sm.save(os.path.join(ROOT, fb), 'JPEG', quality=80, optimize=True, progressive=True)
            else:
                sm.save(os.path.join(ROOT, fb), 'PNG', optimize=True)
        res.append((w, webp, fb))
    return res


def sizes_for(m):
    """m — замеры {ширина окна: ширина картинки}. Возвращает значение sizes."""
    if not m:
        return '100vw'
    g = lambda k: m.get(str(k), 0)
    phone = max(g(360) / 360, g(390) / 390) * 100 or 100      # на телефоне скрыта — неважно, но не 0
    tab = max(g(768) / 768, g(1024) / 1024) * 100 or phone
    big = g(1920) or g(1440) or 1200
    last = f'{round(g(1920) / 1920 * 100 + .5)}vw' if g(1440) and g(1920) > g(1440) * 1.15 else f'{round(big) + 1}px'
    return f'(max-width:600px) {round(phone + .5)}vw, (max-width:1100px) {round(tab + .5)}vw, {last}'


def picturize(html, page_key, measures, base_rel):
    """<img src="assets/x.jpg" …> → <picture>. Первая картинка страницы грузится сразу, остальные — по мере прокрутки."""
    seen, preload = {}, []
    m0 = html.find('<main')
    first_end = html.find('</section>', m0) if m0 >= 0 else -1

    def rep(m):
        tag = m.group(0)
        src = re.search(r'\ssrc="(assets/[\w./-]+\.(?:jpg|jpeg|png))"', tag)
        if not src or 'data-raw' in tag:
            return tag
        rel = src.group(1)
        n = seen.get(rel, 0); seen[rel] = n + 1
        key = f'{page_key}|{rel}|{n}'
        vs = variants(rel)
        w0, h0 = dims(rel)
        sz = sizes_for(measures.get(key))
        webp = ', '.join(f'{p} {w}w' for w, p, _ in vs)
        fb = ', '.join(f'{p} {w}w' for w, _, p in vs)
        mid = min(vs, key=lambda v: abs(v[0] - 960))[2]
        a = re.sub(r'\s(src|srcset|sizes|width|height|loading|decoding|fetchpriority)="[^"]*"', '', tag)
        eager = 'data-eager' in tag or (m0 <= m.start() < first_end and 'data-lazy' not in tag)
        a = a.replace(' data-eager', '').replace(' data-lazy', '')
        load = ' fetchpriority="high" decoding="async"' if eager else ' loading="lazy" decoding="async"'
        a = a[:-1].rstrip('/').rstrip() + f' src="{mid}" srcset="{fb}" sizes="{sz}" width="{w0}" height="{h0}" data-k="{key}"{load}>'
        if eager:
            preload.append(f'<link rel="preload" as="image" type="image/webp" imagesrcset="{webp}" imagesizes="{sz}" fetchpriority="high">\n')
        return f'<picture><source type="image/webp" srcset="{webp}" sizes="{sz}">{a}</picture>'

    html = re.sub(r'<img\b[^>]*>', rep, html)

    def poster(m):
        rel = m.group(2)
        vs = variants(rel)
        want = int(m.group(3) or 960)
        best = min(vs, key=lambda v: (v[0] < want, abs(v[0] - want)))
        return f'{m.group(1)}="{best[2]}"'
    html = re.sub(r'(poster)="(assets/[\w./-]+\.(?:jpg|png))(?:#(\d+))?"', poster, html)
    return html, ''.join(preload[:1])


# ---------- сборка ----------
def css_min(s):
    s = re.sub(r'/\*[\s\S]*?\*/', '', s)
    s = re.sub(r'\s*\n\s*', '\n', s)
    return s.strip() + '\n'


def build(cfg):
    vdir = cfg['dir']                         # где лежат исходники версии (абс. путь)
    prefix = cfg['prefix']                   # 'v7/' или '' для версии 1 (корень)
    outdir = os.path.join(ROOT, prefix) if prefix else ROOT
    pub = cfg.get('pub', prefix)            # папка, где лежат site.css/site.js (от корня сайта)
    css = rd(os.path.join(SYS, 'ядро.css')) + '\n' + rd(os.path.join(vdir, 'тема.css'))
    js = rd(os.path.join(SYS, 'ядро.js'))
    os.makedirs(os.path.join(ROOT, pub), exist_ok=True)
    open(os.path.join(ROOT, pub, 'site.css'), 'w', encoding='utf-8').write(css_min(css))
    open(os.path.join(ROOT, pub, 'site.js'), 'w', encoding='utf-8').write(js)
    V = hashlib.md5((css + js).encode()).hexdigest()[:8]

    measures = json.load(open(SIZES_FILE, encoding='utf-8')) if os.path.exists(SIZES_FILE) else {}
    base_t = rd(os.path.join(SYS, 'основа.html'))
    wm = rd(os.path.join(ASSETS, 'wordmark.svg'))
    wm = re.sub(r'<\?xml[^>]*>\s*', '', wm).replace('<svg ', '<svg aria-hidden="true" focusable="false" ', 1)
    src = lambda n: rd(os.path.join(vdir, 'src', n))

    tel = re.sub(r'[^\d+]', '', cfg.get('phone', ''))
    common = dict(cfg.get('repl', {}))
    common.update({'X': X, 'PLAY': PLAY, 'WORDMARK': wm, 'PHONE': cfg.get('phone', ''), 'TEL': tel,
                   'ARROW': cfg.get('arrow', ''), 'V': V, 'DIR': pub})
    built = []
    for p in cfg['pages']:
        folder = p['folder']
        depth = (prefix + folder).count('/')
        here = prefix + folder
        s = base_t
        body = p['body'] if 'body' in p else src(p['file'])
        if p.get('final'):
            body += cfg['final'].replace('%%F_TITLE%%', p['final'][0]).replace('%%F_TEXT%%', p['final'][1]).replace('%%F_ACTS%%', p['final'][2])
        s = s.replace('%%BODY%%', body)
        cur = ' aria-current="page"'
        nav = ''.join(f'<a href="{prefix + f or "./"}"{cur if k == p["key"] else ""}>{t}</a>' for k, f, t in PAGES_NAV)
        foot_nav = nav.replace(' aria-current="page"', '') + (f'<a href="{prefix}oferta/">Оферта</a>' if cfg.get('offer') else '')
        r = {
            'BASE': '../' * depth if depth else './',
            'TITLE': p['title'], 'DESC': p['desc'],
            'ROBOTS': '' if cfg.get('index') else '<meta name="robots" content="noindex">\n',
            'OG_IMAGE': SITE + cfg['og_image'], 'THEME_COLOR': cfg['theme_color'], 'FONTS': cfg['fonts'],
            'BODY_CLASS': ' '.join(filter(None, [cfg.get('body_class', ''), p.get('body_class', ''), 'has-dock' if p.get('dock') else ''])),
            'HERE': here, 'HOME': prefix or './',
            'HDR_CLASS': cfg.get('hdr_class', '') + p.get('hdr_class', ''),
            'MENU': cfg['menu'],
            'HDR_LOGO': '' if p.get('no_hdr_logo') else f'<a class="logo" href="{prefix or "./"}" aria-label="SHABARSHOV swimming club — на главную">{cfg["logo"]}</a>',
            'NAV': nav, 'FOOT_NAV': foot_nav, 'FOOT_CONTACTS': cfg['foot_contacts'],
            'HDR_BTN': p.get('hdr_btn', cfg.get('hdr_btn', '')),
            'LOGO': cfg['logo'],
            'DOCK': f'<div class="dock" id="dock">{p["dock"]}</div>\n' if p.get('dock') else '',
            'CHOICE': cfg['choice'], 'PAY_MODAL': cfg.get('pay_modal', ''),
            'EXTRA_JS': cfg.get('extra_js', ''),
        }
        for k, v in r.items():
            s = s.replace(f'%%{k}%%', v)
        if cfg.get('pay_buttons'):
            s = cfg['pay_buttons'](s)
        for _ in range(2):
            for k, v in common.items():
                s = s.replace(f'%%{k}%%', v)
        # якоря «#блок»: с <base> они считались бы от корня — ведём на свою страницу
        s = re.sub(r'href="#([\w-]+)"', lambda m: f'href="{here}#{m.group(1)}"', s)
        s, pre = picturize(s, here, measures, here)
        s = s.replace('%%PRELOAD%%', pre)
        left = re.findall(r'%%\w+%%', s)
        assert not left, (p.get('file'), left)
        s = typo(s)
        # файлы, на которые ссылается страница, должны существовать
        for ref in set(re.findall(r'(?:src|href|poster|data-src[-\w]*|data-video)="((?:assets|v\d)/[^"#?]+)', s)):
            assert os.path.exists(os.path.join(ROOT, ref)), (here, 'нет файла', ref)
        for ref in set(re.findall(r'(?:srcset|imagesrcset)="([^"]+)"', s)):
            for part in ref.split(','):
                f = part.strip().split(' ')[0]
                assert os.path.exists(os.path.join(ROOT, f)), (here, 'нет файла', f)
        os.makedirs(os.path.join(outdir, folder), exist_ok=True)
        open(os.path.join(outdir, folder, 'index.html'), 'w', encoding='utf-8').write(s)
        built.append(here or '/')
    print('собрано:', ', '.join(built), '· версия', V)


# ---------- оплата групп (версии 2 и 7): счета ЮKassa из bot/config.json, окно с галочкой оферты ----------
def pay_setup(prefix, on=True):
    cfgp = os.path.join(ROOT, '..', '..', 'bot', 'config.json')
    inv = {p['code']: p for p in json.load(open(cfgp, encoding='utf-8'))['products']}
    on = on and all(inv.get(c, {}).get('invoice_url') for c in ('g1', 'g4', 'g8'))
    modal = f'''<!-- Оплата: согласие с офертой, потом счёт ЮKassa -->
<div class="modal" id="pay" hidden>
  <div class="m-box" role="dialog" aria-modal="true" aria-labelledby="pay-title">
    <button class="m-close" type="button" data-close aria-label="Закрыть">%%X%%</button>
    <h2 class="h2" id="pay-title">Оплата</h2>
    <p class="h3 pay-price" id="pay-price"></p>
    <label class="agree"><input type="checkbox" id="pay-ok"><span>Согласен с <a href="{prefix}oferta/" target="_blank" rel="noopener">офертой</a></span></label>
    <a class="btn pay-go" id="pay-go" href="{prefix}oferta/" target="_blank" rel="noopener" aria-disabled="true">Перейти к оплате</a>
    <p class="mute small">Оплата через ЮKassa. Получатель — ИП Шабаршов А. С.</p>
  </div>
</div>''' if on else ''

    def buttons(s):
        for c, title in (('g1', 'Разовая тренировка'), ('g4', '4 тренировки на месяц'), ('g8', '8 тренировок на месяц')):
            if on:
                price = f"{inv[c]['price']:,}".replace(',', ' ') + ' ₽'
                b = (f'<button class="btn sm out" type="button" data-pay="{inv[c]["invoice_url"]}" '
                     f'data-title="{title}" data-price="{price}">Оплатить</button>')
            else:
                b = '<button class="btn sm out" type="button" data-contact>Записаться</button>'
            s = s.replace(f'%%PAY_{c}%%', b)
        return s
    return modal, buttons


def offer_page(md_path):
    parts = [p.strip() for p in rd(md_path).split('\n\n') if p.strip()]
    paras = '\n'.join(f'    <p>{p}</p>' for p in parts[1:])
    return (f'<section class="sec"><div class="wrap">\n  <h1 class="h2">{parts[0]}</h1>\n'
            f'  <div class="offer-text">\n{paras}\n  </div>\n</div></section>')
