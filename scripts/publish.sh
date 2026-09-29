#!/bin/bash
# Publica o site. Constrói, verifica, envia, e confirma que chegou mesmo ao ar.
#
# O push para o GitHub NÃO publica: o projeto Cloudflare Pages é de upload
# direto. Um push sem isto deixa o repositório à frente do site sem nenhum erro
# que avise (aconteceu no myhelpgroup em 2026-09-20).
#
# Autenticação, por ordem de preferência:
#   1. `npx wrangler login` uma vez (OAuth; fica em ~/.config/.wrangler)
#   2. export CLOUDFLARE_API_TOKEN=...  (painel → My Profile → API Tokens,
#      permissão mínima Account → Cloudflare Pages → Edit)
set -euo pipefail

cd "$(dirname "$0")/.."
HUGO="${HUGO:-$HOME/.local/bin/hugo}"
PROJECT=clinica1-site
# Até a virada do DNS (F3 do plano), o site só existe no endereço do Pages.
BASE="${BASE:-https://clinica1-site.pages.dev}"

echo "→ construir"
"$HUGO" --gc --minify --cleanDestinationDir

echo "→ verificar (nada vai ao ar sem isto passar)"
python3 -m unittest discover -s tests -t .

echo "→ publicar"
npx --yes wrangler@3.114.17 pages deploy public --project-name="$PROJECT" --branch=main

echo "→ conferir ao vivo"
fail=0
for u in / /atendente-virtual-por-ia/ /contato/ /privacidade/; do
    code=$(curl -s -o /dev/null -w '%{http_code}' "$BASE$u" --max-time 20)
    printf '%-26s %s\n' "$u" "$code"
    [ "$code" = "200" ] || fail=1
done

if [ "$fail" -ne 0 ]; then
    echo "AVISO: algum endereço não respondeu 200. A Cloudflare pode levar ~1 min" \
         "para propagar; rode só esta parte de novo antes de concluir que falhou."
    exit 1
fi
echo "publicado."
