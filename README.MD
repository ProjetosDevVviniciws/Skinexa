# Skinexa

<p align="center">
  <img src="assets/logo.png" alt="Skinexa Logo" width="180">
</p>

<p align="center">
  <strong>Pesquise, compare e acompanhe o mercado de itens do Counter-Strike 2 em um único lugar.</strong>
</p>

---

## 📖 Sobre o projeto

O **Skinexa** é um projeto pessoal de engenharia de software desenvolvido com o objetivo de centralizar informações relacionadas ao mercado de itens do Counter-Strike 2.

A plataforma reúne dados provenientes de diferentes marketplaces em uma única interface, permitindo que o usuário pesquise itens, compare preços, monitore variações de valor, acompanhe históricos de preços e configure alertas personalizados.

Além de resolver um problema real enfrentado pela comunidade, o projeto também tem como objetivo aplicar boas práticas de desenvolvimento de software, arquitetura, segurança, persistência de dados e integração com APIs externas.

---

## 🎯 Problema

Atualmente, jogadores, colecionadores e interessados no mercado de itens do Counter-Strike 2 precisam acessar diferentes plataformas para:

- pesquisar itens;
- acompanhar preços;
- comparar marketplaces;
- analisar o histórico de preços;
- acompanhar variações de valor;
- configurar alertas.

Essa fragmentação dificulta o acompanhamento do mercado e torna o processo pouco prático.

---

## 💡 Solução

O Skinexa centraliza essas informações em uma única plataforma.

A aplicação permitirá que o usuário:

- pesquise itens do Counter-Strike 2;
- visualize informações detalhadas sobre cada item;
- compare preços entre diferentes marketplaces;
- consulte preços do Steam Community Market;
- acompanhe o histórico e a variação de preços;
- visualize gráficos e indicadores;
- configure alertas personalizados;
- favorite itens para acompanhamento.

A arquitetura foi projetada para permitir a integração progressiva de novos marketplaces, ampliando as possibilidades de comparação de preços ao longo da evolução do projeto.

---

## 🚀 Funcionalidades

### Autenticação

- Login com Steam (OpenID)
- Logout
- Identificação do usuário por meio da conta Steam

### Dashboard

- Visão geral do mercado
- Itens favoritos
- Alertas ativos
- Indicadores de preços
- Variações de mercado
- Gráficos e informações relevantes

### Pesquisa de itens

- Buscar itens do Counter-Strike 2
- Visualizar informações detalhadas
- Filtrar e ordenar resultados
- Consultar histórico de preços
- Comparar valores entre marketplaces

### Comparação de preços

- Steam Community Market
- Skinport
- CSFloat
- Arquitetura preparada para integração com novos marketplaces

### Histórico de preços

- Registro das coletas de preço
- Consulta da evolução histórica
- Variação de preços ao longo do tempo
- Visualização por meio de gráficos e indicadores

### Favoritos

- Adicionar itens aos favoritos
- Remover itens dos favoritos
- Listar itens acompanhados

### Alertas

- Alerta de preço acima de determinado valor
- Alerta de preço abaixo de determinado valor
- Monitoramento dos itens selecionados
- Notificações internas

### Perfil

- Avatar Steam
- Nome de exibição
- SteamID
- Informações públicas da conta utilizadas pela aplicação

### Configurações

- Tema
- Idioma
- Moeda
- Preferências de notificações

---

## 🛠️ Tecnologias

### Backend

- Python
- Flask
- SQLAlchemy
- Flask-Login
- Flask-WTF
- Flask-Migrate

### Frontend

- HTML5
- CSS3
- Bootstrap 5
- JavaScript

### Banco de Dados

- MySQL

### Integrações

- Steam
- Skinport
- CSFloat
- Banco Central do Brasil (BCB)

### Infraestrutura

- Docker
- Docker Compose

### Ferramentas

- Poetry
- Pytest
- Git
- GitHub

---

## 🏗️ Arquitetura

O projeto utiliza uma organização modular, separando responsabilidades entre rotas, serviços, integrações externas, acesso a dados, DTOs e utilitários.

```text
Cliente (Browser)
        │
        ▼
Frontend
HTML / CSS / Bootstrap / JavaScript
        │
        ▼
Flask
Blueprints / Routes
        │
        ▼
Services
Regras e orquestração da aplicação
        │
   ┌────┴─────────────┐
   ▼                  ▼
Database          Integrations
SQLAlchemy Core       │
   │            ┌─────┴─────────────┐
   ▼            ▼         ▼         ▼
 MySQL        Steam    Skinport   CSFloat
```

Essa separação reduz o acoplamento entre as regras da aplicação, persistência e serviços externos, facilitando testes, manutenção e inclusão de novas integrações.

---

## 📂 Estrutura do Projeto

```text
A estrutura completa do projeto será documentada após a consolidação da arquitetura da versão 1.0.
```

---

## 🧪 Testes

O projeto utiliza **Pytest** para testes automatizados das principais camadas da aplicação.

Atualmente, a suíte possui testes envolvendo:

- autenticação;
- tratamento de erros;
- dashboard;
- persistência e histórico de preços;
- integrações externas;
- normalização de dados;
- comparação e consulta de preços;
- rotas;
- services;
- funções utilitárias.

Para executar a suíte:

```bash
poetry run pytest
```

---

## ⚙️ Como executar

```bash
# Clonar o repositório
git clone https://github.com/ProjetosDevVviniciws/Skinexa.git

# Entrar na pasta
cd Skinexa

# Instalar dependências
poetry install

# Executar a aplicação
poetry run flask run
```

---

## 🗺️ Roadmap

### Versão 1.0

- [x] Autenticação com Steam
- [x] Integração inicial com marketplaces
- [x] Estrutura de comparação de preços
- [x] Histórico de preços
- [x] Testes automatizados da base atual
- [ ] Catálogo e pesquisa de itens
- [ ] Comparação completa entre marketplaces
- [ ] Histórico e gráficos de preços
- [ ] Dashboard
- [ ] Favoritos
- [ ] Alertas
- [ ] Notificações
- [ ] Configurações
- [ ] Dockerização
- [ ] Revisão de segurança
- [ ] Testes finais
- [ ] Deploy

### Futuras versões

- [ ] Novos marketplaces
- [ ] Histórico e analytics avançados
- [ ] Dashboard avançado
- [ ] Insights de mercado
- [ ] Aplicativo mobile
- [ ] Push notifications

---

## 📄 Licença

Este projeto está licenciado sob a licença MIT.

Consulte o arquivo **LICENSE** para mais informações.

---

## 👨‍💻 Autor

Desenvolvido por **Vinícius Pinto Gonçalves**.

Projeto desenvolvido para fins de estudo, portfólio e demonstração de conhecimentos em desenvolvimento de software.