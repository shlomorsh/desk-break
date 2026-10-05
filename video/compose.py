# Puts the promo together: rendered frames + narration take + ding + Hebrew captions + wooden end card.
#   python video/compose.py            -> video/desk-break-promo.mp4
import subprocess, os
from pathlib import Path
from urllib.parse import quote
from playwright.sync_api import sync_playwright

V = Path(__file__).resolve().parent
TAKE = r'C:\studio\tools\video-engine\remotion\voice\desk-break-promo\_take.mp3'
OUT = V / 'desk-break-promo.mp4'
END = 29.5
# phrase timings from the word timestamps of the take
CAPS = [(0.0, 1.55, 'נתת למחשב משימה.'), (1.66, 3.22, 'עכשיו הוא עובד.'), (3.3, 5.7, 'ואתה? אתה מחכה.'),
        (6.44, 9.15, 'וזה בערך מה שהגב שלך עושה בזמן הזה.'), (9.34, 11.62, 'תכירו את השותף החדש שלכם לשולחן.'),
        (11.74, 14.55, 'הוא מראה לך תרגיל, ואתה עושה אותו איתו.'), (14.64, 17.5, 'קצת צוואר, קצת כתפיים, קצת גב.'),
        (17.66, 18.84, 'ויש גם כאלה.'), (18.88, 20.7, 'אנחנו לא שופטים.'), (20.88, 21.98, 'המחשב סיים?'), (22.06, 23.35, 'גם אתה.')]
ENDCARD = [(23.45, 25.35, '1'), (25.35, END, '2')]
DING = 20.9

ov = V / 'overlays'; ov.mkdir(exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 1080, 'height': 1920})
    url = (V / 'overlay.html').as_uri()
    for i, (_, _, text) in enumerate(CAPS):
        pg.goto(f'{url}?cap={quote(text)}'); pg.wait_for_timeout(400)
        pg.screenshot(path=str(ov / f'cap{i:02d}.png'), omit_background=True)
    for _, _, stage in ENDCARD:
        pg.goto(f'{url}?end={stage}'); pg.wait_for_timeout(600)
        pg.screenshot(path=str(ov / f'end{stage}.png'), omit_background=True)
    b.close()

# a soft two-note ding, like the app's
ding = V / 'ding.wav'
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'lavfi', '-i',
                'aevalsrc=0.25*sin(2*PI*660*t)*exp(-6*t)*lt(t,0.6)+0.25*sin(2*PI*880*(t-0.12))*exp(-6*(t-0.12))*gt(t,0.12):d=0.8:s=48000',
                str(ding)], check=True)

layers = [(a, b, ov / f'cap{i:02d}.png') for i, (a, b, _) in enumerate(CAPS)] + [(a, b, ov / f'end{s}.png') for a, b, s in ENDCARD]
cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '24', '-i', str(V / 'frames' / 'f%04d.png'), '-i', TAKE, '-i', str(ding)]
for _, _, png in layers:
    cmd += ['-loop', '1', '-i', str(png)]
f, last = [], '0:v'
for k, (a, b, _) in enumerate(layers):
    f.append(f"[{last}][{k + 3}:v]overlay=0:0:enable='between(t,{a},{b})'[v{k}]")
    last = f'v{k}'
f.append(f'[2:a]adelay={int(DING * 1000)}|{int(DING * 1000)}[d];[1:a][d]amix=inputs=2:duration=first:normalize=0[a]')
cmd += ['-filter_complex', ';'.join(f), '-map', f'[{last}]', '-map', '[a]', '-t', str(END),
        '-c:v', 'libx264', '-crf', '17', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', str(OUT)]
subprocess.run(cmd, check=True)
print('OK', OUT)
