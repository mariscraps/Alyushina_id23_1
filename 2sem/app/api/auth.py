from sqlalchemy.orm import Session
from app.core.security import create_access_token, verify_password, get_current_user
from app.cruds.user import get_user_by_email, create_user
from app.db.database import get_db
from app.schemas.token import TokenWithUser, Token
from app.schemas.user import UserCreate, UserLogin, User
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer # для безопасности (доступ через токен)

router = APIRouter()


@router.post("/sign-up/", response_model=Token)
def sign_up(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = create_user(db, user)
    access_token = create_access_token(data={"sub": user.email})

    return {
        "id": user.id,
        "email": user.email,
        "token": access_token,
        "token_type": "bearer"
    }


@router.post(
    "/login/",
    response_model=TokenWithUser,
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "description": "Successful login",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "email": "user@example.com",
                        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer"
                    }
                }
            }
        },
        400: {
            "description": "Incorrect email or password",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Incorrect email or password"
                    }
                }
            }
        },
        422: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/HTTPValidationError"},
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "email"],
                                "msg": "field required",
                                "type": "value_error.missing"
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def login(
        user: UserLogin,
        db: Session = Depends(get_db)
):
    db_user = get_user_by_email(db, email=user.email)

    if not db_user or not verify_password(user.password,
                                          db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    return TokenWithUser(
        id=db_user.id,
        email=db_user.email,
        token=create_access_token(data={"sub": db_user.email}),
        token_type="bearer"
    )


security_scheme = HTTPBearer()

@router.get(
    "/users/me/",
    response_model=User,
    summary="Get current user info",
    description="Returns authenticated user's data",
    dependencies=[Depends(security_scheme)],
    responses={
        200: {
            "description": "Successful response",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/User"}
                }
            }
        },
        401: {
            "description": "Unauthorized",
            "content": {
                "application/json": {
                    "example": {"detail": "Not authenticated"}
                }
            }
        }
    }
)
async def read_users_me(
        current_user: str = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Получение информации о текущем аутентифицированном пользователе
    """
    db_user = get_user_by_email(db, email=current_user)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
