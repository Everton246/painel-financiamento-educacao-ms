"""Atualiza o painel: baixa só o que é novo, remonta a base e roda as conferências.

Uso:
  python atualizar.py               coleta (01 a 05), base, catálogo de fontes e conferência
  python atualizar.py --so-base     só remonta a base e confere (sem acessar a internet)
  python atualizar.py --verificar   NÃO baixa nada: para cada fonte de dados/fontes_status.csv, verifica se ela publicou
                                    período mais novo que o da base e grava docs/verificacoes/AAAA-MM-DD.md.
                                    Rápido (cada consulta tem limite de 20 s) e não para se uma fonte estiver fora do ar.

Os objetivos a e b NÃO são recalculados aqui: a base lê 04_dados_ICMS_IQE_VAAR/dados_processados. Se os scripts de lá
forem rodados de novo, basta rodar este atualizar.py (ou --so-base) para o painel refletir a mudança.
"""
import json
import re
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
PY = sys.executable
COLETA = ["01_normas.py", "02_fundeb_fnde.py", "03_siope.py", "04_siconfi.py", "05_ibge.py"]
OPCIONAIS = {"03_siope.py"}  # falha esperada enquanto o serviço do FNDE estiver fora do ar


def rodar(args, rotulo):
    print(f"== {rotulo}", flush=True)
    r = subprocess.call([PY] + args, cwd=RAIZ)
    if r != 0:
        print(f"!! {rotulo} terminou com aviso/falha (código {r}); seguindo com o resto")
    return r == 0


def atualizar(so_base=False):
    falhas = []
    if not so_base:
        for s in COLETA:
            if not rodar([str(RAIZ / "coleta" / s)], f"coleta {s}") and s not in OPCIONAIS:
                falhas.append(s)
        censo = RAIZ / "dados" / "cache" / "censo_infra_municipal.parquet"
        iq = RAIZ.parent.parent / "02_iquems" / "02_painel_educacao_ms" / "dados_brutos" / "inep" / "censo"
        zips = list(iq.glob("censo_*.zip"))
        if zips and (not censo.exists() or max(z.stat().st_mtime for z in zips) > censo.stat().st_mtime):
            rodar([str(RAIZ / "tratamento" / "t03_censo_infra.py")], "Censo Escolar (infraestrutura)")
    for s, rot in (("montar_base.py", "montagem da base"), ("fontes.py", "catálogo de fontes"), ("conferir.py", "conferência")):
        if not rodar([str(RAIZ / "tratamento" / s)], rot):
            falhas.append(s)
    print("== concluído" + (f" com falhas em: {', '.join(falhas)}" if falhas else " sem falhas"))
    return 1 if falhas else 0


# ------------------------------------------------------------------------------------------------ --verificar

def _req():
    import truststore
    truststore.inject_into_ssl()
    import requests
    s = requests.Session()
    s.headers["User-Agent"] = "Mozilla/5.0 (pesquisa academica PPGEdu/UFMS; dados publicos)"
    return s


def _gov_itens(s, caminho):
    r = s.get("https://www.gov.br/fnde/++api++/pt-br/acesso-a-informacao/acoes-e-programas/financiamento/fundeb/" + caminho,
              params={"expand": "items"}, headers={"Accept": "application/json"}, timeout=20)
    r.raise_for_status()
    return [it.get("title", "").strip() for it in r.json().get("items", [])]


def v_planalto_lei14113(s, fim):
    r = s.get("https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2020/lei/l14113.htm", timeout=20)
    try:
        t = r.content.decode("utf-8")
    except UnicodeDecodeError:
        t = r.content.decode("latin-1")
    t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t))  # os nomes das leis vêm dentro de links
    atos = sorted(set(re.findall(r"(?:Reda..o dada pela|Inclu.d[oa] pela|Revogad[oa] pela) ((?:Lei(?: Complementar)?|Medida Provis.ria) n[ºo°] ?[\d\.]+, de \d{4})", t)))
    return "; ".join(atos), "leis que alteraram a Lei 14.113 (texto compilado do Planalto)"


def v_fnde_legislacao(s, fim):
    anos = _gov_itens(s, "legislacao")
    ult = max(int(a) for a in anos if a.isdigit())
    itens = _gov_itens(s, f"legislacao/{ult}")
    return f"pasta mais recente: {ult}; {len(itens)} atos nela; último listado: {itens[0] if itens else '—'}", "página de legislação do Fundeb"


def v_fnde_vaar_2026(s, fim):
    pub = _gov_itens(s, "2026-1/publicacoes-2026")
    pastas = [x for x in pub if not re.search(r"\.(pdf|xlsx|csv)$", x, re.I) and not re.search(r" (I|II|III)$", x)]
    try:
        tem_2027 = bool(_gov_itens(s, "2027-1"))
    except Exception:  # noqa: BLE001
        tem_2027 = False
    return (f"publicações de 2026: {len(pub)} itens; subpastas: {', '.join(pastas) or '—'}; pasta de 2027: "
            f"{'EXISTE' if tem_2027 else 'ainda não'}"), "página do Fundeb (FNDE)"


def v_fnde_fundeb_bb(s, fim):
    it = _gov_itens(s, "valores-repassados-2021-a-2025")
    anos = sorted(set(re.findall(r"(20\d\d)", " ".join(it))))
    return f"anos publicados: {', '.join(anos)} ({len(it)} arquivos)", "pasta de valores repassados (FNDE)"


