import streamlit as st
import pandas as pd
from pathlib import Path
import base64
import datetime

# --- Configuração Inicial ---
st.set_page_config(page_title="Relatórios", layout="wide")

# Caminho do arquivo
pasta_datasets = Path("datasets")
arquivo_excel = pasta_datasets / 'vendas_certo.xlsx'

# --- Funções Auxiliares ---
def converter_data(data_str):
    """Converte string 'dd/mm/aaaa' para objeto datetime, removendo espaços."""
    try:
        # A linha abaixo foi alterada para remover espaços em branco
        data_limpa = data_str.strip()
        return datetime.datetime.strptime(data_limpa, '%d/%m/%Y').date()
    except (ValueError, TypeError) as e:
        # Se der erro, retorna None
        return None

@st.cache_data
def load_data():
    """Carrega o DataFrame do arquivo Excel e converte a coluna de data."""
    if arquivo_excel.exists():
        df = pd.read_excel(arquivo_excel, engine='openpyxl')
        # Garante que a coluna é string antes de processar
        df['data_emissao'] = df['data_emissao'].astype(str)
        df['data_objeto'] = df['data_emissao'].apply(converter_data)
        # Remove linhas com datas inválidas
        df.dropna(subset=['data_objeto'], inplace=True)
        # Ordena os dados pela data
        df.sort_values(by='data_objeto', inplace=True)
        return df
    else:
        st.warning("O arquivo 'vendas_certo.xlsx' não foi encontrado.")
        return pd.DataFrame()

# --- Carregar Dados ---
df_vendas = load_data()

if df_vendas.empty:
    st.info("Nenhum dado válido para exibir. Adicione lançamentos na página principal.")
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
    # Exibe o sumário
    total_valor = df_filtrado['valor'].str.replace(',', '.').astype(float).sum()
    st.markdown(f"**Total de Lançamentos:** {len(df_filtrado)}  |  **Valor Total:** R$ {total_valor:,.2f}")
    st.write("---")

    # Exibe cada lançamento por extenso
    for _, row in df_filtrado.iterrows():
        valor_formatado = f"R$ {float(row['valor'].replace(',', '.')):,.2f}"
        st.markdown(
            f"""
            - **ID:** {int(row['id_venda'])}
            - **Data:** {row['data_emissao']}
            - **Fornecedor:** {row['fornecedor']}
            - **Descrição:** {row['descricao']}
            - **Conta:** {row['conta']}
            - **Valor:** {valor_formatado}
            """
        )
        st.markdown("---")

    # --- Opção de Impressão (Download) ---
    def get_table_download_link(df):
        """Cria um link para download de um CSV."""
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="relatorio_vendas_{data_selecionada.replace("/", "-")}.csv">📥 Baixar Relatório em CSV</a>'
        return href

    st.markdown(get_table_download_link(df_filtrado), unsafe_allow_html=True)
else:
    st.warning(f"Nenhum lançamento encontrado para a data **{data_selecionada}**.")