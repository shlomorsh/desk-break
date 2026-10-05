const { app, BrowserWindow, ipcMain, screen, Tray, Menu, globalShortcut, nativeImage } = require('electron');
const fs = require('fs');
const path = require('path');

const arg = name => process.argv.find(a => a.startsWith(name))?.split('=').slice(1).join('=');
const BUBBLE = 84, PEEK = 26, NEXT = 'Control+Alt+N', HIDE = 'Control+Alt+M';
let win, settings, tray;

function shoot(w, file, delay) {      // self-check helper: save a PNG of a window and quit
  setTimeout(async () => {
    console.log('[shot]', await w.webContents.executeJavaScript('document.body.className + " " + innerWidth + "x" + innerHeight'));
    fs.writeFileSync(file, (await w.capturePage()).toPNG()); app.quit();
  }, delay);
}

function gallery(hash, shot) {
  // shots render off-screen so they work even when the screen is locked or the window is covered
  const g = new BrowserWindow({ width: 1280, height: 900, backgroundColor: '#e9e4da', show: !shot,
    webPreferences: { offscreen: shot, backgroundThrottling: false } });
  if (shot) g.webContents.setFrameRate(30);
  g.loadFile('library/gallery.html', { hash });
  g.webContents.on('console-message', e => console.log('[page]', e.message));
  if (shot) setTimeout(async () => {
    const pages = await g.webContents.executeJavaScript('Math.ceil(document.body.scrollHeight / innerHeight)');
    for (let p = 0; p < pages; p++) {
      await g.webContents.executeJavaScript(`scrollTo(0, ${p} * innerHeight)`);
      await new Promise(r => setTimeout(r, 400));
      fs.writeFileSync(`${arg('--out') || 'sheet'}-${p}.png`, (await g.capturePage()).toPNG());
    }
    app.quit();
  }, 4000);
}

function openSettings(hash = '') {
  if (settings) return settings.focus();
  settings = new BrowserWindow({ width: 1180, height: 780, minWidth: 760, minHeight: 520, title: 'הגדרות', autoHideMenuBar: true,
    backgroundColor: '#efe2cb', icon: path.join(__dirname, 'app/icon.png'),
    webPreferences: { preload: path.join(__dirname, 'preload.js') } });
  settings.loadFile('app/settings.html', { hash });
  settings.webContents.on('console-message', e => console.log('[settings]', e.message));
  settings.on('closed', () => { settings = null; });
}

function area() { return screen.getDisplayMatching(win.getBounds()).workArea; }

// The window size is tracked here and re-applied on every move: on scaled displays Windows grows a
// transparent window a little each time only its position is set.
let size = [BUBBLE, BUBBLE];
const place = (x, y) => win.setBounds({ x: Math.round(x), y: Math.round(y), width: size[0], height: size[1] });
// where the window was last left, kept between runs (bottom-right corner, so any size fits)
const POS = () => path.join(app.getPath('userData'), 'position.json');
const remember = () => { const b = win.getBounds(); fs.writeFileSync(POS(), JSON.stringify({ right: b.x + b.width, bottom: b.y + b.height })); };
function recall(wa) {
  try { const p = JSON.parse(fs.readFileSync(POS())); return { x: Math.min(p.right, wa.x + wa.width) - BUBBLE, y: Math.min(p.bottom, wa.y + wa.height) - BUBBLE }; }
  catch { return { x: wa.x + wa.width - BUBBLE - 24, y: wa.y + wa.height - BUBBLE - 24 }; }
}

