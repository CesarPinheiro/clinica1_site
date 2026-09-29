#!/usr/bin/env python3
"""Confere uma zona DNS contra o gabarito exportado do Registro.br (F0 do plano).

Uso:
    scripts/check_zona.py docs/zona-registro-br-AAAA-MM-DD.txt NS [NS ...]

    NS = servidor a consultar: e.sec.dns.br (a zona antiga, prova que o gabarito está
    certo), o par da Cloudflare (F2) ou 1.1.1.1 / 8.8.8.8 (F3, depois da virada).

Gabarito: uma linha por registro, `nome tipo valor` (separados por espaço; o valor pode
ter espaços, ex.: `@ MX 1 aspmx.l.google.com`). `@` é o domínio. Linhas vazias e `#` são
ignoradas. TTL não entra na comparação: a Cloudflare arredonda e "Auto" é 300.

Para cada par (nome, tipo) do gabarito, pergunta ao NS e exige o MESMO conjunto de
valores. Sai 1 com qualquer diferença — é o portão da F2 e da F3, então não há "quase".
Exceções deliberadas (o site vai para o Pages; o A da Linode sai) ficam em PULAR.
"""
import subprocess
import sys

DOMINIO = "clinica1.com.br"
# (nome, tipo) que MUDAM de propósito na migração — ver D1/D3 do plano.
PULAR = {("@", "A"), ("@", "AAAA"), ("www", "CNAME"), ("www", "A"), ("www", "AAAA"), ("@", "NS"), ("@", "SOA")}


def fqdn(nome: str) -> str:
    return DOMINIO if nome == "@" else f"{nome}.{DOMINIO}"


def normaliza(tipo: str, valor: str) -> str:
    v = valor.strip()
    if tipo == "TXT":
        # dig devolve TXT longo em pedaços entre aspas ("a" "b"); o gabarito, o texto inteiro.
        partes = v.split('" "')
        v = "".join(partes).strip('"')
        return v
    return v.lower().rstrip(".")


def le_gabarito(caminho: str) -> dict[tuple[str, str], set[str]]:
    g: dict[tuple[str, str], set[str]] = {}
    with open(caminho, encoding="utf-8") as f:
        for n, linha in enumerate(f, 1):
            linha = linha.strip()
            if not linha or linha.startswith("#"):
                continue
            campos = linha.split(None, 2)
            if len(campos) != 3:
                sys.exit(f"{caminho}:{n}: esperado `nome tipo valor`, veio {linha!r}")
            nome, tipo, valor = campos[0].lower(), campos[1].upper(), campos[2]
            g.setdefault((nome, tipo), set()).add(normaliza(tipo, valor))
    return g


def pergunta(ns: str, nome: str, tipo: str) -> set[str]:
    r = subprocess.run(
        ["dig", "+short", "+norecurse" if not ns[0].isdigit() else "+recurse", f"@{ns}", fqdn(nome), tipo],
        capture_output=True, text=True, timeout=20,
    )
    linhas = [l for l in r.stdout.splitlines() if l and not l.startswith(";")]
    # Um CNAME no caminho aparece antes do A quando o tipo pedido é A: filtra pelo formato.
    return {normaliza(tipo, l) for l in linhas}


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    gabarito = le_gabarito(sys.argv[1])
    falhas = 0
    for ns in sys.argv[2:]:
        print(f"== {ns}")
        for (nome, tipo), esperado in sorted(gabarito.items()):
            if (nome, tipo) in PULAR:
                continue
            visto = pergunta(ns, nome, tipo)
            if visto == esperado:
                print(f"   ok   {nome} {tipo}")
                continue
            falhas += 1
            print(f"   DIF  {nome} {tipo}")
            for v in sorted(esperado - visto):
                print(f"          falta: {v}")
            for v in sorted(visto - esperado):
                print(f"          sobra: {v}")
    print("ZERO diferença" if not falhas else f"{falhas} diferença(s) — NÃO seguir")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
