/* ==========================================================================
   app.js — comportamento comum do sistema (vanilla JS, sem jQuery)
   ========================================================================== */

/* ---- Tema claro/escuro ---- */
const registroGraficos = {}; // canvasId -> { tipo, dados, instancia }

function corDoTema(variavelCss, fallback) {
  const valor = getComputedStyle(document.documentElement).getPropertyValue(variavelCss).trim();
  return valor || fallback;
}

function rerenderizarGraficos() {
  Object.keys(registroGraficos).forEach((canvasId) => {
    const registro = registroGraficos[canvasId];
    if (!registro) return;
    if (registro.instancia) registro.instancia.destroy();
    if (registro.tipo === "movimentacoes") {
      registro.instancia = criarGraficoMovimentacoes(canvasId, registro.dados);
    } else if (registro.tipo === "categorias") {
      registro.instancia = criarGraficoCategorias(canvasId, registro.dados);
    }
  });
}

function limparGraficos() {
  // Chamado pelo nav.js antes de trocar o conteúdo da página: destrói os
  // gráficos da tela que está saindo (os <canvas> vão sumir do DOM) para
  // não vazar instâncias do Chart.js nem tentar redesenhar algo que não
  // existe mais quando o tema mudar.
  Object.keys(registroGraficos).forEach((canvasId) => {
    const registro = registroGraficos[canvasId];
    if (registro && registro.instancia) registro.instancia.destroy();
    delete registroGraficos[canvasId];
  });
}

function limparModais() {
  // Também chamado pelo nav.js antes de trocar o conteúdo da página.
  // Os modais de edição/criação (produto, rua, etc.) vivem dentro de
  // #app-content. Se um formulário é enviado com o modal ainda aberto,
  // o nav.js troca o HTML de #app-content por baixo do modal — e o
  // Bootstrap nunca recebe o evento de fechamento dele. O resultado é
  // um ".modal-backdrop" (o fundo escurecido) que fica grudado na tela
  // para sempre, e a classe "modal-open" no <body>, que trava o scroll.
  // Isso é o que fazia a tela "travar"/"bugar" depois de editar algo.
  document.querySelectorAll(".modal.show").forEach((modalEl) => {
    const instancia = typeof bootstrap !== "undefined" ? bootstrap.Modal.getInstance(modalEl) : null;
    if (instancia) instancia.dispose();
    modalEl.classList.remove("show");
    modalEl.style.display = "none";
    modalEl.setAttribute("aria-hidden", "true");
    modalEl.removeAttribute("aria-modal");
    modalEl.removeAttribute("role");
  });
  document.querySelectorAll(".modal-backdrop").forEach((el) => el.remove());
  document.body.classList.remove("modal-open");
  document.body.style.removeProperty("overflow");
  document.body.style.removeProperty("padding-right");
}

function initTema() {
  const btn = document.getElementById("btnTema");
  const icone = document.getElementById("iconeTema");
  if (!btn) return;

  function aplicarIcone() {
    const escuro = document.documentElement.getAttribute("data-theme") === "dark";
    if (icone) {
      icone.classList.toggle("bi-moon-stars", !escuro);
      icone.classList.toggle("bi-sun", escuro);
    }
  }

  aplicarIcone();

  btn.addEventListener("click", () => {
    const atual = document.documentElement.getAttribute("data-theme") === "dark" ? "dark" : "light";
    const novo = atual === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", novo);
    // data-bs-theme aciona o modo escuro nativo do Bootstrap (modais,
    // dropdowns, inputs, etc.) — sem isso, esses componentes ficam claros
    // mesmo com o resto da página no escuro.
    document.documentElement.setAttribute("data-bs-theme", novo);
    localStorage.setItem("estoque-tema", novo);
    aplicarIcone();
    // Chart.js não recalcula cores sozinho: recriamos os gráficos da
    // página (se houver) para eles também acompanharem o tema novo.
    rerenderizarGraficos();
  });
}

