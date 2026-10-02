#!/bin/bash
# Выкладка сайта на GitHub Pages так, чтобы браузеры сразу видели новую версию.
# Правим Main.dc.html (исходник), затем: bash выложить.sh "что изменилось"
# Проверить у себя без выкладки: NOPUSH=1 bash выложить.sh
set -e
cd "$(dirname "$0")"
MSG="${1:-Обновление сайта}"

# метка версии — по содержимому страницы, скриптов и файлов
V=$(cat Main.dc.html smoke-cursor.js support.js assets/* | md5 -q | cut -c1-8)

# страница под новым именем: старое имя браузер мог запомнить на 10 минут
rm -f Main-*.dc.html
python3 - "$V" <<'EOF'
import re, sys
v = sys.argv[1]
s = open('Main.dc.html', encoding='utf-8').read()
s = re.sub(r'(assets/[\w.-]+\.(?:jpg|png|svg|mp4))', r'\1?v=' + v, s)
open(f'Main-{v}.dc.html', 'w', encoding='utf-8').write(s)
i = open('index.html', encoding='utf-8').read()
i = re.sub(r'<dc-import name="Main[\w-]*"', f'<dc-import name="Main-{v}"', i)
i = re.sub(r'(src="\.?/?(?:support|smoke-cursor)\.js)(\?v=\w+)?"', r'\1?v=' + v + '"', i)
i = re.sub(r'(href="(?:favicon\.svg|apple-touch-icon\.png))(\?v=\w+)?"', r'\1?v=' + v + '"', i)
open('index.html', 'w', encoding='utf-8').write(i)
EOF

if [ -n "$NOPUSH" ]; then echo "собрано локально, версия $V"; exit 0; fi
git add -A
git commit -qm "$MSG

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" || true
git push -q
echo "выложено, версия $V"
