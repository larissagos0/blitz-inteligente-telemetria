import streamlit as st
import pandas as pd
import re
import plotly.express as px
from google import genai


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
    text-align: center;
">
    <h2 style="margin:0;">🚚 Blitz Inteligente de Telemetria</h2>
    <p style="
            margin-top:8px; 
            opacity:0.85;">
        Painel executivo de auditoria de consumo de combustível    
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()

with st.sidebar:
    st.markdown("⚙️ Controle do Painel")

    arquivo = st.file_uploader(
        "Envie a planilha Excel",
        type=["xlsx"]
    )


    pagina_app = st.radio(
        "🧭 Navegação",
        [
            "📊 Dashboard",
            "🤖 Análise IA",
            "📋 Auditoria Completa",
            "📥 Relatórios"
        ]
    )
    
    st.markdown(
    """
    <style>
    .sidebar-footer {
        position: fixed;
        bottom: 15px;
        left: 20px;
        color: #9CA3AF;
        font-size: 12px;
    }
    </style>

    <div class="sidebar-footer">
        🚚 Blitz Inteligente v1.0
    </div>
    """,
    unsafe_allow_html=True
)


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

def gerar_diagnostico_gemini(prompt):
    try:

        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

        resposta = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt
    )

        return resposta.text
    except Exception:

        return """
⚠️ O agente de IA está temporariamente indisponível.

A auditoria e os diagnósticos baseados em regras continuam funcionando normalmente.
"""
    
if pagina_app == "📊 Dashboard":

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


