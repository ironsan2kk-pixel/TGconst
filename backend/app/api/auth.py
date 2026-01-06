"""
API эндпоинты авторизации
"""
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from ..models.main_db import Admin
from ..schemas.auth import LoginRequest, TokenResponse, AdminResponse
from ..utils.security import verify_password, create_access_token
from .deps import DbSession, CurrentAdmin

router = APIRouter()


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Авторизация",
    description="Авторизация администратора по логину и паролю. Возвращает JWT токен."
)
async def login(
    request: LoginRequest,
    db: DbSession
) -> TokenResponse:
    """
    Авторизация администратора.
    
    - **username**: Логин администратора
    - **password**: Пароль
    
    Возвращает JWT токен для дальнейших запросов.
    """
    # Ищем админа по логину
    result = await db.execute(
        select(Admin).where(Admin.username == request.username)
    )
    admin = result.scalar_one_or_none()
    
    # Проверяем что админ существует и пароль верный
    if admin is None or not verify_password(request.password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Создаём токен
    access_token = create_access_token(
        data={"sub": str(admin.id)}
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer"
    )


@router.get(
    "/me",
    response_model=AdminResponse,
    summary="Текущий администратор",
    description="Получение информации о текущем авторизованном администраторе."
)
async def get_me(
    current_admin: CurrentAdmin
) -> AdminResponse:
    """
    Получение информации о текущем администраторе.
    
    Требует авторизации через Bearer токен.
    """
    return AdminResponse.model_validate(current_admin)
