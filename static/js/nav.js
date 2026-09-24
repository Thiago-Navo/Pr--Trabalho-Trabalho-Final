/* ==========================================================================
   nav.js — navegação "suave" entre as páginas internas do sistema
   ==========================================================================
   Este app é servido pelo Flask como páginas separadas (cada link do menu
   é um GET normal, cada formulário dá um POST que recarrega a página).
   Isso significa que, sem ajuda, o navegador destrói e recria a tag
   <audio> a cada clique — a música para e volta para o início toda vez.

   Aqui a gente intercepta os cliques em links internos e os envios de
   formulário, busca a página nova em segundo plano (fetch) e troca só o
   conteúdo principal e a busca do topo. A barra lateral — e o player de
   música dentro dela — nunca é recriada, então o áudio continua tocando
   de onde estava. Se o usuário apertar pausa, ele continua pausado; a
   música só troca de faixa nas trocas normais (fim da faixa, botão
   próxima/anterior).

   Páginas que não usam esse layout (login, cadastro sem sessão) não têm
   o player mesmo, então caem de volta para uma troca de página completa.
   ========================================================================== */

(function () {
  const SELETOR_CONTEUDO = "#app-content";
  const SELETOR_BUSCA = "#app-search";
  const SELETOR_SCRIPTS = "#app-scripts";

  let carregando = false;

  function ehLinkInterno(link) {
    if (!link || !link.getAttribute("href")) return false;
    const href = link.getAttribute("href");
    if (href.startsWith("#")) return false;
    if (/^(mailto:|tel:|javascript:)/i.test(href)) return false;
    if (link.target && link.target !== "_self") return false;
    if (link.hasAttribute("download")) return false;
    if (link.hasAttribute("data-full-reload")) return false;
    let url;
    try {
      url = new URL(link.href, window.location.href);
    } catch (erro) {
      return false;
    }
    return url.origin === window.location.origin;
  }

  function mostrarProgresso(ativo) {
    document.documentElement.classList.toggle("nav-carregando", ativo);
  }

  function extrairEExecutarScripts(container) {
    if (!container) return;
    Array.from(container.querySelectorAll("script")).forEach((antigo) => {
      const novo = document.createElement("script");
      Array.from(antigo.attributes).forEach((attr) => novo.setAttribute(attr.name, attr.value));
      if (antigo.src) {
        novo.src = antigo.src;
      } else {
        // Páginas diferentes declaram "const"/"let" com os mesmos nomes
        // (ex.: "selProduto" existe em várias telas). Um <script> comum
        // reexecutado compartilharia o mesmo escopo do topo e a segunda
        // execução quebraria com "identifier already declared". Isolando
        // em uma função, cada execução fica independente.
        novo.textContent = "(function () {\n" + antigo.textContent + "\n})();";
      }
      antigo.replaceWith(novo);
    });
  }

  function atualizarSidebarAtiva(url) {
    const caminho = new URL(url, window.location.href).pathname;
    document.querySelectorAll(".sidebar-nav a[href]").forEach((a) => {
      let alvo;
      try {
        alvo = new URL(a.href, window.location.href).pathname;
      } catch (erro) {
        return;
      }
      a.classList.toggle("active", alvo === caminho);
    });
  }

  function substituirDocumentoCompleto(html, url) {
    // Usado quando a página de destino não tem o mesmo layout (login,
    // cadastro sem sessão, etc.) — troca o documento inteiro sem tentar
    // preservar a barra lateral, já que ela nem existe lá.
    document.open();
    document.write(html);
    document.close();
    history.replaceState({ ajaxNav: false }, "", url);
  }

  async function irPara(url, opcoes) {
    const { push, method, body } = Object.assign({ push: true, method: "GET", body: null }, opcoes);
    if (carregando) return;
    carregando = true;
    mostrarProgresso(true);

    try {
      const resposta = await fetch(url, {
        method,
        body,
        credentials: "same-origin",
        headers: { "X-Requested-With": "fetch-nav" },
      });
      const html = await resposta.text();
      const urlFinal = resposta.url || url;
      const doc = new DOMParser().parseFromString(html, "text/html");

      const novoConteudo = doc.querySelector(SELETOR_CONTEUDO);
      const conteudoAtual = document.querySelector(SELETOR_CONTEUDO);

      if (!novoConteudo || !conteudoAtual) {
        substituirDocumentoCompleto(html, urlFinal);
        return;
      }

      document.title = doc.title;

      const novaBusca = doc.querySelector(SELETOR_BUSCA);
      const buscaAtual = document.querySelector(SELETOR_BUSCA);
      if (novaBusca && buscaAtual) buscaAtual.innerHTML = novaBusca.innerHTML;

      if (typeof window.limparGraficos === "function") window.limparGraficos();
      if (typeof window.limparModais === "function") window.limparModais();

      conteudoAtual.innerHTML = novoConteudo.innerHTML;

      const scriptsAtuais = document.querySelector(SELETOR_SCRIPTS);
      const novosScripts = doc.querySelector(SELETOR_SCRIPTS);
      if (scriptsAtuais) scriptsAtuais.innerHTML = novosScripts ? novosScripts.innerHTML : "";

      extrairEExecutarScripts(conteudoAtual);
      extrairEExecutarScripts(scriptsAtuais);

      atualizarSidebarAtiva(urlFinal);

      if (push) {
        history.pushState({ ajaxNav: true }, "", urlFinal);
      } else {
        history.replaceState({ ajaxNav: true }, "", urlFinal);
      }

      window.scrollTo(0, 0);
      document.querySelector(".sidebar")?.classList.remove("is-open");
    } catch (erro) {
      // Falha de rede ou algo inesperado: cai para navegação normal do
      // navegador. A música pode parar nesse caso raro, mas o app
      // continua funcionando.
      window.location.href = url;
    } finally {
      carregando = false;
      mostrarProgresso(false);
    }
  }

  document.addEventListener("click", (e) => {
    if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    const link = e.target.closest("a[href]");
    if (!link || !ehLinkInterno(link)) return;
    e.preventDefault();
    irPara(link.href, { push: true });
  });

  document.addEventListener("submit", (e) => {
    if (e.defaultPrevented) return; // ex.: onsubmit="return confirm(...)" cancelado
    const form = e.target.closest("form");
    if (!form || form.hasAttribute("data-full-reload")) return;

    let url;
    try {
      url = new URL(form.getAttribute("action") || window.location.href, window.location.href);
    } catch (erro) {
      return;
    }
    if (url.origin !== window.location.origin) return;

    e.preventDefault();
    const metodo = (form.getAttribute("method") || "GET").toUpperCase();

    if (metodo === "GET") {
      url.search = new URLSearchParams(new FormData(form)).toString();
      irPara(url.href, { push: true });
    } else {
      irPara(url.href, { push: true, method: "POST", body: new FormData(form) });
    }
  });

  window.addEventListener("popstate", () => {
    irPara(window.location.href, { push: false });
  });

  // Estado inicial: garante que o botão "voltar" do navegador já funcione
  // corretamente na primeira navegação suave feita pelo usuário.
  history.replaceState({ ajaxNav: true }, "", window.location.href);
})();
