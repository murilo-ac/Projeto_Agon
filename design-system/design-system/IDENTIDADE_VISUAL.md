# Identidade visual — Ágon

> Conjunto aprovado: **Ágora** (paleta e tipografia) com o símbolo **Chave**. Outubro de 2026.
> A fonte da verdade são os arquivos gerados em [`marca/agon/kit/C/`](../../marca/agon/kit/C/): o guia em PDF, os logos e os tokens. Este documento resume as regras para quem desenha e programa as telas.

---

## 1. Princípios

- **Preciso e analítico:** a tela é um instrumento de leitura de jogos e números. Os dados vêm primeiro; a decoração, só quando ajuda a ler.
- **Competitivo e intenso:** a tensão aparece em pontos escolhidos, como o placar, o resultado e o lance decisivo, nunca na tela inteira.
- **Neutro a clubes:** a interface cobre todos os times, então não usa cores associadas a nenhum deles. Só os escudos trazem as cores dos clubes.
- **Uma coisa alta por vez:** o contraste do Bodoni nos títulos é o elemento expressivo do sistema. Todo o resto (texto, superfícies, ícones) fica silencioso.
- **Origem grega como ideia, não como enfeite:** o *agṓn* é a disputa e a reunião onde os jogos acontecem. Isso está no nome, no corte do Bodoni e no azul do Egeu, não em colunas, louros ou ornamentos.

## 2. Logo

### Conceito
**Chave.** As linhas de um mata-mata convergem e formam o A: as duas semifinais na base, a final no ápice. O acento agudo é o **campeão**, a única peça em laranja. O losango vazio no centro é a própria chave do torneio.

### Peças

| Peça | Uso | Arquivo |
|---|---|---|
| Assinatura horizontal (símbolo + "Ágon") | Logo primário: cabeçalho do site, documentos | `logo/master-lockup-horizontal.svg` |
| Assinatura empilhada | Espaços quadrados ou estreitos | `logo/master-lockup-stacked.svg` |
| Símbolo sozinho | Avatar, ícone, marca-d'água | `logo/master-symbol.svg`, `logo/symbol-only.svg` |
| Logotipo sozinho | Quando o símbolo já aparece perto | `logo/master-wordmark.svg` |
| Favicon | Aba do navegador | `logo/favicon-16/32/48.svg` e `.png` |
| Ícone de app | PWA, atalho no celular | `logo/app-icon-512.svg` e `.png` |
| Versões por fundo | Fundo claro, escuro, primária ou destaque | `logo/on-*.svg`, `logo/one-color-*.svg`, `logo/full-color-dark.svg` |

Caminhos relativos a `marca/agon/kit/C/`.

### Construção e cores
- O símbolo é desenhado numa grade de 100 unidades. As pernas têm inclinação exata de 1:2 e espessura constante.
- O **corpo da chave** usa a primária (Egeu). O **campeão** usa o destaque (Sinal). O **"Ágon"** usa a cor do texto (Tinta) e é composto em Bodoni Moda 600, em contornos, sem depender da fonte instalada.
- **Fundo escuro, primária ou destaque:** se uma cor não atinge contraste de 3:1, o logo inteiro passa para uma cor só. As versões prontas já resolvem isso; use-as.

### Área de proteção e tamanho mínimo
- **Área livre:** pelo menos **x = 1 × a altura das maiúsculas do logotipo** em todos os lados. O valor foi inferido do desenho; ajuste depois do uso real.
- **Tamanho mínimo:** **20 px** de altura na tela, **7 mm** impresso. Abaixo disso, use o favicon.

### Usos incorretos
- Não distorcer nem esticar.
- Não trocar as cores nem recolorir fora da paleta.
- Não invadir a área de proteção.
- Não reorganizar o símbolo e o nome (por exemplo, o nome antes do símbolo).
- **Não preencher o losango:** sem o vazio, a chave some.
- **Não espelhar o acento:** "Á" vira "À", que é outra palavra.

## 3. Paleta de cores

### Cores da marca

| Nome | HEX | Papel |
|---|---|---|
| **Egeu** | `#0b5e75` | Cor principal: símbolo, cabeçalhos, botões primários, links |
| **Sinal** | `#f0602a` | Destaque: o campeão no logo, resultado, chamadas. Sempre em pequena área |
| **Tinta** | `#101e23` | Texto e o "Ágon" do logo |
| **Mármore** | `#f5f4f0` | Fundo da página |

**Proporção:** áreas grandes ficam com o fundo e a primária. O Sinal é a cor mais forte e por isso ocupa a menor área.

### Papéis de interface (tokens)

