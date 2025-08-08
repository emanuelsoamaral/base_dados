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
    df_vendas.to_excel(arquivo_excel, index=False, engine='openpyxl')  # cria o arquivo vazio

# Inputs do formulário
col_a, col_b = st.columns(2)
data_input = col_a.text_input('Data (dd/mm/aaaa):', key='data')
valor_input = col_b.text_input('Valor (ex: 9999,99)', key='valor')

fornecedor = st.text_input('Fornecedor:', key='fornecedor')
descricao = st.text_input('Descrição:', key='descricao')
conta = st.text_input('Conta:', key='conta')

# Validação com regex
padrao_data = r'^\d{2}/\d{2}/\d{4}$'      # dd/mm/aaaa
padrao_valor = r'^\d{1,20},\d{2}$'         # até 20 dígitos antes da vírgula, 2 após

if st.button('💾 GRAVAR'):
    if not re.match(padrao_data, data_input):
        st.error('Data inválida. Use o formato dd/mm/aaaa.')
    elif not re.match(padrao_valor, valor_input):
        st.error('Valor inválido. Use o formato 9999,99.')
    elif not fornecedor or not descricao or not conta:
        st.error('Preencha todos os campos obrigatórios.')
    else:
        try:
            novo_id = int(df_vendas['id_venda'].max()) + 1 if not df_vendas.empty else 1
            nova_linha = pd.DataFrame([{
                "id_venda": novo_id,
                "data_emissao": data_input,
                "valor": valor_input,
                "fornecedor": fornecedor,
                "descricao": descricao,
                "conta": conta
            }])
            df_vendas = pd.concat([df_vendas, nova_linha], ignore_index=True)
            df_vendas.to_excel(arquivo_excel, index=False, engine='openpyxl')  # Salva no Excel
            st.success('✅ Dado adicionado com sucesso e salvo no arquivo!')
        except Exception as e:
            st.error(f"Erro ao adicionar os dados: {e}")


