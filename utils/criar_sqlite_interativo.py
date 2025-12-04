import pandas as pd
import sqlite3
import os

# Ler o arquivo Excel
df = pd.read_excel('oris.xlsx', header=7)

# Lista para armazenar as colunas selecionadas
colunas_selecionadas = []

print("=" * 60)
print("SELEÇÃO DE COLUNAS PARA CRIAR BANCO DE DADOS")
print("=" * 60)
print(f"\nTotal de colunas encontradas: {len(df.columns)}\n")

# Perguntar para cada coluna
for i, coluna in enumerate(df.columns, 1):
    while True:
        resposta = input(f"{i}. Coluna '{coluna}' - Usar? (s/n): ").strip().lower()
        if resposta in ['s', 'sim', 'n', 'não', 'nao']:
            if resposta in ['s', 'sim']:
                colunas_selecionadas.append(coluna)
            break
        else:
            print("   Por favor, digite 's' para sim ou 'n' para não.\n")

import pandas as pd
import sqlite3
import os
import json
import argparse
import sys


# Configurações de arquivos
EXCEL_FILE = 'oris.xlsx'
DB_FILE = 'oris.db'
TABLE_NAME = 'oris'
SELECTION_FILE = 'col_selection.json'


def carregar_df():
    if os.path.exists(DB_FILE):
        try:
            conn = sqlite3.connect(DB_FILE)
            df = pd.read_sql(f"SELECT * FROM {TABLE_NAME}", conn)
            conn.close()
            return df
        except Exception:
            pass
    if os.path.exists(EXCEL_FILE):
        return pd.read_excel(EXCEL_FILE, header=7)
    print(f"Nenhum arquivo encontrado: '{DB_FILE}' nem '{EXCEL_FILE}'.")
    sys.exit(1)


def carregar_selecao():
    if os.path.exists(SELECTION_FILE):
        try:
            with open(SELECTION_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def salvar_selecao(mapping):
    with open(SELECTION_FILE, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)


def perguntar_colunas(df, selecao_existente, force_interactive=False):
    cols = list(df.columns)
    selecionadas = []

    print("=" * 60)
    print("SELEÇÃO DE COLUNAS PARA CRIAR BANCO DE DADOS")
    print("=" * 60)
    print(f"\nTotal de colunas encontradas: {len(cols)}\n")

    for i, coluna in enumerate(cols, 1):
        # usar valor existente quando existir e não for forçado a interagir
        if coluna in selecao_existente and not force_interactive:
            usar = bool(selecao_existente[coluna])
            status = 's' if usar else 'n'
            print(f"{i}. Coluna '{coluna}' - Usar? (s/n): {status}  (pulado - salvo)")
            if usar:
                selecionadas.append(coluna)
            continue

        # perguntar ao usuário
        while True:
            resposta = input(f"{i}. Coluna '{coluna}' - Usar? (s/n): ").strip().lower()
            if resposta in ['s', 'sim', 'n', 'não', 'nao']:
                usar = resposta in ['s', 'sim']
                if usar:
                    selecionadas.append(coluna)
                selecao_existente[coluna] = usar
                break
            else:
                print("   Por favor, digite 's' para sim ou 'n' para não.\n")

    print("\n" + "=" * 60)
    print(f"Colunas selecionadas ({len(selecionadas)}):")
    for col in selecionadas:
        print(f"  ✓ {col}")
    print("=" * 60)

    return selecionadas, selecao_existente


def criar_banco(df_filtrado):
    # Remover arquivo existente
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"\nArquivo {DB_FILE} existente foi removido.")

    conn = sqlite3.connect(DB_FILE)
    df_filtrado.to_sql(TABLE_NAME, conn, index=False, if_exists='replace')
    conn.close()


def main():
    parser = argparse.ArgumentParser(description='Criar SQLite a partir de Excel selecionando colunas')
    parser.add_argument('--interactive', '-i', action='store_true', help='Forçar interação para todas as colunas')
    parser.add_argument('--reset', '-r', action='store_true', help='Resetar arquivo de seleção e iniciar do zero')
    parser.add_argument('--show', action='store_true', help='Mostrar seleção salva e sair')
    args = parser.parse_args()

    df = carregar_df()

    selecao_existente = {} if args.reset else carregar_selecao()

    if args.show:
        if not selecao_existente:
            print('Nenhuma seleção salva encontrada.')
        else:
            true_cols = [c for c, v in selecao_existente.items() if v]
            false_cols = [c for c, v in selecao_existente.items() if not v]
            print('Colunas marcadas como S (total={}):'.format(len(true_cols)))
            for c in true_cols:
                print('  ✓', c)
            print('\nColunas marcadas como N (total={}):'.format(len(false_cols)))
            for c in false_cols:
                print('  -', c)
        return

    selecionadas, selecao_atualizada = perguntar_colunas(df, selecao_existente, force_interactive=args.interactive)

    # Salvar seleção para reutilização futura
    salvar_selecao(selecao_atualizada)

    confirmacao = input("\nDeseja criar o banco de dados SQLite com essas colunas? (s/n): ").strip().lower()
    if confirmacao in ['s', 'sim']:
        df_filtrado = df[selecionadas]
        criar_banco(df_filtrado)
        print(f"\n✓ Banco de dados '{DB_FILE}' criado com sucesso!")
        print(f"  Total de linhas: {len(df_filtrado)}")
        print(f"  Total de colunas: {len(selecionadas)}")
    else:
        print("\nOperação cancelada.")


if __name__ == '__main__':
    main()
