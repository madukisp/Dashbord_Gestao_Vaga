import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(page_title="Dashboard de Indicadores RH", layout="wide", page_icon="📊")

# CSS customizado
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    # Lê o arquivo Base_Bi.xlsx da mesma pasta do projeto
    caminho_arquivo = os.path.join(os.path.dirname(__file__), 'Base_Bi.xlsx')
    df = pd.read_excel(caminho_arquivo)
    df = df.dropna(how='all')
    
    # Limpar espaços extras na coluna Nivel
    df['Nivel'] = df['Nivel'].apply(lambda x: str(x).strip() if pd.notna(x) else 'Não Classificado')
    
    # Limpar espaços extras na coluna LINHA DE CUIDADO
    df['LINHA DE CUIDADO'] = df['LINHA DE CUIDADO'].apply(lambda x: str(x).strip() if pd.notna(x) else 'Não Classificado')
    
    # Calcular tempo de fechamento em seleção (dias)
    df['Tempo Seleção (dias)'] = (df['DATA DE FECHAMENTO VAGA EM SELEÇÃO '] - df['DATA ABERTURA DA VAGA']).dt.days
    
    # Calcular tempo de admissão (dias)
    df['Tempo Admissão (dias)'] = (df['DATA DE INÍCIO SUBSTITUIÇÃO'] - df['DATA DE FECHAMENTO VAGA EM SELEÇÃO ']).dt.days
    
    return df

# Carregar dados
try:
    df = load_data()
    dados_carregados = True
except Exception as e:
    dados_carregados = False
    erro = str(e)

# Título
st.title("📊 Dashboard de Indicadores - Gestão de Vagas")
st.markdown("---")

if not dados_carregados:
    st.error(f"Erro ao carregar o arquivo Base_Bi.xlsx: {erro}")
    st.info("Certifique-se de que o arquivo 'Base_Bi.xlsx' está na mesma pasta do dashboard.")
    st.stop()

# Tabs principais
tab1, tab2, tab3 = st.tabs(["🎯 Vagas Trabalhadas", "🚪 Motivos de Desligamento", "⏱️ Tempo Médio de Fechamento"])

# Obter lista de níveis únicos (excluindo 'Não Classificado')
NIVEIS = [n for n in df['Nivel'].unique() if n != 'Não Classificado']

# Obter lista de linhas de cuidado únicas
LINHAS_CUIDADO = [lc for lc in df['LINHA DE CUIDADO'].unique() if lc != 'Não Classificado']

