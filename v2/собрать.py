# Собирает 4 страницы версии 2 из папки src: основа.html + страница + общие куски.
# Запуск: python3 сайт/выкладка/v2/собрать.py
import hashlib, os, re
D = os.path.dirname(os.path.abspath(__file__))
os.chdir(D)
src = lambda n: open(os.path.join('src', n), encoding='utf-8').read()

css = src('стиль.css')
open('v2.css', 'w', encoding='utf-8').write(css)
V = hashlib.md5(css.encode()).hexdigest()[:8]

wm = open('../assets/wordmark.svg', encoding='utf-8').read()
wm = re.sub(r'<\?xml[^>]*>\s*', '', wm).replace('<svg ', '<svg aria-hidden="true" style="width:100%;height:auto" ', 1)
ARROW = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
PLAY = '<svg width="20" height="20" viewBox="0 0 24 24" fill="#14151F" aria-hidden="true"><path d="M7 4l13 8-13 8z"/></svg>'

POOL = '''<section class="sec pool" id="basseyn">
  <img class="full" src="assets/w-pool-zil.jpg" alt="Открытый бассейн «Акватории ЗИЛ»" loading="lazy">
  <a class="btn route" href="https://yandex.ru/maps/org/akvatoriya_zil/220499522989/" target="_blank" rel="noopener">Маршрут %%ARROW%%</a>
  <div class="over">
    <h2 class="h-l">50 метров под открытым небом.<br>Вода +28 °C круглый год.</h2>
    <p style="margin-top:12px;opacity:.9">ЗИЛ «Акватория» · МЦК ЗИЛ</p>
  </div>
</section>'''
FACTS = '''<div class="rv"><b>Мастер спорта<br>по плаванию</b><span>УОР и РГУФК.</span></div>
    <div class="rv"><b>10 лет<br>тренерского стажа</b><span>От «боюсь воды» до открытой воды.</span></div>
    <div class="rv"><b>Побед —<br>не сосчитать</b><span>Победы и медали: X‑WATERS, Кубок и чемпионат России Мастерс.</span></div>'''
LOGO = '<a class="logo" href="v2/" aria-label="SHABARSHOV swimming club — на главную">%%WORDMARK%%</a>'

PAGES = [
    # файл, папка, page, заголовок, описание, кнопка шапки, ссылка, призыв, текст призыва, кнопка призыва
    ('главная.html', '', 'pers', 'Персональные тренировки по плаванию в «Акватории ЗИЛ» | Анатолий Шабаршов',
     'Персональные тренировки по плаванию в «Акватории ЗИЛ» с мастером спорта Анатолием Шабаршовым. Тренер рядом с вами в воде.',
     'Записаться', 'https://t.me/shabarshov_club_bot?start=pers_v2',
     'Бассейн уже налит. Осталось записаться.', 'Пара нажатий в боте — Анатолий напишет сам.', 'Записаться'),
    ('группы.html', 'gruppy/', 'groups', 'Групповые тренировки по плаванию для взрослых в Москве | SHABARSHOV swimming club',
     'Группы по плаванию для взрослых с Анатолием Шабаршовым, мастером спорта: Бауманка, «Формула Воды», ЗИЛ «Акватория». Первая тренировка бесплатно.',
     'Пробная', 'https://t.me/shabarshov',
     'Приходите на пробную.', 'Напишите Анатолию — подскажет группу по уровню.', 'Написать в Telegram'),
    ('соревнования.html', 'sorevnovaniya/', 'comp', 'Подготовка к заплыву на открытой воде | Анатолий Шабаршов',
     'Подготовка к X‑WATERS, SwimCup, Swimstar, Grand Swim Series, Hydra Swim с мастером спорта Анатолием Шабаршовым. Дистанции от 500 м до 25 км.',
     'Обсудить', 'https://t.me/shabarshov_club_bot?start=pers_v2comp',
     'Готовитесь к старту?', 'Оставьте заявку — Анатолий напишет сам.', 'Обсудить подготовку'),
    ('сертификат.html', 'sertifikat/', 'cert', 'Подарочный сертификат на тренировку по плаванию | Анатолий Шабаршов',
     'Подарочный сертификат на персональную тренировку по плаванию с Анатолием Шабаршовым: 5 000 ₽, «Акватория ЗИЛ», действует 2 месяца.',
     'Подарить', 'https://t.me/shabarshov_club_bot?start=gift_v2',
     'Подарите тренировку.', 'Именная карта придёт в Telegram. Останется вручить.', 'Подарить тренировку'),
]

SHORT = r'(?:[а-яёА-ЯЁ]{1,2}|без|для|над|под|при|про|что|как|или|все|всё|его|её|их)'


def typo(html):
    """Неразрывные пробелы: после коротких слов, перед тире, между числом и единицей."""
    parts = re.split(r'(<script[\s\S]*?</script>|<style[\s\S]*?</style>|<svg[\s\S]*?</svg>|<[^>]+>)', html)
    for i in range(0, len(parts), 2):
        t = parts[i]
        if not t.strip():
            continue
        t = re.sub(r'(?<![\wа-яёА-ЯЁ\-])(' + SHORT + r') (?=\S)', '\\1\u00a0', t)
        t = re.sub(r'(?<![\wа-яёА-ЯЁ\-])(' + SHORT + r') (?=\S)', '\\1\u00a0', t)  # подряд: «и в»
        t = re.sub(r' (—|–)', '\u00a0\\1', t)
        t = re.sub(r'(\d) (?=\d{3}\b)', '\\1\u00a0', t)
        t = re.sub(r'(\d) (?=(₽|м|км|лет|мин|минут|тыс|человек|раз|раза|тренировк|часов|ч)\b|₽)', '\\1\u00a0', t)
        t = re.sub(r'(№|«Акватори[ия]) ', '\\1\u00a0', t)
        parts[i] = t
    return ''.join(parts)


base = src('основа.html')
for fn, folder, pg, title, desc, btn, href, ct, ctt, ctb in PAGES:
    s = base.replace('%%BODY%%', src(fn))
    s = s.replace('%%POOL%%', POOL).replace('%%FACTS%%', FACTS)
    s = s.replace('%%LOGO%%', '' if pg == 'pers' else LOGO)
    for k in ('pers', 'groups', 'comp', 'cert'):
        s = s.replace(f'%%CUR_{k}%%', ' aria-current="page"' if k == pg else '')
    rep = {'BASE': '../' + '../' * folder.count('/'), 'TITLE': title, 'DESC': desc, 'BTN': btn, 'BTN_HREF': href,
           'CTA_TITLE': ct, 'CTA_TEXT': ctt, 'CTA_BTN': ctb, 'V': V}
    for k, v in rep.items():
        s = s.replace(f'%%{k}%%', v)
    s = s.replace('%%WORDMARK%%', wm).replace('%%ARROW%%', ARROW).replace('%%PLAY%%', PLAY)
    assert '%%' not in s, (fn, re.findall(r'%%\w+%%', s))
    s = typo(s)
    os.makedirs(folder or '.', exist_ok=True)
    open(os.path.join(folder, 'index.html'), 'w', encoding='utf-8').write(s)
    print('ok', folder or '/')
