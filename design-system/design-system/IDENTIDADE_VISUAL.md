# Identidade visual — Ágon

> Símbolo **Chave** e cores **Egeu** e **Sinal**, aprovados em outubro de 2026.
> **Revisão de 14/11/2026:** a primeira rodada de mockups foi descartada. Mudaram o público-alvo (seção 1, nova), a distribuição das cores (seção 4), a fonte de títulos (seção 5: Anybody) e a regra das áreas de conteúdo (seção 6.2).
> Os arquivos gerados estão em [`marca/agon/kit/C/`](../../marca/agon/kit/C/): logos, tokens e o guia em PDF. **Onde o kit e este documento divergirem, vale este documento.** O kit foi regenerado em 14/11/2026 com a Anybody e o `accent` corrigido, mas a escala tipográfica e o link de fontes do guia em PDF e do `fonts.css` são os padrões da ferramenta. Para isso, siga a seção 5.

---

## 1. Público-alvo e objetivo da marca

### Quem usa
O Ágon é fechado, para um grupo de convidados (cerca de 10 pessoas). Dentro do grupo convivem quatro perfis, e **nenhum é secundário**:

| Perfil | O que procura | Onde isso fica na tela |
|---|---|---|
| **Torcedor de clube** | Tudo sobre o próprio time: quando joga, quanto ficou, como está | Favoritos no topo da agenda; página do time |
| **Eclético** | O que está acontecendo hoje em todas as ligas e esportes | Agenda do dia, com todas as competições |
| **Analista** | Números e comparações: estatísticas, forma, perfil de times e jogadores | Camada de profundidade do jogo e do time (gráficos) |
| **Fantasy e palpites** | Dados para decidir: forma recente, quem jogou, escalações | Escalações, forma e estatísticas por jogador |

### Quando e onde usa
- **Celular, de relance:** abre para saber uma coisa (o horário, o placar, o resultado) e fecha. O celular é o aparelho principal; o computador é secundário.
- **Segunda tela durante o jogo:** fica aberto enquanto assiste à transmissão, muitas vezes à noite e com a luz baixa.

### Por que volta
- **Rapidez e limpeza:** abre e vê o que importa em segundos, sem notícia, anúncio ou ruído.
- **Tudo num lugar só:** várias ligas e esportes juntos, sem pular entre apps.

### Objetivo da marca
Ser o primeiro lugar que o grupo abre quando a pergunta é "que horas é o jogo?", "quanto está?" ou "quanto foi?", e o lugar onde fica depois, quando quer entender o jogo.

### Regras que saem daqui
1. **Rápido primeiro, fundo depois.** A primeira dobra de cada tela responde à pergunta de relance (placar, horário, situação do jogo) sem rolar e sem tocar. A profundidade (gráficos, comparações, escalações completas) vem ao rolar ou ao tocar. Quem só quer o placar nunca procura o placar no meio dos dados.
2. **Pensado para o ao vivo desde já.** O placar ao vivo chega na v2, mas toda tela é desenhada com os três estados de um jogo: **antes**, **ao vivo** e **encerrado**. O ao vivo é o estado mais forte do sistema (seção 4).
3. **Favoritos desde já.** O usuário marca times favoritos. Os jogos deles abrem a agenda e têm destaque próprio. Até existir login (v4), os favoritos ficam guardados no navegador.
4. **Densidade equilibrada.** Listas que se leem num passar de olhos, com respiro, e destaques grandes onde importa: o placar, o jogo ao vivo, o jogo do favorito. Nem painel apertado, nem tudo gigante.
5. **Celular primeiro.** Toda tela nasce no celular (cerca de 390 px) e depois se expande. Alvos de toque com pelo menos 44 px; o que se usa com o jogo rolando fica ao alcance do polegar.
6. **Modo escuro de primeira classe.** Por causa da segunda tela à noite, o escuro não é um tema derivado: cada tela é conferida nos dois modos.
7. **Personalidade de arquibancada.** Energia de estádio: cor em campos grandes, contraste forte de escala, ritmo. A energia vem da cor, da tipografia e dos dados, nunca de ícones de clichê (seção 6.5).

## 2. Princípios

