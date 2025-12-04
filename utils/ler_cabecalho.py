import pandas as pd

# Ler o cabeçalho da planilha oris.xlsx na linha 8
# header=7 porque pandas usa índice 0-based (linha 8 = índice 7)
df = pd.read_excel('oris.xlsx', header=7)

# Exibir as colunas do cabeçalho
print("Cabeçalho da planilha:")
print(df.columns.tolist())

# Exibir informações adicionais
print(f"\nTotal de colunas: {len(df.columns)}")
print(f"\nPrimeiras 5 linhas de dados:")
print(df.head())
