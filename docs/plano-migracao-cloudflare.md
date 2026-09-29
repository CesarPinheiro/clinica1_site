# Plano — migrar clinica1.com.br do Google Sites para Cloudflare Pages

Data: 29/09/2026 · Base: a stack do `myhelpgroup-site` (Hugo 0.166 estático → Cloudflare
Pages por *upload direto* com `wrangler`, testes Python sobre o `public/`, `scripts/publish.sh`
que recusa publicar vermelho e só diz "publicado" depois de conferir ao vivo).

## 1. O que existe hoje (medido em 29/09/2026)

### Site

- Google Sites, `www.clinica1.com.br` (CNAME `ghs.googlehosted.com`). 13 páginas, todas 200:

| Caminho atual | Conteúdo |
|---|---|
| `/` (= `/pagina-inicial_1`) | Início — anamnese com IA como chamada principal |
| `/pagina-inicial_1/anamnese-inteligente` | Anamnese Inteligente |
| `/pagina-inicial_1/nosso-bot-de-ia-no-whatsapp` | Bot de IA — **só um iframe** com `sobre_modulo_ia.html` |
| `/pagina-inicial_1/prescricao-medica-inteligente` | Prescrição (base ANVISA, PMC) |
| `/pagina-inicial_1/tudo-em-um-só-lugar` | Sistema web |
| `/pagina-inicial_1/clínica-sem-papel` | Prontuário + assinatura digital |
| `/pagina-inicial_1/agendamento-on-line` | Agendamento e confirmações |
| `/pagina-inicial_1/faturamento-eficiente` | Faturamento |
| `/pagina-inicial_1/facilidade-de-uso` | Facilidade de uso |
| `/pagina-inicial_1/imagens-e-documentos` | Imagens e documentos |
| `/pagina-inicial_1/estoque-hospitalar` | Estoque |
| `/privacidade` | Política de privacidade |
| `/contato` | E-mail `contato@clinica1.com.br` + WhatsApp (31) 99446-7173 |

- 4–5 imagens por página, servidas por `googleusercontent.com` — **morrem junto com o Google
  Sites**; têm de ser baixadas e hospedadas no novo site.
- Os blocos HTML deste repositório (`hero.html`, `modulo_ia.html`, `sobre_modulo_ia.html`,
  `funcionalidades.html`, `como_funciona_ia.html`) são os "Incorporar código" colados no Sites.

### Defeitos que a migração resolve (e que já estão no ar)

1. **`https://clinica1.com.br` (sem www) não abre**: o TLS falha (`unexpected eof`). Só o
   `http://` redireciona. Quem digita o domínio num navegador que força HTTPS não chega.
2. **O apex tem um A a mais**: além dos 4 IPs do Google (`216.239.3x.21`), responde
   `139.177.205.92` (Linode) — parece resto antigo. **Decisão: remover** (confirmar antes que
   ninguém usa).
3. **`/privacidade` publica o MODELO, não a política**: "[Nome da Clínica], CNPJ [número],
   com sede em [endereço completo]…", com a frase "Segue um modelo simples…" visível.
   Se esta URL estiver cadastrada na Meta (app do WhatsApp) é o pior lugar para isso.
4. **O botão "Sobre o módulo" aponta para uma página que não existe**:
   `/sobre-nosso-módulo-de-ia` dá 404 (o conteúdo vive no iframe da página do bot).
5. **Sem SPF nem DMARC** no domínio (só DKIM do Google). Fora do escopo da migração —
   não mexer em e-mail no mesmo dia —, mas fica registrado como próximo passo.

### DNS — o ponto de maior risco

`clinica1.com.br` está no **Registro.br**, com o DNS hospedado lá (`e.sec.dns.br`/`f.sec.dns.br`)
e **DNSSEC ativo** (`dsstatus DSOK`). Titular: Bremer Serviços Empresariais, expira 19/04/2028.

O domínio **não é só o site**: é a produção inteira.

| Nome | Destino | Papel |
|---|---|---|
| `ia` | 187.127.29.87 | nó principal (c1pwa, c1api, bot, **webhooks da Meta**, ssh do deploy) |
| `ia2` | 147.93.35.144 | nó reserva |
| `s1` | 92.112.179.53 | (+ TXT google-site-verification) |
| `s2` | 92.112.179.68 | WildFly c1serenity |
| `s3`, `mediaserver` | 207.244.227.165 | mídia |
| `s4` | 66.94.98.253 | WildFly |
| `s5` | 179.184.216.249 | WildFly |
| `@` MX | Google Workspace (9 registros) | **e-mail** |
| `@` TXT | `google-site-verification=…`, `amazonses:…` | Search Console, **Amazon SES** |
| `google._domainkey` | TXT DKIM | assinatura do e-mail |

Levantado por `dig` + Certificate Transparency — **não é a lista completa**. O Registro.br
não permite transferência de zona; a lista autoritativa só existe no painel dele. Registros com
nome aleatório (ex.: CNAMEs de DKIM do SES `xxxx._domainkey`) só aparecem lá.

