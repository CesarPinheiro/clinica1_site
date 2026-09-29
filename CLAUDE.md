# clinica1_site — Documentação de Manutenção

Site de divulgação do sistema Clinica1: **Hugo + Cloudflare Pages**, a mesma stack do
myhelpgroup.com. Código no GitHub: **https://github.com/CesarPinheiro/clinica1_site**.

**Situação (29/09/2026):** migração em andamento — ver
[docs/plano-migracao-cloudflare.md](docs/plano-migracao-cloudflare.md). Até a virada do DNS
(fase F3), `www.clinica1.com.br` ainda é o **Google Sites**; o site Hugo está só em
`https://clinica1-site.pages.dev`.

## Publicar

```bash
scripts/publish.sh     # constrói → testa → envia ao Pages → confere 200 ao vivo
```

O push para o GitHub **não publica**: o projeto Pages (`clinica1-site`) é de upload direto.
Autenticação: `npx wrangler login` uma vez (OAuth em `~/.config/.wrangler`).

## Construir e testar localmente

```bash
~/.local/bin/hugo --gc --minify --cleanDestinationDir   # Hugo 0.166.0, não-extended
python3 -m unittest discover -s tests -t .              # sobre o public/
```

## Onde fica cada coisa

| Caminho | O quê |
|---|---|
| `hugo.toml` | título, números de WhatsApp, e-mail, **menu de recursos** (ordem = ordem do site) |
| `content/*.md` | uma página por arquivo; `url:` fixa o caminho limpo |
| `content/_index.md` | início (`hero_title`/`hero_line` + seções) |
| `layouts/` | `baseof` (cabeçalho, rodapé, script do tema), `single`, `index`, `404` |
| `layouts/shortcodes/` | `cards`/`card` (grade de cartões), `sim`/`nao` (tabela comparativa), `demo` (botão do número de demonstração), `contato` |
| `layouts/partials/icon.html` | ícones SVG (`{{ partial "icon.html" "clock" }}`); nome desconhecido quebra o build |
| `assets/css/main.css` | todo o estilo; **cor só por token** nos três blocos `:root` (dia, noite do sistema, noite escolhida) |
| `static/_redirects` | 301 dos caminhos do Google Sites (`/pagina-inicial_1/...`) para os limpos |
| `static/_headers` | cabeçalhos de segurança e cache |
| `tests/test_site.py` | o que não pode regredir (ver abaixo) |

## Regras que os testes travam

- Build sem `WARN`; todas as rotas existem; todo caminho antigo tem 301 para página que existe.
- Nenhum link interno quebrado; nada de `googleusercontent`/`sites.google`/`pagina-inicial_1`.
- **"Bot" não aparece no texto**: o nome é **Atendente virtual por IA** (pedido do Cesar, 29/09/2026).
- Privacidade sem placeholder, com o controlador, o contato e a Lei 13.787.
- Um único `<script>` (o do tema dia/noite, com `localStorage`), sem pedidos nem cookies.
- Nenhum hex/rgb fora dos blocos `:root` do CSS; nenhum emoji (ícone é SVG).
- WhatsApp só com os dois números certos; nada em inglês herdado do Hugo ("Page not found").

## Dois números de WhatsApp, dois papéis

| Parâmetro | Número | Papel |
|---|---|---|
| `whatsapp_comercial` | +55 (31) 99787-1392 | gente: "Fale conosco", contato |
| `whatsapp_demo` | 553190895376 | o **atendente virtual por IA** em operação — botão "Teste fazendo um agendamento por IA" |

## Política de privacidade

`content/privacidade.md`, caminho `/privacidade/` (**não mudar**: pode estar cadastrado na
Meta). Controlador: Cesar Bremer Pinheiro. A lista de terceiros (Meta, DeepSeek, voz do
navegador, Amazon SES, OpenTimestamps, ViaCEP) foi lida do código do c1api/c1pwa em
29/09/2026 — **serviço externo novo no sistema pede linha nova na tabela e data de revisão nova**.

## HTML de embed antigos (raiz do repo)

`modulo_ia.html`, `sobre_modulo_ia.html`, `hero.html`, `funcionalidades.html`,
`como_funciona_ia.html` eram colados no Google Sites e espelhados no GitHub Pages
(`cesarpinheiro.github.io/clinica1_site/`). **Não entram no build do Hugo.** Ficam até o
Google Sites ser despublicado (F4 do plano); depois, podem ser removidos. O conteúdo de
`sobre_modulo_ia.html` já vive em `content/atendente-virtual-por-ia.md`.
