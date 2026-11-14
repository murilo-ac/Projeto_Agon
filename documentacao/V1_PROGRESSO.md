# v1 — Progresso

> Registro do que foi feito na v1 (Fundação, futebol) até 14/11/2026 e do que ainda falta.
> Objetivo da v1: validar o fluxo completo **coleta → banco → API → tela** com um esporte.
> Planejamento geral: [ROADMAP.md](ROADMAP.md). Exploração das fontes: [V0_EXPLORACAO.md](V0_EXPLORACAO.md).

## Resumo

| Fase | Entrega | Status | Commit |
|---|---|---|---|
| 0. Exploração | Formatos reais da ESPN e ajustes no banco | ✅ (falta o teste da API-Sports) | `b1395d9` |
| 1. Infraestrutura | Docker Compose com `db`, `migrate`, `api`, `worker`, `frontend` | ✅ | `b1395d9` |
| 2. Banco | Modelos SQLAlchemy e migração Alembic | ✅ | `775e07e` |
| 3. Coleta | Adapter ESPN, normalização, upsert idempotente | ✅ | `fda5485` |
| 4. Jobs | Calendário, pós-jogo, recuperação, `sync_runs` | ✅ | `0118d65` |
| 5. API | Rotas de competições, agenda, jogo e time | ✅ | `356bc0d` |
| 6. Frontend | Identidade revisada e mockups escolhidos (opção C); telas no código ainda não | 🟡 em andamento | `2b50222` (identidade) |
| 7. Acesso e fechamento | `agon.fans` com Cloudflare Tunnel + Access ✅; revisão final ⏳ | 🟡 em andamento | `4056bd6` (publicação) |

