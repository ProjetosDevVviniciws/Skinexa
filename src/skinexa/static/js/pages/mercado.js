"use strict";

document.addEventListener("DOMContentLoaded", () => {
    const resultados = document.querySelector(".market-results");
    const carregamento = document.querySelector("#market-loading");
    const formularioOrdenacao = document.querySelector(".market-sort");

    if (!resultados || !carregamento) {
        return;
    }

    const iniciarCarregamento = () => {
        carregamento.hidden = false;

        resultados.classList.add("is-loading");
        resultados.setAttribute("aria-busy", "true");
    };

    const finalizarCarregamento = () => {
        resultados.classList.remove("is-loading");
        resultados.removeAttribute("aria-busy");

        carregamento.hidden = true;
    };

    if (formularioOrdenacao) {
        formularioOrdenacao.addEventListener(
            "submit",
            () => {
                iniciarCarregamento();
            }
        );
    }

    const linksPaginacao = document.querySelectorAll(
        ".market-pagination a.market-pagination-link"
    );

    linksPaginacao.forEach((link) => {
        link.addEventListener("click", (evento) => {
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

            iniciarCarregamento();
        });
    });

    window.addEventListener(
        "pageshow",
        finalizarCarregamento
    );
});