- **O dado é o espetáculo:** a tela é um instrumento de leitura de jogos. A energia de arquibancada se aplica ao dado (o placar enorme, a faixa do ao vivo, a sequência de forma), não a enfeites em volta dele.
- **Intensidade onde há disputa:** a tensão cresce com o estado do jogo. Um jogo encerrado é calmo; um jogo ao vivo é a coisa mais forte da tela.
- **Neutro nas telas comuns, do clube nas telas do clube:** agenda e listas usam só as cores do Ágon. A página do time e o detalhe do jogo assumem as cores dos clubes (seção 4).
- **Uma voz forte por tela:** cada tela tem uma protagonista, desenhada grande e com cor. O resto se organiza em volta dela e fica mais silencioso.
- **Origem grega como ideia, não como enfeite:** o *agṓn* é a disputa e a reunião onde os jogos acontecem. Isso está no nome, na Chave e no azul do Egeu, não em colunas, louros ou ornamentos.

## 3. Logo

### Conceito
**Chave.** As linhas de um mata-mata convergem e formam o A: as duas semifinais na base, a final no ápice. O acento agudo é o **campeão**, a única peça em laranja. O losango vazio no centro é a própria chave do torneio.

### Situação na revisão
- **O símbolo fica** como está, com as mesmas cores.
- **O logotipo "Ágon" mudou:** saiu do Bodoni Moda e agora é desenhado na **Anybody, largura 140 e peso 800** (seção 5), em contornos. Os arquivos de assinatura foram regenerados em 14/11/2026.
- **Em aberto:** ao lado do logotipo largo e pesado, o símbolo ficou leve e pequeno, porque os traços da Chave são mais finos que os das letras. O equilíbrio entre os dois ainda será revisto.

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
- O **corpo da chave** usa a primária (Egeu). O **campeão** usa o destaque (Sinal). O **"Ágon"** usa a cor do texto (Tinta), em contornos, sem depender da fonte instalada.
- **Fundo escuro, primária ou destaque:** se uma cor não atinge contraste de 3:1, o logo inteiro passa para uma cor só. As versões prontas já resolvem isso; use-as.

### Área de proteção e tamanho mínimo
- **Área livre:** pelo menos **x = 1 × a altura das maiúsculas do logotipo** em todos os lados. Ajustar quando o logotipo novo existir.
- **Tamanho mínimo:** **20 px** de altura na tela, **7 mm** impresso. Abaixo disso, use o favicon.

### Usos incorretos
- Não distorcer nem esticar.
- Não trocar as cores nem recolorir fora da paleta.
- Não invadir a área de proteção.
- Não reorganizar o símbolo e o nome (por exemplo, o nome antes do símbolo).
- **Não preencher o losango:** sem o vazio, a chave some.
- **Não espelhar o acento:** "Á" vira "À", que é outra palavra.

## 4. Cores

### Cores da marca

| Nome | HEX | Papel |
|---|---|---|
| **Egeu** | `#0b5e75` | Estrutura: as faixas e superfícies que organizam a tela, o mandante nos gráficos, links |
| **Sinal** | `#f0602a` | Energia e "agora": ao vivo, o jogo em foco, o favorito, a seleção ativa, o visitante nos gráficos |
| **Tinta** | `#101e23` | Texto, e texto sobre o Sinal |
| **Mármore** | `#f5f4f0` | Fundo da página no modo claro |

### O que mudou e por quê
A regra antiga dizia que o Sinal ocupa "sempre pequena área". Nos mockups ele apareceu só num número do placar e no acento do logo: o site ficou bege e azul, e a cor que dá energia à marca sumiu. Na revisão, **o Sinal passa a ocupar campos grandes**, com um papel claro: ele marca o que está acontecendo agora e o que é do usuário.

### Distribuição
Cada cor tem um papel, e cada papel aparece em campo grande quando a tela pede:

| Cor | Em campo grande (faixas, fundos, superfícies) | Em detalhe |
|---|---|---|
| **Egeu** | Cabeçalho do jogo encerrado, faixa da data na agenda, fundo da área de destaque da página do time | Links, foco, linhas e eixos de gráfico |
| **Sinal** | Faixa ou fundo do jogo **ao vivo**, a linha do jogo do **favorito**, o dia selecionado na agenda, o **próximo jogo** do time | O minuto do ao vivo, o placar do vencedor, marcas de gol na linha do tempo |
| **Mármore / fundo escuro** | O resto da página | — |

