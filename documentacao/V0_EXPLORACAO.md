# v0 — Exploração das fontes

> Registro do que foi observado nas respostas reais da ESPN em 27/10/2026 e dos ajustes que isso pede no esboço do banco.

## 1. ESPN: `scoreboard`

Requisição: `GET https://site.api.espn.com/apis/site/v2/sports/soccer/bra.1/scoreboard?dates=20261018` (HTTP 200, ~47 KB, 4 jogos).

Estrutura:

```
{ leagues[], events[], provider }
leagues[0]  → id, slug, name, season{year, startDate, endDate, type}, calendar[], logos[]
events[i]   → id, date (UTC, ISO), name, shortName, season{year, slug}, status, venue, competitions[0]
  status.type → name (STATUS_FULL_TIME), state (pre | in | post), completed, detail
  competitions[0].competitors[2] → homeAway, score (string), winner, form, records[], team{id, displayName, abbreviation, color, logo}
  competitions[0].details[]     → lances (gol, cartão) com minuto, time e atletas envolvidos
  competitions[0].venue         → id, fullName, address{city, country}
```

Pontos importantes:

- `score` vem como **string**; converter para inteiro na normalização.
- O estado do jogo está em `status.type.state` (`pre` / `in` / `post`), mais estável que o `name`. Mapeamento proposto: `pre` → `scheduled`, `in` → `live`, `post` → `final`. Adiados e cancelados aparecem como `name` específico e precisam de tratamento à parte.
- O `scoreboard` já traz os `details` (gols e cartões), então a listagem sozinha basta para o placar e a linha do tempo.
- Uma data sem jogos devolve `events` vazio (HTTP 200), sem erro.

## 2. ESPN: `summary`

Requisição: `GET .../soccer/bra.1/summary?event=401841277` (HTTP 200, **~394 KB**).

Chaves de primeiro nível: `boxscore`, `rosters`, `keyEvents`, `commentary`, `header`, `gameInfo`, `leaders`, `standings`, `lastFiveGames`, `seasonseries`, `odds`, `news`, `videos`, entre outras.

| Chave | Conteúdo | Uso |
|---|---|---|
| `boxscore.teams[]` | `homeAway`, `team`, `statistics[]` (28 itens: `name`, `displayValue`, `label`) | `event_participants.stats` |
| `rosters[]` | `homeAway`, `formation`, `roster[]` com `starter`, `jersey`, `athlete`, `position`, `subbedIn/Out`, `stats[]` | `player_event_stats` e elenco |
| `keyEvents[]` | 28 lances principais | linha do tempo do jogo |
| `commentary[]` | 129 lances narrados | fora da v1 |
| `header` | `season`, `competitions`, `league` | metadados |

Pontos importantes:

- O JSON de um jogo tem ~394 KB, **quatro vezes acima** da estimativa de ~100 KB do ROADMAP. Para 25 jogos/dia seria ~10 MB/dia ≈ 3,6 GB/ano só de JSON bruto. Continua viável, mas a decisão de guardar o JSON bruto deve prever compressão (o JSONB do PostgreSQL já comprime via TOAST) ou descarte do bruto de `commentary`.
- As estatísticas vêm como lista de `{name, displayValue}`, não como objeto. Na normalização, converter para `{name: valor}` em `stats`.
- Cada atleta do `rosters` traz `stats[]` próprio, com os mesmos nomes de campo do time. Dá para montar `player_event_stats` sem outra requisição.
- Os identificadores (`team.id`, `athlete.id`, `event.id`) são do provedor e entram em `external_refs`.

## 3. Outras ligas testadas

Em `dates=20261018`, `bra.copa_do_brazil`, `conmebol.libertadores`, `fifa.friendly` e `basketball/nbb` devolveram 0 eventos. Isso é esperado para uma data sem rodada e **não confirma nem descarta** a cobertura. Para a v1 só o `bra.1` importa; as demais ligas serão validadas quando o adapter aceitar o slug como parâmetro.

## 4. API-Sports (vôlei e NBB)

**Pendente, depende de você.** O teste exige criar a conta grátis e usar a chave pessoal, o que não dá para fazer daqui.

Roteiro (leva ~10 min):

1. Criar conta em <https://dashboard.api-football.com/register> (a mesma chave serve para todos os esportes da família).
2. Em cada esporte, chamar `GET /leagues` com o header `x-apisports-key`:
   - Vôlei: `https://v1.volleyball.api-sports.io/leagues?search=superliga` e `?search=nations`
   - Basquete: `https://v1.basketball.api-sports.io/leagues?search=nbb`
3. Registrar aqui se existem a liga, a temporada 2026 e jogos com placar.

Resultado: _a preencher_.

Isso só bloqueia a **v1.2**. A v1 (futebol) pode seguir sem esse resultado.

## 5. Ajustes no esboço do banco

Decididos com base no que foi observado. O diagrama e as tabelas da seção 6 do ROADMAP continuam valendo, com estas mudanças:

| Mudança | Motivo |
|---|---|
| `events.status` mapeado de `status.type.state` (`pre`/`in`/`post`) | Campo estável da ESPN |
| `events.extra` guarda os lances (`details` do scoreboard, `keyEvents` do summary) na v1 | Os lances só serão lidos pela tela do jogo; tabela própria fica para quando houver consulta transversal (ex.: artilharia) |
| `events.venue` passa a ser `venue_name` + `venue_city` (texto) | A ESPN já entrega nome e cidade; uma tabela `venues` não se justifica ainda |
| `teams` ganha `primary_color` | A ESPN devolve `color` do time; útil para a interface |
| `event_participants.stats` guarda objeto `{nome: valor}` | A lista original é achatada na normalização |
| `raw_payloads` com índice em (`provider`, `endpoint`, `fetched_at`) | Reprocessar sem nova requisição exige achar o payload rápido |
| `seasons.label` = `league.season.year` (ex.: `"2026"`) | O campo vem direto de `leagues[0].season` |
