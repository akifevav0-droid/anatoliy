# Собирает версию 4 (4 страницы + оферта) из папки src: основа.html + страница.
# Запуск: python3 сайт/выкладка/v4/собрать.py   ·   Дизайн-система: v4/ДИЗАЙН_СИСТЕМА.md
import hashlib, json, os, re
D = os.path.dirname(os.path.abspath(__file__))
os.chdir(D)
src = lambda n: open(os.path.join('src', n), encoding='utf-8').read()

# Телефон Анатолия (подтверждён Викторией 04.10.2026). Пусто — только Telegram.
PHONE = '+7 996 966-91-60'
# Кнопки «Оплатить» у групп: счета ЮKassa из bot/config.json. False — только «Записаться».
PAY = True

css = src('стиль.css')
open('v4.css', 'w', encoding='utf-8').write(css)
V = hashlib.md5(css.encode()).hexdigest()[:8]

wm = open('../assets/wordmark.svg', encoding='utf-8').read()
wm = re.sub(r'<\?xml[^>]*>\s*', '', wm).replace('<svg ', '<svg aria-hidden="true" style="width:100%;height:auto" ', 1)
ARROW = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
CHOICE = ('<a class="btn" href="%%TEL%%">Позвонить %%ARROW%%</a>\n      '
          '<a class="btn ghost" href="https://t.me/shabarshov" target="_blank" rel="noopener">Написать в Telegram %%ARROW%%</a>')
if not PHONE:
    CHOICE = CHOICE.split('\n      ', 1)[1]

CFG = json.load(open('../../../bot/config.json', encoding='utf-8'))
INV = {p['code']: p for p in CFG['products']}


def pay_buttons(s):
    on = PAY and all(INV.get(c, {}).get('invoice_url') for c in ('g1', 'g4', 'g8'))
    for c, title in (('g1', 'Разовая тренировка'), ('g4', '4 тренировки на месяц'), ('g8', '8 тренировок на месяц')):
        btn = ''
        if on:
            price = f"{INV[c]['price']:,}".replace(',', ' ') + ' ₽'
            btn = (f'<button class="link" type="button" data-pay="{INV[c]["invoice_url"]}" '
                   f'data-title="{title}" data-price="{price}">Оплатить</button>')
        else:
            btn = '<button class="link" type="button" data-contact>Записаться</button>'
        s = s.replace(f'%%PAY_{c}%%', btn)
    return s


def offer_body():
    parts = [p.strip() for p in src('оферта.md').split('\n\n') if p.strip()]
    paras = '\n'.join(f'    <p>{p}</p>' for p in parts[1:])
    return (f'<section style="padding:calc(var(--hdr) + var(--s4)) var(--pad) var(--s4)">\n  <div class="in">\n'
            f'  <h1 class="t-xl">{parts[0]}</h1>\n  <div class="offer-text">\n{paras}\n  </div>\n  </div>\n</section>')


PAGES = [
    # файл, папка, page, заголовок, описание, призыв, текст призыва
    ('главная.html', '', 'pers', 'Персональные тренировки по плаванию в «Акватории ЗИЛ» | Анатолий Шабаршов',
     'Как вы плаваете? Персональные тренировки по плаванию в «Акватории ЗИЛ» с мастером спорта Анатолием Шабаршовым — тренер рядом с вами в воде.',
     'Бассейн уже налит. Осталось записаться.', 'Позвоните или напишите — Анатолий ответит сам.'),
    ('группы.html', 'gruppy/', 'groups', 'Групповые тренировки по плаванию для взрослых в Москве | SHABARSHOV swimming club',
     'Группы по плаванию для взрослых с Анатолием Шабаршовым: Бауманка, «Формула Воды», ЗИЛ «Акватория». Первая тренировка бесплатно.',
     'Приходите на пробную.', 'Позвоните или напишите — Анатолий подскажет группу по уровню.'),
    ('соревнования.html', 'sorevnovaniya/', 'comp', 'Подготовка к заплыву на открытой воде | Анатолий Шабаршов',
     'Подготовка к X‑WATERS, SwimCup и стартам Мастерс с мастером спорта Анатолием Шабаршовым. Дистанции от 500 м до 25 км.',
     'Готовитесь к старту?', 'Позвоните или напишите — Анатолий ответит сам.'),
    ('сертификат.html', 'sertifikat/', 'cert', 'Подарочный сертификат на тренировку по плаванию | Анатолий Шабаршов',
     'Подарочный сертификат на персональную тренировку по плаванию с Анатолием Шабаршовым: 5 000 ₽, «Акватория ЗИЛ», действует 2 месяца.',
     'Подарите тренировку.', 'Позвоните или напишите Анатолию — карту пришлём после оплаты.'),
    ('_оферта', 'oferta/', 'offer', 'Договор-оферта | SHABARSHOV swimming club',
     'Договор-оферта ИП Шабаршов А. С. на оказание услуг по обучению плаванию.',
     'Остались вопросы?', 'Позвоните или напишите — Анатолий ответит сам.'),
]

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
        t = re.sub(r'(\d) (?=(₽|м|км|лет|мин|минут|тыс|человек|раз|раза|тренировк|часов|ч)\b|₽)', '\\1\u00a0', t)
        t = re.sub(r'(«Акватори[ия]) ', '\\1\u00a0', t)
        parts[i] = t
    return ''.join(parts)


base = src('основа.html')
for fn, folder, pg, title, desc, ct, ctt in PAGES:
    s = base.replace('%%BODY%%', offer_body() if fn == '_оферта' else src(fn))
    s = pay_buttons(s).replace('%%CHOICE%%', CHOICE)
    for k in ('pers', 'groups', 'comp', 'cert'):
        s = s.replace(f'%%CUR_{k}%%', ' aria-current="page"' if k == pg else '')
    rep = {'BASE': '../' + '../' * folder.count('/'), 'TITLE': title, 'DESC': desc, 'CTA_TITLE': ct, 'CTA_TEXT': ctt,
           'V': V, 'PHONE': PHONE, 'TEL': 'tel:' + re.sub(r'[^\d+]', '', PHONE)}
    for k, v in rep.items():
        s = s.replace(f'%%{k}%%', v)
    s = s.replace('%%WORDMARK%%', wm).replace('%%ARROW%%', ARROW)
    assert '%%' not in s, (fn, re.findall(r'%%\w+%%', s))
    s = re.sub(r'(data-(?:head|sub)=")([^"]*)"', lambda m: m.group(1) + typo(m.group(2)) + '"', s)
    s = typo(s)
    os.makedirs(folder or '.', exist_ok=True)
    open(os.path.join(folder, 'index.html'), 'w', encoding='utf-8').write(s)
    print('ok', folder or '/')
