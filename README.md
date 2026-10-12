# 🚧 Auditoria de Calçadas com Visão Computacional

**CPZÃO — Checkpoint Integrado** · Pipeline completo de Visão Computacional, da aquisição de
dados à inferência em tempo real na borda (*edge computing*).

Detecção de defeitos, obstáculos e elementos de acessibilidade em calçadas urbanas com
**YOLOv8n**, exportado para **ONNX** e executado **diretamente no navegador do celular** via
ONNX Runtime Web (WebAssembly) — sem servidor, sem upload de imagem, processamento 100% local.

---

## 👥 Integrantes do Grupo

> ⚠️ **PREENCHER ANTES DE ENTREGAR**

| Nome completo | RM |
|:--|:--|
| *(nome)* | *(RM)* |
| *(nome)* | *(RM)* |
| *(nome)* | *(RM)* |
| *(nome)* | *(RM)* |

---

## 📌 O Problema

Calçadas em más condições são uma barreira concreta de mobilidade urbana. Para quem usa cadeira
de rodas, tem baixa visão ou simplesmente empurra um carrinho de bebê, um buraco, um poste
plantado no meio do caminho ou a ausência de piso tátil deixa de ser um incômodo e passa a ser
um impedimento.

O gargalo não é saber que o problema existe — é **mapeá-lo em escala**. Auditar calçadas
manualmente é lento e caro: a [auditoria de referência](https://falzoni.com.br/auditoriacalcadas/)
cobriu 65 km de calçadas e 578 travessias com observação de campo. Uma cidade do tamanho de
São Paulo tem mais de 30 mil km de calçadas.

**A proposta deste projeto:** transformar qualquer smartphone em um instrumento de auditoria.
O agente percorre a calçada, aponta a câmera traseira, e o modelo identifica e classifica os
problemas em tempo real. A inferência roda na borda — no próprio aparelho — o que elimina custo
de servidor, funciona sem conexão e não transmite imagens da via pública para lugar nenhum.

### Por que na borda?

| | servidor (nuvem) | **borda (este projeto)** |
|:--|:--|:--|
| latência | upload + fila + download | ~100 ms, local |
| funciona offline | ❌ | ✅ (PWA instalável) |
| custo por inferência | $ por imagem | zero |
| privacidade | imagens saem do aparelho | nada sai do aparelho |
| custo de infra | instância + storage | hospedagem estática |

---

## 🏷️ Classes Definidas

Três classes escolhidas para cobrir as dimensões independentes de uma auditoria — **defeito
estrutural**, **recurso de acessibilidade** e **obstrução da faixa livre** — e, ao mesmo tempo,
por serem visualmente distintas entre si (o que mantém a matriz de confusão limpa com um
dataset pequeno).

| id | classe | cor no app | o que inclui | o que **não** inclui |
|:--:|:--|:--|:--|:--|
| 0 | `buraco` | 🔴 vermelho | buraco, cratera, trinca profunda, pedaço de piso faltando ou quebrado | junta de dilatação, risco superficial, mancha |
| 1 | `piso_tatil` | 🟡 amarelo | piso tátil direcional (linhas) e de alerta (pontos) | sinalização pintada no chão, grades de drenagem |
| 2 | `obstaculo` | 🟢 verde | poste, lixeira, hidrante, bicicletário, mesa, placa **sobre a calçada** | poste na rua ou atrás do muro, objeto que não bloqueia a faixa livre |

> As regras de anotação completas estão em **[`CAPTURA.md`](CAPTURA.md)** — foi o critério
> usado de forma consistente em todas as imagens.

---

## 📊 Estatísticas do Dataset

> ⚠️ **PREENCHER** com a saída da célula 9 do notebook `01_dataset_prep.ipynb`
> (ela já gera esta tabela em Markdown, pronta para colar).

| split | imagens | caixas | `buraco` | `piso_tatil` | `obstaculo` |
|:--|--:|--:|--:|--:|--:|
| **train** | — | — | — | — | — |
| **val** | — | — | — | — | — |
| **test** | — | — | — | — | — |
| **TOTAL** | — | — | — | — | — |

- **Anotação:** Roboflow · export formato YOLOv8
- **Pré-processamento:** Auto-Orient + Resize *fit* 640×640
- **Augmentation (somente no train):** flip horizontal, brilho ±20%, blur ≤1.5px, rotação ±10°
- **Divisão:** 70% train / 20% val / 10% test

| evidência | arquivo |
|:--|:--|
| distribuição das classes e tamanho das caixas | `docs/metricas/dataset_stats.png` |
| anotações desenhadas sobre as imagens | `docs/metricas/anotacoes_amostra.png` |

---

## 🎯 Métricas Alcançadas

> ⚠️ **PREENCHER** com a saída da célula 11 do notebook `02_treino_export.ipynb`
> (também já gera o bloco pronto).

**Modelo:** YOLOv8n · `imgsz=192` · transfer learning dos pesos COCO

### Por classe (conjunto de **teste** — imagens nunca vistas pelo modelo)

| classe | Precision | Recall | mAP@50 | mAP@50-95 |
|:--|--:|--:|--:|--:|
| `buraco` | — | — | — | — |
| `piso_tatil` | — | — | — | — |
| `obstaculo` | — | — | — | — |
| **geral** | — | — | — | — |

### Validação × Teste

| métrica | validação | teste |
|:--|--:|--:|
| mAP@50 | — | — |
| mAP@50-95 | — | — |
| Precision | — | — |
| Recall | — | — |

> As métricas de **teste** são as oficiais. O conjunto de validação guiou o *early stopping*,
> então seus números são otimistas por construção; o teste nunca influenciou nenhuma decisão.

| evidência | arquivo |
|:--|:--|
| matriz de confusão normalizada | `docs/metricas/confusion_matrix_normalized.png` |
| curva Precision-Recall | `docs/metricas/PR_curve.png` |
| curva F1 × confiança | `docs/metricas/F1_curve.png` |
| perdas e métricas por época | `docs/metricas/curvas_treino.png` |
| inferência no conjunto de teste | `docs/metricas/predicoes_teste.png` |

---

## 🏗️ Arquitetura do Pipeline

```
┌─────────────────┐   ┌──────────────┐   ┌──────────────┐   ┌─────────────────┐
│  1. AQUISIÇÃO   │   │ 2. ANOTAÇÃO  │   │  3. TREINO   │   │  4. DEPLOY      │
│                 │   │              │   │              │   │                 │
│  câmera do      │──▶│  Roboflow    │──▶│  YOLOv8n     │──▶│  ONNX Runtime   │
│  celular        │   │  3 classes   │   │  Colab (T4)  │   │  Web (WASM)     │
│  (traseira)     │   │  YOLOv8 fmt  │   │  imgsz=192   │   │  PWA no celular │
└─────────────────┘   └──────────────┘   └──────────────┘   └─────────────────┘
     CAPTURA.md         CAPTURA.md          notebook 02           app/
                        notebook 01
```

### A restrição que amarra todo o projeto

O app tem o tamanho de entrada **fixo em código** (`app/src/inference.js`, linhas 3–4):

```js
const INPUT_W = 192;
const INPUT_H = 192;
```

Portanto o modelo **precisa** ser treinado e exportado com `imgsz=192`. Um modelo em 640 carrega
sem erro e desenha caixas em posições completamente erradas — é a falha mais traiçoeira do
pipeline, porque não gera exceção. A célula 9 do notebook 02 verifica isso automaticamente,
replicando em Python a função `detectOutputConventions()` do app.

### Contrato modelo ↔ app

| item | valor | verificado em |
|:--|:--|:--|
| formato | ONNX, opset 12, shape estático | notebook 02, célula 9 |
| entrada | `[1, 3, 192, 192]`, float32, RGB, `/255` | idem |
| saída | `[1, 7, 756]` → `4 + 3 classes` × 756 âncoras | idem |
| NMS | **não** embutido no grafo — o app faz em JS | idem |
| coordenadas | pixel (0–192) → app usa preprocess *letterbox* | idem |
| classes | 3, na mesma ordem do `data.yaml` | `app/src/main.js` |

> **Por que 756 âncoras:** com entrada 192, o YOLOv8 gera grids em 3 escalas —
> 24² + 12² + 6² = 576 + 144 + 36 = **756**.

---

## 📁 Estrutura do Repositório

```
cpzao-auditoria-calcadas/
├── README.md                       ← este arquivo
├── CAPTURA.md                      ← protocolo de captura e regras de anotação
├── notebooks/
│   ├── 01_dataset_prep.ipynb       ← aquisição, validação, split, estatísticas
│   └── 02_treino_export.ipynb      ← treino, métricas, export ONNX, verificação
├── app/                            ← PWA de inferência (fork do yoloinferApp)
│   ├── index.html
│   ├── src/
│   │   ├── main.js                 ← CLASS_NAMES, cores, render, NMS
│   │   ├── inference.js            ← ONNX Runtime Web, pré/pós-processamento
│   │   └── style.css
│   └── public/
│       ├── models/calcadas.onnx    ← ⬅️ o modelo treinado vai AQUI
│       └── manifest.json           ← metadados do PWA
├── models/
│   ├── best.pt                     ← pesos PyTorch (referência)
│   └── best.onnx                   ← modelo exportado
├── dataset/
│   ├── data.yaml                   ← definição das 3 classes
│   └── raw/                        ← fotos originais (não versionadas)
└── docs/metricas/                  ← gráficos e matriz de confusão
```

---

## 🚀 Como Executar

### Pré-requisitos

- **Node.js 18+** (`node --version`)
- Celular e computador **na mesma rede Wi-Fi**
- Conta no [Google Colab](https://colab.research.google.com) (GPU grátis) e no
  [Roboflow](https://roboflow.com) (plano free)

### Parte 1 — Dataset e Treino

```bash
git clone https://github.com/<seu-usuario>/cpzao-auditoria-calcadas.git
cd cpzao-auditoria-calcadas
```

1. Siga o **[`CAPTURA.md`](CAPTURA.md)**: capture 80+ fotos, anote no Roboflow nas 3 classes,
   exporte em formato YOLOv8.
2. Abra **`notebooks/01_dataset_prep.ipynb`** no Colab (runtime **GPU**). Preencha a API key e
   rode tudo. Ele valida as anotações e confere a conformidade com a rubrica.
3. Abra **`notebooks/02_treino_export.ipynb`**. Treina, mostra as métricas e exporta o ONNX.
   **Não prossiga se a célula 9 mostrar algum ❌** — o modelo não funcionaria no celular.
4. Baixe os artefatos e distribua no repositório:

```bash
cp ~/Downloads/calcadas.onnx app/public/models/
cp ~/Downloads/best.pt       models/
cp ~/Downloads/*.png ~/Downloads/labels.jpg docs/metricas/
```

5. Cole no README os blocos gerados pelos notebooks (`dataset_stats.md` e `metricas.md`) nas
   seções marcadas com ⚠️ **PREENCHER**.

### Parte 2 — Rodar o app no celular

#### Opção A — servidor local (rápido, bom para desenvolver)

```bash
cd app
npm install
npm run dev -- --host
```

O Vite imprime duas URLs. Abra a **Network** no celular:

```
➜  Local:   https://localhost:5173/
➜  Network: https://192.168.0.189:5173/   ← esta, no celular
```

O certificado é autoassinado, então o navegador vai alertar:
**"Avançado" → "Prosseguir para 192.168.0.x (não seguro)"**.

> 🔒 **Por que HTTPS é obrigatório:** `getUserMedia()` — a API de câmera — só funciona em
> *secure context*. Em `http://` por IP o navegador **não** entrega a câmera. É por isso que o
> projeto usa o plugin `basicSsl` no modo dev.

#### Opção B — deploy público (recomendado para a apresentação)

Uma URL HTTPS real torna o app instalável como PWA e elimina o aviso de certificado — bem mais
confiável na frente da turma do que depender do Wi-Fi da sala.

```bash
cd app
npm run build

# Netlify
npx netlify-cli deploy --prod --dir=dist

# ou Vercel
npx vercel --prod
```

#### Instalar como aplicativo no celular

- **Android / Chrome:** menu ⋮ → *Instalar aplicativo* (ou *Adicionar à tela inicial*)
- **iOS / Safari:** botão Compartilhar → *Adicionar à Tela de Início*

Instalado, abre em tela cheia, sem barra de navegador, e funciona offline (service worker).

#### Usar

1. Toque em **📷 Start** e **permita o acesso à câmera**.
2. O app usa a **câmera traseira** automaticamente (`facingMode: 'environment'`).
3. Aponte para a calçada. As caixas aparecem em tempo real com classe e confiança.
4. **Confiança** e **Limiar IoU** são ajustáveis nos sliders.

---

## 🎛️ Ajuste Fino na Demonstração

| sintoma | causa provável | o que fazer |
|:--|:--|:--|
| não detecta nada | confiança alta demais | baixe o slider **Confiança** para ~0.20 |
| caixas em todo lugar | confiança baixa demais | suba para ~0.45 |
| caixas duplicadas no mesmo objeto | NMS permissivo | baixe **IoU** para ~0.30 |
| caixas deslocadas / fora do objeto | **modelo não exportado em 192** | re-exporte com `imgsz=192` |
| travando, poucos FPS | modelo grande demais | confirme que é `yolov8n` (não `s`/`m`) |
| câmera não abre | contexto não seguro | use `https://` (Opção A ou B acima) |

> 💡 **Antes da apresentação:** rode a curva F1 × confiança do notebook 02 e use o valor de pico
> como confiança inicial. É o limiar ótimo medido do *seu* modelo, não um palpite.

---

## ✅ Cobertura da Rubrica

| critério | pts | onde está |
|:--|:--:|:--|
| **Dataset & Rotulagem** — 60+ fotos, 3 classes, consistência, split correto | 4,0 | [`CAPTURA.md`](CAPTURA.md) · [notebook 01](notebooks/01_dataset_prep.ipynb) (célula 6 confere a rubrica automaticamente) · `docs/metricas/` |
| **Treinamento & Métricas** — pipeline funcional, análise, export correto | 6,0 | [notebook 02](notebooks/02_treino_export.ipynb) · matriz de confusão, PR, F1, curvas · export ONNX verificado |
| **Deploy Mobile** — integração com o `yoloinferApp`, inferência fluida | 6,0 | [`app/`](app/) · câmera traseira em tempo real · PWA instalável |
| **Organização & GitHub** — repositório e documentação | 4,0 | este README · notebooks documentados · estrutura modular |

---

## 🔧 Decisões Técnicas

**Por que YOLOv8n e não um modelo maior?**
A inferência roda sob WebAssembly, single-thread, na CPU do celular. O nano é o único tamanho
da família que mantém taxa de quadros utilizável nesse ambiente. Em `imgsz=192`, o grafo tem
~756 âncoras e ~3 MB.

**Por que ONNX e não TFLite?**
Imposto pelo app base: o `yoloinferApp` é uma PWA que usa **ONNX Runtime Web**. TFLite exigiria
um app nativo Android (Kotlin + build). A PWA ainda tem a vantagem de rodar em Android e iOS a
partir do mesmo código.

**Por que o NMS fica fora do modelo?**
O app implementa NMS em JavaScript com limiares ajustáveis por slider em tempo real
(`setConf`/`setIou`). Embutir o NMS no grafo ONNX congelaria esses valores no momento do export
e mudaria o shape da saída, quebrando o parser do app.

**Por que transfer learning dos pesos COCO?**
Com 60–80 imagens, treinar de zero não converge. Os pesos COCO já trazem detectores de borda,
textura e forma; o treino só reaprende a cabeça de classificação. É o que viabiliza um mAP
utilizável nessa escala de dados.

---

## 📚 Referências

- [Auditoria de Calçadas — Projeto e Metodologia](https://falzoni.com.br/auditoriacalcadas/) — fundamentação e metodologia de referência
- [yoloinferApp](https://github.com/Mjrovai/yoloinferApp) — app base de inferência mobile, por **Marcelo Rovai**
- [Notebook de Aquisição de Dados](https://colab.research.google.com/drive/1WwkI80sm8gJfrYIiCIOiysChPeg1Km_B) — material de apoio da disciplina
- [Ultralytics YOLOv8](https://docs.ultralytics.com/) · [ONNX Runtime Web](https://onnxruntime.ai/docs/tutorials/web/)

---

## 📄 Licença

Código do app derivado do [yoloinferApp](https://github.com/Mjrovai/yoloinferApp)
(ver [`app/LICENSE`](app/)) — crédito a Marcelo Rovai.
Projeto desenvolvido para fins acadêmicos.
