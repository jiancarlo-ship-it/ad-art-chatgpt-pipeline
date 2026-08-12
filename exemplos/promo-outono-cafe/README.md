# Exemplo real: teste ponta a ponta com um usuário novo (marca fictícia)

Validação completa do sistema, do zero, simulando alguém clonando o
repositório pela primeira vez — marca fictícia "Café Nômade" (sem nenhuma
relação com um cliente real), rodada em 2026-08-12.

## O que foi feito

1. Clone limpo do repositório.
2. `config/minha-marca.json` preenchido com identidade fictícia (paleta
   marrom café `#8B4513`, logo circular de teste, tipografia Poppins).
3. `python scripts/novo_projeto.py --nome promo-outono --marca-config config/minha-marca.json --pasta-base projetos`
4. `projeto.json` preenchido (formato Feed, elemento central "xícara de
   café fumegante sobre mesa de madeira", headline "O outono pede uma
   pausa assim").
5. `python scripts/montar_prompt.py --projeto projetos/promo-outono` — gerou o prompt em parágrafo único.
6. Prompt colado de verdade no ChatGPT (via Claude in Chrome) — geração
   real, não simulada. Resultado: zero erro de texto, headline exata,
   espaço vazio reservado para o logo no canto superior esquerdo
   (conforme instruído no prompt), cena realista de cafeteria com luz
   natural e folhas de outono.
7. Imagem baixada em resolução total (1254x1254px) pelo botão "Baixar"
   do menu de compartilhamento.
8. `python scripts/finalize_arte.py --src ... --logo ... --resize 1080:1080`
   — **sem `--hue-alvo`**, ver "Achado" abaixo.

## Achado importante: correção de cor não se aplica a cena fotográfica

Esta peça é uma cena realista (ambiente, luz natural, sombra), diferente
do exemplo Goalfy (`exemplos/crm-vendedor-brasileiro-v2/`), que é um fundo
gráfico chapado. Ao amostrar um pixel do "fundo" desta peça, ele não é uma
cor sólida — é parede com sombra/luz variando, então o cálculo de HSV
correction (`hue_alvo`/`sat_add`/`val_mult`) deu um `val_mult` de ~2.28,
que estouraria o brilho da imagem inteira se aplicado. **Decisão: pular a
etapa de correção de cor inteiramente para peças fotográficas** — a cor da
marca já entra pelo hex exato no prompt (passo 5), e o resultado do
ChatGPT já ficou fiel o suficiente sem correção adicional. Rodar só logo +
resize.

Isso está documentado no README principal, seção "5. Calibre a cor da
marca" — a correção de cor HSV só faz sentido para fundos chapados/gráficos
(estilo UI mockup), não para cenas fotográficas.

## Achado secundário: cuidado no botão de download

O menu de compartilhamento do ChatGPT tem "Copiar link", "X", "LinkedIn",
"Reddit" e "Baixar" bem próximos uns dos outros. Um clique impreciso abriu
a tela de login do Reddit em vez de baixar a imagem. Sempre confirmar que
o clique caiu exatamente em "Baixar" antes de seguir.

## Resultado

Pipeline mecânico completo, validado com geração real (não simulada):
`novo_projeto.py` → `montar_prompt.py` → ChatGPT real (via Claude in
Chrome) → `finalize_arte.py` (logo + resize) → peça final coerente, texto
correto, logo posicionado no espaço reservado.
