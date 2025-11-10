class AppError(Exception):
    """Base application error"""
    pass

class UserAlreadyExists(AppError):
    pass

class UserNotFound(AppError):
    pass

class InvalidToken(AppError):
    pass

class RefreshTokenRequired(AppError):
    pass

class AccessTokenRequired(AppError):
    pass

class InsufficientPermission(AppError):
    pass

class AccountNotVerified(AppError):
    pass

class InvalidCredentials(AppError):
    pass

# Error handlers
def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(error):
        return {'message': str(error)}, 400
    
    @app.errorhandler(404)
    def handle_not_found(error):
        return {'message': 'Resource not found'}, 404
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        return {'message': 'Internal server error'}, 500