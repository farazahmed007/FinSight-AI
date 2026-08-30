from fastapi import Request
from services.auth_service import AuthService

class AuthException(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message

async def require_auth(request: Request):
    auth_header = request.headers.get('Authorization')
    
    if not auth_header:
        raise AuthException(status_code=401, message="Missing Authorization header")
        
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        raise AuthException(status_code=401, message="Invalid Authorization header format. Expected 'Bearer <token>'")
        
    token = parts[1]
    
    try:
        payload = AuthService.decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise AuthException(status_code=401, message="Invalid token payload")
        
        # Attach user info to request state
        request.state.user_id = user_id
        return user_id
    except ValueError as e:
        raise AuthException(status_code=401, message=str(e))
