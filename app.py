import streamlit as st
import pandas as pd
import re
import plotly.express as px


st.set_page_config(
    page_title="Blitz Inteligente",
    page_icon="🚚",
    layout="wide"
)

st.markdown("""
<div style="
    background: linear-gradient(90deg, #0B1F3A, #1F6FEB);
    padding: 20px;
    border-radius: 12px;
    color: white;
    margin-bottom: 15px;
">
    <h2 style="margin:0;">🚚 Blitz Inteligente de Telemetria</h2>
    <p style="margin:0; opacity:0.8;">
        Painel executivo de auditoria de consumo de combustível    
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()

with st.sidebar:
    st.markdown("##⚙️ Controle do Painel")

    arquivo = st.file_uploader(
        "Envie a planilha Excel",
        type=["xlsx"]
    )

    st.divider()

    filtro_status = st.selectbox(
        "Filtrar por status",
        [
            "Todos",
            "OK",
            "Atenção",
            "Crítico",
            "Sem comparação",
            "Baixa rodagem"
        ]
    )

    st.divider()
    st.caption("Sistema de telemetria v1.0")


def extrair_dados(texto):
    numeros = re.findall(r"\d+", str(texto))

    if len(numeros) >= 2:
        km = int(numeros[0])
        combustivel = int(numeros[1])
        return km, combustivel

    return None, None


def calcular_media(km, combustivel, meta):
    try:
        media = (km / combustivel) / meta
        return round(media * 100, 2)
    except:
        return None


def calcular_divergencia(media_oficial, media_alternativa):
    if pd.isna(media_oficial) or pd.isna(media_alternativa):
        return None

    try:
        if media_oficial <= 1:
            return None

        divergencia = abs(
            (media_alternativa - media_oficial) / media_oficial
        ) * 100

        return round(divergencia, 2)

    except:
        return None


def classificar_divergencia(divergencia, km_valido):
    try:
        if km_valido < 30:
            return "Baixa rodagem"

        if pd.isna(divergencia):
            return "Sem comparação"

        if divergencia <= 5:
            return "OK"

        elif divergencia <= 15:
            return "Atenção"

        else:
            return "Crítico"

    except:
        return None


def gerar_observacao(status, divergencia):
    if status == "OK":
        return "Divergência dentro do padrão esperado."

    elif status == "Atenção":
        return "Divergência moderada identificada. Recomenda-se validação."

    elif status == "Crítico":
        return "Possível inconsistência de telemetria detectada."

    elif status == "Sem comparação":
        return "Não foi possível comparar as telemetrias."

    elif status == "Baixa rodagem":
        return "Veículo com rodagem insuficiente para validação da telemetria."

    return ""


def calcular_score(status):
    if status == "OK":
        return 100

    elif status == "Atenção":
        return 70

    elif status == "Crítico":
        return 30

    elif status == "Baixa rodagem":
        return 0

    return 0


def kpi_card(titulo, valor, cor):
    st.markdown(f"""
        <div style="
            background-color: #111827;
            border-left: 6px solid {cor};
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.2);
            min-height: 70px;
        ">
            <p style="margin:0; color: #9ca3af; font-size:14px;">
                {titulo}
            </p>
            <h2 style="margin:0; color:white;">
                {valor}
            </h2>
        </div>
    """, unsafe_allow_html=True)


if arquivo is not None:

    df = pd.read_excel(arquivo, header=2)

    df["%Média"] = pd.to_numeric(
        df["%Média"],
        errors="coerce"
    )

    df["%Média"] = (df["%Média"] * 100).round(2)

    if "Set Nativo" in df.columns:
        df["KM_Nativo"], df["Comb_Nativo"] = zip(
            *df["Set Nativo"].apply(extrair_dados)
        )

    if "Set Retrac" in df.columns:
        df["KM_Retrac"], df["Comb_Retrac"] = zip(
            *df["Set Retrac"].apply(extrair_dados)
        )

    df["Media_Alternativa"] = None

    for index, row in df.iterrows():
        telemetria = str(row["Telemetria Válida"])
        meta = row["Meta"]

        if "Retrac" in telemetria:
            media = calcular_media(
                row["KM_Nativo"],
                row["Comb_Nativo"],
                meta
            )
        else:
            media = calcular_media(
                row["KM_Retrac"],
                row["Comb_Retrac"],
                meta
            )

        df.at[index, "Media_Alternativa"] = media

    df["Divergencia"] = df.apply(
        lambda row: calcular_divergencia(
            row["%Média"],
            row["Media_Alternativa"]
        ),
        axis=1
    )

    df["Status"] = df.apply(
        lambda row: classificar_divergencia(
            row["Divergencia"],
            row["KM Válido"]
        ),
        axis=1
    )

    df["Observacao_IA"] = df.apply(
        lambda row: gerar_observacao(
            row["Status"],
            row["Divergencia"]
        ),
        axis=1
    )

    df["Score_Confiabilidade"] = df["Status"].apply(
        calcular_score
    )

    total = len(df)
    ok = len(df[df["Status"] == "OK"])
    atencao = len(df[df["Status"] == "Atenção"])
    critico = len(df[df["Status"] == "Crítico"])
    sem_comparacao = len(df[df["Status"] == "Sem comparação"])
    baixa_rodagem = len(df[df["Status"] == "Baixa rodagem"])

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        kpi_card("🚛 Total", total, "#1F6FEB")

    with col2:
        kpi_card("✅ OK", ok, "#22C55E")

    with col3:
        kpi_card("⚠️ Atenção", atencao, "#FACC15")

    with col4:
        kpi_card("❌ Crítico", critico, "#EF4444")

    with col5:
        kpi_card("🔍 Sem comparação", sem_comparacao, "#6B7280")

    with col6:
        kpi_card("🚜 Baixa rodagem", baixa_rodagem, "#60A5FA")

    dados_grafico = pd.DataFrame({
        "Status": [
            "OK",
            "Atenção",
            "Crítico",
            "Sem comparação",
            "Baixa rodagem"
        ],
        "Quantidade": [
            ok,
            atencao,
            critico,
            sem_comparacao,
            baixa_rodagem
        ]
    })

    grafico = px.pie(
        dados_grafico,
        names="Status",
        values="Quantidade",
        hole=0.65,
        title="Distribuição dos Status",
        color="Status",
        color_discrete_map={
            "OK": "#22C55E",
            "Atenção": "#FACC15",
            "Crítico": "#EF4444",
            "Sem comparação": "#6B7280",
            "Baixa rodagem": "#60A5FA"
        }
    )

    grafico.update_layout(
        template="plotly_dark",
        title_x=0.5,
        paper_bgcolor="#0e1117",
        plot_bgcolor="#0e1117",
        font_color="white",
        height=420,
        showlegend=True
    )

    grafico.update_traces(
        textinfo="percent+label"
    )

    col_grafico, col_insights = st.columns([1, 1])

    with col_grafico:
        st.plotly_chart(
            grafico,
            width="stretch"
        )

    with col_insights:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.subheader("📌 Insights")

        df_validos = df[
            df["Status"].isin(["OK", "Atenção", "Crítico"])
        ].copy()

        maior_divergencia = df_validos["Divergencia"].max()
        media_divergencia = df_validos["Divergencia"].mean()

        kpi_card(
            "Maior Divergência",
            f"{maior_divergencia:.2f} %",
            "#EF4444"
        )

        st.markdown("<br>", unsafe_allow_html=True)

        kpi_card(
            "Média de Divergência",
            f"{media_divergencia:.2f} %",
            "#FACC15"
        )

        st.markdown("<br>", unsafe_allow_html=True)

        kpi_card(
            "Total Analisado",
            len(df),
            "#1F6FEB"
        )

    top_criticos = df[
        df["Status"] == "Crítico"
    ].sort_values(
        by="Divergencia",
        ascending=False
    ).head(10)

    colunas_criticos = [
        "Placa",
        "Telemetria Válida",
        "%Média",
        "Media_Alternativa",
        "Divergencia",
        "Score_Confiabilidade",
        "Status",
        "Observacao_IA",
    ]

    st.divider()

    st.subheader("🚨 Top 10 Veículos Críticos")

    st.dataframe(
        top_criticos[colunas_criticos],
        width="stretch"
    )

    if filtro_status == "Todos":
        df_filtrado = df.copy()
    else:
        df_filtrado = df[
            df["Status"] == filtro_status
        ].copy()

    colunas_inteiras = [
        "KM Válido",
        "Comb Válido",
        "Peso da Carga",
        "KM_Nativo",
        "Comb_Nativo",
        "KM_Retrac",
        "Comb_Retrac"
    ]

    for coluna in colunas_inteiras:
        df_filtrado[coluna] = (
            pd.to_numeric(
                df_filtrado[coluna],
                errors="coerce"
            )
            .fillna(0)
            .astype(int)
        )

    colunas_decimais = [
        "%Média",
        "Meta",
        "Media_Alternativa",
        "Divergencia"
    ]

    for coluna in colunas_decimais:
        df_filtrado[coluna] = pd.to_numeric(
            df_filtrado[coluna],
            errors="coerce"
        ).round(2)

    st.divider()

    colunas_exibir = [
        "Peso da Carga",
        "Placa",
        "KM Válido",
        "Comb Válido",
        "Telemetria Válida",
        "Set Nativo",
        "Set Retrac",
        "%Média",
        "Meta",
        "KM_Nativo",
        "Comb_Nativo",
        "KM_Retrac",
        "Comb_Retrac",
        "Media_Alternativa",
        "Divergencia",
        "Status",
        "Observacao_IA",
        "Score_Confiabilidade",
    ]

    with st.expander(
        "📋 Ver Auditoria Completa",
        expanded=False
    ):
        registros_por_pagina = st.selectbox(
            "Registros por página",
            [10, 20, 50, 100],
            index=1
        )

        total_paginas = max(
            1,
            (len(df_filtrado) - 1) // registros_por_pagina + 1
        )

        pagina = st.number_input(
            "Página",
            min_value=1,
            max_value=total_paginas,
            value=1
        )

        inicio = (pagina - 1) * registros_por_pagina
        fim = inicio + registros_por_pagina

        df_pagina = df_filtrado.iloc[inicio:fim]

        st.dataframe(
            df_pagina[colunas_exibir],
            width="stretch"
        )

    df_filtrado.to_excel(
        "relatorio_telemetria.xlsx",
        index=False,
        engine="openpyxl"
    )

    with open("relatorio_telemetria.xlsx", "rb") as arquivo_excel:
        st.download_button(
            label="📥 Exportar Relatório Inteligente",
            data=arquivo_excel,
            file_name="relatorio_telemetria.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )