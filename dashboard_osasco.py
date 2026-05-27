import streamlit as st
import pandas as pd

# Configuração da página para ocupar a tela toda
st.set_page_config(page_title="Mapeamento MPE - Osasco", layout="wide")

# Caminho da nossa "planilha de ouro"
ARQUIVO_CSV = 'osasco_micro_pequenas.csv.zip'

# Função para carregar os dados (o cache evita que ele recarregue tudo a cada clique)
@st.cache_data
def carregar_dados():
    df = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='latin1', dtype=str, compression='zip')
    # Limpando bairros vazios para o filtro não quebrar
    df['bairro'] = df['bairro'].fillna('NÃO INFORMADO').str.upper()
    
    # Criando uma coluna mais legível para o Porte
    df['porte_nome'] = df['porte_empresa'].map({'01': 'Micro Empresa (ME)', '03': 'Pequena Empresa (EPP)'})
    return df

# Título principal do seu Web App
st.title("📊 Ecossistema de Micro e Pequenas Empresas - Osasco")
st.markdown("Painel interativo para mapeamento de atores de inovação e desenvolvimento regional.")

# Carregando os dados
try:
    df = carregar_dados()
except FileNotFoundError:
    st.error("Arquivo não encontrado. Verifique se a extração foi concluída com sucesso na sua Mesa.")
    st.stop()

# --- BARRA LATERAL (Filtros) ---
st.sidebar.header("Filtros de Pesquisa")

# Filtro de Porte
portes = st.sidebar.multiselect(
    "Selecione o Porte:",
    options=df['porte_nome'].unique(),
    default=df['porte_nome'].dropna().unique()
)

# Filtro de Bairro
lista_bairros = sorted(list(df['bairro'].unique()))
bairros_selecionados = st.sidebar.multiselect(
    "Selecione os Bairros:",
    options=lista_bairros,
    default=[] # Começa vazio para mostrar todos
)

# Novo Filtro: Inova Simples
inova_simples = st.sidebar.checkbox("🚀 Mostrar apenas Startups (Inova Simples)")

# Aplicando os filtros
df_filtrado = df[df['porte_nome'].isin(portes)]
if bairros_selecionados:
    df_filtrado = df_filtrado[df_filtrado['bairro'].isin(bairros_selecionados)]

# Aplicando o filtro de inovação
if inova_simples:
    df_filtrado = df_filtrado[df_filtrado['natureza_juridica'] == '2348']

# --- MÉTRICAS GERAIS ---
st.subheader("Resumo dos Dados Filtrados")
col1, col2 = st.columns(2)
col1.metric("Total de Empresas", f"{len(df_filtrado):,}".replace(',', '.'))
col2.metric("Bairros Alcançados", len(df_filtrado['bairro'].unique()))

st.divider()

# --- GRÁFICOS ---
col3, col4 = st.columns(2)

with col3:
    st.markdown("### Top 10 Bairros com mais Empresas")
    top_bairros = df_filtrado['bairro'].value_counts().head(10)
    st.bar_chart(top_bairros)

with col4:
    st.markdown("### Top 10 Ramos de Atividade (CNAE Principal)")
    top_cnaes = df_filtrado['cnae_descricao'].value_counts().head(10)
    st.bar_chart(top_cnaes)

st.divider()

# --- TABELA INTERATIVA ---
st.markdown("### Base de Dados Completa")
st.markdown("Você pode pesquisar diretamente na tabela abaixo:")

# Selecionando apenas colunas úteis para não poluir a tela
colunas_exibicao = ['cnpj_basico', 'razao_social', 'natureza_juridica', 'porte_nome', 'bairro', 'cnae_descricao', 'telefone_1', 'correio_eletronico']
st.dataframe(df_filtrado[colunas_exibicao], use_container_width=True)
