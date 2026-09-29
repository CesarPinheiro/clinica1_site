"""Verificações do site construído (public/). Rodar: python3 -m unittest discover -s tests -t .

Cada teste trava uma decisão do plano (docs/plano-migracao-cloudflare.md): o que não
tem teste volta a quebrar calado na próxima edição.
"""
import html.parser
import pathlib
import re
import subprocess
import unittest
from urllib.parse import unquote, urlsplit

ROOT = pathlib.Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
HUGO = str(pathlib.Path.home() / ".local" / "bin" / "hugo")

ROTAS = [
    "/", "/anamnese-inteligente/", "/atendente-virtual-por-ia/",
    "/prescricao-medica-inteligente/", "/tudo-em-um-so-lugar/", "/clinica-sem-papel/",
    "/agendamento-on-line/", "/faturamento-eficiente/", "/facilidade-de-uso/",
    "/imagens-e-documentos/", "/estoque-hospitalar/", "/contato/", "/privacidade/",
]
# Os caminhos que o Google indexou e que clientes guardaram: nenhum pode dar 404.
ANTIGOS = [
    "/pagina-inicial_1", "/pagina-inicial_1/anamnese-inteligente",
    "/pagina-inicial_1/nosso-bot-de-ia-no-whatsapp",
    "/pagina-inicial_1/prescricao-medica-inteligente",
    "/pagina-inicial_1/tudo-em-um-só-lugar", "/pagina-inicial_1/clínica-sem-papel",
    "/pagina-inicial_1/agendamento-on-line", "/pagina-inicial_1/faturamento-eficiente",
    "/pagina-inicial_1/facilidade-de-uso", "/pagina-inicial_1/imagens-e-documentos",
    "/pagina-inicial_1/estoque-hospitalar", "/sobre-nosso-módulo-de-ia",
]
WA_COMERCIAL = "5531997871392"
WA_DEMO = "553190895376"

_build = None


def build():
    """Constrói uma vez por execução. --cleanDestinationDir: sem ele, arquivo órfão de
    uma página removida sobrevive em public/ e vai ao ar."""
    global _build
    if _build is None:
        _build = subprocess.run(
            [HUGO, "--gc", "--minify", "--cleanDestinationDir"],
            cwd=ROOT, capture_output=True, text=True,
        )
    return _build


def paginas():
    build()
    return sorted(PUBLIC.rglob("*.html"))


def redirects():
    regras = {}
    for linha in (PUBLIC / "_redirects").read_text().splitlines():
        if linha.strip() and not linha.startswith("#"):
            origem, destino, codigo = linha.split()
            regras[origem] = (destino, codigo)
    return regras


def existe(caminho):
    alvo = PUBLIC / unquote(caminho).lstrip("/")
    return (alvo / "index.html").is_file() if caminho.endswith("/") else alvo.is_file()


