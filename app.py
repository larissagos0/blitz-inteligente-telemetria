import streamlit as st 
import pandas as pd
import re 

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
    
if arquivo is not None:
  df = pd.read_excel(arquivo, header=2)
  df["%Média"] = (df["%Média"] * 100)

  st.write("Dados da Planilha:")
  st.dataframe(df)

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
    "Media_Alternativa"
    

  ]

  st.dataframe(df[colunas_exibir])