Os testes do backend rodam com `docker compose exec api pytest`. Tudo está no GitHub ([murilo-ac/Projeto_Agon](https://github.com/murilo-ac/Projeto_Agon), branch `main`).

---

## Fase 0 — Exploração

- **ESPN inspecionada:** os endpoints `scoreboard` e `summary` foram analisados com um jogo real do Brasileirão. Estrutura, campos usados e armadilhas estão em [V0_EXPLORACAO.md](V0_EXPLORACAO.md).
- **Ajustes no esboço do banco:** `venue_name` e `venue_city`, `primary_color` nos times, lances em `events.extra` e estatísticas achatadas para `{nome: valor}`.
- **JSON maior que o previsto:** um `summary` tem cerca de **394 KB**, quatro vezes a estimativa do roadmap. Em volume isso continua viável e foi registrado como risco.
- **Sem intervalo de datas no futebol:** a ESPN responde HTTP 400 a `dates=AAAAMMDD-AAAAMMDD`, então o calendário faz uma requisição por dia e por liga.
- **Pendente:** testar a API-Sports para vôlei e NBB. Exige criar conta e chave; o roteiro está em V0_EXPLORACAO.md, seção 4. Isso só bloqueia a v1.2.

## Fase 1 — Infraestrutura

- **Serviços do `docker-compose.yml`:**
  - `db`: PostgreSQL 16, com volume persistente e aceitando conexões só de `127.0.0.1`.
  - `migrate`: aplica `alembic upgrade head` a cada subida e termina.
  - `api` e `worker`: sobem depois do `migrate`.
  - `frontend`: Vite em modo de desenvolvimento.
- **Um código, dois processos:** `api` e `worker` rodam a partir do mesmo `backend/`, com recarga automática por volume montado.
- **Configuração:** `.env` fica fora do Git; o modelo de variáveis está em `.env.example`.
- **Frontend:** esqueleto Vite + React + TypeScript, com proxy `/api` para a API.
- **Validação:** a subida completa foi testada do zero, com banco vazio, migração, coleta e API respondendo.

## Fase 2 — Banco

- **Tabelas:** 13, seguindo a seção 6 do roadmap.
  - Catálogo: `sports`, `competitions`, `seasons`, `teams`, `players`, `team_players`.
  - Eventos: `events`, `event_participants`, `player_event_stats`.
  - Operação: `external_refs`, `raw_payloads`, `sync_runs`.
- **Migração inicial:** `backend/alembic/versions/2c836d0da1ec_schema_inicial.py`. Já cadastra os 6 esportes (football, basketball, nfl, tennis, f1, volleyball).
- **Garantias do esquema:**
  - Chave única em `external_refs (provider, entity_type, external_id)`.
  - `CHECK` no `events.status`.
  - Índices únicos parciais em `event_participants`: por time em esportes coletivos, por jogador em individuais.
- **Campo novo:** `events.details_synced_at` marca quando o detalhe de um jogo encerrado foi coletado.
- **Testes:** usam um banco separado (`agon_test`), criado e migrado automaticamente, com rollback a cada teste.

## Fase 3 — Coleta (ESPN, futebol)

- **Contrato dos provedores:** `backend/app/providers/base.py` define a interface e os formatos internos. Os provedores não conhecem o banco.
- **Adapter da ESPN:** `backend/app/providers/espn.py`.
  - `listar_jogos(liga, dia)` e `detalhar_jogo(liga, id)`; a liga vem no formato `esporte/slug` (ex.: `soccer/bra.1`).
  - Retry com backoff exponencial em 5xx, timeouts e erros de rede (tenacity).
  - HTTP 429 vira `RateLimitError` e não é repetido. Outros 4xx e respostas que não são JSON viram `ProviderError`.
  - Contador de requisições por instância.
- **Normalização:**
  - Status: `pre` vira `scheduled`, `in` vira `live`, `post` vira `final`. Adiados e cancelados são tratados à parte.
  - Placar em número. Jogo agendado não tem placar, porque a ESPN manda `"0"`.
  - Lances com `lado` (`home`/`away`) em vez do id da ESPN.
  - Estatísticas de time e de jogador. Elenco com número da camisa.
- **Gravação idempotente:** `backend/app/repositories/ingest.py` localiza cada entidade pela referência externa. Rodar duas vezes não duplica nada, e uma coleta pobre (só o calendário) não apaga dados ricos (o detalhe).
- **JSON bruto:** toda resposta é guardada em `raw_payloads`.

## Fase 4 — Jobs

- **Jobs, em `backend/app/ingestion/`:**

  | Job | Quando roda | O que faz |
  |---|---|---|
  | Calendário (`calendar.py`) | Todo dia às 5h (horário de Brasília) | Busca de ontem até +7 dias, para cada liga |
  | Pós-jogo (`postgame.py`) | A cada 20 min | Pega jogos iniciados há mais de 2h, nos últimos 7 dias, sem detalhe ou ainda não `final`. Não registra execução quando não há pendências |
  | Recuperação (`recovery.py`) | Ao iniciar o worker | Roda o calendário se o último sucesso tem mais de 24h, e roda o pós-jogo sempre |

- **Controle de execução (`runner.py`):** cada execução vira uma linha em `sync_runs` com status `success`, `partial`, `failed` ou `rate_limited`, mais as requisições usadas e os erros. Cada unidade (uma liga num dia, ou um jogo) é confirmada à parte: um erro desfaz só aquela unidade e o job segue. Um 429 para o job inteiro.
- **Worker (`backend/app/main_worker.py`):** APScheduler, com uma trava para os jobs rodarem um de cada vez.
- **Ligas coletadas:** Brasileirão, Copa do Brasil, Libertadores, Sul-Americana, Champions League e amistosos de seleções. Configuráveis em `ESPN_LEAGUES`; todos os parâmetros estão comentados em `.env.example`.
- **Validação com a ESPN real:** 54 requisições de calendário e 2 de pós-jogo, sem erros, resultando em 26 jogos de 3 competições.

## Fase 5 — API

| Rota | O que devolve |
|---|---|
| `GET /api/health` | Status da API e do banco (503 se o banco cair) |
| `GET /api/competitions?sport=` | Competições conhecidas |
| `GET /api/events?date=&tz=&competition_id=&sport=` | Agenda do dia no fuso informado (padrão: America/Sao_Paulo) |
| `GET /api/events/{id}` | Detalhe: placar, estatísticas dos times, lances e estatísticas por jogador com número da camisa |
| `GET /api/teams/{id}` | Dados do time |
| `GET /api/teams/{id}/events?status=&order=&limit=` | Jogos do time (resultados recentes ou próximos jogos) |

- **Código:** rotas em `backend/app/api/`, formatos de saída em `backend/app/schemas/`, consultas em `backend/app/repositories/queries.py`.
- **Documentação interativa:** <http://localhost:8000/docs>.
- **Testes:** cobrem filtros, fuso, 404 e 422.

## Fase 6 — Frontend (em andamento)

### Feito: identidade visual
Criada com duas skills de terceiros, revisadas e instaladas em `.claude/skills/`, fora do Git. A origem de cada uma está em `.claude/skills/ORIGEM.txt`.

1. **Logo (skill logo-design).**
   - Fluxo: briefing → pesquisa da categoria → 8 conceitos → 3 construídos em SVG → 3 rodadas de ajuste com testes em 16/32 px.
   - Escolhido: **A — Chave**. As linhas de um mata-mata convergem e formam o A; o acento é o campeão.
2. **Identidade (skill brand-identity).**
   - Três conjuntos de paleta e tipografia ao redor da Chave: Holofote, Volt e Ágora. Todos passaram nos testes de contraste, licença, acentos do português e números tabulares.
   - Escolhido: **C — Ágora**. Azul Egeu `#0b5e75`, laranja Sinal `#f0602a`, Bodoni Moda nos títulos e IBM Plex Sans no texto. As duas fontes são OFL 1.1, livres para usar, inclusive no logo.
   - **Revisão de 14/11/2026:** o Bodoni saiu e entrou a **Anybody** (placar, títulos e logotipo); o Sinal passou a ocupar campos grandes; o `accent` claro foi corrigido para `#bb410e`; o público-alvo ganhou seção própria. O conjunto C foi regenerado. Detalhes na IDENTIDADE_VISUAL.md.
3. **Kit final** em `marca/agon/kit/C/`: guia de marca em PDF com 13 páginas, 16 versões do logo, favicons, ícone de app e tokens (`tokens.css` com modo claro e escuro, `tailwind.palette.js`, `fonts.css`).
4. **Regras para as telas** em [design-system/design-system/IDENTIDADE_VISUAL.md](../design-system/design-system/IDENTIDADE_VISUAL.md): princípios, uso do logo, papéis de cor, escala tipográfica, anti-padrões e o mapa da pasta `marca/`.

### Feito: mockups das telas
- Primeira rodada (PR #3) descartada: cada feature virou um card e o resultado parecia genérico.
- Segunda rodada (14/11/2026): três opções para agenda, jogo e time, com dados reais da ESPN. **Escolhida: opção C, "menu de console"**, em modo escuro, inspirada nos menus dos jogos de futebol de 2015 a 2017. Páginas navegáveis em `design-system/telas/c-fifa/`, material comum (tokens, escudos, logo, dados) em `design-system/telas/comum/` e capturas em `design-system/telas/capturas/`.

### Falta
- [ ] Aplicar os tokens e as fontes no frontend.
- [ ] Componentes do design system: card de jogo, placar, tabela de estatísticas, linha do tempo de lances.
- [ ] Tela de **agenda** por data, com navegação entre dias e filtro por competição.
- [ ] Tela de **detalhe do jogo**: placar, estatísticas mandante × visitante em barras divergentes, lances e escalações.
- [ ] Tela do **time**: próximos jogos, resultados recentes e sequência de forma.
- [ ] Estados de carregamento, vazio e erro; modo escuro; `prefers-reduced-motion`.
- [ ] Favicon e ícone do app nos arquivos do frontend.

## Fase 7 — Acesso remoto e fechamento (em andamento)

- [x] Acesso remoto: `agon.fans` via Cloudflare Tunnel + Cloudflare Access, no servidor do Pedro (ver a seção "Publicação" do README).
- [ ] Revisão final do README (como subir, como testar, como acessar).
- [ ] Marcar a v1 como concluída no ROADMAP.

---

## Pendências e riscos conhecidos

| Item | Tipo | Observação |
|---|---|---|
| Teste da API-Sports (vôlei, NBB) | Pendência | Exige conta própria; bloqueia só a v1.2 |
| `round` (rodada) e `competitions.country` vazios | Pendência | Não vêm no `scoreboard` da ESPN; afeta a futura tela de competição |
| JSON bruto ~394 KB por jogo | Risco | Monitorar `raw_payloads`; se crescer demais, descartar `commentary` ou limpar payloads antigos |
| API não-oficial da ESPN | Risco | Pode mudar sem aviso; o adapter isolado limita o impacto e o fallback (API-Sports) está previsto para a v1.2 |

## Como rodar

```bash
cp .env.example .env              # ajuste a senha do banco
docker compose up --build         # sobe db, migrate, api, worker e frontend
docker compose exec api pytest    # testes do backend
```

- **Endereços:** frontend em <http://localhost:5173>, API em <http://localhost:8000/docs>.
- **Requisito no Windows:** o Docker Desktop precisa do **WSL 2**, que se instala com `wsl --install` num PowerShell de administrador e um reinício.
