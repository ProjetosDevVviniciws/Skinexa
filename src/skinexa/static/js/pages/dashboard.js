import {
    exibirToast
} from "../components/toast.js";

const inventoryState = {
    pagina: 1,
    busca: "",
    tipo: "",
    raridade: "",
    estador: "",
    stattrak: false,
    souvenir: false,
};

document.addEventListener(
    "DOMContentLoaded",
    () => {
        configurarEventosInventario();
        configurarPesquisaInventario();
        configurarFiltroTipoInventario();
        configurarFiltroRaridadeInventario();
        configurarFiltroEstadoInventario();
        configurarFiltroStatTrakInventario();
        configurarFiltroSouvenirInventario();
        configurarSincronizacaoInventario();
        
        carregarTiposInventario();
        carregarRaridadesInventario();
        carregarEstadosInventario();
        carregarInventario();
    }
);

function configurarEventosInventario() {
    const botaoAnterior = document.querySelector(
        "#inventory-previous"
    );

    const botaoProximo = document.querySelector(
        "#inventory-next"
    );

    botaoAnterior?.addEventListener(
        "click",
        () => {
            if (inventoryState.pagina <= 1) {
                return;
            }

            inventoryState.pagina -= 1;

            carregarInventario();
        }
    );

    botaoProximo?.addEventListener(
        "click",
        () => {
            inventoryState.pagina += 1;

            carregarInventario();
        }
    );
}

function configurarPesquisaInventario() {
    const campoBusca = document.querySelector(
        "#inventory-search-input"
    );

    if (!campoBusca) {
        return;
    }

    const pesquisarComDebounce = debounce(
        async () => {
            inventoryState.busca =
                campoBusca.value.trim();

            inventoryState.pagina = 1;

            await carregarInventario();
        },
        350
    );

    campoBusca.addEventListener(
        "input",
        pesquisarComDebounce
    );
}

function configurarFiltroTipoInventario() {
    const select = document.querySelector(
        "#inventory-type-select"
    );

    if (!select) {
        return;
    }

    select.addEventListener(
        "change",
        async () => {
            inventoryState.tipo =
                select.value.trim();

            inventoryState.pagina = 1;

            await carregarInventario();
        }
    );
}

function configurarFiltroRaridadeInventario() {
    const select = document.querySelector(
        "#inventory-rarity-select"
    );

    if (!select) {
        return;
    }

    select.addEventListener(
        "change",
        async () => {
            inventoryState.raridade =
                select.value.trim();

            inventoryState.pagina = 1;

            await carregarInventario();
        }
    );
}

function configurarFiltroEstadoInventario() {
    const select = document.querySelector(
        "#inventory-exterior-select"
    );

    if (!select) {
        return;
    }

    select.addEventListener(
        "change",
        async () => {
            inventoryState.estado =
                select.value.trim();

            inventoryState.pagina = 1;

            await carregarInventario();
        }
    );
}

function configurarFiltroStatTrakInventario() {
    const checkbox = document.querySelector(
        "#inventory-stattrak-filter"
    );

    if (!checkbox) {
        return;
    }

    checkbox.addEventListener(
        "change",
        async () => {
            inventoryState.stattrak =
                checkbox.checked;

            inventoryState.pagina = 1;

            await carregarInventario();
        }
    );
}

function configurarFiltroSouvenirInventario() {
    const checkbox = document.querySelector(
        "#inventory-souvenir-filter"
    );

    if (!checkbox) {
        return;
    }

    checkbox.addEventListener(
        "change",
        async () => {
            inventoryState.souvenir =
                checkbox.checked;

            inventoryState.pagina = 1;

            await carregarInventario();
        }
    );
}

function configurarSincronizacaoInventario() {
    const formulario = document.querySelector(
        "#inventory-sync-form"
    );

    if (!formulario) {
        return;
    }

    formulario.addEventListener(
        "submit",
        async (evento) => {
            evento.preventDefault();

            await sincronizarInventario(
                formulario
            );
        }
    );
}

async function carregarTiposInventario() {
    const select = document.querySelector(
        "#inventory-type-select"
    );

    if (!select) {
        return;
    }

    try {
        const resposta = await fetch(
            "/dashboard/inventario/tipos",
            {
                headers: {
                    Accept: "application/json",
                },
            }
        );

        if (!resposta.ok) {
            throw new Error(
                "Não foi possível carregar os tipos."
            );
        }

        const dados = await resposta.json();

        for (const tipo of dados.tipos) {
            const opcao = document.createElement(
                "option"
            );

            opcao.value = tipo;
            opcao.textContent = tipo;

            select.appendChild(opcao);
        }

    } catch (erro) {
        exibirToast(
            "Não foi possível carregar os tipos do inventário.",
            "error"
        );
    }
}

