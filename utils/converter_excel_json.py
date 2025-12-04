"""
Script para converter planilha Excel para JSON
Uso: python converter_excel_json.py
"""

import pandas as pd
import json


def converter_excel_para_json(arquivo_excel, arquivo_json_saida):
    """
    Converte arquivo Excel para JSON no formato esperado pelo dashboard

    Args:
        arquivo_excel: Caminho do arquivo Excel (.xlsx ou .xls)
        arquivo_json_saida: Caminho do arquivo JSON de saída
    """

    print(f"📖 Lendo arquivo Excel: {arquivo_excel}")

    # Ler Excel
    df = pd.read_excel(arquivo_excel)

    print(f"✅ {len(df)} registros encontrados")
    print(f"📊 Colunas: {', '.join(df.columns.tolist())}")

    # Converter datas para string no formato DD/MM/YYYY
    date_columns = [
        "Dt Admissão",
        "Dt Rescisão",
        "Dt Nascimento",
        "Dt Início Cargo",
        "Dt Início Centro de Custo",
        "Dt Início Empresa",
        "Dt Início Escala",
        "Dt Início Local de Trabalho",
        "Dt Início Situação",
        "Dt Início Tipo Funcionário",
    ]

    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
            df[col] = df[col].dt.strftime("%d/%m/%Y")
            df[col] = df[col].replace("NaT", None)

    # Converter para JSON
    dados_json = df.to_dict(orient="records")

    # Salvar arquivo
    with open(arquivo_json_saida, "w", encoding="utf-8") as f:
        json.dump(dados_json, f, ensure_ascii=False, indent=2)

    print(f"✅ Arquivo JSON criado: {arquivo_json_saida}")
    print(f"📁 Tamanho: {len(json.dumps(dados_json))/1024:.2f} KB")


if __name__ == "__main__":
    # CONFIGURE AQUI OS CAMINHOS DOS ARQUIVOS
    arquivo_entrada = "oris_selecionado.xlsx"  # Seu arquivo Excel
    arquivo_saida = "dados_colaboradores.json"  # Arquivo JSON de saída

    try:
        converter_excel_para_json(arquivo_entrada, arquivo_saida)
        print("\n🎉 Conversão concluída com sucesso!")
        print(
            f"Agora você pode fazer upload do arquivo '{arquivo_saida}' no dashboard."
        )
    except FileNotFoundError:
        print(f"\n❌ ERRO: Arquivo '{arquivo_entrada}' não encontrado!")
        print("Certifique-se de que o arquivo Excel está na mesma pasta do script.")
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
