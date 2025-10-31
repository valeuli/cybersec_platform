from datetime import datetime, timedelta
from fastapi import HTTPException

def validate_attempt_time(start_time: datetime, limit_minutes: int = 30):
    now = datetime.utcnow()
    elapsed = now - start_time
    if elapsed > timedelta(minutes=limit_minutes):
        raise HTTPException(
            status_code=403,
            detail=f"Tiempo de examen excedido ({limit_minutes} minutos)."
        )
