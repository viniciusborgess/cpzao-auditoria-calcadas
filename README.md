# ♿ Auditoria de Acessibilidade em Calçadas com Visão Computacional

**Checkpoint Integrado** · Pipeline completo de Visão Computacional, da aquisição de
dados à inferência em tempo real na borda (*edge computing*).

Detecção de **barreiras de acessibilidade** em espaços públicos — degraus, escadas e
corrimãos — com **YOLOv8n**, exportado para **ONNX** e executado **diretamente no navegador
do celular** via ONNX Runtime Web (WebAssembly). Sem servidor, sem upload de imagem,
processamento 100% local.

## 📱 App no ar

### 🔗 **[viniciusborgess.github.io/cpzao-auditoria-calcadas](https://viniciusborgess.github.io/cpzao-auditoria-calcadas/)**

Abra no celular (Chrome no Android ou Safari no iPhone), toque em **📷 Start**, permita a
câmera e aponte para uma escada. Não precisa instalar nada.

> 🖼️ **Sem uma escada por perto?** Use as
> **[imagens de teste](https://viniciusborgess.github.io/cpzao-auditoria-calcadas/amostras/)** —
> baixe uma e carregue no app pelo botão *📤 Imagem*. São fotos do conjunto de teste, que o
> modelo nunca viu no treino.

> 📖 **Vai apresentar?** O passo a passo está em **[`DEMO.md`](DEMO.md)** — instalação,
> ajuste dos limiares, solução de problemas e os pontos para falar.

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

**Modelo:** YOLOv8n · `imgsz=192` · 150 épocas · transfer learning dos pesos COCO

### Por classe (conjunto de **teste** — imagens nunca vistas pelo modelo)

| classe | Precision | Recall | mAP@50 | mAP@50-95 |
|:--|--:|--:|--:|--:|
| `degrau` | 0,449 | 0,100 | 0,088 | 0,030 |
| `escada` | 0,671 | 0,488 | **0,524** | 0,286 |
| `corrimao` | 0,529 | 0,108 | 0,119 | 0,039 |
| **geral** | **0,550** | **0,232** | **0,244** | **0,118** |

### Validação × Teste

| métrica | validação | teste |
|:--|--:|--:|
| mAP@50 | 0,328 | **0,244** |
| mAP@50-95 | 0,169 | **0,118** |
| Precision | 0,478 | **0,550** |
| Recall | 0,339 | **0,232** |

> As métricas de **teste** são as oficiais. O conjunto de validação guiou o *early stopping*,
> então seus números são otimistas por construção; o teste nunca influenciou nenhuma decisão.

### Modelo exportado

| item | valor |
|:--|:--|
| formato | ONNX opset 12, shape estático |
| entrada | `[1, 3, 192, 192]` |
| saída | `[1, 7, 756]` = `4 + 3 classes` × 756 âncoras |
| NMS | feito em JS pelo app (não embutido no grafo) |
| tamanho | 12,62 MB |
| latência (CPU) | **10,4 ms** (~96 FPS) |

---

## 📉 Análise Crítica dos Resultados

O mAP@50 geral ficou em **0,244**. O diagnóstico de *por quê* é mais informativo que o número.

### O desempenho não é uniforme — e o padrão revela a causa

| classe | Recall | mAP@50 | formato típico do objeto |
|:--|--:|--:|:--|
| `escada` | **0,49** | **0,524** | blob compacto, proporção equilibrada |
| `degrau` | 0,10 | 0,088 | faixa **longa e fina** (guia de calçada) |
| `corrimao` | 0,11 | 0,119 | barra **fina e diagonal** |

A única classe que funciona é a única com formato compacto. Isso aponta para uma causa
**geométrica**, não de quantidade ou qualidade dos dados.

### Três evidências que descartam as hipóteses óbvias

**1. Não é falha de reconhecimento.** A matriz de confusão tem diagonal ≈ 0,47 nas **três**
classes: quando o modelo detecta algo, classifica certo quase metade das vezes, de forma
uniforme.

**2. O modelo enxerga.** As predições no conjunto de teste estão visualmente corretas —
`escada 0,78`, `escada 0,81`, `corrimao 0,74`, `degrau 0,64`, todas sobre os objetos certos.
Ver [`docs/metricas/predicoes_teste.png`](docs/metricas/predicoes_teste.png).

**3. Não é overfitting nem falta de treino.** As curvas mostram train e val loss caindo
**juntas** até a época 150, com o mAP ainda subindo no fim. Ver
[`docs/metricas/curvas_treino.png`](docs/metricas/curvas_treino.png).

### A explicação: localização de objetos finos

O mAP@50 exige IoU ≥ 0,5 com o gabarito, e o IoU de uma caixa longa e fina é brutalmente
sensível ao erro na dimensão curta:

> Uma guia de calçada que ocupa **3% da altura** da imagem vira **≈ 6 pixels** numa entrada de
> 192. Um erro de 3 pixels na borda superior já corta o IoU pela metade — e a detecção,
> visualmente correta, é contabilizada como falha.

Para um blob como `escada`, o mesmo erro absoluto é irrelevante. Daí a diferença de ~5× no mAP
entre classes do mesmo dataset, com exatamente o mesmo treino.

### O que isso significa na prática

| uso | o resultado serve? |
|:--|:--|
| **Auditoria em campo** (contar e medir barreiras) | ❌ 0,244 é insuficiente — precisaria da próxima iteração |
| **Demonstração em tempo real** | ✅ o app precisa de *uma* caixa correta sobre o objeto apontado, não de recuperar todas as instâncias com IoU ≥ 0,5 |

### Próxima iteração — em ordem de impacto esperado

| mudança | de → para | porquê |
|:--|:--|:--|
| **`imgsz`** | 192 → **320** | ataca a causa raiz: o objeto fino ganha 1,7× mais pixels na dimensão crítica. Custo: 10 ms → ~29 ms (~34 FPS), ainda fluido |
| `degrees` | 5.0 → **0.0** | guia de calçada é horizontal por definição; rotacionar descaracteriza o alvo |
| `scale` | 0.5 → **0.3** | encolher a imagem faz o objeto fino desaparecer |
| `mosaic` | 0.5 → **0.3** | o mosaico reduz cada imagem; pesado demais para alvos finos |
| `epochs` | 150 → **250** | o mAP ainda subia, sem sinal de overfitting |

Nada disso exige mexer no app: ele detecta o tamanho de entrada do modelo sozinho. Basta
alterar `IMGSZ` na célula de configuração do notebook 02 e reexecutar.

> Uma alternativa estrutural seria **fundir `degrau` e `escada`**. A matriz de confusão mostra
> 0,28 + 0,19 de confusão cruzada entre as duas, o que faz sentido semântico — uma escada *é*
> uma sequência de degraus, e a fronteira entre "um degrau" e "dois degraus" é genuinamente
> ambígua. Mantivemos separadas porque a rubrica exige no mínimo 3 classes.

| evidência | arquivo |
|:--|:--|
| matriz de confusão normalizada | [`confusion_matrix_normalized.png`](docs/metricas/confusion_matrix_normalized.png) |
| matriz de confusão (contagens) | [`confusion_matrix.png`](docs/metricas/confusion_matrix.png) |
| perdas e métricas por época | [`curvas_treino.png`](docs/metricas/curvas_treino.png) |
| métricas do Ultralytics por época | [`results.png`](docs/metricas/results.png) |
| inferência no conjunto de teste | [`predicoes_teste.png`](docs/metricas/predicoes_teste.png) |
| distribuição das labels | [`labels.jpg`](docs/metricas/labels.jpg) |
| métricas em JSON | [`metricas.json`](docs/metricas/metricas.json) |

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

### Como o app descobre o tamanho de entrada do modelo

O `yoloinferApp` original traz o tamanho de entrada **fixo em código** (`INPUT_W = INPUT_H = 192`).
Isso cria a falha mais traiçoeira possível: um modelo exportado em outro tamanho **carrega sem
erro nenhum** e desenha caixas em posições aleatórias. Nada lança exceção — o app simplesmente
mente.

Nesta versão o tamanho é **detectado por sondagem**. O `onnxruntime-web` 1.18 expõe só
`inputNames`/`outputNames`, sem metadado de dimensões, então `detectInputSize()` tenta uma
inferência dummy em cada candidato — 192, 256, 320, 416, 640 — e fica com o primeiro que o
modelo aceitar. Um ONNX de shape estático rejeita qualquer outro tamanho:

```
sondando 192x192 ... ✅ ACEITO — saída [1,7,756]
sondando 256x256 ... ❌ rejeitado (Got invalid dimensions for input: images)
sondando 320x320 ... ❌ rejeitado
```

Com isso treino e app ficam **desacoplados**: dá para mudar o `imgsz` no notebook sem tocar
em uma linha do app. A célula 9 do notebook 02 ainda confere a compatibilidade antes do
deploy, replicando em Python a lógica de detecção do app.

### Contrato modelo ↔ app

| item | valor | verificado em |
|:--|:--|:--|
| formato | ONNX, opset 12, shape estático | notebook 02, célula 9 |
| entrada | quadrada, float32, RGB, `/255` — tamanho **detectado** pelo app | idem |
| saída | `[1, 7, N]` → `4 + 3 classes` × N âncoras | idem |
| NMS | **não** embutido no grafo — o app faz em JS | idem |
| coordenadas | pixel → app usa preprocess *letterbox* | idem |
| classes | 3, na mesma ordem do `data.yaml` | `app/src/main.js` |

> **De onde vem o N:** o YOLOv8 gera grids em 3 escalas (/8, /16, /32). Com entrada 192 →
> 24² + 12² + 6² = **756** âncoras; com 320 → 40² + 20² + 10² = **2100**.

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

Abra os notebooks **direto do GitHub no Colab** — assim você sempre roda a versão atual:

| notebook | abrir | o que faz |
|:--|:--|:--|
| **01 · Dataset** | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/viniciusborgess/cpzao-auditoria-calcadas/blob/main/notebooks/01_dataset_prep.ipynb) | monta, valida e divide o dataset (~6 min) |
| **02 · Treino** | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/viniciusborgess/cpzao-auditoria-calcadas/blob/main/notebooks/02_treino_export.ipynb) | treina, mede, exporta o ONNX (~20 min) |

