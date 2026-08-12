"""
finalize_arte.py — acabamento determinístico de uma arte gerada no ChatGPT.

Faz os dois ajustes que a IA de imagem nunca acerta de forma confiável:
  1. Corrige matiz/saturação/brilho de uma faixa de cor pra bater com o hex
     oficial exato da marca (a IA sempre entrega uma variação aproximada).
  2. Substitui a área do logo (redesenhado/placeholder) pelo PNG oficial
     real, via alpha_composite — nunca confia na IA para o logo.

Generalizado a partir de 3 scripts quase idênticos usados no projeto
Goalfy "crm-vendedor-brasileiro-v2" (2026-08-11), um por formato
(FEED/STORY/FINAL). Ver README.md deste repositório para o fluxo completo.

Uso básico (tudo via flags):

    python finalize_arte.py \
      --src chatgpt-v1.png \
      --out projeto-FEED.png \
      --logo "caminho/para/logo-oficial.png" \
      --hue-alvo 4.6 --hue-faixa 245:285 --sat-add -0.033 --val-mult 1.031 \
      --logo-pos 0.06:0.02 --logo-largura-frac 0.14 \
      --resize 1080:1080

Uso com config de marca (recomendado depois da primeira calibração — ver
config/identidade-marca.exemplo.json e README.md):

    python finalize_arte.py \
      --src chatgpt-v1.png \
      --out projeto-FEED.png \
      --marca-config config/minha-marca.json \
      --resize 1080:1080

Com --marca-config, o script usa automaticamente `correcao_cor_calibrada`
(hue_alvo/hue_faixa/sat_add/val_mult) e `logo.versao_clara_png` (ou
`--logo-versao escura` para `versao_escura_png`) definidos na config. Toda
flag passada explicitamente na linha de comando tem prioridade sobre o
valor da config — use isso para ajustar pontualmente sem editar o JSON.

Todos os parâmetros de cor/logo são opcionais — se omitidos (e sem
--marca-config), o script só faz o resize (ou nem isso, se --resize também
for omitido).
"""

import argparse
import colorsys
import json
import os

from PIL import Image, ImageDraw


def parse_par(valor, nome):
    """Converte 'a:b' em (float(a), float(b))."""
    try:
        a, b = valor.split(":")
        return float(a), float(b)
    except Exception as exc:
        raise argparse.ArgumentTypeError(
            f"--{nome} precisa estar no formato 'a:b' (recebido: {valor!r})"
        ) from exc


def corrigir_cor(im, hue_faixa, hue_shift_graus, sat_add, val_mult, sat_min=0.3, val_min=0.3):
    """Ajusta HSV pixel a pixel só nos pixels dentro da faixa de matiz.

    hue_faixa: (min_graus, max_graus) — ex. (245, 285) pra tons de roxo.
    hue_shift_graus: deslocamento de matiz a aplicar (pode ser negativo).
    sat_add / val_mult: ajuste aditivo de saturação e multiplicativo de
    brilho, calibrados comparando um pixel da arte gerada com o hex oficial.
    """
    px = im.load()
    w, h = im.size
    hue_shift = hue_shift_graus / 360.0
    hmin, hmax = hue_faixa

    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            hh, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            hue_deg = hh * 360
            if hmin <= hue_deg <= hmax and s > sat_min and v > val_min:
                new_h = (hh + hue_shift) % 1.0
                new_s = max(0.0, min(1.0, s + sat_add))
                new_v = min(1.0, v * val_mult)
                nr, ng, nb = colorsys.hsv_to_rgb(new_h, new_s, new_v)
                px[x, y] = (round(nr * 255), round(ng * 255), round(nb * 255))
    return im


def compositar_logo(im, logo_path, pos_frac, largura_frac, apagar_placeholder=None):
    """Cola o PNG oficial do logo por cima da arte.

    pos_frac: (x_frac, y_frac) — posição do canto superior esquerdo do logo,
    como fração da largura/altura da imagem final (ex. 0.06, 0.02).
    largura_frac: largura do logo como fração da largura da imagem.
    apagar_placeholder: bounding box opcional (x0, y0, x1, y1) em pixels pra
    preencher com a cor de fundo local ANTES de colar o logo — use quando o
    ChatGPT desenhou um placeholder/rabisco no lugar do logo.
    """
    im = im.convert("RGBA")
    w, h = im.size

    if apagar_placeholder is not None:
        px = im.load()
        bg = px[10, 10][:3]  # amostra um pixel de canto, fundo limpo
        draw = ImageDraw.Draw(im)
        draw.rectangle(apagar_placeholder, fill=bg)

    logo = Image.open(logo_path).convert("RGBA")
    target_w = int(w * largura_frac)
    target_h = int(target_w * logo.height / logo.width)
    logo = logo.resize((target_w, target_h), Image.LANCZOS)

    x_frac, y_frac = pos_frac
    logo_x, logo_y = int(w * x_frac), int(h * y_frac)
    im.alpha_composite(logo, (logo_x, logo_y))

    print(f"logo colado em: {(logo_x, logo_y, logo_x + target_w, logo_y + target_h)}")
    return im


