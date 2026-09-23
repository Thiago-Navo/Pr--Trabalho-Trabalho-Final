/**
 * Registra o service worker e controla o botão "Instalar app" do topbar.
 *
 * Funciona assim:
 * 1. Registra o sw.js (permite instalação + cache de estáticos).
 * 2. O Chrome/Edge disparam o evento "beforeinstallprompt" quando acham
 *    que o app é instalável; guardamos esse evento e mostramos nosso
 *    próprio botão em vez do mini-infobar padrão do navegador.
 * 3. Ao clicar no botão, chamamos prompt() no evento guardado — é o
 *    mesmo diálogo nativo que aparece ao "instalar" o YouTube.
 * 4. Se o app já estiver rodando em modo instalado (standalone), ou o
 *    navegador não suportar instalação (ex: Safari/iOS), escondemos o
 *    botão.
 */

(function () {
  if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => {
      navigator.serviceWorker.register("/sw.js").catch((erro) => {
        console.warn("Não foi possível registrar o service worker:", erro);
      });
    });
  }

  let eventoInstalacao = null;
  const btn = document.getElementById("btnInstalarApp");
  if (!btn) return;

  const emModoStandalone =
    window.matchMedia("(display-mode: standalone)").matches ||
    window.navigator.standalone === true;

  if (emModoStandalone) {
    btn.hidden = true;
  }

  window.addEventListener("beforeinstallprompt", (evento) => {
    evento.preventDefault();
    eventoInstalacao = evento;
    if (!emModoStandalone) btn.hidden = false;
  });

  btn.addEventListener("click", async () => {
    if (!eventoInstalacao) return;
    btn.hidden = true;
    eventoInstalacao.prompt();
    await eventoInstalacao.userChoice;
    eventoInstalacao = null;
  });

  window.addEventListener("appinstalled", () => {
    btn.hidden = true;
    eventoInstalacao = null;
  });
})();
