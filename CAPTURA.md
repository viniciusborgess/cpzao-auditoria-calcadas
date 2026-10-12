# Protocolo de Captura e Anotação

> ⏱️ **Tempo estimado:** ~40 min de captura + ~50 min de anotação.
> Faça nesta ordem. O resto do pipeline (treino, export, app) já está pronto e automatizado.

---

## 1. Captura das fotos

### Meta de volume

A rubrica exige **mínimo 60 imagens**. Capture **80–100** — sobra margem para descartar
fotos tremidas/escuras e ainda ficar acima do mínimo.

| classe | fotos-alvo | instâncias mínimas |
|:--|:--:|:--:|
| `buraco` — buraco, cratera, trinca profunda, piso quebrado/faltante | ~30 | 30 |
| `piso_tatil` — piso tátil direcional ou de alerta | ~30 | 30 |
| `obstaculo` — poste, lixeira, hidrante, bicicletário, mesa na calçada | ~30 | 30 |

Uma mesma foto pode conter **mais de uma classe** — isso é ótimo, aproveite
(ex.: poste plantado no meio do piso tátil é a foto perfeita, conta para duas classes).

### ⚠️ A regra que mais vale nota

**Fotografe no mesmo lugar e na mesma altura em que você vai demonstrar o app em aula.**

O modelo aprende o domínio que você mostrar para ele. Se as 80 fotos forem tiradas de pé,
celular na altura do peito, apontado ~45° para baixo na calçada — é **exatamente assim** que
ele vai funcionar na demo. Se você treinar com fotos de cima e demonstrar de longe, não detecta
nada na frente da turma, e a demo vale **6 dos 20 pontos**.

→ Escolha agora a rua da demonstração. Capture lá (e em 2–3 ruas parecidas).

### Protocolo

- **Câmera traseira**, foto normal, **sem zoom** (zoom digital degrada a imagem).
- Altura do peito/cintura, inclinada **30–50° para baixo**, enquadrando a calçada.
- Distância do alvo: **1 a 3 metros**. Varie dentro dessa faixa.
- O alvo deve ocupar entre ~10% e ~60% do quadro. Nem minúsculo, nem colado.

### Variedade (é isso que faz o mAP subir)

Não tire 30 fotos do mesmo buraco. Varie deliberadamente:

- ✅ **Ruas diferentes:** mínimo 3 quadras distintas.
- ✅ **Luz:** sol direto, sombra, nublado. Se der, algumas no fim da tarde.
- ✅ **Ângulo:** frontal, lateral, diagonal do mesmo tipo de alvo.
- ✅ **Piso:** concreto, ladrilho, asfalto, bloquete — fundos diferentes.
- ✅ **Contexto:** alguns quadros com pessoas/carros ao fundo (é o que a câmera vai ver).
- ❌ Evite: fotos tremidas, contraluz extremo, alvo cortado na borda, chão molhado refletindo.

### Transferir para o computador

Jogue tudo em `dataset/raw/`:

```bash
# AirDrop para ~/Downloads, depois:
mv ~/Downloads/IMG_*.{jpg,JPG,jpeg,HEIC,heic} dataset/raw/ 2>/dev/null

# iPhone salva em HEIC — o Roboflow não lê. Converta:
cd dataset/raw && for f in *.HEIC *.heic; do
  [ -e "$f" ] && sips -s format jpeg "$f" --out "${f%.*}.jpg" && rm "$f"
done

ls dataset/raw | wc -l    # confira: deve dar 80+
```

---

## 2. Anotação no Roboflow

Conta gratuita em [roboflow.com](https://roboflow.com) — o plano free cobre este projeto.

### 2.1 Criar o projeto

1. **Create New Project**
2. Project Type: **Object Detection**
3. Project Name: `auditoria-calcadas`
4. Annotation Group: `defeito-calcada`

### 2.2 Upload

Arraste a pasta `dataset/raw/` inteira → **Save and Continue**.

### 2.3 Anotar — as regras de consistência

Na rubrica, *"3 classes anotadas com **consistência**"* vale 4 pontos. Consistência significa
**decidir uma regra e não mudar no meio do caminho**. Use estas:

**Crie as 3 classes exatamente com estes nomes** (minúsculo, com underscore — o app depende disso):
`buraco` · `piso_tatil` · `obstaculo`

| regra | o que fazer |
|:--|:--|
| **Caixa justa** | Encoste a caixa na borda do objeto. Sem folga, sem cortar. |
| **Anote TODAS as instâncias** | 4 buracos na foto = 4 caixas. Objeto não anotado ensina o modelo que aquilo é fundo — é o erro que mais destrói o recall. |
| **`piso_tatil`: uma caixa por trecho contínuo** | A faixa inteira visível = 1 caixa. Não faça uma caixa por placa/ladrilho. Se a faixa for interrompida (por um poste, uma entrada de garagem), aí sim são 2 caixas. |
| **`buraco`: só o que é defeito real** | Buraco, cratera, trinca larga/profunda, pedaço de piso faltando. **Não** anote junta de dilatação, risco superficial ou mancha. |
| **`obstaculo`: só o que bloqueia a faixa livre** | Poste, lixeira, hidrante, bicicletário, mesa, placa **na calçada**. Poste atrás do muro ou na rua **não** conta. |
| **Oclusão** | Objeto 50%+ visível → anote a parte visível. Menos que isso → pule. |
| **Dúvida** | Se você hesitou 5 segundos, pule a instância. Anotação ambígua é pior que ausente. |

> 💡 Divida o trabalho no grupo, mas **anotem as 10 primeiras fotos juntos** para alinhar o
> critério. Cada integrante com uma régua diferente = matriz de confusão suja.

### 2.4 Gerar a versão

**Generate** → configure assim:

**Train/Test Split:** `70% train / 20% valid / 10% test`
*(a rubrica exige explicitamente os três splits — não deixe o test em 0%)*

**Preprocessing:**
- ✅ Auto-Orient *(corrige a rotação EXIF do celular — sem isso suas caixas saem tortas)*
- ✅ Resize → **Fit within** → `640 × 640` *(preserva a proporção; o treino reduz para 192 depois)*

**Augmentation** *(só no train — o Roboflow já cuida disso):*
- ✅ Flip: **Horizontal**
- ✅ Brightness: **±20%**
- ✅ Blur: até **1.5px**
- ✅ Rotation: **±10°**
- **Max version size: 3×** → 60 fotos de treino viram ~170. Com dataset pequeno, isso sozinho
  costuma render +5 a +15 pontos de mAP50.

→ **Create**

### 2.5 Exportar

Na versão criada: **Download Dataset** → Format: **YOLOv8** → **show download code**

Copie o snippet, que tem esta cara:

```python
rf.workspace("seu-workspace").project("auditoria-calcadas").version(1).download("yolov8")
```

➡️ **Cole isso no notebook [`notebooks/01_dataset_prep.ipynb`](notebooks/01_dataset_prep.ipynb), célula 3.**
Pegue também sua **API key** em Roboflow → Settings → API Keys.

---

## 3. Checklist antes de treinar

- [ ] 60+ imagens anotadas (de preferência 80+)
- [ ] 3 classes com os nomes exatos: `buraco`, `piso_tatil`, `obstaculo`
- [ ] 30+ instâncias de cada classe
- [ ] Split 70/20/10 com os três conjuntos preenchidos
- [ ] Auto-Orient ligado
- [ ] Fotos tiradas no local da demonstração
- [ ] Snippet de download + API key em mãos

Tudo marcado → abra o `01_dataset_prep.ipynb` no Colab.
