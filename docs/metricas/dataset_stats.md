## 📊 Estatísticas do Dataset

| split | imagens | caixas | `degrau` | `escada` | `corrimao` |
|:--|--:|--:|--:|--:|--:|
| **train** | 420 | 949 | 308 | 324 | 317 |
| **valid** | 120 | 247 | 78 | 86 | 83 |
| **test** | 60 | 130 | 50 | 43 | 37 |
| **TOTAL** | **600** | **1326** | **436** | **453** | **437** |

- **Total de imagens:** 600
- **Total de caixas:** 1326
- **Média de caixas por imagem:** 2.21
- **Imagens negativas (sem objeto):** 36 — reduzem falso positivo
- **Divisão:** 420 train / 120 valid / 60 test (70/20/10)
- **Balanceamento entre classes:** 0.96 (menor/maior)
- **Resolução:** reduzida para 640 no maior lado, EXIF removido
- **Validação das labels:** 0 problema(s) estrutural(is)
- **Fonte:** [Image Dataset of Accessibility Barriers](https://zenodo.org/records/6382090) — Stolberg, Jakob (2022), CC-BY-4.0
