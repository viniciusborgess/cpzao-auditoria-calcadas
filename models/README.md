# Modelos treinados

| arquivo | formato | imgsz | uso |
|:--|:--|:--:|:--|
| `best.pt` | PyTorch (Ultralytics) | 192 | pesos de referência / re-export |
| `best.onnx` | ONNX opset 12 | 192 | **inferência no celular** (ONNX Runtime Web) |

> ⚠️ O `best.onnx` **precisa** ter sido exportado com `imgsz=192`.
> O app (`app/src/inference.js`) usa `INPUT_W = INPUT_H = 192` fixo.
> Um modelo exportado em 640 carrega mas produz caixas completamente erradas.

Gerados pelo notebook [`../notebooks/02_treino_export.ipynb`](../notebooks/02_treino_export.ipynb).
Para usar no app, copie o `best.onnx` para `app/public/models/`.
