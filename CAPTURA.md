# 📸 Opcional — Ampliar o Dataset com Fotos Próprias

> **Este passo não é necessário.** O dataset do projeto é montado automaticamente pelo
> [`notebooks/01_dataset_prep.ipynb`](notebooks/01_dataset_prep.ipynb) a partir de uma base
> pública aberta ([Zenodo 6382090](https://zenodo.org/records/6382090), CC-BY-4.0), com
> centenas de imagens já anotadas. A rubrica exige no mínimo 60 — o notebook entrega muito
> mais que isso sem você tirar uma única foto.
>
> Siga este guia só se quiser **melhorar a demonstração ao vivo**.

---

## Por que isso melhoraria a demo

O dataset público é de espaços públicos europeus. `degrau`, `escada` e `corrimao` são
visualmente universais — um corrimão metálico é um corrimão metálico em qualquer lugar —
então o modelo transfere bem. É por isso que essas três classes foram escolhidas.

Ainda assim, um modelo vê melhor o que já viu. Acrescentar **20–30 fotos do corredor, da
escada e da rampa da própria faculdade** ancora o modelo no domínio exato da apresentação.
Custa ~30 min e reduz o risco na parte que vale **6 dos 20 pontos**.

Se o tempo estiver curto, **pule**. O modelo treinado só com a base pública funciona.

---

## 1. Captura (~15 min)

### Onde

**No local exato da apresentação.** Escada do prédio, corrimão da rampa, guia da calçada
na entrada. Se você vai demonstrar no corredor do segundo andar, fotografe o corredor do
segundo andar.

### Quanto

| classe | fotos | o que procurar |
|:--|:--:|:--|
| `degrau` | ~10 | guia de calçada, soleira de porta, desnível isolado de um único degrau |
| `escada` | ~10 | qualquer escada — dois ou mais degraus em sequência contam |
| `corrimao` | ~10 | corrimão de escada, guarda-corpo de rampa, barra de apoio |

Uma escada com corrimão é **uma foto que conta para duas classes**. Procure esses
enquadramentos — rendem o dobro.

### Como

- **Câmera traseira**, sem zoom.
- Altura do peito, inclinada **30–50° para baixo**.
- Distância: **1 a 3 m**. Varie dentro da faixa.
- O alvo deve ocupar de ~10% a ~60% do quadro.
- Varie luz (sol, sombra, interior), ângulo (frontal, lateral, diagonal) e piso.
- Evite: tremido, contraluz forte, alvo cortado na borda.

---

## 2. Importar (1 comando)

Mande as fotos para o Mac (AirDrop, cabo, tanto faz) e rode:

```bash
cd ~/Documents/cpzao-auditoria-calcadas
./scripts/preparar_fotos.sh
```

O script move as imagens de `~/Downloads` para `dataset/raw/`, **converte HEIC → JPG**
(o iPhone salva em HEIC e o Roboflow não lê), renumera em sequência e conta o resultado.

Outra pasta de origem:

```bash
./scripts/preparar_fotos.sh ~/Desktop/fotos
```

---

## 3. Anotar no Roboflow (~15 min)

Conta gratuita em [roboflow.com](https://roboflow.com).

1. **Create New Project** → Object Detection → nome `auditoria-calcadas`
2. Upload da pasta `dataset/raw/`
3. Crie as 3 classes com os nomes **exatos** — minúsculo, sem acento, com underscore:
   `degrau` · `escada` · `corrimao`

### Regras de anotação

Use as mesmas regras da base pública, para que suas fotos e as dela sejam consistentes
entre si. São as regras originais do
[protocolo do dataset](https://zenodo.org/records/6382090):

| classe | regra |
|:--|:--|
| `degrau` | A caixa envolve **exatamente a parte vertical** do desnível — não se estende para a superfície horizontal de cima nem de baixo. Só conte desníveis que funcionam como passagem entre duas superfícies de circulação. |
| `escada` | Dois ou mais degraus em sequência = **uma caixa** envolvendo o conjunto todo. Não faça uma caixa por degrau. |
| `corrimao` | Uma caixa por corrimão. Escada com corrimão nos dois lados = 2 caixas. |
| **todas** | Caixa justa, sem folga. Anote **todas** as instâncias visíveis. Objeto visível só pela metade: anote a parte visível. Menos que isso: pule. |

> ⚠️ Fotografado **de cima**, onde o degrau não é visível como desnível, o objeto **não é
> anotado** — mesmo que um humano saiba que há um degrau ali. Essa é a regra da base
> original; mantê-la é o que torna o conjunto consistente.

### Gerar a versão

**Generate** → Train/Test Split `70/20/10` → Preprocessing: **Auto-Orient** + Resize
*Fit within* `640×640` → Augmentation: flip horizontal, brilho ±20%, blur ≤1.5px → **Create**

**Download Dataset** → formato **YOLOv8** → *show download code*.

---

## 4. Juntar com a base pública

No [`notebooks/01_dataset_prep.ipynb`](notebooks/01_dataset_prep.ipynb), depois da célula 7
(que escreve o dataset), acrescente uma célula:

```python
# Baixa suas fotos anotadas e junta ao dataset público
!pip install -q roboflow
from roboflow import Roboflow
rf = Roboflow(api_key="SUA_API_KEY")
meu = rf.workspace("SEU_WORKSPACE").project("auditoria-calcadas").version(1).download("yolov8")

import shutil
from pathlib import Path
origem = Path(meu.location)
for split_rf, split_nosso in [("train", "train"), ("valid", "valid"), ("test", "test")]:
    for sub in ("images", "labels"):
        src = origem / split_rf / sub
        if not src.is_dir():
            continue
        for f in src.iterdir():
            shutil.copy(f, DEST / split_nosso / sub / f"minha_{f.name}")

print("✅ fotos próprias integradas")
```

> ⚠️ Confirme que a **ordem das classes** no seu projeto do Roboflow é a mesma:
> `degrau`, `escada`, `corrimao`. Os `class_id` das labels seguem essa ordem — se estiver
> trocada, o modelo aprende os rótulos errados. A célula 4 do notebook 01 faz essa checagem.

Depois rode as células de validação e estatísticas novamente, e siga para o notebook 02.
