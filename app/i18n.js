// Interface words in Hebrew and English. In the HTML, text is marked with data-t (text), data-t-title,
// data-t-label (aria-label) and data-t-ph (placeholder); apply() fills them in for the chosen language.
export const WORDS = {
  he: {
    appName: 'תרגיל בהמתנה',
    figLabel: 'התרגיל. לחיצה פותחת פרטים, גרירה מזיזה',
    panelLabel: 'פרטי התרגיל', close: 'סגירת הפאנל', closeTitle: 'סגירה (Esc)',
    restart: 'להתחיל מחדש', restartTitle: 'מחדש (רווח)', less: 'פחות', more: 'יותר', slower: 'לאט יותר', faster: 'מהר יותר',
    prev: 'התרגיל הקודם', prevTitle: 'הקודם', next: 'התרגיל הבא',
    library: 'ספרייה', libraryTitle: 'ספרייה והגדרות', minimize: 'מזעור',
    hide: 'הסתרה', hideFull: 'הסתרה מלאה', hideTitle: 'הסתרה מלאה. מחזירים מהאייקון ליד השעון או Ctrl+Alt+M',
    shortcuts: 'קיצורי מקלדת', headLabel: 'החזרת הדמות. אפשר לגרור',
    noneTitle: 'לא נבחרו תרגילים', noneSub: 'בוחרים בספרייה', ofN: '{i} מתוך {n}', once: 'פעם אחת',
    side1: 'צד ראשון', side2: 'צד שני', time: 'זמן', reps: 'חזרות', perSide: ' לצד', sec: 'ש׳', secs: 'שניות',
    tempo: 'קצב (BPM)', speed: 'מהירות',
    keyNext: 'התרגיל הבא (מכל תוכנה)', keyHide: 'מזעור לראש / החזרה, גם אחרי הסתרה מלאה (מכל תוכנה)',
    keyEsc: 'סגירת הפאנל', keyArrows: 'הבא / הקודם, כשהפאנל פתוח', keySpace: 'התחלה מחדש של הספירה', space: 'רווח',
    // library & settings
    settingsTitle: 'ספרייה והגדרות', brandSub: 'ספריית תרגילים', navMine: 'הסט שלי', navAll: 'כל התרגילים',
    groupCats: 'קטגוריות', groupGeneral: 'כללי', navGeneral: 'הגדרות וקיצורים', search: 'חיפוש תרגיל',
    mineSub: 'התרגילים שהדמות תציע לך, לפי הסדר שבחרת בהגדרות', countSub: '{n} תרגילים · לחיצה על כרטיס לפרטים', plusHint: ', + מוסיף לסט',
    emptyMine: 'הסט ריק. בוחרים תרגילים מהקטגוריות בצד.', emptyNone: 'לא נמצאו תרגילים.',
    pickAdd: 'הוספה לסט', pickRemove: 'הסרה מהסט', inSet: 'בסט שלי ✓ (לחיצה מסירה)', addSet: 'הוספה לסט שלי',
    figH: 'גובה הדמות', figHText: 'כמה מקום הדמות תופסת על המסך.', headSize: 'גודל ראש העץ', headText: 'כשהדמות ממוזערת לראש קטן.',
    order: 'סדר התרגילים', orderText: 'מה קורה כשלוחצים "התרגיל הבא".', orderMix: 'מגוון: כל פעם אזור אחר', orderSeq: 'לפי הסדר', orderRandom: 'אקראי',
    general: 'כללי', sound: 'צליל קצר כשמסיימים תרגיל', startup: 'לפתוח אוטומטית כשהמחשב עולה',
    reset: 'איפוס', resetText: 'מחזיר את הסט הקצר לישיבה מול מחשב, ומבטל שינויי חזרות ומהירות.', resetBtn: 'איפוס לברירת המחדל',
    language: 'שפה', footer: 'ספרייה פתוחה (MIT) מתוך', about: 'על הכלי', privacy: 'פרטיות', terms: 'תנאי שימוש', a11y: 'נגישות',
    // tray (main process)
    trayTip: 'תרגיל בהמתנה', trayToggle: 'מזעור / החזרה', trayNext: 'התרגיל הבא', traySettings: 'הגדרות', trayAbout: 'על הכלי · parametric.co.il', trayQuit: 'יציאה',
    hiddenTitle: 'הדמות מוסתרת', hiddenText: 'לחיצה על האייקון כאן ליד השעון, או Ctrl+Alt+M, מחזירה אותה.',
  },
  en: {
    appName: 'Desk Break',
    figLabel: 'The exercise. Click for details, drag to move',
    panelLabel: 'Exercise details', close: 'Close the panel', closeTitle: 'Close (Esc)',
    restart: 'Start over', restartTitle: 'Start over (Space)', less: 'Less', more: 'More', slower: 'Slower', faster: 'Faster',
    prev: 'Previous exercise', prevTitle: 'Previous', next: 'Next exercise',
    library: 'Library', libraryTitle: 'Library & settings', minimize: 'Minimize',
    hide: 'Hide', hideFull: 'Hide completely', hideTitle: 'Hide completely. Bring it back from the tray icon or Ctrl+Alt+M',
    shortcuts: 'Keyboard shortcuts', headLabel: 'Bring the figure back. You can drag it',
    noneTitle: 'No exercises chosen', noneSub: 'Pick some in the library', ofN: '{i} of {n}', once: 'Once',
    side1: 'First side', side2: 'Second side', time: 'Time', reps: 'Reps', perSide: ' each side', sec: 's', secs: 'seconds',
    tempo: 'Tempo (BPM)', speed: 'Speed',
    keyNext: 'Next exercise (from any app)', keyHide: 'Minimize to the head / bring back, also after hiding (from any app)',
    keyEsc: 'Close the panel', keyArrows: 'Next / previous, while the panel is open', keySpace: 'Restart the count', space: 'Space',
    settingsTitle: 'Library & settings', brandSub: 'Exercise library', navMine: 'My set', navAll: 'All exercises',
    groupCats: 'Categories', groupGeneral: 'General', navGeneral: 'Settings & shortcuts', search: 'Search exercises',
    mineSub: 'The exercises the figure will offer you, in the order you chose in settings', countSub: '{n} exercises · click a card for details', plusHint: ', + adds it to your set',
    emptyMine: 'Your set is empty. Pick exercises from the categories on the side.', emptyNone: 'No exercises found.',
    pickAdd: 'Add to my set', pickRemove: 'Remove from my set', inSet: 'In my set ✓ (click to remove)', addSet: 'Add to my set',
    figH: 'Figure height', figHText: 'How much of the screen the figure takes.', headSize: 'Wooden head size', headText: 'When the figure is minimized to a small head.',
    order: 'Exercise order', orderText: 'What happens when you click "Next exercise".', orderMix: 'Mixed: a different body area each time', orderSeq: 'In order', orderRandom: 'Random',
    general: 'General', sound: 'Short chime when an exercise is done', startup: 'Open automatically when the computer starts',
    reset: 'Reset', resetText: 'Brings back the short set for people at a desk and clears your rep and speed changes.', resetBtn: 'Reset to default',
    language: 'Language', footer: 'Open library (MIT) from', about: 'About', privacy: 'Privacy', terms: 'Terms', a11y: 'Accessibility',
    trayTip: 'Desk Break', trayToggle: 'Minimize / bring back', trayNext: 'Next exercise', traySettings: 'Settings', trayAbout: 'About · parametric.co.il', trayQuit: 'Quit',
    hiddenTitle: 'The figure is hidden', hiddenText: 'Click this icon by the clock, or press Ctrl+Alt+M, to bring it back.',
  },
};