def v_siope(s, fim):
    u = ("https://www.fnde.gov.br/olinda-ide/servico/DADOS_ABERTOS_SIOPE/versao/v1/odata/Indicadores_Siope(Ano_Consulta=@Ano_Consulta,"
         "Num_Peri=@Num_Peri,Sig_UF=@Sig_UF)")
    r = s.get(u, params={"@Ano_Consulta": 2024, "@Num_Peri": 6, "@Sig_UF": "'MS'", "$top": 1, "$format": "json"}, timeout=20)
    return f"serviço respondeu {r.status_code}" + (" (VOLTOU: rode atualizar.bat)" if r.ok else " (continua indisponível)"), "serviço OData do Siope"


def v_siconfi_dca(s, fim):
    ano = int(fim or 2024) + 1
    r = s.get("https://apidatalake.tesouro.gov.br/ords/siconfi/tt/dca", params={"an_exercicio": ano, "no_anexo": "DCA-Anexo I-E",
                                                                              "id_ente": "5002704"}, timeout=20)
    n = len(r.json().get("items", []))
    return f"DCA {ano} de Campo Grande: {'publicada' if n else 'ainda não publicada'} ({n} linhas)", "API do Siconfi"


def _head(s, url):
    try:
        return s.head(url, timeout=20, allow_redirects=True).status_code
    except Exception:  # noqa: BLE001
        return "sem resposta"


def v_inep_censo(s, fim):
    ano = int(fim or 2025) + 1
    st = {u: _head(s, u) for u in (f"https://download.inep.gov.br/dados_abertos/microdados_censo_escolar_{ano}.zip",
                                   f"https://download.inep.gov.br/dados_abertos/microdados_censo_escolar_{ano}_.zip")}
    ok = any(v == 200 for v in st.values())
    return f"microdados {ano}: {'PUBLICADOS' if ok else 'não encontrados nos endereços padrão'}", "download.inep.gov.br"


def v_inep_sinopse(s, fim):
    ano = int(fim or 2025) + 1
    c = _head(s, f"https://download.inep.gov.br/dados_abertos/sinopses_estatisticas/sinopse_estatistica_censo_escolar_{ano}.zip")
    return f"sinopse {ano}: {'PUBLICADA' if c == 200 else 'não encontrada no endereço padrão'}", "download.inep.gov.br"


def v_inep_remuneracao(s, fim):
    r = s.get("https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/indicadores-educacionais/remuneracao-media-dos-docentes", timeout=20)
    anos = sorted(set(int(a) for a in re.findall(r">\s*(20\d\d)\s*<", r.text) if 2010 <= int(a) <= date.today().year))
    return f"anos nas abas da página: {anos[0]}–{anos[-1]}" if anos else "página sem anos identificáveis", "página do Inep"


def _ibge(s, tab):
    r = s.get(f"https://servicodados.ibge.gov.br/api/v3/agregados/{tab}/periodos", timeout=20)
    return max(int(p["id"]) for p in r.json())


def v_ibge_pib(s, fim):
    return f"último ano publicado: {_ibge(s, 5938)}", "IBGE, tabela 5938"


def v_ibge_pop(s, fim):
    return f"última estimativa publicada: {_ibge(s, 6579)}", "IBGE, tabela 6579"


def verificar():
    import pandas as pd
    p = RAIZ / "dados" / "fontes_status.csv"
    f = pd.read_csv(p, encoding="utf-8-sig", dtype=str).fillna("")
    snap_p = RAIZ / "dados" / "verificacao_ultima.json"
    antes = json.loads(snap_p.read_text(encoding="utf-8")) if snap_p.exists() else {}
    s = _req()
    hoje = date.today().isoformat()
    linhas, agora = [], {}
    for i, r in f.iterrows():
        metodo = r["verificacao"]
        fn = globals().get(f"v_{metodo}")
        if metodo == "manual" or fn is None:
            res, onde, mudou = "conferir manualmente (sem verificação automática permitida)", "—", ""
        else:
            try:
                res, onde = fn(s, r["ano_final_na_base"])
                agora[r["id"]] = res
                mudou = "" if r["id"] not in antes else ("MUDOU desde a verificação anterior" if antes[r["id"]] != res else "sem mudança")
            except Exception as ex:  # noqa: BLE001
                res, onde, mudou = f"FONTE FORA DO AR OU COM ERRO: {type(ex).__name__}: {str(ex)[:120]}", "—", ""
                agora[r["id"]] = antes.get(r["id"], "")
        f.at[i, "ultima_verificacao"] = hoje
        f.at[i, "resultado_verificacao"] = res + (f" [{mudou}]" if mudou else "")
        linhas.append(f"| {r['item'][:70]} | {r['ano_final_na_base'] or '—'} | {res} | {mudou or 'primeira verificação' if metodo != 'manual' else '—'} |")
        print(f"[verificar] {r['id']}: {res}", flush=True)
    f.to_csv(p, index=False, encoding="utf-8-sig")
    snap_p.write_text(json.dumps(agora, ensure_ascii=False, indent=1), encoding="utf-8")
    pasta = RAIZ / "docs" / "verificacoes"
    pasta.mkdir(parents=True, exist_ok=True)
    md = [f"# Verificação das fontes — {datetime.now():%d/%m/%Y %H:%M}", "",
          "Gerado por `atualizar.py --verificar` (nada foi baixado). 'MUDOU' = a fonte publicou algo diferente desde a "
          "verificação anterior: rode `atualizar.bat` e confira.", "",
          "| fonte | último ano na base | o que a fonte mostra hoje | mudança |", "|---|---|---|---|"] + linhas
    (pasta / f"{hoje}.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"[verificar] relatório: docs/verificacoes/{hoje}.md")
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    sys.exit(verificar() if "--verificar" in a else atualizar(so_base="--so-base" in a))
