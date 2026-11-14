# Projeto Ágon

Hub centralizado para acompanhar vários esportes num só lugar: calendário de partidas, resultados e estatísticas de jogos e jogadores. Placar ao vivo e notícias estão previstos para versões futuras.

> **Status:** v1 em andamento. Coleta, banco e API prontos e publicados em [agon.fans](https://agon.fans) (só para convidados); faltam as telas (fase 6) e o fechamento da v1 (fase 7).

## Esportes

Futebol (Brasileirão, Libertadores, ligas europeias, seleções), basquete (NBA, FIBA), NFL, tênis (ATP/WTA), Fórmula 1, vôlei (Superliga e seleções) e Olimpíadas.

## Stack

| Camada | Tecnologia |
|---|---|
| Coleta de dados | Python, httpx, APScheduler |
| Backend | Python, FastAPI |
| Banco | PostgreSQL, SQLAlchemy, Alembic |
| Frontend | TypeScript, React, Vite |
| Infraestrutura | Docker Compose, Cloudflare Tunnel + Cloudflare Access |

## Como funciona

Um processo **worker** coleta dados de APIs esportivas (ESPN, Jolpica-F1, API-Sports) e grava no PostgreSQL. Uma **API** em FastAPI lê o banco e entrega os dados ao **frontend** em React.

```
APIs externas → worker → PostgreSQL → api → frontend → usuário
```

## Documentação

- [Roadmap](documentacao/ROADMAP.md): objetivo, fontes de dados, stack, arquitetura, esboço do banco, versões e decisões.
- [v0: exploração](documentacao/V0_EXPLORACAO.md): formatos reais da ESPN e ajustes no banco.

## Como rodar

```
cp .env.example .env      # ajuste a senha do banco
docker compose up --build
```

- Frontend: <http://localhost:5173>
- API: <http://localhost:8000/api/health> (documentação interativa em <http://localhost:8000/docs>)

As migrações do banco são aplicadas automaticamente pelo serviço `migrate` a cada subida. O worker coleta os dados da ESPN sozinho ao iniciar e depois em ciclos (calendário às 5h; pós-jogo a cada 20 min). O histórico das execuções fica na tabela `sync_runs`.

### Rotas da API

| Rota | O que devolve |
|---|---|
| `GET /api/competitions?sport=football` | Competições conhecidas |
| `GET /api/events?date=2026-10-18&tz=America/Sao_Paulo&competition_id=&sport=` | Agenda do dia |
| `GET /api/events/{id}` | Detalhe do jogo: placar, estatísticas, lances e jogadores |
| `GET /api/teams/{id}` | Dados do time |
| `GET /api/teams/{id}/events?status=final&order=desc&limit=20` | Jogos do time |

### Testes

```
docker compose exec api pytest
```

Os testes usam um banco separado (`agon_test`) criado automaticamente no mesmo PostgreSQL.

## Publicação

O Ágon está no ar em **<https://agon.fans>**, só para convidados.

```
usuário → Cloudflare Access (login) → Cloudflare Tunnel → frontend (Vite) → api
```

- **Onde roda:** no servidor do Pedro, com este mesmo `docker compose`, a partir do `main` deste repositório.
- **Login:** o Cloudflare Access fica na frente do site inteiro, inclusive de `/api`. Quem não está na lista não chega ao servidor. A entrada é por código enviado por e-mail (One-time PIN), e a sessão dura uma semana.
- **Pedir acesso:** o e-mail precisa estar na política de acesso. O domínio, o túnel e essa lista ficam na conta Cloudflare do Pedro; peça a ele para incluir alguém.
- **Sem portas abertas:** o túnel liga o servidor à Cloudflare de dentro para fora. No servidor, as portas ficam presas a `127.0.0.1` pelo `.env` (ex.: `FRONTEND_PORT=127.0.0.1:5173`).
- **Domínio no Vite:** o `.env` do servidor tem `FRONTEND_ALLOWED_HOSTS=agon.fans,www.agon.fans`. Sem isso, o Vite responde 403 a quem chega pelo domínio.
- **Atualizar o site:** depois do merge no `main`, rodar no servidor `git pull && docker compose up -d --build`. Isso recria os containers que mudaram e aplica as migrações novas.
- **Ainda é ambiente de desenvolvimento:** o site roda com o servidor do Vite e o `uvicorn --reload`. Atrás do login isso é aceitável; antes de abrir para mais gente, o certo é trocar por um build de produção.

