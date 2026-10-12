"""
Monta o dataset de auditoria de calçadas a partir do
"Image Dataset of Accessibility Barriers" (Zenodo 6382090, CC-BY-4.0).

O dataset original tem 8 GB num zip único, anotado em CVAT XML. Este módulo:

  1. lê o índice do zip remotamente (range requests HTTP) — sem baixar 8 GB
  2. extrai apenas o wm_annotations.xml (192 KB comprimido)
  3. converte CVAT XML -> YOLO (bbox normalizada)
  4. seleciona um subconjunto balanceado entre as classes
  5. baixa SOMENTE as imagens selecionadas (range requests) ou usa um zip local
  6. escreve a estrutura train/valid/test + data.yaml

Fonte : https://zenodo.org/records/6382090
Licença: CC-BY-4.0 — Stolberg, Jakob (2022)
         Alexander von Humboldt Institute for Internet and Society
"""

from __future__ import annotations

import collections
import random
import struct
import time
import urllib.request
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path

ZENODO_URL = (
    "https://zenodo.org/api/records/6382090/files/wm_barriers_data.zip/content"
)

# Mapeamento label original -> classe do projeto.
# 'ramp' é deliberadamente omitido: só 143 instâncias contra 3564 de 'step'
# (1:25). Com um desbalanceamento desse tamanho a classe não aprende e ainda
# suja a matriz de confusão.
LABEL_MAP = {
    "step":     "degrau",
    "stair":    "escada",
    "grab_bar": "corrimao",
}

# A ORDEM define os class_id do YOLO. Precisa ser idêntica em:
#   - data.yaml
#   - CLASSES, nos notebooks
#   - CLASS_NAMES, em app/src/main.js
CLASSES = ["degrau", "escada", "corrimao"]


# ───────────────────────── leitura remota do zip ─────────────────────────

def _http_range(url: str, start: int, end: int, tentativas: int = 6) -> bytes:
    """
    Baixa os bytes [start, end] (inclusive) via HTTP Range.

    O Zenodo limita requisições por minuto e devolve 429 quando se passa do
    limite. Também corta conexões no meio (IncompleteRead) sob carga. Por isso
    cada requisição tem retry com backoff exponencial e jitter — sem isso,
    baixar centenas de imagens perde a maioria delas.
    """
    esperado = end - start + 1
    req_headers = {"Range": f"bytes={start}-{end}",
                   "User-Agent": "cpzao-auditoria-calcadas/1.0"}

    ultimo_erro = None
    for n in range(tentativas):
        try:
            req = urllib.request.Request(url, headers=req_headers)
            with urllib.request.urlopen(req, timeout=120) as r:
                if r.status not in (200, 206):
                    raise RuntimeError(f"esperava 206, veio {r.status}")
                dados = r.read()
            if len(dados) != esperado:
                raise RuntimeError(
                    f"recebeu {len(dados)} bytes, esperava {esperado}")
            return dados
        except Exception as exc:                            # noqa: BLE001
            ultimo_erro = exc
            if n == tentativas - 1:
                break
            # 429 merece espera maior: o limite é por minuto
            e429 = "429" in str(exc) or "TOO MANY" in str(exc).upper()
            base = 8.0 if e429 else 1.5
            espera = base * (2 ** n) + random.uniform(0, 1.5)
            time.sleep(min(espera, 75.0))

    raise RuntimeError(
        f"falhou após {tentativas} tentativas ({start}-{end}): {ultimo_erro}")


def _content_length(url: str) -> int:
    req = urllib.request.Request(url, method="HEAD")
    with urllib.request.urlopen(req) as r:
        return int(r.headers["Content-Length"])