// ?lang=en in the address wins (web pages), then the saved choice, then the computer's language
export function langOf(settings) {
  const q = new URLSearchParams(location.search).get('lang');
  if (q in WORDS) return q;
  if (settings?.lang in WORDS) return settings.lang;
  return (navigator.language || '').toLowerCase().startsWith('he') ? 'he' : 'en';
}

export const tr = (lang, key, vars = {}) =>
  (WORDS[lang]?.[key] ?? WORDS.he[key] ?? key).replace(/\{(\w+)\}/g, (_, k) => vars[k]);

export function apply(lang, root = document) {
  document.documentElement.lang = lang;
  document.documentElement.dir = lang === 'he' ? 'rtl' : 'ltr';
  for (const [attr, set] of [['t', (el, v) => { el.textContent = v; }], ['tTitle', (el, v) => { el.title = v; }],
    ['tLabel', (el, v) => el.setAttribute('aria-label', v)], ['tPh', (el, v) => { el.placeholder = v; }]])
    for (const el of root.querySelectorAll(`[data-${attr.replace(/[A-Z]/g, c => '-' + c.toLowerCase())}]`))
      set(el, tr(lang, el.dataset[attr]));
}

// an exercise's texts in the chosen language (English falls back to Hebrew where a translation is missing)
export const exText = (e, lang) => lang === 'en'
  ? { name: e.en || e.he, amount: e.amount_en || e.amount, steps: e.steps_en || e.steps }
  : { name: e.he, amount: e.amount, steps: e.steps };
export const catName = (c, lang) => (lang === 'en' ? c.en : c.he);

export const shortcuts = lang => [
  ['Ctrl + Alt + N', tr(lang, 'keyNext')], ['Ctrl + Alt + M', tr(lang, 'keyHide')], ['Esc', tr(lang, 'keyEsc')],
  ['← / →', tr(lang, 'keyArrows')], [tr(lang, 'space'), tr(lang, 'keySpace')],
];
