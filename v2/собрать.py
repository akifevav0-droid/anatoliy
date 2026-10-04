# Собирает v2/index.html из v2/исходник.html: вставляет SHABARSHOV и значки
import re, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
s = open('исходник.html', encoding='utf-8').read()
wm = open('../assets/wordmark.svg', encoding='utf-8').read()
wm = re.sub(r'<\?xml[^>]*>\s*', '', wm).replace('<svg ', '<svg role="img" aria-hidden="true" style="width:100%;height:auto" ', 1)
ARROW = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
PLAY = '<svg width="20" height="20" viewBox="0 0 24 24" fill="#14151F" aria-hidden="true"><path d="M7 4l13 8-13 8z"/></svg>'
s = s.replace('%%WORDMARK%%', wm).replace('%%ARROW%%', ARROW).replace('%%PLAY%%', PLAY)
assert '%%' not in s
open('index.html', 'w', encoding='utf-8').write(s)
print('ok')
