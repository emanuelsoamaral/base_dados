import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Dashboards", layout="wide")

st.title("📊 Dashboards - Dados Lançados")

# Caminho da planilha
pasta_datasets = Path("datasets")
arquivo_excel = pasta_datasets / "vendas_certo.xlsx"

# Verifica se arquivo existe
if not arquivo_excel.exists():
    st.warning("Nenhum dado lançado encontrado.")
    st.stop()

# Carrega planilha
df = pd.read_excel(arquivo_excel)

# Converte para datetime
df["Data emetida"] = pd.to_datetime(df["Data emetida"], dayfirst=True, errors="coerce")

# Remove linhas sem data
df = df.dropna(subset=["Data emetida"])

# Ordena por data crescente
df = df.sort_values(by="Data emetida")

# Agrupa por data
vendas_dia_df = df.groupby("Data emetida", as_index=False)["Valor em reais:"].sum()

# ----------- Gráfico de Barras (datas na horizontal) -----------
fig_bar_dia = px.bar(
    vendas_dia_df,
    x="Data emetida",
    y="Valor em reais:",
    text="Valor em reais:",
    title="📅 Valores por Data",
)
fig_bar_dia.update_traces(texttemplate='%{text:.2f}', textposition="outside")
fig_bar_dia.update_layout(
    xaxis_title="Data",
    yaxis_title="Valor (R$)",
    xaxis_tickformat="%d/%m/%Y",
)

# ----------- Gráfico de Pizza (proporção de vendas por data) -----------
fig_pizza = px.pie(
    vendas_dia_df,
    names="Data emetida",
    values="Valor em reais:",
    title="🍕 Proporção de Vendas por Data",
    hole=0.3
)
fig_pizza.update_traces(textinfo="percent+label")

# Exibe gráficos
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_bar_dia, use_container_width=True)
with col2:
    st.plotly_chart(fig_pizza, use_container_width=True)

# ----------- Exibe tabela final -----------
st.subheader("📄 Dados Lançados")
st.dataframe(df, use_container_width=True)
