import pandas as pd
import os
from datetime import datetime

# Nome do jogo (edite para cada novo jogo)
CSV_ENTRADA = "Dados SteamDB/dead_by_daylight_381210.csv"  # Exemplo: nome_do_jogo_steamid.csv
# Extrai nome do jogo e steam_id do nome do arquivo
import re
basename = os.path.basename(CSV_ENTRADA)
print(f"Arquivo detectado: {basename}")  # debug
match = re.match(r"(.+)_([0-9]+)\.csv$", basename, re.IGNORECASE)
if match:
    NOME_JOGO = match.group(1).replace('_', ' ').title()
    STEAM_ID = match.group(2)
else:
    raise ValueError("Nome do arquivo deve estar no formato <nome_do_jogo>_<steam_id>.csv (case-insensitive para .csv)")
# Caminho do CSV geral (dataset acumulado)
CSV_SAIDA = "steamdb_dataset_geral.csv"
# Coluna de preço a usar: 'Final price' ou 'Historical Low'
COLUNA_PRECO = 'Final price'  # ou 'Historical Low'

# Lê o CSV exportado do SteamDB
try:
    df = pd.read_csv(CSV_ENTRADA, sep=';')
except Exception:
    try:
        df = pd.read_csv(CSV_ENTRADA, sep='\t')
    except Exception:
        df = pd.read_csv(CSV_ENTRADA, sep=None, engine='python')

# Limpa aspas dos nomes das colunas
df.columns = [c.replace('"', '').replace("'", '').strip() for c in df.columns]

# Checa se as colunas existem
if 'DateTime' not in df.columns or COLUNA_PRECO not in df.columns:
    raise ValueError(f"Colunas esperadas não encontradas. Colunas detectadas: {df.columns.tolist()}")

# Converte data para datetime e preço para float
df['DateTime'] = pd.to_datetime(df['DateTime'], dayfirst=True, errors='coerce')
df[COLUNA_PRECO] = df[COLUNA_PRECO].astype(str).str.replace(',', '.').astype(float)

# Cria coluna de semana no formato YYYY-WW
df['semana'] = df['DateTime'].dt.strftime('%Y-%U')


# Agrupa por semana e pega o menor preço da semana
df_semana = df.groupby('semana')[COLUNA_PRECO].min().reset_index()
df_semana['nome_jogo'] = NOME_JOGO
df_semana['steam_id'] = STEAM_ID

# Reordena colunas
final = df_semana[['nome_jogo', 'steam_id', 'semana', COLUNA_PRECO]]
final = final.rename(columns={COLUNA_PRECO: 'menor_preco_semana'})


# --- NOVO: Atualiza o CSV geral já no formato wide ---
CSV_SAIDA_WIDE = "steamdb_dataset_geral_wide.csv"

# Lê o arquivo wide existente, se houver
if os.path.exists(CSV_SAIDA_WIDE):
    df_wide_existente = pd.read_csv(CSV_SAIDA_WIDE)
    # Garante que steam_id existe
    if 'steam_id' not in df_wide_existente.columns:
        df_wide_existente['steam_id'] = ''
else:
    df_wide_existente = pd.DataFrame()

# Faz o pivot do novo jogo: cada semana vira uma coluna
final_wide = final.pivot(index=['nome_jogo', 'steam_id'], columns='semana', values='menor_preco_semana')
final_wide.columns = [f"semana_{col}" for col in final_wide.columns]
final_wide = final_wide.reset_index()

# Combina os dados: remove o jogo se já existe, depois adiciona a versão atualizada
if not df_wide_existente.empty:
    # Remove o jogo atual se já existe (para atualizar)
    df_wide_existente = df_wide_existente[df_wide_existente['nome_jogo'] != NOME_JOGO]
    # Concatena o jogo atualizado
    df_wide = pd.concat([df_wide_existente, final_wide], ignore_index=True, sort=False)
else:
    df_wide = final_wide

# Unifica todas as colunas de semana (sem duplicatas e sem prefixo duplo)
colunas = list(df_wide.columns)
colunas_unicas = []
for c in colunas:
    if c.startswith('semana_semana_'):
        c = c.replace('semana_semana_', 'semana_')
    if c not in colunas_unicas:
        colunas_unicas.append(c)

# Ordena as colunas de semana cronologicamente
def extrai_ordem(col):
    if col.startswith('semana_'):
        try:
            ano, semana = col.replace('semana_', '').split('-')
            return int(ano)*100 + int(semana)
        except:
            return 99999999
    return 0

colunas_semana = [c for c in colunas_unicas if c.startswith('semana_')]
colunas_semana_ordenadas = sorted(colunas_semana, key=extrai_ordem)
colunas_finais = ['nome_jogo', 'steam_id'] + colunas_semana_ordenadas

# Salva o arquivo wide com colunas ordenadas e sem duplicatas
df_wide_final = df_wide[[c for c in colunas_finais if c in df_wide.columns]]
df_wide_final.to_csv(CSV_SAIDA_WIDE, index=False)

print(f"Arquivo geral atualizado no formato wide: {CSV_SAIDA_WIDE}")
