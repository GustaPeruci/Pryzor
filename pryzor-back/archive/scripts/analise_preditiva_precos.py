import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

class AnalisePreditivaPrecos:
    def __init__(self, csv_path="steamdb_dataset_geral_wide.csv"):
        """Inicializa a análise preditiva com o dataset de preços."""
        self.df = pd.read_csv(csv_path)
        self.jogos_analisados = []
        self.recomendacoes = {}
        
    def preparar_dados(self):
        """Prepara os dados para análise, transformando de wide para long format."""
        # Transforma de wide para long
        df_long = pd.melt(
            self.df, 
            id_vars=['nome_jogo', 'steam_id'], 
            var_name='semana', 
            value_name='preco'
        )
        
        # Remove dados nulos
        df_long = df_long.dropna()
        
        # Extrai ano e semana
        df_long['ano'] = df_long['semana'].str.extract(r'semana_(\d{4})-').astype(int)
        df_long['num_semana'] = df_long['semana'].str.extract(r'-(\d{2})$').astype(int)
        
        # Cria data aproximada
        df_long['data_aproximada'] = pd.to_datetime(
            df_long['ano'].astype(str) + '-01-01'
        ) + pd.to_timedelta((df_long['num_semana'] * 7), unit='D')
        
        # Ordena por jogo e data
        df_long = df_long.sort_values(['nome_jogo', 'data_aproximada'])
        
        return df_long
    
    def calcular_estatisticas_jogo(self, df_jogo):
        """Calcula estatísticas importantes para um jogo específico."""
        stats = {
            'preco_atual': df_jogo['preco'].iloc[-1],
            'preco_minimo': df_jogo['preco'].min(),
            'preco_maximo': df_jogo['preco'].max(),
            'preco_medio': df_jogo['preco'].mean(),
            'volatilidade': df_jogo['preco'].std(),
            'num_observacoes': len(df_jogo),
            'desconto_atual': ((df_jogo['preco'].max() - df_jogo['preco'].iloc[-1]) / df_jogo['preco'].max()) * 100,
            'tempo_desde_minimo': len(df_jogo) - df_jogo['preco'].idxmin() if len(df_jogo) > 0 else 0
        }
        
        # Tendência recente (últimas 8 semanas)
        if len(df_jogo) >= 8:
            recentes = df_jogo.tail(8)
            stats['tendencia_recente'] = np.polyfit(range(len(recentes)), recentes['preco'], 1)[0]
        else:
            stats['tendencia_recente'] = 0
            
        return stats
    
    def detectar_padroes_sazonais(self, df_jogo):
        """Detecta padrões sazonais nos preços."""
        if len(df_jogo) < 20:  # Poucos dados
            return {'sazonalidade': 'Dados insuficientes'}
        
        # Agrupa por mês
        df_jogo['mes'] = df_jogo['data_aproximada'].dt.month
        precos_por_mes = df_jogo.groupby('mes')['preco'].mean()
        
        # Identifica meses com menores preços (promoções)
        meses_baratos = precos_por_mes.nsmallest(3).index.tolist()
        
        meses_nomes = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
        
        return {
            'meses_promocao': [meses_nomes[m] for m in meses_baratos],
            'variacao_sazonal': precos_por_mes.max() - precos_por_mes.min()
        }
    
    def prever_proximo_preco(self, df_jogo):
        """Usa Random Forest para prever o próximo preço."""
        if len(df_jogo) < 10:
            return None
        
        # Prepara features
        df_jogo = df_jogo.copy()
        df_jogo['preco_lag1'] = df_jogo['preco'].shift(1)
        df_jogo['preco_lag2'] = df_jogo['preco'].shift(2)
        df_jogo['media_movel_4'] = df_jogo['preco'].rolling(4).mean()
        df_jogo['mes'] = df_jogo['data_aproximada'].dt.month
        
        # Remove NaN
        df_jogo = df_jogo.dropna()
        
        if len(df_jogo) < 5:
            return None
        
        # Features e target
        features = ['preco_lag1', 'preco_lag2', 'media_movel_4', 'mes']
        X = df_jogo[features]
        y = df_jogo['preco']
        
        # Treina modelo
        model = RandomForestRegressor(n_estimators=50, random_state=42)
        model.fit(X, y)
        
        # Previsão para próxima semana
        ultima_linha = X.iloc[-1:].copy()
        proxima_previsao = model.predict(ultima_linha)[0]
        
        return proxima_previsao
    
    def gerar_recomendacao(self, nome_jogo, stats, padroes, previsao):
        """Gera recomendação de compra baseada nas análises."""
        score_compra = 0
        razoes = []
        
        # Análise do desconto atual
        if stats['desconto_atual'] > 70:
            score_compra += 40
            razoes.append(f"Desconto excelente: {stats['desconto_atual']:.1f}%")
        elif stats['desconto_atual'] > 50:
            score_compra += 25
            razoes.append(f"Bom desconto: {stats['desconto_atual']:.1f}%")
        elif stats['desconto_atual'] > 30:
            score_compra += 15
            razoes.append(f"Desconto moderado: {stats['desconto_atual']:.1f}%")
        
        # Proximidade do preço mínimo
        distancia_minimo = ((stats['preco_atual'] - stats['preco_minimo']) / stats['preco_minimo']) * 100
        if distancia_minimo < 10:
            score_compra += 30
            razoes.append("Preço muito próximo do mínimo histórico")
        elif distancia_minimo < 25:
            score_compra += 20
            razoes.append("Preço próximo do mínimo histórico")
        
        # Tendência recente
        if stats['tendencia_recente'] > 0:
            score_compra += 15
            razoes.append("Preço em tendência de alta")
        elif stats['tendencia_recente'] < -1:
            razoes.append("Preço em queda, pode baixar mais")
        
        # Tempo desde o último mínimo
        if stats['tempo_desde_minimo'] > 20:
            score_compra += 10
            razoes.append("Faz tempo que não atinge preço mínimo")
        
        # Previsão
        if previsao and previsao > stats['preco_atual']:
            score_compra += 15
            razoes.append("Modelo prevê alta de preço")
        elif previsao and previsao < stats['preco_atual'] * 0.9:
            razoes.append("Modelo prevê queda significativa")
        
        # Sazonalidade
        mes_atual = datetime.now().month
        if 'meses_promocao' in padroes:
            meses_promo_num = []
            meses_dict = {
                'Janeiro': 1, 'Fevereiro': 2, 'Março': 3, 'Abril': 4,
                'Maio': 5, 'Junho': 6, 'Julho': 7, 'Agosto': 8,
                'Setembro': 9, 'Outubro': 10, 'Novembro': 11, 'Dezembro': 12
            }
            for mes_nome in padroes['meses_promocao']:
                meses_promo_num.append(meses_dict[mes_nome])
            
            if mes_atual in meses_promo_num:
                score_compra += 10
                razoes.append("Estamos em época de promoções típicas")
        
        # Classificação final
        if score_compra >= 70:
            recomendacao = "COMPRE AGORA! 🟢"
        elif score_compra >= 50:
            recomendacao = "Bom momento para comprar 🟡"
        elif score_compra >= 30:
            recomendacao = "Momento regular, considere esperar 🟠"
        else:
            recomendacao = "Aguarde por melhores preços 🔴"
        
        return {
            'recomendacao': recomendacao,
            'score': score_compra,
            'razoes': razoes,
            'preco_atual': stats['preco_atual'],
            'preco_minimo': stats['preco_minimo'],
            'desconto_atual': stats['desconto_atual'],
            'previsao_proxima_semana': previsao
        }
    
    def analisar_todos_jogos(self):
        """Executa análise completa para todos os jogos."""
        df_long = self.preparar_dados()
        
        print("🎮 ANÁLISE PREDITIVA DE PREÇOS - STEAM GAMES 🎮")
        print("=" * 60)
        
        for jogo in self.df['nome_jogo'].unique():
            df_jogo = df_long[df_long['nome_jogo'] == jogo].copy()
            
            if len(df_jogo) < 5:  # Poucos dados
                continue
                
            # Análises
            stats = self.calcular_estatisticas_jogo(df_jogo)
            padroes = self.detectar_padroes_sazonais(df_jogo)
            previsao = self.prever_proximo_preco(df_jogo)
            
            # Recomendação
            rec = self.gerar_recomendacao(jogo, stats, padroes, previsao)
            self.recomendacoes[jogo] = rec
            
            # Output
            print(f"\n🎲 {jogo.upper()}")
            print("-" * 40)
            print(f"Recomendação: {rec['recomendacao']}")
            print(f"Score de Compra: {rec['score']}/100")
            print(f"Preço Atual: R$ {rec['preco_atual']:.2f}")
            print(f"Preço Mínimo: R$ {rec['preco_minimo']:.2f}")
            print(f"Desconto Atual: {rec['desconto_atual']:.1f}%")
            
            if rec['previsao_proxima_semana']:
                print(f"Previsão Próxima Semana: R$ {rec['previsao_proxima_semana']:.2f}")
            
            if 'meses_promocao' in padroes and padroes['meses_promocao']:
                print(f"Meses típicos de promoção: {', '.join(padroes['meses_promocao'])}")
            
            print("Razões:")
            for razao in rec['razoes']:
                print(f"  • {razao}")
    
    def resumo_geral(self):
        """Gera resumo geral das recomendações."""
        if not self.recomendacoes:
            self.analisar_todos_jogos()
        
        print("\n" + "=" * 60)
        print("📊 RESUMO GERAL DAS RECOMENDAÇÕES")
        print("=" * 60)
        
        # Ordena por score de compra
        jogos_ordenados = sorted(
            self.recomendacoes.items(), 
            key=lambda x: x[1]['score'], 
            reverse=True
        )
        
        print("\n🏆 TOP 5 MELHORES OPORTUNIDADES:")
        for i, (jogo, rec) in enumerate(jogos_ordenados[:5], 1):
            print(f"{i}. {jogo} - {rec['recomendacao']} (Score: {rec['score']})")
        
        print("\n⚠️  JOGOS PARA AGUARDAR:")
        aguardar = [(jogo, rec) for jogo, rec in jogos_ordenados if rec['score'] < 30]
        for jogo, rec in aguardar:
            print(f"• {jogo} - Score: {rec['score']} - Aguarde melhores preços")
        
        # Estatísticas gerais
        scores = [rec['score'] for rec in self.recomendacoes.values()]
        print(f"\n📈 ESTATÍSTICAS GERAIS:")
        print(f"Score médio de compra: {np.mean(scores):.1f}")
        print(f"Jogos com recomendação de compra (score ≥ 50): {len([s for s in scores if s >= 50])}")
        print(f"Total de jogos analisados: {len(scores)}")

def main():
    """Função principal."""
    try:
        analise = AnalisePreditivaPrecos()
        analise.analisar_todos_jogos()
        analise.resumo_geral()
        
        print(f"\n✅ Análise concluída em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except FileNotFoundError:
        print("❌ Arquivo steamdb_dataset_geral_wide.csv não encontrado!")
        print("Execute primeiro o script de coleta de dados.")
    except Exception as e:
        print(f"❌ Erro durante a análise: {e}")

if __name__ == "__main__":
    main()