class _Links(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        for k, v in attrs:
            if k in ("href", "src") and v:
                self.links.append(v)


class TestSite(unittest.TestCase):
    def test_build_sem_erro_nem_aviso(self):
        r = build()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("WARN", r.stdout + r.stderr)

    def test_todas_as_rotas_existem(self):
        build()
        for rota in ROTAS:
            self.assertTrue(existe(rota), rota)

    def test_caminhos_antigos_redirecionam_301_para_pagina_que_existe(self):
        build()
        regras = redirects()
        for antigo in ANTIGOS:
            from urllib.parse import quote
            for forma in {antigo, quote(antigo, safe="/")}:
                for f in (forma, forma + "/"):
                    self.assertIn(f, regras, f"sem redirecionamento: {f}")
                    destino, codigo = regras[f]
                    self.assertEqual(codigo, "301", f)
                    self.assertTrue(existe(destino), f"{f} -> {destino} não existe")

    def test_nenhum_link_interno_quebrado(self):
        for pg in paginas():
            p = _Links()
            p.feed(pg.read_text())
            for link in p.links:
                u = urlsplit(link)
                if u.scheme in ("mailto", "tel") or (u.netloc and u.netloc != "www.clinica1.com.br"):
                    continue
                caminho = u.path
                if not caminho or caminho.startswith("#"):
                    continue
                self.assertTrue(existe(caminho), f"{pg.relative_to(PUBLIC)}: {link}")

    def test_nada_aponta_para_o_google_sites(self):
        for pg in paginas():
            t = pg.read_text()
            for proibido in ("googleusercontent", "sites.google", "pagina-inicial_1"):
                self.assertNotIn(proibido, t, f"{pg.relative_to(PUBLIC)}: {proibido}")

    def test_bot_virou_atendente_virtual(self):
        # Pedido do Cesar (29/09/2026): "bot" não aparece no texto do site.
        for pg in paginas():
            texto = re.sub(r"<[^>]+>", " ", pg.read_text())
            self.assertIsNone(re.search(r"\bbot\b", texto, re.I), pg.relative_to(PUBLIC))

    def test_privacidade_sem_placeholder(self):
        build()
        t = (PUBLIC / "privacidade" / "index.html").read_text()
        self.assertNotRegex(t, r"\[\.\.\.\]|\[…\]|XX\.XXX|a preencher|modelo de pol")
        self.assertIn("Cesar Bremer Pinheiro", t)
        self.assertIn("contato@clinica1.com.br", t)
        self.assertIn("13.787", t)

    def test_um_unico_script_e_sem_pedidos(self):
        for pg in paginas():
            t = pg.read_text()
            scripts = re.findall(r"<script\b[^>]*>(.*?)</script>", t, re.S)
            self.assertEqual(len(scripts), 1, pg.relative_to(PUBLIC))
            self.assertNotRegex(t, r"<script[^>]+src")
            js = scripts[0]
            self.assertLess(len(js), 900)
            for proibido in ("fetch", "XMLHttpRequest", "cookie", "sendBeacon", "import("):
                self.assertNotIn(proibido, js)

    def test_cor_so_por_token(self):
        css = (ROOT / "assets" / "css" / "main.css").read_text()
        css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
        # Tira os três blocos de tokens; o resto não pode ter cor literal.
        fora = re.sub(r":root(?::not\(\[data-theme=\"light\"\]\)|\[data-theme=\"dark\"\])?\s*\{[^}]*\}", "", css)
        achados = re.findall(r"#[0-9a-fA-F]{3,8}\b|rgba?\(", fora)
        self.assertEqual(achados, [])

    def test_numeros_de_whatsapp(self):
        for pg in paginas():
            for n in re.findall(r"wa\.me/(\d+)", pg.read_text()):
                self.assertIn(n, (WA_COMERCIAL, WA_DEMO), pg.relative_to(PUBLIC))
        home = (PUBLIC / "index.html").read_text()
        self.assertIn(f"wa.me/{WA_COMERCIAL}", home)
        demo = (PUBLIC / "atendente-virtual-por-ia" / "index.html").read_text()
        self.assertIn(f"wa.me/{WA_DEMO}", demo)

    def test_sem_emoji(self):
        emoji = re.compile("[\U0001F300-\U0001FAFF☀-➿⭐⭕️]")
        for pg in paginas():
            self.assertIsNone(emoji.search(pg.read_text()), pg.relative_to(PUBLIC))

    def test_lingua_e_canonico_www(self):
        for pg in paginas():
            t = pg.read_text()
            self.assertRegex(t, r'<html lang="?pt-BR"?')
            if pg.name == "index.html":
                self.assertRegex(t, r'rel="?canonical"? href="?https://www\.clinica1\.com\.br/')

    def test_nada_em_ingles_do_tema_padrao(self):
        # O Hugo dá à 404 o título "404 Page not found" se o layout não disser outro.
        for pg in paginas():
            self.assertNotRegex(pg.read_text(), r"Page not found|Read more", pg.relative_to(PUBLIC))


if __name__ == "__main__":
    unittest.main()
