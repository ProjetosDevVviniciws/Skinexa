const DURACAO_PADRAO_TOAST = 4000;

export function exibirToast(
    mensagem,
    tipo = "info",
    duracao = DURACAO_PADRAO_TOAST
) {
    const container = document.querySelector(
        "#toast-container"
    );

    if (!container) {
        return;
    }

    const toast = document.createElement("div");

    toast.classList.add(
        "toast",
        `toast-${tipo}`
    );

    toast.setAttribute("role", "status");

    const texto = document.createElement("p");

    texto.textContent = mensagem;

    const botaoFechar = document.createElement(
        "button"
    );

    botaoFechar.type = "button";
    botaoFechar.textContent = "Fechar";
    botaoFechar.setAttribute(
        "aria-label",
        "Fechar notificação"
    );

    botaoFechar.addEventListener(
        "click",
        () => {
            removerToast(toast);
        }
    );

    toast.append(
        texto,
        botaoFechar
    );

    container.appendChild(toast);

    window.setTimeout(
        () => {
            removerToast(toast);
        },
        duracao
    );
}

function removerToast(toast) {
    if (!toast.isConnected) {
        return;
    }

    toast.remove();
}