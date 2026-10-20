const { contextBridge, ipcRenderer } = require("electron");
contextBridge.exposeInMainWorld("cfg", { ler: () => ipcRenderer.invoke("cfg:ler"), gravar: (c) => ipcRenderer.invoke("cfg:gravar", c) });
