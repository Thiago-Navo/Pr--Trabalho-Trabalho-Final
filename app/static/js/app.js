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
  let historico = []; // pilha de faixas já tocadas nesta sessão, para o botão "anterior" funcionar direito no modo aleatório

  function semFaixas() {
    return lista.length === 0;
  }

  function indiceAleatorio(evitar) {
    // Sorteia uma faixa diferente da que está tocando agora, sempre que
    // houver mais de uma faixa na playlist (senão ia poder repetir a
    // mesma faixa sem querer).
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
    audio.src = faixa.src;
    tituloEl.textContent = faixa.titulo || "Faixa sem nome";
    artistaEl.textContent = faixa.artista || "Artista desconhecido";
    if (capa) capa.src = faixa.capa && faixa.capa.trim() ? faixa.capa : capaPadrao;

    if (autoPlay) {
      audio.play().then(() => {
        atualizarIconePlay(true);
        marcarGirando(true);
      }).catch(() => {
        // navegador pode bloquear autoplay sem interação prévia — sem problema
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
      }).catch(() => {});
    } else {
      audio.pause();
      atualizarIconePlay(false);
      marcarGirando(false);
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
    // Começa numa faixa aleatória a cada login/carregamento completo da
    // página (essa função só roda de novo em recarregamentos de página
    // inteiros — a navegação suave entre telas não mexe no player).
    const indiceInicial = Math.floor(Math.random() * lista.length);
    tentarAutoplay(indiceInicial);
  }

  function tentarAutoplay(indiceEscolhido) {
    // Carrega a faixa (título, capa) sem tentar tocar ainda — quem cuida
    // da tentativa de reprodução é este método, para sabermos exatamente
    // quando o navegador bloqueou o autoplay.
    carregarFaixa(indiceEscolhido, false);

    audio.play().then(() => {
      atualizarIconePlay(true);
      marcarGirando(true);
    }).catch(() => {
      // Navegadores bloqueiam áudio com som tocando sozinho sem que a
      // pessoa já tenha interagido com a página — é uma política do
      // próprio navegador, não dá pra forçar. Para chegar o mais perto
      // possível de "toca sozinho ao logar", a gente espera o primeiro
      // clique/toque/tecla em qualquer lugar da página (que já conta
      // como "interação do usuário") e usa esse gesto para iniciar a
      // reprodução automaticamente, sem precisar apertar o botão de play.
      atualizarIconePlay(false);
      marcarGirando(false);

      function iniciarNoPrimeiroGesto() {
        audio.play().then(() => {
          atualizarIconePlay(true);
          marcarGirando(true);
        }).catch(() => {});
      }

      ["click", "keydown", "touchstart"].forEach((evento) => {
        document.addEventListener(evento, iniciarNoPrimeiroGesto, { once: true });
      });
    });
  }

  btnPlayPause.addEventListener("click", tocarPausar);
  if (btnProxima) btnProxima.addEventListener("click", proximaFaixa);
  if (btnAnterior) btnAnterior.addEventListener("click", faixaAnterior);

  audio.addEventListener("ended", () => proximaFaixa());
  audio.addEventListener("error", () => {
    if (!semFaixas()) {
      artistaEl.textContent = "Arquivo de áudio não encontrado";
      atualizarIconePlay(false);
      marcarGirando(false);
    }
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

/* ---- Gráfico de categorias, alimentado com dados vindos do Jinja2/Flask ---- */
function criarGraficoCategorias(canvasId, dados) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || typeof Chart === "undefined") return null;

  const paleta = ["#0EA5A0", "#F5A524", "#E4572E", "#2FA36B", "#8B97A6", "#1B2430", "#C7CED6", "#0B8783"];
  const corTexto = corDoTema("--color-text-muted", "#6B7785");
  const corFundo = corDoTema("--color-surface", "#FFFFFF");

  return new Chart(canvas.getContext("2d"), {
    type: "doughnut",
    data: {
      labels: dados.labels,
      datasets: [{
        data: dados.valores,
        backgroundColor: paleta,
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

/* ---- Inicialização comum a todas as páginas ---- */
document.addEventListener("DOMContentLoaded", () => {
  initSidebarToggle();
  initTema();
  initMusica();
  initConfirmacaoExclusao();
});
