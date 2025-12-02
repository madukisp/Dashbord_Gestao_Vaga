from flask import Flask, render_template, jsonify, request
import pandas as pd
import json
import os

app = Flask(__name__)

def load_data():
    caminho_arquivo = os.path.join(os.path.dirname(__file__), 'Pasta1.xlsx')
    df = pd.read_excel(caminho_arquivo)
    df = df.dropna(how='all')
    
    # Limpar espaços extras
    df['Nivel'] = df['Nivel'].apply(lambda x: str(x).strip() if pd.notna(x) else 'Não Classificado')
    df['LINHA DE CUIDADO'] = df['LINHA DE CUIDADO'].apply(lambda x: str(x).strip() if pd.notna(x) else 'Não Classificado')
    
    # Criar coluna Mês/Ano
    df['Mês/Ano'] = df['DATA ABERTURA DA VAGA'].dt.to_period('M').astype(str)
    
    # Calcular tempos
    df['Tempo Seleção (dias)'] = (df['DATA DE FECHAMENTO VAGA EM SELEÇÃO '] - df['DATA ABERTURA DA VAGA']).dt.days
    df['Tempo Admissão (dias)'] = (df['DATA DE INÍCIO SUBSTITUIÇÃO'] - df['DATA DE FECHAMENTO VAGA EM SELEÇÃO ']).dt.days
    
    return df

df = load_data()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/filtros')
def get_filtros():
    meses = sorted(df['Mês/Ano'].dropna().unique().tolist())
    niveis = sorted([n for n in df['Nivel'].unique() if n != 'Não Classificado'])
    linhas = sorted([lc for lc in df['LINHA DE CUIDADO'].unique() if lc != 'Não Classificado'])
    status = df['Status Vaga'].dropna().unique().tolist()
    
    return jsonify({
        'meses': meses,
        'niveis': niveis,
        'linhas_cuidado': linhas,
        'status': status
    })

@app.route('/api/vagas')
def get_vagas():
    meses = request.args.getlist('mes')
    niveis = request.args.getlist('nivel')
    status = request.args.getlist('status')
    
    df_filtrado = df.copy()
    
    if meses:
        df_filtrado = df_filtrado[df_filtrado['Mês/Ano'].isin(meses)]
    if niveis:
        df_filtrado = df_filtrado[df_filtrado['Nivel'].isin(niveis)]
    if status:
        df_filtrado = df_filtrado[df_filtrado['Status Vaga'].isin(status)]
    
    # Contagem por nível
    por_nivel = df_filtrado['Nivel'].value_counts().to_dict()
    
    # Contagem por linha de cuidado
    por_linha = df_filtrado['LINHA DE CUIDADO'].value_counts().to_dict()
    if 'Não Classificado' in por_linha:
        del por_linha['Não Classificado']
    
    # Tabela cruzada
    cross = pd.crosstab(df_filtrado['LINHA DE CUIDADO'], df_filtrado['Nivel'], margins=True, margins_name='Total')
    cross_dict = cross.to_dict('index')
    
    return jsonify({
        'total': len(df_filtrado),
        'por_nivel': por_nivel,
        'por_linha_cuidado': por_linha,
        'tabela_cruzada': cross_dict
    })

@app.route('/api/desligamentos')
def get_desligamentos():
    meses = request.args.getlist('mes')
    linhas = request.args.getlist('linha')
    
    df_desl = df[df['MOTIVO DO DESLIGAMENTO'].notna()].copy()
    
    if meses:
        df_desl = df_desl[df_desl['Mês/Ano'].isin(meses)]
    if linhas:
        df_desl = df_desl[df_desl['LINHA DE CUIDADO'].isin(linhas)]
    
    # Urgência e Emergência
    df_ue = df_desl[df_desl['LINHA DE CUIDADO'].str.contains('Urgência|Emergência', case=False, na=False)]
    motivos_ue = df_ue['MOTIVO DO DESLIGAMENTO'].value_counts().head(10).to_dict()
    
    # APS
    df_aps = df_desl[df_desl['LINHA DE CUIDADO'].str.contains('Atenção Básica|Atenção Primária', case=False, na=False)]
    motivos_aps = df_aps['MOTIVO DO DESLIGAMENTO'].value_counts().head(10).to_dict()
    
    # Top 5 geral
    top5 = df_desl['MOTIVO DO DESLIGAMENTO'].value_counts().head(5).to_dict()
    
    return jsonify({
        'urgencia_emergencia': motivos_ue,
        'aps': motivos_aps,
        'top5_geral': top5
    })

@app.route('/api/tempos')
def get_tempos():
    meses = request.args.getlist('mes')
    linhas = request.args.getlist('linha')
    
    df_tempo = df.copy()
    
    if meses:
        df_tempo = df_tempo[df_tempo['Mês/Ano'].isin(meses)]
    if linhas:
        df_tempo = df_tempo[df_tempo['LINHA DE CUIDADO'].isin(linhas)]
    
    # Tempo médio geral
    tempo_sel = df_tempo['Tempo Seleção (dias)'].dropna()
    tempo_sel = tempo_sel[tempo_sel >= 0]
    media_sel = float(tempo_sel.mean()) if len(tempo_sel) > 0 else 0
    
    tempo_adm = df_tempo['Tempo Admissão (dias)'].dropna()
    tempo_adm = tempo_adm[tempo_adm >= 0]
    media_adm = float(tempo_adm.mean()) if len(tempo_adm) > 0 else 0
    
    # Por linha de cuidado
    tempo_por_linha_sel = df_tempo[df_tempo['Tempo Seleção (dias)'] >= 0].groupby('LINHA DE CUIDADO')['Tempo Seleção (dias)'].mean().to_dict()
    tempo_por_linha_adm = df_tempo[df_tempo['Tempo Admissão (dias)'] >= 0].groupby('LINHA DE CUIDADO')['Tempo Admissão (dias)'].mean().to_dict()
    
    # Por nível
    tempo_por_nivel = df_tempo.groupby('Nivel').agg({
        'Tempo Seleção (dias)': lambda x: x[x >= 0].mean(),
        'Tempo Admissão (dias)': lambda x: x[x >= 0].mean()
    }).fillna(0).to_dict('index')
    
    # Evolução mensal
    evolucao = df_tempo.groupby('Mês/Ano').agg({
        'Tempo Seleção (dias)': lambda x: x[x >= 0].mean(),
        'Tempo Admissão (dias)': lambda x: x[x >= 0].mean()
    }).fillna(0).to_dict('index')
    
    return jsonify({
        'media_selecao': round(media_sel, 1),
        'media_admissao': round(media_adm, 1),
        'media_total': round(media_sel + media_adm, 1),
        'por_linha_selecao': tempo_por_linha_sel,
        'por_linha_admissao': tempo_por_linha_adm,
        'por_nivel': tempo_por_nivel,
        'evolucao_mensal': evolucao
    })

if __name__ == '__main__':
    app.run(debug=True)