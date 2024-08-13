
from fastapi import HTTPException
from functools import wraps
import logging

logger = logging.getLogger('app')


def global_exception_handler(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"An unknown error occurred: {str(e)}")
            raise HTTPException(status_code=500, detail="Unknown error")
    return wrapper