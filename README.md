# Sistema de Geração de Artes de Anúncio (ChatGPT + Claude in Chrome)

Pipeline que produziu o **melhor resultado até agora** entre as vias de
geração de arte testadas para criativos de anúncio (validado 2026-08-11,
peça "CRM para o vendedor brasileiro" — duas peças completas, zero erro de
texto). A ideia central: **deixar a IA generativa fazer só o que ela faz
bem (cena, composição, texto renderizado)** e **nunca confiar nela** para
os dois elementos que precisam estar 100% corretos — a cor exata da marca
e o logo oficial — que entram depois por código, determinístico.

Este é um **sistema genérico**, sem identidade de marca embutida. Antes de
gerar qualquer arte, cada usuário cria a própria config de marca e a
própria pasta de referências (ver "Setup" abaixo) — nada aqui é específico
de nenhuma marca ou cliente.

## Por que este pipeline existe

Testamos três abordagens diferentes pra gerar arte de anúncio:

1. **API `gpt-image-1` direta** (`images.generate`, prompt longo
   redescrevendo a cena do zero) — sempre saiu com texto bugado ou logo
   redesenhado errado, mesmo depois de várias rodadas de prompt.
2. **Template HTML/CSS + Playwright** — zero bug de texto/logo (não
   depende de IA pra nada renderizado), mas exige montar a composição
   manualmente em CSS; ótimo quando não existe uma referência forte pra
   editar, mas menos flexível pra cenas realistas complexas.
3. **ChatGPT via navegador** (interface do produto, não a API crua) — o
   produto ChatGPT aplica algum tipo de correção/revisão interna que a
   chamada de API pura não tem (foi observado se autocorrigindo sozinho
   no meio da geração). Resultado sensivelmente mais confiável em texto
   do que a via 1, sem o trabalho manual da via 2.

Este repositório documenta e generaliza a via 3, complementada pelo
acabamento determinístico que qualquer uma das três vias precisa de
qualquer forma (cor de marca exata + logo real).

## Estrutura do repositório

```
config/
  identidade-marca.exemplo.json   <- modelo; copie e preencha, nunca edite o .exemplo
scripts/
  novo_projeto.py                  <- cria a pasta de um novo projeto de criativo
  montar_prompt.py                 <- monta o prompt (marca + projeto) pronto pro ChatGPT
  finalize_arte.py                 <- acabamento: cor de marca + logo real + resize
exemplos/
  crm-vendedor-brasileiro-v2/      <- exemplo real de uso (comandos, não arquivos de marca)
```

`config/` e as pastas de projeto (`referencias/`, `artes-geradas/`,
`projeto.json`, `prompt.txt`) com dados reais de marca/cliente **não
pertencem a este repositório** — cada usuário mantém as suas fora daqui,
ou num repositório privado próprio (ver `.gitignore`).

## Setup (uma vez por marca)

### 1. Crie sua config de identidade de marca

```bash
cp config/identidade-marca.exemplo.json config/minha-marca.json
```

Preencha `config/minha-marca.json` com a paleta (hex), caminhos dos PNGs
do logo (versão clara e escura), tipografia oficial e personalidade
visual da marca. Deixe `correcao_cor_calibrada.hue_alvo` como `null` por
enquanto — isso é calibrado depois de ver a primeira imagem gerada (passo
5 abaixo).

**Importante:** os caminhos de `logo.versao_clara_png` /
`versao_escura_png` são relativos à **pasta onde o arquivo de config está
salvo** (`config/`), não à raiz do repositório nem à pasta do projeto. Ex.:
se o logo está em `assets/logo/marca.png` na raiz do repo, o caminho no
JSON é `../assets/logo/marca.png`. Se o caminho estiver errado,
`finalize_arte.py` avisa exatamente qual arquivo procurou e onde.

Nunca invente hex/fonte se a marca ainda não tiver isso definido
oficialmente — deixe o campo como está e trate como pendência.

### 2. Instale as dependências

```bash
pip install Pillow
```

Nenhuma chave de API é necessária — a geração de imagem acontece na
interface do ChatGPT (manual ou via automação de navegador), não pela
API. O acabamento é só Pillow, local.

## Uso (por projeto/peça)

### 1. Crie a estrutura do projeto

```bash
python scripts/novo_projeto.py \
  --nome lancamento-produto-x \
  --marca-config config/minha-marca.json \
  --pasta-base projetos
```

Isso cria `projetos/lancamento-produto-x/` com `referencias/`,
`artes-geradas/` e um `projeto.json` a preencher.

### 2. Coloque as referências visuais

Cole em `referencias/` os prints/imagens (Pinterest, concorrente, banco de
referências próprio) que servem de **inspiração de composição** — nunca
copie marca/logo/cor de uma referência de outra empresa, só a forma como
ela organiza o espaço.

### 3. Preencha `projeto.json`

Formato de destino, o que da referência deve ser mantido, elemento
central da composição, headline, textos de tela adicionais.

