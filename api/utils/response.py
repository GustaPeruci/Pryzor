"""
Utilitários para padronizar respostas da API
"""

from flask import jsonify
from datetime import datetime

class APIResponse:
    """Classe para padronizar respostas da API"""
    
    @staticmethod
    def success(data=None, message="Success", status_code=200):
        """Resposta de sucesso padronizada"""
        response = {
            "success": True,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        return jsonify(response), status_code
    
    @staticmethod
    def error(message="Error", status_code=400, error_code=None):
        """Resposta de erro padronizada"""
        response = {
            "success": False,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "error_code": error_code
        }
        return jsonify(response), status_code
    
    @staticmethod
    def paginated(data, page=1, per_page=10, total=0, message="Success"):
        """Resposta paginada padronizada"""
        response = {
            "success": True,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "data": data,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page if total > 0 else 1
            }
        }
        return jsonify(response), 200

class APIError(Exception):
    """Exceção customizada para erros da API"""
    
    def __init__(self, message, status_code=400, error_code=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
