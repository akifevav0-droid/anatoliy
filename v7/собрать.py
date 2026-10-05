# Собирает версию 7 (4 страницы + оферта) из папки src: основа.html + страница.
# Запуск: python3 сайт/выкладка/v7/собрать.py
import hashlib, json, os, re
D = os.path.dirname(os.path.abspath(__file__))
os.chdir(D)
src = lambda n: open(os.path.join('src', n), encoding='utf-8').read()

PHONE = '+7 996 966-91-60'   # подтверждён Викторией 04.10.2026
PAY = True                   # «Оплатить» у групп — счета ЮKassa из bot/config.json
TEL = re.sub(r'[^\d+]', '', PHONE)

css = src('стиль.css')
open('v7.css', 'w', encoding='utf-8').write(css)
V = hashlib.md5(css.encode()).hexdigest()[:8]

wm = open('../assets/wordmark.svg', encoding='utf-8').read()
wm = re.sub(r'<\?xml[^>]*>\s*', '', wm).replace('<svg ', '<svg aria-hidden="true" style="width:100%;height:auto" ', 1)

CHOICE = ('<a class="btn" href="https://t.me/shabarshov" target="_blank" rel="noopener">Написать в Telegram</a>'
          f'<a class="btn out" href="tel:{TEL}">Позвонить</a>')
CHOICE_DARK = (f'<a class="btn white" href="tel:{TEL}">Позвонить</a>'
               '<a class="btn white" style="background:transparent;color:#fff" href="https://t.me/shabarshov" target="_blank" rel="noopener">Написать в Telegram</a>')

I = lambda d: f'<svg viewBox="0 0 24 24" aria-hidden="true" stroke-linecap="round" stroke-linejoin="round">{d}</svg>'
ICONS = {
    'I_EYE': I('<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>'),
    'I_HAND': I('<path d="M3 15c2 0 2-2 4-2s2 2 4 2 2-2 4-2 2 2 4 2 2-2 2-2"/><path d="M3 19c2 0 2-2 4-2s2 2 4 2 2-2 4-2 2 2 4 2 2-2 2-2"/><path d="M12 3v7M9 7l3 3 3-3"/>'),
    'I_ZERO': I('<circle cx="12" cy="7" r="3"/><path d="M5 21c0-4 3-7 7-7s7 3 7 7"/>'),
    'I_MEDAL': I('<circle cx="12" cy="15" r="5"/><path d="M8 3l2 7M16 3l-2 7M12 13v4"/>'),
    'I_VIDEO': I('<rect x="2" y="6" width="14" height="12" rx="1"/><path d="M16 10l6-3v10l-6-3z"/>'),
    'I_CLOCK': I('<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>'),
    'I_CHAT': I('<path d="M4 5h16v11H9l-5 4z"/>'),
    'I_WAVE': I('<path d="M2 10c2.5 0 2.5-2 5-2s2.5 2 5 2 2.5-2 5-2 2.5 2 5 2"/><path d="M2 16c2.5 0 2.5-2 5-2s2.5 2 5 2 2.5-2 5-2 2.5 2 5 2"/>'),
    'I_CARD': I('<rect x="2" y="5" width="20" height="14" rx="2"/><path d="M2 10h20"/>'),
    'I_STAR': I('<path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z"/>'),
}

CFG = json.load(open('../../../bot/config.json', encoding='utf-8'))
INV = {p['code']: p for p in CFG['products']}


def pay_buttons(s):
    on = PAY and all(INV.get(c, {}).get('invoice_url') for c in ('g1', 'g4', 'g8'))
    for c, title in (('g1', 'Разовая тренировка'), ('g4', '4 тренировки на месяц'), ('g8', '8 тренировок на месяц')):
        if on:
            price = f"{INV[c]['price']:,}".replace(',', ' ') + ' ₽'
            btn = (f'<button class="lnk" type="button" data-pay="{INV[c]["invoice_url"]}" '
                   f'data-title="{title}" data-price="{price}">Оплатить</button>')
        else:
            btn = '<button class="lnk" type="button" data-contact>Записаться</button>'
        s = s.replace(f'%%PAY_{c}%%', btn)
    return s


def offer_body():
    parts = [p.strip() for p in src('оферта.md').split('\n\n') if p.strip()]
    paras = '\n'.join(f'    <p>{p}</p>' for p in parts[1:])
    return (f'<section class="sec"><div class="wrap">\n  <h1 class="h2">{parts[0]}</h1>\n'
            f'  <div class="offer-text">\n{paras}\n  </div>\n</div></section>')


