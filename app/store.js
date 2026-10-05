// Settings shared by the floating window and the settings window (both read the same localStorage).
const KEY = 'desk-settings';
// figure window: height from the slider, width follows; the panel adds PANEL_W next to it
export const figureSize = s => [Math.round(s.figH * 0.8), s.figH];
export const PANEL_W = 310, PANEL_H = 580;
export const LIMITS = { figH: [180, 640], head: [48, 160] };

// a short desk-break set for people who sit at a computer all day
export const DESK_SET = ['neck-side-tilt', 'chin-tuck', 'shoulder-rolls-back', 'chest-opener-clasp', 'wrist-circles',
  'wrist-flexor-stretch', 'overhead-reach', 'standing-side-bend-reach', 'standing-trunk-twist', 'standing-cat-cow',
  'posture-reset', 'march-in-place', 'calf-raise', 'standing-hip-circles', 'chair-figure-four'];

// on = ids switched on, custom = { id: { reps | seconds, speed } } per-exercise changes
const DEFAULTS = { on: DESK_SET, order: 'mix', figH: 320, head: 84, custom: {}, sound: true };

export function load() {
  try { return { ...DEFAULTS, ...JSON.parse(localStorage.getItem(KEY)) }; } catch { return { ...DEFAULTS }; }
}
export function save(s) {
  try { localStorage.setItem(KEY, JSON.stringify(s)); } catch {}
}

// How much of an exercise: read from its Hebrew "amount" ("10 פעמים", "20 שניות לכל צד", "1 דקה"),
// then the user's changes on top. speed 1 = as written; for dances speed = chosen bpm / written bpm.
export function dose(ex, custom = {}) {
  const a = ex.amount || '', n = +(a.match(/\d+/)?.[0] || 0);
  const seconds = /שני/.test(a) ? n : /דק/.test(a) ? n * 60 : 0;
  const d = ex.once ? { once: true } : seconds ? { seconds } : { reps: n || 10 };
  d.perSide = /לכל (צד|רגל|יד|כיוון)/.test(a);
  d.speed = 1;
  return { ...d, ...custom };
}

// The exercises in the order the "next" button walks through them.
// mix = one from each category in turn, seq = category by category, random = shuffled.
export function playlist(lib, s) {
  const on = new Set(s.on);
  const groups = lib.categories.map(c => lib.exercises.filter(e => e.category === c.id && on.has(e.id)));
  if (s.order === 'seq') return groups.flat();
  if (s.order === 'random') {
    const all = groups.flat();
    for (let i = all.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [all[i], all[j]] = [all[j], all[i]]; }
    return all;
  }
  const out = [], total = groups.flat().length;
  for (let i = 0; out.length < total; i++) for (const g of groups) if (g[i]) out.push(g[i]);
  return out;
}

export const SHORTCUTS = [
  ['Ctrl + Alt + N', 'התרגיל הבא (מכל תוכנה)'],
  ['Ctrl + Alt + M', 'מזעור לראש / החזרה, גם אחרי הסתרה מלאה (מכל תוכנה)'],
  ['Esc', 'סגירת הפאנל'],
  ['← / →', 'הבא / הקודם, כשהפאנל פתוח'],
  ['רווח', 'התחלה מחדש של הספירה'],
];