# ============ TAB 1: VAGAS TRABALHADAS ============
with tab1:
    st.header("Quantidade de Vagas Trabalhadas")
    
    # Criar coluna de Mês/Ano para filtro
    df['Mês/Ano'] = df['DATA ABERTURA DA VAGA'].dt.to_period('M').astype(str)
    meses_disponiveis = sorted(df['Mês/Ano'].dropna().unique())
    
    # Filtros
    col_filter1, col_filter2, col_filter3 = st.columns(3)
    with col_filter1:
        mes_selecionado = st.multiselect("Filtrar por Mês:", meses_disponiveis, default=meses_disponiveis, key='mes_vagas')
    with col_filter2:
        status_disponiveis = df['Status Vaga'].dropna().unique().tolist()
        status_selecionado = st.multiselect("Filtrar por Status:", status_disponiveis, default=status_disponiveis, key='status_vagas')
    with col_filter3:
        niveis_disponiveis = sorted(NIVEIS)
        nivel_selecionado = st.multiselect("Filtrar por Nível:", niveis_disponiveis, default=niveis_disponiveis, key='nivel_vagas')
    
    # Aplicar filtros
    df_filtrado = df.copy()
    if mes_selecionado:
        df_filtrado = df_filtrado[df_filtrado['Mês/Ano'].isin(mes_selecionado)]
    if status_selecionado:
        df_filtrado = df_filtrado[df_filtrado['Status Vaga'].isin(status_selecionado)]
    if nivel_selecionado:
        df_filtrado = df_filtrado[df_filtrado['Nivel'].isin(nivel_selecionado)]
    
    # Métricas principais por nível
    st.subheader("📈 Resumo por Nível")
    
    # Contagem por nível
    contagem_nivel = df_filtrado['Nivel'].value_counts()
    
    # Mostrar métricas em grid
    cols = st.columns(4)
    for i, nivel in enumerate(NIVEIS):
        with cols[i % 4]:
            qtd = contagem_nivel.get(nivel, 0)
            st.metric(label=nivel, value=qtd)
    
    # Total
    st.metric(label="**TOTAL GERAL**", value=len(df_filtrado))
    
    st.markdown("---")
    
    # Gráficos lado a lado
    col_graf1, col_graf2 = st.columns(2)
    
    with col_graf1:
        st.subheader("Por Nível")
        df_nivel = df_filtrado.groupby('Nivel').size().reset_index(name='Quantidade')
        df_nivel = df_nivel[df_nivel['Nivel'] != 'Não Classificado']
        if not df_nivel.empty:
            fig_nivel = px.pie(df_nivel, values='Quantidade', names='Nivel', 
                              color_discrete_sequence=px.colors.qualitative.Set2,
                              hole=0.4)
            fig_nivel.update_traces(textposition='inside', textinfo='percent+value')
            st.plotly_chart(fig_nivel, use_container_width=True)
        else:
            st.info("Sem dados para exibir")
    
    with col_graf2:
        st.subheader("Por Linha de Cuidado")
        df_linha = df_filtrado.groupby('LINHA DE CUIDADO').size().reset_index(name='Quantidade')
        df_linha = df_linha[df_linha['LINHA DE CUIDADO'] != 'Não Classificado']
        if not df_linha.empty:
            fig_linha = px.pie(df_linha, values='Quantidade', names='LINHA DE CUIDADO',
                              color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_linha.update_traces(textposition='inside', textinfo='percent+value')
            st.plotly_chart(fig_linha, use_container_width=True)
        else:
            st.info("Sem dados para exibir")
    
    # Tabela detalhada por Linha de Cuidado e Nível
    st.subheader("📋 Detalhamento: Vagas por Linha de Cuidado e Nível")
    df_cross = pd.crosstab(df_filtrado['LINHA DE CUIDADO'], df_filtrado['Nivel'], margins=True, margins_name='Total')
    st.dataframe(df_cross, use_container_width=True)
    
    # Gráfico de barras empilhadas
    st.subheader("📊 Distribuição por Linha de Cuidado e Nível")
    df_stack = df_filtrado[(df_filtrado['Nivel'] != 'Não Classificado') & (df_filtrado['LINHA DE CUIDADO'] != 'Não Classificado')].groupby(['LINHA DE CUIDADO', 'Nivel']).size().reset_index(name='Quantidade')
    if not df_stack.empty:
        fig_stack = px.bar(df_stack, x='LINHA DE CUIDADO', y='Quantidade', color='Nivel',
                          barmode='stack', color_discrete_sequence=px.colors.qualitative.Set2)
        fig_stack.update_layout(xaxis_title='Linha de Cuidado', yaxis_title='Quantidade de Vagas', xaxis_tickangle=-45)
        st.plotly_chart(fig_stack, use_container_width=True)

# ============ TAB 2: MOTIVOS DE DESLIGAMENTO ============
with tab2:
    st.header("Motivos de Desligamento")
    
    # Filtrar apenas registros com motivo de desligamento
    df_desl = df[df['MOTIVO DO DESLIGAMENTO'].notna()].copy()
    
    # Filtros
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        meses_desl = sorted(df_desl['Mês/Ano'].dropna().unique())
        mes_desl = st.multiselect("Filtrar por Mês:", meses_desl, default=meses_desl, key='mes_desl')
    with col_f2:
        linhas_desl = [lc for lc in df_desl['LINHA DE CUIDADO'].unique() if lc != 'Não Classificado']
        linha_desl = st.multiselect("Filtrar por Linha de Cuidado:", linhas_desl, default=linhas_desl, key='linha_desl')
    
    # Aplicar filtros
    if mes_desl:
        df_desl = df_desl[df_desl['Mês/Ano'].isin(mes_desl)]
    if linha_desl:
        df_desl = df_desl[df_desl['LINHA DE CUIDADO'].isin(linha_desl)]
    
    # ========== GRÁFICO GERAL - TODAS AS LINHAS DE CUIDADO ==========
    st.subheader("📊 Visão Geral - Todos os Motivos de Desligamento")
    motivos_geral = df_desl['MOTIVO DO DESLIGAMENTO'].value_counts().reset_index()
    motivos_geral.columns = ['Motivo', 'Quantidade']
    
    if not motivos_geral.empty:
        altura_geral = max(450, len(motivos_geral) * 35)
        
        fig_geral = px.bar(motivos_geral, x='Quantidade', y='Motivo', orientation='h',
                          color='Quantidade', color_continuous_scale='Viridis',
                          text='Quantidade')
        fig_geral.update_traces(textposition='outside', textfont_size=12)
        fig_geral.update_layout(
            yaxis={'categoryorder':'total ascending'},
            showlegend=False,
            height=altura_geral,
            margin=dict(r=60)
        )
        st.plotly_chart(fig_geral, use_container_width=True)
    
    st.markdown("---")
    
    # ========== DOIS GRÁFICOS PRINCIPAIS ==========
    st.subheader("🏥 Principais Linhas de Cuidado")
    col_ue, col_aps = st.columns(2)
    
    with col_ue:
        st.markdown("**🚑 Urgência e Emergência**")
        df_ue = df_desl[df_desl['LINHA DE CUIDADO'].str.contains('Urgência|Emergência', case=False, na=False)]
        motivos_ue = df_ue['MOTIVO DO DESLIGAMENTO'].value_counts().reset_index()
        motivos_ue.columns = ['Motivo', 'Quantidade']
        
        if not motivos_ue.empty:
            altura_ue = max(400, len(motivos_ue) * 35)
            
            fig_ue = px.bar(motivos_ue, x='Quantidade', y='Motivo', orientation='h',
                          color='Quantidade', color_continuous_scale='Reds',
                          text='Quantidade')
            fig_ue.update_traces(textposition='outside', textfont_size=12)
            fig_ue.update_layout(
                yaxis={'categoryorder':'total ascending'}, 
                showlegend=False,
                height=altura_ue,
                margin=dict(r=50)
            )
            st.plotly_chart(fig_ue, use_container_width=True)
        else:
            st.info("Sem dados de desligamento para Urgência e Emergência")
    
    with col_aps:
        st.markdown("**🏥 Atenção Básica**")
        # Filtrar linhas que contenham "Atenção Básica" ou "Atenção Primária"
        df_aps = df_desl[df_desl['LINHA DE CUIDADO'].str.contains('Atenção Básica|Atenção Primária', case=False, na=False)]
        motivos_aps = df_aps['MOTIVO DO DESLIGAMENTO'].value_counts().reset_index()
        motivos_aps.columns = ['Motivo', 'Quantidade']
        
        if not motivos_aps.empty:
            # Calcular altura dinâmica baseada na quantidade de motivos
            altura_aps = max(400, len(motivos_aps) * 35)
            
            fig_aps = px.bar(motivos_aps, x='Quantidade', y='Motivo', orientation='h',
                           color='Quantidade', color_continuous_scale='Blues',
                           text='Quantidade')
            fig_aps.update_traces(textposition='outside', textfont_size=12)
            fig_aps.update_layout(
                yaxis={'categoryorder':'total ascending'}, 
                showlegend=False,
                height=altura_aps,
                margin=dict(r=50)
            )
            st.plotly_chart(fig_aps, use_container_width=True)
        else:
            st.info("Sem dados de desligamento para Atenção Básica")
    
    st.markdown("---")
    
    # ========== OUTRAS LINHAS DE CUIDADO ==========
    st.subheader("📋 Outras Linhas de Cuidado")
    
    # Filtrar linhas que NÃO são Urgência/Emergência nem Atenção Básica/Primária
    df_outras = df_desl[
        ~df_desl['LINHA DE CUIDADO'].str.contains('Urgência|Emergência|Atenção Básica|Atenção Primária', case=False, na=False)
    ]
    
    # Obter linhas de cuidado únicas das outras e ordenar por quantidade de registros
    outras_linhas = df_outras['LINHA DE CUIDADO'].value_counts().index.tolist()
    outras_linhas = [lc for lc in outras_linhas if lc != 'Não Classificado']
    
    if len(outras_linhas) > 0:
        # Calcular altura máxima para alinhar os gráficos
        max_motivos = max([
            len(df_outras[df_outras['LINHA DE CUIDADO'] == linha]['MOTIVO DO DESLIGAMENTO'].unique())
            for linha in outras_linhas
        ])
        altura_padrao = max(300, max_motivos * 30)
        
        # Criar grid de gráficos menores (4 por linha para melhor alinhamento)
        num_cols = 4
        for i in range(0, len(outras_linhas), num_cols):
            cols_outras = st.columns(num_cols)
            for j, col in enumerate(cols_outras):
                idx = i + j
                if idx < len(outras_linhas):
                    linha = outras_linhas[idx]
                    with col:
                        st.markdown(f"**{linha}**")
                        df_linha_atual = df_outras[df_outras['LINHA DE CUIDADO'] == linha]
                        motivos_linha = df_linha_atual['MOTIVO DO DESLIGAMENTO'].value_counts().reset_index()
                        motivos_linha.columns = ['Motivo', 'Quantidade']
                        
                        if not motivos_linha.empty:
                            fig_linha = px.bar(motivos_linha, x='Quantidade', y='Motivo', orientation='h',
                                             color='Quantidade', color_continuous_scale='Teal',
                                             text='Quantidade')
                            fig_linha.update_traces(textposition='outside', textfont_size=9)
                            fig_linha.update_layout(
                                yaxis={'categoryorder':'total ascending'},
                                showlegend=False,
                                height=altura_padrao,
                                margin=dict(l=5, r=35, t=5, b=5),
                                coloraxis_showscale=False,
                                xaxis_title='',
                                yaxis_title=''
                            )
                            st.plotly_chart(fig_linha, use_container_width=True)
                        else:
                            st.info("Sem dados")
    else:
        st.info("Sem dados de desligamento para outras linhas de cuidado")
    
    st.markdown("---")
    
    # Comparativo geral por Linha de Cuidado
    st.subheader("📊 Comparativo Geral - Top 5 Motivos por Linha de Cuidado")
    df_comp = df_desl.groupby(['LINHA DE CUIDADO', 'MOTIVO DO DESLIGAMENTO']).size().reset_index(name='Quantidade')
    top_motivos = df_desl['MOTIVO DO DESLIGAMENTO'].value_counts().head(5).index.tolist()
    df_comp_top = df_comp[df_comp['MOTIVO DO DESLIGAMENTO'].isin(top_motivos)]
    
    if not df_comp_top.empty:
        fig_comp = px.bar(df_comp_top, x='MOTIVO DO DESLIGAMENTO', y='Quantidade', color='LINHA DE CUIDADO',
                         barmode='group', color_discrete_sequence=px.colors.qualitative.Set1)
        fig_comp.update_layout(xaxis_title='Motivo de Desligamento', xaxis_tickangle=-45)
        st.plotly_chart(fig_comp, use_container_width=True)

# ============ TAB 3: TEMPO MÉDIO DE FECHAMENTO ============
with tab3:
    st.header("Tempo Médio de Fechamento")
    
    # Filtros
    col_tf1, col_tf2 = st.columns(2)
    with col_tf1:
        meses_tempo = sorted(df['Mês/Ano'].dropna().unique())
        mes_tempo = st.multiselect("Filtrar por Mês:", meses_tempo, default=meses_tempo, key='mes_tempo')
    with col_tf2:
        linhas_tempo = [lc for lc in df['LINHA DE CUIDADO'].unique() if lc != 'Não Classificado']
        linha_tempo = st.multiselect("Filtrar por Linha de Cuidado:", linhas_tempo, default=linhas_tempo, key='linha_tempo')
    
    # Aplicar filtros
    df_tempo = df.copy()
    if mes_tempo:
        df_tempo = df_tempo[df_tempo['Mês/Ano'].isin(mes_tempo)]
    if linha_tempo:
        df_tempo = df_tempo[df_tempo['LINHA DE CUIDADO'].isin(linha_tempo)]
    
    # Métricas principais
    st.subheader("⏱️ Indicadores de Tempo")
    
    col_m1, col_m2, col_m3 = st.columns(3)
    
    # Tempo médio em seleção
    tempo_selecao = df_tempo['Tempo Seleção (dias)'].dropna()
    tempo_selecao = tempo_selecao[tempo_selecao >= 0]
    
    # Tempo médio em admissão
    tempo_admissao = df_tempo['Tempo Admissão (dias)'].dropna()
    tempo_admissao = tempo_admissao[tempo_admissao >= 0]
    
    with col_m1:
        media_sel = tempo_selecao.mean() if len(tempo_selecao) > 0 else 0
        st.metric(label="Tempo Médio em Seleção", value=f"{media_sel:.1f} dias", 
                 help="Da abertura da vaga até fechamento em seleção")
    
    with col_m2:
        media_adm = tempo_admissao.mean() if len(tempo_admissao) > 0 else 0
        st.metric(label="Tempo Médio em Admissão", value=f"{media_adm:.1f} dias",
                 help="Do fechamento em seleção até início do colaborador")
    
    with col_m3:
        tempo_total = media_sel + media_adm
        st.metric(label="Tempo Total Médio", value=f"{tempo_total:.1f} dias")
    
    st.markdown("---")
    
    # Gráficos por Linha de Cuidado
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.subheader("📊 Tempo Médio de Seleção por Linha de Cuidado")
        df_sel_linha = df_tempo[df_tempo['Tempo Seleção (dias)'] >= 0].groupby('LINHA DE CUIDADO')['Tempo Seleção (dias)'].mean().reset_index()
        df_sel_linha.columns = ['Linha de Cuidado', 'Tempo Médio (dias)']
        df_sel_linha = df_sel_linha[df_sel_linha['Linha de Cuidado'] != 'Não Classificado']
        
        if not df_sel_linha.empty:
            fig_sel = px.bar(df_sel_linha, x='Linha de Cuidado', y='Tempo Médio (dias)',
                           color='Tempo Médio (dias)', color_continuous_scale='Viridis')
            fig_sel.update_layout(showlegend=False, xaxis_tickangle=-45)
            st.plotly_chart(fig_sel, use_container_width=True)
    
    with col_g2:
        st.subheader("📊 Tempo Médio de Admissão por Linha de Cuidado")
        df_adm_linha = df_tempo[df_tempo['Tempo Admissão (dias)'] >= 0].groupby('LINHA DE CUIDADO')['Tempo Admissão (dias)'].mean().reset_index()
        df_adm_linha.columns = ['Linha de Cuidado', 'Tempo Médio (dias)']
        df_adm_linha = df_adm_linha[df_adm_linha['Linha de Cuidado'] != 'Não Classificado']
        
        if not df_adm_linha.empty:
            fig_adm = px.bar(df_adm_linha, x='Linha de Cuidado', y='Tempo Médio (dias)',
                           color='Tempo Médio (dias)', color_continuous_scale='Plasma')
            fig_adm.update_layout(showlegend=False, xaxis_tickangle=-45)
            st.plotly_chart(fig_adm, use_container_width=True)
    
    # Detalhamento por nível
    st.subheader("📋 Tempo Médio por Nível")
    
    df_tempo_nivel = df_tempo[df_tempo['Nivel'].isin(NIVEIS)]
    
    tempo_por_nivel = df_tempo_nivel.groupby('Nivel').agg({
        'Tempo Seleção (dias)': lambda x: x[x >= 0].mean(),
        'Tempo Admissão (dias)': lambda x: x[x >= 0].mean()
    }).reset_index()
    tempo_por_nivel = tempo_por_nivel.fillna(0)
    tempo_por_nivel['Tempo Total (dias)'] = tempo_por_nivel['Tempo Seleção (dias)'] + tempo_por_nivel['Tempo Admissão (dias)']
    
    if not tempo_por_nivel.empty:
        st.dataframe(tempo_por_nivel.round(1), use_container_width=True)
        
        # Gráfico de barras agrupadas
        fig_tempo = go.Figure()
        fig_tempo.add_trace(go.Bar(name='Seleção', x=tempo_por_nivel['Nivel'], y=tempo_por_nivel['Tempo Seleção (dias)'], marker_color='#667eea'))
        fig_tempo.add_trace(go.Bar(name='Admissão', x=tempo_por_nivel['Nivel'], y=tempo_por_nivel['Tempo Admissão (dias)'], marker_color='#f093fb'))
        fig_tempo.update_layout(barmode='group', xaxis_title='Nível', yaxis_title='Dias')
        st.plotly_chart(fig_tempo, use_container_width=True)
    
    # Evolução mensal
    st.subheader("📈 Evolução Mensal do Tempo de Fechamento")
    
    tempo_mensal = df_tempo.groupby('Mês/Ano').agg({
        'Tempo Seleção (dias)': lambda x: x[x >= 0].mean(),
        'Tempo Admissão (dias)': lambda x: x[x >= 0].mean()
    }).reset_index().sort_values('Mês/Ano')
    
    if not tempo_mensal.empty:
        fig_linha = go.Figure()
        fig_linha.add_trace(go.Scatter(x=tempo_mensal['Mês/Ano'], y=tempo_mensal['Tempo Seleção (dias)'],
                                       mode='lines+markers', name='Seleção', line=dict(color='#667eea', width=3)))
        fig_linha.add_trace(go.Scatter(x=tempo_mensal['Mês/Ano'], y=tempo_mensal['Tempo Admissão (dias)'],
                                       mode='lines+markers', name='Admissão', line=dict(color='#f093fb', width=3)))
        fig_linha.update_layout(xaxis_title='Período', yaxis_title='Dias', hovermode='x unified')
        st.plotly_chart(fig_linha, use_container_width=True)

# Rodapé
st.markdown("---")
st.caption("📊 Dashboard de Indicadores RH")