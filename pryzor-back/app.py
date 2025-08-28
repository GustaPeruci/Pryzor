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
        games_df = db.get_games()
        
        # Converter DataFrame para lista de dicionários
        if games_df.empty:
            games_list = []
        else:
            games_list = games_df.to_dict('records')
            
        return jsonify({"success": True, "data": games_list})
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
        deals_df = analyzer.find_best_deals(top_n=limit)
        
        # Converter DataFrame para lista de dicionários
        if deals_df.empty:
            deals_list = []
        else:
            deals_list = deals_df.to_dict('records')
            
        return jsonify({"success": True, "data": deals_list})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/analysis/stats')
def stats():
    try:
        analyzer = BasicAnalyzer()
        stats = analyzer.get_summary_stats()
        return jsonify({"success": True, "data": "Stats calculadas com sucesso"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/predictions')
def predictions():
    try:
        analyzer = AdvancedAnalyzer()
        days = request.args.get('days', 7, type=int)
        predictions_data = analyzer.predict_future_prices(days_ahead=days)
        
        # Converter para formato do frontend
        result = []
        for pred in predictions_data:
            result.append({
                'game': pred['game'],
                'current_price': float(pred['current_price']),
                'predicted_price': float(pred['predicted_avg']),
                'trend_percent': round(pred['trend_percent'], 1),
                'recommendation': pred['recommendation']
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
        stats = basic_analyzer.get_summary_stats()
        deals = basic_analyzer.find_best_deals(top_n=3)
        predictions_data = advanced_analyzer.predict_future_prices(days_ahead=7)
        
        dashboard_data = {
            'total_games': len(stats),
            'best_deals': deals,
            'recent_predictions': predictions_data[:3] if predictions_data else []
        }
        
        return jsonify({"success": True, "data": dashboard_data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
