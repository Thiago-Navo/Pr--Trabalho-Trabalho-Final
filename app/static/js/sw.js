/**
 * Service Worker do Techstock.
 * Responsável por: (1) permitir que o navegador ofereça a opção
 * "Instalar app" / "Adicionar à tela inicial", e (2) cachear os
 * arquivos estáticos (CSS/JS/ícones) para abrir mais rápido e
 * funcionar parcialmente offline.
 *
 * Não cacheamos páginas HTML (templates) porque elas têm dados
 * dinâmicos (estoque, usuário logado etc.) — só os arquivos
 * estáticos que não mudam de usuário para usuário.
 */

const CACHE_NAME = "techstock-cache-v1";

const ARQUIVOS_ESTATICOS = [
  "/static/css/style.css",
  "/static/js/app.js",
  "/static/js/nav.js",
  "/static/js/playlist.js",
  "/static/img/icons/icon-192.png",
  "/static/img/icons/icon-512.png",
  "/static/img/covers/default-cover.svg",
  "/static/manifest.json",
];

self.addEventListener("install", (evento) => {
  evento.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ARQUIVOS_ESTATICOS))
  );
  self.skipWaiting();
});

self.addEventListener("activate", (evento) => {
  evento.waitUntil(
    caches.keys().then((nomes) =>
      Promise.all(
        nomes
          .filter((nome) => nome !== CACHE_NAME)
          .map((nome) => caches.delete(nome))
      )
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (evento) => {
  const url = new URL(evento.request.url);

  // Só intercepta pedidos de arquivos estáticos (mesma origem).
  // Páginas (dashboard, produtos, login...) sempre vão direto pra rede,
  // pra nunca mostrar dado de estoque desatualizado.
  const ehEstatico = url.origin === self.location.origin && url.pathname.startsWith("/static/");

  if (!ehEstatico) return;

  evento.respondWith(
    caches.match(evento.request).then((respostaCache) => {
      if (respostaCache) return respostaCache;

      return fetch(evento.request).then((respostaRede) => {
        const clone = respostaRede.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(evento.request, clone));
        return respostaRede;
      });
    })
  );
});