// resize keeping the corner nearest the screen edge in place; tells the page which side has more room
ipcMain.handle('mode', (e, w, h) => {
  const b = win.getBounds(), wa = area();
  const right = b.x + b.width / 2 > wa.x + wa.width / 2, bottom = b.y + b.height / 2 > wa.y + wa.height / 2;
  size = [w, h];
  const x = right ? b.x + b.width - w : b.x, y = bottom ? b.y + b.height - h : b.y;
  place(Math.max(wa.x, Math.min(x, wa.x + wa.width - w)), Math.max(wa.y, Math.min(y, wa.y + wa.height - h)));
  remember();
  return { right };
});
ipcMain.on('move', (e, x, y) => place(x, y));
// which screen edge the window was dropped on, if any
ipcMain.handle('drop', () => {
  remember();
  const b = win.getBounds(), wa = area();
  if (b.y + b.height > wa.y + wa.height - 6) return 'bottom';
  if (b.x < wa.x + 6) return 'left';
  if (b.x + b.width > wa.x + wa.width - 6) return 'right';
  return null;
});
// tuck the head into an edge, leaving a piece to click
ipcMain.on('tuck', (e, edge) => {
  const b = win.getBounds(), wa = area();
  if (edge === 'bottom') place(b.x, wa.y + wa.height - PEEK);
  if (edge === 'left') place(wa.x - b.width + PEEK, b.y);
  if (edge === 'right') place(wa.x + wa.width - PEEK, b.y);
});
ipcMain.handle('untuck', () => {
  const b = win.getBounds(), wa = area();
  place(Math.max(wa.x + 8, Math.min(b.x, wa.x + wa.width - b.width - 8)), Math.max(wa.y + 8, Math.min(b.y, wa.y + wa.height - b.height - 8)));
});
ipcMain.on('settings', () => openSettings());
ipcMain.on('quit', () => app.quit());
// hide everything; the tray icon or the shortcut brings it back
let told = false;
ipcMain.on('vanish', () => {
  win.hide();
  if (!told) { told = true; tray?.displayBalloon({ title: 'הדמות מוסתרת', content: 'לחיצה על האייקון כאן ליד השעון, או Ctrl+Alt+M, מחזירה אותה.' }); }
});
function hideOrShow() {
  if (win.isVisible()) return win.webContents.send('command', 'hide');
  win.showInactive(); win.setAlwaysOnTop(true, 'screen-saver');
}
ipcMain.handle('startup', (e, on) => {
  if (on !== undefined) app.setLoginItemSettings({ openAtLogin: on });
  return app.getLoginItemSettings().openAtLogin;
});

app.whenReady().then(() => {
  const g = arg('--gallery');
  if (g !== undefined) return gallery(g, arg('--shot') !== undefined);

  // `electron . --shot=card` (or bubble / settings) saves app-<name>.png off-screen and quits
  const shot = arg('--shot');
  if (shot?.startsWith('settings')) {        // --shot=settings or settings:<view>
    openSettings(shot.split(':')[1]); settings.setBounds({ width: 1180, height: 780 });
    return shoot(settings, `app-${shot.replace(':', '-')}.png`, 6000);
  }

  const wa = screen.getPrimaryDisplay().workArea;
  win = new BrowserWindow({ width: BUBBLE, height: BUBBLE, ...recall(wa),
    transparent: true, frame: false, resizable: false, hasShadow: false, skipTaskbar: true, show: !shot,
    icon: path.join(__dirname, 'app/icon.png'),
    webPreferences: { preload: path.join(__dirname, 'preload.js'), backgroundThrottling: false, offscreen: !!shot } });
  win.setAlwaysOnTop(true, 'screen-saver');
  win.loadFile('app/index.html', { hash: shot || '' });
  win.webContents.on('console-message', e => { if (shot) console.log('[page]', e.message); });
  if (shot) return shoot(win, `app-${shot}.png`, 4500);

  tray = new Tray(nativeImage.createFromPath(path.join(__dirname, 'app/icon.png')).resize({ width: 16, height: 16 }));
  tray.setToolTip('תרגיל בהמתנה');
  tray.setContextMenu(Menu.buildFromTemplate([
    { label: 'מזעור / החזרה', accelerator: HIDE, click: hideOrShow },
    { label: 'הסתרה מלאה', click: () => win.webContents.send('command', 'vanish') },
    { label: 'התרגיל הבא', accelerator: NEXT, click: () => win.webContents.send('command', 'next') },
    { label: 'הגדרות', click: openSettings },
    { type: 'separator' },
    { label: 'יציאה', click: () => app.quit() },
  ]));
  tray.on('click', hideOrShow);
  globalShortcut.register(NEXT, () => { if (!win.isVisible()) hideOrShow(); win.webContents.send('command', 'next'); });
  globalShortcut.register(HIDE, hideOrShow);
});
app.on('will-quit', () => globalShortcut.unregisterAll());
app.on('window-all-closed', () => app.quit());