- **Meta por tela:** toda tela tem pelo menos **uma área grande em Sinal** quando existe algo "agora" (ao vivo, favorito, próximo jogo) e pelo menos **uma área grande em Egeu**. Uma tela só bege, ou só com cor em textos pequenos, está errada.
- **Ao vivo é a área mais forte do sistema:** fundo Sinal, texto Tinta e o minuto em destaque. Nenhum outro elemento usa a mesma combinação.
- **Mandante × visitante, fora das telas de clube:** Egeu para o mandante e Sinal para o visitante. Azul e laranja continuam distinguíveis para os tipos mais comuns de daltonismo, e os dois têm luminosidades diferentes.

### Cores dos clubes
O banco guarda a cor principal de cada time (`teams.primary_color`).

- **Onde entram:** só na página do time e no detalhe do jogo. Ali, as faixas, as barras das estatísticas e a forma do time usam as cores dos clubes no lugar de Egeu e Sinal.
- **Onde não entram:** agenda, listas de jogos e qualquer tela que reúna vários times. Ali valem só as cores do Ágon; os escudos já identificam os clubes.
- **Proteções:**
  - Cor de clube como fundo de texto só se o texto atingir 4,5:1. Se não atingir, a cor vira faixa ou borda, e o texto fica no fundo normal.
  - Se as cores dos dois clubes de um jogo forem parecidas (por exemplo, dois times vermelhos), o visitante usa a versão clara ou escura da sua cor, para os dois lados se distinguirem pela luminosidade.
  - Sem cor cadastrada, o mandante usa Egeu e o visitante usa Sinal.

### Combinações de contraste (calculadas)

| Texto | Fundo | Contraste | Uso |
|---|---|---|---|
| Tinta `#101e23` | Sinal `#f0602a` | **5,20:1** | Texto de qualquer tamanho sobre o Sinal: é a combinação do ao vivo |
| Fundo escuro `#061115` | Sinal `#f0602a` | **5,84:1** | Idem, no modo escuro |
| Branco | Sinal `#f0602a` | 3,28:1 | **Só texto grande** (24 px, ou 19 px em negrito) |
| Branco | Egeu `#0b5e75` | **7,31:1** | Qualquer texto |
| Mármore `#f5f4f0` | Egeu `#0b5e75` | **6,64:1** | Qualquer texto |
| Sinal `#f0602a` | Mármore `#f5f4f0` | 2,98:1 | **Nunca em texto**; só em formas, faixas e barras |
| Sinal `#f0602a` | Egeu `#0b5e75` | 2,23:1 | **Nunca um sobre o outro em texto**; lado a lado em gráfico, só com separação |
| `accent` novo `#bb410e` | Mármore `#f5f4f0` | **4,92:1** | Texto laranja sobre o fundo claro |

### Papéis de interface (tokens)

| Papel | Claro | Escuro |
|---|---|---|
| `background` | `#f5f4f0` | `#061115` |
| `surface` | `#ffffff` | `#101e23` |
| `surfaceAlt` | `#ebeae6` | `#202e33` |
| `border` | `#d5d3cc` | `#35444a` |
| `text` | `#101e23` | `#f1f4f5` |
| `textMuted` | `#4a585d` | `#99a3a8` |
| `primary` / `onPrimary` | `#0b5e75` / `#ffffff` | `#52a6c3` / `#061115` |
| `accent` / `onAccent` | **`#bb410e`** / `#ffffff` | `#f0602a` / `#061115` |
| `link` | `#16728d` | `#52a6c3` |
| `focus` | `#0b5e75` | `#52a6c3` |
| `success` · `warning` · `danger` · `info` | `#08795e` · `#8f5a06` · `#b4312b` · `#196aaf` | `#3fc6a0` · `#e59b37` · `#fe8477` · `#66b2fd` |
| **novo** `live` / `onLive` | `#f0602a` / `#101e23` | `#f0602a` / `#061115` |
| **novo** `band` / `onBand` | `#0b5e75` / `#f5f4f0` | `#0b5e75` / `#f1f4f5` |
| **novo** `favorite` | `#f0602a` | `#f0602a` |

- **Correção do `accent`:** o valor antigo (`#cb4811`) dava 4,26:1 sobre o Mármore, abaixo do mínimo de 4,5:1 para texto pequeno. O novo `#bb410e` dá 4,92:1 sobre o Mármore e 4,50:1 sobre o `surfaceAlt`.
- **Tokens de gráfico** (mandante × visitante nas telas comuns), validados em 14/11/2026 com o validador de paleta da skill de visualização de dados (faixa de luminosidade, saturação mínima, separação para daltonismo e contraste com o fundo). O Egeu e o Sinal originais reprovam como cores de série: o Egeu tem saturação baixa demais e o Sinal fica abaixo de 3:1 sobre o Mármore.

  | Token | Claro | Escuro |
  |---|---|---|
  | `chart-home` (mandante) | `#0686a8` | `#2a8fb0` |
  | `chart-away` (visitante) | `#cb4811` | `#f0602a` |
