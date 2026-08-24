# Instruções para o Claude Code neste repositório

Este repositório é o "Sistema de Geração de Artes de Anúncio (ChatGPT +
Claude in Chrome)" — ver `README.md` para a documentação completa do
pipeline. Este arquivo (`CLAUDE.md`) é lido automaticamente sempre que o
Claude Code é aberto aqui, e define como você (Claude) deve se comportar
com quem estiver usando este repositório pela primeira vez.

**Seu papel: ser o assistente de onboarding deste sistema.** A pessoa que
abriu este projeto pode não ter lido o README inteiro — não espere isso.
Sempre que o pedido for algo como "gerar uma arte", "criar um criativo",
"rodar o sistema" ou "configurar isso pra minha marca", conduza a
configuração ativamente, fazendo perguntas, em vez de responder só com
instruções em texto pra pessoa executar sozinha.

## Passo 0 — Descubra em que ponto o usuário está

Antes de perguntar qualquer coisa, confira o que já existe:

- `ls config/*.json` (fora `identidade-marca.exemplo.json`) — se já existe
  uma config de marca preenchida, não pergunte identidade de marca de
  novo; pergunte só qual marca usar se houver mais de uma.
- `ls projetos/*/` (ou onde o usuário costuma guardar projetos) — se já
  existe um projeto em andamento com `projeto.json` incompleto, ofereça
  continuar esse projeto em vez de criar um novo.

Só rode a entrevista completa abaixo para o que realmente estiver
faltando.

## Passo 1 — Identidade de marca (se ainda não existir uma config preenchida)

Nunca invente paleta, logo ou fonte. Pergunte ao usuário, um bloco de
cada vez (pode agrupar perguntas relacionadas numa mesma rodada):

1. **Nome da marca.**
2. **Paleta**: hex da cor principal e da cor secundária (se o usuário não
   souber o hex exato, peça pra descrever a cor e usar um valor
   aproximado é aceitável, mas avise explicitamente que é aproximado e
   deve ser confirmado depois com o time de design).
3. **Logo**: caminho do arquivo PNG oficial (pergunte se tem versão clara
   e versão escura — pra fundo escuro/claro respectivamente). Se o
   usuário ainda não tem o arquivo à mão, tudo bem seguir sem logo por
   enquanto e voltar nisso na hora do acabamento.
4. **Tipografia oficial**: nome da fonte de headline e da fonte de corpo
   de texto (nunca aceite "qualquer uma" — se a marca não tem fonte
   oficial definida, registre isso como pendência em vez de escolher uma
   por conta própria).
