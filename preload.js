const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('desk', {
  mode: (w, h) => ipcRenderer.invoke('mode', w, h),
  move: (x, y) => ipcRenderer.send('move', x, y),
  drop: () => ipcRenderer.invoke('drop'),
  tuck: edge => ipcRenderer.send('tuck', edge),
  untuck: () => ipcRenderer.invoke('untuck'),
  settings: () => ipcRenderer.send('settings'),
  quit: () => ipcRenderer.send('quit'),
  about: () => ipcRenderer.send('about'),
  vanish: () => ipcRenderer.send('vanish'),
  lang: l => ipcRenderer.send('lang', l),
  startup: on => ipcRenderer.invoke('startup', on),
  onCommand: fn => ipcRenderer.on('command', (e, c) => fn(c)),
});
