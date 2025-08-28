"""
Analisador avançado com modelo preditivo e análise sazonal
Fase 1.2: Análise avançada e predições básicas
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from datetime import datetime, timedelta
import warnings
import sys
import os
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from database_manager import DatabaseManager

warnings.filterwarnings('ignore')

class AdvancedAnalyzer:
    def __init__(self):
        """Inicializa o analisador avançado"""
        self.db = DatabaseManager()
        self.output_path = Path(__file__).parent.parent / "data" / "analysis_output"
        self.output_path.mkdir(exist_ok=True)
        
        # Configuração para gráficos
        plt.style.use('seaborn-v0_8')
        sns.set_palette("viridis")
        
    def prepare_features(self, df):
        """Prepara features para o modelo preditivo"""
        # Converte data para datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Features temporais
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['day_of_year'] = df['date'].dt.dayofyear
        df['week_of_year'] = df['date'].dt.isocalendar().week
        df['quarter'] = df['date'].dt.quarter
        
        # Features sazonais
        df['is_december'] = (df['month'] == 12).astype(int)  # Steam Winter Sale
        df['is_summer'] = df['month'].isin([6, 7, 8]).astype(int)  # Steam Summer Sale
        df['is_weekend'] = df['date'].dt.weekday.isin([5, 6]).astype(int)
        
        # Features de tendência
        df = df.sort_values(['name', 'date'])
        df['price_lag_7'] = df.groupby('name')['price'].shift(7)
        df['price_lag_30'] = df.groupby('name')['price'].shift(30)
        df['price_trend_7'] = df['price'] - df['price_lag_7']
        df['price_trend_30'] = df['price'] - df['price_lag_30']
        
        # Features estatísticas móveis
        df['price_ma_7'] = df.groupby('name')['price'].rolling(window=7).mean().reset_index(0, drop=True)
        df['price_ma_30'] = df.groupby('name')['price'].rolling(window=30).mean().reset_index(0, drop=True)
        df['price_std_30'] = df.groupby('name')['price'].rolling(window=30).std().reset_index(0, drop=True)
        
        # Features do jogo (usando dados históricos)
        game_stats = df.groupby('name')['price'].agg(['min', 'max', 'mean', 'std']).reset_index()
        game_stats.columns = ['name', 'game_min_price', 'game_max_price', 'game_avg_price', 'game_price_volatility']
        df = df.merge(game_stats, on='name')
        
        return df
    
    def analyze_seasonal_patterns(self):
        """Analisa padrões sazonais nos preços"""
        print("📅 ANÁLISE SAZONAL")
        print("=" * 50)
        
        df = self.db.get_price_history()
        if df.empty:
            print("❌ Nenhum dado disponível")
            return
        
        df = self.prepare_features(df)
        
        # Análise por mês
        monthly_stats = df.groupby(['month', 'name'])['price'].mean().unstack().fillna(0)
        monthly_avg = df.groupby('month')['price'].agg(['mean', 'std']).round(2)
        
        print("\n📊 PREÇOS MÉDIOS POR MÊS:")
        print(monthly_avg.to_string())
        
        # Detecta períodos de promoção
        promotion_months = monthly_avg[monthly_avg['mean'] < monthly_avg['mean'].quantile(0.3)].index.tolist()
        
        print(f"\n🔥 MESES COM MAIS PROMOÇÕES: {', '.join(map(str, promotion_months))}")
        
        # Gráfico sazonal
        plt.figure(figsize=(12, 6))
        plt.subplot(1, 2, 1)
        monthly_avg['mean'].plot(kind='bar', color='skyblue', alpha=0.8)
        plt.title('Preço Médio por Mês')
        plt.xlabel('Mês')
        plt.ylabel('Preço Médio (R$)')
        plt.xticks(rotation=45)
        
        plt.subplot(1, 2, 2)
        quarterly_avg = df.groupby('quarter')['price'].mean()
        quarterly_avg.plot(kind='bar', color='lightcoral', alpha=0.8)
        plt.title('Preço Médio por Trimestre')
        plt.xlabel('Trimestre')
        plt.ylabel('Preço Médio (R$)')
        
        plt.tight_layout()
        plt.savefig(self.output_path / "seasonal_analysis.png", dpi=300, bbox_inches='tight')
        plt.show()
        
        return monthly_stats, promotion_months
    
    def train_prediction_model(self):
        """Treina modelo preditivo de preços"""
        print("\n🤖 TREINANDO MODELO PREDITIVO")
        print("=" * 50)
        
        df = self.db.get_price_history()
        if len(df) < 100:
            print("❌ Dados insuficientes para treinar modelo")
            return None
        
        # Prepara dados
        df = self.prepare_features(df)
        
        # Remove NaN e seleciona features
        features = ['year', 'month', 'day_of_year', 'week_of_year', 'quarter',
                   'is_december', 'is_summer', 'is_weekend',
                   'game_min_price', 'game_max_price', 'game_avg_price', 'game_price_volatility']
        
        # Adiciona features que não são NaN
        optional_features = ['price_lag_7', 'price_lag_30', 'price_ma_7', 'price_ma_30', 'price_std_30']
        for feat in optional_features:
            if df[feat].notna().sum() > len(df) * 0.5:  # Se mais de 50% dos dados não são NaN
                features.append(feat)
        
        # Filtra dados válidos
        valid_data = df[features + ['price']].dropna()
        
        if len(valid_data) < 50:
            print("❌ Dados válidos insuficientes após limpeza")
            return None
        
        X = valid_data[features]
        y = valid_data['price']
        
        # Divisão treino/teste
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Treina modelo
        model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
        model.fit(X_train, y_train)
        
        # Avaliação
        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        print(f"📊 Erro Médio Absoluto: R$ {mae:.2f}")
        print(f"📊 R² Score: {r2:.3f}")
        
        # Importância das features
        feature_importance = pd.DataFrame({
            'feature': features,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\n🎯 IMPORTÂNCIA DAS FEATURES:")
        print(feature_importance.head(10).to_string(index=False))
        
        return model, features, {'mae': mae, 'r2': r2}
    
    def predict_future_prices(self, days_ahead=30):
        """Prediz preços futuros para os próximos dias"""
        print(f"\n🔮 PREDIÇÕES PARA OS PRÓXIMOS {days_ahead} DIAS")
        print("=" * 50)
        
        # Treina modelo
        model_result = self.train_prediction_model()
        if not model_result:
            print("❌ Não foi possível treinar modelo")
            return
        
        model, features, metrics = model_result
        
        # Busca dados recentes
        df = self.db.get_price_history()
        df = self.prepare_features(df)
        
        predictions = []
        
        for game in df['name'].unique():
            game_data = df[df['name'] == game].sort_values('date')
            
            if len(game_data) < 10:
                continue
            
            # Último registro válido
            last_record = game_data.dropna(subset=features).iloc[-1]
            
            # Simula datas futuras
            future_dates = pd.date_range(
                start=last_record['date'] + timedelta(days=1),
                periods=days_ahead,
                freq='D'
            )
            
            game_predictions = []
            
            for future_date in future_dates:
                # Cria features para data futura
                future_features = {
                    'year': future_date.year,
                    'month': future_date.month,
                    'day_of_year': future_date.dayofyear,
                    'week_of_year': future_date.isocalendar().week,
                    'quarter': (future_date.month - 1) // 3 + 1,
                    'is_december': int(future_date.month == 12),
                    'is_summer': int(future_date.month in [6, 7, 8]),
                    'is_weekend': int(future_date.weekday() in [5, 6]),
                    'game_min_price': last_record['game_min_price'],
                    'game_max_price': last_record['game_max_price'],
                    'game_avg_price': last_record['game_avg_price'],
                    'game_price_volatility': last_record['game_price_volatility']
                }
                
                # Adiciona features opcionais se disponíveis
                for feat in ['price_lag_7', 'price_lag_30', 'price_ma_7', 'price_ma_30', 'price_std_30']:
                    if feat in features:
                        future_features[feat] = last_record[feat] if pd.notna(last_record[feat]) else last_record['price']
                
                # Predição
                feature_values = [future_features[feat] for feat in features]
                predicted_price = model.predict([feature_values])[0]
                
                game_predictions.append({
                    'date': future_date,
                    'predicted_price': max(0, predicted_price)  # Garante preço positivo
                })
            
            # Calcula tendência
            current_price = last_record['price']
            avg_predicted = np.mean([p['predicted_price'] for p in game_predictions])
            trend = ((avg_predicted - current_price) / current_price) * 100
            
            predictions.append({
                'game': game,
                'current_price': current_price,
                'predicted_avg': avg_predicted,
                'trend_percent': trend,
                'recommendation': self._get_trend_recommendation(trend),
                'predictions': game_predictions
            })
        
        # Ordena por tendência de queda (melhores oportunidades)
        predictions.sort(key=lambda x: x['trend_percent'])
        
        print("\n🎯 PREDIÇÕES E RECOMENDAÇÕES:")
        for pred in predictions[:10]:  # Top 10
            print(f"🎮 {pred['game']}")
            print(f"   💰 Preço atual: R$ {pred['current_price']:.2f}")
            print(f"   📈 Preço médio predito: R$ {pred['predicted_avg']:.2f}")
            print(f"   📊 Tendência: {pred['trend_percent']:+.1f}%")
            print(f"   🎯 Recomendação: {pred['recommendation']}")
            print()
        
        # Salva predições
        pred_df = pd.DataFrame([{
            'Jogo': p['game'],
            'Preço_Atual': f"R$ {p['current_price']:.2f}",
            'Preço_Predito': f"R$ {p['predicted_avg']:.2f}",
            'Tendência_%': f"{p['trend_percent']:+.1f}%",
            'Recomendação': p['recommendation']
        } for p in predictions])
        
        pred_df.to_csv(self.output_path / "price_predictions.csv", index=False)
        print(f"💾 Predições salvas em: {self.output_path / 'price_predictions.csv'}")
        
        return predictions
    
    def _get_trend_recommendation(self, trend_percent):
        """Retorna recomendação baseada na tendência predita"""
        if trend_percent <= -10:
            return "🔥 AGUARDE! Grande queda prevista"
        elif trend_percent <= -5:
            return "⏳ Espere, possível queda"
        elif trend_percent <= 5:
            return "🤔 Preço estável"
        elif trend_percent <= 10:
            return "👍 Compre agora, alta prevista"
        else:
            return "🚀 COMPRE URGENTE! Alta significativa"
    
    def detect_price_anomalies(self):
        """Detecta anomalias nos preços (quedas/picos incomuns)"""
        print("\n⚠️ DETECÇÃO DE ANOMALIAS")
        print("=" * 50)
        
        df = self.db.get_price_history()
        df = self.prepare_features(df)
        
        anomalies = []
        
        for game in df['name'].unique():
            game_data = df[df['name'] == game].sort_values('date')
            
            if len(game_data) < 30:
                continue
            
            # Calcula Z-score dos preços
            mean_price = game_data['price'].mean()
            std_price = game_data['price'].std()
            
            if std_price > 0:
                game_data['z_score'] = (game_data['price'] - mean_price) / std_price
                
                # Detecta anomalias (|z_score| > 2)
                anomaly_records = game_data[abs(game_data['z_score']) > 2]
                
                for _, record in anomaly_records.iterrows():
                    anomaly_type = "📈 Pico de preço" if record['z_score'] > 0 else "📉 Queda de preço"
                    anomalies.append({
                        'game': game,
                        'date': record['date'].strftime('%Y-%m-%d'),
                        'price': record['price'],
                        'type': anomaly_type,
                        'z_score': record['z_score']
                    })
        
        if anomalies:
            print(f"🔍 Encontradas {len(anomalies)} anomalias:")
            for anomaly in sorted(anomalies, key=lambda x: abs(x['z_score']), reverse=True)[:10]:
                print(f"   {anomaly['type']}: {anomaly['game']} - R$ {anomaly['price']:.2f} em {anomaly['date']}")
        else:
            print("✅ Nenhuma anomalia significativa detectada")
        
        return anomalies
    
    def run_advanced_analysis(self):
        """Executa análise avançada completa"""
        print("🚀 INICIANDO ANÁLISE AVANÇADA - FASE 1.2")
        print("=" * 60)
        
        # 1. Análise sazonal
        self.analyze_seasonal_patterns()
        
        # 2. Detecção de anomalias
        self.detect_price_anomalies()
        
        # 3. Predições futuras
        self.predict_future_prices(30)
        
        print("\n✅ ANÁLISE AVANÇADA CONCLUÍDA!")
        print(f"📁 Resultados salvos em: {self.output_path}")

if __name__ == "__main__":
    analyzer = AdvancedAnalyzer()
    analyzer.run_advanced_analysis()
