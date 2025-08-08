import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Gráficos de Vendas", layout="wide")

st.title("📊 Análise de Lançamentos")

# Caminho da planilha
arquivo_excel = Path("datasets/vendas_certo.xlsx")
arquivo_excel.parent.mkdir(exist_ok=True)  # cria a pasta se não existir

# Função para carregar os dados
def carregar_dados():
    if arquivo_excel.exists():
        return pd.read_excel(arquivo_excel, engine="openpyxl")
    return pd.DataFrame(columns=["data_emissao", "fornecedor", "valor"])

# Função para salvar os dados
def salvar_dados(df):
    df.to_excel(arquivo_excel, index=False, engine="openpyxl")

# Carregar dados existentes
df = carregar_dados()

# --- Formulário para adicionar novos dados ---
with st.form("form_lancamento"):
    data_emissao = st.text_input("Data de Emissão (dd/mm/aaaa)")
    fornecedor = st.text_input("Fornecedor")
    valor = st.text_input("Valor (ex: 1500,50)")
    submit = st.form_submit_button("Adicionar Lançamento")

    if submit:
        if data_emissao and fornecedor and valor:
            novo_registro = pd.DataFrame({
                "data_emissao": [data_emissao],
                "fornecedor": [fornecedor],
                "valor": [valor]
            })
            df = pd.concat([df, novo_registro], ignore_index=True)
            salvar_dados(df)  # salva no Excel
            st.success("✅ Lançamento adicionado com sucesso!")
        else:
            st.error("Preencha todos os campos.")

# --- Análise de vendas ---
if df.empty:
    st.warning("Nenhuma venda cadastrada ainda.")
else:
    # Conversão de valores e datas
    df['valor_float'] = df['valor'].str.replace(',', '.', regex=False).astype(float)
    df['data_emissao_dt'] = pd.to_datetime(df['data_emissao'], format="%d/%m/%Y", errors='coerce')
    df = df.dropna(subset=['data_emissao_dt'])

    # Agrupar e ordenar por data
    vendas_dia = df.groupby(df['data_emissao_dt'].dt.strftime('%d/%m/%Y'))['valor_float'].sum().reset_index()
    vendas_dia['data_ordem'] = pd.to_datetime(vendas_dia['data_emissao'], format="%d/%m/%Y")
    vendas_dia = vendas_dia.sort_values(by="data_ordem", ascending=True)

    # Agrupar fornecedores
    vendas_fornecedor = df.groupby("fornecedor")['valor_float'].sum().reset_index().sort_values(by="valor_float", ascending=False)

    # --- Gráfico de barras por data ---
    st.subheader("🔹 Total lançado por data")
    fig_bar_dia = px.bar(vendas_dia, x="data_emissao", y="valor_float", text="valor_float")
    fig_bar_dia.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig_bar_dia.update_xaxes(tickangle=0, title="Data")
    st.plotly_chart(fig_bar_dia, use_container_width=True)

    # --- Gráfico de barras por fornecedor ---
    st.subheader("🔸 Total lançado por fornecedor")
    fig_bar_fornecedor = px.bar(vendas_fornecedor, x="fornecedor", y="valor_float", text="valor_float")
    fig_bar_fornecedor.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig_bar_fornecedor.update_xaxes(tickangle=0, title="Fornecedor")
    st.plotly_chart(fig_bar_fornecedor, use_container_width=True)

    # --- Gráfico de pizza por data (ordenado pelas maiores vendas) ---
    st.subheader("🥧 Proporção de Vendas por Data")
    vendas_dia_pizza = vendas_dia.sort_values(by="valor_float", ascending=False)
    fig_pizza = px.pie(vendas_dia_pizza, names="data_emissao", values="valor_float", title="Proporção de Vendas por Data")
    fig_pizza.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pizza, use_container_width=True)

    # Destaques
    st.markdown("---")
    dia_max = vendas_dia.loc[vendas_dia['valor_float'].idxmax(), 'data_emissao']
    fornecedor_max = vendas_fornecedor.iloc[0]['fornecedor']
    st.success(f"📅 Dia com maior lançamento: **{dia_max}** — R$ {vendas_dia['valor_float'].max():,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    st.success(f"🏢 Fornecedor com maior total: **{fornecedor_max}** — R$ {vendas_fornecedor.iloc[0]['valor_float']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
