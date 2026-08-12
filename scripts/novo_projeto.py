"""
novo_projeto.py — cria a estrutura de pastas de um novo projeto de criativo,
já vinculado a uma config de identidade de marca.

Uso:

    python scripts/novo_projeto.py \
      --nome lancamento-produto-x \
      --marca-config config/minha-marca.json \
      --pasta-base projetos

Cria:

    projetos/lancamento-produto-x/
      referencias/        <- pasta vazia; cole aqui prints/imagens de referência
      artes-geradas/       <- onde o ChatGPT baixa e o finalize_arte.py salva
      projeto.json          <- preencha com formato, textos e elemento central
      prompt.txt             <- gerado depois por montar_prompt.py

Não roda nada de IA nem acessa rede — só monta o esqueleto de pastas/arquivos.
"""

import argparse
import json
import os

PROJETO_TEMPLATE = {
    "_comentario": (
        "Preencha os campos abaixo antes de rodar montar_prompt.py. "
        "'referencia_notas' descreve o que na(s) imagem(ns) de referencias/ "
        "deve ser mantido (composição, hierarquia) — não a paleta de cores "
        "da referência, essa vem da config de marca."
    ),
    "marca_config": None,
    "formato": "Feed (1080x1080px, quadrado)",
    "referencia_notas": "",
    "elemento_central": "",
    "headline": "",
    "textos_tela": [],
    "evitar_extra": []
}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--nome", required=True, help="nome do projeto (usado como nome da pasta, ex. lancamento-produto-x)")
    ap.add_argument("--marca-config", required=True, help="caminho para a config de identidade de marca já preenchida (ver config/identidade-marca.exemplo.json)")
    ap.add_argument("--pasta-base", default=".", help="pasta onde criar a pasta do projeto (padrão: diretório atual)")
    args = ap.parse_args()

    if not os.path.isfile(args.marca_config):
        raise SystemExit(
            f"Config de marca não encontrada: {args.marca_config}\n"
            "Copie config/identidade-marca.exemplo.json, preencha com sua marca, "
            "e aponte --marca-config para essa cópia."
        )

    projeto_dir = os.path.join(args.pasta_base, args.nome)
    referencias_dir = os.path.join(projeto_dir, "referencias")
    artes_dir = os.path.join(projeto_dir, "artes-geradas")

    if os.path.exists(projeto_dir):
        raise SystemExit(f"Já existe uma pasta em {projeto_dir} — escolha outro --nome ou apague antes.")

    os.makedirs(referencias_dir)
    os.makedirs(artes_dir)

    projeto_config = dict(PROJETO_TEMPLATE)
    projeto_config["marca_config"] = os.path.relpath(args.marca_config, projeto_dir).replace("\\", "/")

    projeto_json_path = os.path.join(projeto_dir, "projeto.json")
    with open(projeto_json_path, "w", encoding="utf-8") as f:
        json.dump(projeto_config, f, ensure_ascii=False, indent=2)

    print(f"Projeto criado em: {projeto_dir}")
    print(f"  - {referencias_dir}  (coloque aqui as imagens de referência)")
    print(f"  - {artes_dir}  (vazio por enquanto)")
    print(f"  - {projeto_json_path}  (preencha formato/headline/textos antes de continuar)")
    print()
    print("Próximo passo: preencha projeto.json, coloque referências em referencias/, "
          "depois rode scripts/montar_prompt.py.")


if __name__ == "__main__":
    main()
