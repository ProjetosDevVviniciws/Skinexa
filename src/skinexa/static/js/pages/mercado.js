"use strict";

document.addEventListener("DOMContentLoaded", () => {
    const resultados = document.querySelector(".market-results");
    const carregamento = document.querySelector("#market-loading");
    const formularioOrdenacao = document.querySelector(".market-sort");

    const pesquisa = document.querySelector("[data-market-search]");
    const formularioPesquisa = document.querySelector("#market-search-form");
    const campoPesquisa = document.querySelector("#market-search-input");
    const botaoLimparPesquisa = document.querySelector("#market-search-clear");
    const painelSugestoes = document.querySelector("#market-search-panel");
    const listaSugestoes = document.querySelector("#market-search-suggestions");
    const statusSugestoes = document.querySelector("#market-search-status");
    const linkTodosResultados = document.querySelector("#market-search-all");

    if (
        !resultados ||
        !carregamento ||
        !formularioOrdenacao ||
        !resultados.dataset.marketApiUrl
    ) {
        return;
    }

    const urlApi = resultados.dataset.marketApiUrl;

    if (
        !pesquisa ||
        !formularioPesquisa ||
        !campoPesquisa ||
        !botaoLimparPesquisa ||
        !painelSugestoes ||
        !listaSugestoes ||
        !statusSugestoes ||
        !linkTodosResultados ||
        !pesquisa.dataset.marketSuggestionsUrl
    ) {
        return;
    }

    const urlSugestoes = pesquisa.dataset.marketSuggestionsUrl;

    let controladorAtual = null;
    let identificadorRequisicao = 0;
    

    /**
     * Posiciona a página no início do Mercado
     * após atualizar os resultados.
     *
     * Respeita usuários que preferem movimento reduzido.
     */
    const rolarParaMercado = () => {
        const secaoMercado = resultados.closest(".market");

        if (!secaoMercado) {
            return;
        }

        const movimentoReduzido = window.matchMedia(
            "(prefers-reduced-motion: reduce)"
        ).matches;

        secaoMercado.scrollIntoView({
            behavior: movimentoReduzido ? "auto" : "smooth",
            block: "start",
            inline: "nearest",
        });
    };

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
     * Error State das requisições AJAX.
     * Não modifica o HTML dos cards existentes.
     */
    const estadoErro = criarElemento(
        "div",
        "market-error"
    );

    estadoErro.hidden = true;
    estadoErro.setAttribute("role", "alert");

    const iconeErro = criarElemento(
        "div",
        "market-error-icon",
        "!"
    );

    iconeErro.setAttribute("aria-hidden", "true");

    const tituloErro = criarElemento(
        "h2",
        "market-error-title",
        "Não foi possível carregar os itens"
    );

    const descricaoErro = criarElemento(
        "p",
        "market-error-description",
        "Ocorreu um problema ao atualizar o catálogo. " +
        "Verifique sua conexão e tente novamente."
    );

    const botaoTentarNovamente = criarElemento(
        "button",
        "market-error-action",
        "Tentar novamente"
    );

    botaoTentarNovamente.type = "button";

    estadoErro.append(
        iconeErro,
        tituloErro,
        descricaoErro,
        botaoTentarNovamente
    );

    carregamento.insertAdjacentElement(
        "afterend",
        estadoErro
    );

    let destinoFalho = null;
    let atualizarHistoricoFalho = true;

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

        const termoPesquisa = (
            urlDestino.searchParams.get("q") || ""
        ).trim();

        const pesquisaSemResultados = (
            semItens && termoPesquisa.length > 0
        );

        const titulo = criarElemento(
            "h2",
            "market-empty-title",
            pesquisaSemResultados
                ? "Nenhum item encontrado"
                : semItens
                    ? "Nenhum item disponível"
                    : "Página não encontrada no catálogo"
        );

        titulo.id = "market-empty-title";

        const descricao = criarElemento(
            "p",
            "market-empty-description",
            pesquisaSemResultados
                ? "Não encontramos itens correspondentes à sua pesquisa. Experimente outro nome ou identificador."
                : semItens
                    ? "O catálogo ainda não possui itens disponíveis para exibição. Tente novamente mais tarde."
                    : "A página solicitada não contém itens. Retorne ao início do catálogo para continuar navegando."
        );

        vazio.append(icone, titulo, descricao);

        if (pesquisaSemResultados) {
            const linkLimpar = criarElemento(
                "a",
                "market-empty-action",
                "Limpar pesquisa"
            );

            linkLimpar.href = urlDestino.pathname;

            vazio.append(linkLimpar);
        }

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
        ocultarErro();

        carregamento.hidden = false;
        resultados.classList.add("is-loading");
        resultados.setAttribute("aria-busy", "true");
    };
    
    /**
     * Remove o Error State quando uma nova consulta começa
     * ou quando uma consulta termina com sucesso.
     */
    const ocultarErro = () => {
        estadoErro.hidden = true;
        resultados.classList.remove("is-error");
    };

    /**
     * Mostra o erro e guarda a navegação para permitir retry.
     */
    const mostrarErro = (
        urlDestino,
        atualizarHistorico
    ) => {
        destinoFalho = urlDestino.href;
        atualizarHistoricoFalho = atualizarHistorico;

        estadoErro.hidden = false;
        resultados.classList.add("is-error");
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
        { 
            atualizarHistorico = true,
            rolarAoIniciar = false,
        } = {}
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

        if (rolarAoIniciar) {
            rolarParaMercado();
        }

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
            sincronizarFormularios(urlDestino);

            destinoFalho = null;
            ocultarErro();

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

            mostrarErro(
                urlDestino,
                atualizarHistorico
            );
        } finally {
            if (
                requisicaoAtual === identificadorRequisicao
            ) {
                controladorAtual = null;
                finalizarCarregamento();
            }
        }
    };

    /* Pesquisa de itens e gerenciamento do autocomplete */

    let temporizadorSugestoes = null;
    let controladorSugestoes = null;
    let identificadorSugestoes = 0;

    let sugestoesAtuais = [];
    let indiceSugestaoAtiva = -1;

    const LIMITE_TERMO_PESQUISA = 100;
    const ATRASO_AUTOCOMPLETE = 300;

    const campoOrdenacaoPesquisa = formularioPesquisa.querySelector(
        'input[name="ordenacao"]'
    );

    const campoQuantidadePesquisa = formularioPesquisa.querySelector(
        'input[name="por_pagina"]'
    );

    const campoPesquisaOrdenacao = formularioOrdenacao.querySelector(
        'input[name="q"]'
    );

    const sincronizarFormularios = (url) => {
        const parametros = url.searchParams;
        const termo = parametros.get("q") || "";

        campoPesquisa.value = termo;
        botaoLimparPesquisa.hidden = termo.length === 0;

        if (campoPesquisaOrdenacao) {
            campoPesquisaOrdenacao.value = termo;
        }

        if (campoOrdenacaoPesquisa) {
            campoOrdenacaoPesquisa.value = (
                parametros.get("ordenacao") || "nome_asc"
            );
        }

        if (campoQuantidadePesquisa) {
            campoQuantidadePesquisa.value = (
                parametros.get("por_pagina") || "20"
            );
        }
    };

    const construirUrlPesquisa = (termo) => {
        const url = new URL(
            formularioPesquisa.action,
            window.location.href
        );

        const parametros = new URLSearchParams(
            window.location.search
        );

        parametros.set("pagina", "1");

        if (termo) {
            parametros.set("q", termo);
        } else {
            parametros.delete("q");
        }

        url.search = parametros.toString();

        return url;
    };

    const interromperSugestoes = () => {
        if (temporizadorSugestoes !== null) {
            clearTimeout(temporizadorSugestoes);
            temporizadorSugestoes = null;
        }

        if (controladorSugestoes) {
            controladorSugestoes.abort();
            controladorSugestoes = null;
        }

        identificadorSugestoes += 1;
    };

    const atualizarSelecaoSugestoes = () => {
        const opcoes = listaSugestoes.querySelectorAll(
            ".market-search-suggestion-link"
        );

        opcoes.forEach((opcao, indice) => {
            const ativa = indice === indiceSugestaoAtiva;

            opcao.classList.toggle("is-active", ativa);
            opcao.setAttribute(
                "aria-selected",
                String(ativa)
            );

            if (ativa) {
                campoPesquisa.setAttribute(
                    "aria-activedescendant",
                    opcao.id
                );

                opcao.scrollIntoView({
                    block: "nearest",
                    behavior: "instant",
                });
            }
        });

        if (indiceSugestaoAtiva < 0) {
            campoPesquisa.removeAttribute(
                "aria-activedescendant"
            );
        }
    };

    const fecharSugestoes = () => {
        interromperSugestoes();

        painelSugestoes.hidden = true;
        campoPesquisa.setAttribute("aria-expanded", "false");
        campoPesquisa.removeAttribute("aria-activedescendant");

        indiceSugestaoAtiva = -1;
        sugestoesAtuais = [];
    };

    const abrirSugestoes = () => {
        painelSugestoes.hidden = false;
        campoPesquisa.setAttribute("aria-expanded", "true");
    };

    const mostrarStatusSugestoes = (mensagem) => {
        listaSugestoes.replaceChildren();

        sugestoesAtuais = [];
        indiceSugestaoAtiva = -1;

        campoPesquisa.removeAttribute("aria-activedescendant");

        statusSugestoes.textContent = mensagem;
        statusSugestoes.hidden = false;

        linkTodosResultados.hidden = true;

        abrirSugestoes();
    };

    const renderizarSugestoes = (sugestoes, termo) => {
        listaSugestoes.replaceChildren();

        sugestoesAtuais = sugestoes;
        indiceSugestaoAtiva = -1;

        statusSugestoes.hidden = true;
        statusSugestoes.textContent = "";

        campoPesquisa.removeAttribute("aria-activedescendant");

        const fragmento = document.createDocumentFragment();

        sugestoes.forEach((sugestao, indice) => {
            const item = criarElemento(
                "li",
                "market-search-suggestion"
            );

            const link = criarElemento(
                "a",
                "market-search-suggestion-link"
            );

            link.id = `market-search-option-${indice}`;
            link.href = sugestao.url_detalhes;
            link.setAttribute("role", "option");
            link.setAttribute("aria-selected", "false");

            const imagemContainer = criarElemento(
                "span",
                "market-search-suggestion-image"
            );

            if (sugestao.url_icone) {
                const imagem = document.createElement("img");

                imagem.src = sugestao.url_icone;
                imagem.alt = "";
                imagem.loading = "lazy";
                imagem.decoding = "async";

                imagemContainer.append(imagem);
            } else {
                imagemContainer.classList.add("is-empty");
                imagemContainer.textContent = "Sem imagem";
            }

            const conteudo = criarElemento(
                "span",
                "market-search-suggestion-content"
            );

            conteudo.append(
                criarElemento(
                    "span",
                    "market-search-suggestion-name",
                    sugestao.nome_exibicao
                ),
                criarElemento(
                    "span",
                    "market-search-suggestion-type",
                    String(sugestao.tipo_item).replaceAll("_", " ")
                )
            );

            const seta = criarElemento(
                "span",
                "market-search-suggestion-arrow",
                "→"
            );

            seta.setAttribute("aria-hidden", "true");

            link.append(imagemContainer, conteudo, seta);
            item.append(link);
            fragmento.append(item);
        });

        listaSugestoes.append(fragmento);

        if (sugestoes.length === 0) {
            statusSugestoes.textContent = (
                "Nenhuma sugestão encontrada. " +
                "Você pode pesquisar no catálogo completo."
            );
            statusSugestoes.hidden = false;
        }

        const urlTodos = construirUrlPesquisa(termo);

        linkTodosResultados.href = (
            urlTodos.pathname + urlTodos.search
        );

        linkTodosResultados.replaceChildren(
            document.createTextNode(
                `Ver todos os resultados para "${termo}" `
            ),
            criarElemento("span", "", "→")
        );

        linkTodosResultados.hidden = false;

        abrirSugestoes();
    };

    const consultarSugestoes = async (termo) => {
        if (termo.length < 2) {
            fecharSugestoes();
            return;
        }

        if (controladorSugestoes) {
            controladorSugestoes.abort();
        }

        const controlador = new AbortController();

        controladorSugestoes = controlador;
        const requisicaoAtual = ++identificadorSugestoes;

        mostrarStatusSugestoes("Buscando sugestões...");

        const url = new URL(
            urlSugestoes,
            window.location.origin
        );

        url.searchParams.set("q", termo);

        try {
            const resposta = await fetch(url.href, {
                method: "GET",
                headers: {
                    "Accept": "application/json",
                },
                signal: controlador.signal,
            });

            if (!resposta.ok) {
                throw new Error(
                    `Falha HTTP ${resposta.status}`
                );
            }

            const dados = await resposta.json();

            if (!Array.isArray(dados.sugestoes)) {
                throw new Error(
                    "Resposta inválida do autocomplete."
                );
            }

            if (
                requisicaoAtual !== identificadorSugestoes ||
                campoPesquisa.value.trim() !== termo
            ) {
                return;
            }

            renderizarSugestoes(dados.sugestoes, termo);
        } catch (erro) {
            if (
                erro.name === "AbortError" ||
                requisicaoAtual !== identificadorSugestoes
            ) {
                return;
            }

            console.error(
                "Erro ao consultar sugestões:",
                erro
            );

            mostrarStatusSugestoes(
                "Não foi possível carregar as sugestões. " +
                "Você ainda pode pesquisar normalmente."
            );
        } finally {
            if (requisicaoAtual === identificadorSugestoes) {
                controladorSugestoes = null;
            }
        }
    };

    const agendarSugestoes = () => {
        interromperSugestoes();

        const termo = campoPesquisa.value.trim();

        botaoLimparPesquisa.hidden = termo.length === 0;

        if (
            termo.length < 2 ||
            termo.length > LIMITE_TERMO_PESQUISA
        ) {
            fecharSugestoes();
            return;
        }

        temporizadorSugestoes = setTimeout(() => {
            temporizadorSugestoes = null;
            consultarSugestoes(termo);
        }, ATRASO_AUTOCOMPLETE);
    };

    /* Eventos da pesquisa */

    campoPesquisa.addEventListener(
        "input",
        agendarSugestoes
    );

    campoPesquisa.addEventListener("focus", () => {
        if (
            campoPesquisa.value.trim().length >= 2 &&
            painelSugestoes.hidden
        ) {
            agendarSugestoes();
        }
    });

    campoPesquisa.addEventListener("keydown", (evento) => {
        if (evento.key === "Escape") {
            if (!painelSugestoes.hidden) {
                evento.preventDefault();
                fecharSugestoes();
            }
            return;
        }

        if (
            evento.key === "ArrowDown" ||
            evento.key === "ArrowUp"
        ) {
            if (painelSugestoes.hidden) {
                return;
            }

            if (sugestoesAtuais.length === 0) {
                return;
            }

            evento.preventDefault();

            const direcao = evento.key === "ArrowDown"
                ? 1
                : -1;

            indiceSugestaoAtiva = Math.max(
                -1,
                Math.min(
                    indiceSugestaoAtiva + direcao,
                    sugestoesAtuais.length - 1
                )
            );

            atualizarSelecaoSugestoes();
            return;
        }

        if (
            evento.key === "Enter" &&
            !painelSugestoes.hidden &&
            indiceSugestaoAtiva >= 0
        ) {
            evento.preventDefault();

            const sugestao = sugestoesAtuais[
                indiceSugestaoAtiva
            ];

            if (sugestao?.url_detalhes) {
                window.location.assign(
                    sugestao.url_detalhes
                );
            }
        }
    });

    formularioPesquisa.addEventListener(
        "submit",
        (evento) => {
            if (evento.defaultPrevented) {
                return;
            }

            evento.preventDefault();
            fecharSugestoes();

            const termo = campoPesquisa.value.trim();
            const url = construirUrlPesquisa(termo);

            if (termo.length > LIMITE_TERMO_PESQUISA) {
                return;
            }

            carregarPagina(url.href, {
                rolarAoIniciar: true,
            });
        }
    );

    botaoLimparPesquisa.addEventListener(
        "click",
        () => {
            campoPesquisa.value = "";
            fecharSugestoes();

            const url = construirUrlPesquisa("");

            carregarPagina(url.href);
            campoPesquisa.focus();
        }
    );

    linkTodosResultados.addEventListener(
        "click",
        (evento) => {
            if (
                evento.defaultPrevented ||
                evento.button !== 0 ||
                evento.ctrlKey ||
                evento.metaKey ||
                evento.shiftKey ||
                evento.altKey
            ) {
                return;
            }

            evento.preventDefault();

            const destino = linkTodosResultados.href;

            fecharSugestoes();

            carregarPagina(destino, {
                rolarAoIniciar: true,
            });
        }
    );

    document.addEventListener("pointerdown", (evento) => {
        if (!pesquisa.contains(evento.target)) {
            fecharSugestoes();
        }
    });

    /**
     * Repete a última navegação que falhou.
     */
    botaoTentarNovamente.addEventListener(
        "click",
        () => {
            if (!destinoFalho) {
                return;
            }

            carregarPagina(
                destinoFalho,
                {
                    atualizarHistorico:
                        atualizarHistoricoFalho,
                }
            );
        }
    );
    
    /**
     * Ordena os resultados preservando a pesquisa ativa.
     */
    formularioOrdenacao.addEventListener(
        "submit",
        (evento) => {
            if (evento.defaultPrevented) {
                return;
            }

            evento.preventDefault();

            const url = new URL(
                window.location.href
            );

            const parametrosFormulario = new URLSearchParams(
                new FormData(formularioOrdenacao)
            );

            // Mantém os parâmetros da URL atual,
            // atualizando somente os controles da ordenação.
            const ordenacao = parametrosFormulario.get(
                "ordenacao"
            );

            const porPagina = parametrosFormulario.get(
                "por_pagina"
            );

            if (ordenacao) {
                url.searchParams.set(
                    "ordenacao",
                    ordenacao
                );
            }

            if (porPagina) {
                url.searchParams.set(
                    "por_pagina",
                    porPagina
                );
            }

            // A URL representa a pesquisa já aplicada.
            // Portanto, preservamos seu parâmetro q.
            const termoAtual = (
                url.searchParams.get("q") || ""
            ).trim();

            if (termoAtual) {
                url.searchParams.set("q", termoAtual);
            } else {
                url.searchParams.delete("q");
            }

            // Uma nova ordenação começa na primeira página.
            url.searchParams.set("pagina", "1");

            fecharSugestoes();

            carregarPagina(url.href, {
                rolarAoIniciar: true,
            });
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

        carregarPagina(link.href, {
            rolarAoIniciar: true,
        });
    });

    /**
     * Restaura páginas visitadas usando Voltar/Avançar.
     */
    window.addEventListener("popstate", () => {
        fecharSugestoes();

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

            fecharSugestoes();

            carregarPagina(
                window.location.href,
                { atualizarHistorico: false }
            );
        }
    });
});