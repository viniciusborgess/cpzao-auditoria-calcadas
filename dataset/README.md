# Dataset — Auditoria de Acessibilidade em Calçadas

As **imagens não são versionadas** no Git (ver `.gitignore`): o dataset é reconstruído
integralmente pelo [`notebooks/01_dataset_prep.ipynb`](../notebooks/01_dataset_prep.ipynb)
a partir de uma fonte pública, então versionar centenas de JPEGs não traria nada.

## Estrutura gerada

```
dataset/
├── data.yaml          ← versionado (definição das classes)
├── calcadas/          ← gerado pelo notebook 01 (não versionado)
│   ├── data.yaml      ← com caminhos absolutos, é o que o treino consome
│   ├── train/{images,labels}/
│   ├── valid/{images,labels}/
│   └── test/{images,labels}/
└── raw/               ← opcional: fotos próprias, antes da anotação
```

## Classes

| id | nome | label original | o que é |
|:--:|:--|:--|:--|
| 0 | `degrau` | `step` | desnível isolado: guia de calçada, soleira, mudança de nível |
| 1 | `escada` | `stair` | dois ou mais degraus em sequência |
| 2 | `corrimao` | `grab_bar` | apoio/guarda-corpo de escada ou rampa |

A label `ramp` do dataset original foi descartada: 143 instâncias contra 3.564 de `step`
(1:25) — com esse desbalanceamento a classe não aprende e suja a matriz de confusão.

## Composição atual

| split | imagens | caixas | `degrau` | `escada` | `corrimao` |
|:--|--:|--:|--:|--:|--:|
| train | 420 | 949 | 308 | 324 | 317 |
| valid | 120 | 247 | 78 | 86 | 83 |
| test | 60 | 130 | 50 | 43 | 37 |
| **TOTAL** | **600** | **1326** | **436** | **453** | **437** |

Balanceamento 0,96 · 36 imagens negativas · 0 problemas estruturais nas labels.

## Origem

**Image Dataset of Accessibility Barriers**
Stolberg, Jakob (2022) — Alexander von Humboldt Institute for Internet and Society
https://zenodo.org/records/6382090 · **CC-BY-4.0**

As anotações originais estão em CVAT XML (caixas em pixels absolutos). A conversão para YOLO
(centro e tamanho normalizados), a seleção balanceada e a divisão 70/20/10 estão em
[`../scripts/zenodo_dataset.py`](../scripts/zenodo_dataset.py).

## Como regenerar

Rode o notebook 01 no Colab — não precisa de nenhuma chave de API ou cadastro.

Localmente:

```python
import sys; sys.path.insert(0, "scripts")
import zenodo_dataset as z

entries  = z.read_central_directory()
por_nome = {e["name"]: e for e in entries}
regs     = z.parse_annotations(z.extract_member(z.ZENODO_URL, por_nome["wm_annotations.xml"]))
sel      = z.select_balanced(regs, alvo=600)
blobs    = z.extract_many(z.ZENODO_URL, [por_nome[r["name"]] for r in sel], workers=6)
z.escrever_dataset(z.split_registros(sel), "dataset/calcadas", lambda n: blobs[n])
```

## Fotos próprias (opcional)

Para ampliar o dataset com imagens do local da apresentação, veja
[`../CAPTURA.md`](../CAPTURA.md).
