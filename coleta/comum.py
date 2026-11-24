"""Utilitários dos coletores: caminhos, registro, consulta ao robots.txt e download com manifesto.

Regras (ver README.md e PROGRESSO.md):
- só dados públicos, sem login;
- antes de baixar de um site, o robots.txt é consultado e respeitado;
- o portal de legislação de MS (aacpdappls.net.ms.gov.br) proíbe acesso automatizado: nada é baixado de lá;
- arquivo que já existe (nesta pasta, em 04_dados_ICMS_IQE_VAAR ou no painel do Iquems) não é baixado de novo;
- todo download entra no manifesto dados_brutos/manifesto_downloads.csv (endereço, data, tamanho, sha256).
"""
import csv
import hashlib
import json
import time
import urllib.parse
import urllib.robotparser
from datetime import datetime
from pathlib import Path

import truststore

truststore.inject_into_ssl()  # alguns servidores do governo mandam a cadeia de certificados incompleta

import requests  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
BRUTOS = RAIZ / "dados_brutos"
BASE = RAIZ / "dados" / "base"
DADOS = RAIZ / "dados"
DOCS = RAIZ / "docs"
# fontes vizinhas, só leitura
PESQUISAS = RAIZ.parent.parent
FONTE_AB = RAIZ.parent / "04_dados_ICMS_IQE_VAAR"
IQUEMS = PESQUISAS / "02_iquems" / "02_painel_educacao_ms"

UA = {"User-Agent": "Mozilla/5.0 (pesquisa academica PPGEdu/UFMS; dados publicos)"}
PROIBIDOS = ("aacpdappls.net.ms.gov.br", "in.gov.br")  # legislação de MS (proibido a robôs) e DOU (robots: Disallow /)
MANIFESTO = BRUTOS / "manifesto_downloads.csv"
CAMPOS_MANIFESTO = ["grupo", "arquivo", "url", "baixado_em", "bytes", "sha256", "observacao"]
_robots = {}


def log(msg):
    linha = f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}"
    print(linha, flush=True)
    with open(RAIZ / "coleta.log", "a", encoding="utf-8") as f:
        f.write(linha + "\n")


def robots_permite(url):
    """True se o robots.txt do site permite o endereço (sem robots.txt = permitido)."""
    host = urllib.parse.urlparse(url).netloc
    if any(host.endswith(p) for p in PROIBIDOS):
        return False
    if host not in _robots:
        rp = urllib.robotparser.RobotFileParser()
        try:
            r = requests.get(f"https://{host}/robots.txt", headers=UA, timeout=30)
            if r.status_code == 200 and "html" not in r.headers.get("Content-Type", ""):
                rp.parse(r.text.splitlines())
            else:
                rp.parse([])  # 404 ou página de erro: sem restrição publicada
        except requests.RequestException:
            rp.parse([])  # servidor sem resposta para robots.txt: registra e segue (como no 04_dados)
            log(f"robots.txt de {host} sem resposta; tratado como sem restrição")
        _robots[host] = rp
    return _robots[host].can_fetch(UA["User-Agent"], url)


def sha256(p: Path):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def registrar(grupo, destino: Path, url, obs=""):
    novo = not MANIFESTO.exists()
    MANIFESTO.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFESTO, "a", newline="", encoding="utf-8-sig" if novo else "utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS_MANIFESTO)
        if novo:
            w.writeheader()
        w.writerow({"grupo": grupo, "arquivo": destino.relative_to(BRUTOS).as_posix(), "url": url,
                    "baixado_em": f"{datetime.now():%d/%m/%Y %H:%M}", "bytes": destino.stat().st_size,
                    "sha256": sha256(destino), "observacao": obs})


def baixar(url, destino: Path, grupo, params=None, pausa=0.7, tentativas=3, obs=""):
    """Baixa url para destino, se ainda não existir. Devolve o caminho ou None (falha registrada no log)."""
    if destino.exists() and destino.stat().st_size > 0:
        return destino
    if not robots_permite(url):
        log(f"robots.txt NÃO permite {url}: não baixado")
        return None
    destino.parent.mkdir(parents=True, exist_ok=True)
    for t in range(1, tentativas + 1):
        try:
            r = requests.get(url, params=params, headers=UA, timeout=300)
            r.raise_for_status()
            tmp = destino.with_suffix(destino.suffix + ".part")
            tmp.write_bytes(r.content)
            tmp.replace(destino)
            registrar(grupo, destino, r.url, obs)
            time.sleep(pausa)
            return destino
        except Exception as ex:  # noqa: BLE001 — qualquer falha de rede vira registro, não interrompe as outras fontes
            log(f"falha {t}/{tentativas} em {url}: {ex}")
            time.sleep(3 * t)
    return None


def get_json(url, params=None, timeout=120):
    if not robots_permite(url):
        raise PermissionError(f"robots.txt não permite {url}")
    r = requests.get(url, params=params, headers={**UA, "Accept": "application/json"}, timeout=timeout)
    r.raise_for_status()
    return r.json()


def salvar_json(obj, caminho: Path):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")


def ler_json(caminho: Path, padrao=None):
    if caminho.exists():
        return json.loads(caminho.read_text(encoding="utf-8"))
    return padrao


def municipios():
    """Os 79 municípios (código IBGE de 7 dígitos), da tabela oficial do 04_dados (API do IBGE)."""
    import pandas as pd
    return pd.read_csv(FONTE_AB / "dados_processados" / "01_municipios_ms.csv", dtype={"cod_ibge": str},
                       encoding="utf-8-sig")
