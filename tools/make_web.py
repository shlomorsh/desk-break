# Makes the browser version of the exercise library (the app's library screen, browse-only) in <out>/.
# Run:  python tools/make_web.py <out-folder>
import shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
THREE = 'https://cdn.jsdelivr.net/npm/three@0.186.1/'

page = (ROOT / 'app/settings.html').read_text(encoding='utf-8')
for a, b in [('../vendor/three/three.module.js', THREE + 'build/three.module.js'),
             ('../vendor/three/addons/', THREE + 'examples/jsm/'),
             ('../library/', './'),
             ('    <div id="general">', '    <p class="muted" style="margin-top:28px;font-size:13px">ספרייה פתוחה (MIT) מתוך <a href="https://github.com/shlomorsh/desk-break">Desk Break</a> · <a href="/desk-break/">על הכלי</a> · <a href="/privacy.html">פרטיות</a> · <a href="/terms.html">תנאי שימוש</a> · <a href="/accessibility.html">נגישות</a></p>\n    <div id="general">'),
('<title>ספרייה והגדרות</title>', '<title>ספריית התרגילים · Desk Break</title>')]:
    assert a in page, a
    page = page.replace(a, b)
(out / 'index.html').write_text(page, encoding='utf-8')
(out / 'wood.css').write_text((ROOT / 'app/wood.css').read_text(encoding='utf-8').replace('../library/wood.png', 'wood.png'), encoding='utf-8')
for f in ['app/store.js', 'app/icon.png', 'library/player.js', 'library/wood.png', 'library/exercises.glb', 'library/exercises.json']:
    shutil.copy(ROOT / f, out / Path(f).name)
print('web library ->', out)
