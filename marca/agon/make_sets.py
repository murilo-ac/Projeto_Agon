"""Escreve marca/agon/sets.json: três conjuntos (tipografia + paleta) em torno do mesmo símbolo, a Chave.

A geometria do símbolo vem de marca/logo/build.py (conceito A v3), convertida da grade de 256 para a de 100 que
a brand-identity usa. A forma não muda entre os conjuntos; só as cores dos papéis (primary / accent).
"""

import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).parent
spec = importlib.util.spec_from_file_location("logo_build", HERE.parent / "logo" / "build.py")
lb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lb)

K = 100 / 256  # grade 256 -> 100
DY = 6  # o mesmo translate(0 6) do conceito A v3


def to100(points):
    return " L".join(f"{x * K:.2f} {(y + DY) * K:.2f}" for x, y in points)


def symbol_svg():
    w = 30
    big = lb.chevron((84, 164), (128, 76), (172, 164), w)
    left = lb.chevron((48, 236), (84, 164), (120, 236), w)
    right = lb.chevron((136, 236), (172, 164), (208, 236), w)
    champion = [(140, 36), (164, 36), (178, 8), (154, 8)]
    chave = "".join(f'<path id="{i}" d="M{to100(p)} Z"/>' for i, p in
                    (("final", big), ("semi-esquerda", left), ("semi-direita", right)))
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
            f'<g id="chave" data-color="primary">{chave}</g>'
            f'<path id="campeao" data-color="accent" d="M{to100(champion)} Z"/></svg>')


def face(family, weights, location, features=(), case="as-is", tracking=0, fallback="system-ui, sans-serif"):
    return {"family": family, "source": "google", "license": "OFL-1.1", "weights": list(weights),
            "location": location, "features": list(features), "case": case, "tracking": tracking,
            "fallback": fallback, "file": None}


def logo(case, tracking, location=None):
    return {
        "type": "symbol+wordmark",
        "concept": "As linhas de um mata-mata convergem e formam o A; a final é o ápice e o acento é o campeão.",
        "symbol": "logo/symbol.svg",
        "wordmark": {"text": "Ágon", "role": "display", "location": location, "tracking": tracking, "case": case},
        "monogram": None,
        "lockups": ["horizontal", "stacked"],
        "colors": {"chave": "primary", "campeao": "accent", "wordmark": "text"},
        "tags": ["letterform"],
        "clear_space": {"unit": "cap-height", "multiple": 1, "inferred": True},
        "min_size": {"px": 20, "mm": 7},
        "misuse": [
            {"do": "stretch"}, {"do": "recolour"}, {"do": "crowd"}, {"do": "rearrange"},
            {"svg": "logo/misuse-1.svg", "label": "Não preencher o losango: sem o vazio, a chave some"},
            {"svg": "logo/misuse-2.svg", "label": "Não espelhar o acento: Á vira À"},
        ],
    }


# usos incorretos desenhados a partir do master do símbolo (grade 100)
_CHAVE_SEM_LOSANGO = ("M25.3 94.53L12.2 94.53L32.81 53.3L50 18.93L67.19 53.3L87.8 94.53L74.7 94.53L67.19 79.51"
                      "L59.68 94.53L40.32 94.53L32.81 79.51Z")
_CHAVE = _CHAVE_SEM_LOSANGO + " M39.36 66.4L50 87.67L60.64 66.4L50 45.13Z"
_CAMPEAO = "M54.69 16.41L60.16 5.47L69.53 5.47L64.06 16.41Z"
_CAMPEAO_ESPELHADO = "M45.31 16.41L39.84 5.47L30.47 5.47L35.94 16.41Z"


def misuse_svg(chave, campeao, evenodd=True):
    rule = ' fill-rule="evenodd"' if evenodd else ""
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
            f'<path data-color="primary"{rule} d="{chave}"/><path data-color="accent" d="{campeao}"/></svg>')


MISUSE_SVGS = {
    "misuse-1": misuse_svg(_CHAVE_SEM_LOSANGO, _CAMPEAO, evenodd=False),
    "misuse-2": misuse_svg(_CHAVE, _CAMPEAO_ESPELHADO),
}


def brand(i, name, hex_, usage):
    return {"id": f"brand-{i}", "name": name, "hex": hex_, "source": "chosen", "locked": False, "usage": usage}


