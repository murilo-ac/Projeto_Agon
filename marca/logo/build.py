"""Gera os SVGs dos conceitos de logo do Ágon com geometria calculada (ângulos exatos, grade de 4 unidades).

Uso: python build.py  ->  escreve os arquivos em ./concepts/
"""

import math
from pathlib import Path

OUT = Path(__file__).parent / "concepts"
INK = "#111111"


def svg(view_w, view_h, body, title):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {view_w} {view_h}" '
        f'width="{view_w}" height="{view_h}" role="img" aria-labelledby="t">'
        f'<title id="t">{title}</title>{body}</svg>\n'
    )


def poly(points):
    return "M" + " L".join(f"{fmt(x)} {fmt(y)}" for x, y in points) + " Z"


def fmt(v):
    return f"{round(v, 2):g}"


def intersect(p1, p2, p3, p4):
    """Interseção das retas p1-p2 e p3-p4."""
    (x1, y1), (x2, y2), (x3, y3), (x4, y4) = p1, p2, p3, p4
    d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    a = x1 * y2 - y1 * x2
    b = x3 * y4 - y3 * x4
    return ((a * (x3 - x4) - (x1 - x2) * b) / d, (a * (y3 - y4) - (y1 - y2) * b) / d)


def offset_line(p, q, dist):
    """Desloca a reta p-q perpendicularmente (à esquerda do sentido p->q) por `dist`."""
    dx, dy = q[0] - p[0], q[1] - p[1]
    n = math.hypot(dx, dy)
    ox, oy = -dy / n * dist, dx / n * dist
    return (p[0] + ox, p[1] + oy), (q[0] + ox, q[1] + oy)


def chevron(left, apex, right, width):
    """Λ espesso (contorno preenchido) com pernas de espessura `width`, pés cortados na horizontal."""
    lo = offset_line(left, apex, width / 2)  # lado externo da perna esquerda
    li = offset_line(left, apex, -width / 2)
    ro = offset_line(apex, right, width / 2)
    ri = offset_line(apex, right, -width / 2)
    base = left[1]
    horiz = ((0, base), (1, base))
    outer_apex = intersect(*lo, *ro)
    inner_apex = intersect(*li, *ri)
    pts = [
        intersect(*lo, *horiz),
        outer_apex,
        intersect(*ro, *horiz),
        intersect(*ri, *horiz),
        inner_apex,
        intersect(*li, *horiz),
    ]
    return pts


# ---------------------------------------------------------------- conceito A: chave do mata-mata

def concept_a():
    w = 30  # espessura (≈ 12 % do canvas: aguenta 16 px)
    big = chevron((84, 164), (128, 76), (172, 164), w)
    left = chevron((48, 236), (84, 164), (120, 236), w)
    right = chevron((136, 236), (172, 164), (208, 236), w)
    champion = [(140, 36), (164, 36), (178, 8), (154, 8)]  # acento paralelo à perna esquerda (1:2)
    body = "".join(f'<path fill="{INK}" d="{poly(p)}"/>' for p in (big, left, right, champion))
    return svg(256, 256, f'<g transform="translate(0 6)">{body}</g>', "Ágon — conceito A (chave)")


# ---------------------------------------------------------------- conceito C: Á com o ápice cortado

def concept_c(dx=14, dy=-24):
    # A pontudo, pernas com inclinação exata de 1:2, apoiado na base y=236
    base, apex = 236, (128, 28)
    lo_foot, ro_foot = (24, base), (232, base)
    t = 46  # espessura horizontal das pernas
    li_foot, ri_foot = (24 + t, base), (232 - t, base)
    inner_apex = intersect(li_foot, (li_foot[0] + 104, base - 208), ri_foot, (ri_foot[0] - 104, base - 208))
    bar_top, bar_bot = 172, 200
    # corte: reta com inclinação de 30° (sobe para a direita), passando 52 unidades abaixo do ápice
    cy = apex[1] + 52
    k = math.tan(math.radians(30))
    cut_a, cut_b = (0, cy + k * 128), (256, cy - k * 128)
    cl = intersect(lo_foot, apex, cut_a, cut_b)
    cr = intersect(apex, ro_foot, cut_a, cut_b)

    def x_on(p, q, y):
        return p[0] + (q[0] - p[0]) * (y - p[1]) / (q[1] - p[1])

    body_outer = [lo_foot, cl, cr, ro_foot, ri_foot,
                  (x_on(ri_foot, inner_apex, bar_bot), bar_bot),
                  (x_on(li_foot, inner_apex, bar_bot), bar_bot), li_foot]
    counter = [(x_on(li_foot, inner_apex, bar_top), bar_top), inner_apex,
               (x_on(ri_foot, inner_apex, bar_top), bar_top)]
    piece = [(cl[0] + dx, cl[1] + dy), (apex[0] + dx, apex[1] + dy), (cr[0] + dx, cr[1] + dy)]

    def rnd(pts):
        return pts

    d = poly(rnd(body_outer)) + " " + poly(rnd(counter))
    body = (f'<path fill="{INK}" fill-rule="evenodd" d="{d}"/>'
            f'<path fill="{INK}" d="{poly(rnd(piece))}"/>')
    # o pedaço sobe acima do ápice original: recentraliza no canvas
    return svg(256, 256, f'<g transform="translate(0 8)">{body}</g>', "Ágon — conceito C (ápice cortado)")