elif pagina_app == "🤖 Análise IA":

    st.title("🤖 Análise IA")
    st.markdown("Diagnóstico inteligente por veículo com base nas divergências de telemetria.")

    if arquivo is not None:

        df_ia = pd.read_excel(arquivo, header=2)

        df_ia["%Média"] = pd.to_numeric(
            df_ia["%Média"],
            errors="coerce"
        )

        df_ia["%Média"] = (
            df_ia["%Média"] * 100
        ).round(2)

        if "Set Nativo" in df_ia.columns:
            df_ia["KM_Nativo"], df_ia["Comb_Nativo"] = zip(
                *df_ia["Set Nativo"].apply(extrair_dados)
            )

        if "Set Retrac" in df_ia.columns:
            df_ia["KM_Retrac"], df_ia["Comb_Retrac"] = zip(
                *df_ia["Set Retrac"].apply(extrair_dados)
            )

        df_ia["Media_Alternativa"] = None

        for index, row in df_ia.iterrows():
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

            df_ia.at[index, "Media_Alternativa"] = media

        df_ia["Divergencia"] = df_ia.apply(
            lambda row: calcular_divergencia(
                row["%Média"],
                row["Media_Alternativa"]
            ),
            axis=1
        )

        df_ia["Status"] = df_ia.apply(
            lambda row: classificar_divergencia(
                row["Divergencia"],
                row["KM Válido"]
            ),
            axis=1
        )

        df_ia["Observacao_IA"] = df_ia.apply(
            lambda row: gerar_observacao(
                row["Status"],
                row["Divergencia"]
            ),
            axis=1
        )

        df_ia["Score_Confiabilidade"] = df_ia["Status"].apply(
            calcular_score
        )

        placas = sorted(
            df_ia["Placa"].dropna().unique()
        )

        placa_selecionada = st.selectbox(
            "Selecione o veículo",
            placas
        )

        dados_veiculo = df_ia[
            df_ia["Placa"] == placa_selecionada
        ].iloc[0]

        st.divider()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "%Média Oficial",
                f"{dados_veiculo['%Média']:.2f}%"
            )

        with col2:
            st.metric(
                "Média Alternativa",
                f"{dados_veiculo['Media_Alternativa']:.2f}%"
            )

        with col3:
            st.metric(
                "Divergência",
                f"{dados_veiculo['Divergencia']:.2f}%"
            )

        with col4:
            st.metric(
                "Score IA",
                f"{dados_veiculo['Score_Confiabilidade']}/100"
            )

        st.markdown(f"""
        **Placa:** {dados_veiculo["Placa"]}  
        **Telemetria válida:** {dados_veiculo["Telemetria Válida"]}  
        **Status:** {dados_veiculo["Status"]}
        """)

        st.subheader("🧠 Diagnóstico Inteligente")

        status = dados_veiculo["Status"]

        if status == "OK":
            st.success(
                "✅ As telemetrias estão consistentes. "
                "A divergência está dentro do padrão esperado."
            )

        elif status == "Atenção":
            st.warning(
                "⚠️ Divergência moderada identificada. "
                "Recomenda-se acompanhar este veículo nas próximas análises."
            )

        elif status == "Crítico":
            st.error(
                "🚨 Divergência crítica identificada. "
                "Recomenda-se validar sensores, abastecimentos e histórico de telemetria."
            )

        elif status == "Baixa rodagem":
            st.info(
                "ℹ️ Veículo com baixa rodagem. "
                "A amostra é insuficiente para uma comparação confiável."
            )

        else:
            st.info(
                "Não foi possível realizar comparação entre as telemetrias."
            )

        st.markdown("### Observação automática")
        st.write(dados_veiculo["Observacao_IA"])

        st.divider()


        st.subheader("💬 Chat com Agente de Auditoria")

        st.markdown(
            "Faça perguntas sobre a auditoria, veículos críticos, prioridades ou recomendações operacionais."
        )

        total = len(df_ia)
        ok = len(df_ia[df_ia["Status"] == "OK"])
        atencao = len(df_ia[df_ia["Status"] == "Atenção"])
        critico = len(df_ia[df_ia["Status"] == "Crítico"])
        sem_comparacao = len(df_ia[df_ia["Status"] == "Sem comparação"])
        baixa_rodagem = len(df_ia[df_ia["Status"] == "Baixa rodagem"])

        df_validos = df_ia[
            df_ia["Status"].isin(["OK", "Atenção", "Crítico"])
        ].copy()

        maior_divergencia = df_validos["Divergencia"].max()
        media_divergencia = df_validos["Divergencia"].mean()

        top_criticos_chat = df_ia[
            df_ia["Status"] == "Crítico"
        ].sort_values(
            by="Divergencia",
            ascending=False
        ).head(10)

        contexto_criticos = top_criticos_chat[
            [
                "Placa",
                "Telemetria Válida",
                "%Média",
                "Media_Alternativa",
                "Divergencia",
                "KM Válido",
                "Score_Confiabilidade",
                "Status"
            ]
        ].to_string(index=False)

        pergunta_usuario = st.text_area(
            "Digite sua pergunta para o agente",
            placeholder="Ex: Qual veículo devo priorizar e por quê?"
        )

        if st.button("🤖 Perguntar ao agente"):

            if pergunta_usuario.strip() == "":
                st.warning("Digite uma pergunta antes de enviar.")

            else:
                prompt_chat = f"""
                Você é um agente especialista em auditoria de telemetria de veículos pesados.

                Responda em português, de forma objetiva, operacional e útil para uma equipe de logística.

                Dados gerais da auditoria:
                - Total de veículos analisados: {total}
                - OK: {ok}
                - Atenção: {atencao}
                - Crítico: {critico}
                - Sem comparação: {sem_comparacao}
                - Baixa rodagem: {baixa_rodagem}
                - Maior divergência: {maior_divergencia:.2f}%
                - Média de divergência: {media_divergencia:.2f}%

                Top 10 veículos críticos:
                {contexto_criticos}

                Pergunta do usuário:
                {pergunta_usuario}

                Regras para resposta:
                - Não invente dados fora do contexto informado.
                - Se precisar priorizar, use a maior divergência e o status crítico.
                - Sempre que possível, cite as placas relevantes.
                - Termine com ações recomendadas.
                """

                try:
                    with st.spinner("Consultando agente de auditoria..."):
                        resposta_agente = gerar_diagnostico_gemini(prompt_chat)

                    st.success("Resposta gerada pelo agente.")
                    st.markdown(resposta_agente)

                except Exception as erro:
                    st.error(
                        "Não foi possível consultar a IA neste momento. "
                        "Verifique a cota da API ou tente novamente mais tarde."
                    )
                    st.caption(str(erro))

        
    else:
        st.warning("Envie uma planilha na barra lateral para gerar o diagnóstico.")

