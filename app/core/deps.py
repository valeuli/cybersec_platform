from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from app.database.connection import get_db

import os

from app.database.models.user import User

SECRET_KEY = os.getenv("SECRET_KEY", "A-S3CR3T-K3Y-")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

def get_db_session(db: Session = Depends(get_db)):
    return db

def get_current_user(
    token: str = Depends(lambda authorization: authorization.replace("Bearer ", "") if authorization else None),
    db: Session = Depends(get_db),
    authorization: str | None = Depends(lambda: None),
):
    """Versión simple: si luego quieres usar OAuth2PasswordBearer, lo cambiamos."""
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autorizado")
    token = authorization.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str | None = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    return user