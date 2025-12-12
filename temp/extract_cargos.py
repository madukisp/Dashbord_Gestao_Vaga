
import pandas as pd
import json

def extract_cargos_from_excel(file_path):
    """
    Extrai cargos únicos da coluna 'Cargo' de um arquivo Excel.

    Args:
        file_path (str): O caminho para o arquivo Excel.

    Returns:
        list: Uma lista de cargos únicos.
    """
    try:
        # Carregar a planilha, especificando o cabeçalho na linha 8 (índice 7)
        df = pd.read_excel(file_path, header=7)
        
        # Verificar se a coluna 'Cargo' existe
        if 'Cargo' in df.columns:
            # Obter valores únicos da coluna 'Cargo', remover NaNs e converter para lista
            cargos_unicos = df['Cargo'].dropna().unique().tolist()
            return sorted(cargos_unicos)
        else:
            return "A coluna 'Cargo' não foi encontrada no arquivo."
    except FileNotFoundError:
        return f"O arquivo '{file_path}' não foi encontrado."
    except Exception as e:
        return f"Ocorreu um erro: {e}"

if __name__ == "__main__":
    caminho_arquivo = 'oris.xlsx'
    cargos = extract_cargos_from_excel(caminho_arquivo)
    
    if isinstance(cargos, list):
        # Criar o dicionário para o JSON
        cargos_mapeados = {cargo: "Não Classificado" for cargo in cargos}
        
        # Salvar em um arquivo JSON
        with open('cargos_niveis.json', 'w', encoding='utf-8') as f:
            json.dump(cargos_mapeados, f, ensure_ascii=False, indent=4)
        
        print(f"{len(cargos)} cargos únicos foram extraídos e salvos em 'cargos_niveis.json'.")
    else:
        print(cargos)