/* ---- Música de fundo: playlist com capa giratória, anterior/próxima ---- */
function initMusica() {
  const btnPlayPause = document.getElementById("btnMusica");
  const btnAnterior = document.getElementById("btnAnterior");
  const btnProxima = document.getElementById("btnProxima");
  const btnVolumeBaixo = document.getElementById("btnVolumeBaixo");
  const btnVolumeAlto = document.getElementById("btnVolumeAlto");
  const volumeFill = document.getElementById("volumeFill");
  const audio = document.getElementById("audioFundo");
  const icone = document.getElementById("iconeMusica");
  const capa = document.getElementById("capaMusica");
  const tituloEl = document.getElementById("tituloMusica");
  const artistaEl = document.getElementById("artistaMusica");
  if (!btnPlayPause || !audio) return;

  const lista = typeof PLAYLIST !== "undefined" ? PLAYLIST : [];
  const capaPadrao = capa ? capa.getAttribute("src") : "";
  let indice = 0;
  let historico = [];

  function semFaixas() {
    return lista.length === 0;
  }

  function salvarEstadoPlayer() {
    if (semFaixas()) return;
    try {
      localStorage.setItem("estoque-player-indice", String(indice));
      localStorage.setItem("estoque-player-tocando", String(!audio.paused));
      localStorage.setItem("estoque-player-tempo", String(Math.floor(audio.currentTime || 0)));
    } catch (_) {}
  }

  function indiceAleatorio(evitar) {
    if (lista.length <= 1) return 0;
    let novo;
    do {
      novo = Math.floor(Math.random() * lista.length);
    } while (novo === evitar);
    return novo;
  }

  function marcarGirando(girando) {
    if (capa) capa.classList.toggle("tocando", girando);
  }

  function atualizarIconePlay(tocando) {
    if (!icone) return;
    icone.classList.toggle("bi-play-fill", !tocando);
    icone.classList.toggle("bi-pause-fill", tocando);
  }

  /* ---- Volume: passos de 10%, salvo em localStorage por navegador ---- */
  function aplicarVolume(v) {
    const volume = Math.min(1, Math.max(0, v));
    audio.volume = volume;
    localStorage.setItem("estoque-volume", String(volume));
    if (volumeFill) volumeFill.style.width = `${Math.round(volume * 100)}%`;
    if (btnVolumeBaixo) btnVolumeBaixo.disabled = volume <= 0;
    if (btnVolumeAlto) btnVolumeAlto.disabled = volume >= 1;
  }

  function diminuirVolume() {
    aplicarVolume(audio.volume - 0.1);
  }

  function aumentarVolume() {
    aplicarVolume(audio.volume + 0.1);
  }

  const volumeSalvo = parseFloat(localStorage.getItem("estoque-volume"));
  aplicarVolume(Number.isFinite(volumeSalvo) ? volumeSalvo : 0.6);

  if (btnVolumeBaixo) btnVolumeBaixo.addEventListener("click", diminuirVolume);
  if (btnVolumeAlto) btnVolumeAlto.addEventListener("click", aumentarVolume);

  function carregarFaixa(i, autoPlay) {
    if (semFaixas()) {
      tituloEl.textContent = "Nenhuma faixa";
      artistaEl.textContent = "Adicione músicas em playlist.js";
      return;
    }
    indice = ((i % lista.length) + lista.length) % lista.length;
    const faixa = lista[indice];

    // Só troca o src do áudio se for uma URL diferente, para evitar quebrar buffer existente
    if (audio.getAttribute("src") !== faixa.src) {
      audio.src = faixa.src;
    }
    tituloEl.textContent = faixa.titulo || "Faixa sem nome";
    artistaEl.textContent = faixa.artista || "Artista desconhecido";
    if (capa) capa.src = faixa.capa && faixa.capa.trim() ? faixa.capa : capaPadrao;

    salvarEstadoPlayer();

    if (autoPlay) {
      audio.play().then(() => {
        atualizarIconePlay(true);
        marcarGirando(true);
        salvarEstadoPlayer();
      }).catch(() => {
        atualizarIconePlay(false);
        marcarGirando(false);
      });
    }
  }

  function tocarPausar() {
    if (semFaixas()) return;
    if (!audio.src) carregarFaixa(indice, false);

    if (audio.paused) {
      audio.play().then(() => {
        atualizarIconePlay(true);
        marcarGirando(true);
        salvarEstadoPlayer();
      }).catch(() => {});
    } else {
      audio.pause();
      atualizarIconePlay(false);
      marcarGirando(false);
      salvarEstadoPlayer();
    }
  }

  function proximaFaixa() {
    if (semFaixas()) return;
    const tocando = !audio.paused;
    historico.push(indice);
    carregarFaixa(indiceAleatorio(indice), tocando);
  }

  function faixaAnterior() {
    if (semFaixas()) return;
    const tocando = !audio.paused;
    const anterior = historico.pop();
    carregarFaixa(anterior !== undefined ? anterior : indiceAleatorio(indice), tocando);
  }

  if (semFaixas()) {
    [btnPlayPause, btnAnterior, btnProxima].forEach((b) => b && (b.disabled = true));
  } else {
    // Restaura a faixa que já estava tocando para NUNCA perder a música ao navegar
    const salvo = parseInt(localStorage.getItem("estoque-player-indice"), 10);
    let indiceInicial = (!isNaN(salvo) && salvo >= 0 && salvo < lista.length) ? salvo : Math.floor(Math.random() * lista.length);
    tentarAutoplay(indiceInicial);
  }

  function tentarAutoplay(indiceEscolhido) {
    carregarFaixa(indiceEscolhido, false);

    const tempoSalvo = parseFloat(localStorage.getItem("estoque-player-tempo")) || 0;
    if (tempoSalvo > 0 && Number.isFinite(tempoSalvo)) {
      try { audio.currentTime = tempoSalvo; } catch (_) {}
    }

    const estavaTocando = localStorage.getItem("estoque-player-tocando") === "true";

    audio.play().then(() => {
      atualizarIconePlay(true);
      marcarGirando(true);
      salvarEstadoPlayer();
    }).catch(() => {
      // Se o navegador bloqueou o autoplay sem gesto prévio, espera o primeiro toque/clique para iniciar
      atualizarIconePlay(false);
      marcarGirando(false);

      if (estavaTocando) {
        function iniciarNoPrimeiroGesto() {
          audio.play().then(() => {
            atualizarIconePlay(true);
            marcarGirando(true);
            salvarEstadoPlayer();
          }).catch(() => {});
        }

        ["click", "keydown", "touchstart"].forEach((evento) => {
          document.addEventListener(evento, iniciarNoPrimeiroGesto, { once: true });
        });
      }
    });
  }

  btnPlayPause.addEventListener("click", tocarPausar);
  if (btnProxima) btnProxima.addEventListener("click", proximaFaixa);
  if (btnAnterior) btnAnterior.addEventListener("click", faixaAnterior);

  audio.addEventListener("play", () => {
    atualizarIconePlay(true);
    marcarGirando(true);
    salvarEstadoPlayer();
  });

  audio.addEventListener("pause", () => {
    atualizarIconePlay(false);
    marcarGirando(false);
    salvarEstadoPlayer();
  });

  audio.addEventListener("timeupdate", () => {
    if (Math.floor(audio.currentTime) % 4 === 0) {
      salvarEstadoPlayer();
    }
  });

  // Somente avança a faixa quando a música realmente termina de tocar até o final
  audio.addEventListener("ended", () => {
    proximaFaixa();
  });

  audio.addEventListener("error", (e) => {
    // 1. Erro de abort (código 1 = MEDIA_ERR_ABORTED):
    // Ocorre quando o navegador cancela o stream durante navegação ou troca. É inofensivo.
    if (audio.error && audio.error.code === 1) {
      return;
    }

    console.warn("TechStock Player: aviso de áudio na faixa:", audio.src, audio.error);
    // NÃO chama proximaFaixa() aqui para não criar loop infinito de troca de faixas ao navegar rápido!
  });
}