async function carregarRaridadesInventario() {
    const select = document.querySelector(
        "#inventory-rarity-select"
    );

    if (!select) {
        return;
    }

    try {
        const resposta = await fetch(
            "/dashboard/inventario/raridades",
            {
                headers: {
                    Accept: "application/json",
                },
            }
        );

        if (!resposta.ok) {
            throw new Error(
                "Não foi possível carregar as raridades."
            );
        }

        const dados = await resposta.json();

        for (const raridade of dados.raridades) {
            const opcao = document.createElement(
                "option"
            );

            opcao.value = raridade;
            opcao.textContent = raridade;

            select.appendChild(opcao);
        }

    } catch (erro) {
        exibirToast(
            "Não foi possível carregar as raridades do inventário.",
            "error"
        );
    }
}

async function carregarEstadosInventario() {
    const select = document.querySelector(
        "#inventory-exterior-select"
    );

    if (!select) {
        return;
    }

    try {
        const resposta = await fetch(
            "/dashboard/inventario/estados",
            {
                headers: {
                    Accept: "application/json",
                },
            }
        );

        if (!resposta.ok) {
            throw new Error(
                "Não foi possível carregar os estados exteriores."
            );
        }

        const dados = await resposta.json();

        for (const estado of dados.estados) {
            const opcao = document.createElement(
                "option"
            );

            opcao.value = estado;
            opcao.textContent = estado;

            select.appendChild(opcao);
        }

    } catch (erro) {
        exibirToast(
            "Não foi possível carregar os estados do inventário.",
            "error"
        );
    }
}

async function carregarInventario() {
    const container = document.querySelector(
        "#inventory-list"
    );

    const total = document.querySelector(
        "#inventory-total"
    );

    if (!container || !total) {
        return;
    }

    exibirCarregamentoInventario(
        container,
        total
    );

    try {
        const parametros = new URLSearchParams({
            pagina: String(
                inventoryState.pagina
            ),
        });

        if (inventoryState.busca) {
            parametros.set(
                "busca",
                inventoryState.busca
            );
        }

        if (inventoryState.tipo) {
            parametros.set(
                "tipo",
                inventoryState.tipo
            );
        }

        if (inventoryState.raridade) {
            parametros.set(
                "raridade",
                inventoryState.raridade
            );
        }

        if (inventoryState.estado) {
            parametros.set(
                "estado",
                inventoryState.estado
            );
        }

        if (inventoryState.stattrak) {
            parametros.set(
                "stattrak",
                "1"
            );
        }

        if (inventoryState.souvenir) {
            parametros.set(
                "souvenir",
                "1"
            );
        }

        const resposta = await fetch(
            `/dashboard/inventario?${parametros.toString()}`,
            {
                headers: {
                    Accept: "application/json",
                },
            }
        );

        if (!resposta.ok) {
            throw new Error(
                "Não foi possível carregar o inventário."
            );
        }

        const dados = await resposta.json();

        renderizarInventario(
            container,
            dados
        );

        atualizarPaginacao(dados);

        total.textContent =
            `${dados.total_itens} item(ns) ativo(s)`;

    } catch (erro) {
        exibirErroInventario(
            container,
            total
        );
    }
}

async function sincronizarInventario(formulario) {
    const botao = document.querySelector(
        "#inventory-sync-button"
    );

    if (!botao) {
        return;
    }

    const textoOriginal = botao.textContent;

    let cooldownAtivado = false;

    botao.disabled = true;
    botao.textContent = "Sincronizando...";

    try {
        const formularioDados = new FormData(
            formulario
        );

        const resposta = await fetch(
            formulario.action,
            {
                method: "POST",
                body: formularioDados,
                headers: {
                    Accept: "application/json",
                },
            }
        );

        const dados = await resposta.json();

        if (!resposta.ok) {
            if (
                resposta.status === 429
                && dados.codigo === "cooldown_sincronizacao"
                && dados.segundos_restantes
            ) {
                cooldownAtivado = true;
                
                iniciarCooldownVisual(
                    dados.segundos_restantes
                );

                exibirToast(
                    formatarMensagemCooldown(
                        dados.segundos_restantes
                    ),
                    "warning"
                );

                return;
            }

            throw new Error(
                dados.mensagem
                || "Não foi possível sincronizar."
            );
        }

        exibirToast(
            `${dados.mensagem} `
            + `${dados.itens_ativos} item(ns) ativo(s).`,
            "success"
        );

        await carregarInventario();

    } catch (erro) {
        exibirToast(
            erro.message
            || "Não foi possível sincronizar o inventário.",
            "error"
        );

    } finally {
        if (!cooldownAtivado) {
            botao.disabled = false;
            botao.textContent = textoOriginal;
        }
    }
}

function renderizarInventario(
    container,
    dados
) {
    container.replaceChildren();

    if (!dados.itens.length) {
        const mensagem = document.createElement(
            "p"
        );

        if (inventoryState.busca) {
            mensagem.textContent =
            `Nenhum item encontrado para "${inventoryState.busca}".`;
        } else {
            mensagem.textContent =
                "Nenhum item sincronizado.";
        }

        container.appendChild(mensagem);

        return;
    }

    for (const item of dados.itens) {
        container.appendChild(
            criarElementoInventario(item)
        );
    }
}

