from datetime import datetime, timezone, timedelta
from fastapi import HTTPException

def validate_attempt_time(taken_at, limit_minutes=30):
    if taken_at.tzinfo is None:
        taken_at = taken_at.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)
    elapsed = now - taken_at

    if elapsed > timedelta(minutes=limit_minutes):
        raise HTTPException(
            status_code=403,
            detail=f"Tiempo de examen excedido ({limit_minutes} minutos)."
        )

    return True