def read_central_directory(url: str = ZENODO_URL) -> list:
    """Lê o índice do zip remoto. Suporta zip64 (o arquivo passa de 4 GB)."""
    total = _content_length(url)
    tail = _http_range(url, max(0, total - 131072), total - 1)

    i = tail.rfind(b"PK\x05\x06")
    if i < 0:
        raise RuntimeError("EOCD não encontrado")

    nent = struct.unpack_from("<H", tail, i + 10)[0]
    cdsize = struct.unpack_from("<I", tail, i + 12)[0]
    cdoff = struct.unpack_from("<I", tail, i + 16)[0]

    # zip64: os campos de 32 bits saturam
    if cdoff == 0xFFFFFFFF or nent == 0xFFFF or cdsize == 0xFFFFFFFF:
        k = tail.find(b"PK\x06\x06")
        if k < 0:
            raise RuntimeError("EOCD zip64 não encontrado")
        nent = struct.unpack_from("<Q", tail, k + 32)[0]
        cdsize = struct.unpack_from("<Q", tail, k + 40)[0]
        cdoff = struct.unpack_from("<Q", tail, k + 48)[0]

    cd = _http_range(url, cdoff, cdoff + cdsize - 1)

    entries, off = [], 0
    while off < len(cd) - 4 and cd[off:off + 4] == b"PK\x01\x02":
        method = struct.unpack_from("<H", cd, off + 10)[0]
        csize = struct.unpack_from("<I", cd, off + 20)[0]
        usize = struct.unpack_from("<I", cd, off + 24)[0]
        nlen = struct.unpack_from("<H", cd, off + 28)[0]
        elen = struct.unpack_from("<H", cd, off + 30)[0]
        clen = struct.unpack_from("<H", cd, off + 32)[0]
        lho = struct.unpack_from("<I", cd, off + 42)[0]
        name = cd[off + 46: off + 46 + nlen].decode("utf-8", "replace")
        extra = cd[off + 46 + nlen: off + 46 + nlen + elen]

        if 0xFFFFFFFF in (usize, csize, lho):
            p = 0
            while p < len(extra) - 4:
                hid, hsz = struct.unpack_from("<HH", extra, p)
                if hid == 0x0001:
                    q = p + 4
                    if usize == 0xFFFFFFFF:
                        usize = struct.unpack_from("<Q", extra, q)[0]
                        q += 8
                    if csize == 0xFFFFFFFF:
                        csize = struct.unpack_from("<Q", extra, q)[0]
                        q += 8
                    if lho == 0xFFFFFFFF:
                        lho = struct.unpack_from("<Q", extra, q)[0]
                    break
                p += 4 + hsz

        entries.append({"name": name, "method": method, "csize": csize,
                        "usize": usize, "lho": lho})
        off += 46 + nlen + elen + clen

    return entries


def _descomprimir(raw: bytes, method: int, nome: str) -> bytes:
    if method == 0:
        return raw
    if method == 8:
        return zlib.decompress(raw, -15)
    raise RuntimeError(f"método de compressão não suportado em {nome}: {method}")


def extract_member(url: str, entry: dict) -> bytes:
    """
    Extrai um membro do zip remoto em UM único range request.

    O cabeçalho local tem 30 bytes + nome + campo extra. O nome já é conhecido
    pelo índice central, e o campo extra é pequeno (0 para arquivos comuns,
    ~20-32 bytes em zip64). Então pedimos cabeçalho + dados + uma folga numa
    só requisição e cortamos depois. Duas requisições por imagem fariam a
    latência dominar o tempo total.
    """
    FOLGA = 256
    nlen_est = len(entry["name"].encode("utf-8"))
    span = 30 + nlen_est + FOLGA + entry["csize"]

    buf = _http_range(url, entry["lho"], entry["lho"] + span - 1)
    if buf[:4] != b"PK\x03\x04":
        raise RuntimeError(f"cabeçalho local inválido em {entry['name']}")

    nlen = struct.unpack_from("<H", buf, 26)[0]
    elen = struct.unpack_from("<H", buf, 28)[0]
    ini = 30 + nlen + elen
    raw = buf[ini: ini + entry["csize"]]

    # Se o campo extra for maior que a folga, o buffer não alcançou o fim dos
    # dados — aí sim fazemos a requisição exata.
    if len(raw) < entry["csize"]:
        data_off = entry["lho"] + ini
        raw = _http_range(url, data_off, data_off + entry["csize"] - 1)

    return _descomprimir(raw, entry["method"], entry["name"])


