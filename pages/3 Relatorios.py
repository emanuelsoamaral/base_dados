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
        data_limpa = data_str.strip()
        return datetime.datetime.strptime(data_limpa, '%d/%m/%Y').date()
    except (ValueError, TypeError):
        return None

@st.cache_data
def load_data():
    """Carrega o DataFrame do arquivo Excel e converte as colunas."""
    if arquivo_excel.exists():
        df = pd.read_excel(arquivo_excel, engine='openpyxl')
        
        df['data_emissao'] = df['data_emissao'].astype(str)
        df['valor'] = df['valor'].astype(str)

        df['data_objeto'] = df['data_emissao'].apply(converter_data)
        df.dropna(subset=['data_objeto'], inplace=True)
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
    total_valor = df_filtrado['valor'].astype(str).str.replace(',', '.').astype(float).sum()
    st.markdown(f"**Total de Lançamentos:** {len(df_filtrado)}  |  **Valor Total:** R$ {total_valor:,.2f}")
    st.write("---")

    # String para armazenar o texto do relatório
    relatorio_texto = ""
    relatorio_texto += f"Relatório de Vendas do Dia {data_selecionada}\n"
    relatorio_texto += "========================================\n\n"
    relatorio_texto += f"Total de Lançamentos: {len(df_filtrado)}\n"
    relatorio_texto += f"Valor Total: R$ {total_valor:,.2f}\n\n"
    relatorio_texto += "----------------------------------------\n\n"

    for _, row in df_filtrado.iterrows():
        valor_formatado = f"R$ {float(str(row['valor']).replace(',', '.')):,.2f}"
        
        # Exibe o texto na tela
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

        # Adiciona o texto ao relatório para download
        relatorio_texto += f"ID: {int(row['id_venda'])}\n"
        relatorio_texto += f"Data: {row['data_emissao']}\n"
        relatorio_texto += f"Fornecedor: {row['fornecedor']}\n"
        relatorio_texto += f"Descrição: {row['descricao']}\n"
        relatorio_texto += f"Conta: {row['conta']}\n"
        relatorio_texto += f"Valor: {valor_formatado}\n"
        relatorio_texto += "----------------------------------------\n\n"

    # --- Opção de Impressão (Download) ---
    def get_text_download_link(text_content, filename):
        """Cria um link para download de um arquivo de texto."""
        b64 = base64.b64encode(text_content.encode()).decode()
        href = f'<a href="data:text/plain;base64,{b64}" download="{filename}">📥 Baixar Relatório (texto para impressão)</a>'
        return href

    st.markdown(get_text_download_link(relatorio_texto, f"relatorio_vendas_{data_selecionada.replace('/', '-')}.txt"), unsafe_allow_html=True)

else:
    st.warning(f"Nenhum lançamento encontrado para a data **{data_selecionada}**.")