import streamlit as st 
import pandas as pd

st.title("Blitz Inteligente de Telemetria")

arquivo = st.file_uploader("Envie a planilha Excel", type=["xlsx"])

if arquivo is not None:
  df = pd.read_excel(arquivo)

  st.write("Dados da Planilha:")
  st.dataframe(df)
  
