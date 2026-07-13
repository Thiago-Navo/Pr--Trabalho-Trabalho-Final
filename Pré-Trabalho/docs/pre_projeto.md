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

## 3. Público-Alvo e Contexto
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
[![](https://mermaid.ink/img/pako:eNqtWF1v4jgU_SuRpZF2pVIVVCjwlkI6GwnwTIDVaoWE3NiAV4mdOk7VLdOnfZgf1j-2TiBpYhzIzG4rVcL3ODn369xb9sDnmIAhIGJM0VagcCVWzFI_nz5ZrVbLcqZfPGduW47lzMaO57x_h9Yv9_bc-TU15-CDbQStb99aLb4vbg2tFVC_NajlzB3bY0dHHe_-COjBvvfckT1bXMJBb-aMnDH0SjjN4xGcPbifl579_v39H6gc_811PNv7unTtsss5r9zjo29rZ76AX5c6j-V8aXvuGc81Ep4zsUcunNlTZ7aAc0thv3hwvFzAMoeRvXA-Q88t_Msx1ZdP4diZwPOYUmTO4z4ifcRNbW-kZ_pwlgMOr7_4HB2mhWQCFbbkfM7veD0z115-mCz_gGkU8_QYirdIXZ7Sw8f1BI7siUY_e9sFnEZhCn9302wWdeXZ84Xn2Pfu5FAMJUrlx-f3YE036bT_L7xWsiZY2cuiuff5SfpDmbQoLp_EUlC2tXwSGU5JLBHmJjjFCBODIeBKtDBPhOkWS0JiNPg8jAISEiYL61vFmaNsNPSFRX8ZjgV6RTzmPkWBiRsPyQYxiWKKDGZJArKhL7zG5JMgCZAwhTBENNBpE4aJID5fV_k_ch4QxCwk6TNnAWWVCGMkiaQhsbD0EUbq-bzGjGRS9bFkwyQwhjiXwAshztiHkSAxWhssZr9KITanV2-FBiQSlpWggUSEhCqkyxTKKaQRNyWChOskNpdkLnfNSjJ9byR4xbQJOJIWCmQi0Om5qqat0RCR2NxCQmUF85AyndGTxDWn6EU_9VWlbLmgpuyGajUJuMGw4YKpFsBclIyVaGUC2iCraYwSWVM_ajWi25OaT_-gDXoU1Ec-MpufUXAiWB89oQB6Q1XLszJQftqLSoMoZeVPial8Ay5Nx0-JEqeKExWOH-OgAb_GrzihrSpjq5rijGNYeUZZTQbTPgv5M60ofdHRcYIE1W9W0mRWruNgbN6JTWS6mIt1wu6rBj3xIVItYgLHhO3QDsU7o2u-6jfMyw5WzJmc01cDpDwwssSdmxpqTEntGZU4fmyvzSOZyYXJ3-SxUBKDWRWJ8jmdcrXjz0ixtKX-9JzK2SOfcmbQhdwDKslBVeqqJU4iLmRNO2YLd_M4hkj4SEcjxg-VcaK3B7VjlS7W5CBb3n-AQKbtBgaZlr1S4xZoTmM2KlJ_TJPiIvPSPz7_aRUxq0mjle3MrpclPh13BXdwBbaCYjCUIiFXQC24CqI-gn0KWAG5U3vtCqRLOlYFlQRS7eosvRYh9ifnYX5T8GS7A8MNCmL1KYnSxj1-B1BAMpUd8YRJMOz0b_vZQ8BwD17A8K533e3f3Xbubrq37cGg170Cf4Nhq9_rX7fb3fag27kZDLqDtyvwmr21c307uBvcddrtm95Nv93rqAsEU8nF9PAVRPZNxNu_PMb-mg?type=png)](https://mermaid.live/edit#pako:eNqtWF1v4jgU_SuRpZFmJaiALS3wloZ0NhLgmQCj1QoJuYkBrxI7dZyqU6ZP-zA_rH9snUDSxDiQmd1WqoTvcXLu17m37IHHfAxGAPMxQVuOwhVfUUP-fPhgtNttw55-du25adiGPRvbrv32Axof78y5_VtqzsEHmwWN79_bbbYvbo2MFZC_NajlzBmbY1tFHe_-DOjevHMdy5wtLuGgO7MtewzdEk7x2IKze-fT0jXffrz9A6Xjfzi2a7pflo5ZdjnnlXt89G1tzxfwy1LlsZwvTdc547lCwrUnpuXAmTm1Zws4NyT2swvHywUsc7DMhf0Juk7hX46pvnwKx_YEnseUInMe9x7pI25qupaa6cNZDji8_uJzVJgSkgmU2JLzOb_j9cxce_l-svwTplHM06Mp3iJ1eUoPH9cTaJkThX72tgs4hcIUfnXSbBZ15ZrzhWubd87kUAwlSuXH5_dgTTeptP8vvFKyOljZy6K59_lJ-kOoMIhfPokFJ3RreDjSnOJYIJ_p4MRHPtYYAiZFy2cJ192iSYi1Bo-FUYBDTEVhfa04c5SNhr7Q6G_NMUcviMXMIyjQcWMh3iAqUEyQxixwgDfkmdWYPBwkAeK6EIaIBCptTH3MscfWVf4PjAUYUQMJ8sRoQGglwj4SWJAQG77wkI_k81mNGYmk6mPJ5uNAG-JcAi-EOGMfRhzHaK2x6P0qhVifXrUVGpBIaFaCGhIR4rKQLlMop5BETJcIHK6TWF-Sudw1K8n0vRFnFdMmYEgYKBAJR6fnspq2WkOEY30LcZkVn4WEqowehV9zip7VU09WypZxostuKFeTgGkMG8apbAGf8ZKxEq1MQBtkNY1RImrqR65GZHtS8-kftEEPnHjIQ3rzEwpOBOu9JyRAbahqeVYGyi97UWkQqazsMdGVb8CE7vgxkeJUcaLC8X0cNODX-BUntGVlbGVTnHHMl54RWpPBtM9C9kQqSl90dJwgTtSblTTples4GJt3YhOZLuZinbB7skFPfIhki-jAMaY7tEPxTuuaJ_vNZ2UHK-ZMzsmLBlIeGFnizk0NOaaE8oxKHN-31-aRzORC52_yUCiJxiyLRPqcTrna8aelWNpSf3lO5eyRRxjV6ELuARH4oCp11RInEeOiph2zhbt5HEPEPaSiEWWHyjjR24Pa0UoXK3KQLe8_QSDTdg2DTMteiHYL1KcxGxWpP7pJcZF56R-f_7SK6NWk0cp2ZtfLEp-Ou4I7aIEtJz4YCZ7gFpALroTIj2CfAlZA7OReuwLpku7LgkoCIXd1ml6LEP2LsTC_yVmy3YHRBgWx_JREaeMevwMoIJnKWiyhAox6g-tu9hAw2oNnMBrcXPUHt78Ph91Br3_T6Qxb4BsYtbud68FVt9tPT687_X7vtQVestf2rq6Ht8PbXrfbuekMuje9fgtgnwjGp4fvILKvIl7_BS7u_qo)

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