/* ---- Confirmação de exclusão: substitui o confirm() nativo do navegador
   por um modal com a cara do resto do sistema. Qualquer <form> marcado com
   a classe "form-confirmar-exclusao" passa a usar esse modal em vez do
   alerta simples do navegador.

   Precisa ser registrada em fase de CAPTURA (terceiro argumento "true")
   porque o nav.js também escuta "submit" em document, na fase normal
   (bubbling), e cancela sua própria navegação AJAX quando vê
   e.defaultPrevented. Capturando antes, a gente consegue interceptar,
   mostrar o modal e só disparar o submit de verdade se o usuário
   confirmar — sem depender da ordem em que os scripts foram carregados. */
function initConfirmacaoExclusao() {
  const modalEl = document.getElementById("modalConfirmarExclusao");
  if (!modalEl || typeof bootstrap === "undefined") return;

  const modalConfirmacao = new bootstrap.Modal(modalEl);
  const tituloEl = document.getElementById("confirmarExclusaoTitulo");
  const textoEl = document.getElementById("confirmarExclusaoTexto");
  const btnConfirmar = document.getElementById("btnConfirmarExclusao");
  let formPendente = null;

  document.addEventListener("submit", (e) => {
    const form = e.target.closest("form.form-confirmar-exclusao");
    if (!form || form.dataset.confirmado === "true") return;

    e.preventDefault();
    formPendente = form;
    tituloEl.textContent = form.dataset.confirmarTitulo || "Confirmar exclusão";
    textoEl.textContent = form.dataset.confirmarMensagem ||
      "Tem certeza que deseja excluir este item? Essa ação não pode ser desfeita.";
    modalConfirmacao.show();
  }, true);

  btnConfirmar.addEventListener("click", () => {
    if (!formPendente) return;
    const form = formPendente;
    formPendente = null;
    form.dataset.confirmado = "true";
    modalConfirmacao.hide();
    form.requestSubmit();
  });

  // Se o usuário fechar o modal sem confirmar (Cancelar, X, clique fora,
  // Esc), esquece o form pendente para não sobrar estado de uma exclusão
  // que não aconteceu.
  modalEl.addEventListener("hidden.bs.modal", () => {
    formPendente = null;
  });
}

