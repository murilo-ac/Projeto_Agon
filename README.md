# Projeto Ágon

Hub centralizado para acompanhar vários esportes num só lugar: calendário de partidas, resultados e estatísticas de jogos e jogadores. Placar ao vivo e notícias estão previstos para versões futuras.

> **Status:** v1 em andamento (fases 0 e 1 concluídas: exploração e infraestrutura).

## Esportes

Futebol (Brasileirão, Libertadores, ligas europeias, seleções), basquete (NBA, FIBA), NFL, tênis (ATP/WTA), Fórmula 1, vôlei (Superliga e seleções) e Olimpíadas.

## Stack

| Camada | Tecnologia |
|---|---|
| Coleta de dados | Python, httpx, APScheduler |
| Backend | Python, FastAPI |
| Banco | PostgreSQL, SQLAlchemy, Alembic |
| Frontend | TypeScript, React, Vite |
| Infraestrutura | Docker Compose, Tailscale |

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
- API: <http://localhost:8000/api/health> (documentação em `/docs`)

