from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
import os

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.database_manager import DatabaseManager
from src.basic_analyzer import BasicAnalyzer
from src.advanced_analyzer import AdvancedAnalyzer

app = Flask(__name__)
CORS(app)

@app.route('/health')
def health():
    return jsonify({"status": "ok", "message": "API funcionando"})

@app.route('/api/games')
def get_games():
    try:
        db = DatabaseManager()
        games = db.get_all_games()
        return jsonify({"success": True, "data": games})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/games/<steam_id>')
def get_game(steam_id):
    try:
        db = DatabaseManager()
        game_data = db.get_game_price_history(steam_id)
        if not game_data:
            return jsonify({"success": False, "error": "Jogo não encontrado"}), 404
        return jsonify({"success": True, "data": game_data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/analysis/best-deals')
def best_deals():
    try:
        analyzer = BasicAnalyzer()
        limit = request.args.get('limit', 5, type=int)
        deals = analyzer.find_best_deals(limit=limit)
        return jsonify({"success": True, "data": deals})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/analysis/stats')
def stats():
    try:
        analyzer = BasicAnalyzer()
        stats = analyzer.get_basic_stats()
        return jsonify({"success": True, "data": stats})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/predictions')
def predictions():
    try:
        analyzer = AdvancedAnalyzer()
        days = request.args.get('days', 7, type=int)
        predictions = analyzer.predict_future_prices(days=days)
        
        # Converter para lista de dicts
        result = []
        for _, row in predictions.iterrows():
            trend = ((row['predicted_price'] - row['current_price']) / row['current_price']) * 100
            result.append({
                'game': row['game'],
                'current_price': float(row['current_price']),
                'predicted_price': float(row['predicted_price']),
                'trend_percent': round(trend, 1),
                'recommendation': 'Aguarde' if trend < -10 else 'Compre' if trend > 5 else 'Estável'
            })
        
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/dashboard')
def dashboard():
    try:
        basic_analyzer = BasicAnalyzer()
        advanced_analyzer = AdvancedAnalyzer()
        
        # Dados básicos
        stats = basic_analyzer.get_basic_stats()
        deals = basic_analyzer.find_best_deals(limit=3)
        predictions = advanced_analyzer.predict_future_prices(days=7)
        
        dashboard_data = {
            'total_games': len(stats),
            'best_deals': deals,
            'recent_predictions': predictions.head(3).to_dict('records') if not predictions.empty else []
        }
        
        return jsonify({"success": True, "data": dashboard_data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