/* ---- Sidebar (abrir/fechar no mobile) ---- */
function initSidebarToggle() {
  const toggleBtn = document.querySelector("[data-sidebar-toggle]");
  const sidebar = document.querySelector(".sidebar");
  if (!toggleBtn || !sidebar) return;

  toggleBtn.addEventListener("click", () => {
    sidebar.classList.toggle("is-open");
  });

  document.addEventListener("click", (e) => {
    if (window.innerWidth > 768) return;
    if (!sidebar.contains(e.target) && !toggleBtn.contains(e.target)) {
      sidebar.classList.remove("is-open");
    }
  });
}

/* ---- Gráfico de linha/área: Entradas x Saídas dos últimos 7 dias ---- */
function criarGraficoMovimentacoes(canvasId, dados) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || typeof Chart === "undefined") return null;

  const corTexto = corDoTema("--color-text-muted", "#6B7785");
  const corGrade = corDoTema("--color-border", "rgba(120,130,145,0.12)");

  return new Chart(canvas.getContext("2d"), {
    type: "line",
    data: {
      labels: dados.labels,
      datasets: [
        {
          label: "Entradas",
          data: dados.entradas,
          borderColor: "#0EA5A0",
          backgroundColor: "rgba(14, 165, 160, 0.12)",
          fill: true,
          tension: 0.4,
          pointRadius: 3,
          pointBackgroundColor: "#0EA5A0",
          borderWidth: 2,
        },
        {
          label: "Saídas",
          data: dados.saidas,
          borderColor: "#E4572E",
          backgroundColor: "rgba(228, 87, 46, 0.08)",
          fill: false,
          tension: 0.4,
          pointRadius: 3,
          pointBackgroundColor: "#E4572E",
          borderWidth: 2,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      plugins: {
        legend: { position: "bottom", labels: { usePointStyle: true, boxWidth: 8, color: corTexto, font: { size: 11, family: "Inter" } } },
      },
      scales: {
        y: { beginAtZero: true, grid: { color: corGrade }, ticks: { color: corTexto, font: { size: 11, family: "Inter" } } },
        x: { grid: { display: false }, ticks: { color: corTexto, font: { size: 11, family: "Inter" } } },
      },
    },
  });
}

function initGraficoMovimentacoesServidor(canvasId, dados) {
  registroGraficos[canvasId] = { tipo: "movimentacoes", dados, instancia: null };
  registroGraficos[canvasId].instancia = criarGraficoMovimentacoes(canvasId, dados);
}

/* ---- Cores de alto contraste e sem repetição para gráficos ---- */
function gerarCoresDistintas(qtd) {
  const paletaBase = [
    "#0EA5A0", // 1. Teal vibrante
    "#8B5CF6", // 2. Roxo violeta
    "#F59E0B", // 3. Âmbar dourado
    "#2563EB", // 4. Azul royal
    "#EF4444", // 5. Vermelho coral
    "#10B981", // 6. Verde esmeralda
    "#EC4899", // 7. Rosa pink
    "#0284C7", // 8. Azul celeste
    "#F97316", // 9. Laranja vivo
    "#6366F1", // 10. Índigo profundo
    "#84CC16", // 11. Verde limão
    "#14B8A6", // 12. Ciano escuro
    "#A855F7", // 13. Púrpura
    "#D97706", // 14. Ocre bronze
    "#06B6D4", // 15. Ciano claro
    "#E11D48", // 16. Carmesim
  ];

  if (qtd <= paletaBase.length) {
    return paletaBase.slice(0, qtd);
  }

  // Gera cores pelo ângulo áureo (137.508°) garantindo dispersão máxima no círculo cromático
  const cores = [...paletaBase];
  const passoAureo = 137.508;
  let matiz = (195 + paletaBase.length * passoAureo) % 360;

  for (let i = paletaBase.length; i < qtd; i++) {
    const sat = 74 + (i % 3) * 5;
    const lum = 48 + (i % 2) * 6;
    cores.push(`hsl(${Math.round(matiz)}, ${sat}%, ${lum}%)`);
    matiz = (matiz + passoAureo) % 360;
  }
  return cores;
}

/* ---- Gráfico de categorias, alimentado com dados vindos do Jinja2/Flask ---- */
function criarGraficoCategorias(canvasId, dados) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || typeof Chart === "undefined") return null;

  const CINZA_OUTROS = "#8B97A6";
  const corTexto = corDoTema("--color-text-muted", "#6B7785");
  const corFundo = corDoTema("--color-surface", "#FFFFFF");

  const totalCategorias = dados.labels.filter((r) => r !== "Outros").length;
  const paleta = gerarCoresDistintas(totalCategorias);

  let indiceCor = 0;
  const cores = dados.labels.map((rotulo) => {
    if (rotulo === "Outros") return CINZA_OUTROS;
    const cor = paleta[indiceCor];
    indiceCor += 1;
    return cor;
  });

  return new Chart(canvas.getContext("2d"), {
    type: "doughnut",
    data: {
      labels: dados.labels,
      datasets: [{
        data: dados.valores,
        backgroundColor: cores,
        borderWidth: 2,
        borderColor: corFundo,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: "68%",
      plugins: {
        legend: { position: "right", labels: { usePointStyle: true, boxWidth: 8, color: corTexto, font: { size: 11, family: "Inter" } } },
      },
    },
  });
}

function initGraficoCategoriasServidor(canvasId, dados) {
  registroGraficos[canvasId] = { tipo: "categorias", dados, instancia: null };
  registroGraficos[canvasId].instancia = criarGraficoCategorias(canvasId, dados);
}

/* ==========================================================================
   Rascunho de formulário — nada do que for digitado se perde
   ==========================================================================
   Problema que isso resolve: a pessoa começava a preencher "Novo produto",
   fechava o modal sem querer (Esc, clique fora, botão X) ou o servidor
   recusava o cadastro por algum erro — e o formulário voltava em branco.
   Todo o trabalho tinha que ser refeito.

   Agora cada tecla digitada é salva no navegador (localStorage). Quando o
   formulário aparece de novo, os campos voltam preenchidos exatamente como
   estavam. O rascunho só é apagado em dois casos:
     1. o cadastro foi concluído com sucesso (o servidor avisa);
     2. a pessoa clicou em "Limpar formulário" de propósito.

   O servidor também devolve os valores direto no HTML quando dá erro de
   validação; nesse caso o valor do servidor tem prioridade e o rascunho só
   completa o que estiver vazio. */
const Rascunho = (function () {
  const PREFIXO = "estoque-rascunho:";

  function chaveDe(nome) {
    return PREFIXO + nome;
  }

  function camposDe(form) {
    return Array.from(form.elements).filter(
      (el) => el.name && el.type !== "password" && el.type !== "submit" && el.type !== "button"
    );
  }

  function salvar(form, nome) {
    const dados = {};
    camposDe(form).forEach((el) => {
      if (el.type === "checkbox" || el.type === "radio") {
        if (el.checked) dados[el.name] = el.value;
      } else {
        dados[el.name] = el.value;
      }
    });
    try {
      localStorage.setItem(chaveDe(nome), JSON.stringify(dados));
    } catch (e) {
      /* localStorage cheio ou bloqueado: sem rascunho, mas o app segue */
    }
  }

  function ler(nome) {
    try {
      return JSON.parse(localStorage.getItem(chaveDe(nome)) || "{}");
    } catch (e) {
      return {};
    }
  }

  function apagar(nome) {
    try {
      localStorage.removeItem(chaveDe(nome));
    } catch (e) {}
  }

  function restaurar(form, nome) {
    const dados = ler(nome);
    if (!dados || Object.keys(dados).length === 0) return false;
    let restaurouAlgo = false;

    camposDe(form).forEach((el) => {
      const valor = dados[el.name];
      if (valor === undefined || valor === "") return;
      // Não sobrescreve o que o servidor já devolveu preenchido.
      if (el.type === "checkbox" || el.type === "radio") {
        if (!el.checked && el.value === valor) {
          el.checked = true;
          restaurouAlgo = true;
        }
        return;
      }
      if (el.value) return;
      if (el.tagName === "SELECT" && !Array.from(el.options).some((o) => o.value === valor)) return;
      el.value = valor;
      restaurouAlgo = true;
    });

    return restaurouAlgo;
  }

  /**
   * Liga o rascunho a um formulário.
   * @param {string} seletorForm  seletor do <form>
   * @param {string} nome         identificador do rascunho (ex.: "produto")
   * @param {object} opcoes       { concluido: bool, modal: "#idDoModal", abrir: bool }
   */
  function ligar(seletorForm, nome, opcoes) {
    const form = document.querySelector(seletorForm);
    if (!form) return;
    const opts = opcoes || {};

    // Cadastro concluído com sucesso: o rascunho já cumpriu seu papel.
    if (opts.concluido) {
      apagar(nome);
      form.reset();
    } else {
      restaurar(form, nome);
    }

    if (!form.dataset.rascunhoLigado) {
      form.dataset.rascunhoLigado = "true";
      ["input", "change"].forEach((evento) => {
        form.addEventListener(evento, () => salvar(form, nome));
      });
    }

    // Botão opcional "Limpar formulário": única forma de descartar o que
    // foi digitado — e sempre por decisão explícita da pessoa.
    const btnLimpar = form.querySelector("[data-limpar-rascunho]");
    if (btnLimpar && !btnLimpar.dataset.ligado) {
      btnLimpar.dataset.ligado = "true";
      btnLimpar.addEventListener("click", () => {
        apagar(nome);
        form.reset();
        form.querySelectorAll("input, select, textarea").forEach((el) => {
          if (el.type !== "hidden") el.value = "";
        });
      });
    }

    // Reabre o modal quando o servidor recusou o cadastro, para a pessoa
    // ver o erro e corrigir sem começar do zero.
    if (opts.modal && opts.abrir && typeof bootstrap !== "undefined") {
      const modalEl = document.querySelector(opts.modal);
      if (modalEl) {
        bootstrap.Modal.getOrCreateInstance(modalEl).show();
      }
    }

    // Quando o modal é aberto de novo, repõe o rascunho (caso a pessoa
    // tenha fechado a janela no meio do preenchimento).
    if (opts.modal) {
      const modalEl = document.querySelector(opts.modal);
      if (modalEl && !modalEl.dataset.rascunhoLigado) {
        modalEl.dataset.rascunhoLigado = "true";
        modalEl.addEventListener("shown.bs.modal", () => restaurar(form, nome));
      }
    }
  }

  return { ligar, salvar, restaurar, apagar, ler };
})();

window.Rascunho = Rascunho;

/* ---- Inicialização comum a todas as páginas ---- */
document.addEventListener("DOMContentLoaded", () => {
  initSidebarToggle();
  initTema();
  initMusica();
  initConfirmacaoExclusao();
});
