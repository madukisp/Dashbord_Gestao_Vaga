import pandas as pd
import re
import os


def extrair_colunas_do_md(arquivo_md):
    """Extrai as colunas marcadas como 's' (sim) do arquivo markdown."""
    colunas_sim = []

    with open(arquivo_md, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Padrão: "Coluna 'nome' - Usar? (s/n): s"
    # Captura o nome da coluna e verifica se a resposta é 's'
    padrao = r"Coluna '([^']+)' - Usar\? \(s/n\): ([sn])"
    matches = re.findall(padrao, conteudo)

    for coluna, resposta in matches:
        if resposta.lower() == 's':
            colunas_sim.append(coluna)

    return colunas_sim


def criar_copia_selecionada(arquivo_origem, arquivo_md, arquivo_destino):
    """Cria uma cópia do Excel com apenas as colunas selecionadas."""
    print(f"Lendo arquivo de seleção: {arquivo_md}")
    colunas_selecionadas = extrair_colunas_do_md(arquivo_md)

    if not colunas_selecionadas:
        print("Nenhuma coluna marcada como 's' foi encontrada.")
        return

    print(f"\nColunas encontradas ({len(colunas_selecionadas)}):")
    for col in colunas_selecionadas:
        print(f"  ✓ {col}")

    print(f"\nLendo arquivo original: {arquivo_origem}")
    # Ler o Excel com cabeçalho na linha 8
    df = pd.read_excel(arquivo_origem, header=7)

    print(f"Total de colunas no arquivo original: {len(df.columns)}")
    print(f"Total de linhas no arquivo original: {len(df)}")

    # Validar se todas as colunas existem no arquivo
    colunas_nao_encontradas = [c for c in colunas_selecionadas if c not in df.columns]
    if colunas_nao_encontradas:
        print(f"\n⚠️ Aviso: As seguintes colunas não foram encontradas:")
        for col in colunas_nao_encontradas:
            print(f"  - {col}")
        # Remover colunas não encontradas
        colunas_selecionadas = [c for c in colunas_selecionadas if c in df.columns]
        print(f"\nContinuando com {len(colunas_selecionadas)} colunas válidas...")

    # Filtrar apenas as colunas selecionadas
    df_filtrado = df[colunas_selecionadas]

    # Salvar em novo arquivo Excel
    print(f"\nCriando arquivo de destino: {arquivo_destino}")
    df_filtrado.to_excel(arquivo_destino, index=False)

    print(f"\n✓ Arquivo criado com sucesso!")
    print(f"  Colunas: {len(df_filtrado.columns)}")
    print(f"  Linhas: {len(df_filtrado)}")
    print(f"  Arquivo: {arquivo_destino}")


def main():
    arquivo_md = 'colunas_db.md'
    arquivo_origem = 'oris.xlsx'
    arquivo_destino = 'oris_selecionado.xlsx'

    # Verificar se arquivos existem
    if not os.path.exists(arquivo_md):
        print(f"Erro: Arquivo '{arquivo_md}' não encontrado.")
        return
    if not os.path.exists(arquivo_origem):
        print(f"Erro: Arquivo '{arquivo_origem}' não encontrado.")
        return

    criar_copia_selecionada(arquivo_origem, arquivo_md, arquivo_destino)


if __name__ == '__main__':
    main()
