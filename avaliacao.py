import os
import json


PASTA_METAS = "metas_json"
PASTA_HISTORICO = "historico_json"


for pasta in [PASTA_METAS, PASTA_HISTORICO]:
    if not os.path.exists(pasta):
        os.makedirs(pasta)



def carregar_metas(funcionario):
    caminho = os.path.join(PASTA_METAS, f"{funcionario}.json")

    
    if not os.path.exists(caminho):
        dados = {"metas": {}}  
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)
        return dados

    
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)


def salvar_metas(funcionario, dados):
    caminho = os.path.join(PASTA_METAS, f"{funcionario}.json")
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)


def adicionar_meta(funcionario, nome_meta, descricao):
    dados = carregar_metas(funcionario)
    dados["metas"][nome_meta] = descricao
    salvar_metas(funcionario, dados)
    return True


def carregar_historico(funcionario):
    caminho = os.path.join(PASTA_HISTORICO, f"{funcionario}.json")

    
    if not os.path.exists(caminho):
        dados = {"historico": []}
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)
        return dados

    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)


def salvar_historico(funcionario, dados):
    caminho = os.path.join(PASTA_HISTORICO, f"{funcionario}.json")
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)


def registrar_avaliacao(funcionario, trimestre, nota, comentarios=""):
    dados = carregar_historico(funcionario)

    registro = {
        "trimestre": trimestre,
        "nota": nota,
        "comentarios": comentarios
    }

    dados["historico"].append(registro)
    salvar_historico(funcionario, dados)
    return True




def mostrar_historico(funcionario):
    dados = carregar_historico(funcionario)

    if not dados["historico"]:
        return f"\n⚠ O funcionário '{funcionario}' ainda não possui avaliações registradas."

    texto = f"\n📘 Histórico de Avaliações — {funcionario}\n"
    texto += "-" * 40 + "\n"

    for item in dados["historico"]:
        texto += (
            f"Trimestre: {item['trimestre']}\n"
            f"Nota: {item['nota']}\n"
            f"Comentários: {item['comentarios']}\n"
            "-----------------------------\n"
        )

    return texto
