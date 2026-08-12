"""
montar_prompt.py — monta o prompt de geração de imagem a partir da config de
marca + config do projeto, pronto para colar no ChatGPT.

Uso:

    python scripts/montar_prompt.py --projeto projetos/lancamento-produto-x

Lê `<projeto>/projeto.json` (formato, headline, elemento central, textos) e
a config de marca referenciada nele (`marca_config`), e escreve
`<projeto>/prompt.txt` com o prompt em UM PARÁGRAFO ÚNICO, sem quebra de
linha — quebras de linha no meio do texto disparam o envio prematuro da
mensagem no editor do ChatGPT (bug observado repetidas vezes nesse fluxo).
"""

import argparse
import json
import os


def carregar_json(caminho):
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


def montar_prompt(marca, projeto):
    paleta = marca.get("paleta", {})
    cor_principal = paleta.get("cor_principal", {})
    cor_secundaria = paleta.get("cor_secundaria", {})
    tipografia = marca.get("tipografia", {})

    textos_tela = projeto.get("textos_tela") or []
    textos_tela_fmt = "; ".join(f'"{t}"' for t in textos_tela) if textos_tela else "nenhum texto de interface além do já especificado"

    evitar_padrao = [
        "banco de imagens genérico",
        "pessoas sorrindo forçado",
        "estética de anúncio de coach/infoproduto (gradiente colorido excessivo, emoji em excesso, promessa gritada)",
    ]
    evitar = evitar_padrao + list(projeto.get("evitar_extra") or [])

    blocos = [
        f"FORMATO: {projeto.get('formato', '(preencher formato)')}.",
        f"REFERÊNCIA DE COMPOSIÇÃO: {projeto.get('referencia_notas') or '(preencher o que da referência deve ser mantido: enquadramento, hierarquia visual, forma de destacar o elemento central — use apenas como inspiração de composição, não copie marca, logo, cores ou texto da referência original)'}.",
        f"IDENTIDADE VISUAL DA MARCA: cor principal {cor_principal.get('hex', '(preencher hex)')} ({cor_principal.get('uso', '')}), cor secundária {cor_secundaria.get('hex', '(preencher hex)')} ({cor_secundaria.get('uso', '')}), tipografia {tipografia.get('fonte_headline', '(preencher fonte)')} para headline e {tipografia.get('fonte_corpo', '(preencher fonte)')} para texto de apoio, personalidade visual: {marca.get('personalidade_visual', '(preencher personalidade visual da marca)')}.",
        f"ELEMENTO CENTRAL: {projeto.get('elemento_central') or '(preencher elemento central da composição)'}.",
        f'TEXTO A INSERIR NA IMAGEM: headline "{projeto.get("headline") or "(preencher headline)"}" em destaque, com contraste forte contra o fundo, fonte bold; textos adicionais de tela: {textos_tela_fmt}.',
        "LOGO: não desenhe nenhum logo — deixe um espaço vazio no canto (superior ou inferior) reservado para o logo, que será inserido depois por fora desta geração.",
        f"EVITAR: {', '.join(evitar)}.",
    ]

    # parágrafo único, sem quebra de linha — ver docstring do módulo
    return " ".join(blocos)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--projeto", required=True, help="pasta do projeto (criada por novo_projeto.py, contendo projeto.json)")
    args = ap.parse_args()

    projeto_json_path = os.path.join(args.projeto, "projeto.json")
    projeto = carregar_json(projeto_json_path)

    marca_config_path = projeto.get("marca_config")
    if not marca_config_path:
        raise SystemExit(f"{projeto_json_path} não tem 'marca_config' preenchido.")
    marca_config_abs = os.path.normpath(os.path.join(args.projeto, marca_config_path))
    if not os.path.isfile(marca_config_abs):
        raise SystemExit(f"Config de marca não encontrada: {marca_config_abs}")
    marca = carregar_json(marca_config_abs)

    prompt = montar_prompt(marca, projeto)

    out_path = os.path.join(args.projeto, "prompt.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(prompt)

    print(f"prompt salvo em: {out_path}")
    print()
    print("--- preview ---")
    print(prompt)

    if "(preencher" in prompt:
        print()
        print("AVISO: ainda há campos não preenchidos em projeto.json ou na config de marca "
              "(marcados como '(preencher ...)') — complete antes de colar no ChatGPT.")


if __name__ == "__main__":
    main()
