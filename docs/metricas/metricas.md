## 🎯 Métricas Alcançadas

**Modelo:** YOLOv8n · `imgsz=192` · 150 épocas treinadas · transfer learning de pesos COCO

### Resultado por classe (conjunto de **teste**)

| classe | Precision | Recall | mAP@50 | mAP@50-95 |
|:--|--:|--:|--:|--:|
| `degrau` | 0.449 | 0.100 | 0.088 | 0.030 |
| `escada` | 0.671 | 0.488 | 0.524 | 0.286 |
| `corrimao` | 0.529 | 0.108 | 0.119 | 0.039 |
| **geral (teste)** | **0.550** | **0.232** | **0.244** | **0.118** |

### Validação × Teste

| métrica | validação | teste |
|:--|--:|--:|
| mAP@50 | 0.328 | **0.244** |
| mAP@50-95 | 0.169 | **0.118** |
| Precision | 0.478 | **0.550** |
| Recall | 0.339 | **0.232** |

### Modelo exportado

| item | valor |
|:--|:--|
| formato | ONNX (opset 12), shape estático |
| entrada | `[1, 3, 192, 192]` |
| saída | `(1, 7, 756)` = `[1, 4+3, 756]` |
| NMS | feito em JS pelo app (não embutido no grafo) |
| tamanho | 12.62 MB |
| latência (CPU) | 10.4 ms (~96.0 FPS) |

### Artefatos

- `docs/metricas/curvas_treino.png` — perdas e métricas por época
- `docs/metricas/confusion_matrix_normalized.png` — matriz de confusão
- `docs/metricas/PR_curve.png` — curva Precision-Recall
- `docs/metricas/predicoes_teste.png` — inferência no conjunto de teste