function criarElementoInventario(item) {
    const article = document.createElement(
        "article"
    );

    article.classList.add("inventory-item");

    if (item.imagem) {
        const imagem = document.createElement(
            "img"
        );

        imagem.src = item.imagem;
        imagem.alt = item.nome_mercado;
        imagem.loading = "lazy";

        article.appendChild(imagem);
    }

    const conteudo = document.createElement(
        "div"
    );

    const titulo = document.createElement(
        "h3"
    );

    titulo.textContent = item.nome_mercado;

    conteudo.appendChild(titulo);

    const lista = document.createElement("dl");

    adicionarInformacao(
        lista,
        "Tipo",
        item.tipo_item
    );

    if (item.raridade) {
        adicionarInformacao(
            lista,
            "Raridade",
            item.raridade
        );
    }

    if (item.estado_exterior) {
        adicionarInformacao(
            lista,
            "Estado",
            item.estado_exterior
        );
    }

    adicionarInformacao(
        lista,
        "Trocável",
        item.trocavel ? "Sim" : "Não"
    );

    adicionarInformacao(
        lista,
        "Comercializável",
        item.comercializavel
            ? "Sim"
            : "Não"
    );

    conteudo.appendChild(lista);

    if (item.stattrak) {
        const stattrak = document.createElement(
            "span"
        );

        stattrak.textContent = "StatTrak™";

        conteudo.appendChild(stattrak);
    }

    if (item.souvenir) {
        const souvenir = document.createElement(
            "span"
        );

        souvenir.textContent = "Souvenir";

        conteudo.appendChild(souvenir);
    }

    article.appendChild(conteudo);

    return article;
}

function adicionarInformacao(
    lista,
    titulo,
    valor
) {
    const termo = document.createElement("dt");
    const descricao = document.createElement(
        "dd"
    );

    termo.textContent = titulo;
    descricao.textContent =
        valor ?? "Não informado";

    lista.append(
        termo,
        descricao
    );
}

function atualizarPaginacao(dados) {
    const paginacao = document.querySelector(
        "#inventory-pagination"
    );

    const anterior = document.querySelector(
        "#inventory-previous"
    );

    const proximo = document.querySelector(
        "#inventory-next"
    );

    const pagina = document.querySelector(
        "#inventory-page"
    );

    if (
        !paginacao
        || !anterior
        || !proximo
        || !pagina
    ) {
        return;
    }

    pagina.textContent =
        `Página ${dados.pagina}`;

    anterior.disabled = !dados.tem_anterior;
    proximo.disabled = !dados.tem_proxima;

    paginacao.hidden =
        dados.total_itens === 0;
}

function exibirCarregamentoInventario(
    container,
    total
) {
    total.textContent =
        "Carregando inventário...";

    container.innerHTML = `
        <p class="inventory-loading">
            Carregando inventário...
        </p>
    `;
}

function exibirErroInventario(
    container,
    total
) {
    total.textContent =
        "Não foi possível carregar o inventário.";

    container.replaceChildren();

    const mensagem = document.createElement(
        "p"
    );

    mensagem.textContent =
        "Ocorreu um erro ao carregar os itens do inventário.";

    container.appendChild(mensagem);

    exibirToast(
        "Não foi possível carregar o inventário.",
        "error"
    );
}

function iniciarCooldownVisual(segundos) {
    const botao = document.querySelector(
        "#inventory-sync-button"
    );

    if (!botao) {
        return;
    }

    let segundosRestantes = Math.max(
        0,
        Number(segundos)
    );

    botao.disabled = true;

    atualizarTextoCooldown(
        botao,
        segundosRestantes
    );

    const intervalo = window.setInterval(
        () => {
            segundosRestantes -= 1;

            if (segundosRestantes <= 0) {
                window.clearInterval(
                    intervalo
                );

                botao.disabled = false;
                botao.textContent =
                    "Sincronizar inventário";

                return;
            }

            atualizarTextoCooldown(
                botao,
                segundosRestantes
            );
        },
        1000
    );
}

function atualizarTextoCooldown(
    botao,
    segundos
) {
    botao.textContent =
        `Sincronizar novamente em ${
            formatarTempo(segundos)
        }`;
}

function formatarTempo(segundos) {
    const minutos = Math.floor(
        segundos / 60
    );

    const restanteSegundos =
        segundos % 60;

    return (
        `${minutos}:`
        + `${String(
            restanteSegundos
        ).padStart(2, "0")}`
    );
}

function formatarMensagemCooldown(
    segundos
) {
    const minutos = Math.floor(
        segundos / 60
    );

    const restanteSegundos =
        segundos % 60;

    if (minutos > 0) {
        return (
            "Aguarde "
            + `${minutos} min `
            + `${restanteSegundos} s `
            + "antes de sincronizar novamente."
        );
    }

    return (
        `Aguarde ${restanteSegundos} s `
        + "antes de sincronizar novamente."
    );
}

function debounce(funcao, espera) {
    let temporizador;

    return (...argumentos) => {
        window.clearTimeout(
            temporizador
        );

        temporizador = window.setTimeout(
            () => {
                funcao(...argumentos);
            },
            espera
        );
    };
}