# ---------------------------------------------------------------- conceito B: logotipo geométrico "ágon"

R, S = 52, 24  # raio externo das curvas e espessura do traço
RI = R - S
CY = 120  # centro das curvas (altura-x de 68 a 172)
TOP, BASE = CY - R, CY + R


def ring(cx, cy=CY):
    return (f"M{cx - R} {cy} A{R} {R} 0 1 0 {cx + R} {cy} A{R} {R} 0 1 0 {cx - R} {cy} Z "
            f"M{cx - RI} {cy} A{RI} {RI} 0 1 1 {cx + RI} {cy} A{RI} {RI} 0 1 1 {cx - RI} {cy} Z")


def half_ring(cx, side, cy=CY):
    """Meio anel: side=-1 (esquerdo) ou +1 (direito)."""
    sw = 0 if side < 0 else 1
    return (f"M{cx} {cy - R} A{R} {R} 0 0 {sw} {cx} {cy + R} V{cy + RI} "
            f"A{RI} {RI} 0 0 {1 - sw} {cx} {cy - RI} Z")


def rect(x0, y0, x1, y1):
    return f"M{x0} {y0} H{x1} V{y1} H{x0} Z"


def accent(x, y, h=36, w=S):
    """Acento agudo: paralelogramo a 45° (sobe para a direita), base em (x, y)."""
    return poly([(x, y), (x + w, y), (x + w + h, y - h), (x + h, y - h)])


def letter_a(x):
    cx = x + R
    return [ring(cx), rect(cx + R - S, TOP, cx + R, BASE)]


def letter_g(x):
    cx = x + R
    dcy = BASE + 4  # centro da curva do descendente
    tail = (f"M{cx + R} {dcy} A{R} {R} 0 0 1 {cx - R} {dcy} H{cx - RI} "
            f"A{RI} {RI} 0 0 0 {cx + RI} {dcy} Z")
    return [ring(cx), rect(cx + R - S, TOP, cx + R, dcy + 2), tail]


def letter_o(x, gap=12):
    """O "o" é dividido em dois lados que se enfrentam: a disputa."""
    cx = x + R
    return [half_ring(cx - gap / 2, -1), half_ring(cx + gap / 2, +1)]


def letter_n(x):
    arch = (f"M{x} {CY} A{R} {R} 0 0 1 {x + 2 * R} {CY} H{x + 2 * R - S} "
            f"A{RI} {RI} 0 0 0 {x + S} {CY} Z")
    return [arch, rect(x, TOP, x + S, BASE), rect(x + 2 * R - S, CY - 2, x + 2 * R, BASE)]


def paths(ds):
    return "".join(f'<path fill="{INK}" d="{d}"/>' for d in ds)


def wordmark(x0=8, gap=20):
    """Devolve (corpo SVG, largura) do logotipo "ágon"."""
    xs = [x0 + i * (2 * R + gap) for i in range(4)]
    ds = letter_a(xs[0]) + letter_g(xs[1]) + letter_o(xs[2]) + letter_n(xs[3])
    ds.append(accent(xs[0] + R - 20, TOP - 14))
    return paths(ds), xs[3] + 2 * R + x0


def concept_b():
    body, width = wordmark()
    return svg(width, 256, body, "Ágon — conceito B (logotipo)")


def concept_b_symbol():
    """Para tamanhos pequenos: só o 'á' centralizado no quadrado."""
    x = 128 - R
    body = paths(letter_a(x) + [accent(x + R - 20, TOP - 14)])
    return svg(256, 256, f'<g transform="translate(-38.4 0.5) scale(1.3)">{body}</g>', "Ágon — conceito B (símbolo á)")


def lockup(symbol_svg, title):
    """Símbolo (256) + logotipo à direita, mesma altura."""
    inner = symbol_svg.split("</title>", 1)[1].rsplit("</svg>", 1)[0]
    body, width = wordmark()
    scale = 0.62
    wm = f'<g transform="translate(276 {fmt(128 - 128 * scale)}) scale({scale})">{body}</g>'
    return svg(fmt(276 + width * scale + 8), 256, inner + wm, title)


def main():
    OUT.mkdir(exist_ok=True)
    files = {
        "a-chave-v3.svg": concept_a(),
        "b-logotipo-v3.svg": concept_b(),
        "b-simbolo-v3.svg": concept_b_symbol(),
        "c-apice-v3.svg": concept_c(),
    }
    files["a-chave-lockup-v3.svg"] = lockup(files["a-chave-v3.svg"], "Ágon — conceito A (assinatura)")
    files["c-apice-lockup-v3.svg"] = lockup(files["c-apice-v3.svg"], "Ágon — conceito C (assinatura)")
    for name, content in files.items():
        (OUT / name).write_text(content, encoding="utf-8")
        print("escrito", OUT / name)


if __name__ == "__main__":
    main()