- **`live`, `band` e `favorite`** são os tokens dos campos grandes de cor. Componentes usam esses nomes, não os HEX, para que a distribuição possa ser ajustada num lugar só.

### Regras
- **Sinal original × `accent`:** o Sinal original (`#f0602a`) é para áreas, formas e o logo. Texto laranja sobre fundo claro usa o `accent`.
- **Tons de 80, 50 e 20%:** em gráficos e fundos, nunca em texto. As escalas completas, do 50 ao 950, estão nos tokens.
- **Modo escuro:** segue os tokens, não inverte cores à mão. O Sinal sobre o fundo escuro funciona sem ajuste (5,84:1).
- **Vitória, empate e derrota:** nunca só com verde × vermelho. Sempre com letra (V, E, D) ou ícone.

## 5. Tipografia

### Decisão (14/11/2026)
**O Bodoni Moda saiu.** O contraste de traços finos e grossos dava um ar de revista de moda que não combina com arquibancada, e o título serifado gigante repetido em cada seção reforçava o molde repetitivo (seção 6.2).

| Função | Família | Por quê |
|---|---|---|
| **Placar, títulos e logotipo** | **Anybody** | Um eixo de largura extremo (50 a 150) dá uma voz própria ao Ágon: o placar estreito e pesado de painel de estádio e o logotipo largo saem da mesma fonte. É pouco vista em sites de esporte. |
| **Texto, rótulos e dados** | **IBM Plex Sans** | Já era a fonte de texto. É neutra ao lado da Anybody e muito legível em tamanho pequeno no celular. |

A Anybody foi escolhida entre quatro candidatas aplicadas à mesma tela de celular (comparativo de 14/11/2026). O risco dela é virar enfeite, porque cada tamanho e cada largura chamam atenção. Por isso as regras abaixo limitam o que pode variar.

### Larguras e pesos permitidos
A Anybody só aparece em **três combinações**. Nada entre elas, nada além delas.

| Nome | Largura (`wdth`) | Peso (`wght`) | Uso |
|---|---|---|---|
| **Placar** | 58 | 900 | Os números do placar, em qualquer tamanho a partir de 18 px |
| **Título** | 72 | 800 | Títulos de tela e de área, nomes de times em destaque, rótulos de liga, o número do dia na agenda |
| **Logotipo** | 140 | 800 | **Só o logotipo "Ágon".** Nenhum outro texto usa largura acima de 100 |

### Escala
A escala nasce no celular. O computador só aumenta os tamanhos grandes; o texto quase não muda.

| Nível | Fonte | Combinação | Celular | Computador | Entrelinha |
|---|---|---|---|---|---|
| Placar principal (jogo, ao vivo) | Anybody | Placar | 72 px | 120 px | 0,85 |
| Placar de destaque (faixa do ao vivo na agenda, próximo jogo) | Anybody | Placar | 56 px | 64 px | 0,9 |
| Título de tela | Anybody | Título | 40 px | 56 px | 1,0 |
| Título de área | Anybody | Título | 28 px | 34 px | 1,05 |
| Nome de time em destaque | Anybody | Título | 22 px | 26 px | 1,1 |
| Rótulo de liga ou de área (caixa alta, +0,02 em) | Anybody | Título | 18 px | 20 px | 1,1 |
| Placar em lista | Anybody | Placar | 19 px | 20 px | 1,3 |
| Corpo | IBM Plex Sans 400 | — | 16 px | 17 px | 1,5 |
| Nomes de times em lista | IBM Plex Sans 400 e 600 | — | 15 px | 16 px | 1,3 |
| Pequeno (horário, estado, legenda) | IBM Plex Sans 500 | — | 12 px | 13 px | 1,4 |

No **Pequeno em caixa alta** (por exemplo, "AO VIVO" ou "FIM"), use espaçamento de +0,06 em.

