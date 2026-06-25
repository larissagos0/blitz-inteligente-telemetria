import streamlit as st
import pandas as pd
import re
import plotly.express as px
from google import genai
from agents.agente_auditoria import executar_agente_auditoria

st.set_page_config(
    page_title="Blitz Inteligente",
    page_icon="🚚",
    layout="wide"
)

# Header principal com gradiente
st.markdown("""
<div style="
    background: linear-gradient(90deg, #0B1F3A, #1F6FEB);
    padding: 20px;
    border-radius: 12px;
    color: white;
    margin-bottom: 15px;
    text-align: center;
">
    <h2 style="margin:0;"> Blitz Inteligente de Telemetria</h2>
    <p style="
            margin-top:8px; 
            opacity:0.85;">
        Painel executivo de auditoria de consumo de combustível    
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()

# Sidebar: upload de arquivo e navegação entre páginas
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


# Extrai KM e combustível de strings no formato "XXXX / YYYY"
def extrair_dados(texto):
    numeros = re.findall(r"\d+", str(texto))

    if len(numeros) >= 2:
        km = int(numeros[0])
        combustivel = int(numeros[1])
        return km, combustivel

    return None, None


# Calcula a média percentual em relação à meta
def calcular_media(km, combustivel, meta):
    try:
        media = (km / combustivel) / meta
        return round(media * 100, 2)
    except:
        return None


# Calcula a divergência percentual entre a média oficial e a alternativa
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


# Classifica o status com base na divergência e na quilometragem
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

# Gera uma orientação textual padronizada para facilitar a tratativa operacional.
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


# Score numérico de confiabilidade por status
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


# Componente visual de KPI estilizado
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

# Envia o contexto da auditoria ao Gemini e devolve a resposta do agente.
def gerar_diagnostico_gemini(prompt):
    try:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        resposta = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt
        )
        return resposta.text
    except Exception:
                # Mantém o painel utilizável mesmo quando a API, a chave ou a conexão falham.
        return """
⚠️ O agente de IA está temporariamente indisponível.

A auditoria e os diagnósticos baseados em regras continuam funcionando normalmente.
"""


# Função auxiliar para processar o DataFrame bruto da planilha
def processar_dataframe(df):
    df["%Média"] = pd.to_numeric(df["%Média"], errors="coerce")
    df["%Média"] = (df["%Média"] * 100).round(2)

    # Separa quilometragem e combustível das duas fontes de telemetria.
    if "Set Nativo" in df.columns:
        df["KM_Nativo"], df["Comb_Nativo"] = zip(
            *df["Set Nativo"].apply(extrair_dados)
        )

    if "Set Retrac" in df.columns:
        df["KM_Retrac"], df["Comb_Retrac"] = zip(
            *df["Set Retrac"].apply(extrair_dados)
        )

    df["Media_Alternativa"] = None

    # Usa a telemetria oposta à válida para calcular a média alternativa
    for index, row in df.iterrows():
        telemetria = str(row["Telemetria Válida"])
        meta = row["Meta"]

        if "Retrac" in telemetria:
            media = calcular_media(row["KM_Nativo"], row["Comb_Nativo"], meta)
        else:
            media = calcular_media(row["KM_Retrac"], row["Comb_Retrac"], meta)

        df.at[index, "Media_Alternativa"] = media

    df["Divergencia"] = df.apply(
        lambda row: calcular_divergencia(row["%Média"], row["Media_Alternativa"]),
        axis=1
    )
    df["Status"] = df.apply(
        lambda row: classificar_divergencia(row["Divergencia"], row["KM Válido"]),
        axis=1
    )
    df["Observacao_IA"] = df.apply(
        lambda row: gerar_observacao(row["Status"], row["Divergencia"]),
        axis=1
    )
    df["Score_Confiabilidade"] = df["Status"].apply(calcular_score)

    return df

def formatar_percentual(valor):
    if pd.isna(valor):
        return "Não disponível"
    
    try:
        return f"{float(valor):.2f}%"
    except (TypeError, ValueError):
        return "Não disponível"

def classificar_status_por_divergencia(divergencia):
    """Formata valores percentuais e trata valores nulos ou inválidos."""
    if pd.isna(divergencia):
        return "Sem comparação"
    elif divergencia > 10:
        return "Crítico"
    elif divergencia > 5:
        return "Atenção"
    else:
        return "OK"
    
def calcular_score_por_status(status):
    """Calcula um score simples de confiabilidade com base no status."""
    if status == "OK":
        return 100
    elif status == "Atenção":
        return 70
    elif status == "Crítico":
        return 40
    elif status == "Baixa Rodagem":
        return 50
    else:
        return 0   

# ─── PÁGINAS ────────────────────────────────────────────────────────────────

if pagina_app == "📊 Dashboard":

    if arquivo is not None:
        df = processar_dataframe(pd.read_excel(arquivo, header=2))
        analise_agente = executar_agente_auditoria(df)
        
        total = len(df)
        ok = len(df[df["Status"] == "OK"])
        atencao = len(df[df["Status"] == "Atenção"])
        critico = len(df[df["Status"] == "Crítico"])
        sem_comparacao = len(df[df["Status"] == "Sem comparação"])
        baixa_rodagem = len(df[df["Status"] == "Baixa rodagem"])

        # KPIs no topo
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

        # Resume a quantidade de veículos por status para alimentar o gráfico.
        dados_grafico = pd.DataFrame({
            "Status": ["OK", "Atenção", "Crítico", "Sem comparação", "Baixa rodagem"],
            "Quantidade": [ok, atencao, critico, sem_comparacao, baixa_rodagem]
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
        grafico.update_traces(textinfo="percent+label")

        col_grafico, col_insights = st.columns([1, 1])

        with col_grafico:
            st.plotly_chart(grafico, use_container_width=True)

        with col_insights:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.subheader("📌 Insights")
            st.caption("Indicadores consolidados por veículo, com base no Agente de Auditoria")


            veiculos_validos = analise_agente[
                analise_agente["status_consolidado"].isin(["OK", "Atenção", "Crítico"])
            ].copy()

            maior_divergencia = veiculos_validos["divergencia_consolidada"].max()
            media_divergencia = veiculos_validos["divergencia_consolidada"].mean()
            total_veiculos_analisados = len(analise_agente)

            kpi_card("Maior divergência consolidada", f"{maior_divergencia:.2f} %", "#FF4B4B")
            st.markdown("<br>", unsafe_allow_html=True)
            kpi_card("Média de divergência consolidada", f"{media_divergencia:.2f} %", "#FFD700")
            st.markdown("<br>", unsafe_allow_html=True)
            kpi_card("Veículos analisados", total_veiculos_analisados, "#1F6FEB")
        
        # Cria uma cópia para calcular o ranking consolidado sem alterar o DataFrame original.
        df_ranking = df.copy()

        df_ranking["%Média"] = pd.to_numeric(df_ranking["%Média"], errors="coerce")
        df_ranking["Media_Alternativa"] = pd.to_numeric(df_ranking["Media_Alternativa"], errors="coerce")
        df_ranking["Divergencia"] = pd.to_numeric(df_ranking["Divergencia"], errors="coerce")

        # Consolida os dados por placa
        ranking_placas = (
            df_ranking
            .groupby("Placa")
            .agg(
                telemetria_valida=("Telemetria Válida", "first"),
                dias_analisados=("Placa", "count"),
                dias_criticos=("Divergencia", lambda x: (x > 10).sum()),
                media_oficial_consolidada=("%Média", "mean"),
                media_alternativa_consolidada=("Media_Alternativa", "mean"),
            )
            .reset_index()
        )

        # Calcula a divergência consolidada da placa no período
        ranking_placas["Divergencia_Consolidada"] = ranking_placas.apply(
            lambda linha: abs(
                (linha["media_alternativa_consolidada"] - linha["media_oficial_consolidada"]) / linha["media_oficial_consolidada"]
            ) * 100
            if pd.notna(linha["media_oficial_consolidada"]) and linha["media_oficial_consolidada"] != 0 and pd.notna(linha["media_alternativa_consolidada"])
            else None,
            axis=1
        )

        # Classifica cada placa com base na divergência consolidada
        ranking_placas["Status_Consolidado"] = ranking_placas["Divergencia_Consolidada"].apply(classificar_status_por_divergencia)

        analise_agente = executar_agente_auditoria(df)

        top_criticos = (
            analise_agente[analise_agente["status_consolidado"] == "Crítico"]
            .sort_values(by="divergencia_consolidada", ascending=False)
            .head(10)
        )

        top_criticos_exibir = top_criticos.rename(
            columns={
                "telemetria_valida": "Telemetria Válida",
                "dias_analisados": "Dias válidos",
                "dias_criticos": "Dias críticos",
                "media_oficial_consolidada": "% Média Oficial consolidada",
                "media_alternativa_consolidada": "Média Alternativa consolidada",
                "divergencia_consolidada": "Divergência consolidada (%)",
                "status_consolidado": "Status consolidado",
                "prioridade": "Prioridade",

            }
        )

        colunas_criticos = [
            "Placa",
            "Telemetria Válida",
            "Dias válidos",
            "Dias críticos",
            "% Média Oficial consolidada",
            "Média Alternativa consolidada",
            "Divergência consolidada (%)",
            "Status consolidado",
            "Prioridade",
            ]    

        top_criticos_exibir["% Média Oficial consolidada"] = (
            top_criticos_exibir["% Média Oficial consolidada"].round(2)
        )

        top_criticos_exibir["Média Alternativa consolidada"] = (
            top_criticos_exibir["Média Alternativa consolidada"].round(2)
        )

        top_criticos_exibir["Divergência consolidada (%)"] = (
            top_criticos_exibir["Divergência consolidada (%)"].round(2)
        )
    
        st.divider()
        st.subheader("Top veículos críticos consolidados")

        if top_criticos_exibir.empty:
            st.success("Nenhum veículo crítico identificado no consolidado do período")

        else:
            st.dataframe(
                top_criticos_exibir[colunas_criticos],
                width="stretch"
            )

elif pagina_app == "🤖 Análise IA":

    st.title("🤖 Análise IA")
    st.markdown("Diagnóstico inteligente por veículo com base nas divergências de telemetria.")

    if arquivo is not None:
        df_ia = processar_dataframe(pd.read_excel(arquivo, header=2))

        placas = sorted(df_ia["Placa"].dropna().unique())
        placa_selecionada = st.selectbox("Selecione o veículo", placas)

        dados_placa = df_ia[df_ia["Placa"] == placa_selecionada].copy()

        #Converte colunas numéricas para evitar erro com texto, vazio ou valores nulos
        dados_placa["%Média"] = pd.to_numeric(dados_placa["%Média"], errors="coerce")
        dados_placa["Media_Alternativa"] = pd.to_numeric(dados_placa["Media_Alternativa"], errors="coerce")
        dados_placa["Divergencia"] = pd.to_numeric(dados_placa["Divergencia"], errors="coerce")
        dados_placa["Score_Confiabilidade"] = pd.to_numeric(dados_placa["Score_Confiabilidade"], errors="coerce")

        #Indicadores consolidados da placa no período
        dias_analisados = len(dados_placa)
        media_oficial_consolidada = dados_placa["%Média"].mean()
        media_alternativa_consolidada = dados_placa["Media_Alternativa"].mean()
        dias_criticos = len(dados_placa[dados_placa["Divergencia"] > 10])

        #Divergência consolidada entre a média oficial e a média alternativa do período
        if pd.notna(media_oficial_consolidada) and media_oficial_consolidada != 0 and pd.notna(media_alternativa_consolidada):
            divergencia_consolidada = abs(
                (media_alternativa_consolidada - media_oficial_consolidada) / media_oficial_consolidada
            ) * 100
        else:
            divergencia_consolidada = None

        #Status principal baseado na divergência consolidada        
        status = classificar_status_por_divergencia(divergencia_consolidada)
        score_ia = calcular_score_por_status(status)

        #Pega informações cadastrais da primeira ocorrência válida da placa
        telemetria_valida = (
            dados_placa["Telemetria Válida"]
            .dropna()
            .iloc[0]
            if not dados_placa["Telemetria Válida"].dropna().empty
            else "Não informado"
        )

        st.divider()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Divergência Consolidada",
                formatar_percentual(divergencia_consolidada)
            )

        with col2:
            st.metric(
                "Dias analisados",
                dias_analisados
            )

        with col3:
            st.metric(
                "Dias críticos",
                dias_criticos
            )        

        with col4:
            st.metric(
                "Status",
                status
        
            )

        st.markdown(f"""
        **Placa:** {placa_selecionada}  
        **Telemetria Válida:** {telemetria_valida}  
        **Status consolidado:** {status}  
        """)                

        st.subheader("Consolidado do veículo")

        col_a, col_b, col_c = st.columns(3)

        with col_a:
            st.metric(
                "% Média Oficial consolidada",
                formatar_percentual(media_oficial_consolidada)
            )

        with col_b:
            st.metric(
                "Média Alternativa consolidada",
                formatar_percentual(media_alternativa_consolidada)
            )    

        with col_c:
            st.metric(
                "Score IA",
                f"{score_ia} / 100"
            )

        st.subheader("🧠 Diagnóstico Inteligente")

        if status == "OK":
            st.success("✅ No consolidado do período, as telemetrias estão consistentes.")
        elif status == "Atenção":
            st.warning("⚠️ Divergência moderada no consolidado do período. Recomenda-se acompanhar o veículo.")
        elif status == "Crítico":
            st.error("🚨 Divergência crítica no consolidado do período. Recomenda-se validar o histórico de telemetria.")
        elif status == "Baixa rodagem":
            st.info("ℹ️ Veículo com baixa rodagem. A amostra é insuficiente para uma comparação confiável.")
        else:
            st.info("Não foi possível realizar comparação entre as telemetrias.")

        st.markdown("### Observação automática")
        
        if status == "OK" and dias_criticos == 0:
            observacao_automatica = (
                "No consolidado do período, a divergência está dentro do padrão esperado "
                "e não houve dias críticos registrados para esta placa."

            )
        elif status == "OK" and dias_criticos > 0:
            observacao_automatica = (
                f"No consolidado do período, a divergência está dentro do padrão esperado. "
                f"Apesar disso, a placa apresentou {dias_criticos} dia(s) crítico(s), "
                "o que pode indicar oscilações pontuais entre as telemetrias."
            )  
              
        elif status == "Atenção":
            observacao_automatica = (
                f"A placa apresentou divergência moderada no consolidado do período "
                f"e teve {dias_criticos} dia(s) crítico(s). Recomenda-se acompanhar se o comportamento se repete."
            )       


        elif status == "Crítico":
            observacao_automatica = (
                f"A placa apresentou divergência crítica no consolidado do período "
                f"e teve {dias_criticos} dia(s) crítico(s). Recomenda-se priorizar a validação da telemetria."
            )

        elif status == "Baixa rodagem":
            observacao_automatica = (
                "Veículo com baixa rodagem no período analisado. A amostra pode ser insuficiente para uma comparação confiável."
           )            
        else:
            observacao_automatica = (
                "Não há dados suficientes para comparação entre as telemetrias."
            
            ) 

        st.write(observacao_automatica)      

        st.divider()

        st.subheader("💬 Chat com Agente de Auditoria")
        st.markdown("Faça perguntas sobre a auditoria, veículos críticos, prioridades ou recomendações operacionais.")

        # Monta contexto para o prompt do agente
        df_validos = df_ia[df_ia["Status"].isin(["OK", "Atenção", "Crítico"])].copy()
        total = len(df_ia)
        ok = len(df_ia[df_ia["Status"] == "OK"])
        atencao = len(df_ia[df_ia["Status"] == "Atenção"])
        critico = len(df_ia[df_ia["Status"] == "Crítico"])
        sem_comparacao = len(df_ia[df_ia["Status"] == "Sem comparação"])
        baixa_rodagem = len(df_ia[df_ia["Status"] == "Baixa rodagem"])
        maior_divergencia = df_validos["Divergencia"].max()
        media_divergencia = df_validos["Divergencia"].mean()

        # Converte somente as colunas relevantes em texto para limitar o contexto
        # enviado ao modelo e evitar o compartilhamento desnecessário de dados.
        top_criticos_chat = df_ia[df_ia["Status"] == "Crítico"].sort_values(
            by="Divergencia", ascending=False
        ).head(10)

        contexto_criticos = top_criticos_chat[[
            "Placa", "Telemetria Válida", "%Média", "Media_Alternativa",
            "Divergencia", "KM Válido", "Score_Confiabilidade", "Status"
        ]].to_string(index=False)

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
                    st.error("Não foi possível consultar a IA neste momento.")
                    st.caption(str(erro))

    else:
        st.warning("Envie uma planilha na barra lateral para gerar o diagnóstico.")


elif pagina_app == "📋 Auditoria Completa":

    st.title("📋 Auditoria Completa")

    st.markdown("Visualize todos os registros tratados da auditoria, com filtros e paginação.")

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

        # Usa a telemetria oposta à válida para calcular a média de comparação
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

        col1, col2 = st.columns([1, 1])

        with col1:
            placa_selecionada = st.selectbox(
                "🔎 Buscar placa",
                ["Todas"] + sorted(
                    df_auditoria["Placa"]
                    .dropna()
                    .astype(str)
                    .unique()
                )
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

        # Aplica filtros de status e busca por placa
        if filtro_status == "Todos":
            df_filtrado_auditoria = df_auditoria.copy()
        else:
            df_filtrado_auditoria = df_auditoria[
                df_auditoria["Status"] == filtro_status
            ].copy()

        if placa_selecionada != "Todas":
            df_filtrado_auditoria = df_filtrado_auditoria[
                df_filtrado_auditoria["Placa"].astype(str) == placa_selecionada
            ]

        colunas_exibir = [
            "Peso da Carga", "Placa", "KM Válido", "Comb Válido",
            "Telemetria Válida", "Set Nativo", "Set Retrac", "%Média", "Meta",
            "KM_Nativo", "Comb_Nativo", "KM_Retrac", "Comb_Retrac",
            "Média Alternativa (%)", "Divergência (%)", "Status", "Observacao_IA",
            "Score_Confiabilidade",
        ]

        # Lê valores salvos na sessão para calcular a tabela antes de exibir os widgets
        # Lê valores salvos na sessão para calcular a tabela antes de exibir os widgets
        registros_por_pagina = st.session_state.get("registros_por_pagina_auditoria", 20)
        pagina = st.session_state.get("pagina_auditoria", 1)

        total_paginas = max(
            1,
            (len(df_filtrado_auditoria) - 1) // registros_por_pagina + 1
        )

        inicio = (pagina - 1) * registros_por_pagina
        fim = inicio + registros_por_pagina
        df_pagina = df_filtrado_auditoria.iloc[inicio:fim]

        st.caption(
            f"Exibindo {len(df_pagina)} registros de {len(df_filtrado_auditoria)} filtrados."
        )
        df_pagina_exibir = df_pagina.rename(
            columns={
                "Media_Alternativa": "Média Alternativa (%)",
                "Divergencia": "Divergência (%)"
            }
        )
        st.dataframe(
            df_pagina_exibir[colunas_exibir],
            width="stretch"
        )

        # Controles de paginação abaixo da tabela
        col_pag1, col_pag2 = st.columns([1, 1])

        with col_pag1:
            st.selectbox(
                "Registros por página",
                [10, 20, 50, 100],
                index=1,
                key="registros_por_pagina_auditoria"
            )

        with col_pag2:
            st.number_input(
                "Página",
                min_value=1,
                max_value=total_paginas,
                value=1,
                key="pagina_auditoria"
            )

elif pagina_app == "📥 Relatórios":

    st.title("📥 Relatórios")
    st.markdown("""
    Gere e baixe o relatório final da auditoria de telemetria com médias,
    divergências, status e observações inteligentes.
    """)

    filtro_status_relatorio = st.selectbox(
        "Filtrar relatório por status",
        ["Todos", "OK", "Atenção", "Crítico", "Sem comparação", "Baixa rodagem"]
    )

    if arquivo is not None:
        df_relatorio = processar_dataframe(pd.read_excel(arquivo, header=2))

        if filtro_status_relatorio != "Todos":
            df_relatorio = df_relatorio[df_relatorio["Status"] == filtro_status_relatorio]

        # Seleciona somente as informações relevantes para o relatório final,
        # evitando exportar todas as colunas da planilha original.
        df_relatorio_exportar = df_relatorio[
            [
                "Placa",
                "Telemetria Válida",
                "%Média",
                "Media_Alternativa",
                "Divergencia",
                "Status",
                "Observacao_IA",
                "Score_Confiabilidade"
            ]
        ].copy()

        df_relatorio_exportar = df_relatorio_exportar.rename(
            columns={
                "%Média": "Média Oficial (%)",
                "Media_Alternativa": "Média Alternativa (%)",
                "Divergencia": "Divergência (%)",
                "Observacao_IA": "Observação IA",
                "Score_Confiabilidade": "Score de Confiabilidade"
            }
        )

        df_relatorio_exportar.to_excel("relatorio_telemetria.xlsx", index=False, engine="openpyxl")

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