### 4. Monte o prompt e gere a imagem no ChatGPT

```bash
python scripts/montar_prompt.py --projeto projetos/lancamento-produto-x
```

Isso escreve `prompt.txt` — **um parágrafo único, sem quebra de linha**
(quebras de linha no meio do texto disparam o envio prematuro da mensagem
no editor do ChatGPT, bug observado repetidas vezes nesse fluxo). Copie o
conteúdo, abra o ChatGPT (manualmente ou via Claude in Chrome), anexe a(s)
referência(s) e cole o prompt.

Passos manuais no ChatGPT:

1. Espere terminar (pode levar 1-3 min; o "Pensando" às vezes já inclui
   uma auto-correção espontânea antes da primeira entrega).
2. **Baixe a imagem em resolução total** (botão de download no editor, não
   confie no preview reduzido do chat) — erros de ortografia pequenos só
   aparecem nítidos em resolução real.
3. Salve o arquivo em `artes-geradas/`, com um nome que identifique a
   versão (ex. `chatgpt-feed-v1.png`).
4. Se precisar de ajuste pontual (texto duplicado, elemento grande
   demais), volte na mesma conversa e descreva só a mudança pontual — o
   histórico mantém a composição e o ChatGPT edita só o que foi pedido.

### 5. Calibre a cor da marca (só na primeira peça de uma marca nova)

Abra a imagem baixada, amostre um pixel na área que deveria ser a cor da
marca (ex. um pixel do fundo). Converta esse RGB e o hex oficial pra HSV
(`colorsys.rgb_to_hsv`) e calcule:

- `hue_alvo`: diferença de matiz em graus entre o pixel gerado e o hex oficial;
- `hue_faixa`: faixa de matiz (graus) que cobre a cor a corrigir (ex. `[245, 285]` pra tons de roxo);
- `sat_add` / `val_mult`: ajuste de saturação/brilho pra bater exatamente com o hex.

Salve esses valores em `correcao_cor_calibrada` dentro de
`config/minha-marca.json` — as próximas peças dessa marca reaproveitam a
calibração automaticamente.

### 6. Rode o acabamento

```bash
python scripts/finalize_arte.py \
  --src projetos/lancamento-produto-x/artes-geradas/chatgpt-feed-v1.png \
  --out projetos/lancamento-produto-x/artes-geradas/lancamento-produto-x-FEED.png \
  --marca-config config/minha-marca.json \
  --logo-pos 0.06:0.02 --logo-largura-frac 0.14 \
  --resize 1080:1080
```

Com `--marca-config`, o script usa automaticamente a cor calibrada e o
logo (`versao_clara_png` por padrão; use `--logo-versao escura` se o fundo
da peça for claro). Qualquer flag passada explicitamente (`--hue-alvo`,
`--logo` etc.) tem prioridade sobre o valor da config, pra ajuste pontual
sem editar o JSON.

**Como calibrar a posição do logo:** meça a faixa vazia real na imagem
gerada (nunca assuma "canto superior esquerdo" — depende de onde a
composição começa em cada peça/formato) antes de definir
`--logo-pos`/`--logo-largura-frac`. Se o ChatGPT desenhou um
placeholder/rabisco no lugar do logo, use `--apagar-placeholder
x0:y0:x1:y1` pra apagá-lo (preenchido com a cor de fundo local) antes de
colar o logo real.

Rode `python scripts/finalize_arte.py --help` para ver todos os
parâmetros.

### 7. Revisão obrigatória antes de considerar pronto

Sempre conferir manualmente:

- todo texto legível, letra por letra (headline, subheadline, CTA, labels
  de card, texto de interface simulada) — qualquer erro ortográfico ou
  glifo estranho é falha automática, mesmo em texto "decorativo";
- logo é o arquivo oficial, não redesenhado pela IA;
- nenhuma sobreposição geométrica entre logo e outro elemento (headline,
  CTA, foto);
- se a peça usa screenshot real de produto, todo dado sensível (nome,
  telefone, foto de cliente real) foi anonimizado antes de publicar
  (fora do escopo deste repositório por enquanto — ver "Status" abaixo).

## Exemplo real

Ver `exemplos/crm-vendedor-brasileiro-v2/README.md` — os comandos reais
(sem os arquivos de marca/imagem, que não pertencem a este repositório)
usados na primeira peça validada com este fluxo.

## Status / próximos passos

- [ ] Automatizar o passo de submissão do prompt e download da imagem via
      Claude in Chrome, hoje feito manualmente ou semi-manualmente.
- [ ] Modo de calibração automática de cor (amostrar pixel de entrada e
      hex de destino, calcular `hue_alvo`/`sat_add`/`val_mult` sozinho).
- [ ] Script de anonimização de screenshot (nome/telefone/foto fictícios),
      hoje só documentado como regra manual.
- [ ] Checklist de revisão automatizável (hoje é uma lista manual neste
      README).
