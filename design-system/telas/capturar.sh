#!/bin/sh
# Captura uma tela de mockup em celular (claro e escuro) e computador.
# Uso, a partir de Projeto_Agon/:  sh design-system/telas/capturar.sh design-system/telas/a-painel/agenda.html
# Saída: design-system/telas/capturas/<opcao>-<tela>-{celular,celular-escuro,computador}.png
set -e
html="$1"
opcao=$(basename "$(dirname "$html")")
tela=$(basename "$html" .html)
out="design-system/telas/capturas"
r=".claude/skills/brand-identity/scripts/render_png.py"
mkdir -p "$out"
PYTHONUTF8=1 python "$r" "$html" -o "$out/$opcao-$tela-celular.png" --width 390 --height 844 --scale 2 --full-page --mobile --color-scheme light
PYTHONUTF8=1 python "$r" "$html" -o "$out/$opcao-$tela-celular-escuro.png" --width 390 --height 844 --scale 2 --full-page --mobile --color-scheme dark
PYTHONUTF8=1 python "$r" "$html" -o "$out/$opcao-$tela-computador.png" --width 1440 --height 900 --full-page --color-scheme light
echo "ok: $out/$opcao-$tela-*.png"