SETS = [
    {
        "set": {
            "id": "A",
            "name": "Holofote",
            "recommended": True,
            "mechanism": "O estádio à noite: um único holofote âmbar sobre grafite, que ilumina o campeão no símbolo "
                         "e os números na tela; a tipografia é seca e tabular como um placar.",
            "expression_move": "O âmbar do holofote é a única cor saturada de todo o sistema.",
            "differs_by": "ESPN e ge falam alto com vermelho e verde de portal; SofaScore e FotMob usam azul e verde. "
                          "O Holofote é escuro, quieto e tem um só ponto de luz.",
        },
        "axes": {"warm_cool": 1, "quiet_loud": -1, "classic_contemporary": 1},
        "type": {
            "pairing_mode": "data-face",
            "display": face("Geist", [600], {"wght": 600}, tracking=-10),
            "text": face("Geist", [400, 600], {"wght": 400}, ["tnum"]),
            "mono": face("Geist Mono", [500], {"wght": 500}, ["tnum"], fallback="ui-monospace, monospace"),
        },
        "logo": logo("as-is", -10),
        "palette_build": {"strategy": None, "accent": None, "light_bg": "#f4f5f7", "dark_bg": "#0d1015",
                          "neutral_tint": None, "neutral_chroma": 0.012, "extra": []},
        "card": {"ground": "dark"},
        "palette": {"name": "Holofote", "direction": "Grafite de estádio à noite com um único holofote âmbar.",
                    "brand": [brand(1, "Grafite", "#1c2330", "símbolo, cabeçalhos, superfícies escuras"),
                              brand(2, "Âmbar Holofote", "#ffb000", "o campeão no símbolo; destaques e o placar ao vivo")],
                    "feels": ["noturno", "focado", "exato"]},
    },
    {
        "set": {
            "id": "B",
            "name": "Volt",
            "recommended": False,
            "mechanism": "A linha de cal sobre a quadra: maiúsculas condensadas e apertadas como numeração de camisa, "
                         "tinta quase preta e um verde-volt que só aparece no lance decisivo.",
            "expression_move": "A tipografia condensada em caixa-alta, grande e dominante.",
            "differs_by": "O único caminho barulhento: condensado e de alto contraste, sem o itálico pesado da ESPN e "
                          "com um volt amarelado longe do verde de grama do ge e do FotMob.",
        },
        "axes": {"warm_cool": 2, "quiet_loud": 2, "classic_contemporary": 2},
        "type": {
            "pairing_mode": "superfamily",
            "display": face("Sofia Sans Condensed", [800], {"wght": 800}, case="upper", tracking=20),
            "text": face("Sofia Sans", [400, 600], {"wght": 400}, ["tnum"]),
            "mono": None,
        },
        "logo": logo("upper", 20),
        "palette_build": {"strategy": None, "accent": None, "light_bg": "#f6f6f1", "dark_bg": None,
                          "neutral_tint": None, "neutral_chroma": 0.008, "extra": []},
        "card": {"ground": "light"},
        "palette": {"name": "Volt", "direction": "Tinta quase preta sobre cal, com um volt elétrico para o lance decisivo.",
                    "brand": [brand(1, "Tinta", "#15171a", "símbolo, títulos, texto"),
                              brand(2, "Volt", "#c8f031", "o campeão em fundo escuro; destaques e botões com texto escuro")],
                    "feels": ["elétrico", "direto", "atlético"]},
    },
    {
        "set": {
            "id": "C",
            "name": "Ágora",
            "recommended": False,
            "mechanism": "A origem grega do agṓn: a fineza cortante de um Bodoni (o mesmo gume do símbolo), o azul do "
                         "Egeu sobre mármore e um laranja de sinal para o resultado.",
            "expression_move": "O contraste extremo do Bodoni no nome; o resto é silencioso.",
            "differs_by": "Nenhum concorrente usa serifa de alto contraste com cor (The Athletic usa serifa, mas em "
                          "preto e branco editorial); o azul-petróleo fica longe do azul royal do SofaScore.",
        },
        "axes": {"warm_cool": 0, "quiet_loud": 0, "classic_contemporary": -2},
        "type": {
            "pairing_mode": "contrast",
            "display": face("Bodoni Moda", [600], {"wght": 600, "opsz": 96}, tracking=0, fallback="Didot, Georgia, serif"),
            "text": face("IBM Plex Sans", [400, 600], {"wght": 400}, ["tnum"]),
            "mono": None,
        },
        # opsz baixo no nome: hairlines mais grossas, que sobrevivem ao tamanho mínimo
        "logo": logo("as-is", 0, {"wght": 600, "opsz": 24}),
        "palette_build": {"strategy": None, "accent": None, "light_bg": "#f5f4f0", "dark_bg": None,
                          "neutral_tint": None, "neutral_chroma": None, "extra": []},
        "card": {"ground": "light"},
        "palette": {"name": "Ágora", "direction": "Azul do Egeu sobre mármore, com um laranja de sinal para o resultado.",
                    "brand": [brand(1, "Egeu", "#0b5e75", "símbolo, cabeçalhos, links"),
                              brand(2, "Sinal", "#f0602a", "o campeão no símbolo; resultado e chamadas")],
                    "feels": ["clássico", "lúcido", "afiado"]},
    },
]


def main():
    sym = symbol_svg()
    out = {"schema": "brand-identity/sets@1", "sets": []}
    for s in SETS:
        ident = {
            "set": s["set"], "axes": s["axes"], "type": s["type"], "logo": s["logo"],
            "palette_build": s["palette_build"], "card": s["card"], "defaults_used": [],
            "rationale": [
                {"claim": "O símbolo é a Chave aprovada pelo cliente; a forma é idêntica nos três conjuntos.",
                 "evidence": "judgement", "source": "marca/logo/BRIEF.md"},
                {"claim": "Os concorrentes ocupam vermelho (ESPN), verde (ge, FotMob) e azul royal (SofaScore).",
                 "evidence": "judgement", "source": "pesquisa da categoria"},
            ],
        }
        pal = {"schema": "brand-identity/palette@1", **s["palette"]}
        out["sets"].append({"identity": ident, "palette": pal, "symbol_svg": sym,
                            "symbol_small_svg": None, "wordmark_detail_svg": None,
                            "misuse_svgs": MISUSE_SVGS})
    (HERE / "sets.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("sets.json escrito;", len(out["sets"]), "conjuntos")


if __name__ == "__main__":
    main()
