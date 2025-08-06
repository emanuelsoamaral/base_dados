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
st.markdown("<h1 style='text-align: center; font-weight:bold; color: green;'>Cadastro de lançamentos</h1>", unsafe_allow_html=True)

st.markdown("<h3 style='color:#444;'>Data de emissão:</h3>", unsafe_allow_html=True)
data_emissao = st.text_input('', key='data')

st.markdown("<h3 style='color:#444;'>Valor:</h3>", unsafe_allow_html=True)
valor = st.text_input('', key='valor')

st.markdown("<h3 style='color:#444;'>Fornecedor:</h3>", unsafe_allow_html=True)
fornecedor = st.text_input('', key='fornecedor')

st.markdown("<h3 style='color:#444;'>Descrição:</h3>", unsafe_allow_html=True)
descricao = st.text_input('', key='descricao')

st.markdown("<h3 style='color:#444;'>Conta:</h3>", unsafe_allow_html=True)
conta = st.text_input('', key='conta')

# Validação com regex
padrao_data = r'^\d{2}/\d{2}/\d{4}$'      # dd/mm/aaaa
padrao_valor = r'^\d{1,20},\d{2}$'         # até 6 dígitos antes da vírgula, 2 após

if st.button('GRAVAR'):
    if not re.match(padrao_data, data_emissao):
        st.error('Data inválida. Use o formato dd/mm/aaaa.')
    elif not re.match(padrao_valor, valor):
        st.error('Valor inválido. Use o formato 9999,99.')
    elif not fornecedor or not descricao or not conta:
        st.error('Preencha todos os campos obrigatórios.')
    else:
        try:
            novo_id = int(df_vendas['id_venda'].max()) + 1 if not df_vendas.empty else 1
            nova_linha = pd.DataFrame([{
                "id_venda": novo_id,
                "data_emissao": data_emissao,
                "valor": valor,
                "fornecedor": fornecedor,
                "descricao": descricao,
                "conta": conta  
            }])
            df_vendas = pd.concat([df_vendas, nova_linha], ignore_index=True)
            df_vendas.to_excel(arquivo_excel, index=False, engine='openpyxl')
            st.success('Dado adicionado com sucesso')
        except Exception as e:
            st.error(f"Erro ao adicionar os dados: {e}")