### Cloudflare

Conta `71f9e18d9e389e961a36b0b43acab06c`: zonas `myhelpgroup.com` e `socorra.me` (Free, NS
`merlin`/`nova.ns.cloudflare.com`). **`clinica1.com.br` ainda não existe.** O OAuth do
`wrangler` já feito nesta máquina publica Pages, mas **só LÊ zonas** — criar a zona e os
registros é pelo painel (a aba do Brave) ou por um API token com `Zone:DNS:Edit`.

## 2. Decisões

| # | Decisão | Recomendação | Por quê |
|---|---|---|---|
| D1 | Mover o DNS inteiro para a Cloudflare, ou só apontar o `www`? | **Mover a zona inteira** | O Pages só serve o domínio **raiz** (`clinica1.com.br`) se a zona estiver na Cloudflare — é o defeito 1. É também o que foi feito no myhelpgroup. Bônus futuro: health check para o `ia`/`ia2`, que hoje não existe. |
| D2 | Proxy (nuvem laranja) nos nós de produção? | **NÃO — todos "DNS only"** (cinza) | Proxy quebraria o `ssh root@ia.clinica1.com.br` do deploy, põe teto de 100 s em requisição, e muda o que a Meta vê no webhook. Laranja só no `@` e `www` (Pages). |
| D3 | Endereço canônico | **`www.clinica1.com.br`**, com o raiz redirecionando | É o que o Google já indexou; preserva busca. |
| D4 | Caminhos | **Limpos** (`/anamnese-inteligente/`) + **301** dos antigos via `_redirects` | `pagina-inicial_1` é artefato do Sites. **`/privacidade` e `/contato` ficam idênticos** (podem estar cadastrados na Meta/Play/documentos). |
| D5 | Repositório | **Este (`clinica1_site`)**, virando projeto Hugo | Mantém o histórico; os HTML de embed viram conteúdo/partials. |
| D6 | Conteúdo | **Fase 1: porte fiel** (texto igual, visual novo), exceto a privacidade, que precisa de texto real. Reescrita depois. | Separar "mudou a tecnologia" de "mudou o que o site diz" — cada uma se confere sozinha. |
| D7 | Idiomas | **Só pt-BR** | O myhelpgroup tem 15 idiomas por causa da Play Store; aqui a máquina de i18n é custo sem ganho. |

**Respondido pelo Cesar (29/09/2026):** D1–D7 aprovadas. A privacidade segue o modelo do
myhelpgroup: controlador **Cesar Bremer Pinheiro**, demais dados mediante solicitação do
titular ou à ANPD, contato `contato@clinica1.com.br`. O `A` da Linode no apex **sai**.
E, no meio da F1: **"bot" vira "Atendente virtual por IA"** em todo o texto — a página é
`/atendente-virtual-por-ia/` (os dois caminhos antigos do bot/módulo vão para ela em 301), e
um teste reprova a palavra "bot" no HTML.

## 3. Fases

### F0 — Inventário e congelamento (antes de tocar em nada)

1. **Exportar a zona do Registro.br**: no painel, copiar *todos* os registros (nome, tipo,
   valor, TTL) para `docs/zona-registro-br-AAAA-MM-DD.txt` neste repo. Esta lista é o
   gabarito da F2 **e o plano de volta**.
2. Salvar o HTML das 13 páginas e baixar as imagens do `googleusercontent` para `static/img/`
   (feito parcialmente em 29/09 para o levantamento acima).
3. Descobrir onde `https://clinica1.com.br/privacidade` está cadastrado (app da Meta, WhatsApp
   Business, Play Console) — isso define quais caminhos o teste trava.

### F1 — Construir o site (sem risco: nada muda no ar)

1. Hugo 0.166.0 (mesmo binário `~/.local/bin/hugo`), estrutura do myhelpgroup:
   `hugo.toml`, `layouts/`, `content/`, `static/`, `assets/`, `tests/`, `scripts/`.
2. Portar as 13 páginas; a do atendente virtual (`/atendente-virtual-por-ia/`) passa a ter o
   conteúdo de `sobre_modulo_ia.html` **na página** (fim do iframe e do 404).
3. `static/_redirects` com os 301 dos caminhos antigos (inclusive as variantes com acento
   `%C3%AD`/`%C3%B3`) e `static/_headers` (cache, `X-Content-Type-Options`, etc.).
4. Testes (`python3 -m unittest`, sobre o `public/`), no espírito dos 70 do myhelpgroup:
   - toda rota da tabela da seção 1 responde (direto ou por 301 no `_redirects`);
   - zero link interno quebrado; zero recurso de `googleusercontent`/`google.com`;
   - **a privacidade não contém `[` + `]` de placeholder** nem a palavra "modelo";
   - `hugo` sem nenhum `WARN`; JavaScript dentro do limite (tema dia/noite, como lá);
   - links do WhatsApp com o número certo.
