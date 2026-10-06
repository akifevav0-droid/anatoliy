# Версия 1 «Мягкая» — основной сайт (корень github.io/anatoliy/), собирается общим движком.
# Запуск: python3 сайт/выкладка/v1/собрать.py
# Раньше был выгрузкой из Claude Design (Main.dc.html + support.js); с 06.10.2026 — обычный код.
import os, sys
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(D, '..', 'система'))
import движок as E

BOT = 'https://t.me/shabarshov_club_bot?start='
IC = f'<span class="ic">{E.ARROW}</span>'
TG = 'https://t.me/shabarshov'
WAVES = ('<svg viewBox="0 0 30 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
         '<path d="M2 5 q3.25 -3.5 6.5 0 t6.5 0 t6.5 0 t6.5 0"/><path d="M2 12 q3.25 -3.5 6.5 0 t6.5 0 t6.5 0 t6.5 0"/><path d="M2 19 q3.25 -3.5 6.5 0 t6.5 0 t6.5 0 t6.5 0"/></svg>')
POOL = '''<section class="sec pool-band" id="basseyny">
  <div class="wrap">
    <div class="sec-head"><h2 class="h2 rise">Где тренируемся</h2></div>
    <div class="ph rise"><img src="assets/w-pool-zil.jpg" alt="Открытый бассейн «Акватории ЗИЛ»"></div>
    <div class="cap"><div><b>ЗИЛ «Акватория»</b><br><span>Автозаводская ул., 23А к4 · МЦК ЗИЛ · м. Автозаводская · крытый и открытый бассейн по 50 м</span></div><a class="btn out" href="https://yandex.ru/maps/org/akvatoriya_zil/220499522989/" target="_blank" rel="noopener">Маршрут %%ARROW%%</a></div>
  </div>
</section>'''
FINAL = '''
<section class="sec final" id="zapis">
  <div class="wrap">
    <h2 class="h2">%%F_TITLE%%</h2>
    <p class="lead">%%F_TEXT%%</p>
    <div class="acts">%%F_ACTS%%</div>
  </div>
</section>'''
link = lambda href, text, cls='btn': f'<a class="{cls}" href="{href}" target="_blank" rel="noopener">{text} %%ARROW%%</a>'
DOCK = lambda href, text: f'<a class="btn" href="{href}" target="_blank" rel="noopener">{text}</a>'

E.build({
    'dir': D, 'prefix': '', 'pub': 'v1/', 'phone': '', 'offer': False, 'index': True,
    'fonts': 'https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600&display=swap',
    'theme_color': '#F6F7FB', 'og_image': 'assets/r/hero-pool-1280.jpg',
    'menu': WAVES, 'logo': '<img src="assets/logo.svg" alt="SHABARSHOV swimming club" width="48" height="48">',
    'hdr_class': ' menu-always', 'arrow': IC, 'repl': {'POOL': POOL, 'BOT': BOT},
    'foot_contacts': f'<a href="{TG}" target="_blank" rel="noopener">Telegram</a><a href="https://instagram.com/shabarshov_" target="_blank" rel="noopener">Instagram</a><a href="https://profi.ru/profile/ShabarshovAS/" target="_blank" rel="noopener">Профи.ру</a>',
    'choice': link(TG, 'Написать в Telegram'), 'final': FINAL,
    'extra_js': '<script src="smoke-cursor.js" data-dot="off" defer></script>\n',
    'pages': [
        dict(key='pers', file='главная.html', folder='', no_hdr_logo=True, hdr_class=' float',
             dock=DOCK(BOT + 'pers_site', 'Записаться на тренировку'),
             final=('Запишитесь на первую тренировку', 'Два вопроса в Telegram-боте — и Анатолий напишет вам сам.', link(BOT + 'pers_site', 'Записаться')),
             title='Тренер по плаванию в Москве — персональные тренировки и открытая вода | Анатолий Шабаршов',
             desc='Персональные тренировки по плаванию в Москве с Анатолием Шабаршовым, мастером спорта по плаванию. Тренер рядом с вами в воде, первая тренировка — со съёмкой и разбором техники.'),
        dict(key='groups', file='группы.html', folder='gruppy/', dock=DOCK(TG, 'Записаться на пробную'),
             final=('Приходите на пробную', 'Напишите Анатолию, в какой бассейн удобнее, — подберёт группу по уровню.', link(TG, 'Написать в Telegram')),
             title='Групповые тренировки по плаванию для взрослых в Москве | SHABARSHOV swimming club',
             desc='Группы по плаванию для взрослых с Анатолием Шабаршовым, мастером спорта: Бауманка, «Формула Воды», ЗИЛ «Акватория». Первая тренировка бесплатно.'),
        dict(key='comp', file='соревнования.html', folder='sorevnovaniya/', dock=DOCK(BOT + 'pers_comp', 'Обсудить подготовку'),
             final=('Готовитесь к старту?', 'Напишите, к какому заплыву и какая дистанция, — Анатолий ответит сам.', link(BOT + 'pers_comp', 'Обсудить подготовку')),
             title='Подготовка к заплыву на открытой воде | Анатолий Шабаршов',
             desc='Подготовка к X‑Waters, SwimCup, Swimstar, Grand Swim Series, Hydra Swim с мастером спорта Анатолием Шабаршовым. Дистанции от 500 м до 25 км.'),
        dict(key='cert', file='сертификат.html', folder='sertifikat/', dock=DOCK(BOT + 'gift_site', 'Подарить тренировку'),
             final=('Подарите тренировку', 'Именная карта с номером придёт в Telegram — останется вручить.', link(BOT + 'gift_site', 'Подарить тренировку')),
             title='Подарочный сертификат на тренировку по плаванию | Анатолий Шабаршов',
             desc='Подарочный сертификат на персональную тренировку по плаванию с Анатолием Шабаршовым: 5 000 ₽, ЗИЛ «Акватория», действует 2 месяца.'),
    ],
})
