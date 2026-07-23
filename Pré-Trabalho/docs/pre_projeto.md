# Pré-Projeto — TechStock

## 1. Identificação da Equipe
* **Nome do Projeto:** TechStock
* **Integrantes:**

| Nome | GitHub | Responsabilidade |
| :--- | :--- | :--- |
| Thiago Rodrigues | [https://github.com/thiago-navo](https://github.com/thiago-navo) | Front-end (HTML, CSS, JS), lógica de interface e suporte responsivo |
| Mauricio Keiser | [https://github.com/mauriciokeiser](https://github.com/mauriciokeiser) | Back-end Core, Banco de Dados, lógica do sistema e CRUD básico |
| Pâmela Cristina R. Barbosa | [https://github.com/Pamela-Barbosa](https://github.com/Pamela-Barbosa) | Arquitetura MVC, Dashboard (API), lógica do sistema, Controle de Permissões, Diagramas e Gestão de Merges (Maintainer) |

## 2. Elevator Pitch
Uma aplicação funcional para pequenas empresas e setores de estoque de informática que precisam controlar seus produtos, o **TechStock** é uma aplicação web que permite cadastrar, atualizar, consultar, ver relatórios e gerenciar peças no estoque. Diferente de planilhas ou anotações manuais, o sistema centraliza as informações em um único lugar, trazendo agilidade, segurança e eficiência.

## 3. Público-Alvo e Contexto de Uso
* **Quem:** Encarregados ou gerentes de estoque, conferentes, recebedores, despachadores e operadores.
* **Situação:** Utilizado dentro de pequenos galpões, salas comerciais, empresas de informática e lojas de computadores.
* **Por que é melhor:** Centraliza informações, facilita a busca, reduz erros de atualização e mantém o estoque sempre atualizado em tempo real.

## 4. Funcionalidades Principais
1. **Cadastrar componentes:** Para controlar os produtos disponíveis.
2. **Pesquisar produtos:** Por nome ou categoria para encontrá-los rapidamente.
3. **Registrar movimentações:** Entradas e retiradas para manter o estoque atualizado.
4. **Gerenciar itens:** Editar ou excluir produtos cadastrados para corrigir informações.
5. **Dashboard e Relatórios:** Visualização do estoque atual e indicadores para acompanhamento.

## 5. Escopo Negativo
* Não terá sistema de vendas, emissão de notas fiscais ou controle financeiro complexo.
* Não terá pagamentos online, integração com marketplaces ou login com redes sociais.
* Não terá controle por código de barras nem notificações por e-mail.
* Não será um app mobile nativo (apenas Web responsiva).

## 6. Modelo de Dados Preliminar (SQLAlchemy/SQLite)
[![](https://mermaid.ink/img/pako:eNqtV1tv4jgU_itWpJE6ErRcWqA8rJSFdCZaqDsBuqsVEnJjF7xK7NRxqm4vT_swP6x_bE9SAklwuq20vIT43L5z_J1j58nyJWXW0GJqzMlakXCplgLB78sX1Gw2kTO98pyZjY4Wl-6FO7LHNhrhKXIux47nvP7EDTR3rzAa23Mb_W57zne8mDlfU9PcUe7h-bnZlE_oysPjxRyjIVpat-RGcZ8IzZbWR9SlEsxnVKo39QpUz5nYIxdf2lPnco5naOzsrAtwRvbc-YY91xjB6Pe763i292MBJuByl3n2MpvjHwsHHY2w5zlj7KFf0BTcTTD8uXSvnQk8r21cLkjmYYRXufUWyMF6ljMPNgRRho4iopjQK06_GlFeTBZ_lDHNnCma4LnzgeDPudVqgkf2pFCL1CavUI6zRrUCaIqv3XQn7Nefr_9g5CDPns09x_7VnbhjG4AWUZVcbuPkDnAFzmK2sD0Xv6dWgTLB39LK2CNnNkuR2IuxO884UMBQcQs2q61B2W-VqE_5QvrjQiNO0dVvxcVYKy7WSPNIlkiPntGe0vBCwhsZ7_MsmPoi-suwrMgjkbH0OQkMUiFDdgtxSMxJFaNmAbvlD9K07rMgCYgyeGQh4aZIPotM2rEmVJrUOSWUGQSBhAlEZaJMViIJmVHgyzAKWAjNYTQjPpeCBHUxY67Z25ZUa5HECVFcQsehi9J-3kgZMCIQ0fxeioCLkl9KNNM8ZIhqn1ACYWSNmOikvHEFGWU7yUuJddX-_W_6pYu74VFJpUCVesb6UqktRUNJk0DCH8HvWQDPeyLNjCUhF5vUOoSkFDCUPzIKOPSmgdjDELVPuif9k3anbJ2XloWrJJbGCuTT6MN9lyYXKUkNIspiP23G0g7dBpJoRAKdKHK4Dp2xNgoiFpvZqaK0elCOKuA7TWtWyYPBU0iUT0zrcIIHB53sQ9nXEgp_uOmpeD-FauS7wVSWl8lYGtsfZCLsRKKlOSoTlCnmyxXMDnmX1GC7SwB3qZ9LqPYHwv-A6DDWAVYo8hr4-n5CwDTNhaztwLTVQnnPD8bYu5NoPzCIJsZi5Kfap7rlU6O_7rDwoVEOMomAqyblmIkN2ZB4Y8wOehSOhWKOJXE2R_mjQaU4qbNNfG9cw9GnKz5KpdzfHD9VzKwRTSknN7serR1N6QlTe_QYURbuLR-jfy25tkBIZTzmhKhti7d18GfKCgocp1MHIioW12kIeS9NQm66ZyQxU2QNcWs7YyP3A_vFalhrxak11CphDQsuFUBteLWeUoWlpTdwl1ha6aWPws0gCTQcUSI1i4j4U8owt1QyWW-s4S0JYnhLojTk9iNqp5L1_0gmQlvDXvf8NHNiDZ-sB2vYbreOO4Ne53zQGZz1W63TdsP62xo2u-ft4267O2j1253T_lmv-9KwHrO47eNeqzPot9v987NBqzcYdBsWo1xLNX37iss-5l7-BWMjM_I?type=png)](https://mermaid.live/edit#pako:eNqtV91u4jgUfhUr0kgdCdoCLTBcjJSFdCZaqDsBuqMVEnJjF7xK7NRxULc_V3sxD9YX25OUQBKcbistNyE-f985_s6x82j5kjJrYDE14mSlSLhQC4Hg9-kTajabyJlcec7URkfzS_fCHdojGw3xBDmXI8dzXn7hBpq5VxiN7JmN_rA95zueT53PqWnuKPfw9NRsykd05eHRfIbRAC2sW3KjuE-EZgvrPepSCeYzKtWregWq54ztoYsv7YlzOcNTNHJ21gU4Q3vmfMOea4xg9PvddTzb-zEHE3C5yzx7mc7wj7mDjobY85wR9tBXNAF3Ywx_Lt1rZwzPaxuXC5J5GOJlbr0FcrCe5cyDNUGUoaOIKCb0ktPPRpQX4_nPMqapM0FjPHPeEfwpt1qO8dAeF2qR2uQVynHWqFYATfC1m-6E_fLr5R-MHOTZ05nn2L-5Y3dkA9AiqpLLbZzcAa7AmU_ntufit9QqUMb4W1oZe-hMpykSez5yZxkHChgqbsFmuTUo-60S9TFfSH9caMQpuvq9uBhrxcUKaR7JEunRE9pTGl5IeCPjfZ4FU19EfxmWFXkgMpY-J4FBKmTIbiEOiTmpYtQsYLf8XprWfRYkAVEGjywk3BTJZ5FJO9aESpM6p4QygyCQMIGoTJTJSiQhMwp8GUYBC6E5jGbE51KQoC5mzDV73ZJqLZI4IYpL6Dh0UdrPGykDRgQimm-kCLgo-aVEM81Dhqj2CSUQRtaIiU7KG1eQUbaTPJdYV-3f_6ZfurgbHpVUClSpZ6wvldpSNJQ0CST8EXzDAnhuiDQzloRcrFPrEJJSwFD-wCjg0OsGYvcD1DrpnPROWu2ydV5aFi6TWBorkE-jd_ddmlykJDWIKIv9tBlLO3QbSKIRCXSiyOE6dMbKKIhYbGanitLqQTmqgO80rVkl9wZPIVE-Ma3DCR4cdLIPZV9JKPzhpqfi_RSqke8GU1leJmNpbL-TibATiZbmqExQppgvlzA75F1Sg-0uAdylfi6h2h8I_wOiw1gHWKHIK-Dr2wkB0zQXsrYD01YL5YYfjLE3J9F-YBBNjMXIT7UPdcuHRn_dYeFDoxxkEgFXTcoxE2uyJvHamB30KBwLxRxL4myO8geDSnFSZ5v41riGo09XfJRKub85fqiYWSOaUk5udj1aO5rSE6b26DGiLNxb3kf_WnJtgZDKeMwJUdsWr-vgz5QVFDhOpw5EVCyu0xByI01CbrpnJDFTZAVxaztjLfcD-9lqWCvFqTXQKmENCy4VQG14tR5ThYWl13CXWFjppY_CzSAJNBxRIjWLiPhTyjC3VDJZra3BLQlieEuiNOT2I2qnkvX_UCZCW4Nup9fKnFiDR-veGrTaveN2v9vunZ33263O-Xm3Yf1tDZrtbuu40-r0T8-6nfMv7bPTs-eG9ZAFbh13T9v9XqvV-3LeP-32-52GxSjXUk1eP-Oyr7nnfwGTIjQl)

## 7. Wireframes
* **Desktop:** Layout com menu lateral, campo de pesquisa, tabela de produtos, botões de ação e dashboard com cards de resumo.
* **Mobile:** Menu simplificado, busca rápida e listagem otimizada para dispositivos móveis.

### Imagens de wireframes
![Wireframe Login](imagens/LoginDesktop.PNG)
![Wireframe Desktop](imagens/dashboard.PNG)

![Wireframe Mobile](imagens/mobile.PNG)

## 8. Stack Confirmado
* **Flask + Jinja2:** Back-end e páginas dinâmicas.
* **SQLite:** Banco de dados.
* **HTML + CSS Grid + JS Vanilla:** Interface responsiva.
* **GitHub:** Controle de versão com Pull Requests obrigatórios.

## 9. Autoavaliação de Riscos
1. **Medo:** Inconsistência nos cálculos de saldo durante movimentações.
2. **Ausência de membro:** Redistribuição de tarefas priorizando o "caminho feliz".
3. **Caminho Feliz:** Cadastro, busca e registro de entradas/saídas com atualização automática do saldo.