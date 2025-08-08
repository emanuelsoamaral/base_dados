import streamlit as st
import pandas as pd
from pathlib import Path
import base64

# --- Configuração Inicial ---
st.set_page_config(page_title="Relatórios", layout="wide")

# Caminho do arquivo
pasta_datasets = Path("datasets")
arquivo_excel = pasta_datasets / 'vendas_certo.xlsx'

# --- Carregar Dados ---
@st.cache_data
def load_data():
    """Carrega o DataFrame do arquivo Excel."""
    if arquivo_excel.exists():
        df = pd.read_excel(arquivo_excel, engine='openpyxl')
        return df
    else:
        st.warning("O arquivo 'vendas_certo.xlsx' não foi encontrado. Por favor, adicione lançamentos na página principal primeiro.")
        return pd.DataFrame()

df_vendas = load_data()

# Se o DataFrame estiver vazio, não continue
if df_vendas.empty:
    st.info("Nenhum dado para exibir. Adicione lançamentos na página principal.")
    st.stop()


# --- Sidebar ---
st.sidebar.header("Filtros do Relatório")
datas_unicas = sorted(df_vendas['data_emissao'].unique())
data_selecionada = st.sidebar.selectbox("Selecione uma data:", options=datas_unicas)


# --- Lógica de Geração do Relatório ---
st.title(f"Relatório de Vendas do Dia {data_selecionada}")
st.write("---")

df_filtrado = df_vendas[df_vendas['data_emissao'] == data_selecionada]

if not df_filtrado.empty:
    # Exibir o DataFrame filtrado
    st.dataframe(df_filtrado, use_container_width=True)

    # --- Sumário dos Lançamentos ---
    total_valor = df_filtrado['valor'].str.replace(',', '.').astype(float).sum()
    st.markdown(f"**Total de Lançamentos:** {len(df_filtrado)}  |  **Valor Total:** R$ {total_valor:,.2f}")
    st.write("---")

    # --- Opção de Impressão ---
    def get_table_download_link(df):
        """Cria um link para download de um CSV (que pode ser impresso)."""
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  # Codifica em base64
        href = f'<a href="data:file/csv;base64,{b64}" download="relatorio_vendas_{data_selecionada.replace("/", "-")}.csv">📥 Baixar Relatório em CSV (para impressão)</a>'
        return href

    st.markdown(get_table_download_link(df_filtrado), unsafe_allow_html=True)
else:
    st.warning(f"Nenhum lançamento encontrado para a data **{data_selecionada}**.")