### Regras
- **Anybody nunca abaixo de 18 px**, nunca em texto corrido e nunca em frase longa. Abaixo de 18 px a largura estreita perde legibilidade; ali entra o Plex.
- **Largo só no logotipo:** usar a largura 140 em títulos transformaria a fonte em enfeite e tiraria a força do logotipo.
- **Placar sempre na combinação Placar e com números tabulares** (`font-variant-numeric: tabular-nums`). A Anybody tem a feature `tnum`; o Plex já tem dígitos de largura igual por padrão, mas a propriedade é declarada nos dois para garantir.
- **Vencedor pelo peso e pela cor, não pelo tamanho:** no placar, os dois números têm o mesmo tamanho. O vencedor se destaca pela cor (seção 4) e o perdedor fica em `textMuted`.
- **Caixa alta só em rótulos curtos** (liga, estado do jogo). Nomes de times ficam como são escritos.
- **Sem itálico "esportivo":** a inclinação pesada é clichê (seção 6.5). A Anybody tem itálico; ele não é usado.
- **Licença:** as duas fontes são OFL e vêm do Google Fonts. Os arquivos não entram no repositório.

### Carregamento
Carregar só a faixa de eixos usada, para o arquivo da Anybody ficar menor:

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Anybody:wdth,wght@58..140,800..900&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
```

```css
--font-display: "Anybody", "Arial Narrow", sans-serif;
--font-text: "IBM Plex Sans", system-ui, sans-serif;
--width-placar: 58%;    /* font-stretch */
--width-titulo: 72%;
--width-logotipo: 140%;
```

A largura se aplica com `font-stretch` (por exemplo, `font-stretch: var(--width-titulo)`), e não com `font-variation-settings`, para que o navegador escolha a instância certa.

### Critérios usados na escolha
1. **Energia de estádio:** sem serifa, de preferência com largura condensada disponível. Cabe mais placar e nome de time numa tela de celular, e lembra placar de estádio e número de camisa.
2. **Números tabulares:** dígitos de largura igual, pela feature `tnum` ou por padrão, para os placares alinharem em lista.
3. **Português completo:** Á, Ã, Õ, Ç e os demais acentos, inclusive no "Á" do logotipo.
4. **Licença livre (OFL) e disponível no Google Fonts.**
5. **Vários pesos ou eixo variável:** o mesmo desenho precisa servir ao placar enorme e ao rótulo pequeno.

### Candidatas conferidas (14/11/2026)

| Fonte | Números tabulares | Acentos | Eixos | Situação |
|---|---|---|---|---|
| Barlow Condensed (+ Barlow no texto) | sim (`tnum`) | sim | pesos fixos | candidata |
| Archivo | sim (`tnum`) | sim | peso 100–900, largura 62–125 | candidata |
| Sofia Sans Extra Condensed (+ Sofia Sans) | sim (`tnum`) | sim | peso 1–1000 | candidata |
| Anybody (+ IBM Plex Sans no texto) | sim (`tnum`) | sim | peso 100–900, largura 50–150 | **escolhida** |
| Big Shoulders Display | **não** (dígitos de larguras diferentes) | sim | peso | descartada |
| Antonio | **não** | sim | peso | descartada |

O IBM Plex Sans, fonte de texto, não traz a feature `tnum` na versão do Google Fonts, mas os dígitos já têm todos a mesma largura. Por isso continua válido para tabelas.

## 6. Anti-padrões: o que dá "cara de IA"

Toda tela nova deve ser conferida contra esta lista.

### 6.1 Textos genéricos
- **O problema:** frases que ocupam espaço sem informar. Exemplo rejeitado: "Acompanhe todos os seus esportes favoritos em um só lugar, com dados atualizados e uma experiência incrível."
- **A regra:** o Ágon é uma ferramenta de leitura de jogos, não uma coluna de jornal. Use rótulos, dados e instruções curtas. Nada de subtítulos explicativos, frases de efeito ou textos que repetem o que a tela já mostra. Se um texto pode ser removido sem perda de informação, ele sai. O slogan "Todas as disputas num só lugar" aparece no máximo uma vez, e não em toda tela.

### 6.2 Telas montadas em caixas
- **O que é uma área de conteúdo:** é a parte da página que atende uma feature: a agenda, o placar, os lances, as estatísticas, as escalações, a forma do time. **Uma área de conteúdo não é um card.** É um assunto da tela, não uma moldura.
- **O problema:** na primeira rodada de mockups, cada feature foi posta na própria caixa (título grande, card branco arredondado sobre o fundo bege, conteúdo dentro), e a página virou uma pilha dessas caixas. O resultado parece um painel montado com peças prontas, que serviria para qualquer outro site.
- **A regra:**
  1. **Sem caixa por padrão.** As áreas se separam por escala, alinhamento na grade, espaço, fios, faixas de cor de largura inteira e contraste de peso. Uma moldura é exceção e precisa de motivo: um elemento que de fato flutua, se move ou se destaca do resto.
  2. **A página é uma composição, não uma pilha.** Cada tela tem uma protagonista (no jogo, o placar com os lances; na agenda, o dia; no time, a forma recente e o próximo jogo). As outras áreas se encaixam em volta dela, com pesos diferentes. Áreas vizinhas podem se tocar e se misturar: o placar pode carregar os gols; a linha do tempo pode nascer do placar.
  3. **Cada feature ganha a forma do próprio dado.** Escalação pode ser desenhada como formação em campo, não como lista. A agenda é a linha do dia, organizada pelo que importa, não uma tabela genérica. Se duas features diferentes acabam no mesmo desenho (por exemplo, linhas de tabela com borda), a regra falhou.
  4. **Ritmo variado.** Nada de repetir o mesmo par "título grande + conteúdo" em cada seção. Uma área pode não ter título, se o dado se explica sozinho; outra pode ter só um rótulo pequeno.
- **O teste da troca:** se dá para recortar uma área e colar em outro site de esportes sem que ela pareça fora de lugar, ela está genérica demais.
- **A estética padrão de IA:** fundo creme, título com serifa de alto contraste e laranja só em pontos pequenos é hoje um dos visuais mais comuns em telas geradas por IA. Foi o que a primeira rodada produziu. A revisão evita isso pela fonte sem serifa e pelo laranja em campos grandes.

### 6.3 Ausência de estilização e de UX
- **O problema:** nenhuma animação de transição; mudanças de estado instantâneas e sem resposta visual.
- **A regra:** toda interação dá retorno, por exemplo:
  - transição na troca de dia da agenda;
  - abertura do detalhe do jogo;
  - hover e foco;
  - destaque do time selecionado nos jogos;
  - no ao vivo, a chegada de um gol ou de um lance.

  O movimento deve ter significado, mostrando de onde algo vem e para onde vai. As durações mudam conforme o contexto, e tudo respeita `prefers-reduced-motion`.

### 6.4 Falta de gráficos
- **O problema:** estatísticas de jogo e de jogador apresentadas só em números soltos e listas.
- **A regra:** use visualizações para ajudar a interpretar os dados. Por exemplo:
  - **barras divergentes** (mandante × visitante) para as estatísticas do jogo: posse, finalizações, faltas;
  - **linha do tempo** dos lances (gols, cartões, substituições) por minuto;
  - **radar (kiviat)** para comparar o perfil de dois jogadores ou times;
  - **sequência de forma** (V/E/D dos últimos jogos) na página do time.

  Esses exemplos não limitam: outros gráficos entram sempre que comunicarem melhor o dado. As cores seguem a seção 4: Egeu e Sinal nas telas comuns, cores dos clubes nas telas de clube. Mandante e visitante se diferenciam também pela luminosidade, não só pela cor.

### 6.5 Clichês de esporte
- **O problema:** bolas, chamas, raios, linhas de velocidade, escudos genéricos, troféus, louros e itálico pesado "esportivo".
- **A regra:** a energia vem dos dados, da cor e da tipografia, não de ícones de clichê. Ícones de esporte só quando identificam a modalidade (filtro de futebol, NBA, F1) e sempre no mesmo traço e na mesma grade.

---

## 7. O que existe na pasta `marca/`

Tudo o que foi produzido para chegar a esta identidade, na ordem em que foi feito. O conjunto C foi regenerado em 14/11/2026 com a Anybody. O `accent` claro (`#bb410e`) é fixado à mão no `sets/C/palette.json` depois do `build`, porque a ferramenta calcula outro tom.

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

O conjunto C é regenerado sozinho com `--sets C`. Antes do comando `kit`, fixe o `accent` claro:

```bash
python marca/agon/make_sets.py
python .claude/skills/brand-identity/scripts/brand.py build marca/agon --sets C
# trocar modes.light.accent para "#bb410e" em marca/agon/sets/C/palette.json
PYTHONUTF8=1 python .claude/skills/brand-identity/scripts/brand.py kit marca/agon/sets/C --full
```

No Windows, o `PYTHONUTF8=1` evita um erro de codificação no comando `kit`. Fontes reservas no `make_sets.py` vão sem aspas (`Arial Narrow, sans-serif`): com aspas duplas, quebram os atributos `style` das páginas do guia.
