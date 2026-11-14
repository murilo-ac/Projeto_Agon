# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Cerca de 10 pessoas: o autor e amigos torcedores. Já acompanham futebol, usam apps de placar e leem estatística sem precisar de explicação. Convivem quatro perfis, nenhum secundário: torcedor de clube, eclético multiesporte, analista de dados e quem usa os dados para fantasy e palpites. O aparelho principal é o **celular**, de relance (saber horário, placar ou resultado) e como **segunda tela durante a transmissão**, muitas vezes à noite; o desktop é secundário. Voltam pela rapidez e limpeza e por ter tudo num lugar só (detalhes na seção 1 da IDENTIDADE_VISUAL.md).

## Product Purpose

Hub único para acompanhar vários esportes: agenda de partidas, resultados, estatísticas de jogos e jogadores. Substitui a navegação entre vários sites e apps. Também é projeto de estudo de desenvolvimento web completo.

As tarefas mais frequentes são **ver a agenda do dia** (o que tem hoje, a que horas e os resultados que saíram) e **acompanhar um time** (forma recente, próximos jogos, resultados). A análise de um jogo encerrado e a busca de times vêm depois.

## Positioning

Ferramenta de leitura de jogos com identidade própria e personalidade de arquibancada, para um grupo pequeno. Não é portal de notícias, não é casa de apostas e não é reprodução dos apps de placar existentes.

## Operating Context

- Publicado em `agon.fans` atrás do Cloudflare Access (login por código enviado por e-mail), só para convidados.
- Só leitura: não há contas, escrita, pagamentos nem operações críticas. Favoritos ficam no navegador até existir login (v4).
- Não há placar ao vivo na v1: o resultado chega depois do jogo, por coleta periódica (pós-jogo a cada 20 min, a partir de 2 h após o início). O calendário cobre de ontem até 7 dias à frente; o histórico começa no primeiro dia coletado. **Mesmo assim, as telas já são desenhadas com os três estados de jogo (antes, ao vivo, encerrado)**, para não redesenhar na v2.
- Fuso padrão: America/Sao_Paulo.

## Capabilities and Constraints

- **v1:** futebol (Brasileirão, Copa do Brasil, Libertadores, Sul-Americana, Champions League, amistosos de seleções), dados da API não-oficial da ESPN.
- **API própria:** agenda por dia e competição, detalhe do jogo (placar, pênaltis, agregado, ida/volta, estatísticas dos times, lances com código, escalações com formação, estatísticas por jogador), página do time (dados e jogos), busca de times sem acento e status da coleta (última atualização e intervalo de datas).
- **Por jogador, a ESPN não traz** minutos jogados, passes nem nota.
- **Nomes vêm em inglês** (competições, posições, tipos de lance, estatísticas) e precisam de tradução na interface.
- **Futuro:** basquete, NFL, tênis, F1, vôlei (v1.1+), ao vivo (v2), notícias (v3).
- **Stack do frontend:** TypeScript + Vite + React, já no repositório.

## Brand Commitments

Identidade descrita em `design-system/design-system/IDENTIDADE_VISUAL.md` (revisada em 14/11/2026), que prevalece sobre o kit em `marca/agon/kit/C/` onde divergirem:

- Símbolo **Chave** (mata-mata formando o A; o acento é o campeão).
- Cores: Egeu `#0b5e75` (estrutura), Sinal `#f0602a` (energia e "agora", **em campos grandes**: ao vivo, favorito, seleção ativa), Tinta `#101e23`, Mármore `#f5f4f0`.
- Tipografia: **Anybody** em três combinações fixas (placar 58/900, título 72/800, logotipo 140/800), nunca abaixo de 18 px; **IBM Plex Sans** no texto e nos dados, com números tabulares.
- Cores de clube só na página do time e no detalhe do jogo; agenda e listas usam só as cores do Ágon.
- Anti-padrões da seção 6 da identidade são obrigatórios: sem texto genérico, sem telas montadas em caixas (uma feature não é um card), sem interface estática, com gráficos onde ajudam a ler, sem clichês de esporte.
- O usuário rejeita explicitamente: cara de site de apostas, de painel corporativo genérico, de revista editorial e de cópia do Sofascore.

## Evidence on Hand

- Dados reais coletados da ESPN (jogos de outubro de 2026) e fixtures em `backend/tests/fixtures/`, incluindo um jogo decidido nos pênaltis (Atlético-MG × Flamengo, Copa do Brasil 2025).
- Logos, favicons e tokens em `marca/agon/kit/C/`.
- Não há depoimentos, métricas de uso nem conteúdo editorial; não inventar.

## Product Principles

1. **O dado primeiro.** Cada tela responde uma pergunta de torcedor em segundos; o resto é apoio.
2. **Honestidade sobre o atraso.** Sem ao vivo, a interface diz quando o dado foi atualizado e o que ainda não chegou.
3. **Os times do usuário primeiro.** Nenhum time é privilegiado pela interface em si, mas os favoritos de cada pessoa abrem a agenda e têm destaque próprio.
4. **Rápido primeiro, fundo depois.** A primeira dobra no celular responde à pergunta de relance; a profundidade vem ao rolar ou tocar. O desktop é a mesma ferramenta, expandida.
5. **Pronto para mais esportes.** Estruturas de tela que aceitem basquete, F1 e tênis sem redesenho.

## Accessibility & Inclusion

Contraste mínimo dos tokens (accent escurecido em texto claro); vitória e derrota nunca só por cor; `prefers-reduced-motion` respeitado.
