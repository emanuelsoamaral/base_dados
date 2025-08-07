import streamlit as st
import os
import pandas as pd
from pathlib import Path


st.set_page_config(page_title="Chat com IA", layout="wide")
st.title("🤖 Chat com IA")

# Caminho do arquivo
pasta_datasets = Path("datasets")
pasta_datasets.mkdir(exist_ok=True)
arquivo_excel = pasta_datasets / 'vendas_certo.xlsx'

# Carregar ou criar DataFrame
if arquivo_excel.exists():
    df_vendas = pd.read_excel(arquivo_excel, engine='openpyxl')
else:
   
    df_vendas = pd.DataFrame(columns=["id_venda", "data_emissao", "valor", "fornecedor", "descricao", "conta"])
data_emissao = st.text_input('Data:', key='data')

valor = st.text_input('Valor', key='valor')

fornecedor = st.text_input('Fornecedor:', key='fornecedor')

descricao = st.text_input('Descrição:', key='descricao')

conta = st.text_input('Conta:', key='conta')

# Agrupar e somar os valores por data de emissão
if not df_vendas.empty:
    # Converter a coluna 'valor' de texto para float
    df_vendas['valor_float'] = df_vendas['valor'].str.replace(',', '.', regex=False).astype(float)

    # Agrupar por data e somar
    vendas_por_dia = df_vendas.groupby('data_emissao')['valor_float'].sum().sort_values(ascending=False)

    # Exibir gráfico
    st.subheader("Total de vendas por dia")
    st.bar_chart(vendas_por_dia)

    # Mostrar qual dia mais vendeu
    dia_top = vendas_por_dia.idxmax()
    valor_top = vendas_por_dia.max()
    st.info(f"🟢 Dia com maior venda: **{dia_top}** – R$ {valor_top:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
