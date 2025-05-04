# utils.py
from jose import JWTError, jwt
from fastapi import HTTPException, status, Request
from auth import SECRET_KEY, ALGORITHM

def get_current_user(request: Request):
    # Get token from cookies
    token = request.cookies.get("access_token")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please login first",
            headers={"Location": "/login"}
        )
    
    try:
        # Decode and verify token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"Location": "/login"}
            )
        return username
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"Location": "/login"}
        )