5. Projeto Pages **`clinica1-site`** (direct upload) + `scripts/publish.sh` copiado do
   myhelpgroup (constrói → testa → envia → confere 200 ao vivo). Conferir em
   `clinica1-site.pages.dev`.
6. **Portão da F1**: Cesar aprova o site no `.pages.dev`.
   **Aprovado em 29/09/2026** (`https://clinica1-site.pages.dev`, commits `2e15661`..`b8b5b1a`).

### F2 — Zona na Cloudflare, em paralelo (ainda sem efeito: o Registro.br segue mandando)

1. No painel (Brave): *Add a domain* → `clinica1.com.br` → plano Free. Anotar o par de NS
   atribuído.
2. Apagar o que a varredura automática da Cloudflare inventar e **recriar exatamente a lista
   da F0**, todos em **DNS only**, TTL igual. Exceções deliberadas: `@` e `www` (ver F3), e o
   A do Linode (sai).
3. **Conferência máquina, não olho**: um script compara, nome a nome e tipo a tipo,
   `dig @e.sec.dns.br` com `dig @<ns-da-cloudflare>`. Só segue com **zero diferença**
   (fora `@`/`www`). Este script vai para `scripts/check_zona.sh` e roda de novo na F3.
4. Em *SSL/TLS*: modo **Full (strict)**; não ativar nada que reescreva conteúdo
   (Rocket Loader, Email Obfuscation) — o c1pwa não passa pela Cloudflare, mas por garantia.

### F3 — Virada (janela fora do horário das clínicas, ex.: sábado à noite)

1. Registro.br → *Alterar servidores DNS* → os dois da Cloudflare, **removendo o DS do
   DNSSEC no mesmo ato** (DS antigo + NS novo = domínio inteiro fora do ar para quem valida
   DNSSEC, que inclui o Google e muitos provedores brasileiros).
2. Aguardar a delegação (`dig NS clinica1.com.br @a.dns.br` mostrando a Cloudflare) e a zona
   ativa no painel.
3. No Pages, *Custom domains*: `www.clinica1.com.br` e `clinica1.com.br`; regra de
   redirecionamento raiz → `https://www…` (301, preservando caminho).
4. **Conferência de produção, de fora** (isto é o que diz que a virada acabou):
   - `curl https://ia.clinica1.com.br/sw.js` e idem `ia2` → mesma versão de antes;
   - `ssh root@ia.clinica1.com.br true` e `ia2`;
   - webhook: `POST` ao `/v1/whatsapp/webhook` = 200 e `GET` sem token = 403 (como medido
     em 27/08);
   - `s2`/`s4`/`s5`/`mediaserver` respondem na 443;
   - e-mail: mandar de fora para `contato@clinica1.com.br` e responder;
   - site: `https://clinica1.com.br` → `https://www…`, as 13 rotas, os 301 antigos.
5. `scripts/check_zona.sh` de novo, agora contra o resolvedor público (`1.1.1.1`, `8.8.8.8`).

### F4 — Depois (dias seguintes)

1. Ativar DNSSEC na Cloudflare e cadastrar o novo DS no Registro.br (48 h depois, com a
   delegação estável).
2. Search Console: confirmar propriedade (o TXT veio junto) e enviar o `sitemap.xml`.
3. Google Sites: remover o domínio personalizado, **manter o site despublicado 30 dias**
   (fonte do conteúdo se faltar algo).
4. Atualizar o `CLAUDE.md` deste repo (o fluxo "colar no Sites" morre) e a memória
   `webhook-troca-no-ia-ia2` (o DNS deixou de estar no Registro.br).
5. À parte, sem pressa: SPF e DMARC do e-mail.

## 4. Volta (se a F3 der errado)

Registro.br → servidores DNS de volta para `e.sec.dns.br`/`f.sec.dns.br`. **Não é garantido
que o Registro.br guarde a zona hospedada depois de trocar os NS** — por isso a exportação da
F0 é obrigatória: com ela, a zona se recria à mão em minutos. O Google Sites segue publicado
até a F4, então o site antigo volta junto.

A propagação da volta leva o mesmo tempo da ida (TTL da delegação do `.br`, até ~1 h);
por isso a janela é fora do expediente.

## 5. Riscos, em ordem

1. **Registro esquecido na F2** → um serviço de produção sai do ar calado. Mitigação: F0 pelo
   painel (não pelo `dig`) + `check_zona.sh` com zero diferença como portão.
2. **DNSSEC** mal ordenado → domínio inteiro fora. Mitigação: DS removido junto com a troca
   de NS; DS novo só na F4.
3. **Nuvem laranja em nó de produção** → ssh/webhook quebrados. Mitigação: tudo cinza menos
   `@`/`www`, conferido na F3.
4. **Imagens perdidas** ao despublicar o Sites. Mitigação: teste proíbe `googleusercontent`.

## 6. Esforço

F0 ½ dia · F1 2–3 dias (13 páginas + testes + visual) · F2 ½ dia · F3 1–2 h de janela ·
F4 ½ dia espalhado.
