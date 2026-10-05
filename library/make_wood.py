# Generates wood.png: light natural maple/birch grain, tileable, grain running along V (along each limb).
# Run with any Python that has numpy + Pillow:  python library/make_wood.py
import numpy as np
from PIL import Image

N = 1024
rng = np.random.default_rng(11)


def noise(cy, cx):
    """Smooth tileable value noise, cy x cx cells over the image."""
    g = rng.random((cy + 1, cx + 1)); g[-1] = g[0]; g[:, -1] = g[:, 0]
    y = np.linspace(0, cy, N, endpoint=False); x = np.linspace(0, cx, N, endpoint=False)
    yi, xi = y.astype(int), x.astype(int)
    fy, fx = (y - yi)[:, None], (x - xi)[None, :]
    fy, fx = fy * fy * (3 - 2 * fy), fx * fx * (3 - 2 * fx)
    a, b = g[yi][:, xi], g[yi][:, xi + 1]
    c, d = g[yi + 1][:, xi], g[yi + 1][:, xi + 1]
    return a * (1 - fx) * (1 - fy) + b * fx * (1 - fy) + c * (1 - fx) * fy + d * fx * fy


x = np.linspace(0, 1, N, endpoint=False)[None, :]
phase = x * 26 + 0.9 * noise(2, 3) + 2.2 * noise(1, 9) + 0.08 * noise(40, 8)   # mostly straight, uneven spacing
ring = phase % 1.0
strength = 0.35 + 0.65 * noise(1, 31)                             # some lines strong, some faint
late = np.exp(-((ring - 0.5) / (0.025 + 0.03 * noise(3, 17))) ** 2) * strength
fibre = noise(5, 380) * 0.55 + noise(2, 700) * 0.45                # long thin fibres
tone = noise(2, 3)                                                 # big soft colour drift

light = np.array([242, 222, 186]) / 255                           # pale maple
dark = np.array([196, 152, 98]) / 255
t = np.clip(0.7 * late + 0.4 * (fibre - 0.5) + 0.3 * (tone - 0.5) + 0.16, 0, 1)[..., None]
img = light * (1 - t) + dark * t
Image.fromarray((img * 255).astype(np.uint8)).save(__file__.replace('make_wood.py', 'wood.png'))
print('wood.png')