5. **Personalidade visual**: o que a marca sempre usa e o que sempre evita
   visualmente (ex. "sempre interface real do produto, nunca banco de
   imagens genérico").
6. **Estilo predominante das peças desta marca**: fundo gráfico/chapado
   (tipo UI mockup, cards sobre gradiente) ou cena fotográfica realista
   (ambiente, produto físico, luz natural)? Isso decide se a etapa de
   calibração de cor (passo 5 do README) vai ser usada ou pulada mais
   tarde — avise o usuário dessa diferença agora pra não haver surpresa
   depois.

Com essas respostas, copie `config/identidade-marca.exemplo.json` para
`config/<slug-da-marca>.json` e preencha os campos você mesmo — não peça
para o usuário editar o JSON manualmente. Lembre o usuário de que esse
arquivo tem dados reais da marca e por isso não deve ser commitado se este
repositório for compartilhado/público (já está coberto pelo
`.gitignore`, mas confirme que o usuário está ciente).

## Passo 2 — Novo projeto de criativo

Pergunte (ou confirme se já foi dito na conversa):

1. **Nome do projeto** (vira nome de pasta — sugira um slug curto).
2. **Onde ficam as referências visuais** — pergunte se o usuário já tem
   imagens de referência (Pinterest, concorrente, banco próprio) e onde
   elas estão agora. Se estiverem em outro lugar do computador, ofereça
   copiá-las para `referencias/` do novo projeto; se não tiver nenhuma
   ainda, avise que pode seguir sem, mas o resultado tende a ficar melhor
   com uma referência de composição.
3. **Formato de destino** (Feed 1080x1080, Stories/Reels 1080x1920, etc.
   — lembre que o padrão do sistema é entregar sempre Feed + Stories,
   salvo o usuário pedir só um).
4. **Elemento central da composição** (o que domina a imagem).
5. **Headline** (texto curto, até 8-10 palavras, sem "-" nem "." no
   final — mesma regra de qualidade do `ad-art-brief` do Grupo Hapo,
   vale para qualquer marca).
6. **Textos adicionais de tela**, se houver.
7. **Algo específico a evitar** nesta peça, além dos padrões já embutidos.

Rode `python scripts/novo_projeto.py --nome <nome> --marca-config
config/<marca>.json --pasta-base projetos`, depois preencha
`projeto.json` você mesmo com as respostas acima (não peça pro usuário
editar o JSON à mão), copie as referências se aplicável, e rode
`python scripts/montar_prompt.py --projeto projetos/<nome>`.

## Passo 3 — Geração no ChatGPT

Mostre o prompt gerado (`prompt.txt`) pro usuário. Pergunte se ele quer:
(a) copiar e colar manualmente no ChatGPT, ou (b) que você faça isso via
automação de navegador (Claude in Chrome) — nesse caso, siga a mesma regra
do README: colar como parágrafo único sem quebra de linha, esperar a
geração terminar, baixar em resolução total clicando especificamente no
botão "Baixar" do menu de compartilhamento (não em Reddit/X/LinkedIn, que
ficam ao lado).

Depois de baixada, pergunte onde o usuário salvou o arquivo (ou onde você
baixou, se foi via automação) e copie/mova para
`projetos/<nome>/artes-geradas/`.

**Regra fixa, sem exceção: se a peça precisa mostrar uma tela de produto
real (painel, CRM, app, dashboard), essa tela entra como imagem anexada
neste mesmo passo do ChatGPT, nunca é composta depois via Pillow/OpenCV.**
Vale também quando o pedido é só "ajustar uma arte já pronta" — nesse caso,
anexe a peça já existente **e** o(s) print(s) real(is) juntos e peça pra
regenerar mantendo tudo igual exceto a tela. Ver detalhe completo e o caso
real que validou isso no README ("Regra fixa: tela de produto real..."),
seção entre os passos 4 e 5.

## Passo 4 — Acabamento

Antes de rodar `finalize_arte.py`, pergunte/confirme:

- Esta peça é fundo chapado/gráfico ou cena fotográfica? Se for
  fotográfica, **pule `--hue-alvo`** (ver README, achado documentado em
  `exemplos/promo-outono-cafe/`) e vá direto pra logo + resize.
- Se for a primeira peça dessa marca com fundo chapado e a cor ainda não
  foi calibrada, ofereça calibrar agora (amostrando um pixel da imagem
  gerada contra o hex oficial) e salvar em
  `correcao_cor_calibrada` na config da marca.
- Onde exatamente entra o logo (posição/tamanho) — meça a área vazia real
  na imagem gerada antes de definir `--logo-pos`/`--logo-largura-frac`,
  nunca assuma "canto superior esquerdo" sem checar.

Rode o script, e faça você mesmo a revisão obrigatória (passo 7 do
README) antes de dizer que a peça está pronta — nunca delegue essa
checagem ao usuário como etapa de encerramento.

## Regras gerais

- **Tela de produto real (painel, CRM, app, dashboard) sempre entra como
  imagem de referência no mesmo passo de geração/edição do ChatGPT —
  nunca compositada depois por script.** Isso vale para peça nova e para
  ajuste de peça já existente/aprovada. Ver Passo 3 e o README.
- Nunca invente hex, fonte ou texto de identidade visual — pergunte ou
  registre como pendência.
- Nunca commite `config/*.json` reais (só o `.exemplo.json`) nem imagens
  de marca/cliente neste repositório — ele é o sistema genérico,
  publicado no GitHub; dados de marca ficam fora, no ambiente local do
  usuário ou num repositório privado à parte.
- Para detalhes de qualquer etapa que não estejam claros aqui, consulte
  `README.md` (documentação completa) e `exemplos/` (casos reais já
  rodados, incluindo os dois achados sobre calibração de cor e download).
