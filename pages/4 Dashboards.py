import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Dashboards", page_icon="📊", layout="wide")

st.title("📊 Dashboards - Dados Lançados")

# Caminho do arquivo
pasta_datasets = Path("datasets")
arquivo_excel = pasta_datasets / "vendas_certo.xlsx"

# Carregar os dados
if not arquivo_excel.exists():
    st.error("Arquivo de dados não encontrado. Certifique-se de que o arquivo 'vendas_certo.xlsx' está na pasta datasets.")
    st.stop()

df = pd.read_excel(arquivo_excel)

# Padronizar nomes das colunas
df.columns = df.columns.str.strip().str.lower()

# Verificar se colunas necessárias existem
colunas_necessarias = ["data emissão", "valor em reais:"]
for col in colunas_necessarias:
    if col not in df.columns:
        st.error(f"A coluna '{col}' não foi encontrada no arquivo. Colunas disponíveis: {list(df.columns)}")
        st.stop()

# Converter data e valores
df["data_emissao"] = pd.to_datetime(df["data emissao"], errors="coerce")
df["valor_float"] = pd.to_numeric(df["valor em reais:"], errors="coerce")

# Remover linhas inválidas
df = df.dropna(subset=["data_emissao", "valor_float"])

# Agrupar por dia
vendas_dia_df = df.groupby("data_emissao", as_index=False)["valor_float"].sum()

# Ordenar por data crescente
vendas_dia_df = vendas_dia_df.sort_values("data_emissao")

# Gráfico 1 - Barra por dia
fig_bar_dia = px.bar(
    vendas_dia_df,
    x="data_emissao",
    y="valor_float",
    text="valor_float",
    title="Dados Lançados por Dia",
)
fig_bar_dia.update_traces(texttemplate='%{text:.2f}', textposition="outside")
fig_bar_dia.update_layout(xaxis_title="Data", yaxis_title="Valor (R$)")

# Gráfico 2 - Linha por dia
fig_linha_dia = px.line(
    vendas_dia_df,
    x="data_emissao",
    y="valor_float",
    markers=True,
    title="Evolução dos Dados Lançados por Dia"
)
fig_linha_dia.update_layout(xaxis_title="Data", yaxis_title="Valor (R$)")

# Exibir gráficos lado a lado
col1, col2 = st.columns(2)
col1.plotly_chart(fig_bar_dia, use_container_width=True)
col2.plotly_chart(fig_linha_dia, use_container_width=True)
