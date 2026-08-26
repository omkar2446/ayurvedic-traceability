from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.auth import create_access_token, get_db, hash_password, verify_password
from app.models import IdentityVerification, User
from app.schemas import TokenResponse, UserCreate, UserLogin, UserResponse, VerificationResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    existing = db.query(User).filter((User.email == user_data.email) | (User.username == user_data.username)).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email or username already registered")

    user = User(
        email=user_data.email,
        username=user_data.username,
        password_hash=hash_password(user_data.password),
        full_name=user_data.full_name,
        role=user_data.role.upper(),
        organization_id=user_data.organization_id,
        is_active=True,
        is_approved=False,
    )
    db.add(user)
    db.flush()
    db.add(IdentityVerification(
        user_id=user.id,
        document_type=user_data.verification_document_type,
        verification_details=user_data.verification_details,
        verification_status="PENDING",
    ))
    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)) -> TokenResponse:
    identifier = credentials.email or credentials.username
    if not identifier:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Email or username is required",
        )

    try:
        user = (
            db.query(User)
            .filter((User.email == identifier) | (User.username == identifier))
            .first()
        )
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable. Start PostgreSQL and try again.",
        ) from exc
    if user is None or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email/username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is disabled")
    if not user.is_approved:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User approval is pending")

    return TokenResponse(
        access_token=create_access_token(str(user.username)),
        user=UserResponse.model_validate(user),
    )