# Exemplo real: Goalfy — "CRM para o vendedor brasileiro" (v2)

Primeira peça completa gerada com este fluxo (2026-08-11). Os arquivos
binários (imagens) ficam no projeto original, dentro do Masterplan:

```
Hapo Masterplan 2026/Goalfy/Criativos/crm-vendedor-brasileiro-v2/
```

Este exemplo documenta só os **comandos equivalentes** ao
`scripts/finalize_arte.py` generalizado deste repositório — os scripts
originais (`_finalize.py`, `_finalize_feed.py`, `_finalize_story.py`) eram
hardcoded (cópias quase idênticas, um arquivo por formato); aqui estão os
mesmos ajustes expressos como chamadas do script único e parametrizável.

Cor de marca corrigida: roxo oficial Goalfy `#7F23F7`.
Logo: `Goalfy/Logo PNG/goalfy-logo-original-transparente.png`.

## Peça FINAL (vertical, sem placeholder de logo pra apagar)

```bash
python ../../scripts/finalize_arte.py \
  --src chatgpt-v2.png \
  --out goalfy-crm-vendedor-brasileiro-v2-FINAL.png \
  --hue-alvo 3.9 --hue-faixa 245:285 --sat-add 0.026 --val-mult 1.035 \
  --logo "<Marca>/Logo PNG/goalfy-logo-original-transparente.png" \
  --logo-pos 0.06:0.012 --logo-largura-frac 0.14
```

(sem `--resize`: a peça FINAL manteve a resolução gerada pelo ChatGPT)

## Peça FEED (1080x1080, com placeholder de logo pra apagar antes)

```bash
python ../../scripts/finalize_arte.py \
  --src chatgpt-feed-v1.png \
  --out goalfy-crm-vendedor-brasileiro-v2-FEED.png \
  --hue-alvo 4.6 --hue-faixa 245:285 --sat-add -0.033 --val-mult 1.031 \
  --logo "<Marca>/Logo PNG/goalfy-logo-original-transparente.png" \
  --logo-pos 0.0481:0.0338 --logo-largura-frac 0.1204 \
  --apagar-placeholder 30:30:195:195 \
  --resize 1080:1080
```

Original usava posição/largura de logo em pixels fixos (`logo_x=52`,
`target_w=130`, sobre imagem ~1080px de largura antes do resize) — aqui
convertidos pra fração, que é o formato que o script generalizado espera.

## Peça STORY (1080x1920)

```bash
python ../../scripts/finalize_arte.py \
  --src chatgpt-story-v1.png \
  --out goalfy-crm-vendedor-brasileiro-v2-STORY.png \
  --hue-alvo 5.6 --hue-faixa 245:285 --sat-add 0.025 --val-mult 1.028 \
  --logo "<Marca>/Logo PNG/goalfy-logo-original-transparente.png" \
  --logo-pos 0.06:0.02 --logo-largura-frac 0.16 \
  --resize 1080:1920
```

## Validação

O script generalizado foi testado rodando o comando do FEED acima contra
o `chatgpt-feed-v1.png` original e comparando pixel a pixel com o
`goalfy-crm-vendedor-brasileiro-v2-FEED.png` já entregue: diferença média
de ~0.8 por canal (0-255), atribuível a arredondamento de fração→pixel na
borda do logo — visualmente idêntico.
