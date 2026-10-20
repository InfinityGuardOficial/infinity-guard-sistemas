// Rota do Milhão para Windows: abre o app privado no claude.ai com o login do dono
// e dispara os avisos dos turnos mesmo com a janela fechada (fica na bandeja).
const { app, BrowserWindow, Tray, Menu, Notification, shell, ipcMain, session } = require("electron");
const path = require("path");
const fs = require("fs");

const URL_APP = "https://claude.ai/artifact/V2LctZDwDPV4Ly9S8P8KJx";
const HOSTS_LOGIN = [/(^|\.)claude\.ai$/, /(^|\.)anthropic\.com$/, /(^|\.)google\.com$/, /(^|\.)apple\.com$/, /(^|\.)claudeusercontent\.com$/];
const PADRAO = {
  manha: { nome: "Antes do trabalho", ini: "06:00", dias: [1, 2, 3, 4, 5], texto: "Zerar o WhatsApp, ler o radar da equipe e 1 story." },
  almoco: { nome: "Almoço", ini: "12:10", dias: [1, 2, 3, 4, 5], texto: "Missão de conteúdo do dia." },
  noite: { nome: "Noite", ini: "20:00", dias: [1, 2, 3, 4, 5], texto: "Módulo da semana e números do dia no Placar." },
  sabado: { nome: "Bloco de sábado", ini: "09:00", dias: [6], texto: "Pacote da semana no Planejador e prova do módulo." },
  domingo: { nome: "Revisão de domingo", ini: "19:00", dias: [0], texto: "15 minutos de revisão: execução, meta e 1 decisão." },
};

let win = null, tray = null, sair = false;
const arquivoCfg = () => path.join(app.getPath("userData"), "horarios.json");
function lerCfg() { try { return Object.assign({}, PADRAO, JSON.parse(fs.readFileSync(arquivoCfg(), "utf8"))); } catch (e) { return JSON.parse(JSON.stringify(PADRAO)); } }
function gravarCfg(c) { fs.mkdirSync(path.dirname(arquivoCfg()), { recursive: true }); fs.writeFileSync(arquivoCfg(), JSON.stringify(c, null, 2)); }
const hostOk = (u) => { try { const h = new URL(u).hostname; return HOSTS_LOGIN.some((r) => r.test(h)); } catch (e) { return false; } };

if (!app.requestSingleInstanceLock()) { app.quit(); }
app.on("second-instance", () => mostrar());
app.setAppUserModelId("br.com.infinityguard.rotadomilhao");

function mostrar() { if (!win) criarJanela(); win.show(); if (win.isMinimized()) win.restore(); win.focus(); }

function criarJanela() {
  win = new BrowserWindow({
    width: 1240, height: 880, minWidth: 380, title: "Rota do Milhão",
    icon: path.join(__dirname, "icon.png"), autoHideMenuBar: true, backgroundColor: "#001121",
    webPreferences: { partition: "persist:rota-do-milhao", contextIsolation: true, sandbox: true },
  });
  win.loadURL(URL_APP);
  win.webContents.setWindowOpenHandler(({ url }) => {
    if (hostOk(url)) return { action: "allow" };
    shell.openExternal(url); return { action: "deny" };
  });
  win.webContents.on("will-navigate", (e, url) => { if (!hostOk(url)) { e.preventDefault(); shell.openExternal(url); } });
  win.on("close", (e) => { if (!sair) { e.preventDefault(); win.hide(); avisar("O Rota do Milhão continua na bandeja", "Os avisos dos turnos seguem ligados."); } });
}

function janelaHorarios() {
  const w = new BrowserWindow({ width: 460, height: 640, title: "Horários dos turnos", icon: path.join(__dirname, "icon.png"), autoHideMenuBar: true, webPreferences: { preload: path.join(__dirname, "preload.js"), contextIsolation: true, sandbox: true } });
  w.loadFile(path.join(__dirname, "horarios.html"));
}
ipcMain.handle("cfg:ler", () => lerCfg());
ipcMain.handle("cfg:gravar", (_e, c) => { gravarCfg(c); return true; });

function avisar(titulo, corpo) { if (!Notification.isSupported()) return; const n = new Notification({ title: titulo, body: corpo, icon: path.join(__dirname, "icon.png") }); n.on("click", mostrar); n.show(); }

const disparados = new Set();
function verificarTurnos() {
  const agora = new Date(), dia = agora.getDay(), min = agora.getHours() * 60 + agora.getMinutes();
  const chaveDia = agora.toDateString(); const cfg = lerCfg();
  for (const [id, s] of Object.entries(cfg)) {
    if (!s || !Array.isArray(s.dias) || !s.dias.includes(dia) || !/^\d\d:\d\d$/.test(s.ini || "")) continue;
    const [h, m] = s.ini.split(":").map(Number), ini = h * 60 + m;
    if (min >= ini - 5 && min < ini && !disparados.has(chaveDia + id + "pre")) { disparados.add(chaveDia + id + "pre"); avisar(`${s.nome} em 5 minutos`, s.texto); }
    if (min >= ini && min < ini + 3 && !disparados.has(chaveDia + id)) { disparados.add(chaveDia + id); avisar(`Começou: ${s.nome}`, s.texto + " Abra o app e coloque a prova."); }
  }
}

function montarBandeja() {
  tray = new Tray(path.join(__dirname, "icon.png"));
  tray.setToolTip("Rota do Milhão");
  const menu = () => Menu.buildFromTemplate([
    { label: "Abrir o Rota do Milhão", click: mostrar },
    { label: "Horários dos turnos", click: janelaHorarios },
    { label: "Iniciar com o Windows", type: "checkbox", checked: app.getLoginItemSettings().openAtLogin, click: (i) => app.setLoginItemSettings({ openAtLogin: i.checked, args: ["--oculto"] }) },
    { type: "separator" },
    { label: "Sair", click: () => { sair = true; app.quit(); } },
  ]);
  tray.setContextMenu(menu());
  tray.on("click", mostrar);
}

app.whenReady().then(() => {
  session.fromPartition("persist:rota-do-milhao").setPermissionRequestHandler((_wc, perm, cb) => cb(["notifications", "clipboard-sanitized-write", "fullscreen"].includes(perm)));
  if (!fs.existsSync(arquivoCfg())) gravarCfg(PADRAO);
  montarBandeja();
  criarJanela();
  if (process.argv.includes("--oculto")) win.hide();
  verificarTurnos(); setInterval(verificarTurnos, 30 * 1000);
});
app.on("before-quit", () => { sair = true; });
app.on("window-all-closed", (e) => { if (!sair) e.preventDefault(); });
