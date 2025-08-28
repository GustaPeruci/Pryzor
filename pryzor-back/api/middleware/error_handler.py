"""
Handlers de erro para a API
"""

from flask import jsonify
from api.utils.response import APIResponse, APIError
import traceback

def setup_error_handlers(app):
    """Configura handlers de erro globais"""
    
    @app.errorhandler(APIError)
    def handle_api_error(error):
        """Handler para erros customizados da API"""
        return APIResponse.error(
            message=error.message,
            status_code=error.status_code,
            error_code=error.error_code
        )
    
    @app.errorhandler(404)
    def handle_not_found(error):
        """Handler para 404 - Not Found"""
        return APIResponse.error(
            message="Endpoint não encontrado",
            status_code=404,
            error_code="NOT_FOUND"
        )
    
    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        """Handler para 405 - Method Not Allowed"""
        return APIResponse.error(
            message="Método não permitido para este endpoint",
            status_code=405,
            error_code="METHOD_NOT_ALLOWED"
        )
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        """Handler para 500 - Internal Server Error"""
        if app.debug:
            # Em desenvolvimento, mostrar traceback
            return APIResponse.error(
                message=f"Erro interno: {str(error)}",
                status_code=500,
                error_code="INTERNAL_ERROR"
            )
        else:
            # Em produção, erro genérico
            return APIResponse.error(
                message="Erro interno do servidor",
                status_code=500,
                error_code="INTERNAL_ERROR"
            )
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """Handler para erros não tratados"""
        if app.debug:
            # Log do erro completo em desenvolvimento
            app.logger.error(f"Erro não tratado: {traceback.format_exc()}")
            return APIResponse.error(
                message=f"Erro inesperado: {str(error)}",
                status_code=500,
                error_code="UNEXPECTED_ERROR"
            )
        else:
            # Em produção, erro genérico
            return APIResponse.error(
                message="Erro inesperado do servidor",
                status_code=500,
                error_code="UNEXPECTED_ERROR"
            )
