import pandas as pd
import sqlite3
import os


def transformar_excel_para_sqlite(arquivo_excel, arquivo_db, tabela_nome='oris'):
    """Transforma um arquivo Excel em banco de dados SQLite."""
    
    if not os.path.exists(arquivo_excel):
        print(f"Erro: Arquivo '{arquivo_excel}' não encontrado.")
        return False
    
    print(f"Lendo arquivo Excel: {arquivo_excel}")
    
    try:
        # Tentar ler como arquivo selecionado (sem header específico)
        df = pd.read_excel(arquivo_excel)
    except Exception as e:
        print(f"Erro ao ler Excel: {e}")
        return False
    
    print(f"Total de linhas: {len(df)}")
    print(f"Total de colunas: {len(df.columns)}")
    print(f"\nColunas encontradas:")
    for i, col in enumerate(df.columns, 1):
        print(f"  {i}. {col}")
    
    # Remover arquivo de banco existente
    if os.path.exists(arquivo_db):
        os.remove(arquivo_db)
        print(f"\nArquivo '{arquivo_db}' existente foi removido.")
    
    # Criar conexão e inserir dados
    print(f"\nCriando banco de dados: {arquivo_db}")
    conexao = sqlite3.connect(arquivo_db)
    
    try:
        df.to_sql(tabela_nome, conexao, index=False, if_exists='replace')
        conexao.close()
        
        print(f"\n✓ Banco de dados criado com sucesso!")
        print(f"  Tabela: {tabela_nome}")
        print(f"  Linhas: {len(df)}")
        print(f"  Colunas: {len(df.columns)}")
        print(f"  Arquivo: {arquivo_db}")
        
        return True
    except Exception as e:
        conexao.close()
        print(f"Erro ao criar banco de dados: {e}")
        return False


def main():
    arquivo_excel = 'oris_selecionado.xlsx'
    arquivo_db = 'oris.db'
    
    transformar_excel_para_sqlite(arquivo_excel, arquivo_db)


if __name__ == '__main__':
    main()
