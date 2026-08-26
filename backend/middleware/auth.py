from fastapi import Request
import os
from dotenv import load_dotenv

load_dotenv()

# For prototype purposes, a static token. In production, use OAuth2 / JWT verification.
VALID_TOKENS = {
    os.getenv('DEV_API_TOKEN', 'dev-token-123'): 'user_123'
}

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
    
    if token not in VALID_TOKENS:
        raise AuthException(status_code=401, message="Invalid or expired token")
        
    # Attach user info to request state
    request.state.user_id = VALID_TOKENS[token]
    
    return request.state.user_id
