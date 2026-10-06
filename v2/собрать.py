# Версия 2 «Белая строгая» — собирается общим движком (система/движок.py).
# Запуск: python3 сайт/выкладка/v2/собрать.py
import os, re, sys
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(D, '..', 'система'))
import движок as E

P = 'v2/'
PHONE = '+7 996 966-91-60'   # подтверждён Викторией 04.10.2026
TEL = re.sub(r'[^\d+]', '', PHONE)
PAY_MODAL, PAY_BUTTONS = E.pay_setup(P, on=True)
A = '%%ARROW%%'
CHOICE = (f'<a class="btn" href="tel:{TEL}">Позвонить {A}</a>'
          f'<a class="btn out" href="https://t.me/shabarshov" target="_blank" rel="noopener">Написать в Telegram {A}</a>')
FINAL = '''
<section class="sec final" id="zapis">
  <div class="wrap">
    <h2 class="h1">%%F_TITLE%%</h2>
    <p class="lead">%%F_TEXT%%</p>
    <div class="acts">%%F_ACTS%%</div>
    <p class="phone">%%PHONE%%</p>
  </div>
</section>'''
POOL = f'''<section class="sec pool-band" id="basseyn">
  <div class="wrap">
    <div class="ph rise"><img src="assets/w-pool-zil.jpg" alt="Открытый бассейн «Акватории ЗИЛ»"></div>
    <div class="cap"><div><b>50 метров под открытым небом. Вода +28 °C круглый год.</b><br><span>ЗИЛ «Акватория» · МЦК ЗИЛ</span></div><a class="btn out" href="https://yandex.ru/maps/org/akvatoriya_zil/220499522989/" target="_blank" rel="noopener">Маршрут {A}</a></div>
  </div>
</section>'''
POOL_LINE = '''<section class="pool-band line">
  <div class="wrap"><div class="cap rise"><div><b>Тренируемся в «Акватории ЗИЛ»</b><br><span>Автозаводская ул., 23А к4 · МЦК ЗИЛ · открытый бассейн 50 м</span></div><a class="lnk" href="https://yandex.ru/maps/org/akvatoriya_zil/220499522989/" target="_blank" rel="noopener">Маршрут</a></div></div>
</section>'''
ASK = 'Позвоните или напишите — Анатолий ответит сам.'
HB = '<button class="btn sm" type="button" data-contact>Связаться</button>'
COMMON = dict(hdr_btn=HB)

E.build({
    'dir': D, 'prefix': P, 'phone': PHONE, 'offer': True, 'index': False,
    'fonts': 'https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&display=swap',
    'theme_color': '#FFFFFF', 'og_image': 'assets/r/w-tariff-pers-1280.jpg',
    'menu': 'Меню', 'logo': '%%WORDMARK%%', 'hdr_class': ' float', 'arrow': E.ARROW,
    'repl': {'POOL': POOL, 'POOL_LINE': POOL_LINE},
    'foot_contacts': '<a href="https://t.me/shabarshov" target="_blank" rel="noopener">Telegram</a><a href="https://instagram.com/shabarshov_" target="_blank" rel="noopener">Instagram</a><a href="https://profi.ru/profile/ShabarshovAS/" target="_blank" rel="noopener">Профи.ру</a>',
    'choice': CHOICE, 'final': FINAL, 'pay_modal': PAY_MODAL, 'pay_buttons': PAY_BUTTONS,
    'pages': [
        dict(COMMON, key='pers', file='главная.html', folder='', no_hdr_logo=True,
             final=('Бассейн уже налит. Осталось записаться.', 'Позвоните или напишите — Анатолий ответит сам.', CHOICE),
             title='Персональные тренировки по плаванию в «Акватории ЗИЛ» | Анатолий Шабаршов',
             desc='Персональные тренировки по плаванию в «Акватории ЗИЛ» с мастером спорта Анатолием Шабаршовым. Тренер рядом с вами в воде.'),
        dict(COMMON, key='groups', file='группы.html', folder='gruppy/',
             final=('Приходите на пробную.', 'Позвоните или напишите — Анатолий подскажет группу по уровню.', CHOICE),
             title='Групповые тренировки по плаванию для взрослых в Москве | SHABARSHOV swimming club',
             desc='Группы по плаванию для взрослых с Анатолием Шабаршовым, мастером спорта: Бауманка, «Формула Воды», ЗИЛ «Акватория». Первая тренировка бесплатно.'),
        dict(COMMON, key='comp', file='соревнования.html', folder='sorevnovaniya/',
             final=('Готовитесь к старту?', ASK, CHOICE),
             title='Подготовка к заплыву на открытой воде | Анатолий Шабаршов',
             desc='Подготовка к X‑WATERS, SwimCup, Swimstar, Grand Swim Series, Hydra Swim с мастером спорта Анатолием Шабаршовым. Дистанции от 500 м до 25 км.'),
        dict(COMMON, key='cert', file='сертификат.html', folder='sertifikat/',
             final=('Подарите тренировку.', 'Позвоните или напишите Анатолию — карту пришлём после оплаты.', CHOICE),
             title='Подарочный сертификат на тренировку по плаванию | Анатолий Шабаршов',
             desc='Подарочный сертификат на персональную тренировку по плаванию с Анатолием Шабаршовым: 5 000 ₽, «Акватория ЗИЛ», действует 2 месяца.'),
        dict(COMMON, key='offer', body=E.offer_page(os.path.join(D, 'src', 'оферта.md')).replace('class="sec"', 'class="sec intro"', 1), folder='oferta/',
             final=('Остались вопросы?', ASK, CHOICE),
             title='Договор-оферта | SHABARSHOV swimming club',
             desc='Договор-оферта ИП Шабаршов А. С. на оказание услуг по обучению плаванию.'),
    ],
})