def extract_many(url: str, entries: list, workers: int = 6,
                 progresso=None) -> dict:
    """
    Extrai vários membros em paralelo. Devolve {nome: bytes}.

    A latência para o Zenodo é de alguns segundos por requisição, então algum
    paralelismo é necessário para baixar centenas de imagens. Mas o Zenodo
    limita requisições por minuto: medimos 16 workers derrubando ~60% dos
    downloads com HTTP 429. Com 6 workers mais o backoff de `_http_range`,
    a taxa de perda cai para ~zero.

    Se precisar de MUITAS imagens (>1000), baixar o zip inteiro de uma vez
    (`baixar_zip_completo`) sai mais barato que milhares de requisições.
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed

    out, erros = {}, []
    total = len(entries)

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futuros = {pool.submit(extract_member, url, e): e for e in entries}
        for n, fut in enumerate(as_completed(futuros), 1):
            e = futuros[fut]
            try:
                out[e["name"]] = fut.result()
            except Exception as exc:                      # noqa: BLE001
                erros.append((e["name"], repr(exc)))
            if progresso and (n % 25 == 0 or n == total):
                progresso(n, total)

    if erros:
        print(f"⚠️  {len(erros)} download(s) falharam; serão ignorados")
        for nome, msg in erros[:5]:
            print("   •", nome, msg)

    return out


def baixar_zip_completo(destino, url: str = ZENODO_URL, progresso=None):
    """
    Baixa o zip inteiro (≈8 GB) em UMA requisição, com retomada.

    É o caminho mais robusto quando há banda sobrando (Colab, por exemplo):
    uma requisição só não encosta no rate limit do Zenodo. Se o arquivo já
    existir parcialmente, continua de onde parou.

    Devolve um `zipfile.ZipFile` aberto.
    """
    import zipfile

    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    total = _content_length(url)
    ja = destino.stat().st_size if destino.exists() else 0

    while ja < total:
        req = urllib.request.Request(
            url, headers={"Range": f"bytes={ja}-",
                          "User-Agent": "cpzao-auditoria-calcadas/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=120) as r, \
                    open(destino, "ab") as f:
                while True:
                    bloco = r.read(1 << 20)
                    if not bloco:
                        break
                    f.write(bloco)
                    ja += len(bloco)
                    if progresso:
                        progresso(ja, total)
        except Exception as exc:                            # noqa: BLE001
            ja = destino.stat().st_size if destino.exists() else 0
            print(f"  conexão caiu em {ja/1e9:.2f} GB ({exc}); retomando...")
            time.sleep(5)

    return zipfile.ZipFile(destino)


# ───────────────────────── anotações CVAT -> YOLO ─────────────────────────

#: Lado mínimo de uma caixa, em fração da imagem.
#: 2/192 porque o treino roda em 192 px: abaixo disso a caixa ocupa menos de
#: 2 pixels na entrada da rede. O modelo não tem como aprendê-la, mas continua
#: sendo penalizado por não encontrá-la — ou seja, vira ruído puro na loss e
#: derruba o recall medido. Na base original isso atinge 5,5% das caixas.
LADO_MIN_NORM = 2 / 192


def parse_annotations(xml_bytes: bytes,
                      lado_min: float = LADO_MIN_NORM) -> list:
    """
    Converte o CVAT XML para uma lista de registros:
        {name, width, height, boxes: [(class_id, cx, cy, w, h), ...]}
    com as coordenadas já normalizadas em [0,1], no formato YOLO.

    Caixas com lado menor que `lado_min` são descartadas (ver LADO_MIN_NORM).
    Passe `lado_min=0` para manter todas.
    """
    root = ET.fromstring(xml_bytes)
    registros = []

    for im in root.findall("image"):
        W = float(im.get("width"))
        H = float(im.get("height"))
        boxes = []

        for b in im.findall("box"):
            nome = LABEL_MAP.get(b.get("label"))
            if nome is None:          # label fora do escopo (ex.: ramp)
                continue

            xtl, ytl = float(b.get("xtl")), float(b.get("ytl"))
            xbr, ybr = float(b.get("xbr")), float(b.get("ybr"))

            # recorta aos limites da imagem antes de normalizar
            xtl, xbr = max(0.0, min(xtl, W)), max(0.0, min(xbr, W))
            ytl, ybr = max(0.0, min(ytl, H)), max(0.0, min(ybr, H))
            if xbr <= xtl or ybr <= ytl:
                continue              # caixa degenerada

            cx, cy = (xtl + xbr) / 2 / W, (ytl + ybr) / 2 / H
            bw, bh = (xbr - xtl) / W, (ybr - ytl) / H
            if bw <= 0 or bh <= 0:
                continue
            if bw < lado_min or bh < lado_min:
                continue              # pequena demais para a resolução de treino

            boxes.append((CLASSES.index(nome),
                          round(cx, 6), round(cy, 6),
                          round(bw, 6), round(bh, 6)))

        registros.append({"name": im.get("name"), "width": int(W),
                          "height": int(H), "boxes": boxes})

    return registros


# ───────────────────────── seleção balanceada ─────────────────────────

def select_balanced(registros: list, alvo: int = 800,
                    frac_negativas: float = 0.06,
                    seed: int = 42) -> list:
    """
    Escolhe ~`alvo` imagens tentando equilibrar as classes.

    Estratégia: processa as classes da mais RARA para a mais comum. Como
    'corrimao' e 'escada' quase sempre aparecem junto de 'degrau', priorizar
    as raras eleva as três de uma vez — pegar imagens aleatórias encheria o
    conjunto de 'degrau' sozinho.
    """
    rng = random.Random(seed)
    com_box = [r for r in registros if r["boxes"]]
    negativas = [r for r in registros if not r["boxes"]]

    por_classe = collections.defaultdict(list)
    for r in com_box:
        for cid in {b[0] for b in r["boxes"]}:
            por_classe[cid].append(r)

    ordem = sorted(por_classe, key=lambda c: len(por_classe[c]))  # rara -> comum
    n_pos = int(alvo * (1 - frac_negativas))
    cota = n_pos // len(ordem)

    escolhidas, vistos = [], set()
    for cid in ordem:
        pool = [r for r in por_classe[cid] if id(r) not in vistos]
        rng.shuffle(pool)
        for r in pool[:cota]:
            escolhidas.append(r)
            vistos.add(id(r))

    # completa com qualquer positiva restante
    resto = [r for r in com_box if id(r) not in vistos]
    rng.shuffle(resto)
    for r in resto[: max(0, n_pos - len(escolhidas))]:
        escolhidas.append(r)
        vistos.add(id(r))

    # negativas reduzem falso positivo; poucas, de propósito
    rng.shuffle(negativas)
    escolhidas += negativas[: max(0, alvo - len(escolhidas))]

    rng.shuffle(escolhidas)
    return escolhidas


def estatisticas(registros: list) -> dict:
    cnt = collections.Counter()
    for r in registros:
        for b in r["boxes"]:
            cnt[CLASSES[b[0]]] += 1
    return {
        "imagens": len(registros),
        "com_caixa": sum(1 for r in registros if r["boxes"]),
        "negativas": sum(1 for r in registros if not r["boxes"]),
        "caixas": sum(cnt.values()),
        "por_classe": {c: cnt.get(c, 0) for c in CLASSES},
    }


# ───────────────────────── escrita do dataset ─────────────────────────

def split_registros(registros: list, seed: int = 42) -> dict:
    """Divide 70/20/10 em train/valid/test."""
    rng = random.Random(seed)
    rs = list(registros)
    rng.shuffle(rs)
    n = len(rs)
    i, j = int(n * 0.70), int(n * 0.90)
    return {"train": rs[:i], "valid": rs[i:j], "test": rs[j:]}


def _redimensionar(jpeg: bytes, max_lado: int) -> bytes:
    """
    Reduz a imagem para que o maior lado seja `max_lado` e REMOVE o EXIF.

    Remover o EXIF é essencial, não cosmético: os originais são fotos de
    celular e podem trazer a tag de orientação. As anotações do CVAT foram
    feitas sobre as dimensões armazenadas no arquivo (conferimos que
    width/height do XML batem com o SOF do JPEG), então qualquer rotação
    automática aplicada na leitura desalinharia todas as caixas. Sem a tag,
    não há ambiguidade.

    As coordenadas YOLO são normalizadas, então reduzir a imagem não exige
    recalcular nada.
    """
    import io

    from PIL import Image

    im = Image.open(io.BytesIO(jpeg))
    im = im.convert("RGB")
    w, h = im.size
    if max(w, h) > max_lado:
        escala = max_lado / max(w, h)
        im = im.resize((max(1, round(w * escala)), max(1, round(h * escala))),
                       Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=88, optimize=True)   # sem exif
    return buf.getvalue()


def escrever_dataset(splits: dict, destino, ler_imagem, progresso=None,
                     max_lado: int = 640):
    """
    Escreve a estrutura YOLO em `destino`. `ler_imagem` recebe o nome do
    membro ('images/000123.jpg') e devolve os bytes do JPEG.

    `max_lado=640` reduz as imagens (originais ~1350x1800). O treino roda em
    192, então 640 é folga de sobra e economiza disco e tempo de I/O.
    Passe `max_lado=0` para guardar o original.
    """
    destino = Path(destino)
    for split in splits:
        (destino / split / "images").mkdir(parents=True, exist_ok=True)
        (destino / split / "labels").mkdir(parents=True, exist_ok=True)

    total = sum(len(v) for v in splits.values())
    feitas = 0

    for split, regs in splits.items():
        for r in regs:
            stem = Path(r["name"]).stem
            jpeg = ler_imagem(r["name"])
            if max_lado:
                jpeg = _redimensionar(jpeg, max_lado)
            (destino / split / "images" / f"{stem}.jpg").write_bytes(jpeg)
            linhas = [f"{c} {cx} {cy} {w} {h}" for c, cx, cy, w, h in r["boxes"]]
            (destino / split / "labels" / f"{stem}.txt").write_text(
                "\n".join(linhas) + ("\n" if linhas else ""))
            feitas += 1
            if progresso and feitas % 25 == 0:
                progresso(feitas, total)

    (destino / "data.yaml").write_text(
        f"path: {destino.resolve()}\n"
        "train: train/images\n"
        "val: valid/images\n"
        "test: test/images\n\n"
        f"nc: {len(CLASSES)}\n"
        "names:\n" + "".join(f"  - {c}\n" for c in CLASSES) +
        "\n# Derivado de: Image Dataset of Accessibility Barriers\n"
        "# Stolberg, Jakob (2022) · CC-BY-4.0 · https://zenodo.org/records/6382090\n"
    )
    return destino
