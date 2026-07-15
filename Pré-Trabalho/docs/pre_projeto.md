# Pré-Projeto — TechStock

## 1. Identificação da Equipe
* **Nome do Projeto:** TechStock
* **Integrantes:**

| Nome | GitHub | Responsabilidade |
| :--- | :--- | :--- |
| Thiago Rodrigues | [https://github.com/thiago-navo](https://github.com/thiago-navo) | Front-end (HTML, CSS, JS), lógica de interface e suporte responsivo |
| Mauricio Keiser | [https://github.com/mauriciokeiser](https://github.com/mauriciokeiser) | Back-end Core, Banco de Dados, lógica do sistema e CRUD básico |
| Pâmela Cristina | [https://github.com/Pamela-Barbosa](https://github.com/Pamela-Barbosa) | Arquitetura MVC, Dashboard (API), lógica do sistema, Controle de Permissões, Diagramas e Gestão de Merges (Maintainer) |

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
[![](https://mermaid.ink/img/pako:eNqlWG1v4jgQ_itRpJV2pVK1hdIt31JIe9EC6QY4nU6VkBsb8CmxU8epeqX9dB_2h_WP3TiQkBeHwh2VipgZe96fmWRt-hwTs2cSMaBoKVD4IB6YAZ8vX4xWq2XYo3vPnliGbdjjge3ZH79c4-uNNbG_KXYmvOH1XePtrdXib0Z-rGc8mPCXiW2pW6m-O5561tQaT-39grfWjef0D5BzvbHdtweuV5CrOARKb527mWd9_Pr4xwW_fnNsz_J-zhyr6FHRtvT2de7k3J5M3Z-zqi2aE7PJzPIct9kYzx5afccdWyN7PHUnxsA27j13MJu6JVusqX3neo6V3ZvJlA0YuQN76O6Xyb4LEd3KjyyvX83XhpYJbK5v9GXowmUFqzMDtsdTdvn6Qrqahba33w5nf7gqPlnwNdWXJ2ZbDtuf86Hbt4aVa1NNWWL3yBXM0KtpqIsFDVbIwMT4GiFBmJxT_E0btpH7u6Oyn9ejZ02mnm3dOENnYA1KjhaNzs5VM9xkZZN8VqN7xGqJvlOJsPr2ZKIMtmYDZ5qWZ8HUyrVwZr49UL63hiDrjKI-lEmDYuP-R5EYS0HZ0vBJpKGSWCLMdeIUI0w0jIAD7GGeCN0ploREy_B5GAUkhMzm3HdNXde8IWEkSIzmqVcnxu2PqkASJ0hQrgR2zHdN3x53deYP8ilnKGgKRkwlWaBHQf2S6ireHp4kFv2lIQv0injMfYoCnZE8BCOYRDFFVUWSBGRBX7iO7pMgCZDQVUWIaFCLF8NEEL8SavV55DwgiBlI0mfOAspKocJIEklDYmDpI4xABW9gI5mUHSzwMAm0IS6Okf-WYoiePnlVZPg8i4rocyYFkpAPUo-UEsgB7nN7CmRJI66LOQnnScy1DmQT5eDqU6ojwXGRtQg4kgYKZCJQnQ7ls9QyIhLrYUBARjAPKasa9SRxAxW91GIMdbHkgiJ9hEPY0QIdJJQGw2HpVPFIJG9MF-yDdFkraPUPbYAB-UjPftbAyq7gQUDXLcqkBRcMmhdzsbNKX8GlQf0__S1BAIwN_pQ0FHjAm0r_KYG2KDldsnc3TA-z9RhFNRegfJbQPPv9xOAoZc3ZV10Z8mdaGmx7R1Mty9pIZOvAUa17CJDny0AT9PvQ0TVPImgonXBM2AqtULzSeudDg2Je9LHETtGevmpEivMkTWJ9qHyKtLsYw6STFSXlCZI_LhwV7RSDdDFJHnN40rChoiAualA2TtDqFlN-vDjKyBAJv7YTIMY3qakBywawavGsNGn6XHOcGSkga-xI0eaVajdQfaRSfFdeNZpYBvp8jz4MUhp7dmtUFc2zPmtEmw0d7tN5CDmIVbhBI-wpTRKMP3Mdk-oW-iQmAi1BbyPgrPhuYL-bJ-ZSUGz2pEjIiQnbOyAG_DTXaShNuYKl_cFUDyEYlswkkPAswtSxCLE_OQ-zk4Iny5XZW6Aghl9JpFRuX5HkVJHiap8nTJq99tlleonZW5svZq910TntdL932u3L8-vuWbcD3L-BfN69Pj3vdNvAu2h3L9tXnfcT8zVVfHF61b04-969vupcnneur09MgqnkYrR5RZO-qXn_FzGhTc8?type=png)](https://mermaid.live/edit#pako:eNqlWNtu4kgQ_RXL0kgzEkS5MNzeHHCy1gDOGFitVpFQx91Ar-xup92OsiE87cN8WH5sywYbX9oEdokURFV11_1U2Rvd5ZjofZ2IIUUrgfxH8cg0-Hz5ojWbTc0cPzjm1NBMzZwMTcf8-GVrX2-NqfktZqfCO97A1t7fm03-rmXH-tqjDn-p2J66lxrYk5ljzIzJzDwueGfcOtbgBDnbmZgDc2g7ObmSQ6D0zrqfO8bHr49_bPDrN8t0DOfn3DLyHuVtS27fZE4uzOnM_jkv26I4MZ_ODcey641xzJExsOyJMTYnM3uqDU3twbGH85ldsMWYmfe2YxnpvalM0YCxPTRH9nGZ9DsX0b382HAG5XztaKnA7vpaX0Y2XJazOjVgfzxhF6_PpateaH_73Wj-hx3HJw2-ovqyxOzLYf9zMbIHxqh0baIpTewRuZwZajU1dbGk3hppmGhfAyQIkwuKvynDNrZ_t-LsZ_XoGNOZYxq31sgaGsOCo3mj03PlDNdZWSef1ugRsUqi7-NEGANzOo0NNuZDa5aUZ87U0rVwZrE_ULy3giCblBJ_KJMaxdrDjzwxlIKyleaSQEEloUSYq8QpRpgoGB4H2MM8EqpTLPKJkuFyP_CID5nNuFtFXVe8IX4gSIgWiVcN7e5HWSAKIyQojwUOzK2ib8-7OvUHuZQz5NUFI6SSLNGToG5BdRlvT08SC_5SkAV6QzzkLkWeykjugxFMopCisiJJPLKkr1xFd4kXeUioqsJH1KvEi2EiiFsKdfx54twjiGlI0hfOPMoKocJIEkl9omHpIoxABa9hIxkVHczxMPGUIc6Pkf-WYoieOnllZPg8izHR5UwKJCEfpBqpWCADuM_tyZElDbgq5sRfRCFXOpBOlJOrL1YdCI7zrKXHkdSQJyOBqnQon5WSEZBQDQMCMoK5T1nZqGeJa6jotRJjqIsVFxSpI-zDjuapIKEwGE5LZxyPSPLadME-SFeVgo7_oR0wIBep2S8KWDkUPAiouiU2ackFg-bFXBysUldwYVD_T38LEABjgz9HNQXu8brSf46gLQpOF-w9DNPTbD1HUcUFKJ8VNM9xPzE4Sll99uOu9PkLLQy2o6OpkmVlJNJ14KzWPQXIs2WgDvpd6OiKJwE0lEo4JGyN1ihcK71zoUExz_tYYCdoT98UIvl5kiSxOlQ-RdpDjGHSyZKS4gTJHhfOinaCQaqYRE8ZPCnYUFEQl3hQ1k7Q8hZTfLw4y0gfCbeyEyDGd6mpAMsOsCrxLDVp8lxznhkJICvsSNDmjSo3UHWkEnyPvao1sQj02R59GqTU9uzeqDKap31WizY7Otyn8hByEMbhBo2wp9RJMP7CVUyqWuijkAi0Ar21gLPmh4G91Rv6SlCs96WISEOH7R0QA37qmySUulzD0v6oxw8hGJbMyJPwLMLiYwFif3LupycFj1Zrvb9EXgi_oiBWuX9FklFFgqsDHjGp9687neQSvb_RX_V-86p70Wp3W9e9m063873V7XUb-t9Av-l1Lq5a7ZvW5eVN96rda28b-lui-Pqi076-7LZ7ndb3q1av19AJppKL8e4VTfKmZvsvO89N7g)

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
