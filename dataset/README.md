# Dataset — Auditoria de Calçadas

As **imagens não são versionadas** no Git (ver `.gitignore`) para manter o repositório leve.
Esta pasta guarda a estrutura e a definição do dataset.

## Estrutura esperada (formato YOLOv8)

```
dataset/
├── data.yaml          ← versionado (definição das classes)
├── raw/               ← suas fotos originais, antes da anotação
├── train/
│   ├── images/
│   └── labels/
├── valid/
│   ├── images/
│   └── labels/
└── test/
    ├── images/
    └── labels/
```

## Classes

| id | nome         | descrição                                                        |
|:--:|:-------------|:-----------------------------------------------------------------|
| 0  | `buraco`     | buraco, cratera, trinca profunda ou piso quebrado/faltante       |
| 1  | `piso_tatil` | piso tátil direcional ou de alerta (faixa amarela/cinza em relevo) |
| 2  | `obstaculo`  | poste, lixeira, hidrante, bicicletário, mesa ou qualquer objeto que bloqueie a faixa livre |

## Como obter

1. **Fotos próprias (recomendado):** siga o protocolo em [`../CAPTURA.md`](../CAPTURA.md).
2. **Anotação:** Roboflow → exportar em **YOLOv8** → colar a URL no notebook `01_dataset_prep.ipynb`.
3. O notebook `01` faz o split 70/20/10 e gera as estatísticas que entram no README.
