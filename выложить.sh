#!/bin/bash
# Сборка и выкладка версий 1 (корень), 2 и 7 на GitHub Pages. Версию 8 не трогает.
# Правим исходники (vN/src, vN/тема.css, система/), затем: bash выложить.sh "что изменилось"
# Собрать без выкладки: NOPUSH=1 bash выложить.sh
set -e
cd "$(dirname "$0")"
MSG="${1:-Обновление сайта}"
python3 v1/собрать.py
python3 v2/собрать.py
python3 v7/собрать.py
if [ -n "$NOPUSH" ]; then echo "собрано локально"; exit 0; fi
git add -A -- index.html gruppy sorevnovaniya sertifikat v1 v2 v7 система assets smoke-cursor.js выложить.sh
git add -u -- .
git reset -q -- v8 2>/dev/null || true
git commit -qm "$MSG

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" || true
git push -q
echo "выложено"
