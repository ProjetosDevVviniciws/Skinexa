"use strict";

document.addEventListener("DOMContentLoaded", () => {
    const resultados = document.querySelector(".market-results");
    const carregamento = document.querySelector("#market-loading");
    const formularioOrdenacao = document.querySelector(".market-sort");

    if (
        !resultados ||
        !carregamento ||
        !formularioOrdenacao ||
        !resultados.dataset.marketApiUrl
    ) {
        return;
    }

    const urlApi = resultados.dataset.marketApiUrl;

    let controladorAtual = null;
    let identificadorRequisicao = 0;

    /**
     * Cria elementos com classes e conteúdo textual seguros.
     */
    const criarElemento = (
        tag,
        classe = "",
        texto = null
    ) => {
        const elemento = document.createElement(tag);

        if (classe) {
            elemento.className = classe;
        }

        if (texto !== null && texto !== undefined) {
            elemento.textContent = String(texto);
        }

        return elemento;
    };

    /**
     * Cria o Empty State utilizando os mesmos elementos
     * visuais da renderização inicial do Jinja.
     */
    const criarEstadoVazio = (paginacao, urlDestino) => {
        const vazio = criarElemento("div", "market-empty");

        vazio.setAttribute("role", "status");
        vazio.setAttribute(
            "aria-labelledby",
            "market-empty-title"
        );

        const icone = criarElemento(
            "div",
            "market-empty-icon"
        );

        const svg = document.createElementNS(
            "http://www.w3.org/2000/svg",
            "svg"
        );

        svg.setAttribute("width", "28");
        svg.setAttribute("height", "28");
        svg.setAttribute("viewBox", "0 0 24 24");
        svg.setAttribute("fill", "none");
        svg.setAttribute("stroke", "currentColor");
        svg.setAttribute("stroke-width", "1.8");
        svg.setAttribute("stroke-linecap", "round");
        svg.setAttribute("stroke-linejoin", "round");

        const circulo = document.createElementNS(
            "http://www.w3.org/2000/svg",
            "circle"
        );

        circulo.setAttribute("cx", "11");
        circulo.setAttribute("cy", "11");
        circulo.setAttribute("r", "8");

        const cabo = document.createElementNS(
            "http://www.w3.org/2000/svg",
            "path"
        );

        cabo.setAttribute("d", "m21 21-4.35-4.35");

        svg.append(circulo, cabo);
        icone.append(svg);

        const semItens = paginacao.total_itens === 0;

        const titulo = criarElemento(
            "h2",
            "market-empty-title",
            semItens
                ? "Nenhum item disponível"
                : "Página não encontrada no catálogo"
        );

        titulo.id = "market-empty-title";

        const descricao = criarElemento(
            "p",
            "market-empty-description",
            semItens
                ? "O catálogo ainda não possui itens disponíveis para exibição. Tente novamente mais tarde."
                : "A página solicitada não contém itens. Retorne ao início do catálogo para continuar navegando."
        );

        vazio.append(icone, titulo, descricao);

        if (!semItens) {
            const urlInicial = new URL(urlDestino.href);

            urlInicial.searchParams.set("pagina", "1");

            const link = criarElemento(
                "a",
                "market-empty-action",
                "Voltar à primeira página"
            );

            link.href = urlInicial.pathname + urlInicial.search;

            vazio.append(link);
        }

        return vazio;
    };

    /**
     * Mostra o estado visual de carregamento.
     */
    const iniciarCarregamento = () => {
        carregamento.hidden = false;
        resultados.classList.add("is-loading");
        resultados.setAttribute("aria-busy", "true");
    };

    /**
     * Oculta o carregamento após a requisição.
     */
    const finalizarCarregamento = () => {
        carregamento.hidden = true;
        resultados.classList.remove("is-loading");
        resultados.removeAttribute("aria-busy");
    };

    /**
     * Cria um card preservando o HTML visual do Jinja.
     */
    const criarCard = (item) => {
        const card = criarElemento("article", "market-card");

        if (
            typeof item.cor_raridade === "string" &&
            /^#[0-9a-fA-F]{6}$/.test(item.cor_raridade)
        ) {
            card.style.setProperty(
                "--rarity-color",
                item.cor_raridade
            );
        }

        const link = criarElemento("a", "market-card-link");
        link.href = item.url_detalhes;
        link.setAttribute(
            "aria-label",
            `Ver detalhes de ${item.nome_exibicao}`
        );

        const areaImagem = criarElemento(
            "div",
            "market-card-image"
        );

        const urlImagem = (
            item.url_icone_grande || item.url_icone
        );

        if (urlImagem) {
            const imagem = document.createElement("img");

            imagem.src = urlImagem;
            imagem.alt = "";
            imagem.loading = "lazy";
            imagem.decoding = "async";

            areaImagem.append(imagem);
        } else {
            areaImagem.append(
                criarElemento(
                    "span",
                    "market-card-no-image",
                    "Imagem indisponível"
                )
            );
        }

        const conteudo = criarElemento(
            "div",
            "market-card-content"
        );

        conteudo.append(
            criarElemento(
                "span",
                "market-card-type",
                item.tipo_item.replaceAll("_", " ")
            )
        );

        conteudo.append(
            criarElemento(
                "h2",
                "market-card-title",
                item.nome_exibicao
            )
        );

        const detalhes = [
            item.nome_arma,
            item.nome_acabamento,
            item.estado_exterior,
        ].filter(Boolean);

        if (detalhes.length > 0) {
            const grupoDetalhes = criarElemento(
                "div",
                "market-card-details"
            );

            detalhes.forEach((detalhe) => {
                grupoDetalhes.append(
                    criarElemento("span", "", detalhe)
                );
            });

            conteudo.append(grupoDetalhes);
        }

        if (item.raridade) {
            const raridade = criarElemento(
                "p",
                "market-card-rarity"
            );

            const indicador = criarElemento(
                "span",
                "market-card-rarity-dot"
            );

            indicador.setAttribute("aria-hidden", "true");

            raridade.append(
                indicador,
                document.createTextNode(` ${item.raridade}`)
            );

            conteudo.append(raridade);
        }

        if (
            item.variante_stattrak ||
            item.variante_souvenir
        ) {
            const etiquetas = criarElemento(
                "div",
                "market-card-tags"
            );

            if (item.variante_stattrak) {
                etiquetas.append(
                    criarElemento(
                        "span",
                        "market-card-tag market-card-tag-stattrak",
                        "StatTrak™"
                    )
                );
            }

            if (item.variante_souvenir) {
                etiquetas.append(
                    criarElemento(
                        "span",
                        "market-card-tag market-card-tag-souvenir",
                        "Souvenir"
                    )
                );
            }

            conteudo.append(etiquetas);
        }

        link.append(areaImagem, conteudo);
        card.append(link);

        return card;
    };

    /**
     * Cria a grade com os itens retornados pela API.
     */
    const criarListagem = (
        itens,
        paginacao,
        urlDestino
    ) => {
        if (itens.length === 0) {
            return criarEstadoVazio(
                paginacao,
                urlDestino
            );
        }

        const grade = criarElemento("div", "market-grid");

        const fragmento = document.createDocumentFragment();

        itens.forEach((item) => {
            fragmento.append(criarCard(item));
        });

        grade.append(fragmento);

        return grade;
    };

    /**
     * Cria os links da paginação mantendo os parâmetros.
     */
    const criarUrlPagina = (urlBase, pagina) => {
        const url = new URL(urlBase.href);

        url.searchParams.set("pagina", String(pagina));

        return url.pathname + url.search;
    };

    const criarLinkPaginacao = (
        texto,
        habilitado,
        href,
        proxima = false
    ) => {
        const classe = proxima
            ? "market-pagination-link market-pagination-next"
            : "market-pagination-link";

        if (!habilitado) {
            const desabilitado = criarElemento(
                "span",
                `${classe} is-disabled`,
                texto
            );

            desabilitado.setAttribute(
                "aria-disabled",
                "true"
            );

            return desabilitado;
        }

        const link = criarElemento("a", classe, texto);
        link.href = href;

        return link;
    };

    /**
     * Reproduz a estrutura visual da paginação Jinja.
     */
    const criarPaginacao = (paginacao, urlBase) => {
        if (paginacao.total_paginas <= 1) {
            return null;
        }

        const nav = criarElemento(
            "nav",
            "market-pagination"
        );

        nav.setAttribute(
            "aria-label",
            "Paginação dos itens do mercado"
        );

        nav.append(
            criarLinkPaginacao(
                "Anterior",
                paginacao.tem_anterior,
                criarUrlPagina(
                    urlBase,
                    paginacao.pagina - 1
                )
            )
        );

        nav.append(
            criarElemento(
                "span",
                "market-pagination-current",
                `${paginacao.pagina} de ${paginacao.total_paginas}`
            )
        );

        nav.append(
            criarLinkPaginacao(
                "Próxima",
                paginacao.tem_proxima,
                criarUrlPagina(
                    urlBase,
                    paginacao.pagina + 1
                ),
                true
            )
        );

        return nav;
    };

    /**
     * Atualiza a listagem e os indicadores da página.
     */
    const atualizarInterface = (dados, urlDestino) => {
        const paginacao = dados.paginacao;

        const novaListagem = criarListagem(
            dados.itens,
            paginacao,
            urlDestino
        );

        const novaPaginacao = dados.itens.length > 0
            ? criarPaginacao(paginacao, urlDestino)
            : null;

        const listagemAtual = resultados.querySelector(
            ".market-grid, .market-empty"
        );

        if (listagemAtual) {
            listagemAtual.replaceWith(novaListagem);
        } else {
            carregamento.insertAdjacentElement(
                "afterend",
                novaListagem
            );
        }

        const paginacaoAtual = resultados.querySelector(
            ".market-pagination"
        );

        if (paginacaoAtual) {
            paginacaoAtual.remove();
        }

        if (novaPaginacao) {
            resultados.append(novaPaginacao);
        }

        const contador = resultados.querySelector(
            ".market-results-count strong"
        );

        const indicadorPagina = resultados.querySelector(
            ".market-results-page"
        );

        if (contador) {
            contador.textContent = String(
                paginacao.total_itens
            );
        }

        if (indicadorPagina) {
            indicadorPagina.hidden = (
                paginacao.total_paginas === 0
            );

            indicadorPagina.textContent = (
                paginacao.total_paginas > 0
                    ? `Página ${paginacao.pagina} de ${paginacao.total_paginas}`
                    : ""
            );
        }

        const seletorOrdenacao = formularioOrdenacao.querySelector(
            'select[name="ordenacao"]'
        );

        if (seletorOrdenacao) {
            seletorOrdenacao.value = dados.ordenacao;
        }
    };

    /**
     * Faz uma consulta AJAX e atualiza os dados da tela.
     */
    const carregarPagina = async (
        destino,
        { atualizarHistorico = true } = {}
    ) => {
        const urlDestino = new URL(
            destino,
            window.location.href
        );

        const urlRequisicao = new URL(
            urlApi,
            window.location.origin
        );

        urlRequisicao.search = urlDestino.search;

        if (controladorAtual) {
            controladorAtual.abort();
        }

        const controlador = new AbortController();
        controladorAtual = controlador;

        const requisicaoAtual = ++identificadorRequisicao;

        iniciarCarregamento();

        try {
            const resposta = await fetch(
                urlRequisicao.href,
                {
                    method: "GET",
                    headers: {
                        "Accept": "application/json",
                    },
                    signal: controlador.signal,
                }
            );

            if (!resposta.ok) {
                throw new Error(
                    `Falha HTTP ${resposta.status}`
                );
            }

            const dados = await resposta.json();

            if (
                !Array.isArray(dados.itens) ||
                !dados.paginacao ||
                typeof dados.ordenacao !== "string"
            ) {
                throw new Error(
                    "Resposta inválida da API do Mercado."
                );
            }

            if (
                requisicaoAtual !== identificadorRequisicao
            ) {
                return;
            }

            atualizarInterface(dados, urlDestino);

            if (atualizarHistorico) {
                window.history.pushState(
                    {},
                    "",
                    urlDestino.pathname + urlDestino.search
                );
            }
        } catch (erro) {
            if (
                erro.name === "AbortError" ||
                requisicaoAtual !== identificadorRequisicao
            ) {
                return;
            }

            console.error(
                "Erro ao atualizar o Mercado:",
                erro
            );

            /*
             * Fallback temporário:
             * utiliza a navegação Flask tradicional.
             *
             * Na etapa Error State, implementaremos
             * um tratamento visual próprio.
             */
            window.location.assign(urlDestino.href);
        } finally {
            if (
                requisicaoAtual === identificadorRequisicao
            ) {
                controladorAtual = null;
                finalizarCarregamento();
            }
        }
    };

    /**
     * Intercepta somente o formulário da página Mercado.
     */
    formularioOrdenacao.addEventListener(
        "submit",
        (evento) => {
            if (evento.defaultPrevented) {
                return;
            }

            evento.preventDefault();

            const url = new URL(
                formularioOrdenacao.action
            );

            const parametros = new URLSearchParams(
                new FormData(formularioOrdenacao)
            );

            parametros.set("pagina", "1");

            url.search = parametros.toString();

            carregarPagina(url.href);
        }
    );

    /**
     * Delegação de eventos:
     * funciona inclusive após substituir a paginação.
     */
    resultados.addEventListener("click", (evento) => {
        const link = evento.target.closest(
            ".market-pagination a.market-pagination-link"
        );

        if (!link) {
            return;
        }

        if (
            evento.defaultPrevented ||
            evento.button !== 0 ||
            evento.ctrlKey ||
            evento.metaKey ||
            evento.shiftKey ||
            evento.altKey ||
            link.target === "_blank"
        ) {
            return;
        }

        evento.preventDefault();

        carregarPagina(link.href);
    });

    /**
     * Restaura páginas visitadas usando Voltar/Avançar.
     */
    window.addEventListener("popstate", () => {
        carregarPagina(
            window.location.href,
            { atualizarHistorico: false }
        );
    });

    /**
     * Trata restauração da página pelo cache do navegador.
     */
    window.addEventListener("pageshow", (evento) => {
        if (evento.persisted) {
            if (controladorAtual) {
                controladorAtual.abort();
            }

            identificadorRequisicao += 1;
            controladorAtual = null;
            finalizarCarregamento();

            carregarPagina(
                window.location.href,
                { atualizarHistorico: false }
            );
        }
    });
});