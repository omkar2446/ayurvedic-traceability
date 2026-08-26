from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.auth import get_current_user, get_db
from app.models import User
from app.schemas import UserResponse

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[User]:
    users = db.query(User).filter(User.id != current_user.id, User.is_active == True).all()
    return users
