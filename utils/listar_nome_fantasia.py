import sqlite3
import sys

DB_FILE = 'oris.db'
TABLE = 'oris'
COL = 'Nome Fantasia'

if __name__ == '__main__':
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        # Usar colchetes para lidar com nomes com espaços
        q = f"SELECT DISTINCT [{COL}] FROM {TABLE} ORDER BY [{COL}] COLLATE NOCASE"
        cur.execute(q)
        rows = cur.fetchall()
        conn.close()
    except Exception as e:
        print(f"Erro ao acessar {DB_FILE}: {e}")
        sys.exit(1)

    valores = [r[0] for r in rows if r[0] is not None]
    if not valores:
        print('Nenhum valor encontrado em "Nome Fantasia".')
    else:
        print(f'Total distintos: {len(valores)}')
        for v in valores:
            print(v)
