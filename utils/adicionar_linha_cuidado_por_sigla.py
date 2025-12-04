import os
import re
import sys
import json
import sqlite3
import pandas as pd

# Linhas de cuidado padrão
LINHAS_CUIDADO = [
    "URGENCIA E EMERGENCIA",
    "SAUDE MENTAL",
    "APS",
    "SAUDE DO IDOSO",
    "PROGRAMAS",
]

DB_FILE = 'oris.db'
TABLE_NAME = 'oris'
MAPPING_FILE = 'mappings_nome_fantasia.json'


def aplicar_regras_automaticas_nome(nome):
    """Aplica regras automáticas verificando se o nome contém siglas-chave.
    Retorna a linha de cuidado ou None se não aplicável.
    """
    if pd.isna(nome) or nome == '':
        return None
    texto = str(nome).upper()
    if re.search(r"\bUBS\b", texto):
        return 'APS'
    if re.search(r"\bCAPS\b", texto):
        return 'SAUDE MENTAL'
    if re.search(r"\bUPA\b", texto):
        return 'URGENCIA E EMERGENCIA'
    if re.search(r"\bPAI\b", texto):
        return 'SAUDE DO IDOSO'
    return None


def carregar_mapeamento():
    if os.path.exists(MAPPING_FILE):
        try:
            with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def salvar_mapeamento(mapping):
    with open(MAPPING_FILE, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)


def perguntar_linha_para_nome(nome, mapping):
    """Interação para um `Nome Fantasia` individual.
    Retorna a linha de cuidado escolhida e atualiza `mapping`.
    """
    if nome in mapping:
        return mapping[nome]

    print('\n' + '=' * 60)
    print(f"Nome Fantasia: {nome}")
    print('=' * 60)
    print('\nEscolha a Linha de cuidado correspondente:')
    for i, opc in enumerate(LINHAS_CUIDADO, 1):
        print(f"  {i}. {opc}")
    print('  0. Outra (escrever manualmente)')

    while True:
        escolha = input('\nDigite o número ou texto (ex: 1 ou "APS"): ').strip()
        if escolha == '0':
            while True:
                outra = input('Digite a linha de cuidado: ').strip()
                if outra:
                    mapping[nome] = outra
                    return outra
                print('Entrada vazia. Tente novamente.')

        if escolha.isdigit():
            num = int(escolha)
            if 1 <= num <= len(LINHAS_CUIDADO):
                resultado = LINHAS_CUIDADO[num - 1]
                mapping[nome] = resultado
                return resultado

        escolha_upper = escolha.upper()
        for opc in LINHAS_CUIDADO:
            if escolha_upper == opc.upper() or escolha_upper in opc.upper():
                mapping[nome] = opc
                return opc

        print('Entrada inválida. Tente novamente.')


def main():
    print('Carregando banco de dados...')
    if not os.path.exists(DB_FILE):
        print(f"Erro: '{DB_FILE}' não encontrado. Execute 'transformar_excel_sqlite.py' primeiro.")
        sys.exit(1)

    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql(f"SELECT * FROM {TABLE_NAME}", conn)
    conn.close()

    # localizar coluna Nome Fantasia
    nome_col = None
    for col in df.columns:
        if col.lower().strip() in ('nome fantasia', 'nome_fantasia'):
            nome_col = col
            break
    if not nome_col:
        print("Erro: coluna 'Nome Fantasia' não encontrada. Colunas disponíveis:")
        for col in df.columns:
            print(' -', col)
        sys.exit(1)

    print(f"Coluna usada: '{nome_col}'")

    nomes_unicos = [n for n in df[nome_col].astype(str).fillna('').unique() if n != '']
    print(f"Total de nomes fantasia únicos: {len(nomes_unicos)}")

    mapping = carregar_mapeamento()

    resultados_auto = []
    resultados_inter = []

    for nome in sorted(nomes_unicos):
        # tentar regra automática
        linha_auto = aplicar_regras_automaticas_nome(nome)
        if linha_auto:
            mapping[nome] = linha_auto
            resultados_auto.append((nome, linha_auto))
            print(f"Auto: {nome} -> {linha_auto}")
            continue
        # se já mapeado, pular
        if nome in mapping:
            continue
        # perguntar
        linha = perguntar_linha_para_nome(nome, mapping)
        resultados_inter.append((nome, linha))

    # salvar mapeamento
    salvar_mapeamento(mapping)
    print(f"\n✓ Mapeamento salvo em '{MAPPING_FILE}'")

    # aplicar ao DataFrame
    nova_col = 'Linha de cuidado'
    def obter(nome):
        if nome in mapping:
            return mapping[nome]
        auto = aplicar_regras_automaticas_nome(nome)
        return auto if auto else 'NÃO DEFINIDO'

    df[nova_col] = df[nome_col].astype(str).map(obter)

    # reordenar para inserir após Nome Fantasia
    cols = list(df.columns)
    try:
        idx = cols.index(nome_col)
        if nova_col in cols:
            cols.remove(nova_col)
        cols.insert(idx + 1, nova_col)
        df = df[cols]
    except ValueError:
        pass

    # salvar no DB
    conn = sqlite3.connect(DB_FILE)
    df.to_sql(TABLE_NAME, conn, index=False, if_exists='replace')
    conn.close()

    print(f"\n✓ Banco atualizado: {DB_FILE} (tabela: {TABLE_NAME})")
    print(f"Linhas: {len(df)} | Colunas: {len(df.columns)}")


if __name__ == '__main__':
    main()