def carregar_marca_config(caminho):
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", required=True, help="arte gerada no ChatGPT (PNG)")
    ap.add_argument("--out", required=True, help="caminho de saída")

    ap.add_argument("--marca-config", default=None,
                     help="JSON de identidade de marca (ver config/identidade-marca.exemplo.json). "
                          "Preenche hue-alvo/hue-faixa/sat-add/val-mult/logo automaticamente; "
                          "qualquer flag abaixo passada explicitamente tem prioridade sobre a config.")
    ap.add_argument("--logo-versao", choices=["clara", "escura"], default="clara",
                     help="qual versão do logo usar da marca-config, conforme o fundo da peça (padrão: clara)")

    ap.add_argument("--hue-alvo", type=float, default=None,
                     help="deslocamento de matiz em graus a aplicar (positivo ou negativo). "
                          "Calibre olhando o pixel gerado vs. o hex oficial (ex. colorsys.rgb_to_hsv).")
    ap.add_argument("--hue-faixa", type=lambda v: parse_par(v, "hue-faixa"), default=None,
                     help="faixa de matiz em graus a corrigir, formato 'min:max' (padrão 245:285 se não vier de config)")
    ap.add_argument("--sat-add", type=float, default=None, help="ajuste aditivo de saturação (-1 a 1)")
    ap.add_argument("--val-mult", type=float, default=None, help="multiplicador de brilho")

    ap.add_argument("--logo", default=None, help="caminho do PNG oficial do logo (sobrepõe o da marca-config, se houver)")
    ap.add_argument("--logo-pos", type=lambda v: parse_par(v, "logo-pos"), default=(0.06, 0.02),
                     help="posição do logo como fração 'x:y' da imagem (padrão 0.06:0.02)")
    ap.add_argument("--logo-largura-frac", type=float, default=0.14,
                     help="largura do logo como fração da largura da imagem (padrão 0.14)")
    ap.add_argument("--apagar-placeholder", type=str, default=None,
                     help="bounding box 'x0:y0:x1:y1' em pixels pra apagar um placeholder antes de colar o logo")

    ap.add_argument("--resize", type=lambda v: parse_par(v, "resize"), default=None,
                     help="tamanho final 'largura:altura' em pixels, ex. 1080:1080")

    args = ap.parse_args()

    # config de marca preenche o que não veio explícito por flag
    hue_alvo, hue_faixa, sat_add, val_mult, logo_path = args.hue_alvo, args.hue_faixa, args.sat_add, args.val_mult, args.logo
    if args.marca_config:
        marca = carregar_marca_config(args.marca_config)
        corr = marca.get("correcao_cor_calibrada", {})
        if hue_alvo is None:
            hue_alvo = corr.get("hue_alvo")
        if hue_faixa is None and corr.get("hue_faixa"):
            hue_faixa = tuple(corr["hue_faixa"])
        if sat_add is None:
            sat_add = corr.get("sat_add", 0.0)
        if val_mult is None:
            val_mult = corr.get("val_mult", 1.0)
        if logo_path is None:
            chave_logo = "versao_clara_png" if args.logo_versao == "clara" else "versao_escura_png"
            logo_cfg = marca.get("logo", {}).get(chave_logo)
            if logo_cfg:
                # caminhos de logo na marca-config são relativos à PASTA DA CONFIG, não à raiz do repo/projeto
                logo_path = os.path.normpath(os.path.join(os.path.dirname(args.marca_config), logo_cfg))
                if not os.path.isfile(logo_path):
                    raise SystemExit(
                        f"Logo não encontrado em: {logo_path}\n"
                        f"O campo '{chave_logo}' em {args.marca_config} é relativo à pasta dessa "
                        "config, não à raiz do repositório nem à pasta do projeto. Ajuste o caminho "
                        "no JSON (ver comentário em config/identidade-marca.exemplo.json) ou passe "
                        "--logo <caminho> diretamente para sobrepor."
                    )

    hue_faixa = hue_faixa or (245, 285)
    sat_add = sat_add if sat_add is not None else 0.0
    val_mult = val_mult if val_mult is not None else 1.0

    im = Image.open(args.src).convert("RGB")

    if hue_alvo is not None:
        im = corrigir_cor(im, hue_faixa, hue_alvo, sat_add, val_mult)

    if logo_path:
        placeholder_box = None
        if args.apagar_placeholder:
            x0, y0, x1, y1 = (int(v) for v in args.apagar_placeholder.split(":"))
            placeholder_box = (x0, y0, x1, y1)
        im = compositar_logo(im, logo_path, args.logo_pos, args.logo_largura_frac, placeholder_box)

    im = im.convert("RGB")

    if args.resize:
        w, h = (int(v) for v in args.resize)
        im = im.resize((w, h), Image.LANCZOS)

    im.save(args.out)
    print("salvo em", args.out)


if __name__ == "__main__":
    main()
