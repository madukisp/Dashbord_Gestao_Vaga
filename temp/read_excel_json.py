import pandas as pd
import json
import os

file_path = "oris_selecionado.xlsx"
output_path = "temp/output.json"

try:
    df = pd.read_excel(file_path, nrows=1)

    if not df.empty:
        # Convert to json string
        json_str = df.iloc[0].to_json(force_ascii=False)
        # Write to file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(json_str)
        print("JSON written to " + output_path)
    else:
        print("Empty file")

except Exception as e:
    print(str(e))