| Papel | Claro | Escuro |
|---|---|---|
| `background` | `#f5f4f0` | `#061115` |
| `surface` (cards, painéis) | `#ffffff` | `#101e23` |
| `surfaceAlt` | `#ebeae6` | `#202e33` |
| `border` | `#d5d3cc` | `#35444a` |
| `text` | `#101e23` | `#f1f4f5` |
| `textMuted` | `#4a585d` | `#99a3a8` |
| `primary` / `onPrimary` | `#0b5e75` / `#ffffff` | `#52a6c3` / `#061115` |
| `accent` / `onAccent` | `#cb4811` / `#ffffff` | `#f0602a` / `#061115` |
| `link` | `#16728d` | `#52a6c3` |
| `focus` | `#0b5e75` | `#52a6c3` |
| `success` · `warning` · `danger` · `info` | `#08795e` · `#8f5a06` · `#b4312b` · `#196aaf` | `#3fc6a0` · `#e59b37` · `#fe8477` · `#66b2fd` |

### Regras
- **Sinal original ou escurecido:** o Sinal original (`#f0602a`) é para o logo e para preenchimentos grandes. Em **texto e botões sobre fundo claro**, use o token `accent` (`#cb4811`), que atinge o contraste mínimo.
- **Tons de 80, 50 e 20%:** só em gráficos e fundos, nunca em texto. As escalas completas, do 50 ao 950, estão nos tokens.
- **Modo escuro:** é derivado, com o Egeu mais claro sobre um quase preto azulado. Siga os tokens, não inverta cores à mão.
- **Vitória e derrota:** nunca sinalizar só com verde × vermelho. Some texto ou ícone, pensando em daltônicos.
- **Arquivos:** `marca/agon/kit/C/tokens/tokens.css` (variáveis `--bi-*`, com claro, escuro e `prefers-color-scheme`) e `tailwind.palette.js`. Para outros usos, há `tokens.scss`, `tokens.dtcg.json` e `palette.gpl`.

## 4. Tipografia

| Função | Família | Pesos | Observação |
|---|---|---|---|
| **Títulos** | Bodoni Moda | 600 | Eixo `opsz` alto em títulos grandes; no logotipo, `opsz` 24 para os traços finos não sumirem |
| **Texto e dados** | IBM Plex Sans | 400, 600 | Sempre com números tabulares (`font-feature-settings: "tnum"`) em placares e estatísticas |

### Escala

| Nível | Tamanho | Entrelinha | Fonte |
|---|---|---|---|
| H1 | 64 px | 1.05 | Bodoni Moda |
| H2 | 40 px | 1.1 | Bodoni Moda |
| H3 | 28 px | 1.2 | IBM Plex Sans |
| Corpo | 18 px | 1.5 | IBM Plex Sans |
| Pequeno | 14 px | 1.45 | IBM Plex Sans (+0,01 em de espaçamento) |

### Regras
- **Bodoni só em tamanho grande (H1 e H2).** Abaixo de cerca de 28 px os traços finos se perdem. Nunca use para texto corrido, rótulos ou números de placar.
- **Números de placar, tabelas e estatísticas:** sempre em IBM Plex Sans com `tnum`, para as colunas alinharem.
- **Licença:** as duas fontes são OFL 1.1 e vêm do Google Fonts. Os arquivos não entram no repositório.
- **Carregamento:** use o link e as variáveis prontos em `tokens/fonts.css`.
  - Família de títulos: `"Bodoni Moda", Didot, Georgia, serif`.
  - Família de texto: `"IBM Plex Sans", system-ui, sans-serif`.

## 5. Anti-padrões: o que dá "cara de IA"

Toda tela nova deve ser conferida contra esta lista.

### 5.1 Textos genéricos
- **O problema:** frases que ocupam espaço sem informar. Exemplo rejeitado: "Acompanhe todos os seus esportes favoritos em um só lugar, com dados atualizados e uma experiência incrível."
- **A regra:** o Ágon é uma ferramenta de leitura de jogos, não uma coluna de jornal. Use rótulos, dados e instruções curtas. Nada de subtítulos explicativos, frases de efeito ou textos que repetem o que a tela já mostra. Se um texto pode ser removido sem perda de informação, ele sai. O slogan "Todas as disputas num só lugar" aparece no máximo uma vez, e não em toda tela.

### 5.2 Blocos padronizados
- **O problema:** todos os elementos (busca, filtros, card de jogo, tabela de estatísticas) com exatamente o mesmo desenho: retângulo de bordas arredondadas, borda fina e fundo padrão.
- **A regra:** cada bloco tem um objetivo próprio e deve ser desenhado para ele.
  - Um card de jogo não se parece com um filtro.
  - O placar não se parece com uma tabela.
  - A linha do tempo de lances não se parece com uma lista.

  Primeiro se desenha cada bloco pela sua função; só depois se estuda como encaixar os blocos numa tela única e coesa.

### 5.3 Ausência de estilização e de UX
- **O problema:** nenhuma animação de transição; mudanças de estado instantâneas e sem resposta visual.
- **A regra:** toda interação dá retorno, por exemplo:
  - transição na troca de dia da agenda;
  - abertura do detalhe do jogo;
  - hover e foco;
  - destaque do time selecionado nos jogos.

  O movimento deve ter significado, mostrando de onde algo vem e para onde vai. As durações mudam conforme o contexto, e tudo respeita `prefers-reduced-motion`.

