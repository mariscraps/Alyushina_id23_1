from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import engine, Base
from app.api import auth, encode, ws
from fastapi.openapi.utils import get_openapi

app = FastAPI()

# настраиваем приложение FastAPI и добавляем поддержку CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# создаем таблицы БД
Base.metadata.create_all(bind=engine)

# подключаем роутеры
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(ws.router, prefix="/ws", tags=["websocket"])
app.include_router(encode.router, prefix="/api", tags=["encoding"])


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Encryption API",
        version="1.0.0",
        description="API for data encryption with Huffman and XOR",
        routes=app.routes,
    )

    if "components" not in openapi_schema:
        openapi_schema["components"] = {"schemas": {}}

    # добавляем WebSocket
    openapi_schema["paths"]["/ws/encode"] = {
        "websocket": {
            "tags": ["websocket"],
            "summary": "Real-time encoding via WebSocket",
            "description": "Establish WebSocket connection for real-time encoding",
            "parameters": [
                {
                    "name": "token",
                    "in": "query",
                    "required": True,
                    "schema": {"type": "string"},
                    "description": "JWT token for authentication"
                }
            ],
            "responses": {
                "101": {
                    "description": "WebSocket connection established"
                }
            }
        }
    }

    openapi_schema.setdefault("components", {})
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }

    protected_paths = ["/auth/users/me/"]
    for path in protected_paths:
        if path in openapi_schema["paths"]:
            for method in openapi_schema["paths"][path]:
                openapi_schema["paths"][path][method]["security"] = [
                    {"BearerAuth": []}]

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }

    if "security" in openapi_schema:
        del openapi_schema["security"]

    app.openapi_schema = openapi_schema
    return openapi_schema


app.openapi = custom_openapi
