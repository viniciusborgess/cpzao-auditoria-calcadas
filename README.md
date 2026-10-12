# ♿ Auditoria de Acessibilidade em Calçadas com Visão Computacional

**CPZÃO — Checkpoint Integrado** · Pipeline completo de Visão Computacional, da aquisição de
dados à inferência em tempo real na borda (*edge computing*).

Detecção de **barreiras de acessibilidade** em espaços públicos — degraus, escadas e
corrimãos — com **YOLOv8n**, exportado para **ONNX** e executado **diretamente no navegador
do celular** via ONNX Runtime Web (WebAssembly). Sem servidor, sem upload de imagem,
processamento 100% local.

---

## 👥 Integrantes do Grupo

| Nome completo | RM |
|:--|:--|
| Vinicius Sobreira Borges | RM97767 |
| Leticia Baptista | RM550289 |
| Julia Ortiz | RM550204 |
| Julia Palomari | RM551910 |

---

## 📌 O Problema

Calçadas em más condições são uma barreira concreta de mobilidade urbana. Para quem usa
cadeira de rodas, tem baixa visão ou empurra um carrinho de bebê, um degrau sem rampa, uma
escada sem corrimão ou uma guia alta deixa de ser um incômodo e vira um impedimento.

O gargalo não é saber que o problema existe — é **mapeá-lo em escala**. A
[auditoria de referência](https://falzoni.com.br/auditoriacalcadas/) cobriu 65 km de calçadas
e 578 travessias com observação de campo. São Paulo tem mais de 30 mil km de calçadas.

**A proposta:** transformar qualquer smartphone em instrumento de auditoria. O agente percorre
o trajeto, aponta a câmera traseira, e o modelo identifica as barreiras em tempo real. A
inferência roda na borda — no próprio aparelho — eliminando custo de servidor, funcionando
offline e sem transmitir imagens da via pública para lugar nenhum.

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

Três classes que cobrem o eixo central de uma auditoria de acessibilidade — **o desnível**
(a barreira) e **o apoio** (o recurso que a mitiga):

| id | classe | cor no app | o que é |
|:--:|:--|:--|:--|
| 0 | `degrau` | 🔴 vermelho | desnível isolado: guia de calçada, soleira, mudança de nível que funciona como passagem |
| 1 | `escada` | 🟡 amarelo | dois ou mais degraus em sequência — uma caixa para o conjunto |
| 2 | `corrimao` | 🟢 verde | apoio ou guarda-corpo de escada ou rampa |

**Por que estas três:** são as que têm anotação pública de qualidade disponível, são
visualmente distintas entre si (matriz de confusão limpa) e — decisivo para a apresentação —
**existem em qualquer prédio**. A demonstração ao vivo não depende de achar um buraco na rua
na hora certa: basta o corredor ou a escada da própria sala.

> A base original tem uma quarta label, `ramp`, **descartada de propósito**: 143 instâncias
> contra 3.564 de `step` (1:25). Com esse desbalanceamento a classe não aprende e ainda
> contamina a matriz de confusão das outras.

---

## 📊 Estatísticas do Dataset

| split | imagens | caixas | `degrau` | `escada` | `corrimao` |
|:--|--:|--:|--:|--:|--:|
| **train** | 420 | 949 | 308 | 324 | 317 |
| **valid** | 120 | 247 | 78 | 86 | 83 |
| **test** | 60 | 130 | 50 | 43 | 37 |
| **TOTAL** | **600** | **1326** | **436** | **453** | **437** |

- **Total de imagens:** 600 — **10× o mínimo exigido** (60)
- **Total de caixas:** 1.326 · média de 2,21 por imagem
- **Divisão:** 70/20/10 em train/valid/test
- **Balanceamento entre classes:** **0,96** (menor/maior) — praticamente perfeito
- **Imagens negativas (sem objeto):** 36 — ensinam o modelo a *não* detectar, reduzindo falso positivo
- **Validação estrutural das labels:** **0 problemas**
- **Resolução:** reduzida para 640 no maior lado, EXIF removido

| evidência | arquivo |
|:--|:--|
| anotações desenhadas sobre as imagens | [`docs/metricas/anotacoes_amostra.png`](docs/metricas/anotacoes_amostra.png) |
| estatísticas em JSON | [`docs/metricas/dataset_stats.json`](docs/metricas/dataset_stats.json) |

### Origem dos dados

**Image Dataset of Accessibility Barriers**
Stolberg, Jakob (2022) — *Alexander von Humboldt Institute for Internet and Society*
🔗 https://zenodo.org/records/6382090 · **Licença CC-BY-4.0**

5.538 fotos de espaços públicos anotadas com caixas delimitadoras em CVAT, acompanhadas de um
**protocolo de anotação documentado** — é essa documentação que sustenta a consistência da
rotulagem, em vez de critério improvisado.

> Quer reforçar a demonstração com fotos do próprio local? O guia opcional está em
> [`CAPTURA.md`](CAPTURA.md).

---

## 🎯 Métricas Alcançadas

> ⚠️ **PREENCHER** com a saída da célula 11 do notebook
> [`02_treino_export.ipynb`](notebooks/02_treino_export.ipynb) — ela gera este bloco pronto.

**Modelo:** YOLOv8n · `imgsz=192` · transfer learning dos pesos COCO

### Por classe (conjunto de **teste** — imagens nunca vistas pelo modelo)

| classe | Precision | Recall | mAP@50 | mAP@50-95 |
|:--|--:|--:|--:|--:|
| `degrau` | — | — | — | — |
| `escada` | — | — | — | — |
| `corrimao` | — | — | — | — |
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
┌──────────────────┐   ┌───────────────┐   ┌──────────────┐   ┌─────────────────┐
│  1. AQUISIÇÃO    │   │ 2. PREPARAÇÃO │   │  3. TREINO   │   │  4. DEPLOY      │
│                  │   │               │   │              │   │                 │
│  Zenodo 6382090  │──▶│ CVAT XML →    │──▶│  YOLOv8n     │──▶│  ONNX Runtime   │
│  CC-BY-4.0       │   │ YOLO · split  │   │  Colab (T4)  │   │  Web (WASM)     │
│  range requests  │   │ 70/20/10      │   │  imgsz=192   │   │  PWA no celular │
└──────────────────┘   └───────────────┘   └──────────────┘   └─────────────────┘
      notebook 01            notebook 01        notebook 02          app/
   scripts/zenodo_dataset.py
```

### Como o dataset é montado sem baixar 8 GB

O dataset original é um **zip único de 8 GB**. Baixá-lo inteiro para usar 600 imagens seria
desperdício. [`scripts/zenodo_dataset.py`](scripts/zenodo_dataset.py) resolve isso com
**range requests HTTP**:

1. Lê os últimos 128 KB do arquivo remoto para achar o **EOCD do zip** (formato zip64, já que
   passa de 4 GB) e descobrir onde fica o índice.
2. Baixa só o **diretório central** (517 KB) — o índice de todos os 5.540 membros.
3. Extrai apenas `wm_annotations.xml` (**192 KB** comprimido) e converte CVAT → YOLO.
4. Decide quais imagens interessam e **baixa somente essas**.

Resultado: **~650 MB em vez de 8 GB**, e o dataset fica pronto em ~6 minutos.

> Cada membro é extraído em **uma** requisição, não duas: o cabeçalho local e os dados vêm
> no mesmo range, com folga, e são fatiados depois. Duas requisições por imagem fariam a
> latência dominar o tempo total.

### A restrição que amarra todo o projeto

O app tem o tamanho de entrada **fixo em código** (`app/src/inference.js`, linhas 3–4):

```js
const INPUT_W = 192;
const INPUT_H = 192;
```

Portanto o modelo **precisa** ser treinado e exportado com `imgsz=192`. Um modelo em 640
carrega sem erro e desenha caixas em posições completamente erradas — é a falha mais
traiçoeira do pipeline, porque não lança exceção. A célula 9 do notebook 02 verifica isso
automaticamente, replicando em Python a função `detectOutputConventions()` do app.

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
├── CAPTURA.md                      ← opcional: ampliar com fotos próprias
├── notebooks/
│   ├── 01_dataset_prep.ipynb       ← monta o dataset do Zenodo, valida, divide
│   └── 02_treino_export.ipynb      ← treino, métricas, export ONNX, verificação
├── scripts/
│   ├── zenodo_dataset.py           ← range requests, CVAT→YOLO, seleção balanceada
│   └── preparar_fotos.sh           ← intake de fotos do celular (HEIC→JPG)
├── app/                            ← PWA de inferência (fork do yoloinferApp)
│   ├── index.html
│   ├── src/
│   │   ├── main.js                 ← CLASS_NAMES, cores, render, NMS
│   │   ├── inference.js            ← ONNX Runtime Web, pré/pós-processamento
│   │   └── style.css
│   └── public/
│       ├── models/calcadas.onnx    ← ⬅️ o modelo treinado vai AQUI
│       └── manifest.json           ← metadados do PWA
├── models/                         ← best.pt / best.onnx
├── dataset/
│   ├── data.yaml                   ← definição versionada das 3 classes
│   └── calcadas/                   ← dataset gerado (não versionado)
└── docs/metricas/                  ← gráficos, matriz de confusão, estatísticas
```

---

## 🚀 Como Executar

### Pré-requisitos

- **Node.js 18+** (`node --version`)
- Celular e computador **na mesma rede Wi-Fi**
- Conta no [Google Colab](https://colab.research.google.com) — GPU grátis

> Não é preciso conta no Roboflow nem no Zenodo. O dataset é público e baixado direto.

### Parte 1 — Dataset e Treino

1. Abra **[`notebooks/01_dataset_prep.ipynb`](notebooks/01_dataset_prep.ipynb)** no Colab
   (runtime **GPU**) e rode tudo. Em ~6 min você tem o dataset montado, validado e dividido.
   Nenhuma configuração é necessária.
2. Abra **[`notebooks/02_treino_export.ipynb`](notebooks/02_treino_export.ipynb)** e rode tudo.
   Treina, mostra as métricas e exporta o ONNX.
   **Não prossiga se a célula 9 mostrar algum ❌** — o modelo não funcionaria no celular.
3. Baixe os artefatos e distribua no repositório:

```bash
cd ~/Documents/cpzao-auditoria-calcadas
cp ~/Downloads/calcadas.onnx app/public/models/
cp ~/Downloads/best.pt       models/
cp ~/Downloads/*.png ~/Downloads/labels.jpg docs/metricas/
```

4. Cole o bloco de `metricas.md` na seção **Métricas Alcançadas** acima.

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

O certificado é autoassinado, então o navegador alerta:
**"Avançado" → "Prosseguir para 192.168.0.x (não seguro)"**.

> 🔒 **Por que HTTPS é obrigatório:** `getUserMedia()` — a API de câmera — só funciona em
> *secure context*. Em `http://` por IP o navegador **não** entrega a câmera. É por isso que
> o projeto usa o plugin `basicSsl` no modo dev.

#### Opção B — deploy público (recomendado para a apresentação)

Uma URL HTTPS real torna o app instalável como PWA e elimina o aviso de certificado — bem
mais confiável na frente da turma do que depender do Wi-Fi da sala.

```bash
cd app
npm run build
npx netlify-cli deploy --prod --dir=dist     # ou: npx vercel --prod
```

#### Instalar como aplicativo

- **Android / Chrome:** menu ⋮ → *Instalar aplicativo*
- **iOS / Safari:** Compartilhar → *Adicionar à Tela de Início*

Instalado, abre em tela cheia, sem barra de navegador, e funciona offline (service worker).

#### Usar

1. Toque em **📷 Start** e **permita o acesso à câmera**.
2. O app usa a **câmera traseira** automaticamente (`facingMode: 'environment'`).
3. Aponte para uma escada, um corrimão ou a guia da calçada.
4. **Confiança** e **Limiar IoU** são ajustáveis nos sliders.

---

## 🎛️ Ajuste Fino na Demonstração

| sintoma | causa provável | o que fazer |
|:--|:--|:--|
| não detecta nada | confiança alta demais | baixe **Confiança** para ~0.20 |
| caixas em todo lugar | confiança baixa demais | suba para ~0.45 |
| caixas duplicadas no mesmo objeto | NMS permissivo | baixe **IoU** para ~0.30 |
| caixas deslocadas / fora do objeto | **modelo não exportado em 192** | re-exporte com `imgsz=192` |
| travando, poucos FPS | modelo grande demais | confirme que é `yolov8n` (não `s`/`m`) |
| câmera não abre | contexto não seguro | use `https://` (Opção A ou B) |

> 💡 **Antes de apresentar:** veja a curva F1 × confiança gerada pelo notebook 02 e use o
> valor de pico como confiança inicial. É o limiar ótimo medido do *seu* modelo, não um
> palpite. O padrão do app é 0.35.

---

## ✅ Cobertura da Rubrica

| critério | pts | onde está |
|:--|:--:|:--|
| **Dataset & Rotulagem** — 60+ fotos, 3 classes, consistência, split correto | 4,0 | 600 imagens (10× o mínimo), balanceamento 0,96, 0 erros estruturais · [notebook 01](notebooks/01_dataset_prep.ipynb) célula 9 confere a rubrica automaticamente |
| **Treinamento & Métricas** — pipeline funcional, análise, export correto | 6,0 | [notebook 02](notebooks/02_treino_export.ipynb) · matriz de confusão, PR, F1, curvas · export ONNX verificado contra o app |
| **Deploy Mobile** — integração com o `yoloinferApp`, inferência fluida | 6,0 | [`app/`](app/) · câmera traseira em tempo real · PWA instalável |
| **Organização & GitHub** — repositório e documentação | 4,0 | este README · notebooks documentados · módulo reutilizável em `scripts/` |

---

## 🔧 Decisões Técnicas

**Por que YOLOv8n e não um modelo maior?**
A inferência roda sob WebAssembly, single-thread, na CPU do celular. O nano é o único tamanho
da família que mantém taxa de quadros utilizável nesse ambiente.

**Por que ONNX e não TFLite?**
Imposto pelo app base: o `yoloinferApp` é uma PWA que usa **ONNX Runtime Web**. TFLite exigiria
um app nativo Android (Kotlin + build). A PWA ainda roda em Android e iOS com o mesmo código.

**Por que o NMS fica fora do modelo?**
O app implementa NMS em JavaScript com limiares ajustáveis por slider em tempo real
(`setConf`/`setIou`). Embutir o NMS no grafo congelaria esses valores no export e mudaria o
shape da saída, quebrando o parser do app.

**Por que descartar caixas menores que 2 px?**
O treino roda em 192. Uma caixa com lado abaixo de `2/192` ocupa menos de dois pixels na
entrada da rede: o modelo não tem como aprendê-la, mas continua sendo penalizado por não
encontrá-la. Vira ruído puro na loss e derruba o recall medido. Isso atinge 5,5% das caixas
da base original — o filtro está em `LADO_MIN_NORM`, em `scripts/zenodo_dataset.py`.

**Por que remover o EXIF das imagens?**
São fotos de celular e podem trazer a tag de orientação. As anotações do CVAT foram feitas
sobre as dimensões **armazenadas** no arquivo (conferimos que `width`/`height` do XML batem
com o marcador SOF do JPEG), então qualquer rotação automática aplicada na leitura
desalinharia todas as caixas. Sem a tag, não há ambiguidade.

**Por que 6 workers no download e não 16?**
O Zenodo limita requisições por minuto. Com 16 workers, ~60% dos downloads voltaram
**HTTP 429**. Com 6 workers mais backoff exponencial, a perda cai para zero.

---

## 📚 Referências

- [Auditoria de Calçadas — Projeto e Metodologia](https://falzoni.com.br/auditoriacalcadas/) — fundamentação e metodologia de referência
- [Image Dataset of Accessibility Barriers](https://zenodo.org/records/6382090) — Stolberg, Jakob (2022), CC-BY-4.0 — **fonte dos dados**
- [yoloinferApp](https://github.com/Mjrovai/yoloinferApp) — app base de inferência mobile, por **Marcelo Rovai**
- [Ultralytics YOLOv8](https://docs.ultralytics.com/) · [ONNX Runtime Web](https://onnxruntime.ai/docs/tutorials/web/)

---

## 📄 Licença e Atribuição

**Dados:** derivados de *Image Dataset of Accessibility Barriers* por Jakob Stolberg
(Alexander von Humboldt Institute for Internet and Society), licenciado sob
[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/). As anotações originais em CVAT XML
foram convertidas para o formato YOLO e um subconjunto balanceado foi selecionado.

**Código do app:** derivado do [yoloinferApp](https://github.com/Mjrovai/yoloinferApp)
(ver [`app/LICENSE`](app/LICENSE)) — crédito a Marcelo Rovai.

Projeto desenvolvido para fins acadêmicos.
