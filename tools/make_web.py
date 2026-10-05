# Makes the browser version of the exercise library (the app's library screen, browse-only) in <out>/,
# plus app.html, the floating figure + panel for a live demo inside a web page (open it as app.html#panel).
# Both pages speak Hebrew or English: ?lang=en in the address, otherwise the visitor's browser language.
# Run:  python tools/make_web.py <out-folder>
import shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
THREE = 'https://cdn.jsdelivr.net/npm/three@0.186.1/'
FOOTER = ('    <p class="muted" style="margin-top:28px;font-size:13px"><span data-t="footer"></span> '
          '<a href="https://github.com/shlomorsh/desk-break">Desk Break</a> · <a id="aboutLink" href="/desk-break/" data-t="about"></a> · '
          '<a href="/privacy.html" data-t="privacy"></a> · <a href="/terms.html" data-t="terms"></a> · '
          '<a href="/accessibility.html" data-t="a11y"></a></p>\n')
CDN = [('../vendor/three/three.module.js', THREE + 'build/three.module.js'),
       ('../vendor/three/addons/', THREE + 'examples/jsm/'), ('../library/', './')]


def page(src, extra=()):
    text = (ROOT / src).read_text(encoding='utf-8')
    for a, b in CDN + list(extra):
        assert a in text, a
        text = text.replace(a, b)
    return text


(out / 'index.html').write_text(page('app/settings.html', [
    ('    <div id="general">', FOOTER + '    <div id="general">'),
    ('<title>ספרייה והגדרות</title>', '<title>ספריית התרגילים · Desk Break</title>')]), encoding='utf-8')
(out / 'app.html').write_text(page('app/index.html'), encoding='utf-8')
(out / 'wood.css').write_text((ROOT / 'app/wood.css').read_text(encoding='utf-8').replace('../library/wood.png', 'wood.png'), encoding='utf-8')
for f in ['app/store.js', 'app/i18n.js', 'app/icon.png', 'library/player.js', 'library/wood.png', 'library/exercises.glb', 'library/exercises.json']:
    shutil.copy(ROOT / f, out / Path(f).name)
print('web library ->', out)
