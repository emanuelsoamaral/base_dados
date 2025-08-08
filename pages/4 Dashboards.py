# 4 Dashboards.py
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import unicodedata, re, numpy as np

st.set_page_config(page_title="Dashboards", page_icon="📊", layout="wide")
st.title("📊 Dashboards - Dados Lançados")

# --- Helpers ---
def normalize_col(name):
    if pd.isna(name):
        return ""
    s = str(name).strip().lower()
    s = unicodedata.normalize('NFKD', s).encode('ascii','ignore').decode('ascii')
    s = re.sub(r'[^a-z0-9]+', '_', s)
    s = re.sub(r'_+', '_', s).strip('_')
    return s

def detect_columns(cols):
    norm = {c: normalize_col(c) for c in cols}
    date_col = None; valor_col = None; fornecedor_col = None
    for c,n in norm.items():
        if date_col is None and ('data' in n or 'date' in n) and ('emiss' in n or 'emet' in n or 'emit' in n or 'emissao' in n):
            date_col = c
        if valor_col is None and ('valor' in n or 'reais' in n or 'value' in n or 'amount' in n):
            valor_col = c
        if fornecedor_col is None and ('fornec' in n or 'supplier' in n):
            fornecedor_col = c
    # fallbacks
    if date_col is None:
        for c,n in norm.items():
            if 'data' in n or 'date' in n:
                date_col = c; break
    if valor_col is None:
        for c,n in norm.items():
            if 'valor' in n or 'value' in n or 'amount' in n:
                valor_col = c; break
    if fornecedor_col is None:
        for c,n in norm.items():
            if 'fornec' in n or 'supplier' in n:
                fornecedor_col = c; break
    return date_col, valor_col, fornecedor_col

def parse_numeric_value(s):
    if pd.isna(s):
        return np.nan
    s = str(s).strip()
    s = re.sub(r'[^\d,.\-]', '', s)  # remove currency symbols and spaces
    if s == '': return np.nan
    if s.count('.')>0 and s.count(',')>0:
        s = s.replace('.','').replace(',','.')
    else:
        if s.count(',')==1 and s.count('.')==0:
            s = s.replace(',','.')
        elif s.count('.')>1:
            s = s.replace('.','')
    try:
        return float(s)
    except:
        return np.nan

# --- Load file ---
pasta = Path("datasets")
arquivo_excel = pasta / "vendas_certo.xlsx"

if not arquivo_excel.exists():
    st.error("Arquivo 'datasets/vendas_certo.xlsx' não encontrado. Adicione dados pela página de cadastro antes de abrir este dashboard.")
    st.stop()

# read
df = pd.read_excel(arquivo_excel)
orig_cols = list(df.columns)

# detect/mapping
date_col, valor_col, fornecedor_col = detect_columns(orig_cols)
if date_col is None or valor_col is None:
    st.error(f"Não foi possível identificar colunas de data/valor no arquivo. Colunas encontradas: {orig_cols}")
    st.stop()

df = df.rename(columns={date_col: 'data_emissao', valor_col: 'valor_raw'})
if fornecedor_col is not None:
    df = df.rename(columns={fornecedor_col: 'fornecedor'})

# parse date and value
df['data_emissao'] = pd.to_datetime(df['data_emissao'], dayfirst=True, errors='coerce', infer_datetime_format=True)
# try fallback replacing '-' with '/'
if df['data_emissao'].isna().any():
    df['data_emissao'] = df['data_emissao'].fillna(pd.to_datetime(df['data_emissao'].astype(str).str.replace('-','/'), dayfirst=True, errors='coerce', infer_datetime_format=True))

df['valor_float'] = df['valor_raw'].apply(parse_numeric_value)

# drop invalid rows
df = df.dropna(subset=['data_emissao','valor_float']).copy()

if df.empty:
    st.warning("Nenhum dado válido após conversão (verifique formatos de data/valor).")
    st.stop()

# aggregate per day and sort
vendas_dia_df = df.groupby('data_emissao', as_index=False)['valor_float'].sum()
vendas_dia_df = vendas_dia_df.sort_values('data_emissao').reset_index(drop=True)
vendas_dia_df['data_str'] = vendas_dia_df['data_emissao'].dt.strftime('%d/%m/%Y')

# --- Figures ---
# Bar (datas em ordem cronológica, rótulos horizontais)
fig_bar = px.bar(vendas_dia_df, x='data_str', y='valor_float', text='valor_float', title='Dados Lançados por Data')
fig_bar.update_traces(texttemplate='R$ %{text:,.2f}', textposition='outside')
fig_bar.update_layout(xaxis_title='Data', yaxis_title='Valor (R$)')
fig_bar.update_xaxes(tickangle=0)

# Pie (ordenada pelas maiores vendas)
vendas_pie = vendas_dia_df.sort_values('valor_float', ascending=False)
fig_pie = px.pie(vendas_pie, names='data_str', values='valor_float', title='Proporção de Dados Lançados por Data')
fig_pie.update_traces(textinfo='percent+label')

# Line (evolução)
fig_line = px.line(vendas_dia_df, x='data_emissao', y='valor_float', markers=True, title='Evolução dos Dados Lançados')
fig_line.update_layout(xaxis_title='Data', yaxis_title='Valor (R$)')
fig_line.update_xaxes(tickformat="%d/%m/%Y")

# --- Display ---
st.markdown("### Visualizações - Dados Lançados")
c1, c2 = st.columns(2)
with c1:
    st.plotly_chart(fig_bar, use_container_width=True)
with c2:
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")
st.plotly_chart(fig_line, use_container_width=True)

st.markdown("---")
st.subheader("📄 Tabela de Dados Lançados (amostra)")
st.dataframe(df.sort_values('data_emissao', ascending=True).reset_index(drop=True))