elif pagina_app == "📋 Auditoria Completa":

    st.title("📋 Auditoria Completa")
    col1, col2 = st.columns([2, 1])

    with col1:
        placa_busca = st.text_input(
            "🔎 Buscar placa",
            placeholder="Digite a placa..."
        )

    with col2:
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

    st.markdown(
        "Visualize todos os registros tratados da auditoria, com filtros e paginação."
    )

    if arquivo is not None:

        df_auditoria = pd.read_excel(arquivo, header=2)

        df_auditoria["%Média"] = pd.to_numeric(
            df_auditoria["%Média"],
            errors="coerce"
        )

        df_auditoria["%Média"] = (
            df_auditoria["%Média"] * 100
        ).round(2)

        if "Set Nativo" in df_auditoria.columns:
            df_auditoria["KM_Nativo"], df_auditoria["Comb_Nativo"] = zip(
                *df_auditoria["Set Nativo"].apply(extrair_dados)
            )

        if "Set Retrac" in df_auditoria.columns:
            df_auditoria["KM_Retrac"], df_auditoria["Comb_Retrac"] = zip(
                *df_auditoria["Set Retrac"].apply(extrair_dados)
            )

        df_auditoria["Media_Alternativa"] = None

        for index, row in df_auditoria.iterrows():
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

            df_auditoria.at[index, "Media_Alternativa"] = media

        df_auditoria["Divergencia"] = df_auditoria.apply(
            lambda row: calcular_divergencia(
                row["%Média"],
                row["Media_Alternativa"]
            ),
            axis=1
        )

        df_auditoria["Status"] = df_auditoria.apply(
            lambda row: classificar_divergencia(
                row["Divergencia"],
                row["KM Válido"]
            ),
            axis=1
        )

        df_auditoria["Observacao_IA"] = df_auditoria.apply(
            lambda row: gerar_observacao(
                row["Status"],
                row["Divergencia"]
            ),
            axis=1
        )

        df_auditoria["Score_Confiabilidade"] = df_auditoria["Status"].apply(
            calcular_score
        )

        if filtro_status == "Todos":
            df_filtrado_auditoria = df_auditoria.copy()
        else:
            df_filtrado_auditoria = df_auditoria[
                df_auditoria["Status"] == filtro_status
            ].copy()
        if placa_busca:
            df_filtrado_auditoria = df_filtrado_auditoria[
                df_filtrado_auditoria["Placa"]
                .astype(str)
                .str.contains(
                    placa_busca,
                    case=False,
                    na=False
                )
            ]

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

        registros_por_pagina = st.selectbox(
            "Registros por página",
            [10, 20, 50, 100],
            index=1
        )

        total_paginas = max(
            1,
            (len(df_filtrado_auditoria) - 1) // registros_por_pagina + 1
        )

        pagina = st.number_input(
            "Página",
            min_value=1,
            max_value=total_paginas,
            value=1
        )

        inicio = (pagina - 1) * registros_por_pagina
        fim = inicio + registros_por_pagina

        df_pagina = df_filtrado_auditoria.iloc[inicio:fim]

        st.caption(
            f"Exibindo {len(df_pagina)} registros de {len(df_filtrado_auditoria)} filtrados."
        )

        st.dataframe(
            df_pagina[colunas_exibir],
            width="stretch"
        )

    else:
        st.warning("Envie uma planilha na barra lateral para visualizar a auditoria.")

elif pagina_app == "📥 Relatórios":
    
    st.title("📥 Relatórios")

    st.markdown("""
    Gere e baixe o relatório final da auditoria de telemetria com médias,
    divergências, status e observações inteligentes.
    """)

    filtro_status_relatorio = st.selectbox(
        "Filtrar relatório por status",
        [
            "Todos",
            "OK",
            "Atenção",
            "Crítico",
            "Sem comparação",
            "Baixa rodagem"
        ]
    )

    if arquivo is not None:

        df_relatorio = pd.read_excel(arquivo, header=2)

        df_relatorio["%Média"] = pd.to_numeric(
            df_relatorio["%Média"],
            errors="coerce"
        )

        df_relatorio["%Média"] = (
            df_relatorio["%Média"] * 100
        ).round(2)

        if "Set Nativo" in df_relatorio.columns:
            df_relatorio["KM_Nativo"], df_relatorio["Comb_Nativo"] = zip(
                *df_relatorio["Set Nativo"].apply(extrair_dados)
            )

        if "Set Retrac" in df_relatorio.columns:
            df_relatorio["KM_Retrac"], df_relatorio["Comb_Retrac"] = zip(
                *df_relatorio["Set Retrac"].apply(extrair_dados)
            )

        df_relatorio["Media_Alternativa"] = None

        for index, row in df_relatorio.iterrows():
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

            df_relatorio.at[index, "Media_Alternativa"] = media

        df_relatorio["Divergencia"] = df_relatorio.apply(
            lambda row: calcular_divergencia(
                row["%Média"],
                row["Media_Alternativa"]
            ),
            axis=1
        )

        df_relatorio["Status"] = df_relatorio.apply(
            lambda row: classificar_divergencia(
                row["Divergencia"],
                row["KM Válido"]
            ),
            axis=1
        )

        df_relatorio["Observacao_IA"] = df_relatorio.apply(
            lambda row: gerar_observacao(
                row["Status"],
                row["Divergencia"]
            ),
            axis=1
        )

        df_relatorio["Score_Confiabilidade"] = df_relatorio["Status"].apply(
            calcular_score
        )

        if filtro_status_relatorio != "Todos":
            df_relatorio = df_relatorio[
                df_relatorio["Status"] == filtro_status_relatorio
            ]

        df_relatorio.to_excel(
            "relatorio_telemetria.xlsx",
            index=False,
            engine="openpyxl"
        )

        st.success("Relatório gerado com sucesso.")

        with open("relatorio_telemetria.xlsx", "rb") as arquivo_excel:
            st.download_button(
                label="📥 Baixar Relatório Excel",
                data=arquivo_excel,
                file_name="relatorio_telemetria.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    else:
        st.warning("Envie uma planilha na barra lateral para gerar o relatório.")