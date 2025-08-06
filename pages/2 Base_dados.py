import streamlit as st
import pandas as pd
from pathlib import Path
import re

st.set_page_config(page_title="Chat com IA", layout="wide")


pasta_datasets = Path("datasets")
pasta_datasets.mkdir(exist_ok=True)
arquivo_excel = pasta_datasets / 'vendas_certo.xlsx'

if arquivo_excel.exists():
    df_vendas = pd.read_excel(arquivo_excel, engine='openpyxl')
else:
    df_vendas = pd.DataFrame(columns=["id_venda", "data_emissao", "valor", "fornecedor", "descricao", "conta"])

st.subheader("Dados registrados")
st.dataframe(df_vendas)