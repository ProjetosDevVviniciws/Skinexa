import {
    exibirToast
} from "../components/toast.js";

const inventoryState = {
    pagina: 1,
};

document.addEventListener(
    "DOMContentLoaded",
    () => {
        configurarEventosInventario();
        configurarSincronizacaoInventario();
        carregarInventario();
    }
);

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

async function sincronizarInventario(formulario) {
    const botao = document.querySelector(
        "#inventory-sync-button"
    );

    if (!botao) {
        return;
    }

    const textoOriginal = botao.textContent;

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
        botao.disabled = false;
        botao.textContent = textoOriginal;
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
        const resposta = await fetch(
            `/dashboard/inventario?pagina=${inventoryState.pagina}`,
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

function renderizarInventario(
    container,
    dados
) {
    container.replaceChildren();

    if (!dados.itens.length) {
        const mensagem = document.createElement(
            "p"
        );

        mensagem.textContent =
            "Nenhum item sincronizado.";

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