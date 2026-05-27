import streamlit as st 
import pandas as pd
import re 
import plotly.express as px


st.title("Blitz Inteligente de Telemetria")

arquivo = st.file_uploader("Envie a planilha Excel", type=["xlsx"])

def extrair_dados(texto):
  numeros = re.findall(r'\d+', str(texto))

  if len(numeros) >=2:
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
    divergencia = abs(
      (media_alternativa - media_oficial) / media_oficial
    ) * 100

    return round(divergencia, 2)
  
  except:
    return None

def classificar_divergencia(divergencia):
  
  try:

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
  
  return ""

def colorir_status(valor):
  if valor == "OK":
    return "background-color: #b6fcb6"
  elif valor == "Atenção":
    return "background-color: #fff3b0"
  elif valor == "Crítico":
    return "background-color: #ffb3b3"
  elif valor == "Sem comparação":
    return "background-color: #d9d9d9"

  return ""

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

    peso = float(str(row["Peso da Carga"]).replace(".", ""))
    meta = row["Meta"]

    if "Retrac" in telemetria:

      media = calcular_media (
        row["KM_Nativo"],
        row["Comb_Nativo"],
        meta
      )

      df.at[index, "Media_Alternativa"] = media

    else:

      media = calcular_media (
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

  df["Status"] = df["Divergencia"].apply(
    classificar_divergencia
  )

  df["Observacao_IA"] = df.apply(
    lambda row: gerar_observacao(
      row["Status"],
      row["Divergencia"]
    ),
    axis=1
  )

  total = len(df)
  ok = len(df[df["Status"] == "OK"])
  atencao = len(df[df["Status"] == "Atenção"])
  critico = len(df[df["Status"] == "Crítico"])
  sem_comparacao = len(df[df["Status"] == "Sem comparação"])

  col1, col2, col3, col4, col5 = st.columns(5)
  col1.metric("Total", total)
  col2.metric("OK", ok)
  col3.metric("Atenção", atencao)
  col4.metric("Crítico", critico)
  col5.metric("Sem Comparação", sem_comparacao)

  dados_grafico = pd.DataFrame({
    "Status": ["OK", "Atenção", "Crítico", "Sem comparação"],
    "Quantidade": [ok, atencao, critico, sem_comparacao]
  })

  grafico = px.bar(
    dados_grafico,
    x="Status",
    y="Quantidade",
    color="Status",
    title="Resumo do status"
  )

  st.plotly_chart(grafico, use_container_width=True)

  st.subheader("Veículos mais críticos")

  top_criticos = df.sort_values(
    by="Divergencia",
    ascending=False
  ).head(10)

  colunas_criticos = [
    "Telemetria Válida",
    "Divergencia",
    "Status",
    "Observacao_IA"
  ]

  st.dataframe(
    top_criticos[colunas_criticos]
  )

  filtro_status = st.selectbox(
    "Filtar por status",
    [
      "Todos",
      "OK",
      "Atenção",
      "Crítico",
      "Sem comparação"
    ]
  )

  if filtro_status == "Todos":
    df_filtrado = df

  else:
    df_filtrado = df[
      df["Status"] == filtro_status
    ]

  st.write("Dados tratados:")

  colunas_exibir = [
    "Peso da Carga",
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
    "Observacao_IA"
    

  ]

  tabela_estilizada = df_filtrado[colunas_exibir].style.map(
    colorir_status,
    subset=["Status"]
)

  st.dataframe(tabela_estilizada)
  
  excel = df_filtrado.to_excel(
    "relatorio_telemetria.xlsx",
    index=False,
    engine="openpyxl"
  )

  with open("relatorio_telemetria.xlsx", "rb") as arquivo_excel:
    st.download_button(
      label="Baixar relatório em Excel",
      data=arquivo_excel,
      file_name="relatorio_telemetria.xlsx",
      mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