> ⚠️ **Não baixe o `.ipynb` para rodar.** Um arquivo baixado congela a versão daquele momento;
> qualquer correção feita no repositório depois não chega até ele. Use os botões acima.

1. Rode o **notebook 01** com runtime **GPU** (`Ambiente de execução → Alterar tipo → T4`).
   Nenhuma configuração é necessária.
2. Rode o **notebook 02**. Ele é autossuficiente: como no Colab cada notebook abre um runtime
   separado, se o dataset não estiver presente ele o remonta sozinho.
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

#### Opção B — a versão publicada (é o que usamos na apresentação)

O app já está no ar em **https://viniciusborgess.github.io/cpzao-auditoria-calcadas/**,
servido pelo GitHub Pages a partir da branch `gh-pages`.

Uma URL HTTPS pública resolve três coisas de uma vez: funciona em qualquer celular sem
depender da máquina de ninguém, elimina o aviso de certificado autoassinado, e torna o app
instalável como PWA.

Para republicar depois de mudar o modelo ou o código:

```bash
cd app
npm run build
cd dist && touch .nojekyll && rm -rf .git && git init -q && git checkout -q -b gh-pages
git add -A && git commit -q -m "Deploy"
git push --force https://github.com/viniciusborgess/cpzao-auditoria-calcadas.git gh-pages
```

> O `vite.config.js` usa `base: './'` — todos os caminhos são relativos. Sem isso o app
> quebraria ao ser servido numa subpasta, que é como o GitHub Pages funciona.

> **Offline:** o service worker guarda o app e o modelo de 12 MB em cache na primeira visita.
> Depois disso ele abre e infere sem rede — essencial numa sala com Wi-Fi ruim.

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
| **Treinamento & Métricas** — pipeline funcional, análise, export correto | 6,0 | [notebook 02](notebooks/02_treino_export.ipynb) · matriz de confusão, PR, curvas · diagnóstico das classes fracas e segunda iteração em 320 · export ONNX verificado contra o app |
| **Deploy Mobile** — integração com o `yoloinferApp`, inferência fluida | 6,0 | [app publicado](https://viniciusborgess.github.io/cpzao-auditoria-calcadas/) · câmera traseira em tempo real · PWA instalável · offline via service worker · ~10 ms por inferência |
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
