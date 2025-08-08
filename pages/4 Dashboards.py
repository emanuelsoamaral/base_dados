import streamlit as st
import pandas as pd
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

        if df.empty:
            st.warning("Nenhuma venda cadastrada ainda.")
        else:
            # Converter valores e datas
            df['valor_float'] = df['valor'].str.replace(',', '.', regex=False).astype(float)
            df['data_emissao_dt'] = pd.to_datetime(df['data_emissao'], format="%d/%m/%Y", errors='coerce')

        # Remover linhas com datas inválidas
        df = df.dropna(subset=['data_emissao_dt'])

        # Gráfico 1 – Vendas por dia
        st.subheader("🔹 Total lançado por data")
        vendas_dia = df.groupby("data_emissao")['valor_float'].sum().sort_index()
        st.bar_chart(vendas_dia)

        # Gráfico 2 – Vendas por fornecedor
        st.subheader("🔸 Total lançado por fornecedor")
        vendas_fornecedor = df.groupby("fornecedor")['valor_float'].sum().sort_values(ascending=False)
        st.bar_chart(vendas_fornecedor)

        # Destaques
        st.markdown("---")
        st.success(f"📅 Dia com maior lançamentos: **{vendas_dia.idxmax()}** — R$ {vendas_dia.max():,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        st.success(f"🏢 Fornecedor com maior total: **{vendas_fornecedor.idxmax()}** — R$ {vendas_fornecedor.max():,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
