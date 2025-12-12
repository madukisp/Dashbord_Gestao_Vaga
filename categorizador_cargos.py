import streamlit as st
import json
import pandas as pd
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Categorizador de Cargos - SBCD", page_icon="📋", layout="wide"
)

# Categorias disponíveis
CATEGORIAS = [
    "Não Classificado",
    "ADMINISTRATIVO",
    "APRENDIZ",
    "ASSESSOR",
    "COORDENADOR",
    "DIRETOR",
    "ENFERMAGEM",
    "GERENTE",
    "MEDICOS",
    "MULTIDISCIPLINAR",
    "OPERACIONAL",
    "SUPERVISOR",
    "TÉCNICO",
    "AUTONOMO",
]

# CSS customizado com cores SBCD
st.markdown(
    """
<style>
    .main {
        background-color: #1a1a2e;
    }
    .stButton>button {
        background-color: #0f3460;
        color: white;
        border-radius: 5px;
        padding: 10px 24px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #16213e;
    }
    .cargo-card {
        background-color: #16213e;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 10px;
        border-left: 4px solid #e94560;
    }
    .progress-bar {
        background-color: #0f3460;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    h1, h2, h3, p {
        color: white !important;
    }
</style>
""",
    unsafe_allow_html=True,
)


# Funções auxiliares
def carregar_cargos():
    """Carrega o arquivo JSON de cargos"""
    try:
        with open("cargos_niveis.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("❌ Arquivo 'cargos_niveis.json' não encontrado!")
        return {}


def salvar_cargos(cargos_dict):
    """Salva as alterações no arquivo JSON"""
    with open("cargos_niveis.json", "w", encoding="utf-8") as f:
        json.dump(cargos_dict, f, ensure_ascii=False, indent=4)


def calcular_progresso(cargos_dict):
    """Calcula o progresso da categorização"""
    total = len(cargos_dict)
    classificados = sum(1 for v in cargos_dict.values() if v != "Não Classificado")
    percentual = (classificados / total * 100) if total > 0 else 0
    return classificados, total, percentual


def exportar_csv(cargos_dict):
    """Exporta para CSV"""
    df = pd.DataFrame(list(cargos_dict.items()), columns=["Cargo", "Categoria"])
    return df.to_csv(index=False).encode("utf-8")


# Inicialização do estado da sessão
if "cargos" not in st.session_state:
    st.session_state.cargos = carregar_cargos()
if "filtro_categoria" not in st.session_state:
    st.session_state.filtro_categoria = "Não Classificado"
if "busca" not in st.session_state:
    st.session_state.busca = ""

# Interface principal
st.title("📋 Categorizador de Cargos - SBCD")

# Barra de progresso
classificados, total, percentual = calcular_progresso(st.session_state.cargos)
st.markdown(
    f"""
<div class="progress-bar">
    <h3>Progresso: {classificados}/{total} ({percentual:.1f}%)</h3>
    <progress value="{percentual}" max="100" style="width: 100%; height: 30px;"></progress>
</div>
""",
    unsafe_allow_html=True,
)

# Filtros e busca
col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    filtro = st.selectbox(
        "🔍 Filtrar por categoria:",
        ["Todos"] + CATEGORIAS,
        index=1,  # "Não Classificado" por padrão
    )

with col2:
    busca = st.text_input("🔎 Buscar cargo:", placeholder="Digite o nome do cargo...")

with col3:
    st.write("")
    st.write("")
    if st.button("💾 Salvar Alterações"):
        salvar_cargos(st.session_state.cargos)
        st.success("✅ Salvo com sucesso!")

# Botões de exportação
col_exp1, col_exp2, col_exp3 = st.columns([1, 1, 3])
with col_exp1:
    csv = exportar_csv(st.session_state.cargos)
    st.download_button(
        "📥 Exportar CSV",
        csv,
        f"cargos_categorizados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        "text/csv",
    )

with col_exp2:
    json_str = json.dumps(st.session_state.cargos, ensure_ascii=False, indent=4)
    st.download_button(
        "📥 Exportar JSON",
        json_str,
        f"cargos_categorizados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        "application/json",
    )

st.divider()

# Filtrar cargos
cargos_filtrados = {}
for cargo, categoria in st.session_state.cargos.items():
    # Filtro por categoria
    if filtro != "Todos" and categoria != filtro:
        continue

    # Filtro por busca
    if busca and busca.lower() not in cargo.lower():
        continue

    cargos_filtrados[cargo] = categoria

# Mostrar quantidade de resultados
st.info(f"📊 Mostrando {len(cargos_filtrados)} de {total} cargos")

# Listagem de cargos
if len(cargos_filtrados) == 0:
    st.warning("Nenhum cargo encontrado com os filtros aplicados.")
else:
    # Modo de visualização
    modo = st.radio(
        "Modo de visualização:",
        ["📝 Edição Individual", "⚡ Edição Rápida"],
        horizontal=True,
    )

    if modo == "📝 Edição Individual":
        # Modo individual - mais detalhado
        for cargo, categoria_atual in cargos_filtrados.items():
            with st.container():
                st.markdown(
                    f"""
                <div class="cargo-card">
                    <h3>{cargo}</h3>
                </div>
                """,
                    unsafe_allow_html=True,
                )

                col_a, col_b = st.columns([3, 1])
                with col_a:
                    nova_categoria = st.selectbox(
                        "Categoria:",
                        CATEGORIAS,
                        index=CATEGORIAS.index(categoria_atual),
                        key=f"select_{cargo}",
                        label_visibility="collapsed",
                    )

                with col_b:
                    if st.button("✅ Atualizar", key=f"btn_{cargo}"):
                        st.session_state.cargos[cargo] = nova_categoria
                        st.rerun()

                st.markdown("---")

    else:
        # Modo rápido - tabela editável
        st.info(
            "💡 Dica: Edite diretamente na tabela e clique em 'Salvar Alterações' no topo da página"
        )

        cargos_list = list(cargos_filtrados.keys())
        categorias_list = [cargos_filtrados[c] for c in cargos_list]

        # Criar DataFrame editável
        df_edicao = pd.DataFrame(
            {"Cargo": cargos_list, "Categoria Atual": categorias_list}
        )

        # Mostrar em batches de 50 para performance
        itens_por_pagina = 50
        total_paginas = (len(cargos_list) + itens_por_pagina - 1) // itens_por_pagina

        if total_paginas > 1:
            pagina = st.selectbox(
                "Página:",
                range(1, total_paginas + 1),
                format_func=lambda x: f"Página {x} de {total_paginas}",
            )
            inicio = (pagina - 1) * itens_por_pagina
            fim = min(inicio + itens_por_pagina, len(cargos_list))
            cargos_pagina = cargos_list[inicio:fim]
        else:
            cargos_pagina = cargos_list

        # Edição rápida com selectbox para cada cargo
        for cargo in cargos_pagina:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.text(cargo)
            with col2:
                nova_cat = st.selectbox(
                    "Cat",
                    CATEGORIAS,
                    index=CATEGORIAS.index(st.session_state.cargos[cargo]),
                    key=f"quick_{cargo}",
                    label_visibility="collapsed",
                )
                if nova_cat != st.session_state.cargos[cargo]:
                    st.session_state.cargos[cargo] = nova_cat

# Estatísticas por categoria
st.divider()
st.subheader("📊 Estatísticas por Categoria")

stats = {}
for categoria in CATEGORIAS:
    stats[categoria] = sum(
        1 for v in st.session_state.cargos.values() if v == categoria
    )

df_stats = pd.DataFrame(list(stats.items()), columns=["Categoria", "Quantidade"])
df_stats = df_stats.sort_values("Quantidade", ascending=False)

col_stat1, col_stat2 = st.columns(2)
with col_stat1:
    st.dataframe(df_stats, hide_index=True, use_container_width=True)

with col_stat2:
    st.bar_chart(df_stats.set_index("Categoria"))

# Rodapé
st.divider()
st.caption(
    "💾 Lembre-se de clicar em 'Salvar Alterações' regularmente para não perder seu progresso!"
)