### 5.4 Falta de gráficos
- **O problema:** estatísticas de jogo e de jogador apresentadas só em números soltos e listas.
- **A regra:** use visualizações para ajudar a interpretar os dados. Por exemplo:
  - **barras divergentes** (mandante × visitante) para as estatísticas do jogo: posse, finalizações, faltas;
  - **linha do tempo** dos lances (gols, cartões, substituições) por minuto;
  - **radar (kiviat)** para comparar o perfil de dois jogadores ou times;
  - **sequência de forma** (V/E/D dos últimos jogos) na página do time.

  Esses exemplos não limitam: outros gráficos entram sempre que comunicarem melhor o dado. As cores dos gráficos vêm das escalas dos tokens. Mandante e visitante se diferenciam por luminosidade, e não só pela cor.

### 5.5 Clichês de esporte
- **O problema:** bolas, chamas, raios, linhas de velocidade, escudos genéricos, troféus, louros e itálico pesado "esportivo".
- **A regra:** a energia vem dos dados e do contraste tipográfico, não de ícones de clichê. Ícones de esporte só quando identificam a modalidade (filtro de futebol, NBA, F1) e sempre no mesmo traço e na mesma grade.

---

## 6. O que existe na pasta `marca/`

Tudo o que foi produzido para chegar a esta identidade, na ordem em que foi feito.

### `marca/logo/` — criação do logo (skill **logo-design**)

| Arquivo | O que é |
|---|---|
| `BRIEF.md` | Briefing de design: público, adjetivos, concorrentes, clichês da categoria, mapa de palavras e a lista longa de 8 conceitos |
| `build.py` | Gerador em Python dos conceitos em SVG, com geometria calculada (ângulos exatos e grade) em vez de desenho à mão |
| `concepts/` | Os três conceitos (A Chave, B Logotipo, C Ápice cortado) em três rodadas de ajuste (`-v1` a `-v3`), com assinaturas (`-lockup-`) |
| `renders/` | PNGs das rodadas usados para inspecionar cada versão, mais `preview.png` (folha de testes de 16/32 px, uma cor, invertido) |
| `preview.html` | Folha de testes interativa gerada pela skill |
| `concepts.png` / `concepts.svg` | Folha de apresentação dos três conceitos, a mesma usada na escolha do logo |

O conceito escolhido foi o **A — Chave**, na versão `a-chave-v3.svg`.

### `marca/agon/` — sistema de identidade (skill **brand-identity**)

| Arquivo | O que é |
|---|---|
| `brief.json` | Briefing da marca para a skill: setor, público, atributos, concorrentes, idioma e frases reais para as amostras |
| `make_sets.py` | Gerador dos três conjuntos. Usa a geometria exata da Chave (importada de `marca/logo/build.py`) e define fontes, paletas, eixos e usos incorretos |
| `sets.json` | Os três conjuntos escritos por `make_sets.py`; é a entrada do pipeline |
| `sets/A`, `sets/B`, `sets/C` | Holofote, Volt e Ágora: ficha de identidade, paleta calculada, auditorias e todas as versões do logo de cada um |
| `logo-sheet.png` | Folha de contato dos logos dos três conjuntos (grande, 32 px, 16 px, claro e escuro) |
| `review.png`, `board.png`, `board.html` | Revisão e painel de comparação dos três conjuntos, usados na escolha |
| `table.md` | Tabela-resumo dos conjuntos: mecanismo, fontes, paleta, diferenças e alertas |
| `i18n.json` | Tradução para português dos rótulos da ferramenta (os textos dos cards e do guia) |
| **`kit/C/`** | **Kit final da Ágora**, a parte que o frontend usa |

### `marca/agon/kit/C/` — kit final

| Item | Conteúdo |
|---|---|
| `gon-guidelines.pdf` | Guia de marca com 13 páginas (a ferramenta tirou o "Á" do nome do arquivo) |
| `pages/` | As 13 páginas em PNG: capa, ideia, logo, versões, logo sobre cor e usos incorretos, cores, tipografia, aplicações, grade, modo escuro, acessibilidade, iconografia e imagens |
| `logo/` | 16 versões do logo em SVG e PNG, favicons, ícone de app e os masters |
| `tokens/` | `tokens.css`, `tailwind.palette.js`, `tokens.scss`, `tokens.dtcg.json`, `fonts.css`, `palette.gpl` e `swatches.html` |
| `fonts.md` | Fontes, origem, licença e pesos |

### Como regenerar
Os resultados podem ser refeitos a partir dos geradores. Os comandos rodam a partir de `Projeto_Agon/`, com as skills instaladas em `.claude/skills/`.

```bash
python marca/logo/build.py                                        # conceitos de logo
python marca/agon/make_sets.py                                    # sets.json
python .claude/skills/brand-identity/scripts/brand.py build marca/agon
python .claude/skills/brand-identity/scripts/brand.py kit marca/agon/sets/C --full
```
