import json
import os
import unicodedata
from datetime import date

from avaliacao import adicionar_meta, registrar_avaliacao, mostrar_historico



def normalizar(texto):
    texto = texto.lower()
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    texto = texto.replace("_", " ")
    texto = ' '.join(texto.split())
    return texto.strip()


if not os.path.exists('json'):
    os.makedirs('json')

if not os.path.exists('dados_funcionario'):
    os.makedirs('dados_funcionario')


caminho_cargos = 'json/cargos_salarios.json'

with open(caminho_cargos, 'r', encoding='utf-8') as file:
    cargos_salarios = json.load(file)


cargos_normalizados = {}

for categoria, cargos in cargos_salarios.items():
    for cargo, salario in cargos.items():
        chave = normalizar(cargo)
        cargos_normalizados[chave] = salario


def obter_salario(cargo):
    chave = normalizar(cargo)
    return cargos_normalizados.get(chave)


def calcular_idade(dia, mes, ano):
    hoje = date.today()
    idade = hoje.year - ano
    if (hoje.month, hoje.day) < (mes, dia):
        idade -= 1
    return idade


def cadastro():
    nome = input('Nome: ').title()
    dia = int(input('Dia de nascimento: '))
    mes = int(input('Mês de nascimento: '))
    ano = int(input('Ano de nascimento: '))
    sexo = input('Sexo (M/F): ').upper()
    cpf = input('CPF: ')

    while True:
        cargo = input('Cargo: ')
        salario = obter_salario(cargo)
        if salario is not None:
            break
        print('Cargo não encontrado. Digite novamente.')

    idade = calcular_idade(dia, mes, ano)

    dados = {
        "nome": nome,
        "nascimento": f"{dia:02d}/{mes:02d}/{ano}",
        "idade": idade,
        "sexo": sexo,
        "cpf": cpf,
        "cargo": cargo.title(),
        "salario": salario
    }

    nome_arquivo = normalizar(nome).replace(" ", "_")

    with open(f'dados_funcionario/{nome_arquivo}.json', 'w', encoding='utf-8') as file:
        json.dump(dados, file, indent=4, ensure_ascii=False)

    print("Cadastro salvo com sucesso!")


def listar_funcionarios():
    arquivos = os.listdir('dados_funcionario')
    if not arquivos:
        print("Nenhum funcionário cadastrado.")
        return

    for arq in arquivos:
        with open(f'dados_funcionario/{arq}', 'r', encoding='utf-8') as file:
            print(json.load(file))


def buscar_funcionario():
    nome = input('Nome do funcionário: ').title()
    nome_arquivo = nome.replace(" ", "_")
    caminho = f'dados_funcionario/{nome_arquivo}.json'

    if os.path.exists(caminho):
        with open(caminho, 'r', encoding='utf-8') as file:
            print(json.load(file))
    else:
        print("Funcionário não encontrado.")


PERMISSOES_CARGA = {
    "leve": [
        "motorista vuc",
        "motorista toco",
        "motorista truck",
        "motorista de coleta e entrega",
        "motorista operador"
    ],

    "pesada": [
        "motorista truck",
        "motorista carreteiro",
        "motorista munck",
        "motorista operador"
    ],

    "bi trem": [
        "motorista bi-trem / rodotrem",
        "motorista carreteiro"
    ],

    "rodo trem": [
        "motorista bi-trem / rodotrem",
        "motorista carreteiro"
    ]
}


def locar_caminhao():
    nome_input = input('Nome do funcionário que vai dirigir: ')
    nome_normalizado = normalizar(nome_input)

    encontrado = None

    for arq in os.listdir("dados_funcionario"):
        nome_arquivo = arq.replace(".json", "")
        if normalizar(nome_arquivo) == nome_normalizado:
            encontrado = arq
            break

    if encontrado is None:
        print("Funcionário não encontrado!")
        return

    with open(f"dados_funcionario/{encontrado}", "r", encoding="utf-8") as file:
        dados = json.load(file)

    cargo_funcionario = normalizar(dados["cargo"])

    if not cargo_funcionario.startswith("motorista"):
        print(f"O funcionário {dados['nome']} NÃO é motorista e não pode dirigir caminhão!")
        return

    print("\nTipos de carga disponíveis:")
    print(" - leve")
    print(" - pesada")
    print(" - bi trem")
    print(" - rodo trem")
    print()

    carga = input("Qual o tipo de carga?: ").lower().strip()

    if carga not in PERMISSOES_CARGA:
        print("Tipo de carga inválido!")
        return

    permissoes = PERMISSOES_CARGA[carga]

    if cargo_funcionario not in permissoes:
        print(f"O motorista {dados['nome']} NÃO tem permissão para transportar carga '{carga}'.")
        print("Cargos permitidos para essa carga:")
        for c in permissoes:
            print(" - " + c.title())
        return

    caminhao = input("Número do caminhão: ")
    print(f"Caminhão {caminhao} locado com sucesso para {dados['nome']} para carga '{carga}'!")


def debug_ver_nomes():
    print("\n=== DEBUG: Arquivos na pasta dados_funcionario/ ===")
    for arq in os.listdir("dados_funcionario"):
        print("Arquivo:", arq, "| normalizado:", normalizar(arq.replace(".json", "")))
    print("====================================================\n")


# ====================================================
# =================== MENU ===========================
# ====================================================

def menu():
    while True:
        print('\n1 - Cadastrar funcionário')
        print('2 - Listar funcionários')
        print('3 - Buscar por nome')
        print('4 - Locar caminhão')
        print('5 - Debug: ver arquivos')
        print('6 - Registrar metas')
        print('7 - Registrar avaliação trimestral')
        print('8 - Ver histórico de avaliações')
        print('0 - SAIR')

        opc = input('Escolha: ')
        if opc == '1':
            cadastro()

        elif opc == '2':
            listar_funcionarios()

        elif opc == '3':
            buscar_funcionario()

        elif opc == '4':
            locar_caminhao()

        elif opc == '5':
            debug_ver_nomes()

        elif opc == '6':   # registrar meta
            nome = input("Nome do funcionário: ").title().replace(" ", "_")
            meta = input("Nome da meta: ")
            desc = input("Descrição da meta: ")
            adicionar_meta(nome, meta, desc)
            print("Meta registrada!")

        elif opc == '7':  # registrar avaliação
            nome = input("Nome do funcionário: ").title().replace(" ", "_")
            trimestre = input("Trimestre (ex: 1º Trimestre): ")
            nota = float(input("Nota: "))
            com = input("Comentários: ")
            registrar_avaliacao(nome, trimestre, nota, com)
            print("Avaliação registrada!")

        elif opc == '8':  # ver histórico
            nome = input("Nome do funcionário: ").title().replace(" ", "_")
            print(mostrar_historico(nome))


        elif opc == '0':
            break


menu()
