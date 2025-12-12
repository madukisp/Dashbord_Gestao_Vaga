import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

st.set_page_config(
    page_title="Dashboard RH - Análise de Colaboradores", layout="wide", page_icon="📊"
)

# CSS customizado
st.markdown(
    """
<style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        font-weight: 600;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ============ CONFIGURAÇÕES ============

# Classificação de Níveis (baseado na imagem fornecida)
NIVEIS_HIERARQUIA = {
    "DIRETOR": "DIRETOR",
    "ASSESSOR": "ASSESSOR",
    "SUPERVISOR": "SUPERVISOR",
    "GERENTE": "GERENTE",
    "COORDENADOR": "COORDENADOR",
    "TECNICO": "TÉCNICO",
    "MEDICO": "MÉDICOS",
    "ENFERMAGEM": "ENFERMAGEM",
    "MULTIDISCIPLINAR": "MULTIDISCIPLINAR",
    "ADMINISTRATIVO": "ADMINISTRATIVO",
    "OPERACIONAL": "OPERACIONAL",
    "APRENDIZ": "APRENDIZ",
}

# Mapeamento de cidades por Nome Fantasia
CIDADES_MAPA = {
    "SBCD - AME CRI ZN": {
        "cidade": "São Paulo",
        "estado": "SP",
        "lat": -23.5505,
        "lon": -46.6333,
    },
    "SBCD - ANDRADINA AME": {
        "cidade": "Andradina",
        "estado": "SP",
        "lat": -20.8958,
        "lon": -51.3786,
    },
    "SBCD - CANDIDO FERRAZ (HRSCF)": {
        "cidade": "São Raimundo Nonato",
        "estado": "PI",
        "lat": -9.0115,
        "lon": -42.6983,
    },
    "SBCD - CENTRAL DE EXAMES DE PICOS": {
        "cidade": "Picos",
        "estado": "PI",
        "lat": -7.0767,
        "lon": -41.4669,
    },
    "SBCD - CENTRAL DE EXAMES VALENÇA": {
        "cidade": "Valença do Piauí",
        "estado": "PI",
        "lat": -6.4058,
        "lon": -41.7461,
    },
    "SBCD - CER II SAO JOAO DO PIAUI": {
        "cidade": "São João do Piauí",
        "estado": "PI",
        "lat": -8.3589,
        "lon": -42.2447,
    },
    "SBCD - CETEA - PI": {
        "cidade": "Teresina",
        "estado": "PI",
        "lat": -5.0919,
        "lon": -42.8034,
    },
    "SBCD - CUBATÃO - APS": {
        "cidade": "Cubatão",
        "estado": "SP",
        "lat": -23.8950,
        "lon": -46.4253,
    },
    "SBCD - GARÇA": {
        "cidade": "Garça",
        "estado": "SP",
        "lat": -22.2111,
        "lon": -49.6522,
    },
    "SBCD - HMC - CUBATÃO - NOVO": {
        "cidade": "Cubatão",
        "estado": "SP",
        "lat": -23.8950,
        "lon": -46.4253,
    },
    "SBCD - HOSP ITURAMA": {
        "cidade": "Iturama",
        "estado": "MG",
        "lat": -19.7292,
        "lon": -50.1950,
    },
    "SBCD - HOSP JUSTINO LUZ": {
        "cidade": "Picos",
        "estado": "PI",
        "lat": -7.0767,
        "lon": -41.4669,
    },
    "SBCD - HOSP PICOS": {
        "cidade": "Picos",
        "estado": "PI",
        "lat": -7.0767,
        "lon": -41.4669,
    },
    "SBCD - HOSP REG EUSTAQUIO PORTELA": {
        "cidade": "São Paulo",
        "estado": "SP",
        "lat": -23.5505,
        "lon": -46.6333,
    },
    "SBCD - ITU RT": {
        "cidade": "Itu",
        "estado": "SP",
        "lat": -23.2642,
        "lon": -47.2997,
    },
    "SBCD - MOCAMBINHO": {
        "cidade": "São Paulo",
        "estado": "SP",
        "lat": -23.5505,
        "lon": -46.6333,
    },
    "SBCD - PAI ZN": {
        "cidade": "São Paulo",
        "estado": "SP",
        "lat": -23.5505,
        "lon": -46.6333,
    },
    "SBCD - PROMISSÃO AME": {
        "cidade": "Promissão",
        "estado": "SP",
        "lat": -21.5372,
        "lon": -49.8581,
    },
    "SBCD - PRONTO ATENDIMENTO SAO VICENTE DE PAULO": {
        "cidade": "São Paulo",
        "estado": "SP",
        "lat": -23.5505,
        "lon": -46.6333,
    },
    "SBCD - REDE ASSIST. NORTE-SP": {
        "cidade": "São Paulo",
        "estado": "SP",
        "lat": -23.5505,
        "lon": -46.6333,
    },
    "SBCD - SEDE CORPORATIVA TERESINA": {
        "cidade": "Teresina",
        "estado": "PI",
        "lat": -5.0919,
        "lon": -42.8034,
    },
    "SBCD - UPA DE SÃO RAIMUNDO NONATO": {
        "cidade": "São Raimundo Nonato",
        "estado": "PI",
        "lat": -9.0115,
        "lon": -42.6983,
    },
    "SBCD - UPA DR THELMO JACAREÍ": {
        "cidade": "Jacareí",
        "estado": "SP",
        "lat": -23.3054,
        "lon": -45.9658,
    },
    "SBCD - UPA ITU": {
        "cidade": "Itu",
        "estado": "SP",
        "lat": -23.2642,
        "lon": -47.2997,
    },
    "SBCD - UPA PICOS": {
        "cidade": "Picos",
        "estado": "PI",
        "lat": -7.0767,
        "lon": -41.4669,
    },
}

# ============ FUNÇÕES DE CLASSIFICAÇÃO ============


def classificar_nivel(cargo):
    """Classifica o cargo em um nível hierárquico"""
    if pd.isna(cargo):
        return "NÃO CLASSIFICADO"

    cargo_upper = str(cargo).upper()

    for palavra_chave, nivel in NIVEIS_HIERARQUIA.items():
        if palavra_chave in cargo_upper:
            return nivel

    return "OUTROS"


def classificar_linha_cuidado(nome_fantasia, centro_custo):
    """Classifica a linha de cuidado baseado no nome fantasia e centro de custo"""
    texto = f"{nome_fantasia} {centro_custo}".upper()

    # Ordem de prioridade na classificação
    if any(palavra in texto for palavra in ["AME", "UPA", "CER"]):
        return "URGÊNCIA E EMERGÊNCIA"
    elif any(palavra in texto for palavra in ["CETEA", "APS", "GARÇA", "NORTE"]):
        return "APS"
    elif any(
        palavra in texto
        for palavra in ["HOSP", "HMC", "HRSCF", "PRONTO ATENDIMENTO", "MOCAMBINHO"]
    ):
        return "HOSPITAIS"
    elif any(palavra in texto for palavra in ["ITU RT", "SEDE CORPORATIVA"]):
        return "SEDE CORPORATIVA"
    elif "PAI" in texto:
        return "SAÚDE DO IDOSO"
    elif "CER" in texto and "UPA" not in texto and "AME" not in texto:
        return "PROGRAMAS"
    else:
        return "OUTROS"


def limpar_tipo_rescisao(tipo_rescisao):
    """Remove prefixo numérico (ex: '01-', '14-') do tipo de rescisão"""
    if pd.isna(tipo_rescisao):
        return tipo_rescisao

    tipo_str = str(tipo_rescisao)
    # Remove padrão: número(s)-
    import re

    return re.sub(r"^\d+-", "", tipo_str).strip()


def agrupar_tipos_rescisao(tipo_rescisao):
    """Agrupa tipos de rescisão similares"""
    if pd.isna(tipo_rescisao):
        return tipo_rescisao

    tipo_upper = str(tipo_rescisao).upper()

    # Agrupamentos solicitados:
    # 6+14 = PEDIDO ANTES TERMINO + PEDIDO DE DEMISSÃO
    if "PEDIDO" in tipo_upper and (
        "DEMISSÃO" in tipo_upper or "ANTES TERMINO" in tipo_upper
    ):
        return "PEDIDO DE DEMISSÃO"

    # 1+2 = DISPENSA SEM JUSTA CAUSA AVISO INDENIZADO + TRABALHADO
    if "DISPENSA SEM JUSTA CAUSA" in tipo_upper:
        return "DISPENSA SEM JUSTA CAUSA"

    # 5+3 = DISPENSA TERMINO CONTRATO EXPERIENCIA + ANTES TERMINO CONTRATO
    if "DISPENSA" in tipo_upper and (
        "TERMINO CONTRATO" in tipo_upper or "ANTES TERMINO" in tipo_upper
    ):
        return "DISPENSA TERMINO CONTRATO"

    return tipo_rescisao


# ============ CARREGAMENTO E PROCESSAMENTO DE DADOS ============


@st.cache_data
def load_and_process_data():
    """Carrega e processa os dados do arquivo Excel oris.xlsx"""

    # Caminho do arquivo
    caminho_arquivo = os.path.join(os.path.dirname(__file__), "oris.xlsx")

    if not os.path.exists(caminho_arquivo):
        st.error(f"❌ Arquivo 'oris.xlsx' não encontrado na pasta do projeto!")
        st.info(
            "Certifique-se de que o arquivo 'oris.xlsx' está na mesma pasta do arquivo dashboard_rh.py"
        )
        st.stop()

    # Carregar Excel (cabeçalho na linha 8 = header=7 pois é zero-indexed)
    df = pd.read_excel(caminho_arquivo, header=7)

    # Remover linhas completamente vazias
    df = df.dropna(how="all")

    # Converter datas
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
            df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=True)

    # Classificações
    df["Nivel"] = df["Cargo"].apply(classificar_nivel)
    df["Linha de Cuidado"] = df.apply(
        lambda x: classificar_linha_cuidado(
            x["Nome Fantasia"] if "Nome Fantasia" in df.columns else "",
            x["Centro custo"] if "Centro custo" in df.columns else "",
        ),
        axis=1,
    )

    # Limpar e agrupar tipos de rescisão
    if "Tipo Rescisão" in df.columns:
        df["Tipo Rescisão"] = df["Tipo Rescisão"].apply(limpar_tipo_rescisao)
        df["Tipo Rescisão"] = df["Tipo Rescisão"].apply(agrupar_tipos_rescisao)

    # Calcular tempo de permanência (em dias)
    df["Tempo Permanência (dias)"] = (df["Dt Rescisão"] - df["Dt Admissão"]).dt.days

    # Criar coluna Mês/Ano para admissões e rescisões
    df["Mês/Ano Admissão"] = df["Dt Admissão"].dt.to_period("M").astype(str)
    df["Mês/Ano Rescisão"] = df["Dt Rescisão"].dt.to_period("M").astype(str)

    # Identificar demissões em experiência
    df["Demitido 45 dias"] = (df["Tempo Permanência (dias)"] <= 45) & (
        df["Demitido"] == "Sim"
    )
    df["Demitido 90 dias"] = (
        (df["Tempo Permanência (dias)"] > 45)
        & (df["Tempo Permanência (dias)"] <= 90)
        & (df["Demitido"] == "Sim")
    )

    return df


def calcular_substituicoes(df, data_inicio, data_fim):
    """Calcula substituições: mesma vaga preenchida após demissão por OUTRA pessoa"""

    # Filtrar demissões no período
    demissoes = df[
        (df["Demitido"] == "Sim")
        & (df["Dt Rescisão"] >= data_inicio)
        & (df["Dt Rescisão"] <= data_fim)
    ].copy()

    substituicoes = []
    ids_usados = set()  # Para evitar contar a mesma substituição múltiplas vezes

    for idx, demissao in demissoes.iterrows():
        # Buscar admissões posteriores com mesmo cargo, centro custo e escala
        # MAS com PESSOA DIFERENTE (ID diferente e Nome diferente)
        candidatos = df[
            (df["Dt Admissão"] >= demissao["Dt Rescisão"])
            & (df["ID"] != demissao["ID"])  # ID diferente
            & (df["Nome"] != demissao["Nome"])  # Nome diferente
            & (df["Cargo"] == demissao["Cargo"])
            & (df["Centro custo"] == demissao["Centro custo"])
            & (df["Dt Início Escala"] == demissao["Dt Início Escala"])
            & (~df["ID"].isin(ids_usados))  # Não usar a mesma pessoa novamente
        ].copy()

        if len(candidatos) > 0:
            # Ordenar por data de admissão e pegar a mais próxima
            candidatos = candidatos.sort_values("Dt Admissão")
            candidato = candidatos.iloc[0]
            dias_substituicao = (
                candidato["Dt Admissão"] - demissao["Dt Rescisão"]
            ).days

            # Adicionar ID do candidato aos IDs usados
            ids_usados.add(candidato["ID"])

            substituicoes.append(
                {
                    "Nome Saída": demissao["Nome"],
                    "Nome Entrada": candidato["Nome"],
                    "Cargo": demissao["Cargo"],
                    "Centro Custo": demissao["Centro custo"],
                    "Data Saída": demissao["Dt Rescisão"],
                    "Data Entrada": candidato["Dt Admissão"],
                    "Dias Substituição": dias_substituicao,
                    "Escala": demissao["Dt Início Escala"],
                }
            )

    return pd.DataFrame(substituicoes)


# ============ INTERFACE PRINCIPAL ============

st.title("📊 Dashboard RH - Análise de Colaboradores")

# Carregar dados automaticamente
try:
    df = load_and_process_data()
    st.success(f"✅ Dados carregados: {len(df)} colaboradores")
except Exception as e:
    st.error(f"❌ Erro ao carregar arquivo oris.xlsx: {e}")
    st.stop()

# ============ SIDEBAR: FILTROS E MAPA ============

st.sidebar.header("🎯 Filtros")

# Filtro de Nome Fantasia
empresas_disponiveis = ["TODAS"] + sorted(df["Nome Fantasia"].unique().tolist())
empresa_selecionada = st.sidebar.selectbox("🏢 Empresa:", empresas_disponiveis)

# Filtrar dados por empresa primeiro
if empresa_selecionada != "TODAS":
    df_temp = df[df["Nome Fantasia"] == empresa_selecionada].copy()
else:
    df_temp = df.copy()

# Filtro de Centro de Custo (baseado na empresa selecionada)
centros_custo_disponiveis = ["TODOS"] + sorted(
    df_temp["Centro custo"].dropna().unique().tolist()
)
centro_custo_selecionado = st.sidebar.selectbox(
    "🏥 Centro de Custo:", centros_custo_disponiveis
)

# Aplicar filtro de centro de custo
if centro_custo_selecionado != "TODOS":
    df_filtrado = df_temp[df_temp["Centro custo"] == centro_custo_selecionado].copy()
else:
    df_filtrado = df_temp.copy()

# Mostrar linha de cuidado da empresa selecionada
if empresa_selecionada != "TODAS" and len(df_filtrado) > 0:
    linha_cuidado_empresa = df_filtrado["Linha de Cuidado"].mode()[
        0
    ]  # Pega a linha mais comum
    st.markdown(f"### 🏥 Linha de Cuidado: **{linha_cuidado_empresa}**")

st.markdown("---")

# Mapa da região
st.sidebar.markdown("---")
st.sidebar.subheader("🗺️ Localização")

if empresa_selecionada != "TODAS" and empresa_selecionada in CIDADES_MAPA:
    cidade_info = CIDADES_MAPA[empresa_selecionada]
    st.sidebar.markdown(f"**📍 {cidade_info['cidade']}, {cidade_info['estado']}**")

    # Criar mapa simples
    mapa_df = pd.DataFrame([cidade_info])
    st.sidebar.map(mapa_df[["lat", "lon"]], zoom=10)
elif empresa_selecionada == "TODAS":
    st.sidebar.info("Selecione uma empresa para ver a localização no mapa")
else:
    st.sidebar.warning("Localização não cadastrada para esta empresa")

# Filtro de período
st.sidebar.markdown("---")
st.sidebar.subheader("📅 Período de Análise")

# Definir período padrão (últimos 6 meses)
data_max = df_filtrado["Dt Admissão"].max()
data_min_padrao = data_max - timedelta(days=180)
data_min_total = df_filtrado["Dt Admissão"].min()

periodo_inicio = st.sidebar.date_input(
    "Data Início:",
    value=data_min_padrao,
    min_value=data_min_total,
    max_value=data_max,
    format="DD/MM/YYYY",
)

periodo_fim = st.sidebar.date_input(
    "Data Fim:",
    value=data_max,
    min_value=data_min_total,
    max_value=data_max,
    format="DD/MM/YYYY",
)

# Converter para datetime
periodo_inicio = pd.to_datetime(periodo_inicio, dayfirst=True)
periodo_fim = pd.to_datetime(periodo_fim, dayfirst=True)

# ============ MÉTRICAS GERAIS ============

col1, col2, col3, col4 = st.columns(4)

# Admissões no período
admissoes_periodo = df_filtrado[
    (df_filtrado["Dt Admissão"] >= periodo_inicio)
    & (df_filtrado["Dt Admissão"] <= periodo_fim)
]

# Demissões no período
demissoes_periodo = df_filtrado[
    (df_filtrado["Demitido"] == "Sim")
    & (df_filtrado["Dt Rescisão"] >= periodo_inicio)
    & (df_filtrado["Dt Rescisão"] <= periodo_fim)
]

# Calcular substituições
df_substituicoes = calcular_substituicoes(df_filtrado, periodo_inicio, periodo_fim)

with col1:
    st.metric("👥 Admissões", len(admissoes_periodo))

with col2:
    st.metric("🚪 Demissões", len(demissoes_periodo))

with col3:
    saldo = len(admissoes_periodo) - len(demissoes_periodo)
    st.metric("📊 Saldo", saldo, delta=f"{saldo:+d}")

with col4:
    taxa_sub = (
        (len(df_substituicoes) / len(demissoes_periodo) * 100)
        if len(demissoes_periodo) > 0
        else 0
    )
    st.metric("🔄 Taxa Substituição", f"{taxa_sub:.1f}%")

st.markdown("---")

# ============ TABS PRINCIPAIS ============

tab1, tab2, tab3 = st.tabs(
    ["📈 Movimentações", "🚪 Motivos de Desligamento", "⏱️ Análise de Permanência"]
)

# ============ TAB 1: MOVIMENTAÇÕES ============
with tab1:
    st.header("Análise de Movimentações")

    # Subtabs
    subtab1, subtab2, subtab3 = st.tabs(["Admissões", "Demissões", "Substituições"])

    # SUBTAB: ADMISSÕES
    with subtab1:
        st.subheader("📈 Admissões no Período")

        col_a1, col_a2 = st.columns(2)

        with col_a1:
            st.markdown("**Por Nível**")
            adm_nivel = admissoes_periodo["Nivel"].value_counts().reset_index()
            adm_nivel.columns = ["Nivel", "Quantidade"]

            if not adm_nivel.empty:
                fig_adm_nivel = px.pie(
                    adm_nivel,
                    values="Quantidade",
                    names="Nivel",
                    color_discrete_sequence=px.colors.qualitative.Set2,
                    hole=0.4,
                )
                fig_adm_nivel.update_traces(
                    textposition="inside", textinfo="percent+value"
                )
                st.plotly_chart(fig_adm_nivel, use_container_width=True)
            else:
                st.info("Sem dados de admissões")

        with col_a2:
            st.markdown("**Por Linha de Cuidado**")
            adm_linha = (
                admissoes_periodo["Linha de Cuidado"].value_counts().reset_index()
            )
            adm_linha.columns = ["Linha de Cuidado", "Quantidade"]

            if not adm_linha.empty:
                fig_adm_linha = px.pie(
                    adm_linha,
                    values="Quantidade",
                    names="Linha de Cuidado",
                    color_discrete_sequence=px.colors.qualitative.Pastel,
                )
                fig_adm_linha.update_traces(
                    textposition="inside", textinfo="percent+value"
                )
                st.plotly_chart(fig_adm_linha, use_container_width=True)
            else:
                st.info("Sem dados de admissões")

        # Evolução mensal de admissões
        st.markdown("---")
        st.subheader("📊 Evolução Mensal de Admissões")

        adm_mensal = (
            admissoes_periodo.groupby("Mês/Ano Admissão")
            .size()
            .reset_index(name="Quantidade")
        )
        adm_mensal = adm_mensal.sort_values("Mês/Ano Admissão")

        if not adm_mensal.empty:
            # Converter para datetime para formatação correta no gráfico
            adm_mensal["Data_Plot"] = pd.to_datetime(
                adm_mensal["Mês/Ano Admissão"], format="%Y-%m"
            )

            fig_adm_mensal = px.line(
                adm_mensal,
                x="Data_Plot",
                y="Quantidade",
                markers=True,
                line_shape="spline",
            )
            fig_adm_mensal.update_traces(line_color="#667eea", line_width=3)
            fig_adm_mensal.update_layout(xaxis_title="Período", yaxis_title="Admissões")
            fig_adm_mensal.update_xaxes(tickformat="%m/%Y")
            st.plotly_chart(fig_adm_mensal, use_container_width=True)

    # SUBTAB: DEMISSÕES
    with subtab2:
        st.subheader("📉 Demissões no Período")

        col_d1, col_d2 = st.columns(2)

        with col_d1:
            st.markdown("**Por Nível**")
            dem_nivel = demissoes_periodo["Nivel"].value_counts().reset_index()
            dem_nivel.columns = ["Nivel", "Quantidade"]

            if not dem_nivel.empty:
                fig_dem_nivel = px.pie(
                    dem_nivel,
                    values="Quantidade",
                    names="Nivel",
                    color_discrete_sequence=px.colors.qualitative.Set3,
                    hole=0.4,
                )
                fig_dem_nivel.update_traces(
                    textposition="inside", textinfo="percent+value"
                )
                st.plotly_chart(fig_dem_nivel, use_container_width=True)
            else:
                st.info("Sem dados de demissões")

        with col_d2:
            st.markdown("**Por Linha de Cuidado**")
            dem_linha = (
                demissoes_periodo["Linha de Cuidado"].value_counts().reset_index()
            )
            dem_linha.columns = ["Linha de Cuidado", "Quantidade"]

            if not dem_linha.empty:
                fig_dem_linha = px.pie(
                    dem_linha,
                    values="Quantidade",
                    names="Linha de Cuidado",
                    color_discrete_sequence=px.colors.qualitative.Vivid,
                )
                fig_dem_linha.update_traces(
                    textposition="inside", textinfo="percent+value"
                )
                st.plotly_chart(fig_dem_linha, use_container_width=True)
            else:
                st.info("Sem dados de demissões")

        # Evolução mensal de demissões
        st.markdown("---")
        st.subheader("📊 Evolução Mensal de Demissões")

        dem_mensal = (
            demissoes_periodo.groupby("Mês/Ano Rescisão")
            .size()
            .reset_index(name="Quantidade")
        )
        dem_mensal = dem_mensal.sort_values("Mês/Ano Rescisão")

        if not dem_mensal.empty:
            # Converter para datetime para formatação correta no gráfico
            dem_mensal["Data_Plot"] = pd.to_datetime(
                dem_mensal["Mês/Ano Rescisão"], format="%Y-%m"
            )

            fig_dem_mensal = px.line(
                dem_mensal,
                x="Data_Plot",
                y="Quantidade",
                markers=True,
                line_shape="spline",
            )
            fig_dem_mensal.update_traces(line_color="#f093fb", line_width=3)
            fig_dem_mensal.update_layout(xaxis_title="Período", yaxis_title="Demissões")
            fig_dem_mensal.update_xaxes(tickformat="%m/%Y")
            st.plotly_chart(fig_dem_mensal, use_container_width=True)

    # SUBTAB: SUBSTITUIÇÕES
    with subtab3:
        st.subheader("🔄 Análise de Substituições")

        if len(df_substituicoes) > 0:
            col_s1, col_s2 = st.columns(2)

            with col_s1:
                st.metric("✅ Vagas Substituídas", len(df_substituicoes))
                st.metric(
                    "⏱️ Tempo Médio de Substituição",
                    f"{df_substituicoes['Dias Substituição'].mean():.1f} dias",
                )

            with col_s2:
                vagas_nao_substituidas = len(demissoes_periodo) - len(df_substituicoes)
                st.metric("❌ Vagas Não Substituídas", vagas_nao_substituidas)
                st.metric("📊 Taxa de Substituição", f"{taxa_sub:.1f}%")

            # Gráfico de pizza
            st.markdown("---")
            dados_sub = pd.DataFrame(
                {
                    "Status": ["Substituídas", "Não Substituídas"],
                    "Quantidade": [len(df_substituicoes), vagas_nao_substituidas],
                }
            )

            fig_sub = px.pie(
                dados_sub,
                values="Quantidade",
                names="Status",
                color_discrete_sequence=["#4CAF50", "#FF5252"],
                hole=0.4,
            )
            fig_sub.update_traces(textposition="inside", textinfo="percent+value")
            st.plotly_chart(fig_sub, use_container_width=True)

            # Tabela detalhada
            st.markdown("---")
            st.subheader("📋 Detalhamento de Substituições")

            # Formatar datas para exibição (DD/MM/YYYY)
            df_display = df_substituicoes.copy()
            if "Data Saída" in df_display.columns:
                df_display["Data Saída"] = pd.to_datetime(
                    df_display["Data Saída"], dayfirst=True
                ).dt.strftime("%d/%m/%Y")
            if "Data Entrada" in df_display.columns:
                df_display["Data Entrada"] = pd.to_datetime(
                    df_display["Data Entrada"], dayfirst=True
                ).dt.strftime("%d/%m/%Y")
            if "Escala" in df_display.columns:
                df_display["Escala"] = pd.to_datetime(
                    df_display["Escala"], dayfirst=True
                ).dt.strftime("%d/%m/%Y")

            st.dataframe(df_display, use_container_width=True)
        else:
            st.info("Nenhuma substituição identificada no período")

# ============ TAB 2: MOTIVOS DE DESLIGAMENTO ============
with tab2:
    st.header("Motivos de Desligamento")

    # Filtrar apenas demissões
    df_desl = demissoes_periodo.copy()

    if len(df_desl) == 0:
        st.warning("Sem dados de desligamento no período selecionado")
    else:
        # Gráfico geral
        st.subheader("📊 Visão Geral - Todos os Tipos de Rescisão")
        motivos_geral = df_desl["Tipo Rescisão"].value_counts().reset_index()
        motivos_geral.columns = ["Tipo Rescisão", "Quantidade"]

        altura_geral = max(450, len(motivos_geral) * 35)

        fig_geral = px.bar(
            motivos_geral,
            x="Quantidade",
            y="Tipo Rescisão",
            orientation="h",
            color="Quantidade",
            color_continuous_scale="Viridis",
            text="Quantidade",
        )
        fig_geral.update_traces(textposition="outside", textfont_size=12)
        fig_geral.update_layout(
            yaxis={"categoryorder": "total ascending"},
            showlegend=False,
            coloraxis_showscale=False,  # Remove a barra lateral de cores
            height=altura_geral,
            margin=dict(r=60),
        )
        st.plotly_chart(fig_geral, use_container_width=True)

        st.markdown("---")

        # Por Linha de Cuidado - APENAS se empresa = TODAS
        if empresa_selecionada == "TODAS":
            st.subheader("🏥 Análise por Linha de Cuidado")

            linhas_disponiveis = df_desl["Linha de Cuidado"].unique()

            for linha in sorted(linhas_disponiveis):
                with st.expander(f"📋 {linha}", expanded=True):
                    df_linha = df_desl[df_desl["Linha de Cuidado"] == linha]
                    motivos_linha = (
                        df_linha["Tipo Rescisão"].value_counts().reset_index()
                    )
                    motivos_linha.columns = ["Tipo Rescisão", "Quantidade"]

                    if not motivos_linha.empty:
                        altura_linha = max(300, len(motivos_linha) * 30)

                        fig_linha = px.bar(
                            motivos_linha,
                            x="Quantidade",
                            y="Tipo Rescisão",
                            orientation="h",
                            color="Quantidade",
                            color_continuous_scale="Teal",
                            text="Quantidade",
                        )
                        fig_linha.update_traces(
                            textposition="outside", textfont_size=11
                        )
                        fig_linha.update_layout(
                            yaxis={"categoryorder": "total ascending"},
                            showlegend=False,
                            coloraxis_showscale=False,  # Remove a barra lateral de cores
                            height=altura_linha,
                            margin=dict(r=50),
                        )
                        st.plotly_chart(fig_linha, use_container_width=True)

# ============ TAB 3: ANÁLISE DE PERMANÊNCIA ============
with tab3:
    st.header("Análise de Permanência")

    # Filtrar apenas demitidos com tempo calculado
    df_perm = df_filtrado[
        (df_filtrado["Demitido"] == "Sim")
        & (df_filtrado["Tempo Permanência (dias)"].notna())
        & (df_filtrado["Dt Rescisão"] >= periodo_inicio)
        & (df_filtrado["Dt Rescisão"] <= periodo_fim)
    ].copy()

    if len(df_perm) == 0:
        st.warning("Sem dados de permanência no período selecionado")
    else:
        # Métricas principais
        col_p1, col_p2, col_p3, col_p4 = st.columns(4)

        tempo_medio_geral = df_perm["Tempo Permanência (dias)"].mean()
        demitidos_45 = df_perm["Demitido 45 dias"].sum()
        demitidos_90 = df_perm["Demitido 90 dias"].sum()
        total_demitidos = len(df_perm)

        with col_p1:
            st.metric("⏱️ Permanência Média", f"{tempo_medio_geral:.0f} dias")

        with col_p2:
            perc_45 = (
                (demitidos_45 / total_demitidos * 100) if total_demitidos > 0 else 0
            )
            st.metric(
                "📉 Demitidos até 45 dias",
                f"{perc_45:.1f}%",
                help=f"{demitidos_45} colaboradores",
            )

        with col_p3:
            perc_90 = (
                (demitidos_90 / total_demitidos * 100) if total_demitidos > 0 else 0
            )
            st.metric(
                "📉 Demitidos 45-90 dias",
                f"{perc_90:.1f}%",
                help=f"{demitidos_90} colaboradores",
            )

        with col_p4:
            demitidos_apos_90 = total_demitidos - demitidos_45 - demitidos_90
            perc_apos_90 = (
                (demitidos_apos_90 / total_demitidos * 100)
                if total_demitidos > 0
                else 0
            )
            st.metric(
                "✅ Permaneceram >90 dias",
                f"{perc_apos_90:.1f}%",
                help=f"{demitidos_apos_90} colaboradores",
            )

        st.markdown("---")

        # Gráfico de permanência por faixa
        st.subheader("📊 Demissões por Período de Experiência")

        dados_experiencia = pd.DataFrame(
            {
                "Período": ["Até 45 dias", "45-90 dias", "Após 90 dias"],
                "Quantidade": [demitidos_45, demitidos_90, demitidos_apos_90],
            }
        )

        fig_exp = px.bar(
            dados_experiencia,
            x="Período",
            y="Quantidade",
            color="Quantidade",
            color_continuous_scale="Reds",
            text="Quantidade",
        )
        fig_exp.update_traces(textposition="outside")
        fig_exp.update_layout(showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig_exp, use_container_width=True)

        st.markdown("---")

        # Tempo médio por nível
        col_pn1, col_pn2 = st.columns(2)

        with col_pn1:
            st.subheader("📋 Permanência Média por Nível")
            perm_nivel = (
                df_perm.groupby("Nivel")["Tempo Permanência (dias)"]
                .mean()
                .reset_index()
            )
            perm_nivel.columns = ["Nivel", "Permanência Média (dias)"]
            perm_nivel = perm_nivel.sort_values(
                "Permanência Média (dias)", ascending=False
            )

            if not perm_nivel.empty:
                fig_perm_nivel = px.bar(
                    perm_nivel,
                    x="Permanência Média (dias)",
                    y="Nivel",
                    orientation="h",
                    color="Permanência Média (dias)",
                    color_continuous_scale="Blues",
                )
                fig_perm_nivel.update_layout(
                    showlegend=False, coloraxis_showscale=False
                )
                st.plotly_chart(fig_perm_nivel, use_container_width=True)

        with col_pn2:
            st.subheader("📋 Permanência Média por Linha de Cuidado")
            perm_linha = (
                df_perm.groupby("Linha de Cuidado")["Tempo Permanência (dias)"]
                .mean()
                .reset_index()
            )
            perm_linha.columns = ["Linha de Cuidado", "Permanência Média (dias)"]
            perm_linha = perm_linha.sort_values(
                "Permanência Média (dias)", ascending=False
            )

            if not perm_linha.empty:
                fig_perm_linha = px.bar(
                    perm_linha,
                    x="Permanência Média (dias)",
                    y="Linha de Cuidado",
                    orientation="h",
                    color="Permanência Média (dias)",
                    color_continuous_scale="Greens",
                )
                fig_perm_linha.update_layout(
                    showlegend=False, coloraxis_showscale=False
                )
                st.plotly_chart(fig_perm_linha, use_container_width=True)

        st.markdown("---")

        # Evolução mensal de turnover
        st.subheader("📈 Evolução Mensal")

        # Calcular turnover mensal (demissões / colaboradores ativos)
        meses_periodo = pd.period_range(start=periodo_inicio, end=periodo_fim, freq="M")

        dados_evolucao = []

        for mes in meses_periodo:
            mes_str = str(mes)

            # Demissões no mês
            demissoes_mes = len(df_perm[df_perm["Mês/Ano Rescisão"] == mes_str])

            # Permanência média no mês
            perm_mes = df_perm[df_perm["Mês/Ano Rescisão"] == mes_str][
                "Tempo Permanência (dias)"
            ].mean()

            dados_evolucao.append(
                {
                    "Mês": mes_str,
                    "Demissões": demissoes_mes,
                    "Permanência Média (dias)": (
                        perm_mes if not pd.isna(perm_mes) else 0
                    ),
                }
            )

        df_evolucao = pd.DataFrame(dados_evolucao)

        if not df_evolucao.empty:
            # Converter para datetime para formatação correta no gráfico
            df_evolucao["Data_Plot"] = pd.to_datetime(
                df_evolucao["Mês"], format="%Y-%m"
            )

            fig_evolucao = go.Figure()

            fig_evolucao.add_trace(
                go.Scatter(
                    x=df_evolucao["Data_Plot"],
                    y=df_evolucao["Demissões"],
                    mode="lines+markers",
                    name="Demissões",
                    line=dict(color="#f093fb", width=3),
                    yaxis="y",
                )
            )

            fig_evolucao.add_trace(
                go.Scatter(
                    x=df_evolucao["Data_Plot"],
                    y=df_evolucao["Permanência Média (dias)"],
                    mode="lines+markers",
                    name="Permanência Média",
                    line=dict(color="#667eea", width=3),
                    yaxis="y2",
                )
            )

            fig_evolucao.update_layout(
                xaxis_title="Período",
                xaxis=dict(tickformat="%m/%Y"),
                yaxis=dict(title="Demissões", side="left"),
                yaxis2=dict(
                    title="Permanência Média (dias)", side="right", overlaying="y"
                ),
                hovermode="x unified",
                legend=dict(x=0.5, y=1.1, orientation="h", xanchor="center"),
            )

            st.plotly_chart(fig_evolucao, use_container_width=True)

# Rodapé
st.markdown("---")
st.caption("📊 Dashboard RH - Gestão de Colaboradores | SBCD")
