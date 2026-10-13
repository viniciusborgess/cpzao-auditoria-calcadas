# 📱 Guia da Demonstração

> Para quem vai apresentar em aula. **Não precisa de computador, nem do repositório, nem de
> instalar nada.** Só do celular.

---

## 🔗 O link

# [viniciusborgess.github.io/cpzao-auditoria-calcadas](https://viniciusborgess.github.io/cpzao-auditoria-calcadas/)

Abra no **Chrome (Android)** ou **Safari (iPhone)**. Funciona em qualquer celular, em qualquer
rede.

---

## ⚠️ Faça isto ANTES de sair de casa

**Abra o link uma vez no Wi-Fi.** O app baixa um modelo de 12 MB na primeira vez e guarda em
cache. Depois disso ele abre e funciona **mesmo sem internet** — o que salva a apresentação se
o Wi-Fi da sala estiver ruim ou o 4G não pegar.

1. Abra o link
2. Espere aparecer o botão **📷 Start** (alguns segundos na primeira vez)
3. Toque em **📷 Start** e **permita o acesso à câmera**
4. Aponte para uma escada e confirme que aparece a caixa amarela

Se isso funcionou em casa, vai funcionar na aula.

---

## 📲 Instalar como aplicativo (opcional, mas fica melhor)

Instalado, abre em tela cheia, sem a barra do navegador — parece um app de verdade.

| celular | como |
|:--|:--|
| **Android / Chrome** | menu **⋮** → *Instalar aplicativo* (ou *Adicionar à tela inicial*) |
| **iPhone / Safari** | botão **Compartilhar** ⬆️ → *Adicionar à Tela de Início* |

---

## ▶️ Como usar

1. Toque em **📷 Start**
2. **Permita** o acesso à câmera quando o navegador perguntar
3. Aponte a **câmera traseira** para o objeto
4. As caixas aparecem em tempo real, com a classe e a confiança

### O que apontar

| classe | cor | onde achar no prédio |
|:--|:--|:--|
| **Escada** | 🟡 amarelo | qualquer escada — **é a classe que funciona melhor, comece por ela** |
| **Corrimão** | 🟢 verde | corrimão da escada, guarda-corpo da rampa |
| **Degrau** | 🔴 vermelho | guia da calçada na entrada, soleira de porta, degrau isolado |

> 💡 **Melhor enquadramento:** fique a **2–3 metros** do objeto, celular na altura do peito,
> inclinado para baixo. Escada inteira no quadro funciona melhor que close-up.
>
> 💡 **A melhor tomada:** uma escada **com corrimão** — detecta duas classes ao mesmo tempo,
> e fica bonito na demonstração.

---

## 🎛️ Se não detectar

Tem dois controles deslizantes embaixo da tela. Ajuste **ao vivo**, não precisa recarregar:

| situação | o que fazer |
|:--|:--|
| **Não aparece nenhuma caixa** | arraste **Confiança** para baixo, até ~**0.20** |
| **Caixas demais / em coisa errada** | arraste **Confiança** para cima, até ~**0.45** |
| **Duas caixas no mesmo objeto** | arraste **Limiar IoU** para baixo, até ~**0.30** |

> O padrão é 0.35. Se tiver pouco tempo, **comece em 0.25** — detecta mais, e é melhor mostrar
> algo do que não mostrar nada.

---

## 🆘 Problemas

| problema | solução |
|:--|:--|
| A câmera não abre | O navegador bloqueou. Vá em Configurações do site → Permissões → Câmera → Permitir. Depois recarregue. |
| Travou na tela de carregando | Primeira vez baixa 12 MB. Espere. Se passar de 1 min, recarregue. |
| Abriu a câmera frontal | Feche e abra de novo. O app pede a traseira por padrão. |
| Está lento / travando | Feche os outros apps. O processamento é todo no celular. |
| Não detecta nada mesmo com confiança baixa | Afaste-se um pouco e enquadre o objeto inteiro. Tente uma escada — é a classe mais forte. |
| Nada funciona | Abra pelo Chrome (Android) ou Safari (iPhone). Outros navegadores podem não dar acesso à câmera. |

---

## 🗣️ O que falar na apresentação

Caso perguntem — os pontos que mostram que o trabalho foi entendido, não só executado:

**O que é**
> Auditoria de acessibilidade urbana. O modelo detecta três barreiras — degrau, escada e
> corrimão — e roda **inteiramente dentro do celular**.

**Por que roda na borda e não num servidor**
> Não há upload de imagem, funciona offline, custo zero por inferência, e nenhuma foto da via
> pública sai do aparelho. A inferência leva ~10 ms.

**Como funciona por dentro**
> YOLOv8n treinado em 600 imagens de uma base pública licenciada (CC-BY), exportado para ONNX
> e executado no navegador com ONNX Runtime Web compilado para WebAssembly. É uma PWA, então
> o mesmo código roda em Android e iPhone.

**Se perguntarem sobre as métricas** — responda com honestidade, está tudo documentado:
> O mAP@50 geral ficou em 0,244, mas o número isolado engana. `escada` chega a 0,52 enquanto
> `degrau` fica em 0,088 — e a causa é geométrica, não de dados. Guia de calçada é uma caixa
> longa e fina: numa entrada de 192 pixels ela ocupa ~6 pixels de altura, e errar 3 pixels já
> derruba o IoU abaixo de 0,5. A detecção fica visualmente certa mas conta como erro. A
> matriz de confusão confirma: a diagonal é ~0,47 nas três classes, ou seja, o
> reconhecimento não é o gargalo — a localização é. No README tem a análise completa e o que
> mudaríamos na próxima iteração.

**Se perguntarem por que não usaram fotos próprias**
> A base pública tem protocolo de anotação documentado e revisado, o que dá consistência de
> rotulagem melhor do que conseguiríamos anotando à mão em um dia. E as classes escolhidas
> existem em qualquer prédio, o que torna a demonstração reproduzível.

---

## 👥 Grupo

| Nome | RM |
|:--|:--|
| Vinicius Sobreira Borges | RM97767 |
| Leticia Baptista | RM550289 |
| Julia Ortiz | RM550204 |
| Julia Palomari | RM551910 |

📂 Repositório: https://github.com/viniciusborgess/cpzao-auditoria-calcadas
