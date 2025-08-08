import streamlit as st
import pandas as pd
from pathlib import Path
import re

# Caminho do arquivo
pasta_datasets = Path("datasets")
pasta_datasets.mkdir(exist_ok=True)
arquivo_excel = pasta_datasets / 'vendas_certo.xlsx'

# Configuração da página
st.set_page_config(page_title="Formulário", layout="wide")

# Carregar ou criar DataFrame
if arquivo_excel.exists():
    df_vendas = pd.read_excel(arquivo_excel, engine='openpyxl')
else:
    df_vendas = pd.DataFrame(columns=["id_venda", "data_emissao", "valor", "fornecedor", "descricao", "conta"])

# Inputs do formulário
col1, col2 = st.columns(2)

col1 = st.text_input('Data:', key='data')

col2 = st.text_input('Valor', key='valor')

fornecedor = st.text_input('Fornecedor:', key='fornecedor')

descricao = st.text_input('Descrição:', key='descricao')

conta = st.text_input('Conta:', key='conta')

# Validação com regex
padrao_data = r'^\d{2}/\d{2}/\d{4}$'      # dd/mm/aaaa
padrao_valor = r'^\d{1,20},\d{2}$'         # até 6 dígitos antes da vírgula, 2 após

if st.button('GRAVAR'):
    if not re.match(padrao_data, col1):
        st.error('Data inválida. Use o formato dd/mm/aaaa.')
    elif not re.match(padrao_valor, col2):
        st.error('Valor inválido. Use o formato 9999,99.')
    elif not fornecedor or not descricao or not conta:
        st.error('Preencha todos os campos obrigatórios.')
    else:
        try:
            novo_id = int(df_vendas['id_venda'].max()) + 1 if not df_vendas.empty else 1
            nova_linha = pd.DataFrame([{
                "id_venda": novo_id,
                "data_emissao": col1,
                "valor": col2,
                "fornecedor": fornecedor,
                "descricao": descricao,
                "conta": conta  
            }])
            df_vendas = pd.concat([df_vendas, nova_linha], ignore_index=True)
            df_vendas.to_excel(arquivo_excel, index=False, engine='openpyxl')
            st.success('Dado adicionado com sucesso')
        except Exception as e:
            st.error(f"Erro ao adicionar os dados: {e}")

