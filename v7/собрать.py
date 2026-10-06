# Версия 7 «Сначала страхи» — собирается общим движком (система/движок.py).
# Запуск: python3 сайт/выкладка/v7/собрать.py
import os, re, sys
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(D, '..', 'система'))
import движок as E

P = 'v7/'
PHONE = '+7 996 966-91-60'   # подтверждён Викторией 04.10.2026
TEL = re.sub(r'[^\d+]', '', PHONE)
PAY_MODAL, PAY_BUTTONS = E.pay_setup(P, on=True)

CHOICE = ('<a class="btn" href="https://t.me/shabarshov" target="_blank" rel="noopener">Написать в Telegram</a>'
          f'<a class="btn out" href="tel:{TEL}">Позвонить</a>')
FINAL = '''
<section class="sec final" id="zapis">
  <div class="wrap">
    <h2 class="h2">%%F_TITLE%%</h2>
    <p class="lead">%%F_TEXT%%</p>
    <div class="acts">%%F_ACTS%%</div>
    <p class="phone">%%PHONE%%</p>
  </div>
</section>'''
ASK = 'Позвоните или напишите — Анатолий ответит сам.'
HB = '<button class="btn" type="button" data-contact>{}</button>'
DOCK = '<button class="btn" type="button" data-contact>{}</button>'

E.build({
    'dir': D, 'prefix': P, 'phone': PHONE, 'offer': True, 'index': False,
    'fonts': 'https://fonts.googleapis.com/css2?family=Unbounded:wght@400&family=Onest:wght@400;500;600&display=swap',
    'theme_color': '#FFFFFF', 'og_image': 'assets/r/v7-trener-1400-1280.jpg',
    'menu': 'Меню', 'logo': '%%WORDMARK%%',
    'foot_contacts': f'<a href="tel:{TEL}">{PHONE}</a><a href="https://t.me/shabarshov" target="_blank" rel="noopener">Telegram</a><a href="https://instagram.com/shabarshov_" target="_blank" rel="noopener">Instagram</a>',
    'choice': CHOICE, 'final': FINAL, 'pay_modal': PAY_MODAL, 'pay_buttons': PAY_BUTTONS,
    'pages': [
        dict(key='pers', file='главная.html', folder='', hdr_btn=HB.format('Записаться'), dock=DOCK.format('Записаться · 5 000 ₽'),
             title='Персональные тренировки по плаванию в «Акватории ЗИЛ» | Анатолий Шабаршов',
             desc='Персональные тренировки по плаванию в «Акватории ЗИЛ» с мастером спорта Анатолием Шабаршовым — тренер плывёт рядом с вами в воде.'),
        dict(key='groups', file='группы.html', folder='gruppy/', hdr_btn=HB.format('Записаться'), dock=DOCK.format('Записаться на пробную'),
             final=('Приходите на пробную', ASK, CHOICE),
             title='Групповые тренировки по плаванию для взрослых в Москве | SHABARSHOV swimming club',
             desc='Группы по плаванию для взрослых с Анатолием Шабаршовым: Бауманка, «Формула Воды», ЗИЛ «Акватория». Группы по уровню, клубные старты и открытая вода.'),
        dict(key='comp', file='соревнования.html', folder='sorevnovaniya/', hdr_btn=HB.format('Записаться'), dock=DOCK.format('Обсудить подготовку'),
             final=('Готовитесь к старту?', ASK, CHOICE),
             title='Подготовка к заплыву на открытой воде | Анатолий Шабаршов',
             desc='Подготовка к X‑WATERS, SwimCup и стартам Мастерс с мастером спорта Анатолием Шабаршовым. Дистанции от 500 м до 25 км.'),
        dict(key='cert', file='сертификат.html', folder='sertifikat/', hdr_btn=HB.format('Подарить'), dock=DOCK.format('Подарить · 5 000 ₽'),
             final=('Подарите тренировку', ASK, CHOICE),
             title='Подарочный сертификат на тренировку по плаванию | Анатолий Шабаршов',
             desc='Подарочный сертификат на персональную тренировку по плаванию с Анатолием Шабаршовым: 5 000 ₽, «Акватория ЗИЛ», действует 2 месяца.'),
        dict(key='offer', body=E.offer_page(os.path.join(D, 'src', 'оферта.md')), folder='oferta/', hdr_btn=HB.format('Записаться'),
             title='Договор-оферта | SHABARSHOV swimming club',
             desc='Договор-оферта ИП Шабаршов А. С. на оказание услуг по обучению плаванию.'),
    ],
})