PAGES = [
    # файл, папка, page, заголовок, описание, кнопка шапки
    ('главная.html', '', 'pers', 'Персональные тренировки по плаванию в «Акватории ЗИЛ» | Анатолий Шабаршов',
     'Персональные тренировки по плаванию в «Акватории ЗИЛ» с мастером спорта Анатолием Шабаршовым — тренер плывёт рядом с вами в воде.', 'Записаться'),
    ('группы.html', 'gruppy/', 'groups', 'Групповые тренировки по плаванию для взрослых в Москве | SHABARSHOV swimming club',
     'Группы по плаванию для взрослых с Анатолием Шабаршовым: Бауманка, «Формула Воды», ЗИЛ «Акватория». Группы по уровню, клубные старты и открытая вода.', 'Записаться'),
    ('соревнования.html', 'sorevnovaniya/', 'comp', 'Подготовка к заплыву на открытой воде | Анатолий Шабаршов',
     'Подготовка к X‑WATERS, SwimCup и стартам Мастерс с мастером спорта Анатолием Шабаршовым. Дистанции от 500 м до 25 км.', 'Записаться'),
    ('сертификат.html', 'sertifikat/', 'cert', 'Подарочный сертификат на тренировку по плаванию | Анатолий Шабаршов',
     'Подарочный сертификат на персональную тренировку по плаванию с Анатолием Шабаршовым: 5 000 ₽, «Акватория ЗИЛ», действует 2 месяца.', 'Подарить'),
    ('_оферта', 'oferta/', 'offer', 'Договор-оферта | SHABARSHOV swimming club',
     'Договор-оферта ИП Шабаршов А. С. на оказание услуг по обучению плаванию.', 'Записаться'),
]

FINAL = """
<section class="sec final2" id="zapis">
  <div class="wrap">
    <h2 class="h2">%%F_TITLE%%</h2>
    <p class="lead">Позвоните или напишите — Анатолий ответит сам.</p>
    <div class="acts">%%CHOICE%%</div>
    <p class="phone">%%PHONE%%</p>
  </div>
</section>"""
FINALS = {'groups': 'Приходите на пробную', 'comp': 'Готовитесь к старту?', 'cert': 'Подарите тренировку'}

SHORT = r'(?:[а-яёА-ЯЁ]{1,2}|без|для|над|под|при|про|что|как|или|все|всё|его|её|их)'


def typo(html):
    """Неразрывные пробелы: после коротких слов, перед тире, между числом и единицей."""
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
        t = re.sub(r'(«Акватори[ия]) ', '\\1\u00a0', t)
        parts[i] = t
    return ''.join(parts)


base = src('основа.html')
for fn, folder, pg, title, desc, hdr in PAGES:
    body = offer_body() if fn == '_оферта' else src(fn)
    if pg in FINALS:
        body += FINAL.replace('%%F_TITLE%%', FINALS[pg])
    s = base.replace('%%BODY%%', body)
    s = pay_buttons(s).replace('%%CHOICE_DARK%%', CHOICE_DARK).replace('%%CHOICE%%', CHOICE)
    for k, v in ICONS.items():
        s = s.replace(f'%%{k}%%', v)
    for k in ('pers', 'groups', 'comp', 'cert'):
        s = s.replace(f'%%CUR_{k}%%', ' aria-current="page"' if k == pg else '')
    BARS = {}  # полоса сверху убрана: повторяла первый экран
    DOCK = {'pers': 'Записаться · 5 000 ₽', 'groups': 'Записаться на пробную', 'comp': 'Обсудить подготовку', 'cert': 'Подарить · 5 000 ₽'}
    s = s.replace('%%DOCK%%', DOCK.get(pg, 'Записаться'))
    bar = BARS.get(pg, '')
    s = s.replace('<div class="bar">%%BAR%%</div>\n', f'<div class="bar">{bar}</div>\n' if bar else '')
    rep = {'BASE': '../' + '../' * folder.count('/'), 'TITLE': title, 'DESC': desc, 'HDR_BTN': hdr,
           'V': V, 'PHONE': PHONE, 'TEL': TEL}
    for k, v in rep.items():
        s = s.replace(f'%%{k}%%', v)
    s = s.replace('%%WORDMARK%%', wm)
    # якоря «#блок»: из-за <base> ссылка считалась бы от корня сайта и уводила на версию 1 — ведём на свою страницу
    s = re.sub(r'href="#([\w-]+)"', lambda m: f'href="v7/{folder}#{m.group(1)}"', s)
    assert '%%' not in s, (fn, re.findall(r'%%\w+%%', s))
    s = typo(s)
    os.makedirs(folder or '.', exist_ok=True)
    open(os.path.join(folder, 'index.html'), 'w', encoding='utf-8').write(s)
    print('ok', folder or '/')
