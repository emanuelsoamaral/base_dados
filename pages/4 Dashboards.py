import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Gráficos de Vendas", layout="wide")

st.title("📊 Análise de Lançamentos")

# Caminho e leitura
arquivo_excel = Path("datasets/vendas_certo.xlsx")

if not arquivo_excel.exists():
    st.warning("Nenhuma venda cadastrada ainda.")
else:
    df = pd.read_excel(arquivo_excel, engine='openpyxl')

    if df.empty:
        st.warning("Nenhuma venda cadastrada ainda.")
    else:
        # Converter valor para float
        df['valor_float'] = df['valor'].str.replace(',', '.', regex=False).astype(float)
        df['data_emissao_dt'] = pd.to_datetime(df['data_emissao'], format="%d/%m/%Y", errors='coerce')

        # Remover linhas com datas inválidas
        df = df.dropna(subset=['data_emissao_dt'])

        # Agrupamento por data
        vendas_dia = df.groupby("data_emissao")['valor_float'].sum().sort_index()
        vendas_dia_df = vendas_dia.reset_index()

        # Agrupamento por fornecedor
        vendas_fornecedor = df.groupby("fornecedor")['valor_float'].sum().sort_values(ascending=False)
        vendas_fornecedor_df = vendas_fornecedor.reset_index()

        # --- Gráfico 1 – Vendas por dia ---
        st.subheader("Total lançado por data")
        fig_bar_dia = px.bar(vendas_dia_df, x="Data emetida", y="Valor em reais:", text="Valor:")
        fig_bar_dia.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig_bar_dia.update_xaxes(tickangle=0)  # Mantém horizontal
        st.plotly_chart(fig_bar_dia, use_container_width=True)

        # --- Gráfico 2 – Vendas por fornecedor ---
        st.subheader("Total lançado por fornecedor")
        fig_bar_fornecedor = px.bar(vendas_fornecedor_df, x="Fornecedor", y="Valor em reais:", text="Valor:")
        fig_bar_fornecedor.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig_bar_fornecedor.update_xaxes(tickangle=0)  # Horizontal
        st.plotly_chart(fig_bar_fornecedor, use_container_width=True)

        # --- Gráfico 3 – Pizza: proporção de vendas por data ---
        st.subheader("Proporção de Vendas por Data")
        fig_pizza = px.pie(vendas_dia_df, names="data_emissao", values="valor_float", title="Proporção de Vendas por Data")
        fig_pizza.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pizza, use_container_width=True)

        # Destaques
        st.markdown("---")
        st.success(f"📅 Dia com maior lançamentos: **{vendas_dia.idxmax()}** — R$ {vendas_dia.max():,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        st.success(f"🏢 Fornecedor com maior total: **{vendas_fornecedor.idxmax()}** — R$ {vendas_fornecedor.max():,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
