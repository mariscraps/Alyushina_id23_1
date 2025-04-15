from .encode import router as encode_router
from .auth import router as auth_router
from .ws import router as ws_router


# указываем, какие объекты будут экспортироваться при импорте через
# from app.api import *
__all__ = [
    'encode_router',
    'auth_router',
    'ws_router'
]